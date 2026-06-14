"""
Playwright fallback scraper for municipalities with custom/JS-rendered calendar sites.
Used when platform == 'custom'.
"""
import logging
import re
from datetime import date, timedelta

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from config import DAYS_AHEAD, find_keyword_matches
import db

logger = logging.getLogger(__name__)


def _scrape_page_text(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=45_000)
            text = page.inner_text("body")
        except PWTimeout:
            logger.warning("[playwright] Timeout loading %s", url)
            text = ""
        finally:
            browser.close()
    return text


def scrape_municipality(municipality: dict) -> None:
    calendar_url = municipality.get("calendar_url")
    if not calendar_url:
        logger.warning("[playwright] %s: no calendar_url configured", municipality["name"])
        return

    name = municipality["name"]
    muni_id = municipality["id"]
    logger.info("[playwright] %s", name)

    page_text = _scrape_page_text(calendar_url)
    if not page_text:
        return

    # Use the calendar page itself as a single searchable item scoped to today's run.
    # A future enhancement can parse individual meeting links from the rendered DOM.
    run_date = date.today().isoformat()
    meeting_payload = {
        "external_id":  f"calendar-{run_date}",
        "title":        "Calendar Page Scan",
        "meeting_date": run_date,
        "agenda_url":   calendar_url,
        "status":       "scheduled",
    }

    try:
        meeting_db_id = db.upsert_meeting(muni_id, meeting_payload)
    except Exception as e:
        logger.warning("[playwright] %s: failed to upsert meeting: %s", name, e)
        return

    item_payload = {
        "external_id":  f"page-{run_date}",
        "title":        "Full calendar page text",
        "attachments":  [{"name": "Calendar", "url": calendar_url}],
    }

    try:
        item_db_id = db.upsert_agenda_item(meeting_db_id, item_payload)
    except Exception as e:
        logger.warning("[playwright] %s: failed to upsert item: %s", name, e)
        return

    if item_db_id:
        matches = find_keyword_matches(page_text)
        if matches:
            logger.info("[playwright] MATCH in %s: %s", name, [kw for kw, _ in matches])
            db.insert_keyword_matches(item_db_id, matches)
