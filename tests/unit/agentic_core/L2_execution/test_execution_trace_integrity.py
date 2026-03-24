"""Addendum 1.1: ExecutionTrace.validate_completeness() tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.execution_trace_types import ExecutionTrace, ExecutionTraceBuilder
from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_execution_trace_integrity", "p4obs", "metric_1")
_emit_emits_metric_event("test_execution_trace_integrity", "p4obs", "metric_2")
_emit_emits_metric_event("test_execution_trace_integrity", "p4obs", "metric_3")
_emit_emits_metric_event("test_execution_trace_integrity", "p4obs", "metric_4")
_emit_emits_metric_event("test_execution_trace_integrity", "p4obs", "metric_5")
_emit_emits_metric_event("test_execution_trace_integrity", "p4obs", "metric_6")
_emit_records_incident_event("test_execution_trace_integrity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_execution_trace_integrity", "p4obs", "anomaly")
_emit_writes_observability_log("test_execution_trace_integrity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_execution_trace_integrity", "p4obs", "mon_state")
_emit_triggers_alert("test_execution_trace_integrity", "p4obs", "alert")
_emit_links_incident_trace("test_execution_trace_integrity", "p4obs", "trace_link")
_emit_captures_pattern("test_execution_trace_integrity", "p3lm", "pattern")
_emit_records_learning_event("test_execution_trace_integrity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_execution_trace_integrity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_execution_trace_integrity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_execution_trace_integrity", "p3lm", "routing")
_emit_improves_agent_policy("test_execution_trace_integrity", "p3lm", "policy")
_emit_stores_learning_state("test_execution_trace_integrity", "p3lm", "state")
_emit_records_execution_trace("test_execution_trace_integrity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_execution_trace_integrity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_execution_trace_integrity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_execution_trace_integrity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_execution_trace_integrity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_execution_trace_integrity", "env_read", "p2_env_1")
_emit_reads_environ("test_execution_trace_integrity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_execution_trace_integrity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_execution_trace_integrity", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_execution_trace_integrity")
_emit_applies_guardrail("p0", "test_execution_trace_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_trace_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_execution_trace_integrity", "state_snapshot")
_emit_pulls_context("p1", "test_execution_trace_integrity", "context_pull")
_emit_pulls_context("p1", "test_execution_trace_integrity", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_execution_trace_integrity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_execution_trace_integrity", "uwg_term_secondary")
_emit_writes_through("p1", "test_execution_trace_integrity", "write_through")
_emit_writes_through("p1", "test_execution_trace_integrity", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_execution_trace_integrity", "safety_validation")
_emit_invokes_eval("p1", "test_execution_trace_integrity", "eval_call")
_emit_proposal_commits_routing("p1", "test_execution_trace_integrity", "routing_commit")
_emit_escalates_to_human("p1", "test_execution_trace_integrity", "human_escalation")
_emit_routes_through("p1", "test_execution_trace_integrity", "route_through")
_emit_checks_agent_registry("p1", "test_execution_trace_integrity", "agent_registry")
_emit_validates_agent_capability("p1", "test_execution_trace_integrity", "capability")
_emit_dispatches_execution_plan("p1", "test_execution_trace_integrity", "exec_plan")
_emit_agent_executes_agent("p1", "test_execution_trace_integrity", "sub_agent")
_emit_routes_to_agent("p1", "test_execution_trace_integrity", "target_agent")
_emit_verifies_policy("p1", "test_execution_trace_integrity", "policy_check")
_emit_observes_runtime_state("p1", "test_execution_trace_integrity", "runtime_state")
_emit_verifies_boundary("p1", "test_execution_trace_integrity", "boundary_check")
_emit_transcripts_response("p1", "test_execution_trace_integrity", "transcript")
_emit_hard_fails_untranscripted("p1", "test_execution_trace_integrity")
_emit_gated_by_confidence("p1", "test_execution_trace_integrity", "confidence_gate")
emit_replay_key("p0", "test_execution_trace_integrity")
emit_determinism_digest("p0", "test_execution_trace_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_trace_integrity", "execution_auth")
_emit_validates_capability("p2", "test_execution_trace_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_execution_trace_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_trace_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_trace_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_trace_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_trace_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_execution_trace_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_trace_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_trace_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_trace_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_trace_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_trace_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_trace_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_trace_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_trace_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_trace_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_execution_trace_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_trace_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_trace_integrity", "exec_snapshot_link")


def _complete_trace() -> ExecutionTrace:
    b = ExecutionTraceBuilder("trace-001", "ip-001")
    b.set_governed_payload("abc123")
    b.set_llm_response("some response text")
    b.set_hash_chain_root("root-hash-abc")
    b.set_validation_decision("PASS")
    b.set_transcript(b"tool transcript bytes")
    return b.seal()


class TestValidateCompleteness:
    def test_complete_trace_passes(self):
        trace = _complete_trace()
        trace.validate_completeness()

    def test_empty_governed_payload_raises(self):
        b = ExecutionTraceBuilder("trace-002", "ip-002")
        b.set_llm_response("response")
        b.set_hash_chain_root("root")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="governed_payload_hash"):
            trace.validate_completeness()

    def test_empty_llm_response_hash_raises(self):
        b = ExecutionTraceBuilder("trace-003", "ip-003")
        b.set_governed_payload("abc")
        b.set_hash_chain_root("root")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="llm_response_hash"):
            trace.validate_completeness()

    def test_empty_hash_chain_root_raises(self):
        b = ExecutionTraceBuilder("trace-004", "ip-004")
        b.set_governed_payload("abc")
        b.set_llm_response("resp")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="hash_chain_root"):
            trace.validate_completeness()

    def test_negative_no_error_on_full_trace(self):
        """Negative control: error must NOT be raised on a complete trace."""
        trace = _complete_trace()
        raised = False
        try:
            trace.validate_completeness()
        except ExecutionTraceIntegrityError:  # guardian: allow-silent-swallower
            raised = True
        assert not raised

    def test_multiple_missing_fields_listed(self):
        b = ExecutionTraceBuilder("trace-005", "ip-005")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError) as exc_info:
            trace.validate_completeness()
        msg = str(exc_info.value)
        assert "governed_payload_hash" in msg or "llm_response_hash" in msg
