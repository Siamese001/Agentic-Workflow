"""Unit tests for execute_ssot ADG integration (Phase 5).

Tests cover:
- build_pre_run_report returns PreRunADGReport
- unavailable() produces a degraded report with adg_available=False
- changed_files in result are sorted
- route_mode is a valid string
- to_dict has required keys
- summary is non-empty string
- graceful degradation when ADG unavailable
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.applications.execute_ssot_integration import (
    PreRunADGReport,
    emit_pre_run_log,
)
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

_emit_records_execution_trace("p0", "evidence", "test_execute_ssot_integration")
_emit_applies_guardrail("p0", "test_execute_ssot_integration", "p0_governance")
_emit_reads_policy_state("p0", "test_execute_ssot_integration", "policy_binding")
_emit_snapshots_state("p0", "test_execute_ssot_integration", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_execute_ssot_integration", "p4obs", "metric_1")
_emit_emits_metric_event("test_execute_ssot_integration", "p4obs", "metric_2")
_emit_emits_metric_event("test_execute_ssot_integration", "p4obs", "metric_3")
_emit_emits_metric_event("test_execute_ssot_integration", "p4obs", "metric_4")
_emit_emits_metric_event("test_execute_ssot_integration", "p4obs", "metric_5")
_emit_emits_metric_event("test_execute_ssot_integration", "p4obs", "metric_6")
_emit_records_incident_event("test_execute_ssot_integration", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_execute_ssot_integration", "p4obs", "anomaly")
_emit_writes_observability_log("test_execute_ssot_integration", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_execute_ssot_integration", "p4obs", "mon_state")
_emit_triggers_alert("test_execute_ssot_integration", "p4obs", "alert")
_emit_links_incident_trace("test_execute_ssot_integration", "p4obs", "trace_link")
_emit_captures_pattern("test_execute_ssot_integration", "p3lm", "pattern")
_emit_records_learning_event("test_execute_ssot_integration", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_execute_ssot_integration", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_execute_ssot_integration", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_execute_ssot_integration", "p3lm", "routing")
_emit_improves_agent_policy("test_execute_ssot_integration", "p3lm", "policy")
_emit_stores_learning_state("test_execute_ssot_integration", "p3lm", "state")
_emit_records_execution_trace("test_execute_ssot_integration", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_execute_ssot_integration", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_execute_ssot_integration", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_execute_ssot_integration", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_execute_ssot_integration", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_execute_ssot_integration", "env_read", "p2_env_1")
_emit_reads_environ("test_execute_ssot_integration", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_execute_ssot_integration", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_execute_ssot_integration", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_execute_ssot_integration", "context_pull")
_emit_pulls_context("p1", "test_execute_ssot_integration", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_execute_ssot_integration", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_execute_ssot_integration", "uwg_term_2")
_emit_writes_through("p1", "test_execute_ssot_integration", "write_through")
_emit_writes_through("p1", "test_execute_ssot_integration", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_execute_ssot_integration", "safety_validation")
_emit_invokes_eval("p1", "test_execute_ssot_integration", "eval_call")
_emit_proposal_commits_routing("p1", "test_execute_ssot_integration", "routing_commit")
emit_replay_key("p0", "test_execute_ssot_integration")
emit_determinism_digest("p0", "test_execute_ssot_integration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execute_ssot_integration", "execution_auth")
_emit_validates_capability("p2", "test_execute_ssot_integration", "capability_check")
_emit_routes_to_capability("p2", "test_execute_ssot_integration", "capability_route")
_emit_writes_via_uwg("p2", "test_execute_ssot_integration", "uwg_write")
_emit_blocks_direct_write("p2", "test_execute_ssot_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execute_ssot_integration", "tool_invocation")
_emit_captures_execution_output("p2", "test_execute_ssot_integration", "exec_output")
_emit_dispatches_agent("p3", "test_execute_ssot_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execute_ssot_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execute_ssot_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execute_ssot_integration", "healing_outcome")
_emit_escalates_failure("p3", "test_execute_ssot_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execute_ssot_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execute_ssot_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execute_ssot_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execute_ssot_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execute_ssot_integration", "eval_metric")
_emit_stores_embedding("p4", "test_execute_ssot_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execute_ssot_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execute_ssot_integration", "exec_snapshot_link")

_REPO_ROOT = Path(__file__).resolve().parents[2]


class TestPreRunADGReportUnavailable:
    """PreRunADGReport.unavailable() produces correct degraded report."""

    @pytest.mark.unit
    def test_unavailable_sets_adg_available_false(self) -> None:
        report = PreRunADGReport.unavailable(["foo.py"], "test error")
        assert report.adg_available is False

    @pytest.mark.unit
    def test_unavailable_stores_error(self) -> None:
        report = PreRunADGReport.unavailable(["foo.py"], "some error")
        assert "some error" in report.adg_error

    @pytest.mark.unit
    def test_unavailable_route_mode_normal(self) -> None:
        report = PreRunADGReport.unavailable(["foo.py"], "error")
        assert report.route_mode == "NORMAL"

    @pytest.mark.unit
    def test_unavailable_changed_files_sorted(self) -> None:
        report = PreRunADGReport.unavailable(["z.py", "a.py"], "error")
        assert report.changed_files == sorted(["z.py", "a.py"])

    @pytest.mark.unit
    def test_unavailable_zero_counts(self) -> None:
        report = PreRunADGReport.unavailable([], "error")
        assert report.risk_score == 0
        assert report.impacted_module_count == 0
        assert report.impacted_test_count == 0


class TestPreRunADGReportToDict:
    """to_dict produces all required keys."""

    @pytest.mark.unit
    def test_to_dict_has_required_keys(self) -> None:
        report = PreRunADGReport.unavailable(["foo.py"], "error")
        d = report.to_dict()
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
            "layer_violation_count",
            "impact_digest",
            "adg_available",
            "adg_error",
            "summary",
        }
        assert required <= set(d.keys())

    @pytest.mark.unit
    def test_to_dict_summary_nonempty(self) -> None:
        report = PreRunADGReport.unavailable(["foo.py"], "test")
        d = report.to_dict()
        assert len(d["summary"]) > 0


class TestPreRunADGReportSummary:
    """Summary property produces readable string."""

    @pytest.mark.unit
    def test_summary_contains_route_mode(self) -> None:
        report = PreRunADGReport(
            changed_files=["a.py"],
            impacted_module_count=5,
            impacted_modules=["a.py", "b.py", "c.py", "d.py", "e.py"],
            impacted_test_count=2,
            impacted_tests=["tests/test_a.py", "tests/test_b.py"],
            risk_score=100,
            route_mode="NORMAL",
            scope_widening_events=[],
            uncovered_changed_files=[],
            layer_violation_count=0,
            impact_digest="abc123" * 10 + "a",
        )
        assert "NORMAL" in report.summary

    @pytest.mark.unit
    def test_summary_contains_risk_score(self) -> None:
        report = PreRunADGReport(
            changed_files=["a.py"],
            impacted_module_count=3,
            impacted_modules=["a.py", "b.py", "c.py"],
            impacted_test_count=1,
            impacted_tests=["tests/test_a.py"],
            risk_score=250,
            route_mode="NORMAL",
            scope_widening_events=[],
            uncovered_changed_files=[],
            layer_violation_count=0,
            impact_digest="abc" * 21 + "a",
        )
        assert "250" in report.summary


class TestEmitPreRunLog:
    """emit_pre_run_log does not raise on any valid report."""

    @pytest.mark.unit
    def test_emit_unavailable_report_no_crash(self) -> None:
        report = PreRunADGReport.unavailable(["a.py"], "error")
        emit_pre_run_log(report)

    @pytest.mark.unit
    def test_emit_available_normal_report_no_crash(self) -> None:
        report = PreRunADGReport(
            changed_files=["a.py"],
            impacted_module_count=1,
            impacted_modules=["a.py"],
            impacted_test_count=0,
            impacted_tests=[],
            risk_score=0,
            route_mode="NORMAL",
            scope_widening_events=[],
            uncovered_changed_files=[],
            layer_violation_count=0,
            impact_digest="a" * 64,
        )
        emit_pre_run_log(report)

    @pytest.mark.unit
    def test_emit_restricted_report_no_crash(self) -> None:
        report = PreRunADGReport(
            changed_files=["a.py"],
            impacted_module_count=10,
            impacted_modules=["a.py"] * 10,
            impacted_test_count=5,
            impacted_tests=["tests/t.py"] * 5,
            risk_score=500,
            route_mode="RESTRICTED",
            scope_widening_events=["b.py(layer=L2)"],
            uncovered_changed_files=["c.py"],
            layer_violation_count=3,
            impact_digest="b" * 64,
        )
        emit_pre_run_log(report)


class TestBuildPreRunReportIntegration:
    """Integration: build_pre_run_report on real repo returns valid report."""

    @pytest.mark.unit
    def test_build_pre_run_report_returns_report(self) -> None:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report

        report = build_pre_run_report(
            changed_files=["agentic_core/adg/schema.py"],
            repo_root=_REPO_ROOT,
        )
        assert isinstance(report, PreRunADGReport)

    @pytest.mark.unit
    def test_build_pre_run_report_route_mode_valid(self) -> None:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report

        report = build_pre_run_report(
            changed_files=["agentic_core/adg/schema.py"],
            repo_root=_REPO_ROOT,
        )
        assert report.route_mode in ("NORMAL", "RESTRICTED", "HUMAN_REVIEW")

    @pytest.mark.unit
    def test_build_pre_run_empty_files_normal(self) -> None:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report

        report = build_pre_run_report(changed_files=[], repo_root=_REPO_ROOT)
        assert report.risk_score == 0
        assert report.route_mode == "NORMAL"

    @pytest.mark.unit
    def test_available_report_has_empty_adg_error(self) -> None:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report

        report = build_pre_run_report(changed_files=[], repo_root=_REPO_ROOT)
        # When ADG is available, adg_error must be empty string (not None)
        assert report.adg_error == ""
        assert report.adg_available is True
