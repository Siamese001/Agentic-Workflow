"""Architecture tests for ADG enhancements 6-10.

Covers:
  E6  - Deterministic graph snapshotting (CanonicalSnapshot / build_snapshot)
  E7  - Historical graph diff engine (GraphDiff / diff_snapshots)
  E8  - Ownership / blast-radius overlay (ModuleOwnership / OwnershipRegistry)
  E9  - Edge confidence and provenance scoring (EdgeConfidence / score_edges)
  E10 - Repair recommendation / routing layer (RepairRoute / route_violations)
"""

from __future__ import annotations

import json

#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_enhancements_6_10")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_enhancements_6_10", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_enhancements_6_10", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_enhancements_6_10", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_adg_enhancements_6_10", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_enhancements_6_10", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_enhancements_6_10", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_enhancements_6_10", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_enhancements_6_10", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_enhancements_6_10", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_enhancements_6_10", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_enhancements_6_10", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_enhancements_6_10", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_enhancements_6_10", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_enhancements_6_10", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_enhancements_6_10", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_enhancements_6_10", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_enhancements_6_10", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_enhancements_6_10", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_enhancements_6_10", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_enhancements_6_10", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_enhancements_6_10", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_enhancements_6_10", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_enhancements_6_10", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_enhancements_6_10", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_enhancements_6_10", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_enhancements_6_10", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_enhancements_6_10", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_enhancements_6_10", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_enhancements_6_10", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_enhancements_6_10", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_enhancements_6_10", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_enhancements_6_10", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_enhancements_6_10", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_enhancements_6_10", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_enhancements_6_10", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_enhancements_6_10", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_enhancements_6_10", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_enhancements_6_10", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_enhancements_6_10", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_enhancements_6_10", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_enhancements_6_10", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_enhancements_6_10", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_enhancements_6_10", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_enhancements_6_10", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_enhancements_6_10", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_enhancements_6_10", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_enhancements_6_10", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_enhancements_6_10", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_enhancements_6_10", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_enhancements_6_10", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_enhancements_6_10", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_enhancements_6_10")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_enhancements_6_10", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_enhancements_6_10")
# REMOVED: emit_determinism_digest("p0", "test_adg_enhancements_6_10")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_enhancements_6_10", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_enhancements_6_10", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_enhancements_6_10", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_enhancements_6_10", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_enhancements_6_10", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_enhancements_6_10", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_enhancements_6_10", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_enhancements_6_10", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_enhancements_6_10", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_enhancements_6_10", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_enhancements_6_10", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_enhancements_6_10", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_enhancements_6_10", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_enhancements_6_10", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_enhancements_6_10", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_enhancements_6_10", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_enhancements_6_10", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_enhancements_6_10", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_enhancements_6_10", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_enhancements_6_10", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_edge(
    from_name: str,
    relation: str,
    to_name: str,
    edge_kind: str = "import",
    source_file: str = "agentic_core/mod.py",
    line_no: int = 1,
    symbol: str = "",
) -> Edge:
    return Edge(
        from_name=from_name,
        relation_type=relation,
        to_name=to_name,
        edge_kind=edge_kind,
        source_file=source_file,
        line_no=line_no,
        symbol=symbol or to_name,
    )


def _make_result(edges: list[Edge], modules: list[str] | None = None) -> ScanResult:
    return ScanResult(
        edges=sorted(set(edges)),
        modules=sorted(modules or []),
        commit_sha="abc123",
    )


# ---------------------------------------------------------------------------
# Enhancement 6: Deterministic graph snapshotting
# ---------------------------------------------------------------------------


class TestCanonicalSnapshot:
    """E6: CanonicalSnapshot correctness and determinism."""

    def _build(self, edges: list[Edge]) -> object:
