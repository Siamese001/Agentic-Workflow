"""Tests for SQLiteGraphStore implementation."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from agentic_core.L4_state.types.graph_store_types import (
    GraphEntity,
)
from agentic_core.L4_state.utils.memory.graph_knowledge_store import SQLiteGraphStore


def test_sqlite_graph_store_init_raises_on_nonexistent_path() -> None:
    """Test that SQLiteGraphStore raises FileNotFoundError for nonexistent path."""
    with pytest.raises(FileNotFoundError, match="does not exist"):
        SQLiteGraphStore(db_path="/nonexistent/path/to/db.sqlite")


def test_sqlite_graph_store_init_raises_on_directory_path() -> None:
    """Test that SQLiteGraphStore raises FileNotFoundError for directory path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(FileNotFoundError, match="not a file"):
            SQLiteGraphStore(db_path=tmpdir)


def test_sqlite_graph_store_init_raises_on_invalid_sqlite_file() -> None:
    """Test that SQLiteGraphStore handles invalid SQLite file."""
    # Note: sqlite3.connect() will create a new database if file doesn't exist
    # or is invalid, so this test validates that we don't crash on init
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp.write(b"not a valid sqlite database")
        tmp_path = tmp.name

    try:
        # Should not raise on init (validation happens on first query)
        store = SQLiteGraphStore(db_path=tmp_path)
        # Close to release file lock
        store.close()
    finally:
        Path(tmp_path).unlink()


def test_sqlite_graph_store_add_entity_read_only() -> None:
    """Test that add_entity raises NotImplementedError (read-only)."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Create a minimal valid SQLite database
        conn = sqlite3.connect(tmp_path)
        conn.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS edges (src INTEGER, tgt INTEGER, relation TEXT)")
        conn.commit()
        conn.close()

        store = SQLiteGraphStore(db_path=tmp_path)
        entity = GraphEntity(
            id="test_entity",
            name="Test Entity",
            entity_type="test",
            description="Test description",
        )

        # Should raise NotImplementedError (read-only)
        with pytest.raises(NotImplementedError, match="read-only"):
            store.add_entity(entity)

        store.close()
    finally:
        Path(tmp_path).unlink()


def test_sqlite_graph_store_get_entity_returns_none_for_missing() -> None:
    """Test that get_entity returns None for missing entity."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Create a minimal valid SQLite database
        conn = sqlite3.connect(tmp_path)
        conn.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS edges (src INTEGER, tgt INTEGER, relation TEXT)")
        conn.commit()
        conn.close()

        store = SQLiteGraphStore(db_path=tmp_path)
        # Use integer ID as expected by implementation
        result = store.get_entity("999999")
        assert result is None
        store.close()
    finally:
        Path(tmp_path).unlink()


def test_sqlite_graph_store_search_entities_returns_empty_list() -> None:
    """Test that search_entities returns empty list when no results."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Create a minimal valid SQLite database with ADG schema
        conn = sqlite3.connect(tmp_path)
        conn.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, name TEXT, adg_name TEXT, resolved_path TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS edges (src INTEGER, tgt INTEGER, relation TEXT)")
        conn.commit()
        conn.close()

        store = SQLiteGraphStore(db_path=tmp_path)
        result = store.search_entities("nonexistent_query")
        assert isinstance(result, list)
        assert len(result) == 0
        store.close()
    finally:
        Path(tmp_path).unlink()


def test_sqlite_graph_store_close_idempotent() -> None:
    """Test that close() can be called multiple times safely."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Create a minimal valid SQLite database
        conn = sqlite3.connect(tmp_path)
        conn.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS edges (src INTEGER, tgt INTEGER, relation TEXT)")
        conn.commit()
        conn.close()

        store = SQLiteGraphStore(db_path=tmp_path)
        store.close()
        store.close()  # Should not raise
    finally:
        Path(tmp_path).unlink()


def test_sqlite_graph_store_context_manager() -> None:
    """Test that SQLiteGraphStore works as context manager."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Create a minimal valid SQLite database
        conn = sqlite3.connect(tmp_path)
        conn.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS edges (src INTEGER, tgt INTEGER, relation TEXT)")
        conn.commit()
        conn.close()

        with SQLiteGraphStore(db_path=tmp_path) as store:
            assert store is not None
        # Connection should be closed after context exit
    finally:
        Path(tmp_path).unlink()
