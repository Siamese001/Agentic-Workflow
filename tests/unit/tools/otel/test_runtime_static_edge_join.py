"""W2.0/W2.1: runtime v_runtime_proof must link static_edge_id via path/name fallback."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from agentic_core.adg.artifact.edge_authority import SQL_CREATE_V_RUNTIME_PROOF
from tools.otel.runtime_view_builder import (
    _resolve_static_edge_id,
    _select_static_edge_id,
    build_runtime_view,
    runtime_static_edge_linkage_counts,
)


def _mini_static_db(tmp_path: Path) -> tuple[sqlite3.Connection, Path]:
    db = tmp_path / "mini_adg.sqlite"
    con = sqlite3.connect(str(db))
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL DEFAULT 'module',
            layer TEXT NOT NULL DEFAULT 'L2',
            identity_kind TEXT NOT NULL DEFAULT 'path',
            confidence REAL NOT NULL DEFAULT 1.0,
            resolved_path TEXT NOT NULL
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT NOT NULL DEFAULT 'AST',
            bucket TEXT NOT NULL DEFAULT 'static',
            authority TEXT NOT NULL DEFAULT 'verified'
        );
        INSERT INTO nodes (id, adg_name, resolved_path) VALUES
            (1, 'pkg.mod_a', 'apps/demo/mod_a.py'),
            (2, 'pkg.mod_b', 'apps/demo/mod_b.py');
        INSERT INTO edges (id, src_id, dst_id, relation_type, bucket) VALUES
            (10, 1, 2, 'imports', 'static');
        """
    )
    con.executescript(SQL_CREATE_V_RUNTIME_PROOF)
    return con, db


def test_negative_control_adg_name_only_labels_miss(tmp_path: Path) -> None:
    """Path-shaped runtime labels must not match unrelated static nodes."""
    con, _db = _mini_static_db(tmp_path)
    # Path labels that do not equal dotted adg_name — old adg_name-only join returned None.
    assert (
        _select_static_edge_id(
            con,
            src_name="apps/demo/mod_a.py",
            dst_name="apps/demo/mod_b.py",
            relation_type="imports",
        )
        is not None
    )
    # Wrong paths still miss.
    assert (
        _resolve_static_edge_id(
            con,
            src_name="totally/wrong.py",
            dst_name="apps/demo/mod_b.py",
            relation_type="imports",
        )
        is None
    )
    con.close()


def test_path_fallback_sets_static_edge_id_on_build(tmp_path: Path) -> None:
    con, db_path = _mini_static_db(tmp_path)
    payloads = [
        {
            "snapshot_id": "snap-1",
            "trace_id": "trace-abc",
            "nodes": [
                {"node_id": "n1", "name": "apps/demo/mod_a.py"},
                {"node_id": "n2", "name": "apps/demo/mod_b.py", "started_at_utc": 1_700_000_000_000},
            ],
            "edges": [
                {"src_id": "n1", "dst_id": "n2", "relation": "imports"},
            ],
            "metadata": {"run_id": "run-1"},
        }
    ]
    stats = build_runtime_view(db_path, explicit_payloads=payloads)
    assert stats.error is None
    assert stats.rows_written >= 1 or stats.rows_updated >= 1

    row = con.execute(
        "SELECT static_edge_id FROM v_runtime_proof WHERE attesting_trace_count >= 1"
    ).fetchone()
    assert row is not None
    assert row[0] == 10

    total, linked = runtime_static_edge_linkage_counts(con)
    assert total >= 1
    assert linked >= 1
    con.close()


def test_parent_child_runtime_rel_can_map_to_static_imports(tmp_path: Path) -> None:
    con, _db = _mini_static_db(tmp_path)
    edge_id = _resolve_static_edge_id(
        con,
        src_name="apps/demo/mod_a.py",
        dst_name="apps/demo/mod_b.py",
        relation_type="parent_child",
    )
    assert edge_id == 10
    con.close()
