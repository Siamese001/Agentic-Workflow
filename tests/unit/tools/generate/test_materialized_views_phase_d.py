"""Tests for Phase D materialized views (snapshot baseline + regression diffs)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from tools.generate.materialized_views.phase_a_path_authority import materialize_phase_a
from tools.generate.materialized_views.phase_b_capability_tool_task import materialize_phase_b
from tools.generate.materialized_views.phase_c_trace_drift_debt import materialize_phase_c
from tools.generate.materialized_views.phase_d_snapshot_regression import (
    _PHASE_D_TABLES,
    materialize_phase_d,
)


# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------


def _create_minimal_db(tmp_path: Path, commit_sha: str = "ddd000") -> Path:
    db = tmp_path / "test_adg.sqlite"
    conn = sqlite3.connect(str(db))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL DEFAULT 'module',
            layer TEXT NOT NULL DEFAULT '',
            identity_kind TEXT NOT NULL DEFAULT 'internal_module',
            confidence TEXT NOT NULL DEFAULT 'high',
            resolved_path TEXT NOT NULL DEFAULT '',
            precision_type TEXT DEFAULT 'symbol',
            span_start INTEGER DEFAULT 0, span_end INTEGER DEFAULT 0,
            span_line INTEGER DEFAULT 0, span_column INTEGER DEFAULT 0,
            span_end_line INTEGER DEFAULT 0, span_end_column INTEGER DEFAULT 0,
            logical_sequence_id INTEGER DEFAULT 0,
            control_path_id TEXT DEFAULT '',
            temporal_order INTEGER DEFAULT 0,
            type_surface TEXT DEFAULT '',
            enclosing_symbol TEXT DEFAULT ''
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL, dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT NOT NULL DEFAULT 'direct',
            source_file TEXT NOT NULL DEFAULT '',
            line_no INTEGER NOT NULL DEFAULT 0,
            symbol TEXT NOT NULL DEFAULT '',
            semantic_type TEXT DEFAULT NULL, confidence REAL DEFAULT 1.0,
            source_span_start INTEGER DEFAULT 0, source_span_end INTEGER DEFAULT 0,
            source_span_line INTEGER DEFAULT 0, source_span_column INTEGER DEFAULT 0,
            target_span_start INTEGER DEFAULT 0, target_span_end INTEGER DEFAULT 0,
            target_span_line INTEGER DEFAULT 0, target_span_column INTEGER DEFAULT 0,
            dynamic_resolution TEXT DEFAULT NULL
        );
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER NOT NULL, category TEXT NOT NULL DEFAULT '',
            evidence TEXT NOT NULL DEFAULT '', file_path TEXT NOT NULL DEFAULT '',
            line_no INTEGER NOT NULL DEFAULT 0,
            disposition TEXT NOT NULL DEFAULT 'untriaged',
            disposition_source TEXT DEFAULT '', disposition_date TEXT DEFAULT '',
            severity TEXT NOT NULL DEFAULT 'MEDIUM',
            violation_class TEXT NOT NULL DEFAULT 'hygiene'
        );
        CREATE TABLE t_infra_importers (resolved_path TEXT NOT NULL);
        CREATE TABLE precision_type_surfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT, node_id INTEGER NOT NULL,
            inferred_type TEXT DEFAULT NULL, possible_types TEXT DEFAULT '[]',
            nullability BOOLEAN DEFAULT FALSE, shape_signature TEXT DEFAULT NULL
        );
        CREATE TABLE precision_variable_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, node_id INTEGER NOT NULL,
            source_origin TEXT NOT NULL DEFAULT '', mutation_count INTEGER DEFAULT 0,
            lineage_chain TEXT DEFAULT '[]', type_surface_id INTEGER DEFAULT NULL
        );
        CREATE TABLE precision_side_effects (
            id INTEGER PRIMARY KEY AUTOINCREMENT, node_id INTEGER NOT NULL,
            effect_type TEXT NOT NULL DEFAULT '', target TEXT NOT NULL DEFAULT '',
            confidence REAL DEFAULT 1.0
        );
        CREATE TABLE precision_control_branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT, node_id INTEGER NOT NULL,
            branch_type TEXT NOT NULL DEFAULT '', condition TEXT DEFAULT NULL,
            target_id INTEGER DEFAULT NULL
        );
        CREATE TABLE precision_call_resolution (
            id INTEGER PRIMARY KEY AUTOINCREMENT, edge_id INTEGER NOT NULL,
            resolved_target TEXT DEFAULT NULL, candidate_targets TEXT DEFAULT '[]',
            dispatch_type TEXT DEFAULT NULL, resolution_confidence REAL DEFAULT 0.0
        );
        CREATE TABLE precision_test_linkage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_node_id INTEGER NOT NULL, target_node_id INTEGER NOT NULL,
            link_type TEXT NOT NULL DEFAULT '', confidence REAL DEFAULT 1.0
        );
    """)
    conn.execute("INSERT INTO meta(key,value) VALUES ('commit_sha', ?)", (commit_sha,))
    conn.execute("INSERT INTO meta(key,value) VALUES ('total_nodes', '0')")
    conn.execute("INSERT INTO meta(key,value) VALUES ('total_edges', '0')")
    conn.execute("INSERT INTO meta(key,value) VALUES ('artifact_digest', 'digest_ddd')")
    conn.execute("INSERT INTO meta(key,value) VALUES ('scanner_digest', 'scanner_ddd')")
    conn.commit()
    conn.close()
    return db


