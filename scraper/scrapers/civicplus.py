"""
CivicPlus AgendaCenter scraper.

The new CivicPlus platform ("newCP") renders meeting lists via JavaScript.
We use Playwright to fill the date search form and extract the rendered rows.

Row format (first TD, no class):
  "{date} — Posted {posted_date} {time} {title}"
Link format: /AgendaCenter/ViewFile/Agenda/_{MMDDYYYY}-{id}[?html=true|?packet=true]

URL pattern: https://{host}/AgendaCenter
"""
import logging
import re
from datetime import date, timedelta, datetime
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from config import DAYS_AHEAD, find_keyword_matches
import db

logger = logging.getLogger(__name__)

_DATE_RE = re.compile(
    r'^([A-Za-z]+ \d{1,2},\s*\d{4}|\d{1,2}/\d{1,2}/\d{4})'
)
_POSTED_RE = re.compile(
    r'^[^\-]+\s*—\s*Posted\s+\w+ \d+,\s*\d+\s+\d+:\d+\s+(?:AM|PM)\s+',
    re.IGNORECASE
)
_ID_RE = re.compile(r'_\d+-(\d+)')


def _base_url(municipality: dict) -> str:
    return (municipality.get("calendar_url") or "").rstrip("/")


def _render_and_search(base_url: str) -> str:
    """Navigate to AgendaCenter, fill date form, return rendered HTML."""
    today = date.today()
    end = today + timedelta(days=DAYS_AHEAD)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(base_url, wait_until="domcontentloaded", timeout=45_000)
            # wait for the search form to be ready
            page.wait_for_selector("#StartDatePicker", timeout=15_000)
            page.fill("#StartDatePicker", today.strftime("%m/%d/%Y"))
            page.fill("#EndDatePicker", end.strftime("%m/%d/%Y"))
            # search button is an <input type="image" id="searchButton">
            page.click("#searchButton", timeout=8_000)
            try:
                page.wait_for_selector("tr[id^='row'], p.dim.results", timeout=15_000)
            except PWTimeout:
                pass
            html = page.content()
        except PWTimeout:
            logger.warning("[civicplus] Timeout on %s", base_url)
            html = ""
        finally:
            browser.close()
    return html


def _parse_meetings(html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    today = date.today()
    cutoff = today + timedelta(days=DAYS_AHEAD)
    meetings = []

    for row in soup.select("tr[id^='row']"):
        # first TD holds "date — Posted ... title"
        tds = row.find_all("td")
        if not tds:
            continue
        main_td = tds[0]
        text = main_td.get_text(" ", strip=True)

        # extract meeting date
        date_match = _DATE_RE.match(text)
        if not date_match:
            continue
        try:
            meeting_date = _parse_date(date_match.group(1))
        except ValueError:
            continue
        if meeting_date < today or meeting_date > cutoff:
            continue

        # extract title (strip the "date — Posted ... PM" prefix)
        title = _POSTED_RE.sub("", text).strip()
        if not title:
            title = "Meeting"

        # find the PDF link (no query string = plain PDF)
        pdf_link = None
        html_link = None
        for a in row.find_all("a", href=True):
            href = a["href"]
            if "ViewFile" in href:
                if "html=true" in href:
                    html_link = href
                elif "packet" not in href and "?" not in href:
                    pdf_link = href
        agenda_url = html_link or pdf_link
        if agenda_url and not agenda_url.startswith("http"):
            agenda_url = urljoin(base_url, agenda_url)

        # external_id from URL or row id
        id_match = _ID_RE.search(agenda_url or "")
        external_id = id_match.group(1) if id_match else row.get("id", "")

        meetings.append({
            "external_id":  external_id,
            "title":        title,
            "meeting_date": meeting_date.isoformat(),
            "agenda_url":   agenda_url,
        })

    return meetings


def _parse_date(text: str) -> date:
    text = re.sub(r'\s+', ' ', text.strip())
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date: {text!r}")


def _fetch_agenda_text(agenda_url: str) -> str:
    """Download agenda page/PDF and return plain text."""
    try:
        r = httpx.get(agenda_url, timeout=30, follow_redirects=True)
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        if "pdf" in ct:
            # basic PDF text extraction
            try:
                import pdfplumber, io
                with pdfplumber.open(io.BytesIO(r.content)) as pdf:
                    return "\n".join(p.extract_text() or "" for p in pdf.pages)
            except Exception:
                return ""
        return BeautifulSoup(r.text, "lxml").get_text(" ", strip=True)
    except Exception as e:
        logger.debug("[civicplus] Could not fetch agenda from %s: %s", agenda_url, e)
        return ""


def scrape_municipality(municipality: dict) -> None:
    base_url = _base_url(municipality)
    if not base_url:
        logger.warning("[civicplus] %s: no calendar_url configured", municipality["name"])
        return

    name = municipality["name"]
    muni_id = municipality["id"]
    logger.info("[civicplus] %s", name)

    html = _render_and_search(base_url)
    if not html:
        return

    meetings = _parse_meetings(html, base_url)
    if not meetings:
        logger.debug("[civicplus] %s: no upcoming meetings in window", name)
        return

    for m in meetings:
        try:
            meeting_db_id = db.upsert_meeting(muni_id, m)
        except Exception as e:
            logger.warning("[civicplus] %s: upsert meeting failed: %s", name, e)
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
        except Exception as e:
            logger.warning("[civicplus] %s: upsert item failed: %s", name, e)
            continue

        if item_db_id:
            matches = find_keyword_matches(agenda_text)
            if matches:
                logger.info("[civicplus] MATCH in %s on %s: %s",
                            name, m["meeting_date"], [kw for kw, _ in matches])
                db.insert_keyword_matches(item_db_id, matches)