#  # MOVED: from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot

        return build_snapshot(_make_result(edges))

    def test_snapshot_has_graph_hash(self):
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot
                from agentic_core.adg.analysis.CanonicalSnapshot import CanonicalSnapshot
                from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot
                from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot
                from agentic_core.adg.analysis.GraphDiff import diff_snapshots
                from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot
                from agentic_core.adg.analysis.GraphDiff import diff_snapshots
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import ModuleOwnership
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
                from agentic_core.adg.analysis.EdgeConfidence import score_edge
                from agentic_core.adg.analysis.EdgeConfidence import score_edge
                from agentic_core.adg.analysis.EdgeConfidence import score_edge
                from agentic_core.adg.analysis.EdgeConfidence import score_edge
                from agentic_core.adg.analysis.EdgeConfidence import score_edge
                from agentic_core.adg.analysis.EdgeConfidence import score_edges
                from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges
                from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges
                from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges
                from agentic_core.adg.analysis.EdgeConfidence import score_edge
                from agentic_core.adg.analysis.EdgeConfidence import score_edge
                from agentic_core.adg.analysis.EdgeConfidence import score_edge
                from agentic_core.adg.analysis.EdgeConfidence import confidence_summary
                from agentic_core.adg.analysis.RepairRoute import route_violations
                from agentic_core.adg.analysis.RepairRoute import route_violations
                from agentic_core.adg.analysis.RepairRoute import route_violations
                from agentic_core.adg.analysis.RepairRoute import route_violations
                from agentic_core.adg.analysis.RepairRoute import route_violations
                from agentic_core.adg.analysis.RepairRoute import RepairRoute
                from agentic_core.adg.analysis.RepairRoute import repair_routing_summary, route_violations
                from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot
                from agentic_core.adg.analysis.GraphDiff import diff_snapshots
                from agentic_core.adg.analysis.RepairRoute import route_diff_violations
                from agentic_core.adg.analysis.RepairRoute import route_violations
                e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
                snap = self._build([e])
                assert len(snap.graph_hash) == 64  # SHA-256 hex

        assert len(snap.graph_hash) == 64  # SHA-256 hex

    def test_snapshot_deterministic_same_edges(self):
        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b"),
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::c"),
        ]
        snap1 = self._build(edges)
        snap2 = self._build(edges)
        assert snap1.graph_hash == snap2.graph_hash

    def test_snapshot_differs_on_different_edges(self):
        e1 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        e2 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::c")
        snap1 = self._build([e1])
        snap2 = self._build([e2])
        assert snap1.graph_hash != snap2.graph_hash

    def test_snapshot_node_count(self):
        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b"),
            _make_edge("ADG::Module::c.py", "imports", "ADG::Symbol::d"),
        ]
        snap = self._build(edges)
        assert snap.node_count == 4

    def test_snapshot_edge_count(self):
        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b"),
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::c"),
        ]
        snap = self._build(edges)
        assert snap.edge_count == 2

    def test_snapshot_violation_count(self):
        edges = [
            _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5"),
            _make_edge("ADG::Module::b.py", "imports", "ADG::Symbol::x"),
        ]
        snap = self._build(edges)
        assert snap.violation_count == 1

    def test_snapshot_coverage_count(self):
        edges = [
            _make_edge("ADG::Module::tests/test_a.py", "covers", "ADG::Module::a.py"),
        ]
        snap = self._build(edges)
        assert snap.coverage_count == 1

    def test_snapshot_call_count(self):
    """Test snapshot_call_count runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute snapshot_call_count
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        assert snap.governance_count == 2

    def test_snapshot_canonical_node_order_sorted(self):
        edges = [
            _make_edge("ADG::Module::z.py", "imports", "ADG::Symbol::a"),
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::z"),
        ]
        snap = self._build(edges)
        assert snap.canonical_node_order == sorted(snap.canonical_node_order)

    def test_snapshot_canonical_edge_order_sorted(self):
        edges = [
            _make_edge("ADG::Module::z.py", "imports", "ADG::Symbol::a"),
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::z"),
        ]
        snap = self._build(edges)
        assert snap.canonical_edge_order == sorted(snap.canonical_edge_order)

    def test_snapshot_to_dict_roundtrip(self):
        e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        snap = self._build([e])
        d = snap.to_dict()
        assert d["graph_hash"] == snap.graph_hash
        assert d["node_count"] == snap.node_count
        assert d["edge_count"] == snap.edge_count

    def test_snapshot_to_json_valid(self):
        e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        snap = self._build([e])
        j = snap.to_json()
        parsed = json.loads(j)
        assert "graph_hash" in parsed

    def test_snapshot_from_dict_roundtrip(self):
#  # MOVED: from agentic_core.adg.analysis.CanonicalSnapshot import CanonicalSnapshot

        e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        snap = self._build([e])
        d = snap.to_dict()
        restored = CanonicalSnapshot.from_dict(d)
        assert restored.graph_hash == snap.graph_hash
        assert restored.node_count == snap.node_count

    def test_snapshot_commit_sha_propagated(self):
#  # MOVED: from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot

        result = ScanResult(
            edges=sorted({_make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")}),
            modules=[],
            commit_sha="deadbeef",
        )
        snap = build_snapshot(result)
        assert snap.commit_sha == "deadbeef"

    def test_empty_result_snapshot(self):
        snap = self._build([])
        assert snap.node_count == 0
        assert snap.edge_count == 0
        assert snap.graph_hash != ""  # hash of empty canonical list

    def test_snapshot_schema_version_populated(self):
        e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        snap = self._build([e])
        assert snap.schema_version != ""
        assert snap.scanner_version != ""


# ---------------------------------------------------------------------------
# Enhancement 7: Historical graph diff engine
# ---------------------------------------------------------------------------


class TestGraphDiff:
    """E7: GraphDiff between two CanonicalSnapshots."""

    def _snap(self, edges: list[Edge]) -> object:
#  # MOVED: from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot

        return build_snapshot(_make_result(edges))

    def _diff(self, before_edges: list[Edge], after_edges: list[Edge]) -> object:
#  # MOVED: from agentic_core.adg.analysis.GraphDiff import diff_snapshots

        return diff_snapshots(self._snap(before_edges), self._snap(after_edges))

    def test_identical_snapshots_is_identical(self):
        edges = [_make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")]
        diff = self._diff(edges, edges)
        assert diff.is_identical is True

    def test_new_edge_detected(self):
        e1 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        e2 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::c")
        diff = self._diff([e1], [e1, e2])
        assert len(diff.new_edges) == 1
        assert diff.new_edges[0][1] == "imports"

    def test_removed_edge_detected(self):
        e1 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        e2 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::c")
        diff = self._diff([e1, e2], [e1])
        assert len(diff.removed_edges) == 1

    def test_new_violation_detected(self):
        e_ok = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        e_viol = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        diff = self._diff([e_ok], [e_ok, e_viol])
        assert len(diff.new_violations) == 1

    def test_resolved_violation_detected(self):
        e_ok = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        e_viol = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        diff = self._diff([e_ok, e_viol], [e_ok])
        assert len(diff.resolved_violations) == 1

    def test_risk_delta_positive_on_new_violation(self):
        e_viol = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        diff = self._diff([], [e_viol])
        assert diff.risk_delta > 0

    def test_risk_delta_negative_on_resolved_violation(self):
        e_viol = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        diff = self._diff([e_viol], [])
        assert diff.risk_delta < 0

    def test_risk_delta_zero_when_no_violation_change(self):
        e_import = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        e_new = _make_edge("ADG::Module::c.py", "imports", "ADG::Symbol::d")
        diff = self._diff([e_import], [e_import, e_new])
        assert diff.risk_delta == 0

    def test_new_coverage_edges_detected(self):
        e_cov = _make_edge("ADG::Module::tests/t.py", "covers", "ADG::Module::a.py")
        diff = self._diff([], [e_cov])
        assert len(diff.new_coverage) == 1

    def test_new_calls_detected(self):
    """Test new_calls_detected runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute new_calls_detected
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        assert diff.node_delta == 2

    def test_edge_delta(self):
        e1 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        e2 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::c")
        diff = self._diff([e1], [e1, e2])
        assert diff.edge_delta == 1

    def test_summary_identical(self):
        edges = [_make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")]
        diff = self._diff(edges, edges)
        assert "unchanged" in diff.summary

    def test_summary_regression(self):
        e_viol = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        diff = self._diff([], [e_viol])
        assert "WORSE" in diff.summary

    def test_summary_improved(self):
        e_viol = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        diff = self._diff([e_viol], [])
        assert "IMPROVED" in diff.summary

    def test_to_dict_roundtrip(self):
        e1 = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        e2 = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        diff = self._diff([e1], [e1, e2])
        d = diff.to_dict()
        assert "new_violations" in d
        assert len(d["new_violations"]) == 1

    def test_to_json_valid(self):
        e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        diff = self._diff([e], [e])
        j = diff.to_json()
        parsed = json.loads(j)
        assert "is_identical" in parsed

    def test_commit_shas_propagated(self):
#  # MOVED: from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot
#  # MOVED: from agentic_core.adg.analysis.GraphDiff import diff_snapshots

        r1 = ScanResult(edges=sorted({_make_edge("M::a", "imports", "S::b")}), modules=[], commit_sha="aaa")
        r2 = ScanResult(edges=sorted({_make_edge("M::a", "imports", "S::c")}), modules=[], commit_sha="bbb")
        diff = diff_snapshots(build_snapshot(r1), build_snapshot(r2))
        assert diff.commit_before == "aaa"
        assert diff.commit_after == "bbb"


# ---------------------------------------------------------------------------
# Enhancement 8: Ownership / blast-radius overlay
# ---------------------------------------------------------------------------


class TestOwnershipRegistry:
    """E8: ModuleOwnership and OwnershipRegistry."""

    def test_l0_routing_is_platform_high(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(["agentic_core/L0_routing/engines/router.py"])
        meta = reg.get("agentic_core/L0_routing/engines/router.py")
        assert meta.owner == "platform"
        assert meta.criticality == "high"

    def test_l5_safety_is_safety_governance(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(["agentic_core/L5_safety/config/ssot.py"])
        meta = reg.get("agentic_core/L5_safety/config/ssot.py")
        assert meta.owner == "safety"
        assert meta.runtime_surface == "governance"

    def test_apps_rg_owner(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(["apps_rg/reasoning/ATSCompatibilityAgent.py"])
        meta = reg.get("apps_rg/reasoning/ATSCompatibilityAgent.py")
        assert meta.owner == "apps_rg"

    def test_tests_is_ci_low(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(["tests/unit/test_foo.py"])
        meta = reg.get("tests/unit/test_foo.py")
        assert meta.runtime_surface == "CI"
        assert meta.criticality == "low"

    def test_unknown_module_returns_default(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry()
        meta = reg.get("some/unknown/module.py")
        assert meta.owner == "unknown"

    def test_blast_radius_high_risk_for_high_criticality_changed(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(
            [
                "agentic_core/L2_execution/UniversalWriteGateway.py",
                "agentic_core/L0_routing/engines/router.py",
                "agentic_core/L5_safety/config/ssot.py",
                "apps_rg/reasoning/ATSCompatibilityAgent.py",
            ]
        )
        report = reg.blast_radius_report(
            "agentic_core/L2_execution/UniversalWriteGateway.py",
            [
                "agentic_core/L0_routing/engines/router.py",
                "agentic_core/L5_safety/config/ssot.py",
                "apps_rg/reasoning/ATSCompatibilityAgent.py",
            ],
        )
        assert report["aggregate_risk"] == "HIGH"
        assert report["owner"] == "platform"
        assert report["impacted_module_count"] == 3

    def test_blast_radius_low_risk_for_low_criticality(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(["tools/some_script.py", "tests/unit/test_x.py"])
        report = reg.blast_radius_report("tools/some_script.py", ["tests/unit/test_x.py"])
        assert report["aggregate_risk"] == "LOW"

    def test_blast_radius_report_has_affected_domains(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(
            [
                "agentic_core/L0_routing/engines/r.py",
                "apps_rg/reasoning/a.py",
            ]
        )
        report = reg.blast_radius_report(
            "agentic_core/L0_routing/engines/r.py",
            ["apps_rg/reasoning/a.py"],
        )
        assert "apps_rg" in report["affected_domains"]

    def test_module_ownership_to_dict(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import ModuleOwnership

        m = ModuleOwnership(
            module_path="agentic_core/L2_execution/x.py",
            owner="platform",
            criticality="high",
            runtime_surface="governance",
        )
        d = m.to_dict()
        assert d["owner"] == "platform"
        assert d["criticality"] == "high"

    def test_registry_from_scan_result(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        result = _make_result([], modules=["agentic_core/L0_routing/engines/r.py", "apps_rg/reasoning/a.py"])
        reg = OwnershipRegistry.from_scan_result(result)
        assert reg.get("agentic_core/L0_routing/engines/r.py").owner == "platform"

    def test_to_json_valid(self):
#  # MOVED: from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(["agentic_core/L0_routing/x.py"])
        j = reg.to_json()
        parsed = json.loads(j)
        assert len(parsed) == 1


# ---------------------------------------------------------------------------
# Enhancement 9: Edge confidence and provenance scoring
# ---------------------------------------------------------------------------


class TestEdgeConfidence:
    """E9: EdgeConfidence assignment and summary."""

    def test_import_edge_confidence_1_0(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edge

        e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b", edge_kind="import")
        ec = score_edge(e)
        assert ec.confidence == 1.00
        assert ec.provenance == "ast_import"

    def test_inheritance_edge_confidence(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edge

        e = _make_edge("ADG::Module::a.py", "implements", "ADG::Symbol::Base", edge_kind="import")
        ec = score_edge(e)
        assert ec.confidence == 0.90
        assert ec.provenance == "ast_inheritance"

    def test_calls_edge_confidence(self):
    """Test calls_edge_confidence runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute calls_edge_confidence
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions

    def test_covers_edge_confidence_naming_heuristic(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edge

        e = _make_edge("ADG::Module::tests/t.py", "covers", "ADG::Module::a.py")
        ec = score_edge(e)
        assert ec.confidence == 0.65
        assert ec.provenance == "naming_heuristic"

    def test_network_edge_kind_reduces_confidence(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edge

        e = _make_edge("ADG::Module::a.py", "invokes_provider", "ADG::Symbol::openai", edge_kind="network")
        ec = score_edge(e)
        assert ec.confidence < 0.90

    def test_dynamic_exec_edge_kind_reduces_confidence(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edge

        e = _make_edge("ADG::Module::a.py", "influences", "ADG::Symbol::eval", edge_kind="dynamic_exec")
        ec = score_edge(e)
        assert ec.confidence < 0.75

    def test_score_edges_sorted(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edges

        edges = [
            _make_edge("ADG::Module::z.py", "imports", "ADG::Symbol::a"),
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::z"),
        ]
        scored = score_edges(edges)
        names = [ec.from_name for ec in scored]
        assert names == sorted(names)

    def test_confidence_summary_tiers(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges

        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b"),
            _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5"),
        ]
        scored = score_edges(edges)
        summary = confidence_summary(scored)
        assert summary["total_edges"] == 2
        assert summary["confidence_tiers"]["high"] >= 1
        assert summary["confidence_tiers"]["low"] >= 1

    def test_confidence_summary_average(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges

        edges = [_make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")]
        scored = score_edges(edges)
        summary = confidence_summary(scored)
        assert summary["average_confidence"] == 1.0

    def test_confidence_summary_provenance_breakdown(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges

        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b"),
            _make_edge("ADG::Module::a.py", "implements", "ADG::Symbol::Base"),
        ]
        scored = score_edges(edges)
        summary = confidence_summary(scored)
        assert "ast_import" in summary["provenance_breakdown"]
        assert "ast_inheritance" in summary["provenance_breakdown"]

    def test_confidence_clamp_max_1(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edge

        e = _make_edge("ADG::Module::a.py", "belongs_to_layer", "ADG::Layer::L0")
        ec = score_edge(e)
        assert ec.confidence <= 1.0

    def test_confidence_clamp_min_0(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edge

        e = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5", edge_kind="dynamic_exec")
        ec = score_edge(e)
        assert ec.confidence >= 0.0

    def test_edge_confidence_to_dict(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import score_edge

        e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        ec = score_edge(e)
        d = ec.to_dict()
        assert "confidence" in d
        assert "provenance" in d
        assert d["confidence"] == 1.0

    def test_empty_edges_summary(self):
#  # MOVED: from agentic_core.adg.analysis.EdgeConfidence import confidence_summary

        summary = confidence_summary([])
        assert summary["total_edges"] == 0
        assert summary["average_confidence"] == 0.0


# ---------------------------------------------------------------------------
# Enhancement 10: Repair recommendation / routing layer
# ---------------------------------------------------------------------------


class TestRepairRouting:
    """E10: RepairRoute recommendations from violation edges."""

    def test_violates_routes_to_architecture_governor(self):
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import route_violations

        e = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        routes = route_violations([e])
        assert len(routes) == 1
        assert routes[0].recommended_agent == "ArchitectureGovernorAgent"
        assert routes[0].ci_lane == "layer_guard"
        assert routes[0].severity == "critical"

    def test_dynamic_exec_routes_to_dynamic_review(self):
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import route_violations

        e = _make_edge("ADG::Module::a.py", "dynamic_exec", "ADG::Symbol::eval", edge_kind="dynamic_exec")
        routes = route_violations([e])
        assert any(r.recommended_agent == "DynamicExecReviewAgent" for r in routes)

    def test_invokes_provider_routes_to_dependency_repair(self):
    """Test invokes_provider_routes_to_dependency_repair runtime behavior."""
    # Arrange
    # TODO: Set up test data for invokes_provider_routes_to_dependency_repair
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute invokes_provider_routes_to_dependency_repair
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
    def test_routes_through_routes_to_healing_orchestrator(self):
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import route_violations

        e = _make_edge("ADG::Module::a.py", "routes_through", "ADG::Symbol::H", edge_kind="call")
        routes = route_violations([e])
        assert any(r.recommended_agent == "HealingOrchestrator" for r in routes)

    def test_benign_import_not_routed(self):
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import route_violations

        e = _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        routes = route_violations([e])
        assert routes == []

    def test_routes_sorted_by_severity(self):
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import route_violations

        edges = [
            _make_edge("ADG::Module::a.py", "invokes_provider", "ADG::Symbol::openai", edge_kind="network"),
            _make_edge("ADG::Module::b.py", "violates", "ADG::Layer::L5"),
        ]
        routes = route_violations(edges)
        severities = [r.severity for r in routes]
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        assert order[severities[0]] <= order[severities[-1]]

    def test_repair_route_to_dict(self):
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import RepairRoute

        r = RepairRoute(
            violation_type="violates",
            description="test",
            recommended_agent="ArchitectureGovernorAgent",
            ci_lane="layer_guard",
            severity="critical",
            source_file="a.py",
        )
        d = r.to_dict()
        assert d["recommended_agent"] == "ArchitectureGovernorAgent"
        assert d["ci_lane"] == "layer_guard"

    def test_routing_summary_counts(self):
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import repair_routing_summary, route_violations

        edges = [
            _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5"),
            _make_edge("ADG::Module::b.py", "violates", "ADG::Layer::L4"),
            _make_edge("ADG::Module::c.py", "invokes_provider", "ADG::Symbol::x", edge_kind="network"),
        ]
        routes = route_violations(edges)
        summary = repair_routing_summary(routes)
        assert summary["total_routes"] == 3
        assert summary["by_agent"]["ArchitectureGovernorAgent"] == 2

    def test_route_diff_violations_new_violation(self):
#  # MOVED: from agentic_core.adg.analysis.CanonicalSnapshot import build_snapshot
#  # MOVED: from agentic_core.adg.analysis.GraphDiff import diff_snapshots
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import route_diff_violations

        e_viol = _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L5")
        diff = diff_snapshots(build_snapshot(_make_result([])), build_snapshot(_make_result([e_viol])))
        routes = route_diff_violations(diff)
        assert any(r.recommended_agent == "ArchitectureGovernorAgent" for r in routes)
        assert any(r.recommended_agent == "DriftGovernorAgent" for r in routes)

    def test_route_diff_missing_test_coverage_for_new_calls(self):
    """Test route_diff_missing_coverage_for_new_calls runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute route_diff_missing_coverage_for_new_calls
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions

        edges = [_make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::b")]
        diff = diff_snapshots(build_snapshot(_make_result(edges)), build_snapshot(_make_result(edges)))
        routes = route_diff_violations(diff)
        assert routes == []

    def test_empty_edges_no_routes(self):
#  # MOVED: from agentic_core.adg.analysis.RepairRoute import route_violations

        assert route_violations([]) == []
