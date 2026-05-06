"""Tests for tools/adg/adg_wiring_gap_check.py — P3 wiring gap detection.

Plan: adg-distilled-followups-c8e4a1 W2 / P3.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures: in-memory SQLite stubs that simulate ADG snapshot schema
# ---------------------------------------------------------------------------


def _make_conn(edges: list[tuple[str, str, str]], nodes: list[tuple[str, str, str]] | None = None) -> sqlite3.Connection:
    """Build an in-memory SQLite connection with edges (and optionally nodes)."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relation_type TEXT,
            symbol TEXT,
            source_file TEXT,
            target_id INTEGER,
            target_file TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO edges (relation_type, symbol, source_file) VALUES (?, ?, ?)",
        edges,
    )
    if nodes is not None:
        conn.execute(
            """
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adg_name TEXT,
                resolved_path TEXT,
                layer TEXT
            )
            """
        )
        conn.executemany(
            "INSERT INTO nodes (adg_name, resolved_path, layer) VALUES (?, ?, ?)",
            nodes,
        )
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Infrastructure helpers
# ---------------------------------------------------------------------------


def test_has_table_true():
    from tools.adg.adg_wiring_gap_check import _has_table

    conn = _make_conn([])
    assert _has_table(conn, "edges") is True
    assert _has_table(conn, "nodes") is False
    conn.close()


def test_has_table_false_on_missing():
    from tools.adg.adg_wiring_gap_check import _has_table

    conn = sqlite3.connect(":memory:")
    assert _has_table(conn, "nonexistent") is False
    conn.close()


def test_edge_cols_returns_columns():
    from tools.adg.adg_wiring_gap_check import _edge_cols

    conn = _make_conn([])
    cols = _edge_cols(conn)
    assert "relation_type" in cols
    assert "symbol" in cols
    assert "source_file" in cols
    conn.close()


# ---------------------------------------------------------------------------
# Mode 2: instantiation-orphans
# ---------------------------------------------------------------------------


def test_instantiation_orphans_clean():
    """Symbol with both instantiates AND imports edge → no orphan."""
    from tools.adg.adg_wiring_gap_check import _check_instantiation_orphans

    conn = _make_conn([
        ("instantiates", "agentic_core.L0_routing.SomeAgent", "apps_qna/runner.py"),
        ("imports", "agentic_core.L0_routing.SomeAgent", "apps_qna/runner.py"),
    ])
    result = _check_instantiation_orphans(conn)
    assert result == []
    conn.close()


def test_instantiation_orphans_detects_gap():
    """Symbol with instantiates but no imports edge → orphan."""
    from tools.adg.adg_wiring_gap_check import _check_instantiation_orphans

    conn = _make_conn([
        ("instantiates", "agentic_core.L0_routing.SomeAgent", "apps_qna/runner.py"),
    ])
    result = _check_instantiation_orphans(conn)
    assert len(result) == 1
    assert result[0]["symbol"] == "agentic_core.L0_routing.SomeAgent"
    assert result[0]["severity"] == "WARN"
    conn.close()


def test_instantiation_orphans_ignores_undotted():
    """Short (no-dot) symbol names are noise — should not be flagged."""
    from tools.adg.adg_wiring_gap_check import _check_instantiation_orphans

    conn = _make_conn([
        ("instantiates", "SomeBuiltin", "apps_qna/runner.py"),
    ])
    result = _check_instantiation_orphans(conn)
    assert result == []
    conn.close()


def test_instantiation_orphans_no_instantiates_relation():
    """If no instantiates edges exist in snapshot, returns empty list gracefully."""
    from tools.adg.adg_wiring_gap_check import _check_instantiation_orphans

    conn = _make_conn([
        ("imports", "agentic_core.some.Module", "apps_qna/runner.py"),
    ])
    result = _check_instantiation_orphans(conn)
    assert result == []
    conn.close()


# ---------------------------------------------------------------------------
# Mode 3: port-adapter-gaps
# ---------------------------------------------------------------------------


