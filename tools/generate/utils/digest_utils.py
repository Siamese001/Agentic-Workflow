"""Digest and ratio utilities for ADG generation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


def _validate_sqlite_path(sqlite_path: Path) -> Path:
    sqlite_path = sqlite_path.expanduser().resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite artifact not found: {sqlite_path}")
    if not sqlite_path.is_file():
        raise ValueError(f"SQLite artifact is not a file: {sqlite_path}")
    return sqlite_path


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
    sqlite_path = _validate_sqlite_path(sqlite_path)
    with sqlite3.connect(str(sqlite_path), timeout=30) as conn:
        cur = conn.cursor()
        col_rows = cur.execute(f"PRAGMA table_info({table_name})").fetchall()
        columns = [row[1] for row in col_rows]
        if not columns:
            return ""
        order_by = "id" if "id" in columns else ", ".join(columns)
        rows = cur.execute(f"SELECT {', '.join(columns)} FROM {table_name} ORDER BY {order_by}").fetchall()
    return _stable_digest(rows)
