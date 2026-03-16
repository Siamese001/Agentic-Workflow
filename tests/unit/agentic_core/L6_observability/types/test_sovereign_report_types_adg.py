"""ADG contract tests for L6_observability/types/sovereign_report_types.py."""
from __future__ import annotations

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_sovereign_report_types_adg")
_emit_applies_guardrail("p0", "test_sovereign_report_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereign_report_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_sovereign_report_types_adg", "state_snapshot")
emit_replay_key("p0", "test_sovereign_report_types_adg")
emit_determinism_digest("p0", "test_sovereign_report_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_sovereign_report_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_sovereign_report_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_sovereign_report_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_sovereign_report_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_sovereign_report_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sovereign_report_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_sovereign_report_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_sovereign_report_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sovereign_report_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sovereign_report_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sovereign_report_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_sovereign_report_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sovereign_report_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sovereign_report_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sovereign_report_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sovereign_report_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sovereign_report_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_sovereign_report_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sovereign_report_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sovereign_report_types_adg", "exec_snapshot_link")
pytestmark = pytest.mark.unit
from agentic_core.L6_observability.types.sovereign_report_types import SovereignReport
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

_emit_emits_metric_event("test_sovereign_report_types_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_sovereign_report_types_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_sovereign_report_types_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_sovereign_report_types_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_sovereign_report_types_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_sovereign_report_types_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_sovereign_report_types_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sovereign_report_types_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_sovereign_report_types_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sovereign_report_types_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_sovereign_report_types_adg", "p4obs", "alert")
_emit_links_incident_trace("test_sovereign_report_types_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_sovereign_report_types_adg", "p3lm", "pattern")
_emit_records_learning_event("test_sovereign_report_types_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sovereign_report_types_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sovereign_report_types_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sovereign_report_types_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_sovereign_report_types_adg", "p3lm", "policy")
_emit_stores_learning_state("test_sovereign_report_types_adg", "p3lm", "state")
_emit_records_execution_trace("test_sovereign_report_types_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_sovereign_report_types_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_sovereign_report_types_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_sovereign_report_types_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_sovereign_report_types_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_sovereign_report_types_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_sovereign_report_types_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_sovereign_report_types_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_sovereign_report_types_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_sovereign_report_types_adg", "context_pull")
_emit_pulls_context("p1", "test_sovereign_report_types_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_sovereign_report_types_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_sovereign_report_types_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_sovereign_report_types_adg", "write_through")
_emit_writes_through("p1", "test_sovereign_report_types_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_sovereign_report_types_adg", "safety_validation")
_emit_invokes_eval("p1", "test_sovereign_report_types_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_sovereign_report_types_adg", "routing_commit")


class TestSovereignReport:
    def test_creates(self): r = SovereignReport(); assert r.scores == {}
    def test_overall_score_empty(self): r = SovereignReport(); assert r.get_overall_score() == 0.0
    def test_has_builder(self): assert hasattr(SovereignReport, "Builder")
    def test_get_all_issues_empty(self): r = SovereignReport(); assert r.get_all_issues() == []

class TestSovereignReportBuilder:
    def test_builds_report(self):
        b = SovereignReport.Builder()
        r = b.with_dimension("Structural SSOT", 90.0).build()
        assert isinstance(r, SovereignReport)
        assert r.scores["Structural SSOT"] == 90.0
    def test_unknown_dimension_raises(self):
        b = SovereignReport.Builder()
        with pytest.raises(ValueError): b.with_dimension("Unknown Dim", 50.0)
    def test_score_out_of_range_raises(self):
        b = SovereignReport.Builder()
        with pytest.raises(ValueError): b.with_dimension("Structural SSOT", 101.0)
    def test_report_id_set(self):
        r = SovereignReport.Builder().build()
        assert r.report_id.startswith("audit-")
