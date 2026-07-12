"""Exact row-membership regression tests for Phase D materialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from tools.generate.materialized_views.phase_d_snapshot_regression import materialize_phase_d


def _create_db(path: Path, snapshot_id: str) -> Path:
    conn = sqlite3.connect(str(path))
    conn.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL DEFAULT 'module',
            layer TEXT NOT NULL DEFAULT '',
            resolved_path TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            source_file TEXT NOT NULL DEFAULT '',
            line_no INTEGER NOT NULL DEFAULT 0,
            symbol TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER NOT NULL
        );
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE mv_path_criticality_rollup (
            snapshot_id TEXT NOT NULL,
            node_id INTEGER NOT NULL,
            adg_name TEXT NOT NULL,
            layer TEXT NOT NULL,
            resolved_path TEXT NOT NULL,
            criticality_score REAL NOT NULL
        );
        CREATE TABLE mv_write_sovereignty_paths (
            snapshot_id TEXT NOT NULL,
            edge_id INTEGER NOT NULL,
            writer_file TEXT NOT NULL,
            writer_layer TEXT NOT NULL,
            write_symbol TEXT NOT NULL,
            write_line INTEGER NOT NULL,
            source_file TEXT NOT NULL,
            is_uwg_routed INTEGER NOT NULL,
            is_direct_infra_write INTEGER NOT NULL,
            severity TEXT NOT NULL
        );
        CREATE TABLE mv_debt_concentration_hotspots (
            total_debt_score REAL NOT NULL
        );
        """
    )
    conn.execute("INSERT INTO meta(key, value) VALUES ('commit_sha', ?)", (snapshot_id,))
    conn.execute("INSERT INTO mv_debt_concentration_hotspots VALUES (2.0)")
    conn.commit()
    conn.close()
    return path


def _node(conn: sqlite3.Connection, node_id: int, name: str, layer: str, path: str) -> None:
    conn.execute(
        "INSERT INTO nodes(id, adg_name, entity_type, layer, resolved_path) "
        "VALUES (?, ?, 'module', ?, ?)",
        (node_id, name, layer, path),
    )


def _edge(
    conn: sqlite3.Connection,
    src_id: int,
    dst_id: int,
    relation_type: str,
    *,
    source_file: str,
    line_no: int = 1,
    symbol: str = "",
) -> int:
    cur = conn.execute(
        "INSERT INTO edges(src_id, dst_id, relation_type, source_file, line_no, symbol) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (src_id, dst_id, relation_type, source_file, line_no, symbol),
    )
    return int(cur.lastrowid)


def _critical(
    conn: sqlite3.Connection,
    snapshot_id: str,
    node_id: int,
    name: str,
    layer: str,
    path: str,
    score: float,
) -> None:
    conn.execute(
        "INSERT INTO mv_path_criticality_rollup VALUES (?, ?, ?, ?, ?, ?)",
        (snapshot_id, node_id, name, layer, path, score),
    )


def _bypass(
    conn: sqlite3.Connection,
    snapshot_id: str,
    edge_id: int,
    *,
    writer_file: str,
    writer_layer: str,
    write_symbol: str,
    write_line: int,
    severity: str = "warning",
) -> None:
    conn.execute(
        "INSERT INTO mv_write_sovereignty_paths VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?)",
        (
            snapshot_id,
            edge_id,
            writer_file,
            writer_layer,
            write_symbol,
            write_line,
            writer_file,
            severity,
        ),
    )


def _seed_common(db: Path, snapshot_id: str) -> int:
    conn = sqlite3.connect(str(db))
    _node(conn, 1, "actor", "L2", "agentic_core/L2/actor.py")
    _node(conn, 2, "target", "L0", "agentic_core/L0/target.py")
    _node(conn, 3, "provider", "L3", "agentic_core/L3/provider.py")
    _edge(
        conn,
        1,
        2,
        "imports",
        source_file="agentic_core/L2/actor.py",
        line_no=1,
    )
    _edge(
        conn,
        1,
        3,
        "invokes_provider",
        source_file="agentic_core/L2/actor.py",
        line_no=2,
    )
    write_edge_id = _edge(
        conn,
        1,
        2,
        "writes_to",
        source_file="agentic_core/L2/actor.py",
        line_no=10,
        symbol="state.write",
    )
    _critical(conn, snapshot_id, 1, "actor", "L2", "agentic_core/L2/actor.py", 8.0)
    _bypass(
        conn,
        snapshot_id,
        write_edge_id,
        writer_file="agentic_core/L2/actor.py",
        writer_layer="L2",
        write_symbol="state.write",
        write_line=10,
    )
    conn.commit()
    conn.close()
    return write_edge_id


