"""Shared SQLite helpers for ADG materialized-view materialization.

Centralizes path validation and connection tuning so every phase uses the same
WAL + bulk-write pragmas (plan: reduce MV refresh wall-clock without changing
query semantics).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def validate_sqlite_path(sqlite_path: Path) -> Path:
    """Resolve and validate the ADG SQLite file path."""
    sqlite_path = sqlite_path.expanduser().resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"ADG SQLite not found: {sqlite_path}")
    if not sqlite_path.is_file():
        raise ValueError(f"ADG SQLite path is not a file: {sqlite_path}")
    return sqlite_path


def connect_sqlite_for_mv(sqlite_path: Path, *, timeout: float = 30.0) -> sqlite3.Connection:
    """Open SQLite for MV refresh: WAL durability with faster bulk DDL/DML.

    ``synchronous=NORMAL`` is appropriate for local artifact regeneration (WAL
    already provides crash safety for readers). ``temp_store=MEMORY`` keeps
    large CREATE AS SELECT spills off disk where possible.
    """
    conn = sqlite3.connect(str(validate_sqlite_path(sqlite_path)), timeout=timeout)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn
