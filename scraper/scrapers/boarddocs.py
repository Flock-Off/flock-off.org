"""
BoardDocs scraper for FL school districts.

Board URLs follow: https://go.boarddocs.com/fl/{slug}/Board.nsf/Public

BoardDocs has a public REST API backed by an IBM Domino server:
  POST /Board.nsf/BD-GetMeetings-Public  → JSON meeting list
  GET  /Board.nsf/BD-GetAgendaDoc-Public?openagent&id={unique_id}  → HTML agenda

Meeting list payload: {"current_meeting_id": ""}
Each meeting entry contains at least: unique_id, numberdate, name
"""
import logging
import re
from datetime import date, datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from config import DAYS_AHEAD, find_keyword_matches
import db

_DAYS_AHEAD = max(DAYS_AHEAD, 365)
logger = logging.getLogger(__name__)

_DATE_FMTS = ["%Y%m%d", "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"]


def _base(municipality: dict) -> str:
    url = (municipality.get("calendar_url") or "").rstrip("/")
    # url is like https://go.boarddocs.com/fl/{slug}/Board.nsf/Public
    # We need the Board.nsf root, e.g. https://go.boarddocs.com/fl/{slug}/Board.nsf
    return re.sub(r"/Public$", "", url, flags=re.IGNORECASE)


def _parse_date(raw: str) -> date | None:
    s = str(raw).strip()
    for fmt in _DATE_FMTS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _get_meetings(board_url: str) -> list[dict]:
    """
    POST to BD-GetMeetings-Public and return upcoming meetings.
    Falls back to parsing the public HTML page if the API fails.
    """
    today  = date.today()
    cutoff = today + timedelta(days=_DAYS_AHEAD)
    meetings: list[dict] = []

    api_url = f"{board_url}/BD-GetMeetings-Public"
    try:
        r = httpx.post(
            api_url,
            data={"current_meeting_id": ""},
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json, */*"},
            timeout=30,
            follow_redirects=True,
        )
        r.raise_for_status()
        data = r.json()
        # API returns a list of meeting objects
        for mtg in data:
            raw_date = mtg.get("numberdate") or mtg.get("date") or mtg.get("unique_id", "")[:8]
            mtg_date = _parse_date(raw_date)
            if mtg_date is None:
                continue
            if mtg_date < today or mtg_date > cutoff:
                continue

            uid    = mtg.get("unique_id", "")
            name   = mtg.get("name", "Board Meeting") or "Board Meeting"
            agenda = f"{board_url}/BD-GetAgendaDoc-Public?openagent&id={uid}" if uid else None

            meetings.append({
                "external_id":  uid or f"bd-{raw_date}",
                "title":        name,
                "meeting_date": mtg_date.isoformat(),
                "location":     None,
                "agenda_url":   agenda,
                "_bd_uid":      uid,
                "_board_url":   board_url,
            })
    except Exception as exc:
        logger.debug("[boarddocs] API failed for %s: %s — trying HTML fallback", board_url, exc)
        meetings = _html_fallback(board_url, today, cutoff)

    return meetings


def _html_fallback(board_url: str, today: date, cutoff: date) -> list[dict]:
    """Parse upcoming meetings from the public landing page HTML."""
    meetings: list[dict] = []
    pub_url = f"{board_url}/Public"
    try:
        r = httpx.get(
            pub_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
            follow_redirects=True,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        # BoardDocs renders meeting links in <a> tags containing the unique ID
        # Pattern: /Board.nsf/Public#btdetails/{unique_id}
        id_re = re.compile(r"#btdetails/([A-Z0-9]{16,})", re.IGNORECASE)
        seen: set[str] = set()

        for a in soup.find_all("a", href=True):
            m = id_re.search(a["href"])
            if not m:
                continue
            uid = m.group(1)
            if uid in seen:
                continue
            seen.add(uid)

            # Date is usually embedded in the text near the link or in the uid itself
            text = a.get_text(" ", strip=True)
            mtg_date: date | None = None
            # Try to find a date in surrounding text
            date_m = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", text)
            if date_m:
                mtg_date = _parse_date(date_m.group(1))

            if mtg_date is None:
                continue
            if mtg_date < today or mtg_date > cutoff:
                continue

            meetings.append({
                "external_id":  uid,
                "title":        text or "Board Meeting",
                "meeting_date": mtg_date.isoformat(),
                "location":     None,
                "agenda_url":   f"{board_url}/BD-GetAgendaDoc-Public?openagent&id={uid}",
                "_bd_uid":      uid,
                "_board_url":   board_url,
            })
    except Exception as exc:
        logger.warning("[boarddocs] HTML fallback failed for %s: %s", board_url, exc)

    return meetings


def _fetch_agenda_text(agenda_url: str) -> str:
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
        logger.debug("[boarddocs] Agenda fetch failed %s: %s", agenda_url, exc)
        return ""


def scrape_municipality(municipality: dict) -> None:
    board_url = _base(municipality)
    if not board_url:
        logger.warning("[boarddocs] %s: no calendar_url configured", municipality["name"])
        return

    name    = municipality["name"]
    muni_id = municipality["id"]
    logger.info("[boarddocs] Scraping %s", name)

    meetings = _get_meetings(board_url)
    if not meetings:
        logger.debug("[boarddocs] %s: no upcoming meetings in window", name)
        return

    for m in meetings:
        try:
            meeting_db_id = db.upsert_meeting(muni_id, m)
        except Exception as exc:
            logger.warning("[boarddocs] %s: upsert meeting failed: %s", name, exc)
            continue

        if not m.get("agenda_url"):
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
            logger.warning("[boarddocs] %s: upsert item failed: %s", name, exc)
            continue

        if item_db_id:
            matches = find_keyword_matches(agenda_text)
            if matches:
                logger.info(
                    "[boarddocs] MATCH in %s on %s: %s",
                    name, m["meeting_date"], [kw for kw, _ in matches],
                )
                db.insert_keyword_matches(item_db_id, matches)