def _advance_snapshot(db: Path, snapshot_id: str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db))
    conn.execute("UPDATE meta SET value=? WHERE key='commit_sha'", (snapshot_id,))
    conn.execute("UPDATE mv_path_criticality_rollup SET snapshot_id=?", (snapshot_id,))
    conn.execute("UPDATE mv_write_sovereignty_paths SET snapshot_id=?", (snapshot_id,))
    return conn


def test_first_run_newness_is_unknown_not_true(tmp_path: Path) -> None:
    db = _create_db(tmp_path / "adg_indexed_001.sqlite", "snap_001")
    _seed_common(db, "snap_001")
    materialize_phase_d(db)

    conn = sqlite3.connect(str(db))
    try:
        tables = (
            "mv_newly_introduced_critical_paths",
            "mv_new_cross_layer_dependencies",
            "mv_new_provider_surfaces",
            "mv_new_write_bypass_paths",
        )
        for table_name in tables:
            row = conn.execute(
                f"SELECT is_new, comparison_status FROM {table_name} LIMIT 1"
            ).fetchone()
            assert row == (None, "NO_BASELINE")
    finally:
        conn.close()


def test_identical_consecutive_snapshot_has_no_new_rows(tmp_path: Path) -> None:
    db = _create_db(tmp_path / "adg_indexed_001.sqlite", "snap_001")
    _seed_common(db, "snap_001")
    materialize_phase_d(db)

    conn = _advance_snapshot(db, "snap_002")
    conn.commit()
    conn.close()
    materialize_phase_d(db)

    conn = sqlite3.connect(str(db))
    try:
        tables = (
            "mv_newly_introduced_critical_paths",
            "mv_new_cross_layer_dependencies",
            "mv_new_provider_surfaces",
            "mv_new_write_bypass_paths",
        )
        for table_name in tables:
            assert conn.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE is_new=1"
            ).fetchone()[0] == 0
            assert conn.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE comparison_status='EXACT'"
            ).fetchone()[0] > 0
    finally:
        conn.close()


def test_critical_path_score_change_is_delta_not_new_membership(tmp_path: Path) -> None:
    db = _create_db(tmp_path / "adg_indexed_001.sqlite", "snap_001")
    _seed_common(db, "snap_001")
    materialize_phase_d(db)

    conn = _advance_snapshot(db, "snap_002")
    conn.execute(
        "UPDATE mv_path_criticality_rollup SET criticality_score=10.0 WHERE adg_name='actor'"
    )
    _node(conn, 4, "new_hub", "L1", "agentic_core/L1/new_hub.py")
    _critical(conn, "snap_002", 4, "new_hub", "L1", "agentic_core/L1/new_hub.py", 9.0)
    conn.commit()
    conn.close()
    materialize_phase_d(db)

    conn = sqlite3.connect(str(db))
    try:
        existing = conn.execute(
            "SELECT prev_score, delta, is_new FROM mv_newly_introduced_critical_paths "
            "WHERE adg_name='actor'"
        ).fetchone()
        added = conn.execute(
            "SELECT prev_score, delta, is_new FROM mv_newly_introduced_critical_paths "
            "WHERE adg_name='new_hub'"
        ).fetchone()
        assert existing == (8.0, 2.0, 0)
        assert added == (None, 9.0, 1)
    finally:
        conn.close()


def test_cross_layer_growth_is_not_new_group_but_new_group_is(tmp_path: Path) -> None:
    db = _create_db(tmp_path / "adg_indexed_001.sqlite", "snap_001")
    _seed_common(db, "snap_001")
    materialize_phase_d(db)

    conn = _advance_snapshot(db, "snap_002")
    _edge(
        conn,
        1,
        2,
        "imports",
        source_file="agentic_core/L2/actor.py",
        line_no=20,
    )
    _node(conn, 4, "new_caller", "L1", "agentic_core/L1/new_caller.py")
    _node(conn, 5, "new_target", "L4", "agentic_core/L4/new_target.py")
    _edge(
        conn,
        4,
        5,
        "calls",
        source_file="agentic_core/L1/new_caller.py",
        line_no=1,
    )
    conn.commit()
    conn.close()
    materialize_phase_d(db)

    conn = sqlite3.connect(str(db))
    try:
        existing = conn.execute(
            "SELECT prev_edge_count, edge_delta, is_new FROM mv_new_cross_layer_dependencies "
            "WHERE src_layer='L2' AND dst_layer='L0' AND relation_type='imports'"
        ).fetchone()
        added = conn.execute(
            "SELECT prev_edge_count, edge_delta, is_new FROM mv_new_cross_layer_dependencies "
            "WHERE src_layer='L1' AND dst_layer='L4' AND relation_type='calls'"
        ).fetchone()
        assert existing == (1, 1, 0)
        assert added == (None, 1, 1)
    finally:
        conn.close()


