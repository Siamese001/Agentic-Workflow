"""Shared SQLite helpers for ADG materialized-view materialization.

Centralizes path validation and connection tuning so every phase uses the same
WAL, integrity, and bulk-write settings.
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


def connect_sqlite_for_mv(
    sqlite_path: Path,
    *,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """Open SQLite for MV refresh with bounded contention and FK enforcement.

    ``synchronous=NORMAL`` is appropriate for a locally regenerated WAL artifact.
    ``temp_store=MEMORY`` and a 64 MiB page-cache target accelerate the large
    CREATE-AS-SELECT phases without changing query semantics.
    """

    conn = sqlite3.connect(str(validate_sqlite_path(sqlite_path)), timeout=timeout)
    conn.execute(f"PRAGMA busy_timeout = {max(1, int(timeout * 1000))}")
    conn.execute("PRAGMA trusted_schema = OFF")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -65536")
    return conn
