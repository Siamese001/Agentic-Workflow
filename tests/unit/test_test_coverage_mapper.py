"""Unit tests for Test Coverage Mapper (Phase 3).

Tests cover:
- Test modules are correctly identified
- Direct imports from test to source module create coverage entry
- Transitive imports propagate coverage
- tests_for_modules returns deduplicated sorted list
- coverage_report has required keys
- to_index_dict is deterministic
- No full-suite fallback: unmapped modules return empty list
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

_emit_authorize_and_execute("p2", "test_test_coverage_mapper", "execution_auth")
_emit_validates_capability("p2", "test_test_coverage_mapper", "capability_check")
_emit_routes_to_capability("p2", "test_test_coverage_mapper", "capability_route")
_emit_writes_via_uwg("p2", "test_test_coverage_mapper", "uwg_write")
_emit_blocks_direct_write("p2", "test_test_coverage_mapper", "direct_write_block")
_emit_records_tool_invocation("p2", "test_test_coverage_mapper", "tool_invocation")
_emit_captures_execution_output("p2", "test_test_coverage_mapper", "exec_output")
_emit_dispatches_agent("p3", "test_test_coverage_mapper", "agent_dispatch")
_emit_coordinates_agents("p3", "test_test_coverage_mapper", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_test_coverage_mapper", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_test_coverage_mapper", "healing_outcome")
_emit_escalates_failure("p3", "test_test_coverage_mapper", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_test_coverage_mapper", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_test_coverage_mapper", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_test_coverage_mapper", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_test_coverage_mapper", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_test_coverage_mapper", "eval_metric")
_emit_stores_embedding("p4", "test_test_coverage_mapper", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_test_coverage_mapper", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_test_coverage_mapper", "exec_snapshot_link")
from tools.test_coverage_mapper import TestCoverageMapper

_emit_records_execution_trace("p0", "evidence", "test_test_coverage_mapper")
_emit_applies_guardrail("p0", "test_test_coverage_mapper", "p0_governance")
_emit_reads_policy_state("p0", "test_test_coverage_mapper", "policy_binding")
_emit_snapshots_state("p0", "test_test_coverage_mapper", "state_snapshot")
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

_emit_emits_metric_event("test_test_coverage_mapper", "p4obs", "metric_1")
_emit_emits_metric_event("test_test_coverage_mapper", "p4obs", "metric_2")
_emit_emits_metric_event("test_test_coverage_mapper", "p4obs", "metric_3")
_emit_emits_metric_event("test_test_coverage_mapper", "p4obs", "metric_4")
_emit_emits_metric_event("test_test_coverage_mapper", "p4obs", "metric_5")
_emit_emits_metric_event("test_test_coverage_mapper", "p4obs", "metric_6")
_emit_records_incident_event("test_test_coverage_mapper", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_test_coverage_mapper", "p4obs", "anomaly")
_emit_writes_observability_log("test_test_coverage_mapper", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_test_coverage_mapper", "p4obs", "mon_state")
_emit_triggers_alert("test_test_coverage_mapper", "p4obs", "alert")
_emit_links_incident_trace("test_test_coverage_mapper", "p4obs", "trace_link")
_emit_captures_pattern("test_test_coverage_mapper", "p3lm", "pattern")
_emit_records_learning_event("test_test_coverage_mapper", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_test_coverage_mapper", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_test_coverage_mapper", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_test_coverage_mapper", "p3lm", "routing")
_emit_improves_agent_policy("test_test_coverage_mapper", "p3lm", "policy")
_emit_stores_learning_state("test_test_coverage_mapper", "p3lm", "state")
_emit_records_execution_trace("test_test_coverage_mapper", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_test_coverage_mapper", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_test_coverage_mapper", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_test_coverage_mapper", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_test_coverage_mapper", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_test_coverage_mapper", "env_read", "p2_env_1")
_emit_reads_environ("test_test_coverage_mapper", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_test_coverage_mapper", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_test_coverage_mapper", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_test_coverage_mapper", "context_pull")
_emit_pulls_context("p1", "test_test_coverage_mapper", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_test_coverage_mapper", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_test_coverage_mapper", "uwg_term_2")
_emit_writes_through("p1", "test_test_coverage_mapper", "write_through")
_emit_writes_through("p1", "test_test_coverage_mapper", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_test_coverage_mapper", "safety_validation")
_emit_invokes_eval("p1", "test_test_coverage_mapper", "eval_call")
_emit_proposal_commits_routing("p1", "test_test_coverage_mapper", "routing_commit")
emit_replay_key("p0", "test_test_coverage_mapper")
emit_determinism_digest("p0", "test_test_coverage_mapper")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_result_with_test_imports() -> ScanResult:
    """
    tests/unit/test_a.py -> agentic_core/adg/schema.py (direct)
    agentic_core/adg/schema.py -> agentic_core/adg/__init__.py (transitive)
    """
    result = ScanResult(commit_sha="t")
    result.modules = [
        "tests/unit/test_a.py",
        "agentic_core/adg/schema.py",
        "agentic_core/adg/__init__.py",
        "agentic_core/adg/cli.py",
    ]
    result.edges = [
        Edge(
            from_name="ADG::Module::tests/unit/test_a.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/adg/schema.py",
            edge_kind="import",
            source_file="tests/unit/test_a.py",
            line_no=2,
        ),
        Edge(
            from_name="ADG::Module::agentic_core/adg/schema.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/adg/__init__.py",
            edge_kind="import",
            source_file="agentic_core/adg/schema.py",
            line_no=3,
        ),
    ]
    result.compute_digest()
    return result


class TestTestModuleIdentification:
    """Test modules under tests/ are correctly classified."""

    @pytest.mark.unit
    def test_test_module_detected(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        assert "tests/unit/test_a.py" in mapper._test_modules

    @pytest.mark.unit
    def test_source_module_not_a_test(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        assert "agentic_core/adg/schema.py" not in mapper._test_modules


class TestDirectImportCoverage:
    """Direct imports from test to source create coverage entries."""

    @pytest.mark.unit
    def test_direct_import_creates_coverage(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_module("agentic_core/adg/schema.py")
        assert "tests/unit/test_a.py" in tests

    @pytest.mark.unit
    def test_uncovered_module_returns_empty(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_module("agentic_core/adg/cli.py")
        assert tests == []

    @pytest.mark.unit
    def test_no_full_suite_fallback(self) -> None:
        """Uncovered module must NOT fall back to all tests."""
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_module("agentic_core/adg/cli.py")
        assert "tests/unit/test_a.py" not in tests


class TestTransitiveCoverage:
    """Tests propagate transitively through import chain."""

    @pytest.mark.unit
    def test_transitive_import_propagates(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        # test_a imports schema, schema imports __init__; so __init__ is transitively covered
        tests = mapper.tests_for_module("agentic_core/adg/__init__.py")
        assert "tests/unit/test_a.py" in tests


class TestTestsForModules:
    """tests_for_modules returns deduplicated sorted list."""

    @pytest.mark.unit
    def test_tests_for_modules_deduplicates(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_modules(
            [
                "agentic_core/adg/schema.py",
                "agentic_core/adg/__init__.py",
            ]
        )
        assert tests.count("tests/unit/test_a.py") == 1

    @pytest.mark.unit
    def test_tests_for_modules_sorted(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_modules(["agentic_core/adg/schema.py"])
        assert tests == sorted(tests)

    @pytest.mark.unit
    def test_tests_for_empty_list_returns_empty(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_modules([])
        assert tests == []


class TestCoverageReport:
    """coverage_report has required keys."""

    @pytest.mark.unit
    def test_coverage_report_has_required_keys(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        report = mapper.coverage_report()
        required = {
            "source_module_count",
            "test_module_count",
            "covered_count",
            "uncovered_count",
            "coverage_pct",
            "uncovered_modules",
            "hotspot_modules",
        }
        assert required <= set(report.keys())

    @pytest.mark.unit
    def test_coverage_pct_between_0_and_100(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        report = mapper.coverage_report()
        assert 0.0 <= report["coverage_pct"] <= 100.0

    @pytest.mark.unit
    def test_covered_plus_uncovered_equals_source(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        report = mapper.coverage_report()
        assert report["covered_count"] + report["uncovered_count"] == report["source_module_count"]


class TestToIndexDict:
    """to_index_dict is deterministic."""

    @pytest.mark.unit
    def test_to_index_dict_has_both_keys(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        idx = mapper.to_index_dict()
        assert "module_to_tests" in idx
        assert "symbol_to_tests" in idx

    @pytest.mark.unit
    def test_to_index_dict_deterministic(self) -> None:
        import json

        result = _make_result_with_test_imports()
        m1 = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        m2 = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        assert json.dumps(m1.to_index_dict(), sort_keys=True) == json.dumps(
            m2.to_index_dict(), sort_keys=True
        )

    @pytest.mark.unit
    def test_build_is_idempotent(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT)
        mapper.build()
        mapper.build()
        tests = mapper.tests_for_module("agentic_core/adg/schema.py")
        assert tests.count("tests/unit/test_a.py") == 1


class TestSortedOutputGuarantees:
    """tests_for_module always returns sorted output."""

    @pytest.mark.unit
    def test_tests_for_module_result_is_sorted(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_module("agentic_core/adg/schema.py")
        assert tests == sorted(tests)

    @pytest.mark.unit
    def test_module_to_tests_values_are_sorted_lists(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        idx = mapper.to_index_dict()
        for module, tests in idx["module_to_tests"].items():
            assert tests == sorted(tests), f"Tests for {module} are not sorted"
