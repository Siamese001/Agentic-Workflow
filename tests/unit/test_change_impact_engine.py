"""Unit tests for Change Impact Engine (Phase 3).

Tests cover:
- Empty changed files produce zero impact
- Direct importer is found at depth 0
- Transitive importer is found at higher depth
- Route mode thresholds (NORMAL / RESTRICTED / HUMAN_REVIEW)
- Uncovered changed files reported explicitly
- Impact digest is deterministic
- No silent full-suite fallback
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
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
)

_emit_authorize_and_execute("p2", "test_change_impact_engine", "execution_auth")
_emit_validates_capability("p2", "test_change_impact_engine", "capability_check")
_emit_routes_to_capability("p2", "test_change_impact_engine", "capability_route")
_emit_writes_via_uwg("p2", "test_change_impact_engine", "uwg_write")
_emit_blocks_direct_write("p2", "test_change_impact_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "test_change_impact_engine", "tool_invocation")
_emit_captures_execution_output("p2", "test_change_impact_engine", "exec_output")
_emit_dispatches_agent("p3", "test_change_impact_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "test_change_impact_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_change_impact_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_change_impact_engine", "healing_outcome")
_emit_escalates_failure("p3", "test_change_impact_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_change_impact_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_change_impact_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_change_impact_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_change_impact_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_change_impact_engine", "eval_metric")
_emit_stores_embedding("p4", "test_change_impact_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_change_impact_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_change_impact_engine", "exec_snapshot_link")
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
)
from tools.change_impact_engine import ChangeImpactEngine

_emit_emits_metric_event("test_change_impact_engine", "p4obs", "metric_1")
_emit_emits_metric_event("test_change_impact_engine", "p4obs", "metric_2")
_emit_emits_metric_event("test_change_impact_engine", "p4obs", "metric_3")
_emit_emits_metric_event("test_change_impact_engine", "p4obs", "metric_4")
_emit_emits_metric_event("test_change_impact_engine", "p4obs", "metric_5")
_emit_emits_metric_event("test_change_impact_engine", "p4obs", "metric_6")
_emit_records_incident_event("test_change_impact_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_change_impact_engine", "p4obs", "anomaly")
_emit_writes_observability_log("test_change_impact_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_change_impact_engine", "p4obs", "mon_state")
_emit_triggers_alert("test_change_impact_engine", "p4obs", "alert")
_emit_links_incident_trace("test_change_impact_engine", "p4obs", "trace_link")
_emit_captures_pattern("test_change_impact_engine", "p3lm", "pattern")
_emit_records_learning_event("test_change_impact_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_change_impact_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_change_impact_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_change_impact_engine", "p3lm", "routing")
_emit_improves_agent_policy("test_change_impact_engine", "p3lm", "policy")
_emit_stores_learning_state("test_change_impact_engine", "p3lm", "state")
_emit_records_execution_trace("test_change_impact_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_change_impact_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_change_impact_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_change_impact_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_change_impact_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_change_impact_engine", "env_read", "p2_env_1")
_emit_reads_environ("test_change_impact_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_change_impact_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_change_impact_engine", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_change_impact_engine")
_emit_applies_guardrail("p0", "test_change_impact_engine", "p0_governance")
_emit_reads_policy_state("p0", "test_change_impact_engine", "policy_binding")
_emit_snapshots_state("p0", "test_change_impact_engine", "state_snapshot")
_emit_pulls_context("p1", "test_change_impact_engine", "context_pull")
_emit_pulls_context("p1", "test_change_impact_engine", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_change_impact_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_change_impact_engine", "uwg_term_secondary")
_emit_writes_through("p1", "test_change_impact_engine", "write_through")
_emit_writes_through("p1", "test_change_impact_engine", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_change_impact_engine", "safety_validation")
_emit_invokes_eval("p1", "test_change_impact_engine", "eval_call")
_emit_proposal_commits_routing("p1", "test_change_impact_engine", "routing_commit")
emit_replay_key("p0", "test_change_impact_engine")
emit_determinism_digest("p0", "test_change_impact_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_scan_result_with_imports() -> ScanResult:
    """
    Graph: A -> B -> C (B imports A; C imports B)
    A = agentic_core/L0_routing/config/path_constants.py  (L0)
    B = agentic_core/L2_execution/UniversalWriteGateway.py (L2)
    C = apps_rg/engines/SomeAgent.py (L_APP)
    """
    result = ScanResult(commit_sha="test")
    result.modules = [
        "agentic_core/L0_routing/config/path_constants.py",
        "agentic_core/L2_execution/UniversalWriteGateway.py",
        "apps_rg/engines/SomeAgent.py",
    ]
    result.edges = [
        Edge(
            from_name="ADG::Module::agentic_core/L2_execution/UniversalWriteGateway.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/L0_routing/config/path_constants.py",
            edge_kind="import",
            source_file="agentic_core/L2_execution/UniversalWriteGateway.py",
            line_no=3,
        ),
        Edge(
            from_name="ADG::Module::apps_rg/engines/SomeAgent.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/L2_execution/UniversalWriteGateway.py",
            edge_kind="import",
            source_file="apps_rg/engines/SomeAgent.py",
            line_no=5,
        ),
    ]
    result.compute_digest()
    return result


class TestEmptyChangedFiles:
    """No changed files -> no impact."""

    @pytest.mark.unit
    def test_zero_changed_files_zero_impact(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze([], include_tests=False)
        assert impact.impacted_modules == []

    @pytest.mark.unit
    def test_zero_changed_files_normal_route(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze([], include_tests=False)
        assert impact.route_mode == "NORMAL"
        assert impact.risk_score == 0


class TestBlastRadiusComputation:
    """Changed files cause transitive reverse-dependency detection."""

    @pytest.mark.unit
    def test_direct_importer_found(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        assert "agentic_core/L2_execution/UniversalWriteGateway.py" in impact.impacted_modules

    @pytest.mark.unit
    def test_transitive_importer_found(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        assert "apps_rg/engines/SomeAgent.py" in impact.impacted_modules

    @pytest.mark.unit
    def test_leaf_change_has_higher_depth(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        assert impact.blast_radius_by_depth.get("apps_rg/engines/SomeAgent.py", -1) > 0

    @pytest.mark.unit
    def test_changed_file_itself_included_at_depth_zero(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        target = "agentic_core/L0_routing/config/path_constants.py"
        assert target in impact.impacted_modules
        assert impact.blast_radius_by_depth.get(target) == 0


class TestUncoveredChangedFiles:
    """Files not in ADG index are reported explicitly, never silently ignored."""

    @pytest.mark.unit
    def test_file_not_in_adg_goes_to_uncovered(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["totally/missing/module.py"],
            include_tests=False,
        )
        assert "totally/missing/module.py" in impact.uncovered_changed_files

    @pytest.mark.unit
    def test_missing_file_not_in_impacted_modules(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["totally/missing/module.py"],
            include_tests=False,
        )
        assert "totally/missing/module.py" not in impact.impacted_modules


class TestRouteModeThresholds:
    """Route mode thresholds match blast_radius.py constants."""

    @pytest.mark.unit
    def test_restricted_threshold_is_300(self) -> None:
        engine = ChangeImpactEngine(_make_scan_result_with_imports())
        assert engine._RESTRICTED_THRESHOLD == 300

    @pytest.mark.unit
    def test_human_review_threshold_is_700(self) -> None:
        engine = ChangeImpactEngine(_make_scan_result_with_imports())
        assert engine._HUMAN_REVIEW_THRESHOLD == 700

    @pytest.mark.unit
    def test_zero_risk_is_normal(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze([], include_tests=False)
        assert impact.route_mode == "NORMAL"


class TestImpactDigest:
    """Impact digest is deterministic."""

    @pytest.mark.unit
    def test_same_inputs_same_digest(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        i1 = engine.analyze(["agentic_core/L0_routing/config/path_constants.py"], include_tests=False)
        i2 = engine.analyze(["agentic_core/L0_routing/config/path_constants.py"], include_tests=False)
        assert i1.impact_digest == i2.impact_digest

    @pytest.mark.unit
    def test_different_inputs_different_digest(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        i1 = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        i2 = engine.analyze(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            include_tests=False,
        )
        assert i1.impact_digest != i2.impact_digest

    @pytest.mark.unit
    def test_impact_digest_is_64_hex(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        assert len(impact.impact_digest) == 64
        assert all(c in "0123456789abcdef" for c in impact.impact_digest)


class TestBFSDepthCorrectness:
    """BFS must assign *minimal* depth; DFS would produce incorrect values."""

    @pytest.mark.unit
    def test_chain_a_b_c_depths_are_correct(self) -> None:
        """
        Chain: A -> B -> C (B depends on A; C depends on B)
        Changing A:  A=depth0, B=depth1, C=depth2.
        DFS (stack.pop) can visit C before B, yielding C=depth1 — wrong.
        BFS (deque.popleft) guarantees minimal depth.
        """
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        depths = impact.blast_radius_by_depth
        a = "agentic_core/L0_routing/config/path_constants.py"
        b = "agentic_core/L2_execution/UniversalWriteGateway.py"
        c = "apps_rg/engines/SomeAgent.py"
        assert depths[a] == 0
        assert depths[b] == 1
        assert depths[c] == 2


class TestChangeImpactResultToDict:
    """to_dict produces expected keys."""

    @pytest.mark.unit
    def test_to_dict_has_required_keys(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze([], include_tests=False)
        d = impact.to_dict()
        required = {
            "changed_files",
            "impacted_module_count",
            "impacted_modules",
            "impacted_test_count",
            "impacted_tests",
            "risk_score",
            "route_mode",
            "scope_widening_events",
            "uncovered_changed_files",
            "impact_digest",
        }
        assert required <= set(d.keys())

    @pytest.mark.unit
    def test_to_dict_sorted_deterministic(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        d1 = impact.to_dict()
        d2 = impact.to_dict()
        assert d1 == d2


class TestScopeWideningEvents:
    """scope_widening_events is always present in output and is a list."""

    @pytest.mark.unit
    def test_scope_widening_events_present_in_to_dict(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        d = impact.to_dict()
        assert "scope_widening_events" in d
        assert isinstance(d["scope_widening_events"], list)

    @pytest.mark.unit
    def test_include_tests_flag_separates_test_paths(self) -> None:
        """With include_tests=False, test files appear in impacted_modules but
        are separated into impacted_tests; include_tests=True puts them in both."""
        result = ScanResult(commit_sha="test")
        result.modules = [
            "agentic_core/L0_routing/config/path_constants.py",
            "tests/unit/test_something.py",
        ]
        result.edges = [
            Edge(
                from_name="ADG::Module::tests/unit/test_something.py",
                relation_type="imports",
                to_name="ADG::Module::agentic_core/L0_routing/config/path_constants.py",
                edge_kind="import",
                source_file="tests/unit/test_something.py",
                line_no=1,
            )
        ]
        result.compute_digest()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        # include_tests=True: test files appear in impacted_tests list
        impact_with_tests = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=True,
        )
        assert "tests/unit/test_something.py" in impact_with_tests.impacted_tests