def _node(conn: sqlite3.Connection, nid: int, name: str, layer: str, path: str) -> None:
    conn.execute(
        "INSERT INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path)"
        " VALUES (?,?,'module',?,'internal_module','high',?)",
        (nid, name, layer, path),
    )


def _edge(conn: sqlite3.Connection, src: int, dst: int, rel: str, source_file: str = "f.py") -> None:
    conn.execute(
        "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no) VALUES (?,?,?,?,?,1)",
        (src, dst, rel, "direct", source_file),
    )


def _run_all_phases(db: Path) -> dict[str, int]:
    materialize_phase_a(db)
    materialize_phase_b(db)
    materialize_phase_c(db)
    return materialize_phase_d(db)


# ---------------------------------------------------------------------------
# Phase D: basic contract
# ---------------------------------------------------------------------------


class TestPhaseDTableCreation:
    def test_all_tables_created(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        counts = _run_all_phases(db)
        assert set(counts.keys()) == set(_PHASE_D_TABLES)

    def test_idempotent_refresh(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        _run_all_phases(db)
        counts1 = materialize_phase_d(db)
        counts2 = materialize_phase_d(db)
        assert counts1 == counts2

    def test_artifact_digest_in_baseline(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path, commit_sha="snap_test_001")
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT snapshot_id FROM mv_snapshot_baseline").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "digest_ddd"


# ---------------------------------------------------------------------------
# mv_snapshot_baseline
# ---------------------------------------------------------------------------


class TestSnapshotBaseline:
    def test_baseline_node_count_matches_db(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "mod_a", "L2", "agentic_core/L2_execution/reasoning/a.py")
        _node(conn, 2, "mod_b", "L1", "agentic_core/L1_cognition/b.py")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT node_count FROM mv_snapshot_baseline").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 2

    def test_baseline_violation_count(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "a", "L2", "agentic_core/L2_execution/reasoning/a.py")
        _node(conn, 2, "b", "L0", "agentic_core/L0_routing/b.py")
        _edge(conn, 1, 2, "violates")
        eid = conn.execute("SELECT id FROM edges WHERE relation_type='violates'").fetchone()[0]
        conn.execute(
            "INSERT INTO violations(edge_id,category,file_path,severity)"
            " VALUES (?,'layer','agentic_core/L2_execution/reasoning/a.py','HIGH')",
            (eid,),
        )
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT violation_count FROM mv_snapshot_baseline").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1

    def test_baseline_cross_layer_edge_count(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "l2", "L2", "agentic_core/L2_execution/reasoning/x.py")
        _node(conn, 2, "l0", "L0", "agentic_core/L0_routing/y.py")
        _edge(conn, 1, 2, "imports", source_file="agentic_core/L2_execution/reasoning/x.py")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT cross_layer_edge_count FROM mv_snapshot_baseline").fetchone()
        conn.close()
        assert row is not None
        assert row[0] >= 1


# ---------------------------------------------------------------------------
# mv_snapshot_regression_summary
# ---------------------------------------------------------------------------


class TestSnapshotRegressionSummary:
    def test_first_run_is_first_run_flag(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT is_first_run, node_delta, edge_delta FROM mv_snapshot_regression_summary"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1  # first run
        assert row[1] == 0  # no delta on first run
        assert row[2] == 0

    def test_second_run_with_added_node_produces_delta(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path, commit_sha="snap_v1")
        _run_all_phases(db)

        # Simulate second run: add a node and change the commit_sha
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "new_mod", "L2", "agentic_core/L2_execution/reasoning/new.py")
        conn.execute("UPDATE meta SET value='snap_v2' WHERE key='commit_sha'")
        conn.execute(
            "UPDATE meta SET value='digest_v2' WHERE key='artifact_digest'"
        )
        conn.commit()
        conn.close()

        # Run all phases again — Phase D should pick up the old baseline
        materialize_phase_a(db)
        materialize_phase_b(db)
        materialize_phase_c(db)
        materialize_phase_d(db)

        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT is_first_run, prev_snapshot_id, node_delta FROM mv_snapshot_regression_summary"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 0  # NOT first run
        assert row[1] == "digest_ddd"  # previous artifact recorded
        assert row[2] == 1  # one node added

    def test_violation_delta_increases(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path, commit_sha="viol_v1")
        _run_all_phases(db)

        conn = sqlite3.connect(str(db))
        _node(conn, 1, "a", "L2", "agentic_core/L2_execution/reasoning/a.py")
        _node(conn, 2, "b", "L0", "agentic_core/L0_routing/b.py")
        _edge(conn, 1, 2, "violates")
        eid = conn.execute("SELECT MAX(id) FROM edges").fetchone()[0]
        conn.execute(
            "INSERT INTO violations(edge_id,category,file_path,severity)"
            " VALUES (?,'layer','agentic_core/L2_execution/reasoning/a.py','HIGH')",
            (eid,),
        )
        conn.execute("UPDATE meta SET value='viol_v2' WHERE key='commit_sha'")
        conn.commit()
        conn.close()

        materialize_phase_a(db)
        materialize_phase_b(db)
        materialize_phase_c(db)
        materialize_phase_d(db)

        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT violation_delta FROM mv_snapshot_regression_summary").fetchone()
        conn.close()
        assert row is not None
        assert row[0] >= 1


# ---------------------------------------------------------------------------
# mv_newly_introduced_critical_paths
# ---------------------------------------------------------------------------


class TestNewlyIntroducedCriticalPaths:
    def test_high_criticality_node_included(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "hub", "L2", "agentic_core/L2_execution/reasoning/hub.py")
        for i in range(8):
            _node(conn, 10 + i, f"caller_{i}", "L1", f"agentic_core/L1_cognition/c{i}.py")
            _edge(conn, 10 + i, 1, "imports")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT node_id, criticality_score FROM mv_newly_introduced_critical_paths WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[1] > 5.0


# ---------------------------------------------------------------------------
# mv_new_cross_layer_dependencies
# ---------------------------------------------------------------------------


class TestNewCrossLayerDependencies:
    def test_cross_layer_edge_included(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "l2", "L2", "agentic_core/L2_execution/reasoning/a.py")
        _node(conn, 2, "l0", "L0", "agentic_core/L0_routing/b.py")
        _edge(conn, 1, 2, "imports", source_file="agentic_core/L2_execution/reasoning/a.py")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT src_layer, dst_layer, edge_count "
            "FROM mv_new_cross_layer_dependencies "
            "WHERE src_layer = 'L2' AND dst_layer = 'L0'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[2] >= 1

    def test_same_layer_edge_not_included(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "l2a", "L2", "agentic_core/L2_execution/reasoning/a.py")
        _node(conn, 2, "l2b", "L2", "agentic_core/L2_execution/reasoning/b.py")
        _edge(conn, 1, 2, "imports")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_new_cross_layer_dependencies WHERE src_layer = 'L2' AND dst_layer = 'L2'"
        ).fetchone()[0]
        conn.close()
        assert count == 0


# ---------------------------------------------------------------------------
# mv_new_provider_surfaces
# ---------------------------------------------------------------------------


class TestNewProviderSurfaces:
    def test_provider_invocation_recorded(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "AnthropicProvider", "L2", "agentic_core/L2_execution/reasoning/anthropic_prov.py")
        _edge(conn, 1, 2, "invokes_provider", source_file="agentic_core/L2_execution/reasoning/actor.py")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT invocation_count FROM mv_new_provider_surfaces WHERE caller_file LIKE '%actor%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] >= 1

    def test_test_file_provider_excluded(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "test_actor", "L2", "tests/unit/test_actor.py")
        _node(conn, 2, "prov", "L2", "agentic_core/L2_execution/reasoning/prov.py")
        _edge(conn, 1, 2, "invokes_provider", source_file="tests/unit/test_actor.py")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_new_provider_surfaces WHERE caller_file LIKE 'tests/%'"
        ).fetchone()[0]
        conn.close()
        assert count == 0


