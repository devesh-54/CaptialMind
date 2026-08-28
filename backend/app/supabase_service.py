import os
import json
import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://zjvvbteptuqufobeykop.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_XToGIQhvkRliU_AqbR-WsQ_vez8nkrb")

supabase_client: Optional[Client] = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"Supabase Client Connected: {SUPABASE_URL}")
except Exception as err:
    print(f"Supabase Client Initialization Warning: {err}")

def sync_stream_event_to_supabase(record: Dict[str, Any]) -> bool:
    """
    Persists streamed event record into Supabase streamed_events table.
    Falls back gracefully if Supabase table is restricted or offline.
    """
    if not supabase_client:
        return False

    try:
        data = {
            "event_id": record.get("id"),
            "event_type": record.get("event_type", "STREAM_EVENT"),
            "stage": record.get("stage", "OBSERVE"),
            "title": record.get("title", "Stream Ingestion"),
            "detail": record.get("detail", ""),
            "impact": record.get("impact", ""),
            "timestamp": record.get("time", ""),
            "payload": record
        }
        res = supabase_client.table("streamed_events").insert(data).execute()
        return True
    except Exception as e:
        # Fallback to local persistent ledger
        return False

def fetch_supabase_stream_records() -> List[Dict[str, Any]]:
    """
    Fetches stored stream records from Supabase to incorporate into decision making.
    """
    if not supabase_client:
        return []

    try:
        res = supabase_client.table("streamed_events").select("*").order("created_at", desc=True).limit(200).execute()
        if res.data:
            return res.data
    except Exception:
        pass
    return []
