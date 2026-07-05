"""Tests for Phase B materialized views (capability/egress, tool/agent, task-contract)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from tools.generate.materialized_views.phase_a_path_authority import materialize_phase_a
from tools.generate.materialized_views.phase_b_capability_tool_task import (
    _PHASE_B_TABLES,
    materialize_phase_b,
)


# ---------------------------------------------------------------------------
# Shared fixture helpers (mirrors phase_a test helpers)
# ---------------------------------------------------------------------------


def _create_minimal_db(tmp_path: Path, commit_sha: str = "bbb456") -> Path:
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
    conn.execute("INSERT INTO meta(key,value) VALUES ('artifact_digest', 'digest_bbb')")
    conn.execute("INSERT INTO meta(key,value) VALUES ('scanner_digest', 'scanner_bbb')")
    conn.commit()
    conn.close()
    return db


def _node(
    conn: sqlite3.Connection,
    nid: int,
    name: str,
    layer: str,
    path: str,
    entity_type: str = "module",
    identity_kind: str = "internal_module",
) -> None:
    conn.execute(
        "INSERT INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path)"
        " VALUES (?,?,?,?,?,'high',?)",
        (nid, name, entity_type, layer, identity_kind, path),
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


def _setup_phase_a(db: Path) -> None:
    """Run Phase A so Phase B views that depend on it succeed."""
    materialize_phase_a(db)


# ---------------------------------------------------------------------------
# Phase B: basic contract
# ---------------------------------------------------------------------------


class TestPhaseBTableCreation:
    def test_all_tables_created(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        _setup_phase_a(db)
        counts = materialize_phase_b(db)
        assert set(counts.keys()) == set(_PHASE_B_TABLES)

    def test_empty_db_returns_zero_counts(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        _setup_phase_a(db)
        counts = materialize_phase_b(db)
        for tbl in _PHASE_B_TABLES:
            assert counts[tbl] == 0, f"{tbl} should be 0 on empty DB"

    def test_idempotent_refresh(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        _setup_phase_a(db)
        counts1 = materialize_phase_b(db)
        counts2 = materialize_phase_b(db)
        assert counts1 == counts2

    def test_snapshot_id_populated(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path, commit_sha="phase_b_sha")
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "src", "L2", "agentic_core/L2_execution/reasoning/src.py")
        _node(conn, 2, "provider", "L2", "agentic_core/L2_execution/reasoning/prov.py")
        _edge(conn, 1, 2, "invokes_provider")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT snapshot_id FROM mv_capability_and_egress_gaps LIMIT 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "phase_b_sha"


# ---------------------------------------------------------------------------
# Family 4 — Capability / provider / egress
# ---------------------------------------------------------------------------


class TestCapabilityEgressViews:
    def test_provider_without_capability_route(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "prov", "L2", "agentic_core/L2_execution/reasoning/prov.py")
        _edge(conn, 1, 2, "invokes_provider")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_type FROM mv_capability_and_egress_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "provider_without_capability_route"

    def test_capability_route_present_no_gap(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "prov", "L2", "agentic_core/L2_execution/reasoning/prov.py")
        _node(conn, 3, "cap", "L3", "agentic_core/L3_orchestration/cap.py")
        _edge(conn, 1, 2, "invokes_provider")
        _edge(conn, 1, 3, "routes_to_capability")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_type FROM mv_capability_and_egress_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is None or row[0] == "ok"

    def test_provider_sprawl_multi_provider(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "prov_a", "L2", "agentic_core/L2_execution/reasoning/prov_a.py")
        _node(conn, 3, "prov_b", "L2", "agentic_core/L2_execution/reasoning/prov_b.py")
        _edge(conn, 1, 2, "invokes_provider")
        _edge(conn, 1, 3, "invokes_provider")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT provider_count, sprawl_flag FROM mv_provider_surface_sprawl WHERE file LIKE '%actor%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 2
        assert row[1] == 1

    def test_gateway_bypass_non_infra_path(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "prov", "L2", "agentic_core/L2_execution/reasoning/prov.py")
        _edge(conn, 1, 2, "invokes_provider", source_file="agentic_core/L2_execution/reasoning/actor.py")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute("SELECT COUNT(*) FROM mv_gateway_bypass_paths").fetchone()[0]
        conn.close()
        assert count >= 1

    def test_gateway_bypass_approved_path_not_flagged(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "gateway", "L_SHARED", "infrastructure/sdks_mcps/client_wrappers.py")
        _node(conn, 2, "prov", "L2", "agentic_core/L2_execution/reasoning/prov.py")
        _edge(conn, 1, 2, "invokes_provider", source_file="infrastructure/sdks_mcps/client_wrappers.py")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM mv_gateway_bypass_paths WHERE src_file LIKE '%sdks_mcps%'"
        ).fetchone()[0]
        conn.close()
        assert count == 0

    def test_gateway_bypass_contrast_approved_and_non_approved_same_run(self, tmp_path: Path) -> None:
        """G7: approved path excluded; non-approved path included — both in same run."""
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        # Non-approved caller (must be flagged)
        _node(conn, 1, "bad_actor", "L2", "agentic_core/L2_execution/reasoning/bad_actor.py")
        # Approved gateway caller (must NOT be flagged)
        _node(conn, 2, "gateway", "L_SHARED", "infrastructure/sdks_mcps/gateway.py")
        _node(conn, 3, "prov", "L2", "agentic_core/L2_execution/reasoning/prov.py")
        _edge(conn, 1, 3, "invokes_provider", source_file="agentic_core/L2_execution/reasoning/bad_actor.py")
        _edge(conn, 2, 3, "invokes_provider", source_file="infrastructure/sdks_mcps/gateway.py")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        flagged_bad = conn.execute(
            "SELECT COUNT(*) FROM mv_gateway_bypass_paths WHERE src_file LIKE '%bad_actor%'"
        ).fetchone()[0]
        flagged_good = conn.execute(
            "SELECT COUNT(*) FROM mv_gateway_bypass_paths WHERE src_file LIKE '%sdks_mcps%'"
        ).fetchone()[0]
        conn.close()
        assert flagged_bad >= 1, "Non-approved bypass must appear in mv_gateway_bypass_paths"
        assert flagged_good == 0, "Approved gateway path must NOT appear in mv_gateway_bypass_paths"


# ---------------------------------------------------------------------------
# Family 5 — Tool and agent shape
# ---------------------------------------------------------------------------


class TestToolAgentViews:
    def test_tool_surface_overlap_multi_layer_callers(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "MyTool", "L_SHARED", "tools/shared/my_tool.py")
        _node(conn, 2, "caller_l2", "L2", "agentic_core/L2_execution/reasoning/c.py")
        _node(conn, 3, "caller_l1", "L1", "agentic_core/L1_cognition/c.py")
        _edge(conn, 2, 1, "imports")
        _edge(conn, 3, 1, "imports")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT caller_count, distinct_caller_layers FROM mv_tool_surface_overlap "
            "WHERE tool_file LIKE '%my_tool%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 2
        assert row[1] == 2

    def test_agent_tool_ratio_no_tools_anomaly(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "MyAgent", "L2", "agentic_core/L2_execution/reasoning/MyAgent.py")
        _node(conn, 2, "AnotherAgent", "L2", "agentic_core/L2_execution/reasoning/AnotherAgent.py")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT anomaly_flag FROM mv_agent_tool_ratio WHERE layer = 'L2'").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1

    def test_manager_sprawl_flagged_above_threshold(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "BigOrchestrator", "L3", "agentic_core/L3_orchestration/big_orchestrator.py")
        for i in range(6):
            _node(conn, 10 + i, f"agent_{i}", "L2", f"agentic_core/L2_execution/reasoning/agent_{i}.py")
            _edge(conn, 1, 10 + i, "routes_to_agent")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT direct_report_count, sprawl_flag FROM mv_manager_sprawl "
            "WHERE manager_file LIKE '%big_orchestrator%'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 6
        assert row[1] == 1


# ---------------------------------------------------------------------------
# Family 6 — Task-contract and action-safety
# ---------------------------------------------------------------------------


class TestTaskContractViews:
    def test_task_contract_gap_action_no_policy(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "target", "L4", "agentic_core/L4_state/store.py")
        _edge(conn, 1, 2, "writes_to")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_flag FROM mv_task_contract_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "action_without_contract"

    def test_task_contract_ok_with_policy(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "target", "L4", "agentic_core/L4_state/store.py")
        _node(conn, 3, "policy", "L2", "agentic_core/L2_execution/enforcement/policy.py")
        _edge(conn, 1, 2, "writes_to")
        _edge(conn, 1, 3, "reads_policy_state")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_flag FROM mv_task_contract_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is None or row[0] == "ok"

    def test_untrusted_text_to_action_dynamic_exec(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "actor", "L2", "agentic_core/L2_execution/reasoning/actor.py")
        _node(conn, 2, "dyn", "L2", "agentic_core/L2_execution/reasoning/dyn.py")
        _edge(conn, 1, 2, "dynamic_exec")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT dynamic_exec_count FROM mv_untrusted_text_to_action_risk WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1

    def test_structured_output_gap_generates_prompt_no_schema(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "prompter", "L1", "agentic_core/L1_cognition/prompter.py")
        _node(conn, 2, "prompt_target", "L2", "agentic_core/L2_execution/reasoning/target.py")
        _edge(conn, 1, 2, "generates_prompt")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT gap_flag FROM mv_structured_output_gaps WHERE node_id = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 1

    def test_structured_output_gap_r0_prompt_symbol_counts_as_schema(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "prompter", "L0", "agentic_core/L0_routing/reasoning/assembly_stage.py")
        _node(conn, 2, "prompt_target", "L2", "agentic_core/L2_execution/reasoning/target.py")
        _edge(conn, 1, 2, "generates_prompt", symbol="R0:json")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT output_schema_flag, gap_flag FROM mv_structured_output_gaps WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row == (1, 0)


# ---------------------------------------------------------------------------
# Remaining Family 10 — Topology
# ---------------------------------------------------------------------------


class TestTopologyViews:
    def test_dependency_cone_risk_single_hop(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "core", "L2", "agentic_core/L2_execution/reasoning/core.py")
        _node(conn, 2, "caller", "L1", "agentic_core/L1_cognition/caller.py")
        _edge(conn, 2, 1, "imports")
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT direct_fan_in, cone_risk_score FROM mv_dependency_cone_risk WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] >= 1
        assert row[1] > 0.0

    def test_high_fan_in_with_defects_combined_score(self, tmp_path: Path) -> None:
        db = _create_minimal_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "hot", "L2", "agentic_core/L2_execution/reasoning/hot.py")
        _node(conn, 2, "ca", "L1", "agentic_core/L1_cognition/ca.py")
        _edge(conn, 2, 1, "imports")
        eid = conn.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no)"
            " VALUES (1,2,'violates','direct','agentic_core/L2_execution/reasoning/hot.py',5)"
        ).lastrowid
        conn.execute(
            "INSERT INTO violations(edge_id,category,severity) VALUES (?,'layer_violation','HIGH')",
            (eid,),
        )
        conn.commit()
        conn.close()
        _setup_phase_a(db)
        materialize_phase_b(db)
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT violation_count, combined_risk_score FROM mv_high_fan_in_out_with_defects "
            "WHERE node_id = 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] >= 1
        assert row[1] > 0.0
