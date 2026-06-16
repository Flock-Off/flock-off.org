"""
Hyland OnBase AgendaOnline scraper.

Currently used by: City of Tampa
  Base URL: https://tampagov.hylandcloud.com/251agendaonline/

How it works:
  - The Meetings/Search page renders upcoming meetings via JavaScript.
    Playwright loads it and parses the table (default "Recent/Upcoming" view
    requires no form submission).
  - Each meeting row may contain a ViewMeeting link with doctype=1 (Agenda).
    Meetings without an agenda link are skipped.
  - Agenda HTML is fetched directly with httpx using the Documents/ViewAgenda
    endpoint, which returns a server-rendered HTML document (no JS needed).
"""
import logging
import re
from datetime import date, datetime, timedelta
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from config import DAYS_AHEAD, find_keyword_matches
import db

logger = logging.getLogger(__name__)

_DATETIME_FMT = "%m/%d/%Y %I:%M:%S %p"   # "6/18/2026 9:00:00 AM"
_MTG_ID_RE    = re.compile(r"ViewMeeting\?id=(\d+)&doctype=1", re.IGNORECASE)
_DAYS_AHEAD   = max(DAYS_AHEAD, 180)      # OnBase agendas are posted weeks ahead


def _base_url(municipality: dict) -> str:
    url = (municipality.get("calendar_url") or "").rstrip("/")
    return url + "/" if url else ""


def _get_meetings(base_url: str) -> list[dict]:
    """
    Load the default Meeting Search page (Recent/Upcoming) with Playwright.
    Returns meetings that have a posted agenda (doctype=1) within the window.
    """
    today  = date.today()
    cutoff = today + timedelta(days=_DAYS_AHEAD)
    search_url = urljoin(base_url, "Meetings/Search")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        html = ""
        try:
            page.goto(search_url, wait_until="networkidle", timeout=60_000)

            # Collect initial results.  If "Get More Results" is visible,
            # click it once to expand (covers typical Tampa meeting volume).
            try:
                more = page.query_selector("#btnGetMoreResults:visible")
                if more:
                    more.click()
                    page.wait_for_load_state("networkidle", timeout=15_000)
            except PWTimeout:
                pass

            html = page.content()
        except PWTimeout as exc:
            logger.warning("[hyland] Timeout at %s: %s", search_url, exc)
        finally:
            browser.close()

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    meetings: list[dict] = []
    seen_ids: set[str] = set()

    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        name     = cells[0].get_text(strip=True)
        mtype    = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        date_str = cells[2].get_text(strip=True) if len(cells) > 2 else ""

        try:
            dt = datetime.strptime(date_str, _DATETIME_FMT)
        except ValueError:
            continue

        meeting_date = dt.date()
        if meeting_date < today or meeting_date > cutoff:
            continue

        # Only keep meetings that have a posted Agenda (doctype=1)
        meeting_id: str | None = None
        for a in row.find_all("a", href=True):
            m = _MTG_ID_RE.search(a["href"])
            if m:
                meeting_id = m.group(1)
                break

        if not meeting_id or meeting_id in seen_ids:
            continue
        seen_ids.add(meeting_id)

        agenda_url = urljoin(
            base_url,
            f"Meetings/ViewMeeting?id={meeting_id}&doctype=1",
        )
        meetings.append({
            "external_id":  meeting_id,
            "title":        name,
            "meeting_date": meeting_date.isoformat(),
            "meeting_time": dt.strftime("%H:%M"),
            "meeting_type": mtype or None,
            "location":     None,
            "agenda_url":   agenda_url,
        })

    return meetings


def _fetch_agenda_text(base_url: str, meeting_id: str) -> str:
    """
    Fetch rendered agenda HTML directly from the Documents/ViewAgenda endpoint.
    This endpoint is server-rendered and requires no JavaScript.
    """
    url = urljoin(
        base_url,
        f"Documents/ViewAgenda?meetingId={meeting_id}&type=agenda&doctype=1",
    )
    try:
        r = httpx.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
            follow_redirects=True,
        )
        r.raise_for_status()
        if len(r.text) < 1000:
            return ""
        return BeautifulSoup(r.text, "lxml").get_text(" ", strip=True)
    except Exception as exc:
        logger.debug("[hyland] Could not fetch agenda %s: %s", url, exc)
        return ""


def scrape_municipality(municipality: dict) -> None:
    base_url = _base_url(municipality)
    if not base_url:
        logger.warning(
            "[hyland] %s: no calendar_url configured", municipality["name"]
        )
        return

    name    = municipality["name"]
    muni_id = municipality["id"]
    logger.info("[hyland] Scraping %s", name)

    meetings = _get_meetings(base_url)
    if not meetings:
        logger.debug("[hyland] %s: no upcoming meetings with agendas", name)
        return

    for m in meetings:
        try:
            meeting_db_id = db.upsert_meeting(muni_id, m)
        except Exception as exc:
            logger.warning("[hyland] %s: upsert meeting failed: %s", name, exc)
            continue

        agenda_text = _fetch_agenda_text(base_url, m["external_id"])
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
            logger.warning("[hyland] %s: upsert item failed: %s", name, exc)
            continue

        if item_db_id:
            matches = find_keyword_matches(agenda_text)
            if matches:
                logger.info(
                    "[hyland] MATCH in %s on %s: %s",
                    name,
                    m["meeting_date"],
                    [kw for kw, _ in matches],
                )
                db.insert_keyword_matches(item_db_id, matches)
