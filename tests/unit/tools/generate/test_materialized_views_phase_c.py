"""Tests for Phase C materialized views (trace/replay/eval, determinism, exemption/debt)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from tools.generate.materialized_views.phase_a_path_authority import materialize_phase_a
from tools.generate.materialized_views.phase_b_capability_tool_task import materialize_phase_b
from tools.generate.materialized_views.phase_c_trace_drift_debt import (
    _PHASE_C_TABLES,
    materialize_phase_c,
)


# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------


def _create_minimal_db(tmp_path: Path, commit_sha: str = "ccc789") -> Path:
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
    conn.execute("INSERT INTO meta(key,value) VALUES ('artifact_digest', 'digest_ccc')")
    conn.execute("INSERT INTO meta(key,value) VALUES ('scanner_digest', 'scanner_ccc')")
    conn.commit()
    conn.close()
    return db


def _node(
    conn: sqlite3.Connection, nid: int, name: str, layer: str, path: str, entity_type: str = "module"
) -> None:
    conn.execute(
        "INSERT INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path)"
        " VALUES (?,?,?,?,'internal_module','high',?)",
        (nid, name, entity_type, layer, path),
    )


def _node2(conn: sqlite3.Connection, nid: int, name: str, layer: str, path: str) -> None:
    conn.execute(
        "INSERT INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path)"
        " VALUES (?,?,'module',?,'internal_module','high',?)",
        (nid, name, layer, path),
    )


def _edge(
    conn: sqlite3.Connection,
    src: int,
    dst: int,
    rel: str,
    source_file: str = "f.py",
    line_no: int = 1,
    edge_kind: str = "direct",
    symbol: str = "",
) -> None:
    conn.execute(
        "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol)"
        " VALUES (?,?,?,?,?,?,?)",
        (src, dst, rel, edge_kind, source_file, line_no, symbol),
    )


def _setup_phases_ab(db: Path) -> None:
    materialize_phase_a(db)
    materialize_phase_b(db)


# ---------------------------------------------------------------------------
# Phase C: basic contract
# ---------------------------------------------------------------------------


class TestPhaseCTableCreation:
    def test_all_tables_created(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        _setup_phases_ab(db)
        counts = materialize_phase_c(db)
        assert set(counts.keys()) == set(_PHASE_C_TABLES)

    def test_empty_db_returns_zero_or_valid_counts(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        _setup_phases_ab(db)
        counts = materialize_phase_c(db)
        for tbl in _PHASE_C_TABLES:
            assert isinstance(counts[tbl], int)

    def test_idempotent_refresh(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        _setup_phases_ab(db)
        counts1 = materialize_phase_c(db)
        counts2 = materialize_phase_c(db)
        assert counts1 == counts2


# ---------------------------------------------------------------------------
# Family 7 — Trace / replay / eval
# ---------------------------------------------------------------------------


class TestTraceReplayEvalViews:
    def test_no_trace_replay_eval_gap(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node2(conn, 2, "tgt", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to")
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_type FROM mv_trace_replay_eval_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert "no_trace" in row[0] or row[0] == "no_trace_replay_eval"

    def test_ok_when_all_three_present(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node2(conn, 2, "tgt", "L4", "agentic_core/L4_state/store.py")
        _node2(conn, 3, "trace", "L2", "agentic_core/L2_execution/enforcement/trace.py")
        _node2(conn, 4, "snap", "L2", "agentic_core/L2_execution/enforcement/snap.py")
        _node2(conn, 5, "eval_n", "L5", "agentic_core/L5_eval/eval.py")
        _edge(conn, 1, 2, "writes_to")
        _edge(conn, 1, 3, "signs_execution_trace")
        _edge(conn, 1, 4, "links_execution_to_snapshot")
        _edge(conn, 1, 5, "invokes_eval")
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_type FROM mv_trace_replay_eval_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "ok"

    def test_eval_coverage_by_path_gap_count(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node2(conn, 2, "tgt", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to")
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_count FROM mv_eval_coverage_by_path WHERE layer = 'L2'").fetchone()
        # Confirm no row under the broken '?' layer (regression guard for G4 fix)
        bogus = conn.execute("SELECT COUNT(*) FROM mv_eval_coverage_by_path WHERE layer = '?'").fetchone()[0]
        conn.close()
        assert row is not None
        assert row[0] >= 1
        assert bogus == 0, "layer column must not contain literal '?' — _node helper was broken"

    def test_replay_surface_gap_mutation_no_link(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "writer", "L2", "agentic_core/L2_execution/reasoning/writer.py")
        _node2(conn, 2, "tgt", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to")
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_flag FROM mv_replay_surface_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1

    def test_replay_surface_ok_with_snapshot_link(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "writer", "L2", "agentic_core/L2_execution/reasoning/writer.py")
        _node2(conn, 2, "tgt", "L4", "agentic_core/L4_state/store.py")
        _node2(conn, 3, "snap", "L2", "agentic_core/L2_execution/enforcement/snap.py")
        _edge(conn, 1, 2, "writes_to")
        _edge(conn, 1, 3, "links_execution_to_snapshot")
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_flag FROM mv_replay_surface_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 0

    def test_claude_hook_scripts_are_exempt_from_runtime_gap_views(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(
            conn,
            1,
            "hook",
            "L_UNKNOWN",
            ".codex/governance/scripts/post_agent_recommendation_gate_audit.py",
        )
        _node2(conn, 2, "tgt", "L4", "agentic_core/L4_state/store.py")
        _node2(conn, 3, "writer", "L2", "agentic_core/L2_execution/reasoning/writer.py")
        _edge(conn, 1, 2, "writes_to")
        _edge(conn, 3, 2, "writes_to")
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        trace_hook = conn.execute("SELECT COUNT(*) FROM mv_trace_replay_eval_gaps WHERE node_id = 1").fetchone()
        replay_hook = conn.execute("SELECT COUNT(*) FROM mv_replay_surface_gaps WHERE node_id = 1").fetchone()
        runtime_writer = conn.execute("SELECT gap_flag FROM mv_replay_surface_gaps WHERE node_id = 3").fetchone()
        conn.close()
        assert trace_hook == (0,)
        assert replay_hook == (0,)
        assert runtime_writer == (1,)

    def test_proof_harness_and_post_runtime_helpers_are_exempt_from_runtime_gap_views(
        self,
        tmp_path: Path,
    ) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "target", "L4", "agentic_core/L4_state/store.py")
        exempt_paths = [
            "agentic_core/L6_observability/shadow_eval/span_export.py",
            "apps_eval/adapters/apps_rg.py",
            "apps_eval/l6_shadow_bridge.py",
            "apps_eval/matrix.py",
            "apps_eval/scenarios.py",
            "apps_eval/tests/test_apps_rg_live_adapter.py",
            "apps_eval/tests/test_apps_rg_scenario_scaffold.py",
            "apps_eval/tests/test_baseline_workflow.py",
            "apps_eval/tests/test_trend_workflow.py",
            "apps_eval/trends.py",
            "apps_rg/hitl/hitl_replay_store.py",
            "apps_rg/runtime/spine/l6_shadow_eval_runner.py",
        ]
        for node_id, path in enumerate(exempt_paths, start=2):
            _node2(conn, node_id, f"src_{node_id}", "L_APP", path)
            _edge(conn, node_id, 1, "writes_to")
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        try:
            for path in exempt_paths:
                trace_count = conn.execute(
                    "SELECT COUNT(*) FROM mv_trace_replay_eval_gaps WHERE file = ?",
                    (path,),
                ).fetchone()[0]
                assert trace_count == 0, path
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Family 8 (remaining) — Determinism / provenance drift
# ---------------------------------------------------------------------------


class TestDeterminismViews:
    def test_drift_flag_dynamic_resolution(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node2(conn, 2, "dst", "L3", "agentic_core/L3_orchestration/dst.py")
        conn.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,"
            " dynamic_resolution) VALUES (1,2,'calls','direct','actor.py',1,'getattr_override')"
        )
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT drift_flag FROM mv_determinism_provenance_drift WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1

    def test_graph_vs_report_orphan_violation(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        conn.execute(
            "INSERT INTO violations(edge_id,category,file_path,severity)"
            " VALUES (99999,'layer_violation','some/file.py','HIGH')"
        )
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_graph_vs_report_mismatches WHERE mismatch_type = 'orphan_violation'"
        ).fetchone()[0]
        conn.close()
        assert count >= 1

    def test_graph_vs_report_meta_mismatch(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "mod", "L2", "agentic_core/L2_execution/reasoning/mod.py")
        conn.execute("UPDATE meta SET value = '999' WHERE key = 'total_nodes'")
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_graph_vs_report_mismatches WHERE mismatch_type = 'meta_count_mismatch'"
        ).fetchone()[0]
        conn.close()
        assert count >= 1


# ---------------------------------------------------------------------------
# Family 9 — Exemption / debt / concentration
# ---------------------------------------------------------------------------


class TestExemptionDebtViews:
    def _insert_antipattern_edge(
        self,
        conn: sqlite3.Connection,
        src: int,
        dst: int,
        kind: str,
        source_file: str = "agentic_core/L2_execution/reasoning/f.py",
        line_no: int = 10,
    ) -> None:
        conn.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no)"
            " VALUES (?,?,'antipattern',?,'?',?)",
            (src, dst, kind, source_file, line_no),
        )

    def test_exemption_near_critical_path(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "hot", "L2", "agentic_core/L2_execution/reasoning/hot.py")
        _node2(conn, 2, "caller_a", "L1", "agentic_core/L1_cognition/ca.py")
        _node2(conn, 3, "caller_b", "L1", "agentic_core/L1_cognition/cb.py")
        _node2(conn, 4, "caller_c", "L0", "agentic_core/L0_routing/cc.py")
        _edge(conn, 2, 1, "imports")
        _edge(conn, 3, 1, "imports")
        _edge(conn, 4, 1, "imports")
        conn.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no)"
            " VALUES (1,2,'antipattern','broad_exception_catch',"
            "'agentic_core/L2_execution/reasoning/hot.py',5)"
        )
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_exemptions_near_critical_paths "
            "WHERE exemption_kind = 'broad_exception_catch'"
        ).fetchone()[0]
        conn.close()
        assert count >= 1

    def test_debt_concentration_hotspot_weighted_score(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "toxic", "L2", "agentic_core/L2_execution/reasoning/toxic.py")
        _node2(conn, 2, "dst", "L3", "agentic_core/L3_orchestration/dst.py")
        e1 = conn.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no)"
            " VALUES (1,2,'violates','direct',"
            "'agentic_core/L2_execution/reasoning/toxic.py',1)"
        ).lastrowid
        e2 = conn.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no)"
            " VALUES (1,2,'violates','direct',"
            "'agentic_core/L2_execution/reasoning/toxic.py',2)"
        ).lastrowid
        conn.execute(
            "INSERT INTO violations(edge_id,category,file_path,severity)"
            " VALUES (?,'layer','agentic_core/L2_execution/reasoning/toxic.py','CRITICAL')",
            (e1,),
        )
        conn.execute(
            "INSERT INTO violations(edge_id,category,file_path,severity)"
            " VALUES (?,'layer','agentic_core/L2_execution/reasoning/toxic.py','HIGH')",
            (e2,),
        )
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT p0_count, p1_count, total_debt_score, hotspot_rank "
            "FROM mv_debt_concentration_hotspots "
            "WHERE file LIKE '%toxic%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1  # CRITICAL = p0
        assert row[1] == 1  # HIGH = p1
        assert row[2] >= 15  # 10*1 + 5*1
        assert row[3] == 1  # rank 1

    def test_repeated_p3_chronic_flag(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node2(conn, 1, "repeat_offender", "L2", "agentic_core/L2_execution/reasoning/repeat.py")
        _node2(conn, 2, "dst", "L3", "agentic_core/L3_orchestration/dst.py")
        for _ in range(3):
            conn.execute(
                "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no)"
                " VALUES (1,2,'antipattern','broad_exception_catch',"
                "'agentic_core/L2_execution/reasoning/repeat.py',1)"
            )
        conn.commit()
        conn.close()
        _setup_phases_ab(db)
        materialize_phase_c(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT p3_count, chronic_flag FROM mv_repeated_p3_near_critical_paths WHERE file LIKE '%repeat%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 3
        assert row[1] == 1
