"""SQLiteGraphStore Factory and Configuration.

Provides factory functions and configuration for instantiating SQLiteGraphStore
with the ADG SQLite database. This serves as the integration point for
wiring the graph store into the system.
"""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_core.L4_state.utils.memory.graph_knowledge_store import SQLiteGraphStore

logger = logging.getLogger(__name__)

# Default ADG SQLite database path (relative to repository root)
_DEFAULT_ADG_DB_PATH = "artifacts/adg/adg_indexed.sqlite"


def get_default_adg_db_path() -> Path | None:
    """Get the default ADG SQLite database path.

    Checks for the ADG database in the standard artifacts location.

    Returns:
        Path to the ADG SQLite database, or None if not found
    """
    # Try repository root relative path
    db_path = Path(_DEFAULT_ADG_DB_PATH)

    if db_path.exists() and db_path.is_file():
        logger.info("[SQLiteGraphStore Factory] Found ADG database at: %s", db_path)
        return db_path

    # Try absolute path from current working directory
    cwd_db_path = Path.cwd() / _DEFAULT_ADG_DB_PATH
    if cwd_db_path.exists() and cwd_db_path.is_file():
        logger.info("[SQLiteGraphStore Factory] Found ADG database at: %s", cwd_db_path)
        return cwd_db_path

    logger.warning(
        "[SQLiteGraphStore Factory] ADG database not found at %s or %s",
        db_path,
        cwd_db_path,
    )
    return None


def create_sqlite_graph_store(
    db_path: str | Path | None = None,
) -> SQLiteGraphStore:
    """Create a SQLiteGraphStore instance.

    Args:
        db_path: Path to the ADG SQLite database. If None, uses default path.

    Returns:
        SQLiteGraphStore instance

    Raises:
        FileNotFoundError: If the database file doesn't exist
    """
    if db_path is None:
        db_path = get_default_adg_db_path()

    if db_path is None:
        raise FileNotFoundError(
            "ADG SQLite database not found. Please provide db_path or ensure "
            "the database exists at the default location.",
        )

    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"ADG SQLite database not found at: {db_path}")

    logger.info("[SQLiteGraphStore Factory] Creating SQLiteGraphStore with: %s", db_path)

    return SQLiteGraphStore(db_path=str(db_path))


def create_sqlite_graph_store_or_none(
    db_path: str | Path | None = None,
) -> SQLiteGraphStore | None:
    """Create a SQLiteGraphStore instance, returning None if database not found.

    This is a convenience function for optional graph store initialization.

    Args:
        db_path: Path to the ADG SQLite database. If None, uses default path.

    Returns:
        SQLiteGraphStore instance, or None if database not found
    """
    try:
        return create_sqlite_graph_store(db_path)
    except FileNotFoundError as e:
        logger.warning("[SQLiteGraphStore Factory] Failed to create graph store: %s", e)
        return None


__all__ = [
    "create_sqlite_graph_store",
    "create_sqlite_graph_store_or_none",
    "get_default_adg_db_path",
]
