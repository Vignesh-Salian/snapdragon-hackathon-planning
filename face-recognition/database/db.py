"""SQLite donor store (stdlib sqlite3 — no ORM needed for two queries).

Landmarks are stored as JSON text. `enrolled_at` is indexed so the 56-day
lockout lookup stays fast at 1k+ donors.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = os.getenv("DONORS_DB", "donors.db")
LOCKOUT_DAYS = 56  # clinical minimum gap between whole-blood donations


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS donors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                enrolled_at TEXT NOT NULL,
                landmarks TEXT NOT NULL
            )
            """
        )
        c.execute("CREATE INDEX IF NOT EXISTS idx_enrolled_at ON donors(enrolled_at)")


def add_donor(name: str, landmarks: list[float]) -> int:
    ts = datetime.now(timezone.utc).isoformat()
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO donors (name, enrolled_at, landmarks) VALUES (?, ?, ?)",
            (name, ts, json.dumps(landmarks)),
        )
        return int(cur.lastrowid)


def recent_donors(days: int = LOCKOUT_DAYS) -> list[dict]:
    """Donors enrolled within the lockout window (the only ones worth comparing)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with _conn() as c:
        rows = c.execute(
            "SELECT id, name, enrolled_at, landmarks FROM donors WHERE enrolled_at >= ?",
            (cutoff,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "enrolled_at": r["enrolled_at"],
            "landmarks": json.loads(r["landmarks"]),
        }
        for r in rows
    ]
