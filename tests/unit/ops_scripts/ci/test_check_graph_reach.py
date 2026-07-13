from __future__ import annotations

import sqlite3

import pytest

from ops_scripts.ci import check_graph_reach

pytestmark = pytest.mark.unit


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "create table nodes(id int primary key, layer text, entity_type text, resolved_path text, adg_name text)"
    )
    conn.execute("create table edges(src_id int, dst_id int, relation_type text)")
    return conn


def _node(conn: sqlite3.Connection, node_id: int, layer: str, path: str) -> None:
    conn.execute(
        "insert into nodes values (?, ?, ?, ?, ?)",
        (node_id, layer, "module", path, f"ADG::Module::{path}"),
    )


def _symbol(conn: sqlite3.Connection, node_id: int, layer: str, path: str, name: str) -> None:
    conn.execute(
        "insert into nodes values (?, ?, ?, ?, ?)",
        (node_id, layer, "symbol", path, f"ADG::Symbol::{name}"),
    )


def test_graph_reach_ignores_apps_layer_for_core_l0_reachability(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check_graph_reach, "_source_file_exists", lambda _path: True)
    conn = _conn()
    _node(conn, 1, "L0", "agentic_core/L0_routing/entry.py")
    _node(conn, 2, "L_APP", "apps_rg/runtime/orphan.py")

    violations = check_graph_reach.GraphReachGate().run(conn)

    assert violations == []


def test_graph_reach_still_flags_unreachable_core_module(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check_graph_reach, "_source_file_exists", lambda _path: True)
    conn = _conn()
    _node(conn, 1, "L0", "agentic_core/L0_routing/entry.py")
    _node(conn, 2, "L5", "agentic_core/L5_safety/orphan.py")

    violations = check_graph_reach.GraphReachGate().run(conn)

    assert len(violations) == 1
    assert violations[0].subject == "agentic_core/L5_safety/orphan.py"


def test_graph_reach_accepts_core_module_reachable_from_l0(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check_graph_reach, "_source_file_exists", lambda _path: True)
    conn = _conn()
    _node(conn, 1, "L0", "agentic_core/L0_routing/entry.py")
    _node(conn, 2, "L5", "agentic_core/L5_safety/reachable.py")
    conn.execute("insert into edges values (?, ?, ?)", (1, 2, "imports"))

    violations = check_graph_reach.GraphReachGate().run(conn)

    assert violations == []


def test_graph_reach_accepts_module_when_l0_reaches_symbol_in_same_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(check_graph_reach, "_source_file_exists", lambda _path: True)
    conn = _conn()
    _node(conn, 1, "L0", "agentic_core/L0_routing/entry.py")
    _node(conn, 2, "L1", "agentic_core/L1_cognition/reachable.py")
    _symbol(
        conn,
        3,
        "L1",
        "agentic_core/L1_cognition/reachable.py",
        "agentic_core.L1_cognition.reachable.ExportedSymbol",
    )
    conn.execute("insert into edges values (?, ?, ?)", (1, 3, "imports"))

    violations = check_graph_reach.GraphReachGate().run(conn)

    assert violations == []


def test_graph_reach_follows_module_imports_after_reaching_exported_symbol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(check_graph_reach, "_source_file_exists", lambda _path: True)
    conn = _conn()
    _node(conn, 1, "L0", "agentic_core/L0_routing/entry.py")
    _node(conn, 2, "L_PG", "agentic_core/prompt_governance/__init__.py")
    _symbol(
        conn,
        3,
        "L_PG",
        "agentic_core/prompt_governance/__init__.py",
        "agentic_core.prompt_governance.get_bundled_mixin",
    )
    _node(conn, 4, "L_PG", "agentic_core/prompt_governance/mixins.py")
    _symbol(
        conn,
        5,
        "L_PG",
        "agentic_core/prompt_governance/mixins.py",
        "agentic_core.prompt_governance.mixins.get_bundled_mixin",
    )
    conn.execute("insert into edges values (?, ?, ?)", (1, 3, "imports"))
    conn.execute("insert into edges values (?, ?, ?)", (2, 5, "imports"))

    violations = check_graph_reach.GraphReachGate().run(conn)

    assert violations == []
