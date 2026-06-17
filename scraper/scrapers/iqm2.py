"""
IQM2 (Accela Meeting Portal / Granicus) scraper.

Public calendar: https://{slug}.iqm2.com/Citizens/Calendar.aspx
  → Lists all meetings as <a href="/Citizens/Detail_Meeting.aspx?ID={id}">
    with link text like "Jan 5, 2026 9:00 AM"

Meeting detail: https://{slug}.iqm2.com/Citizens/Detail_Meeting.aspx?ID={id}
  → Server-rendered HTML with agenda items as plain text

No JavaScript required — plain httpx throughout.
"""
import logging
import re
from datetime import date, datetime, timedelta
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from config import DAYS_AHEAD, find_keyword_matches
import db

_DAYS_AHEAD = max(DAYS_AHEAD, 365)
logger = logging.getLogger(__name__)

_DATE_FMTS = ["%b %d, %Y %I:%M %p", "%b %d, %Y", "%Y/%m/%d %I:%M %p", "%Y/%m/%d"]
_HEADERS    = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def _base(municipality: dict) -> str:
    url = (municipality.get("calendar_url") or "").rstrip("/")
    # calendar_url is the Citizens/default.aspx root; strip to base
    return re.sub(r"/Citizens.*$", "", url, flags=re.IGNORECASE)


def _parse_date(text: str) -> date | None:
    s = text.strip()
    for fmt in _DATE_FMTS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _get_meetings(base_url: str) -> list[dict]:
    cal_url = f"{base_url}/Citizens/Calendar.aspx"
    today   = date.today()
    cutoff  = today + timedelta(days=_DAYS_AHEAD)
    meetings: list[dict] = []

    try:
        r = httpx.get(cal_url, headers=_HEADERS, timeout=30, follow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        seen: set[str] = set()
        for a in soup.find_all("a", href=re.compile(r"Detail_Meeting\.aspx\?ID=\d+", re.I)):
            href     = a["href"]
            id_match = re.search(r"ID=(\d+)", href, re.IGNORECASE)
            if not id_match:
                continue
            mid = id_match.group(1)
            if mid in seen:
                continue

            # Link text is the date: "Jan 5, 2026 9:00 AM" or "Jan 5, 2026"
            link_text  = a.get_text(strip=True)
            mtg_date   = _parse_date(link_text)
            if mtg_date is None:
                continue
            if mtg_date < today or mtg_date > cutoff:
                continue

            seen.add(mid)
            detail_url = urljoin(f"{base_url}/Citizens/", href)
            # Meeting title is often in the surrounding context
            parent_text = a.parent.get_text(" ", strip=True) if a.parent else link_text
            meetings.append({
                "external_id":  mid,
                "title":        "Board Meeting",   # refined in detail fetch
                "meeting_date": mtg_date.isoformat(),
                "meeting_time": None,
                "location":     None,
                "agenda_url":   detail_url,
                "_detail_url":  detail_url,
            })
    except Exception as exc:
        logger.warning("[iqm2] Calendar fetch failed for %s: %s", base_url, exc)

    return meetings


def _fetch_detail(detail_url: str) -> tuple[str, str, str]:
    """Returns (title, location, agenda_text)."""
    try:
        r = httpx.get(detail_url, headers=_HEADERS, timeout=30, follow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(" ", strip=True)

        # Page text starts: "YYYY/MM/DD HH:MM AM <Title> - Web Outline - City, FL ..."
        # Capture everything between the time and " - Web Outline" (or similar suffix).
        title = ""
        m = re.match(
            r'\d{4}/\d{2}/\d{2}\s+\d{1,2}:\d{2}\s+(?:AM|PM)\s+(.+?)(?:\s+-\s+Web\s+\w+|\s+-\s+\w+\s+Outline|\s{3,})',
            text,
            re.IGNORECASE,
        )
        if m:
            title = m.group(1).strip()[:150]

        # Location: look for a street address or "City Hall"
        location = ""
        loc_m = re.search(
            r'(\d+\s+[A-Z][^,\n]{3,50},\s*[A-Z][a-z]+,?\s*FL\s*\d{5}|City Hall[^,\n]{0,60})',
            text[:1000],
        )
        if loc_m:
            location = loc_m.group(0).strip()[:200]

        return title or "Board Meeting", location, text
    except Exception as exc:
        logger.debug("[iqm2] Detail fetch failed %s: %s", detail_url, exc)
        return "Board Meeting", "", ""


def scrape_municipality(municipality: dict) -> None:
    base_url = _base(municipality)
    if not base_url:
        logger.warning("[iqm2] %s: no calendar_url configured", municipality["name"])
        return

    name    = municipality["name"]
    muni_id = municipality["id"]
    logger.info("[iqm2] Scraping %s", name)

    meetings = _get_meetings(base_url)
    if not meetings:
        logger.debug("[iqm2] %s: no upcoming meetings in window", name)
        return

    logger.info("[iqm2] %s: %d upcoming meetings", name, len(meetings))

    for m in meetings:
        title, location, agenda_text = _fetch_detail(m["_detail_url"])
        m["title"]    = title or m["title"]
        m["location"] = location or None

        try:
            meeting_db_id = db.upsert_meeting(muni_id, m)
        except Exception as exc:
            logger.warning("[iqm2] %s: upsert meeting failed: %s", name, exc)
            continue

        if not agenda_text:
            continue

        item_payload = {
            "external_id": f"agenda-{m['external_id']}",
            "title":       f"Agenda – {m['title']}",
            "description": None,
            "attachments": [{"name": "Agenda", "url": m["agenda_url"]}],
        }

        try:
            item_db_id = db.upsert_agenda_item(meeting_db_id, item_payload)
        except Exception as exc:
            logger.warning("[iqm2] %s: upsert item failed: %s", name, exc)
            continue

        if item_db_id:
            matches = find_keyword_matches(agenda_text)
            if matches:
                logger.info(
                    "[iqm2] MATCH in %s on %s: %s",
                    name, m["meeting_date"], [kw for kw, _ in matches],
                )
                db.insert_keyword_matches(item_db_id, matches)
