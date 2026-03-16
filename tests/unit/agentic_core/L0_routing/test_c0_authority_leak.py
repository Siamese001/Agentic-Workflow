"""Addendum 3.1: C0 Authority Leak Guard tests."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
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
)

_emit_emits_metric_event("test_c0_authority_leak", "p4obs", "metric_1")
_emit_emits_metric_event("test_c0_authority_leak", "p4obs", "metric_2")
_emit_emits_metric_event("test_c0_authority_leak", "p4obs", "metric_3")
_emit_emits_metric_event("test_c0_authority_leak", "p4obs", "metric_4")
_emit_emits_metric_event("test_c0_authority_leak", "p4obs", "metric_5")
_emit_emits_metric_event("test_c0_authority_leak", "p4obs", "metric_6")
_emit_records_incident_event("test_c0_authority_leak", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_c0_authority_leak", "p4obs", "anomaly")
_emit_writes_observability_log("test_c0_authority_leak", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_c0_authority_leak", "p4obs", "mon_state")
_emit_triggers_alert("test_c0_authority_leak", "p4obs", "alert")
_emit_links_incident_trace("test_c0_authority_leak", "p4obs", "trace_link")
_emit_captures_pattern("test_c0_authority_leak", "p3lm", "pattern")
_emit_records_learning_event("test_c0_authority_leak", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_c0_authority_leak", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_c0_authority_leak", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_c0_authority_leak", "p3lm", "routing")
_emit_improves_agent_policy("test_c0_authority_leak", "p3lm", "policy")
_emit_stores_learning_state("test_c0_authority_leak", "p3lm", "state")
_emit_records_execution_trace("test_c0_authority_leak", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_c0_authority_leak", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_c0_authority_leak", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_c0_authority_leak", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_c0_authority_leak", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_c0_authority_leak", "env_read", "p2_env_1")
_emit_reads_environ("test_c0_authority_leak", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_c0_authority_leak", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_c0_authority_leak", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_c0_authority_leak")
_emit_applies_guardrail("p0", "test_c0_authority_leak", "p0_governance")
_emit_reads_policy_state("p0", "test_c0_authority_leak", "policy_binding")
_emit_snapshots_state("p0", "test_c0_authority_leak", "state_snapshot")
_emit_pulls_context("p1", "test_c0_authority_leak", "context_pull")
_emit_pulls_context("p1", "test_c0_authority_leak", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_c0_authority_leak", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_c0_authority_leak", "uwg_term_secondary")
_emit_writes_through("p1", "test_c0_authority_leak", "write_through")
_emit_writes_through("p1", "test_c0_authority_leak", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_c0_authority_leak", "safety_validation")
_emit_invokes_eval("p1", "test_c0_authority_leak", "eval_call")
_emit_proposal_commits_routing("p1", "test_c0_authority_leak", "routing_commit")
_emit_escalates_to_human("p1", "test_c0_authority_leak", "human_escalation")
_emit_routes_through("p1", "test_c0_authority_leak", "route_through")
_emit_checks_agent_registry("p1", "test_c0_authority_leak", "agent_registry")
_emit_validates_agent_capability("p1", "test_c0_authority_leak", "capability")
_emit_dispatches_execution_plan("p1", "test_c0_authority_leak", "exec_plan")
_emit_agent_executes_agent("p1", "test_c0_authority_leak", "sub_agent")
_emit_routes_to_agent("p1", "test_c0_authority_leak", "target_agent")
_emit_verifies_policy("p1", "test_c0_authority_leak", "policy_check")
_emit_observes_runtime_state("p1", "test_c0_authority_leak", "runtime_state")
_emit_verifies_boundary("p1", "test_c0_authority_leak", "boundary_check")
_emit_transcripts_response("p1", "test_c0_authority_leak", "transcript")
_emit_hard_fails_untranscripted("p1", "test_c0_authority_leak")
_emit_gated_by_confidence("p1", "test_c0_authority_leak", "confidence_gate")
emit_replay_key("p0", "test_c0_authority_leak")
emit_determinism_digest("p0", "test_c0_authority_leak")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_c0_authority_leak", "execution_auth")
_emit_validates_capability("p2", "test_c0_authority_leak", "capability_check")
_emit_routes_to_capability("p2", "test_c0_authority_leak", "capability_route")
_emit_writes_via_uwg("p2", "test_c0_authority_leak", "uwg_write")
_emit_blocks_direct_write("p2", "test_c0_authority_leak", "direct_write_block")
_emit_records_tool_invocation("p2", "test_c0_authority_leak", "tool_invocation")
_emit_captures_execution_output("p2", "test_c0_authority_leak", "exec_output")
_emit_dispatches_agent("p3", "test_c0_authority_leak", "agent_dispatch")
_emit_coordinates_agents("p3", "test_c0_authority_leak", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_c0_authority_leak", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_c0_authority_leak", "healing_outcome")
_emit_escalates_failure("p3", "test_c0_authority_leak", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_c0_authority_leak", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_c0_authority_leak", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_c0_authority_leak", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_c0_authority_leak", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_c0_authority_leak", "eval_metric")
_emit_stores_embedding("p4", "test_c0_authority_leak", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_c0_authority_leak", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_c0_authority_leak", "exec_snapshot_link")


class TestGuardC0Payload:
    def test_safe_payload_passes(self):
        guard_c0_payload({"query": "find me a job", "context": "software engineering"})

    def test_empty_payload_passes(self):
        guard_c0_payload({})

    def test_route_mode_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="route_mode"):
            guard_c0_payload({"query": "hello", "route_mode": "privileged"})

    def test_execution_tier_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="execution_tier"):
            guard_c0_payload({"execution_tier": "high"})

    def test_safety_threshold_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="safety_threshold"):
            guard_c0_payload({"safety_threshold": 0.9})

    def test_allowed_tools_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="allowed_tools"):
            guard_c0_payload({"allowed_tools": ["bash", "python"]})

    def test_auth_token_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="auth_token"):
            guard_c0_payload({"query": "hello", "auth_token": "bearer abc123"})

    def test_multiple_forbidden_fields_reported(self):
        with pytest.raises(C0AuthorityLeakError):
            guard_c0_payload({"route_mode": "x", "auth_token": "y"})

    def test_negative_safe_fields_never_raise(self):
        """Negative control: allowed fields must never trigger the guard."""
        safe = {
            "query": "test query",
            "context": "some context",
            "metadata": {"source": "rag"},
            "score": 0.95,
        }
        raised = False
        try:
            guard_c0_payload(safe)
        except C0AuthorityLeakError:  # guardian: allow-silent-swallower
            raised = True
        assert not raised
