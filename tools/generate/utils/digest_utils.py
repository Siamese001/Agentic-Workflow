"""Digest and ratio utilities for ADG generation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 1.0
    return round(numerator / denominator, 4)


def _stable_digest(payload: object) -> str:
    text = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sqlite_table_digest(sqlite_path: Path, table_name: str) -> str:
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    col_rows = cur.execute(f"PRAGMA table_info({table_name})").fetchall()
    columns = [row[1] for row in col_rows]
    if not columns:
        conn.close()
        return ""
    order_by = "id" if "id" in columns else ", ".join(columns)
    rows = cur.execute(f"SELECT {', '.join(columns)} FROM {table_name} ORDER BY {order_by}").fetchall()
    conn.close()
    return _stable_digest(rows)
