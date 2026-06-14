"""
Legistar REST API scraper.
Legistar exposes a public JSON API at webapi.legistar.com for municipalities
that have not token-gated their data.

Verified public FL slugs (as of 2026-06-14):
  fortlauderdale, broward, gainesville, clearwater, hollywoodfl, miramar,
  pensacola, delraybeach, coconutcreek, hallandalebeach, pinellas, alachua,
  ocala, cocoa
"""
import logging
from datetime import date, timedelta

import httpx

from config import DAYS_AHEAD, find_keyword_matches
import db

logger = logging.getLogger(__name__)

BASE = "https://webapi.legistar.com/v1"


def _get(slug: str, path: str, params: dict | None = None) -> list | dict:
    url = f"{BASE}/{slug}/{path.lstrip('/')}"
    resp = httpx.get(url, params=params or {}, timeout=30, verify=False)
    resp.raise_for_status()
    return resp.json()


def _fetch_events(slug: str) -> list[dict]:
    today = date.today()
    end = today + timedelta(days=DAYS_AHEAD)
    return _get(slug, "Events", {
        "$filter": (
            f"EventDate ge datetime'{today.isoformat()}T00:00:00' and "
            f"EventDate le datetime'{end.isoformat()}T23:59:59'"
        ),
        "$orderby": "EventDate asc",
    })


def _fetch_items(slug: str, event_id: int) -> list[dict]:
    try:
        return _get(slug, f"Events/{event_id}/EventItems")
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (404, 400):
            return []
        raise


def _item_text(item: dict) -> str:
    parts = [
        item.get("EventItemTitle") or "",
        item.get("EventItemMatterName") or "",
        item.get("EventItemActionText") or "",
        item.get("EventItemMatterType") or "",
    ]
    return " ".join(p for p in parts if p)


def scrape_municipality(municipality: dict) -> None:
    slug = municipality["legistar_client"]
    muni_id = municipality["id"]
    name = municipality["name"]

    logger.info("[legistar] %s (%s)", name, slug)

    try:
        events = _fetch_events(slug)
    except Exception as e:
        logger.warning("[legistar] %s: failed to fetch events: %s", name, e)
        return

    for ev in events:
        agenda_status = (ev.get("EventAgendaStatusName") or "").lower()
        if agenda_status in ("", "not published", "draft"):
            continue

        meeting_date = ev.get("EventDate", "")[:10]  # "YYYY-MM-DD"
        meeting_payload = {
            "external_id":  str(ev["EventId"]),
            "title":        ev.get("EventBodyName", "Council Meeting"),
            "meeting_date": meeting_date,
            "meeting_time": ev.get("EventTime") or None,
            "location":     ev.get("EventLocation"),
            # Prefer the direct PDF; fall back to the portal page
            "agenda_url":   ev.get("EventAgendaFile") or ev.get("EventInSiteURL"),
            "status":       "scheduled",
        }

        try:
            meeting_db_id = db.upsert_meeting(muni_id, meeting_payload)
        except Exception as e:
            logger.warning("[legistar] %s: failed to upsert meeting %s: %s", name, ev["EventId"], e)
            continue

        try:
            items = _fetch_items(slug, ev["EventId"])
        except Exception as e:
            logger.warning("[legistar] %s: failed to fetch items for event %s: %s", name, ev["EventId"], e)
            continue

        for item in items:
            title = item.get("EventItemTitle") or ""
            if not title:
                continue

            attachments = [
                {
                    "name": a.get("MatterAttachmentName", ""),
                    "url":  a.get("MatterAttachmentHyperlink", ""),
                }
                for a in (item.get("EventItemMatterAttachments") or [])
            ]

            item_payload = {
                "external_id":  str(item["EventItemId"]),
                "item_number":  item.get("EventItemAgendaNumber"),
                "title":        title,
                "description":  item.get("EventItemMatterName") or item.get("EventItemActionText"),
                "attachments":  attachments,
            }

            try:
                item_db_id = db.upsert_agenda_item(meeting_db_id, item_payload)
            except Exception as e:
                logger.warning("[legistar] %s: failed to upsert item: %s", name, e)
                continue

            if item_db_id:
                matches = find_keyword_matches(_item_text(item))
                if matches:
                    logger.info(
                        "[legistar] MATCH in %s on %s: %s",
                        name, meeting_date, [kw for kw, _ in matches],
                    )
                    db.insert_keyword_matches(item_db_id, matches)
