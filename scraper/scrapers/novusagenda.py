"""
NovusAgenda (Granicus) scraper.

Public calendar: https://{slug}.novusagenda.com/agendapublic/
Uses a Telerik Web Forms search UI backed by ASP.NET UpdatePanels.
Playwright selects a date-range preset and clicks Search; rows are then
parsed from the Telerik RadGrid.  Agenda text is fetched via httpx
(MeetingView.aspx is server-rendered, no JS required).

Row structure (0-indexed cells):
  0 – meeting date  (e.g. "02/17/26" or "6/17/2025")
  1 – meeting type / board name
  2 – location
  3 – icon link whose onclick contains MeetingID
"""
import logging
import re
from datetime import date, datetime, timedelta
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from config import DAYS_AHEAD, find_keyword_matches

# NovusAgenda instances post meetings months in advance; use a wider window.
_DAYS_AHEAD = max(DAYS_AHEAD, 365)
import db

logger = logging.getLogger(__name__)

_MEETING_ID_RE = re.compile(r"MeetingID=(\d+)", re.IGNORECASE)
# NovusAgenda uses 2-digit years ("02/17/26") but some instances use 4-digit.
_DATE_FMTS = ["%m/%d/%y", "%m/%d/%Y"]

# Preset label whose forward window comfortably covers DAYS_AHEAD (up to 365).
_RANGE_LABEL = "Next Year"


def _base_url(municipality: dict) -> str:
    url = (municipality.get("calendar_url") or "").rstrip("/")
    return url + "/" if url else ""


def _parse_date(text: str) -> date | None:
    text = text.strip()
    for fmt in _DATE_FMTS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _get_meetings(base_url: str) -> list[dict]:
    """
    Drive the NovusAgenda search form with Playwright.
    Returns a list of meeting dicts filtered to today..today+DAYS_AHEAD.
    """
    today  = date.today()
    cutoff = today + timedelta(days=_DAYS_AHEAD)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        html = ""
        try:
            page.goto(base_url, wait_until="networkidle", timeout=60_000)

            # Bail immediately if ASP.NET returned its generic tenant-error page
            # (happens when a subdomain exists on novusagenda.com but has no
            # configured instance — page is ~1.4 KB and contains this string).
            quick_html = page.content()
            if len(quick_html) < 5_000 or "http error occurred" in quick_html.lower():
                logger.warning("[novusagenda] Instance not available at %s", base_url)
                return []

            try:
                page.wait_for_selector("select[name*='ddlDateRange']", timeout=15_000)
            except PWTimeout:
                logger.warning("[novusagenda] No search form at %s", base_url)
                return []

            page.select_option("select[name*='ddlDateRange']", label=_RANGE_LABEL)
            page.wait_for_load_state("networkidle", timeout=15_000)

            page.click("input[id*='imageButtonSearch']")
            try:
                page.wait_for_selector(
                    "td.rgNoRecords, tr.rgRow, tr.rgAltRow", timeout=15_000
                )
            except PWTimeout:
                page.wait_for_load_state("networkidle", timeout=10_000)

            html = page.content()
        except PWTimeout as exc:
            logger.warning("[novusagenda] Timeout at %s: %s", base_url, exc)
        finally:
            browser.close()

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    meetings: list[dict] = []
    seen_ids: set[str] = set()  # deduplicate — grid may repeat a MeetingID for sub-items

    for row in soup.select("tr.rgRow, tr.rgAltRow"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        meeting_date = _parse_date(cells[0].get_text(strip=True))
        if meeting_date is None:
            continue
        if meeting_date < today or meeting_date > cutoff:
            continue

        meeting_type = cells[1].get_text(strip=True) or "Meeting"
        location     = cells[2].get_text(strip=True) if len(cells) > 2 else ""

        # MeetingID lives in the onclick of the agenda icon (cell 3)
        meeting_id: str | None = None
        for td in cells[3:] if len(cells) > 3 else cells:
            for a in td.find_all("a", onclick=True):
                m = _MEETING_ID_RE.search(a["onclick"])
                if m:
                    meeting_id = m.group(1)
                    break
            if meeting_id:
                break

        if not meeting_id or meeting_id in seen_ids:
            continue
        seen_ids.add(meeting_id)

        agenda_url = urljoin(
            base_url,
            f"MeetingView.aspx?MeetingID={meeting_id}&MinutesMeetingID=-1&doctype=Agenda",
        )
        meetings.append({
            "external_id":  meeting_id,
            "title":        meeting_type,
            "meeting_date": meeting_date.isoformat(),
            "location":     location or None,
            "agenda_url":   agenda_url,
        })

    return meetings


def _fetch_agenda_text(agenda_url: str) -> str:
    """Fetch MeetingView.aspx and return plain-text agenda."""
    try:
        r = httpx.get(
            agenda_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
            follow_redirects=True,
        )
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml").get_text(" ", strip=True)
    except Exception as exc:
        logger.debug("[novusagenda] Could not fetch agenda %s: %s", agenda_url, exc)
        return ""


def scrape_municipality(municipality: dict) -> None:
    base_url = _base_url(municipality)
    if not base_url:
        logger.warning(
            "[novusagenda] %s: no calendar_url configured", municipality["name"]
        )
        return

    name    = municipality["name"]
    muni_id = municipality["id"]
    logger.info("[novusagenda] Scraping %s", name)

    meetings = _get_meetings(base_url)
    if not meetings:
        logger.debug("[novusagenda] %s: no upcoming meetings in window", name)
        return

    for m in meetings:
        try:
            meeting_db_id = db.upsert_meeting(muni_id, m)
        except Exception as exc:
            logger.warning(
                "[novusagenda] %s: upsert meeting failed: %s", name, exc
            )
            continue

        agenda_text = _fetch_agenda_text(m["agenda_url"])
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
            logger.warning(
                "[novusagenda] %s: upsert item failed: %s", name, exc
            )
            continue

        if item_db_id:
            matches = find_keyword_matches(agenda_text)
            if matches:
                logger.info(
                    "[novusagenda] MATCH in %s on %s: %s",
                    name,
                    m["meeting_date"],
                    [kw for kw, _ in matches],
                )
                db.insert_keyword_matches(item_db_id, matches)
