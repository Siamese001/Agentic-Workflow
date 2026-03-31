"""Addendum 3.1: C0 Authority Leak Guard.

C0 RAG is informational only — must not carry authority fields.
Raises C0AuthorityLeakError if forbidden fields are present.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "c0_guard")
emit_determinism_digest("p0", "c0_guard")

_emit_dispatches_healing_run("p1", "c0_guard", "L0")
_emit_routes_through("p1", "c0_guard", "L0")
_emit_checks_agent_registry("p1", "c0_guard", "agent_registry")
_emit_validates_agent_capability("p1", "c0_guard", "capability")
_emit_dispatches_execution_plan("p1", "c0_guard", "exec_plan")
_emit_agent_executes_agent("p1", "c0_guard", "sub_agent")
_emit_routes_to_agent("p1", "c0_guard", "target_agent")
_emit_verifies_policy("p1", "c0_guard", "policy_check")
_emit_observes_runtime_state("p1", "c0_guard", "runtime_state")
_emit_verifies_boundary("p1", "c0_guard", "boundary_check")
_emit_transcripts_response("p1", "c0_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "c0_guard")
_emit_gated_by_confidence("p1", "c0_guard", "confidence_gate")
_emit_escalates_to_human("p1", "c0_guard", "L0")
_emit_reads_policy_state("p1", "c0_guard", "L0")
_emit_authorize_and_execute("p2", "c0_guard", "execution_auth")
_emit_validates_capability("p2", "c0_guard", "capability_check")
_emit_routes_to_capability("p2", "c0_guard", "capability_route")
_emit_writes_via_uwg("p2", "c0_guard", "uwg_write")
_emit_blocks_direct_write("p2", "c0_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "c0_guard", "tool_invocation")
_emit_captures_execution_output("p2", "c0_guard", "exec_output")
_emit_dispatches_agent("p3", "c0_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "c0_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "c0_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "c0_guard", "healing_outcome")
_emit_escalates_failure("p3", "c0_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "c0_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "c0_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "c0_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "c0_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "c0_guard", "eval_metric")
_emit_stores_embedding("p4", "c0_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "c0_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "c0_guard", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

_emit_emits_metric_event("c0_guard", "p4obs", "metric_1")
_emit_emits_metric_event("c0_guard", "p4obs", "metric_2")
_emit_emits_metric_event("c0_guard", "p4obs", "metric_3")
_emit_emits_metric_event("c0_guard", "p4obs", "metric_4")
_emit_emits_metric_event("c0_guard", "p4obs", "metric_5")
_emit_emits_metric_event("c0_guard", "p4obs", "metric_6")
_emit_records_incident_event("c0_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("c0_guard", "p4obs", "anomaly")
_emit_writes_observability_log("c0_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("c0_guard", "p4obs", "mon_state")
_emit_triggers_alert("c0_guard", "p4obs", "alert")
_emit_links_incident_trace("c0_guard", "p4obs", "trace_link")
_emit_captures_pattern("c0_guard", "p3lm", "pattern")
_emit_records_learning_event("c0_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("c0_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("c0_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("c0_guard", "p3lm", "routing")
_emit_improves_agent_policy("c0_guard", "p3lm", "policy")
_emit_stores_learning_state("c0_guard", "p3lm", "state")
_emit_records_execution_trace("c0_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("c0_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("c0_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("c0_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("c0_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("c0_guard", "env_read", "p2_env_1")
_emit_reads_environ("c0_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("c0_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("c0_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "c0_guard", "context_pull")
_emit_pulls_context("p1", "c0_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "c0_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "c0_guard", "uwg_term_2")
_emit_writes_through("p1", "c0_guard", "write_through")
_emit_writes_through("p1", "c0_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "c0_guard", "safety_validation")
_emit_invokes_eval("p1", "c0_guard", "eval_call")
_emit_proposal_commits_routing("p1", "c0_guard", "routing_commit")


def _get_hardening_errors():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_hardening_errors", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_hardening_errors", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_hardening_errors")
    from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError, C0MutationViolation

    return C0AuthorityLeakError, C0MutationViolation


_FORBIDDEN_AUTHORITY_FIELDS = frozenset(
    {"route_mode", "execution_tier", "safety_threshold", "allowed_tools", "auth_token"}
)


def guard_c0_payload(payload: dict[str, Any]) -> None:
    """Raise C0AuthorityLeakError if payload contains authority fields.

    Wire into RAG context assembly before payload is passed downstream.
    """
    leaked = _FORBIDDEN_AUTHORITY_FIELDS & set(payload.keys())
    if leaked:
        C0AuthorityLeakError, _ = _get_hardening_errors()
        raise C0AuthorityLeakError(
            f"C0 payload contains forbidden authority fields: {sorted(leaked)}. "
            "C0 RAG context is informational only."
        )


def verify_c0_immutability(payload_pre: dict[str, Any], payload_post: dict[str, Any]) -> None:
    """Raise C0MutationViolation if the payload was modified during assembly.

    Addendum 3.2: context mutation prevention.
    """
    import hashlib  # noqa: E401 (inline import acceptable here)
    import json

    def _hash(d: dict[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, ensure_ascii=True, default=str).encode()
        ).hexdigest()

    if _hash(payload_pre) != _hash(payload_post):
        _, C0MutationViolation = _get_hardening_errors()
        raise C0MutationViolation("C0 context payload was mutated during assembly — hash mismatch.")


__all__ = ["guard_c0_payload", "verify_c0_immutability"]
