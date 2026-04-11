"""Tests for Phase A materialized views (path/authority/lifecycle/topology seeds)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tools.generate.materialized_views.phase_a_path_authority import (
    _PHASE_A_TABLES,
    materialize_phase_a,
)


# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------


def _create_minimal_db(tmp_path: Path, commit_sha: str = "abc123") -> Path:
    """Create a minimal ADG SQLite with all canonical tables."""
    db = tmp_path / "test_adg.sqlite"
    conn = sqlite3.connect(str(db))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE nodes (
            id            INTEGER PRIMARY KEY,
            adg_name      TEXT NOT NULL,
            entity_type   TEXT NOT NULL DEFAULT 'module',
            layer         TEXT NOT NULL DEFAULT '',
            identity_kind TEXT NOT NULL DEFAULT 'internal_module',
            confidence    TEXT NOT NULL DEFAULT 'high',
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
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id        INTEGER NOT NULL,
            dst_id        INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind     TEXT NOT NULL DEFAULT 'direct',
            source_file   TEXT NOT NULL DEFAULT '',
            line_no       INTEGER NOT NULL DEFAULT 0,
            symbol        TEXT NOT NULL DEFAULT '',
            semantic_type TEXT DEFAULT NULL,
            confidence    REAL DEFAULT 1.0,
            source_span_start INTEGER DEFAULT 0, source_span_end INTEGER DEFAULT 0,
            source_span_line INTEGER DEFAULT 0, source_span_column INTEGER DEFAULT 0,
            target_span_start INTEGER DEFAULT 0, target_span_end INTEGER DEFAULT 0,
            target_span_line INTEGER DEFAULT 0, target_span_column INTEGER DEFAULT 0,
            dynamic_resolution TEXT DEFAULT NULL
        );
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER NOT NULL,
            category TEXT NOT NULL DEFAULT '',
            evidence TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL DEFAULT '',
            line_no INTEGER NOT NULL DEFAULT 0,
            disposition TEXT NOT NULL DEFAULT 'untriaged',
            disposition_source TEXT DEFAULT '',
            disposition_date TEXT DEFAULT '',
            severity TEXT NOT NULL DEFAULT 'MEDIUM',
            violation_class TEXT NOT NULL DEFAULT 'hygiene'
        );
        CREATE TABLE t_infra_importers (resolved_path TEXT NOT NULL);
        CREATE TABLE precision_type_surfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER NOT NULL,
            inferred_type TEXT DEFAULT NULL,
            possible_types TEXT DEFAULT '[]',
            nullability BOOLEAN DEFAULT FALSE,
            shape_signature TEXT DEFAULT NULL
        );
        CREATE TABLE precision_variable_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER NOT NULL,
            source_origin TEXT NOT NULL DEFAULT '',
            mutation_count INTEGER DEFAULT 0,
            lineage_chain TEXT DEFAULT '[]',
            type_surface_id INTEGER DEFAULT NULL
        );
        CREATE TABLE precision_side_effects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER NOT NULL,
            effect_type TEXT NOT NULL DEFAULT '',
            target TEXT NOT NULL DEFAULT '',
            confidence REAL DEFAULT 1.0
        );
        CREATE TABLE precision_control_branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER NOT NULL,
            branch_type TEXT NOT NULL DEFAULT '',
            condition TEXT DEFAULT NULL,
            target_id INTEGER DEFAULT NULL
        );
        CREATE TABLE precision_call_resolution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER NOT NULL,
            resolved_target TEXT DEFAULT NULL,
            candidate_targets TEXT DEFAULT '[]',
            dispatch_type TEXT DEFAULT NULL,
            resolution_confidence REAL DEFAULT 0.0
        );
        CREATE TABLE precision_test_linkage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_node_id INTEGER NOT NULL,
            target_node_id INTEGER NOT NULL,
            link_type TEXT NOT NULL DEFAULT '',
            confidence REAL DEFAULT 1.0
        );
    """)
    conn.execute("INSERT INTO meta(key,value) VALUES ('commit_sha', ?)", (commit_sha,))
    conn.execute("INSERT INTO meta(key,value) VALUES ('total_nodes', '0')")
    conn.execute("INSERT INTO meta(key,value) VALUES ('total_edges', '0')")
    conn.execute("INSERT INTO meta(key,value) VALUES ('artifact_digest', 'digest_abc')")
    conn.execute("INSERT INTO meta(key,value) VALUES ('scanner_digest', 'scanner_abc')")
    conn.commit()
    conn.close()
    return db


