"""Addendum 3.1: C0 Authority Leak Guard.

C0 RAG is informational only — must not carry authority fields.
Raises C0AuthorityLeakError if forbidden fields are present.
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

from agentic_core.runtime.lifecycle_trace_contract import (
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
