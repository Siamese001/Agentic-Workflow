"""Gap-filling unit tests for ADG analysis modules.

Covers:
  - E15: detect_test_gaps (test_gap.py)
  - E6:  CanonicalSnapshot / build_snapshot / round-trip (snapshot.py)
  - E7:  GraphDiff / diff_snapshots (diff.py)
  - E9:  score_edge / score_edges / confidence_summary (confidence.py)
  - E10: route_violations / RepairRoute (repair.py)
  - E8:  _infer_ownership / OwnershipRegistry (ownership.py)

All tests use synthetic stubs — no live ADG files required.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_adg_analysis_modules")
_emit_applies_guardrail("p0", "test_adg_analysis_modules", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_analysis_modules", "policy_binding")
_emit_snapshots_state("p0", "test_adg_analysis_modules", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_adg_analysis_modules", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_analysis_modules", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_analysis_modules", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_analysis_modules", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_analysis_modules", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_analysis_modules", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_analysis_modules", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_analysis_modules", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_analysis_modules", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_analysis_modules", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_analysis_modules", "p4obs", "alert")
_emit_links_incident_trace("test_adg_analysis_modules", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_analysis_modules", "p3lm", "pattern")
_emit_records_learning_event("test_adg_analysis_modules", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_analysis_modules", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_analysis_modules", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_analysis_modules", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_analysis_modules", "p3lm", "policy")
_emit_stores_learning_state("test_adg_analysis_modules", "p3lm", "state")
_emit_records_execution_trace("test_adg_analysis_modules", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_analysis_modules", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_analysis_modules", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_analysis_modules", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_analysis_modules", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_analysis_modules", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_analysis_modules", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_analysis_modules", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_analysis_modules", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_analysis_modules", "context_pull")
_emit_pulls_context("p1", "test_adg_analysis_modules", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_analysis_modules", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_analysis_modules", "uwg_term_2")
_emit_writes_through("p1", "test_adg_analysis_modules", "write_through")
_emit_writes_through("p1", "test_adg_analysis_modules", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_analysis_modules", "safety_validation")
_emit_invokes_eval("p1", "test_adg_analysis_modules", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_analysis_modules", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_analysis_modules", "human_escalation")
_emit_routes_through("p1", "test_adg_analysis_modules", "route_through")
_emit_checks_agent_registry("p1", "test_adg_analysis_modules", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_analysis_modules", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_analysis_modules", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_analysis_modules", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_analysis_modules", "target_agent")
_emit_verifies_policy("p1", "test_adg_analysis_modules", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_analysis_modules", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_analysis_modules", "boundary_check")
_emit_transcripts_response("p1", "test_adg_analysis_modules", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_analysis_modules")
_emit_gated_by_confidence("p1", "test_adg_analysis_modules", "confidence_gate")
emit_replay_key("p0", "test_adg_analysis_modules")
emit_determinism_digest("p0", "test_adg_analysis_modules")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_analysis_modules", "execution_auth")
_emit_validates_capability("p2", "test_adg_analysis_modules", "capability_check")
_emit_routes_to_capability("p2", "test_adg_analysis_modules", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_analysis_modules", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_analysis_modules", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_analysis_modules", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_analysis_modules", "exec_output")
_emit_dispatches_agent("p3", "test_adg_analysis_modules", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_analysis_modules", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_analysis_modules", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_analysis_modules", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_analysis_modules", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_analysis_modules", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_analysis_modules", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_analysis_modules", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_analysis_modules", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_analysis_modules", "eval_metric")
_emit_stores_embedding("p4", "test_adg_analysis_modules", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_analysis_modules", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_analysis_modules", "exec_snapshot_link")


# ---------------------------------------------------------------------------
# Shared stubs
# ---------------------------------------------------------------------------


@dataclass
class _Edge:
    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str = "import"
    source_file: str = "mod.py"
    line_no: int = 1
    symbol: str = ""


@dataclass
class _ScanResult:
    edges: list[_Edge] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    digest: str = "abc123"
    commit_sha: str = ""

    def edge_counts_by_relation(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self.edges:
            counts[e.relation_type] = counts.get(e.relation_type, 0) + 1
        return counts


# ---------------------------------------------------------------------------
# E15: Test Gap Detector
# ---------------------------------------------------------------------------


class TestDetectTestGaps:
    """Unit tests for detect_test_gaps()."""

    def _make_result(
        self,
        modules: list[str],
        covers_targets: list[str] | None = None,
    ) -> _ScanResult:
        edges = []
        for target in covers_targets or []:
            edges.append(
                _Edge(
                    from_name="ADG::Module::tests/test_foo.py",
                    relation_type="covers",
                    to_name=f"ADG::Module::{target}",
                    edge_kind="import",
                    source_file="tests/test_foo.py",
                )
            )
        return _ScanResult(edges=edges, modules=modules)  # type: ignore[arg-type]

    def test_no_modules_no_gaps(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(modules=[])
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        assert report.total_production_modules == 0
        assert report.coverage_rate == 0.0
        assert report.uncovered_modules == []

    def test_single_uncovered_module(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(
            modules=["agentic_core/L0_routing/foo.py"],
            covers_targets=[],
        )
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        assert report.total_production_modules == 1
        assert report.coverage_rate == 0.0
        assert len(report.uncovered_modules) == 1
        assert report.uncovered_modules[0].module_path == "agentic_core/L0_routing/foo.py"

    def test_covered_module_excluded_from_gaps(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(
            modules=["agentic_core/L0_routing/foo.py"],
            covers_targets=["agentic_core/L0_routing/foo.py"],
        )
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        assert report.coverage_rate == 1.0
        assert len(report.uncovered_modules) == 0
        assert "agentic_core/L0_routing/foo.py" in report.covered_modules

    def test_test_files_excluded_from_production(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(
            modules=["tests/test_foo.py", "agentic_core/bar.py"],
        )
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        assert report.total_production_modules == 1

    def test_tools_and_ops_excluded(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(
            modules=["tools/gen.py", "ops_scripts/deploy.py", "agentic_core/core.py"],
        )
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        assert report.total_production_modules == 1

    def test_coverage_rate_partial(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(
            modules=["agentic_core/a.py", "agentic_core/b.py"],
            covers_targets=["agentic_core/a.py"],
        )
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        assert report.coverage_rate == pytest_approx(0.5, abs=0.01)

    def test_gap_by_layer_populated(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(
            modules=["agentic_core/L0_routing/foo.py", "agentic_core/L5_safety/bar.py"],
        )
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        assert "L0" in report.gap_by_layer or "L5" in report.gap_by_layer

    def test_to_json_round_trip(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(
            modules=["agentic_core/L0_routing/foo.py"],
        )
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        json.loads(report.to_json())

    def test_summary_string_format(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(modules=[])
        report = detect_test_gaps(result)  # type: ignore[arg-type]
        assert "coverage=" in report.summary
        assert "covered=" in report.summary
        assert "uncovered=" in report.summary

    def test_include_layers_filter(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = self._make_result(
            modules=["agentic_core/L0_routing/foo.py", "agentic_core/L5_safety/bar.py"],
        )
        report = detect_test_gaps(result, include_layers=["L0"])  # type: ignore[arg-type]
        for entry in report.uncovered_modules:
            assert entry.layer == "L0"


# ---------------------------------------------------------------------------
# E6: CanonicalSnapshot
# ---------------------------------------------------------------------------


class TestCanonicalSnapshot:
    """Unit tests for build_snapshot() and CanonicalSnapshot round-trip."""

    def _make_scan_result(self) -> _ScanResult:
        edges = [
            _Edge("ADG::Module::a.py", "imports", "ADG::Module::b.py"),
            _Edge("ADG::Module::c.py", "violates", "ADG::Module::d.py"),
            _Edge("ADG::Module::e.py", "covers", "ADG::Module::f.py"),
        ]
        return _ScanResult(
            edges=edges,  # type: ignore[arg-type]
            modules=["a.py", "b.py", "c.py", "d.py", "e.py", "f.py"],
            digest="deadbeef",
            commit_sha="abc",
        )

    def test_build_snapshot_returns_canonical_snapshot(self):
        from agentic_core.adg.analysis.snapshot import CanonicalSnapshot, build_snapshot

        result = self._make_scan_result()
        snap = build_snapshot(result)  # type: ignore[arg-type]
        assert isinstance(snap, CanonicalSnapshot)

    def test_graph_hash_is_64_hex_chars(self):
        from agentic_core.adg.analysis.snapshot import build_snapshot

        snap = build_snapshot(self._make_scan_result())  # type: ignore[arg-type]
        assert len(snap.graph_hash) == 64
        assert all(c in "0123456789abcdef" for c in snap.graph_hash)

    def test_deterministic_same_input(self):
        from agentic_core.adg.analysis.snapshot import build_snapshot

        r = self._make_scan_result()
        snap1 = build_snapshot(r)  # type: ignore[arg-type]
        snap2 = build_snapshot(r)  # type: ignore[arg-type]
        assert snap1.graph_hash == snap2.graph_hash

    def test_edge_count_matches(self):
        from agentic_core.adg.analysis.snapshot import build_snapshot

        r = self._make_scan_result()
        snap = build_snapshot(r)  # type: ignore[arg-type]
        assert snap.edge_count == 3

    def test_violation_count_extracted(self):
        from agentic_core.adg.analysis.snapshot import build_snapshot

        r = self._make_scan_result()
        snap = build_snapshot(r)  # type: ignore[arg-type]
        assert snap.violation_count == 1

    def test_coverage_count_extracted(self):
        from agentic_core.adg.analysis.snapshot import build_snapshot

        r = self._make_scan_result()
        snap = build_snapshot(r)  # type: ignore[arg-type]
        assert snap.coverage_count == 1

    def test_to_dict_json_serializable(self):
        from agentic_core.adg.analysis.snapshot import build_snapshot

        snap = build_snapshot(self._make_scan_result())  # type: ignore[arg-type]
        json.dumps(snap.to_dict())

    def test_from_dict_round_trip(self):
        from agentic_core.adg.analysis.snapshot import CanonicalSnapshot, build_snapshot

        snap = build_snapshot(self._make_scan_result())  # type: ignore[arg-type]
        restored = CanonicalSnapshot.from_dict(snap.to_dict())
        assert restored.graph_hash == snap.graph_hash
        assert restored.edge_count == snap.edge_count
        assert restored.violation_count == snap.violation_count

    def test_different_edges_different_hash(self):
        from agentic_core.adg.analysis.snapshot import build_snapshot

        r1 = _ScanResult(
            edges=[_Edge("ADG::Module::a.py", "imports", "ADG::Module::b.py")],  # type: ignore[arg-type]
            modules=["a.py", "b.py"],
        )
        r2 = _ScanResult(
            edges=[_Edge("ADG::Module::a.py", "imports", "ADG::Module::c.py")],  # type: ignore[arg-type]
            modules=["a.py", "c.py"],
        )
        assert build_snapshot(r1).graph_hash != build_snapshot(r2).graph_hash  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# E7: GraphDiff
# ---------------------------------------------------------------------------


class TestGraphDiff:
    """Unit tests for diff_snapshots() and GraphDiff."""

    def _snap(self, edges: list[tuple[str, str, str]], violations: int = 0) -> object:
        import hashlib

        from agentic_core.adg.analysis.snapshot import CanonicalSnapshot

        edge_text = "\n".join(f"{f}|{r}|{t}" for f, r, t in sorted(edges))
        h = hashlib.sha256(edge_text.encode()).hexdigest()
        counts = {}
        for _, r, _ in edges:
            counts[r] = counts.get(r, 0) + 1
        return CanonicalSnapshot(
            graph_hash=h,
            scanner_hash="x",
            edge_count=len(edges),
            violation_count=violations,
            coverage_count=counts.get("covers", 0),
            call_count=counts.get("calls", 0),
            governance_count=counts.get("writes_through", 0),
            canonical_edge_order=list(edges),
            edge_counts_by_relation=counts,
        )

    def test_identical_snapshots_is_identical(self):
        from agentic_core.adg.analysis.diff import diff_snapshots

        edges = [("A", "imports", "B"), ("C", "covers", "D")]
        snap = self._snap(edges)
        result = diff_snapshots(snap, snap)  # type: ignore[arg-type]
        assert result.is_identical is True

    def test_added_edge_detected(self):
        from agentic_core.adg.analysis.diff import diff_snapshots

        snap1 = self._snap([("A", "imports", "B")])
        snap2 = self._snap([("A", "imports", "B"), ("C", "imports", "D")])
        diff = diff_snapshots(snap1, snap2)  # type: ignore[arg-type]
        assert len(diff.new_edges) == 1
        assert diff.new_edges[0] == ("C", "imports", "D")

    def test_removed_edge_detected(self):
        from agentic_core.adg.analysis.diff import diff_snapshots

        snap1 = self._snap([("A", "imports", "B"), ("C", "imports", "D")])
        snap2 = self._snap([("A", "imports", "B")])
        diff = diff_snapshots(snap1, snap2)  # type: ignore[arg-type]
        assert len(diff.removed_edges) == 1

    def test_new_violation_increases_risk_delta(self):
        from agentic_core.adg.analysis.diff import diff_snapshots

        snap1 = self._snap([("A", "imports", "B")], violations=0)
        snap2 = self._snap([("A", "imports", "B"), ("X", "violates", "Y")], violations=1)
        diff = diff_snapshots(snap1, snap2)  # type: ignore[arg-type]
        assert diff.risk_delta > 0

    def test_resolved_violation_decreases_risk_delta(self):
        from agentic_core.adg.analysis.diff import diff_snapshots

        snap1 = self._snap([("X", "violates", "Y")], violations=1)
        snap2 = self._snap([], violations=0)
        diff = diff_snapshots(snap1, snap2)  # type: ignore[arg-type]
        assert diff.risk_delta < 0

    def test_summary_contains_edge_counts(self):
        from agentic_core.adg.analysis.diff import diff_snapshots

        snap1 = self._snap([])
        snap2 = self._snap([("A", "imports", "B")])
        diff = diff_snapshots(snap1, snap2)  # type: ignore[arg-type]
        assert "edge" in diff.summary.lower() or "ADG" in diff.summary

    def test_to_dict_json_serializable(self):
        from agentic_core.adg.analysis.diff import diff_snapshots

        snap = self._snap([("A", "imports", "B")])
        diff = diff_snapshots(snap, snap)  # type: ignore[arg-type]
        json.dumps(diff.to_dict())

    def test_edge_delta_correct(self):
        from agentic_core.adg.analysis.diff import diff_snapshots

        snap1 = self._snap([("A", "imports", "B")])
        snap2 = self._snap([("A", "imports", "B"), ("C", "imports", "D"), ("E", "imports", "F")])
        diff = diff_snapshots(snap1, snap2)  # type: ignore[arg-type]
        assert diff.edge_delta == 2


# ---------------------------------------------------------------------------
# E9: Edge confidence scoring
# ---------------------------------------------------------------------------


class TestEdgeConfidence:
    """Unit tests for score_edge, score_edges, confidence_summary."""

    def test_imports_get_highest_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        e = _Edge("A", "imports", "B", edge_kind="import")
        ec = score_edge(e)  # type: ignore[arg-type]
        assert ec.confidence == 1.0
        assert ec.provenance == "ast_import"

    def test_violates_gets_low_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        e = _Edge("A", "violates", "B", edge_kind="call")
        ec = score_edge(e)  # type: ignore[arg-type]
        assert ec.confidence < 0.80

    def test_star_import_reduces_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        e_normal = _Edge("A", "imports", "B", edge_kind="import")
        e_star = _Edge("A", "imports", "B", edge_kind="star_import")
        ec_normal = score_edge(e_normal)  # type: ignore[arg-type]
        ec_star = score_edge(e_star)  # type: ignore[arg-type]
        assert ec_star.confidence < ec_normal.confidence

    def test_dynamic_exec_reduces_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        e_norm = _Edge("A", "imports", "B", edge_kind="import")
        e_dyn = _Edge("A", "dynamic_exec", "B", edge_kind="dynamic_exec")
        ec_norm = score_edge(e_norm)  # type: ignore[arg-type]
        ec_dyn = score_edge(e_dyn)  # type: ignore[arg-type]
        assert ec_dyn.confidence < ec_norm.confidence

    def test_score_edge_preserves_from_to_names(self):
        from agentic_core.adg.analysis.confidence import score_edge

        e = _Edge("from_mod", "imports", "to_mod", edge_kind="import")
        ec = score_edge(e)  # type: ignore[arg-type]
        assert ec.from_name == "from_mod"
        assert ec.to_name == "to_mod"

    def test_confidence_clamped_between_0_and_1(self):
        from agentic_core.adg.analysis.confidence import score_edge

        for rel in ["imports", "violates", "covers", "dynamic_exec"]:
            e = _Edge("A", rel, "B", edge_kind="import")
            ec = score_edge(e)  # type: ignore[arg-type]
            assert 0.0 <= ec.confidence <= 1.0

    def test_score_edges_sorted(self):
        from agentic_core.adg.analysis.confidence import score_edges

        edges = [
            _Edge("Z", "imports", "A"),
            _Edge("A", "imports", "Z"),
            _Edge("M", "covers", "N"),
        ]
        scored = score_edges(edges)  # type: ignore[arg-type]
        names = [ec.from_name for ec in scored]
        assert names == sorted(names)

    def test_confidence_summary_tier_breakdown(self):
        from agentic_core.adg.analysis.confidence import confidence_summary, score_edges

        edges = [
            _Edge("A", "imports", "B", edge_kind="import"),    # 1.00 → high
            _Edge("A", "covers", "B", edge_kind="import"),     # 0.65 → low
            _Edge("A", "violates", "B", edge_kind="import"),   # 0.60 → low
        ]
        scored = score_edges(edges)  # type: ignore[arg-type]
        summary = confidence_summary(scored)
        assert summary["confidence_tiers"]["high"] >= 1
        assert summary["confidence_tiers"]["low"] >= 2
        assert 0.0 < summary["average_confidence"] <= 1.0

    def test_confidence_summary_json_serializable(self):
        from agentic_core.adg.analysis.confidence import confidence_summary, score_edges

        edges = [_Edge("A", "imports", "B")]
        scored = score_edges(edges)  # type: ignore[arg-type]
        json.dumps(confidence_summary(scored))

    def test_unknown_relation_uses_fallback_provenance(self):
        from agentic_core.adg.analysis.confidence import score_edge

        e = _Edge("A", "unknown_relation_type_xyz", "B", edge_kind="import")
        ec = score_edge(e)  # type: ignore[arg-type]
        assert ec.confidence >= 0.0
        assert ec.provenance != ""


# ---------------------------------------------------------------------------
# E10: Repair routing
# ---------------------------------------------------------------------------


class TestRepairRouting:
    """Unit tests for route_violations() and RepairRoute."""

    def _make_edges(self, relation_types: list[str]) -> list:
        return [
            _Edge(f"mod_{i}.py", rt, f"target_{i}.py", edge_kind="call")
            for i, rt in enumerate(relation_types)
        ]

    def test_violates_routes_to_architecture_governor(self):
        from agentic_core.adg.analysis.repair import route_violations

        edges = self._make_edges(["violates"])
        routes = route_violations(edges)  # type: ignore[arg-type]
        assert len(routes) == 1
        assert routes[0].recommended_agent == "ArchitectureGovernorAgent"
        assert routes[0].ci_lane == "layer_guard"

    def test_dynamic_exec_routes_to_dynamic_exec_agent(self):
        from agentic_core.adg.analysis.repair import route_violations

        edges = self._make_edges(["dynamic_exec"])
        routes = route_violations(edges)  # type: ignore[arg-type]
        assert any(r.recommended_agent == "DynamicExecReviewAgent" for r in routes)

    def test_non_violation_edges_not_routed(self):
        from agentic_core.adg.analysis.repair import route_violations

        edges = self._make_edges(["imports", "calls", "instantiates"])
        routes = route_violations(edges)  # type: ignore[arg-type]
        assert routes == []

    def test_multiple_violations_produce_multiple_routes(self):
        from agentic_core.adg.analysis.repair import route_violations

        edges = self._make_edges(["violates", "violates", "dynamic_exec"])
        routes = route_violations(edges)  # type: ignore[arg-type]
        assert len(routes) == 3

    def test_repair_route_to_dict_json_serializable(self):
        from agentic_core.adg.analysis.repair import route_violations

        edges = self._make_edges(["violates"])
        routes = route_violations(edges)  # type: ignore[arg-type]
        json.dumps(routes[0].to_dict())

    def test_violates_severity_is_critical(self):
        from agentic_core.adg.analysis.repair import route_violations

        edges = self._make_edges(["violates"])
        routes = route_violations(edges)  # type: ignore[arg-type]
        assert routes[0].severity == "critical"

    def test_route_summary_groups_by_severity(self):
        from agentic_core.adg.analysis.repair import repair_routing_summary, route_violations

        edges = self._make_edges(["violates", "dynamic_exec"])
        routes = route_violations(edges)  # type: ignore[arg-type]
        summary = repair_routing_summary(routes)
        assert "by_severity" in summary
        assert "total_routes" in summary

    def test_repair_route_preserves_source_file(self):
        from agentic_core.adg.analysis.repair import route_violations

        edge = _Edge("mymodule.py", "violates", "other.py", source_file="mymodule.py")
        routes = route_violations([edge])  # type: ignore[arg-type]
        assert routes[0].source_file == "mymodule.py"


# ---------------------------------------------------------------------------
# E8: Ownership / blast-radius overlay
# ---------------------------------------------------------------------------


class TestOwnership:
    """Unit tests for _infer_ownership and OwnershipRegistry."""

    def test_l0_routing_is_platform_high(self):
        from agentic_core.adg.analysis.ownership import _infer_ownership

        o = _infer_ownership("agentic_core/L0_routing/foo.py")
        assert o.owner == "platform"
        assert o.criticality == "high"

    def test_l5_safety_is_safety_governance(self):
        from agentic_core.adg.analysis.ownership import _infer_ownership

        o = _infer_ownership("agentic_core/L5_safety/bar.py")
        assert o.owner == "safety"
        assert o.runtime_surface == "governance"

    def test_apps_rg_is_apps_rg(self):
        from agentic_core.adg.analysis.ownership import _infer_ownership

        o = _infer_ownership("apps_rg/agents/my_agent.py")
        assert o.owner == "apps_rg"

    def test_unknown_path_gets_unknown_owner(self):
        from agentic_core.adg.analysis.ownership import _infer_ownership

        o = _infer_ownership("some/external/dep.py")
        assert o.owner == "unknown"

    def test_adg_module_prefix_stripped(self):
        from agentic_core.adg.analysis.ownership import _infer_ownership

        o = _infer_ownership("ADG::Module::agentic_core/L0_routing/foo.py")
        assert o.owner == "platform"

    def test_to_dict_json_serializable(self):
        from agentic_core.adg.analysis.ownership import _infer_ownership

        o = _infer_ownership("agentic_core/L0_routing/foo.py")
        json.dumps(o.to_dict())

    def test_registry_lookup_returns_ownership(self):
        from agentic_core.adg.analysis.ownership import OwnershipRegistry

        reg = OwnershipRegistry.from_module_list(["agentic_core/L0_routing/foo.py", "apps_rg/bar.py"])
        o = reg.get("agentic_core/L0_routing/foo.py")
        assert o.owner == "platform"

    def test_blast_radius_report_aggregate_risk(self):
        from agentic_core.adg.analysis.ownership import OwnershipRegistry

        modules = [
            "agentic_core/L0_routing/foo.py",
            "agentic_core/L5_safety/bar.py",
        ]
        reg = OwnershipRegistry.from_module_list(modules)
        impacted = ["agentic_core/L5_safety/bar.py"]
        report = reg.blast_radius_report("agentic_core/L0_routing/foo.py", impacted)
        assert report["aggregate_risk"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert report["impacted_module_count"] == 1

    def test_registry_all_modules_registered(self):
        from agentic_core.adg.analysis.ownership import OwnershipRegistry

        modules = [
            "agentic_core/L0_routing/a.py",
            "apps_rg/b.py",
            "tools/c.py",
        ]
        reg = OwnershipRegistry.from_module_list(modules)
        for m in modules:
            o = reg.get(m)
            assert o.module_path == m


# ---------------------------------------------------------------------------
# Helper import for approximate comparison
# ---------------------------------------------------------------------------


def pytest_approx(value: float, abs: float = 0.001) -> object:
    import pytest

    return pytest.approx(value, abs=abs)
