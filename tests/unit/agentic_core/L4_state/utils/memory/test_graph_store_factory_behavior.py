"""Behavioral tests for ``agentic_core.L4_state.utils.memory.graph_store_factory``.

Covers:
- get_default_adg_db_path: returns Path when file exists at relative path;
  falls back to cwd-relative path; returns None when neither exists.
- create_sqlite_graph_store: delegates to SQLiteGraphStore(db_path=<str>);
  raises FileNotFoundError when default resolution yields None;
  raises FileNotFoundError when explicit path doesn't exist.
- create_sqlite_graph_store_or_none: returns instance on success;
  returns None when file missing (swallows FileNotFoundError).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L4_state.utils.memory import graph_store_factory as mod
from agentic_core.L4_state.utils.memory.graph_store_factory import (
    create_sqlite_graph_store,
    create_sqlite_graph_store_or_none,
    get_default_adg_db_path,
)


# ---- get_default_adg_db_path --------------------------------------------

class TestGetDefaultAdgDbPath:
    def test_returns_path_when_relative_exists(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Build the expected relative path under tmp cwd and create it
        monkeypatch.chdir(tmp_path)
        db = tmp_path / "artifacts" / "adg" / "adg_indexed.sqlite"
        db.parent.mkdir(parents=True)
        db.touch()
        result = get_default_adg_db_path()
        assert result is not None
        assert result.name == "adg_indexed.sqlite"

    def test_returns_none_when_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)  # empty dir
        assert get_default_adg_db_path() is None

    def test_rejects_if_path_is_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        # Create a directory at the expected db location, not a file
        (tmp_path / "artifacts" / "adg" / "adg_indexed.sqlite").mkdir(parents=True)
        # Neither branch (relative nor cwd) should accept a directory
        assert get_default_adg_db_path() is None


# ---- create_sqlite_graph_store ------------------------------------------

class TestCreateSqliteGraphStore:
    def test_explicit_path_delegates_to_store(self, tmp_path: Path) -> None:
        db = tmp_path / "adg.sqlite"
        db.touch()
        with patch.object(mod, "SQLiteGraphStore") as Store:
            Store.return_value = MagicMock(name="store_instance")
            result = create_sqlite_graph_store(db_path=db)
        Store.assert_called_once_with(db_path=str(db))
        assert result is Store.return_value

    def test_explicit_path_accepts_str(self, tmp_path: Path) -> None:
        db = tmp_path / "adg.sqlite"
        db.touch()
        with patch.object(mod, "SQLiteGraphStore") as Store:
            create_sqlite_graph_store(db_path=str(db))
        Store.assert_called_once_with(db_path=str(db))

    def test_missing_explicit_path_raises(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope.sqlite"
        with pytest.raises(FileNotFoundError, match="not found"):
            create_sqlite_graph_store(db_path=missing)

    def test_default_resolution_miss_raises(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)  # no artifacts/ here
        with pytest.raises(FileNotFoundError, match="ADG SQLite database not found"):
            create_sqlite_graph_store(db_path=None)

    def test_default_resolution_hit_delegates(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        db = tmp_path / "artifacts" / "adg" / "adg_indexed.sqlite"
        db.parent.mkdir(parents=True)
        db.touch()
        with patch.object(mod, "SQLiteGraphStore") as Store:
            create_sqlite_graph_store(db_path=None)
        # Called with *some* string path ending in our db filename
        call_path = Store.call_args.kwargs["db_path"]
        assert call_path.endswith("adg_indexed.sqlite")


# ---- create_sqlite_graph_store_or_none ----------------------------------

class TestCreateOrNone:
    def test_returns_instance_on_success(self, tmp_path: Path) -> None:
        db = tmp_path / "adg.sqlite"
        db.touch()
        with patch.object(mod, "SQLiteGraphStore") as Store:
            Store.return_value = MagicMock(name="store_instance")
            result = create_sqlite_graph_store_or_none(db_path=db)
        assert result is Store.return_value

    def test_returns_none_on_missing(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.sqlite"
        assert create_sqlite_graph_store_or_none(db_path=missing) is None

    def test_returns_none_on_default_miss(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert create_sqlite_graph_store_or_none(db_path=None) is None

    def test_only_catches_file_not_found(self, tmp_path: Path) -> None:
        """Other errors from SQLiteGraphStore construction must propagate."""
        db = tmp_path / "adg.sqlite"
        db.touch()
        with patch.object(mod, "SQLiteGraphStore", side_effect=RuntimeError("init-failed")):
            with pytest.raises(RuntimeError, match="init-failed"):
                create_sqlite_graph_store_or_none(db_path=db)
