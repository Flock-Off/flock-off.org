"""
BoardDocs scraper for FL school districts.

Board URLs: https://go.boarddocs.com/fl/{slug}/Board.nsf/Public

Strategy:
  1. Fetch the meeting list via the public SEO endpoint (plain httpx, no auth).
     GET /Board.nsf/BD-GETMeetingsListForSEO?open  → JSON list of all meetings.
     Fields: Name, Description, Unique (12-char ID), Date (ISO 8601).

  2. For each upcoming meeting, navigate to its detail page inside a single
     Playwright browser session using hash routing (#btdetails/{unique}).
     Hash changes are client-side so CloudFront sees only one initial page load.

  3. Extract the rendered inner text for keyword scanning.
"""
import logging
import re
from datetime import date, datetime, timedelta

import httpx
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from config import DAYS_AHEAD, find_keyword_matches
import db

_DAYS_AHEAD = max(DAYS_AHEAD, 365)
logger = logging.getLogger(__name__)


def _base(municipality: dict) -> str:
    url = (municipality.get("calendar_url") or "").rstrip("/")
    return re.sub(r"/Public$", "", url, flags=re.IGNORECASE)


def _parse_date(raw: str) -> date | None:
    s = str(raw).strip().replace("Z", "+00:00")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y%m%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _fetch_meeting_list(board_url: str) -> list[dict]:
    """Fetch all meetings from the public SEO endpoint via plain httpx."""
    url = f"{board_url}/BD-GETMeetingsListForSEO?open"
    today  = date.today()
    cutoff = today + timedelta(days=_DAYS_AHEAD)
    upcoming = []
    try:
        r = httpx.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": f"{board_url}/Public",
            },
            timeout=30,
            follow_redirects=True,
        )
        r.raise_for_status()
        for mtg in r.json():
            raw_date = mtg.get("Date", "")
            mtg_date = _parse_date(raw_date)
            if mtg_date is None or mtg_date < today or mtg_date > cutoff:
                continue
            uid = str(mtg.get("Unique", "")).strip()
            upcoming.append({
                "external_id":  uid or f"bd-{raw_date[:10]}",
                "title":        mtg.get("Name") or "Board Meeting",
                "meeting_date": mtg_date.isoformat(),
                "location":     None,
                "agenda_url":   f"{board_url}/Public#btdetails/{uid}" if uid else f"{board_url}/Public",
                "_uid":         uid,
            })
    except Exception as exc:
        logger.warning("[boarddocs] SEO endpoint failed for %s: %s", board_url, exc)
    return upcoming


def _fetch_agendas_playwright(board_url: str, meetings: list[dict], name: str) -> None:
    """
    Open one Playwright session per district; navigate to each meeting via
    hash routing (client-side, no new CloudFront requests) and extract text.
    Stores agenda_text back into each meeting dict in-place.
    """
    public_url = f"{board_url}/Public"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1400, "height": 900},
        )
        try:
            page.goto(public_url, wait_until="networkidle", timeout=60_000)
        except PWTimeout:
            logger.warning("[boarddocs] %s: initial page load timeout", name)
            browser.close()
            return

        html_check = page.content()
        if "403" in html_check[:500] or len(html_check) < 2_000:
            logger.warning("[boarddocs] %s: blocked or empty page", name)
            browser.close()
            return

        for m in meetings:
            uid = m.get("_uid", "")
            if not uid:
                continue
            try:
                # Hash navigation is client-side; Angular router handles it.
                page.evaluate(f"window.location.hash = '#btdetails/{uid}'")
                page.wait_for_load_state("networkidle", timeout=15_000)
                text = page.locator("body").inner_text()
                m["_agenda_text"] = text
            except Exception as exc:
                logger.debug("[boarddocs] %s: agenda nav failed for %s: %s", name, uid, exc)
                m["_agenda_text"] = ""

        browser.close()


def scrape_municipality(municipality: dict) -> None:
    board_url = _base(municipality)
    if not board_url:
        logger.warning("[boarddocs] %s: no calendar_url configured", municipality["name"])
        return

    name    = municipality["name"]
    muni_id = municipality["id"]
    logger.info("[boarddocs] Scraping %s", name)

    meetings = _fetch_meeting_list(board_url)
    if not meetings:
        logger.debug("[boarddocs] %s: no upcoming meetings in window", name)
        return

    logger.info("[boarddocs] %s: %d upcoming meetings — fetching agendas", name, len(meetings))
    _fetch_agendas_playwright(board_url, meetings, name)

    for m in meetings:
        try:
            meeting_db_id = db.upsert_meeting(muni_id, m)
        except Exception as exc:
            logger.warning("[boarddocs] %s: upsert meeting failed: %s", name, exc)
            continue

        agenda_text = m.get("_agenda_text", "")
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
