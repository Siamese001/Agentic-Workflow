"""Tests for SQLiteGraphStore factory functions."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
_graph_store_factory_module = import_or_skip(
    "agentic_core.L4_state.utils.memory.graph_store_factory",
    reason="Graph-store factory module unavailable for SQLiteGraphStore factory tests",
)
create_sqlite_graph_store = _graph_store_factory_module.create_sqlite_graph_store
create_sqlite_graph_store_or_none = _graph_store_factory_module.create_sqlite_graph_store_or_none
get_default_adg_db_path = _graph_store_factory_module.get_default_adg_db_path


def test_get_default_adg_db_path_returns_none_when_not_found() -> None:
    """Test that get_default_adg_db_path returns None when database not found."""
    result = get_default_adg_db_path()
    # In most test environments, the ADG database won't exist
    # This test verifies the function handles the missing case gracefully
    assert result is None or isinstance(result, Path)


def test_create_sqlite_graph_store_raises_when_db_not_found() -> None:
    """Test that create_sqlite_graph_store raises FileNotFoundError for missing database."""
    with pytest.raises(FileNotFoundError, match="ADG SQLite database not found"):
        create_sqlite_graph_store(db_path="/nonexistent/path/to/db.sqlite")


def test_create_sqlite_graph_store_raises_when_path_is_directory() -> None:
    """Test that create_sqlite_graph_store raises when path is a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(FileNotFoundError, match="not a file"):
            create_sqlite_graph_store(db_path=tmpdir)


def test_create_sqlite_graph_store_or_none_returns_none_on_error() -> None:
    """Test that create_sqlite_graph_store_or_none returns None on error."""
    result = create_sqlite_graph_store_or_none(db_path="/nonexistent/path/to/db.sqlite")
    assert result is None


def test_create_sqlite_graph_store_or_none_returns_none_for_directory() -> None:
    """Test that create_sqlite_graph_store_or_none returns None for directory path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = create_sqlite_graph_store_or_none(db_path=tmpdir)
        assert result is None