def test_provider_replacement_is_new_when_total_count_is_unchanged(tmp_path: Path) -> None:
    db = _create_db(tmp_path / "adg_indexed_001.sqlite", "snap_001")
    _seed_common(db, "snap_001")
    materialize_phase_d(db)

    conn = _advance_snapshot(db, "snap_002")
    conn.execute("DELETE FROM edges WHERE relation_type='invokes_provider'")
    _node(conn, 4, "new_provider", "L3", "agentic_core/L3/new_provider.py")
    _edge(
        conn,
        1,
        4,
        "invokes_provider",
        source_file="agentic_core/L2/actor.py",
        line_no=4,
    )
    conn.commit()
    conn.close()
    materialize_phase_d(db)

    conn = sqlite3.connect(str(db))
    try:
        summary = conn.execute(
            "SELECT provider_delta FROM mv_snapshot_regression_summary"
        ).fetchone()
        new_surface = conn.execute(
            "SELECT provider_name, is_new FROM mv_new_provider_surfaces"
        ).fetchone()
        assert summary == (0,)
        assert new_surface == ("new_provider", 1)
    finally:
        conn.close()


def test_bypass_replacement_is_new_when_total_count_is_unchanged(tmp_path: Path) -> None:
    db = _create_db(tmp_path / "adg_indexed_001.sqlite", "snap_001")
    old_edge_id = _seed_common(db, "snap_001")
    materialize_phase_d(db)

    conn = _advance_snapshot(db, "snap_002")
    conn.execute("DELETE FROM mv_write_sovereignty_paths WHERE edge_id=?", (old_edge_id,))
    conn.execute("DELETE FROM edges WHERE id=?", (old_edge_id,))
    new_edge_id = _edge(
        conn,
        1,
        2,
        "writes_to",
        source_file="agentic_core/L2/actor.py",
        line_no=30,
        symbol="state.direct_write",
    )
    _bypass(
        conn,
        "snap_002",
        new_edge_id,
        writer_file="agentic_core/L2/actor.py",
        writer_layer="L2",
        write_symbol="state.direct_write",
        write_line=30,
        severity="critical",
    )
    conn.commit()
    conn.close()
    materialize_phase_d(db)

    conn = sqlite3.connect(str(db))
    try:
        summary = conn.execute(
            "SELECT bypass_delta FROM mv_snapshot_regression_summary"
        ).fetchone()
        new_bypass = conn.execute(
            "SELECT edge_id, src_file, src_layer, bypass_type, source_file, line_no, is_new "
            "FROM mv_new_write_bypass_paths"
        ).fetchone()
        assert summary == (0,)
        assert new_bypass == (
            new_edge_id,
            "agentic_core/L2/actor.py",
            "L2",
            "state.direct_write",
            "agentic_core/L2/actor.py",
            30,
            1,
        )
    finally:
        conn.close()


def test_fresh_database_reads_exact_rows_from_prior_database(tmp_path: Path) -> None:
    prior = _create_db(tmp_path / "adg_indexed_001.sqlite", "snap_001")
    _seed_common(prior, "snap_001")
    materialize_phase_d(prior)

    current = _create_db(tmp_path / "adg_indexed_002.sqlite", "snap_002")
    _seed_common(current, "snap_002")
    materialize_phase_d(current)

    conn = sqlite3.connect(str(current))
    try:
        summary = conn.execute(
            "SELECT prev_snapshot_id, is_first_run, comparison_status "
            "FROM mv_snapshot_regression_summary"
        ).fetchone()
        bypass = conn.execute(
            "SELECT is_new, comparison_status FROM mv_new_write_bypass_paths"
        ).fetchone()
        assert summary == ("snap_001", 0, "EXACT")
        assert bypass == (0, "EXACT")
    finally:
        conn.close()