def _node(
    conn: sqlite3.Connection,
    node_id: int,
    adg_name: str,
    layer: str,
    resolved_path: str,
    entity_type: str = "module",
    identity_kind: str = "internal_module",
) -> None:
    conn.execute(
        "INSERT INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path) "
        "VALUES (?,?,?,?,?,'high',?)",
        (node_id, adg_name, entity_type, layer, identity_kind, resolved_path),
    )


def _edge(
    conn: sqlite3.Connection,
    src: int,
    dst: int,
    rel: str,
    source_file: str = "file.py",
    line_no: int = 1,
    edge_kind: str = "direct",
    symbol: str = "",
    dynamic_resolution: str | None = None,
) -> None:
    conn.execute(
        "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol,dynamic_resolution) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (src, dst, rel, edge_kind, source_file, line_no, symbol, dynamic_resolution),
    )


# ---------------------------------------------------------------------------
# Phase A: basic contract tests
# ---------------------------------------------------------------------------


class TestPhaseATableCreation:
    def test_all_tables_created_on_empty_db(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        counts = materialize_phase_a(db)
        assert set(counts.keys()) == set(_PHASE_A_TABLES)

    def test_empty_db_returns_zero_counts(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        counts = materialize_phase_a(db)
        for tbl in (
            "mv_runtime_spine_gaps",
            "mv_path_criticality_rollup",
            "mv_authority_boundary_breaches",
            "mv_write_sovereignty_paths",
            "mv_hitl_reclearance_gaps",
            "mv_l2_phase_coverage",
            "mv_exit_disposition_coverage",
            "mv_heal_retry_exit_gaps",
            "mv_hotspot_centrality",
            "mv_unknown_taxonomy_and_orphans",
        ):
            assert counts[tbl] == 0, f"{tbl} should be 0 on empty DB"

    def test_idempotent_refresh(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        counts1 = materialize_phase_a(db)
        counts2 = materialize_phase_a(db)
        assert counts1 == counts2

    def test_snapshot_id_in_all_tables(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path, commit_sha="test_sha_999")
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "A", "L2", "agentic_core/L2_execution/reasoning/foo.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        for tbl in _PHASE_A_TABLES:
            row = conn.execute(f"SELECT snapshot_id FROM {tbl} LIMIT 1").fetchone()
            if row is not None:
                assert row[0] == "test_sha_999", f"{tbl} has wrong snapshot_id: {row[0]}"
        conn.close()


class TestPhaseACriticalPath:
    def test_critical_path_segments_cross_layer_edge(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "L0_mod", "L0", "agentic_core/L0_routing/mod.py")
        _node(conn, 2, "L2_mod", "L2", "agentic_core/L2_execution/reasoning/mod.py")
        _edge(conn, 1, 2, "imports", "agentic_core/L0_routing/mod.py")
        conn.commit()
        conn.close()
        counts = materialize_phase_a(db)
        assert counts["mv_critical_path_segments"] >= 1

    def test_path_criticality_rollup_fan_in(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "hub", "L2", "agentic_core/L2_execution/reasoning/hub.py")
        _node(conn, 2, "caller_a", "L1", "agentic_core/L1_cognition/a.py")
        _node(conn, 3, "caller_b", "L1", "agentic_core/L1_cognition/b.py")
        _edge(conn, 2, 1, "imports")
        _edge(conn, 3, 1, "imports")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT fan_in, criticality_score FROM mv_path_criticality_rollup WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 2  # fan_in
        assert row[1] >= 2.0  # criticality_score

    def test_path_criticality_zero_violations(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "isolated", "L0", "agentic_core/L0_routing/isolated.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT violation_count FROM mv_path_criticality_rollup WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 0


class TestPhaseAAuthority:
    def test_authority_breach_l6_to_l2(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "l6_mod", "L6", "system_learning/output.py")
        _node(conn, 2, "l2_mod", "L2", "agentic_core/L2_execution/reasoning/core.py")
        _edge(conn, 1, 2, "imports")
        conn.commit()
        conn.close()
        counts = materialize_phase_a(db)
        assert counts["mv_authority_boundary_breaches"] >= 1

    def test_authority_ok_l0_to_l2(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "l0_mod", "L0", "agentic_core/L0_routing/mod.py")
        _node(conn, 2, "l2_mod", "L2", "agentic_core/L2_execution/reasoning/core.py")
        _edge(conn, 1, 2, "imports")
        conn.commit()
        conn.close()
        counts = materialize_phase_a(db)
        assert counts["mv_authority_boundary_breaches"] == 0

    def test_write_sovereignty_non_uwg_flagged(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "writer", "L2", "agentic_core/L2_execution/reasoning/action.py")
        _node(conn, 2, "target", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT is_uwg_routed, severity FROM mv_write_sovereignty_paths WHERE writer_file LIKE '%action%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 0  # not UWG routed

    def test_hitl_reclearance_gap_write_no_guardrail(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "target", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_type FROM mv_hitl_reclearance_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "write_without_guardrail"

    def test_hitl_reclearance_ok_with_guardrail(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "target", "L4", "agentic_core/L4_state/store.py")
        _node(conn, 3, "guard", "L2", "agentic_core/L2_execution/enforcement/guard.py")
        _edge(conn, 1, 2, "writes_to")
        _edge(conn, 1, 3, "applies_guardrail")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_type FROM mv_hitl_reclearance_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "ok"


class TestPhaseALifecycle:
    def test_l2_phase_coverage_healing_node(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "heal_mod", "L2", "agentic_core/L2_execution/reasoning/healing.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT phase_label, node_count FROM mv_l2_phase_coverage WHERE phase_label = 'healing'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[1] >= 1

    def test_l2_phase_coverage_gap_flag_for_empty_phase(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "foo", "L2", "agentic_core/L2_execution/reasoning/foo.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT gap_flag FROM mv_l2_phase_coverage WHERE phase_label = 'phase_unknown'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 0  # phase_unknown bucket has a node — not a gap

    def test_exit_disposition_gap_detected(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "l2_actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_type FROM mv_exit_disposition_coverage WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "no_exit_disposition"

    def test_exit_disposition_ok_with_route(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "l2_actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "cap", "L3", "agentic_core/L3_orchestration/cap.py")
        _edge(conn, 1, 2, "routes_to_capability")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_type FROM mv_exit_disposition_coverage WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "ok"

    def test_heal_retry_exit_gap_detected(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "heal_pipe", "L2", "agentic_core/L2_execution/enforcement/healer_pipe_order.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_flag FROM mv_heal_retry_exit_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1


class TestPhaseATopologyAndDiagnostics:
    def test_hotspot_centrality_top_node_has_highest_fan_in(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "hub", "L2", "agentic_core/L2_execution/reasoning/hub.py")
        _node(conn, 2, "a", "L1", "agentic_core/L1_cognition/a.py")
        _node(conn, 3, "b", "L1", "agentic_core/L1_cognition/b.py")
        _node(conn, 4, "c", "L0", "agentic_core/L0_routing/c.py")
        _edge(conn, 2, 1, "imports")
        _edge(conn, 3, 1, "imports")
        _edge(conn, 4, 1, "imports")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT node_id, fan_in FROM mv_hotspot_centrality ORDER BY fan_in DESC LIMIT 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1
        assert row[1] == 3

    def test_unknown_taxonomy_flag(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        conn.execute(
            "INSERT INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path) "
            "VALUES (1,'no_layer','module','','internal_module','high','some/file.py')"
        )
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT unknown_taxonomy_flag FROM mv_unknown_taxonomy_and_orphans WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1

    def test_orphan_flag_for_disconnected_module(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "loner", "L2", "agentic_core/L2_execution/reasoning/loner.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT orphan_flag FROM mv_unknown_taxonomy_and_orphans WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1

    def test_digest_reconciliation_match(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        conn.execute("UPDATE meta SET value = '0' WHERE key = 'total_nodes'")
        conn.execute("UPDATE meta SET value = '0' WHERE key = 'total_edges'")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        rows = conn.execute(
            "SELECT meta_key, match_flag FROM mv_digest_reconciliation "
            "WHERE meta_key IN ('total_nodes','total_edges')"
        ).fetchall()
        conn.close()
        assert len(rows) == 2
        for _, flag in rows:
            assert flag == 1

    def test_digest_reconciliation_mismatch(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "mod", "L2", "agentic_core/L2_execution/reasoning/mod.py")
        conn.execute("UPDATE meta SET value = '999' WHERE key = 'total_nodes'")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT match_flag FROM mv_digest_reconciliation WHERE meta_key = 'total_nodes'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 0

    def test_snapshot_integrity_null_resolved_path(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        conn.execute(
            "INSERT INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path) "
            "VALUES (10,'null_path','module','L2','internal_module','high','')"
        )
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_snapshot_integrity_anomalies WHERE anomaly_type='null_resolved_path'"
        ).fetchone()[0]
        conn.close()
        assert count >= 1

    def test_dynamic_resolution_anomaly(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "src", "L2", "agentic_core/L2_execution/reasoning/src.py")
        _node(conn, 2, "dst", "L3", "agentic_core/L3_orchestration/dst.py")
        _edge(
            conn,
            1,
            2,
            "calls",
            source_file="agentic_core/L2_execution/reasoning/src.py",
            dynamic_resolution="getattr_override",
        )
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_snapshot_integrity_anomalies WHERE anomaly_type='dynamic_override'"
        ).fetchone()[0]
        conn.close()
        assert count >= 1


# ---------------------------------------------------------------------------
# G9 — connection released on OperationalError (failure path)
# ---------------------------------------------------------------------------


class TestConnectionReleasedOnError:
    def test_phase_a_raises_and_does_not_leak_on_missing_nodes_table(self, tmp_path: Path) -> None:
        db = tmp_path / "broken.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute("INSERT INTO meta(key,value) VALUES ('commit_sha','x')")
        conn.commit()
        conn.close()
        with pytest.raises(Exception):
            materialize_phase_a(db)
        # After the raise the WAL file must not be locked — re-opening must succeed
        conn2 = sqlite3.connect(str(db))
        conn2.execute("SELECT 1")
        conn2.close()


# ---------------------------------------------------------------------------
# G8 — spine gap_pct accuracy
# ---------------------------------------------------------------------------


class TestSpineGapPct:
    def test_gap_pct_100_when_no_callers(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "isolated", "L2", "agentic_core/L2_execution/reasoning/isolated.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT gap_count, module_count, gap_pct FROM mv_runtime_spine_gaps WHERE layer = 'L2'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1  # gap_count
        assert row[1] == 1  # module_count
        assert row[2] == 100.0  # gap_pct

    def test_gap_pct_0_when_all_connected(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "mod", "L2", "agentic_core/L2_execution/reasoning/mod.py")
        _node(conn, 2, "caller", "L1", "agentic_core/L1_cognition/caller.py")
        _edge(conn, 2, 1, "imports")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT gap_count, gap_pct FROM mv_runtime_spine_gaps WHERE layer = 'L2'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 0
        assert row[1] == 0.0


# ---------------------------------------------------------------------------
# G3 — write sovereignty severity column correctness
# ---------------------------------------------------------------------------


class TestWriteSovereigntySeverity:
    def test_non_uwg_write_has_warning_severity(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "store", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to", source_file="agentic_core/L2_execution/reasoning/actor.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT is_uwg_routed, severity FROM mv_write_sovereignty_paths WHERE writer_file LIKE '%actor%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 0  # not UWG-routed
        assert row[1] in ("warning", "critical")  # severity must be labelled

    def test_uwg_routed_write_has_ok_severity(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "uwg_writer", "L2", "agentic_core/L2_execution/reasoning/UniversalWriteGateway.py")
        _node(conn, 2, "store", "L4", "agentic_core/L4_state/store.py")
        _edge(
            conn,
            1,
            2,
            "writes_to",
            source_file="agentic_core/L2_execution/reasoning/UniversalWriteGateway.py",
        )
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT is_uwg_routed, severity FROM mv_write_sovereignty_paths "
            "WHERE writer_file LIKE '%UniversalWrite%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1  # UWG-routed
        assert row[1] == "ok"


# ---------------------------------------------------------------------------
# G10 — mv_live_future_mutation_conflicts (zero tests previously)
# ---------------------------------------------------------------------------


class TestLiveFutureMutationConflicts:
    def test_table_created_on_empty_db(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute("SELECT COUNT(*) FROM mv_live_future_mutation_conflicts").fetchone()[0]
        conn.close()
        assert isinstance(count, int)

    def test_conflict_detected_same_file_live_write_and_snapshot_link(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "ambiguous", "L2", "agentic_core/L2_execution/reasoning/ambiguous.py")
        _node(conn, 2, "store", "L4", "agentic_core/L4_state/store.py")
        _node(conn, 3, "snap", "L2", "agentic_core/L2_execution/enforcement/snap.py")
        # Same source file: one live write + one snapshot link → conflict
        _edge(conn, 1, 2, "writes_to", source_file="agentic_core/L2_execution/reasoning/ambiguous.py")
        _edge(
            conn,
            1,
            3,
            "links_execution_to_snapshot",
            source_file="agentic_core/L2_execution/reasoning/ambiguous.py",
        )
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT conflict_type FROM mv_live_future_mutation_conflicts WHERE file LIKE '%ambiguous%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "live_and_future_write_conflict"

    def test_no_conflict_write_only_no_snapshot_link(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "writer", "L2", "agentic_core/L2_execution/reasoning/writer.py")
        _node(conn, 2, "store", "L4", "agentic_core/L4_state/store.py")
        # Only a live write — no snapshot link → no conflict row (HAVING filters it out)
        _edge(conn, 1, 2, "writes_to", source_file="agentic_core/L2_execution/reasoning/writer.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_live_future_mutation_conflicts WHERE file LIKE '%writer%'"
        ).fetchone()[0]
        conn.close()
        assert count == 0


# ---------------------------------------------------------------------------
# mv_prompt_assembly_wiring_gaps — negative-space detection
# ---------------------------------------------------------------------------


class TestPhaseAPromptAssemblyWiringGaps:
    """Tests for mv_prompt_assembly_wiring_gaps.

    Positive case: at least one live (non-test) caller → gap_type = 'ok'.
    Negative case: test-only callers, zero live callers → gap_type = 'disconnected'.
    """

    def _setup_dispatcher_node(self, conn: sqlite3.Connection, node_id: int) -> None:
        _node(
            conn,
            node_id,
            "ADG::Module::tools/adg/prompt_assembly/c0_dispatcher.py",
            "L_TOOLS",
            "tools/adg/prompt_assembly/c0_dispatcher.py",
        )

    def test_table_in_phase_a_tables(self) -> None:
        assert "mv_prompt_assembly_wiring_gaps" in _PHASE_A_TABLES

    def test_empty_db_produces_zero_rows(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        counts = materialize_phase_a(db)
        assert counts["mv_prompt_assembly_wiring_gaps"] == 0

    def test_positive_live_caller_produces_ok_gap_type(self, tmp_path: Path) -> None:
        """Positive case: dispatcher has a live runtime caller (orchestrator).

        After Stage 3 fix, sovereign_rag_orchestrator imports c0_dispatcher.
        The view should emit gap_type='ok'.
        """
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        self._setup_dispatcher_node(conn, 1)
        _node(
            conn,
            2,
            "ADG::Module::agentic_core/L3_orchestration/reasoning/engines/sovereign_rag_orchestrator.py",
            "L3",
            "agentic_core/L3_orchestration/reasoning/engines/sovereign_rag_orchestrator.py",
        )
        _edge(
            conn,
            2,
            1,
            "imports",
            source_file="agentic_core/L3_orchestration/reasoning/engines/sovereign_rag_orchestrator.py",
        )
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT gap_type, live_callers, test_callers "
            "FROM mv_prompt_assembly_wiring_gaps "
            "WHERE target_file LIKE '%c0_dispatcher%'"
        ).fetchone()
        conn.close()
        assert row is not None, "dispatcher node should appear in view"
        gap_type, live_callers, test_callers = row
        assert gap_type == "ok", f"expected ok but got {gap_type!r}"
        assert live_callers >= 1
        assert test_callers == 0

    def test_negative_test_only_caller_produces_disconnected(self, tmp_path: Path) -> None:
        """Negative case: dispatcher has ONLY a test-file caller.

        This reproduces the pre-Stage-3 state where the prompt assembly subsystem
        existed and was test-covered but had no live runtime entry point.
        The view should emit gap_type='disconnected'.
        """
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        self._setup_dispatcher_node(conn, 1)
        _node(
            conn,
            2,
            "ADG::Module::tests/unit/tools/adg/prompt_assembly/test_c0_dispatcher.py",
            "L_TEST",
            "tests/unit/tools/adg/prompt_assembly/test_c0_dispatcher.py",
        )
        _edge(conn, 2, 1, "imports", source_file="tests/unit/tools/adg/prompt_assembly/test_c0_dispatcher.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT gap_type, live_callers, test_callers "
            "FROM mv_prompt_assembly_wiring_gaps "
            "WHERE target_file LIKE '%c0_dispatcher%'"
        ).fetchone()
        conn.close()
        assert row is not None, "dispatcher node should appear in view"
        gap_type, live_callers, test_callers = row
        assert gap_type == "disconnected", f"expected disconnected but got {gap_type!r}"
        assert live_callers == 0
        assert test_callers >= 1

    def test_no_callers_produces_disconnected(self, tmp_path: Path) -> None:
        """Edge case: zero callers at all → also disconnected (test_callers=0, live=0)."""
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        self._setup_dispatcher_node(conn, 1)
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT gap_type, live_callers, test_callers "
            "FROM mv_prompt_assembly_wiring_gaps "
            "WHERE target_file LIKE '%c0_dispatcher%'"
        ).fetchone()
        conn.close()
        assert row is not None
        gap_type, live_callers, test_callers = row
        assert gap_type == "disconnected"
        assert live_callers == 0
        assert test_callers == 0

    def test_mixed_live_and_test_callers_produces_ok(self, tmp_path: Path) -> None:
        """Both a live and a test caller → gap_type='ok' (live caller is enough)."""
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        self._setup_dispatcher_node(conn, 1)
        _node(conn, 2, "live_orchestrator", "L3", "agentic_core/L3_orchestration/orch.py")
        _node(conn, 3, "test_module", "L_TEST", "tests/unit/test_dispatch.py")
        _edge(conn, 2, 1, "imports", source_file="agentic_core/L3_orchestration/orch.py")
        _edge(conn, 3, 1, "imports", source_file="tests/unit/test_dispatch.py")
        conn.commit()
        conn.close()
        materialize_phase_a(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT gap_type FROM mv_prompt_assembly_wiring_gaps WHERE target_file LIKE '%c0_dispatcher%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "ok"

    def test_idempotent_refresh_preserves_results(self, tmp_path: Path) -> None:
        """Refreshing Phase A twice returns identical wiring gap counts."""
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        self._setup_dispatcher_node(conn, 1)
        _node(conn, 2, "test_caller", "L_TEST", "tests/unit/test_d.py")
        _edge(conn, 2, 1, "imports", source_file="tests/unit/test_d.py")
        conn.commit()
        conn.close()
        counts1 = materialize_phase_a(db)
        counts2 = materialize_phase_a(db)
        assert counts1["mv_prompt_assembly_wiring_gaps"] == counts2["mv_prompt_assembly_wiring_gaps"]