def _make_conn_with_nodes_and_edges(
    nodes: list[tuple[str, str, str]],
    edges: list[tuple[str, str, str, str | None]],
) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT,
            resolved_path TEXT,
            layer TEXT
        )
        """
    )
    conn.executemany("INSERT INTO nodes (adg_name, resolved_path, layer) VALUES (?, ?, ?)", nodes)
    conn.execute(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relation_type TEXT,
            symbol TEXT,
            source_file TEXT,
            target_id INTEGER,
            target_file TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO edges (relation_type, symbol, source_file, target_file) VALUES (?, ?, ?, ?)",
        edges,
    )
    conn.commit()
    return conn


def test_port_adapter_gaps_detects_zero_fanin():
    """Adapter module with no importer → gap."""
    from tools.adg.adg_wiring_gap_check import _check_port_adapter_gaps

    conn = _make_conn_with_nodes_and_edges(
        nodes=[("ADG::Module::apps_qna/adapters/cache_adapter.py", "apps_qna/adapters/cache_adapter.py", "L2")],
        edges=[],
    )
    result = _check_port_adapter_gaps(conn)
    assert len(result) == 1
    assert "cache_adapter" in result[0]["path"]
    assert result[0]["severity"] == "WARN"
    conn.close()


def test_port_adapter_gaps_clean_when_imported():
    """Adapter module that is imported → no gap."""
    from tools.adg.adg_wiring_gap_check import _check_port_adapter_gaps

    conn = _make_conn_with_nodes_and_edges(
        nodes=[("ADG::Module::apps_qna/adapters/cache_adapter.py", "apps_qna/adapters/cache_adapter.py", "L2")],
        edges=[
            ("imports", "apps_qna.adapters.cache_adapter.Adapter", "apps_qna/runner.py",
             "apps_qna/adapters/cache_adapter.py"),
        ],
    )
    result = _check_port_adapter_gaps(conn)
    assert result == []
    conn.close()


def test_port_adapter_gaps_skips_test_files():
    """Adapter modules under tests/ tree are excluded."""
    from tools.adg.adg_wiring_gap_check import _check_port_adapter_gaps

    conn = _make_conn_with_nodes_and_edges(
        nodes=[("ADG::Module::tests/adapters/fake_adapter.py", "tests/adapters/fake_adapter.py", "test")],
        edges=[],
    )
    result = _check_port_adapter_gaps(conn)
    assert result == []
    conn.close()


def test_port_adapter_gaps_no_nodes_table():
    """No nodes table → returns empty list (schema guard)."""
    from tools.adg.adg_wiring_gap_check import _check_port_adapter_gaps

    conn = _make_conn([])  # only edges table
    result = _check_port_adapter_gaps(conn)
    assert result == []
    conn.close()


# ---------------------------------------------------------------------------
# Mode 4: dead-imports
# ---------------------------------------------------------------------------


def test_dead_imports_detects_missing_module():
    """Import edge whose symbol has no matching node → dead import."""
    from tools.adg.adg_wiring_gap_check import _check_dead_imports

    conn = _make_conn_with_nodes_and_edges(
        nodes=[("ADG::Module::agentic_core/L0_routing/__init__.py", "agentic_core/L0_routing/__init__.py", "L0")],
        edges=[
            ("imports", "agentic_core.deleted_module.SomeClass", "apps_qna/runner.py", None),
        ],
    )
    result = _check_dead_imports(conn)
    symbols = [r["symbol"] for r in result]
    assert "agentic_core.deleted_module.SomeClass" in symbols
    assert result[0]["severity"] == "CRITICAL"
    conn.close()


def test_dead_imports_clean_when_node_present():
    """Import edge whose prefix matches a known node → not dead."""
    from tools.adg.adg_wiring_gap_check import _check_dead_imports

    conn = _make_conn_with_nodes_and_edges(
        nodes=[("ADG::Module::agentic_core/L0_routing/__init__.py", "agentic_core/L0_routing/__init__.py", "L0")],
        edges=[
            ("imports", "agentic_core.L0_routing.SomeClass", "apps_qna/runner.py", None),
        ],
    )
    result = _check_dead_imports(conn)
    assert result == []
    conn.close()


def test_dead_imports_skips_test_files():
    """Imports from test files are excluded from dead-import checks."""
    from tools.adg.adg_wiring_gap_check import _check_dead_imports

    conn = _make_conn_with_nodes_and_edges(
        nodes=[],
        edges=[
            ("imports", "totally.missing.Module", "tests/unit/test_something.py", None),
        ],
    )
    result = _check_dead_imports(conn)
    assert result == []
    conn.close()


def test_dead_imports_skips_undotted():
    """Short single-segment symbols (stdlib) not flagged."""
    from tools.adg.adg_wiring_gap_check import _check_dead_imports

    conn = _make_conn_with_nodes_and_edges(
        nodes=[],
        edges=[
            ("imports", "os", "apps_qna/runner.py", None),
        ],
    )
    result = _check_dead_imports(conn)
    assert result == []
    conn.close()


def test_dead_imports_deduplicates_by_symbol():
    """Same dead symbol imported from multiple files → appears once."""
    from tools.adg.adg_wiring_gap_check import _check_dead_imports

    conn = _make_conn_with_nodes_and_edges(
        nodes=[],
        edges=[
            ("imports", "gone.pkg.Symbol", "apps_qna/runner.py", None),
            ("imports", "gone.pkg.Symbol", "apps_rg/runner.py", None),
        ],
    )
    result = _check_dead_imports(conn)
    symbols = [r["symbol"] for r in result]
    assert symbols.count("gone.pkg.Symbol") == 1
    conn.close()


# ---------------------------------------------------------------------------
# main() CLI integration
# ---------------------------------------------------------------------------


def _make_sqlite_file(
    edges: list[tuple[str, str, str]],
    nodes: list[tuple[str, str, str]] | None = None,
) -> Path:
    """Write a real SQLite file (in tmpdir) for CLI tests."""
    tmp = Path(tempfile.mkdtemp())
    db_path = tmp / "adg_indexed_20260101_0000.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relation_type TEXT, symbol TEXT, source_file TEXT,
            target_id INTEGER, target_file TEXT
        )
        """
    )
    conn.executemany("INSERT INTO edges (relation_type, symbol, source_file) VALUES (?,?,?)", edges)
    if nodes is not None:
        conn.execute(
            """
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adg_name TEXT, resolved_path TEXT, layer TEXT
            )
            """
        )
        conn.executemany("INSERT INTO nodes (adg_name, resolved_path, layer) VALUES (?,?,?)", nodes)
    conn.commit()
    conn.close()
    return db_path


