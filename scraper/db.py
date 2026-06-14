import logging
import truststore
truststore.inject_into_ssl()
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _client


def get_active_municipalities(platform: str | None = None) -> list[dict]:
    q = get_client().table("municipalities").select("*").eq("active", True)
    if platform:
        q = q.eq("platform", platform)
    return q.execute().data


def upsert_meeting(municipality_id: str, meeting: dict) -> str:
    """Insert or update a meeting. Returns the meeting's UUID."""
    row = {
        "municipality_id": municipality_id,
        "external_id":     meeting["external_id"],
        "title":           meeting["title"],
        "meeting_date":    meeting["meeting_date"],
        "meeting_time":    meeting.get("meeting_time"),
        "location":        meeting.get("location"),
        "agenda_url":      meeting.get("agenda_url"),
        "minutes_url":     meeting.get("minutes_url"),
        "status":          meeting.get("status", "scheduled"),
    }
    result = (
        get_client()
        .table("meetings")
        .upsert(row, on_conflict="municipality_id,external_id")
        .execute()
    )
    return result.data[0]["id"]


def upsert_agenda_item(meeting_id: str, item: dict) -> str | None:
    """Insert or update an agenda item. Returns the item's UUID."""
    if not item.get("external_id"):
        # Items without an ID can't be meaningfully upserted; insert only
        result = (
            get_client()
            .table("agenda_items")
            .insert({
                "meeting_id":  meeting_id,
                "item_number": item.get("item_number"),
                "title":       item["title"],
                "description": item.get("description"),
                "attachments": item.get("attachments", []),
            })
            .execute()
        )
    else:
        result = (
            get_client()
            .table("agenda_items")
            .upsert(
                {
                    "meeting_id":  meeting_id,
                    "external_id": item["external_id"],
                    "item_number": item.get("item_number"),
                    "title":       item["title"],
                    "description": item.get("description"),
                    "attachments": item.get("attachments", []),
                },
                on_conflict="meeting_id,external_id",
            )
            .execute()
        )
    return result.data[0]["id"] if result.data else None


def insert_keyword_matches(agenda_item_id: str, matches: list[tuple[str, str]]) -> None:
    if not matches:
        return
    # Avoid duplicates: delete existing matches for this item then re-insert
    get_client().table("keyword_matches").delete().eq("agenda_item_id", agenda_item_id).execute()
    rows = [
        {"agenda_item_id": agenda_item_id, "keyword": kw, "matched_text": ctx}
        for kw, ctx in matches
    ]
    get_client().table("keyword_matches").insert(rows).execute()
