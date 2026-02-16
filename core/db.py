"""MongoDB persistence for group analysis snapshots (async via motor)."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
from pymongo.server_api import ServerApi

load_dotenv()
logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db = None


def _get_db():
    """Lazy singleton async MongoDB connection."""
    global _client, _db
    if _db is not None:
        return _db

    uri = os.getenv("MONGODB_URI")
    if not uri:
        logger.warning("MONGODB_URI not set — snapshot persistence disabled")
        return None

    _client = AsyncIOMotorClient(uri, server_api=ServerApi("1"))
    _db = _client["stock_analyze"]
    return _db


async def ensure_indexes():
    """Create indexes (call once at app startup)."""
    db = _get_db()
    if db is None:
        return
    await db["group_snapshots"].create_index(
        [("group_id", 1), ("market", 1), ("session_date", 1)],
        unique=True,
    )


async def save_snapshot(group_id: str, market: str, session_date: str,
                        symbols: list[str], rankings: list[dict]):
    """Upsert a group analysis snapshot keyed by (group_id, market, session_date)."""
    db = _get_db()
    if db is None:
        return

    now = datetime.now(timezone.utc)
    await db["group_snapshots"].update_one(
        {"group_id": group_id, "market": market, "session_date": session_date},
        {"$set": {
            "symbols": symbols,
            "rankings": rankings,
            "updated_at": now,
        }, "$setOnInsert": {
            "created_at": now,
        }},
        upsert=True,
    )
    logger.info("Snapshot saved: %s / %s / %s (%d rankings)",
                group_id, market, session_date, len(rankings))


async def get_snapshot(group_id: str, market: str, session_date: str) -> dict | None:
    """Fetch a single snapshot. Returns None if not found or DB unavailable."""
    db = _get_db()
    if db is None:
        return None

    doc = await db["group_snapshots"].find_one(
        {"group_id": group_id, "market": market, "session_date": session_date},
        {"_id": 0},
    )
    return doc


async def list_snapshot_dates(group_id: str, market: str) -> list[str]:
    """Return available session dates (descending) for a group+market."""
    db = _get_db()
    if db is None:
        return []

    cursor = db["group_snapshots"].find(
        {"group_id": group_id, "market": market},
        {"session_date": 1, "_id": 0},
    ).sort("session_date", DESCENDING)

    return [d["session_date"] async for d in cursor]