def test_main_advisory_always_exits_0(monkeypatch):
    """Advisory mode (default, no --gate) always exits 0 even with findings."""
    db = _make_sqlite_file(
        edges=[("instantiates", "some.pkg.Missing", "apps_qna/main.py")],
        nodes=[],
    )
    monkeypatch.setattr("sys.argv", ["adg_wiring_gap_check.py", "--snapshot", str(db)])
    from tools.adg.adg_wiring_gap_check import main

    rc = main()
    assert rc == 0


def test_main_gate_exits_1_on_critical_dead_imports(monkeypatch):
    """Gate mode exits 1 when dead-imports CRITICAL findings are present."""
    db = _make_sqlite_file(
        edges=[("imports", "dead.pkg.Symbol", "apps_qna/runner.py")],
        nodes=[],
    )
    monkeypatch.setattr(
        "sys.argv",
        ["adg_wiring_gap_check.py", "--snapshot", str(db), "--gate", "--mode", "dead-imports"],
    )
    from tools.adg.adg_wiring_gap_check import main

    rc = main()
    assert rc == 1


def test_main_gate_exits_0_on_clean(monkeypatch):
    """Gate mode exits 0 when no critical findings."""
    db = _make_sqlite_file(
        edges=[("imports", "agentic_core.L0_routing.Router", "apps_qna/runner.py")],
        nodes=[("ADG::Module::agentic_core/L0_routing/__init__.py", "agentic_core/L0_routing/__init__.py", "L0")],
    )
    monkeypatch.setattr(
        "sys.argv",
        ["adg_wiring_gap_check.py", "--snapshot", str(db), "--gate", "--mode", "dead-imports"],
    )
    from tools.adg.adg_wiring_gap_check import main

    rc = main()
    assert rc == 0


def test_main_missing_snapshot_returns_2(monkeypatch, tmp_path):
    """Non-existent --snapshot returns exit code 2."""
    fake = tmp_path / "does_not_exist.sqlite"
    monkeypatch.setattr("sys.argv", ["adg_wiring_gap_check.py", "--snapshot", str(fake)])
    from tools.adg.adg_wiring_gap_check import main

    rc = main()
    assert rc == 2


def test_main_no_snapshot_skips(monkeypatch, tmp_path):
    """No snapshot found → SKIP with exit 0."""

    def _no_sqlite():
        return None

    monkeypatch.setattr("tools.adg.adg_wiring_gap_check._latest_sqlite", _no_sqlite)
    monkeypatch.setattr("sys.argv", ["adg_wiring_gap_check.py"])
    from tools.adg.adg_wiring_gap_check import main

    rc = main()
    assert rc == 0


def test_main_single_mode_filter(monkeypatch):
    """--mode flag restricts to only that detection mode."""
    db = _make_sqlite_file(
        edges=[("instantiates", "some.Orphan", "apps_qna/main.py")],
        nodes=[],
    )
    monkeypatch.setattr(
        "sys.argv",
        ["adg_wiring_gap_check.py", "--snapshot", str(db), "--mode", "instantiation-orphans"],
    )
    from tools.adg.adg_wiring_gap_check import main

    rc = main()
    assert rc == 0  # advisory — always 0 without --gate


def test_main_stub_snapshot_skips_gracefully(monkeypatch, tmp_path):
    """Snapshot without edges table → SKIP with exit 0."""
    db_path = tmp_path / "adg_indexed_stub.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()
    monkeypatch.setattr("sys.argv", ["adg_wiring_gap_check.py", "--snapshot", str(db_path)])
    from tools.adg.adg_wiring_gap_check import main

    rc = main()
    assert rc == 0
