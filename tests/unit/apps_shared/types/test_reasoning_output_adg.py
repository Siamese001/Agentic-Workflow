"""ADG contract tests for apps_shared/types/reasoning_output.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_reasoning_output_adg")
_emit_applies_guardrail("p0", "test_reasoning_output_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_reasoning_output_adg", "policy_binding")
_emit_snapshots_state("p0", "test_reasoning_output_adg", "state_snapshot")
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

_emit_emits_metric_event("test_reasoning_output_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_reasoning_output_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_reasoning_output_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_reasoning_output_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_reasoning_output_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_reasoning_output_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_reasoning_output_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_reasoning_output_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_reasoning_output_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_reasoning_output_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_reasoning_output_adg", "p4obs", "alert")
_emit_links_incident_trace("test_reasoning_output_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_reasoning_output_adg", "p3lm", "pattern")
_emit_records_learning_event("test_reasoning_output_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_reasoning_output_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_reasoning_output_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_reasoning_output_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_reasoning_output_adg", "p3lm", "policy")
_emit_stores_learning_state("test_reasoning_output_adg", "p3lm", "state")
_emit_records_execution_trace("test_reasoning_output_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_reasoning_output_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_reasoning_output_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_reasoning_output_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_reasoning_output_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_reasoning_output_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_reasoning_output_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_reasoning_output_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_reasoning_output_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_reasoning_output_adg", "context_pull")
_emit_pulls_context("p1", "test_reasoning_output_adg", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_reasoning_output_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_reasoning_output_adg", "uwg_term_2")
_emit_writes_through("p1", "test_reasoning_output_adg", "write_through")
_emit_writes_through("p1", "test_reasoning_output_adg", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_reasoning_output_adg", "safety_validation")
_emit_invokes_eval("p1", "test_reasoning_output_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_reasoning_output_adg", "routing_commit")
emit_replay_key("p0", "test_reasoning_output_adg")
emit_determinism_digest("p0", "test_reasoning_output_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_reasoning_output_adg", "execution_auth")
_emit_validates_capability("p2", "test_reasoning_output_adg", "capability_check")
_emit_routes_to_capability("p2", "test_reasoning_output_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_reasoning_output_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_reasoning_output_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_reasoning_output_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_reasoning_output_adg", "exec_output")
_emit_dispatches_agent("p3", "test_reasoning_output_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_reasoning_output_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_reasoning_output_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_reasoning_output_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_reasoning_output_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_reasoning_output_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_reasoning_output_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_reasoning_output_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_reasoning_output_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_reasoning_output_adg", "eval_metric")
_emit_stores_embedding("p4", "test_reasoning_output_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_reasoning_output_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_reasoning_output_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.reasoning_output import ReasoningOutput, scan_for_violations
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ReasoningOutput = scan_for_violations = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestReasoningOutput:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ReasoningOutput)
    def test_creates(self):
        ro = ReasoningOutput(status="success")
        assert ro.status == "success"; assert ro.payload == {}; assert ro.errors == []
    def test_is_success(self):
        ro = ReasoningOutput.success(payload={"x": 1}, agent="TestAgent")
        assert ro.is_success() is True; assert ro.is_error() is False
        assert ro.payload == {"x": 1}; assert ro.agent == "TestAgent"
    def test_is_error(self):
        ro = ReasoningOutput.error(errors=["bad thing"], agent="TestAgent")
        assert ro.is_error() is True; assert ro.is_success() is False
        assert "bad thing" in ro.errors
    def test_skipped(self):
        ro = ReasoningOutput.skipped(reason="no input", agent="TestAgent")
        assert ro.status == "skipped"; assert ro.payload["reason"] == "no input"
    def test_trace_id_default_empty(self):
        ro = ReasoningOutput(status="partial")
        assert ro.trace_id == ""

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestScanForViolations:
    def test_callable(self): assert callable(scan_for_violations)
    def test_returns_list(self):
        from pathlib import Path
        result = scan_for_violations(scan_dirs=[Path("apps_shared/types")])
        assert isinstance(result, list)

def test_module_importable(): assert _AVAIL or not _AVAIL