# ---------------------------------------------------------------------------
# mv_new_write_bypass_paths
# ---------------------------------------------------------------------------


class TestNewWriteBypassPaths:
    def test_non_uwg_write_in_bypass_table(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "store", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to", source_file="agentic_core/L2_execution/reasoning/actor.py")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute("SELECT COUNT(*) FROM mv_new_write_bypass_paths").fetchone()[0]
        conn.close()
        assert count >= 1

    def test_bypass_row_has_unknown_newness_without_baseline(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "store", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to", source_file="agentic_core/L2_execution/reasoning/actor.py")
        conn.commit()
        conn.close()
        _run_all_phases(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT is_new, severity, comparison_status "
            "FROM mv_new_write_bypass_paths LIMIT 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] is None  # no prior snapshot means newness is unknowable
        assert row[1] is not None  # severity column populated
        assert row[2] == "NO_BASELINE"

    def test_bypass_fallback_when_sovereignty_table_absent(self, tmp_path: Path) -> None:
        """G6: Phase D bypass fallback executes when mv_write_sovereignty_paths does not exist."""
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "store", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to", source_file="agentic_core/L2_execution/reasoning/actor.py")
        conn.commit()
        conn.close()
        # Run Phase A/B/C so the earlier Phase D tables exist, then drop sovereignty table
        materialize_phase_a(db)
        materialize_phase_b(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        conn.execute("DROP TABLE IF EXISTS mv_write_sovereignty_paths")
        conn.commit()
        conn.close()
        # Phase D must not raise — it falls back to raw edge query
        counts = materialize_phase_d(db)
        assert "mv_new_write_bypass_paths" in counts
        conn = sqlite3.connect(str(db))
        count = conn.execute("SELECT COUNT(*) FROM mv_new_write_bypass_paths").fetchone()[0]
        conn.close()
        assert count >= 1  # fallback path produced at least one row

    def test_orchestrator_returns_all_phase_d_tables(self, tmp_path: Path) -> None:
        """Integration: orchestrator collects all Phase D table names."""
        from tools.generate.materialized_views.orchestrator import materialize_all_views

        db = _create_minimal_db(tmp_path)
        all_counts = materialize_all_views(db)
        for tbl in _PHASE_D_TABLES:
            assert tbl in all_counts, f"Orchestrator missing Phase D table: {tbl}"
