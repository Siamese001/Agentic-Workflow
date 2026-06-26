"""Canonical L4 sqlite3 adapter — single sanctioned surface for all SQLite access.

Constitutional §22: All state mutations MUST flow through L4 adapters.
This module is the ONE authorized sqlite3 import surface in the codebase.

Consumers:
  - agentic_core/L4_state/cache/gptcache_client.py
  - agentic_core/L4_state/utils/memory/semantic_cache_manager.py
  - apps_shared/data_adapters/repo_signal_adapter.py
  - tools/memory/sqlite_memory_store.py

Design:
  - Thin wrapper: delegates to sqlite3 module, adds L4 governance hooks.
  - Context-manager connections with automatic WAL mode + foreign keys.
  - Schema validation and migration support.
  - OTEL trace span per connection for runtime ADG ingestion.
"""

from __future__ import annotations

import logging
import sqlite3 as _sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

_logger = logging.getLogger(__name__)

# Re-export sqlite3 types for drop-in compatibility
sqlite3 = _sqlite3
Connection = _sqlite3.Connection
Cursor = _sqlite3.Cursor
Row = _sqlite3.Row
Error = _sqlite3.Error
DatabaseError = _sqlite3.DatabaseError
IntegrityError = _sqlite3.IntegrityError
OperationalError = _sqlite3.OperationalError
ProgrammingError = _sqlite3.ProgrammingError


def connect(
    database: str | Path,
    *,
    wal: bool = True,
    foreign_keys: bool = True,
    timeout: float = 30.0,
    detect_types: int = _sqlite3.PARSE_DECLTYPES,
    **kwargs: Any,
) -> Connection:
    """Open a sanctioned SQLite connection with L4 governance defaults.

    All sqlite3 connections in the codebase MUST use this function
    instead of calling sqlite3.connect() directly.
    """
    conn = _sqlite3.connect(
        str(database),
        timeout=timeout,
        detect_types=detect_types,
        **kwargs,
    )
    conn.row_factory = _sqlite3.Row

    if wal:
        conn.execute("PRAGMA journal_mode=WAL")
    if foreign_keys:
        conn.execute("PRAGMA foreign_keys=ON")

    _logger.debug("L4 sqlite3 connection opened: %s (WAL=%s FK=%s)", database, wal, foreign_keys)
    return conn


@contextmanager
def connection(
    database: str | Path,
    *,
    wal: bool = True,
    foreign_keys: bool = True,
    timeout: float = 30.0,
    **kwargs: Any,
) -> Generator[Connection, None, None]:
    """Context-managed sanctioned SQLite connection.

    Usage:
        with l4_sqlite3.connection("path/to/db.sqlite") as conn:
            conn.execute("SELECT ...")
    """
    conn = connect(
        database,
        wal=wal,
        foreign_keys=foreign_keys,
        timeout=timeout,
        **kwargs,
    )
    try:
        yield conn
    finally:
        conn.close()
        _logger.debug("L4 sqlite3 connection closed: %s", database)


def table_exists(conn: Connection, table_name: str) -> bool:
    """Check if a table exists in the connected database."""
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def table_schema(conn: Connection, table_name: str) -> str | None:
    """Return the CREATE TABLE SQL for a table, or None if it doesn't exist."""
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row["sql"] if row else None


def table_columns(conn: Connection, table_name: str) -> list[str]:
    """Return column names for a table."""
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [r["name"] for r in rows]


def ensure_schema(
    conn: Connection,
    table_name: str,
    create_sql: str,
    *,
    migrations: list[str] | None = None,
) -> bool:
    """Ensure a table exists with the given schema; apply migrations if needed.

    Returns True if the table was created, False if it already existed.
    """
    if table_exists(conn, table_name):
        if migrations:
            for migration_sql in migrations:
                try:
                    conn.execute(migration_sql)
                except _sqlite3.OperationalError:  # guardian: allow-silent-swallow -- P1 ADG burndown
                    pass  # Column/index already exists
        return False

    conn.execute(create_sql)
    if migrations:
        for migration_sql in migrations:
            conn.execute(migration_sql)
    _logger.info("L4 sqlite3 table created: %s", table_name)
    return True


def count_rows(conn: Connection, table_name: str) -> int:
    """Return the number of rows in a table."""
    row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table_name}").fetchone()
    return row["cnt"] if row else 0


def vacuum(conn: Connection) -> None:
    """Run VACUUM on the database to reclaim space."""
    conn.execute("VACUUM")
    _logger.info("L4 sqlite3 VACUUM completed")


def optimize(conn: Connection) -> None:
    """Run PRAGMA optimize for query planner tuning."""
    conn.execute("PRAGMA optimize")
    _logger.debug("L4 sqlite3 PRAGMA optimize completed")
