"""Unit tests for ``ADGNodeResolver`` used by ``ingest_code``.

Verifies the tail-of-adg-name indexing rule (ADG stores qualified names like
``ADG::Symbol::pkg.sub.Module.ClassName``; chunks only know the terminal
symbol name) and the graceful-degradation contract.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tools.ingestion.ingest_code import ADGNodeResolver


@pytest.fixture(name="resolver_db")
def _resolver_db(tmp_path: Path) -> Path:
    db = tmp_path / "adg.sqlite"
    conn = sqlite3.connect(db)
    try:
        conn.execute(
            """
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                entity_type TEXT,
                layer TEXT,
                identity_kind TEXT,
                confidence REAL,
                resolved_path TEXT,
                precision_type TEXT,
                span_start INT, span_end INT, span_line INT,
                span_column INT, span_end_line INT, span_end_column INT,
                logical_sequence_id TEXT, control_path_id TEXT, temporal_order INT,
                type_surface TEXT, enclosing_symbol TEXT
            )
            """
        )
        conn.executemany(
            "INSERT INTO nodes (id, adg_name, resolved_path) VALUES (?, ?, ?)",
            [
                (101, "ADG::Symbol::pkg.sub.mod.MyClass", "pkg/sub/mod.py"),
                (102, "ADG::Symbol::pkg.sub.mod.my_func", "pkg/sub/mod.py"),
                (103, "ADG::Module::pkg/sub/mod.py", "pkg/sub/mod.py"),
                (104, "ADG::Symbol::other.module.MyClass", "other/module.py"),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return db


def test_resolver_matches_on_file_and_tail(resolver_db: Path) -> None:
    resolver = ADGNodeResolver(resolver_db)
    assert resolver.resolve(Path("/x/pkg/sub/mod.py"), "MyClass") == 101
    assert resolver.resolve(Path("/x/pkg/sub/mod.py"), "my_func") == 102


def test_resolver_prefers_scoped_match_over_global(resolver_db: Path) -> None:
    resolver = ADGNodeResolver(resolver_db)
    # MyClass exists in both files; scoped lookup must win for the matching file.
    assert resolver.resolve(Path("/a/other/module.py"), "MyClass") == 104


def test_resolver_returns_none_for_unknown_symbol(resolver_db: Path) -> None:
    resolver = ADGNodeResolver(resolver_db)
    assert resolver.resolve(Path("/x/pkg/sub/mod.py"), "does_not_exist") is None


def test_resolver_degrades_when_path_missing(tmp_path: Path) -> None:
    missing = tmp_path / "not_there.sqlite"
    resolver = ADGNodeResolver(missing)
    assert resolver.resolve(Path("/x/a.py"), "anything") is None


def test_resolver_handles_none_path() -> None:
    resolver = ADGNodeResolver(None)
    assert resolver.resolve(Path("/x/a.py"), "anything") is None
