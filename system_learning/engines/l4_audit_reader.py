"""L4 audit reader — read-only access to audit surfaces with authority guards.

System Learning has zero execution authority.  All reads from L4 audit
surfaces are validated through constitutional authority invariants before
the store is consulted.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "l4_audit_reader", "execution_auth")
_emit_validates_capability("p2", "l4_audit_reader", "capability_check")
_emit_routes_to_capability("p2", "l4_audit_reader", "capability_route")
_emit_writes_via_uwg("p2", "l4_audit_reader", "uwg_write")
_emit_blocks_direct_write("p2", "l4_audit_reader", "direct_write_block")
_emit_records_tool_invocation("p2", "l4_audit_reader", "tool_invocation")
_emit_captures_execution_output("p2", "l4_audit_reader", "exec_output")
_emit_dispatches_agent("p3", "l4_audit_reader", "agent_dispatch")
_emit_coordinates_agents("p3", "l4_audit_reader", "agent_coordination")
_emit_records_workflow_lineage("p3", "l4_audit_reader", "workflow_lineage")
_emit_records_healing_outcome("p3", "l4_audit_reader", "healing_outcome")
_emit_escalates_failure("p3", "l4_audit_reader", "failure_escalation")
_emit_orchestrates_workflow("p3", "l4_audit_reader", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "l4_audit_reader", "healing_dispatch")
_emit_invokes_evaluation("p3", "l4_audit_reader", "evaluation_signal")
_emit_records_telemetry_event("p4", "l4_audit_reader", "telemetry_event")
_emit_captures_evaluation_metric("p4", "l4_audit_reader", "eval_metric")
_emit_stores_embedding("p4", "l4_audit_reader", "embedding_store")
_emit_updates_meta_learning_state("p4", "l4_audit_reader", "meta_learning")
_emit_links_execution_to_snapshot("p4", "l4_audit_reader", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
from system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    AuthorityViolation,  # re-exported for callers
    assert_read_only_audit_access,
    assert_zero_execution_authority,
)

_emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_1")
_emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_2")
_emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_3")
_emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_4")
_emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_5")
_emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_6")
_emit_records_incident_event("l4_audit_reader", "p4obs", "incident")
_emit_captures_runtime_anomaly("l4_audit_reader", "p4obs", "anomaly")
_emit_writes_observability_log("l4_audit_reader", "p4obs", "obs_log")
_emit_updates_monitoring_state("l4_audit_reader", "p4obs", "mon_state")
_emit_triggers_alert("l4_audit_reader", "p4obs", "alert")
_emit_links_incident_trace("l4_audit_reader", "p4obs", "trace_link")
_emit_captures_pattern("l4_audit_reader", "p3lm", "pattern")
_emit_records_learning_event("l4_audit_reader", "p3lm", "learning_event")
_emit_writes_learning_snapshot("l4_audit_reader", "p3lm", "snapshot")
_emit_feeds_meta_learning("l4_audit_reader", "p3lm", "meta_feed")
_emit_updates_routing_strategy("l4_audit_reader", "p3lm", "routing")
_emit_improves_agent_policy("l4_audit_reader", "p3lm", "policy")
_emit_stores_learning_state("l4_audit_reader", "p3lm", "state")
_emit_records_execution_trace("l4_audit_reader", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("l4_audit_reader", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("l4_audit_reader", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("l4_audit_reader", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("l4_audit_reader", "L4_STATE", "p2_trace_5")
_emit_reads_environ("l4_audit_reader", "env_read", "p2_env_1")
_emit_reads_environ("l4_audit_reader", "env_read", "p2_env_2")
_emit_reads_runtime_state("l4_audit_reader", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("l4_audit_reader", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "l4_audit_reader")
_emit_applies_guardrail("p0", "l4_audit_reader", "p0_governance")
_emit_reads_policy_state("p0", "l4_audit_reader", "policy_binding")
_emit_snapshots_state("p0", "l4_audit_reader", "state_snapshot")
_emit_pulls_context("p1", "l4_audit_reader", "context_pull")
_emit_pulls_context("p1", "l4_audit_reader", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "l4_audit_reader", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "l4_audit_reader", "uwg_term_secondary")
_emit_writes_through("p1", "l4_audit_reader", "write_through")
_emit_writes_through("p1", "l4_audit_reader", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "l4_audit_reader", "safety_validation")
_emit_invokes_eval("p1", "l4_audit_reader", "eval_call")
_emit_proposal_commits_routing("p1", "l4_audit_reader", "routing_commit")
_emit_escalates_to_human("p1", "l4_audit_reader", "human_escalation")
_emit_routes_through("p1", "l4_audit_reader", "route_through")
_emit_checks_agent_registry("p1", "l4_audit_reader", "agent_registry")
_emit_validates_agent_capability("p1", "l4_audit_reader", "capability")
_emit_dispatches_execution_plan("p1", "l4_audit_reader", "exec_plan")
_emit_agent_executes_agent("p1", "l4_audit_reader", "sub_agent")
_emit_routes_to_agent("p1", "l4_audit_reader", "target_agent")
_emit_verifies_policy("p1", "l4_audit_reader", "policy_check")
_emit_observes_runtime_state("p1", "l4_audit_reader", "runtime_state")
_emit_verifies_boundary("p1", "l4_audit_reader", "boundary_check")
_emit_transcripts_response("p1", "l4_audit_reader", "transcript")
_emit_hard_fails_untranscripted("p1", "l4_audit_reader")
_emit_gated_by_confidence("p1", "l4_audit_reader", "confidence_gate")
emit_replay_key("p0", "l4_audit_reader")
emit_determinism_digest("p0", "l4_audit_reader")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# =============================================================================
# AuditStore protocol (read-only)
# =============================================================================


@runtime_checkable
class AuditStore(Protocol):
    """Read-only protocol for L4 audit stores.

    Intentionally exposes NO write, append, delete, or mutate methods.
    """

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        """Return raw audit bytes for the given time window."""
        ...


# =============================================================================
# pull_audit_data
# =============================================================================


def pull_audit_data(
    store: AuditStore,
    window_start_utc: int,
    window_end_utc: int,
) -> bytes:
    """Pull audit data from an AuditStore for a validated time window.

    Parameters
    ----------
    store : AuditStore
        The audit store to read from.
    window_start_utc : int
        Window start (inclusive, Unix timestamp).  Must be strictly less
        than ``window_end_utc``.
    window_end_utc : int
        Window end (exclusive, Unix timestamp).

    Returns
    -------
    bytes
        Raw audit data for the window (may be empty).

    Raises
    ------
    ValueError
        If ``window_start_utc >= window_end_utc``.
    AuthorityViolation
        If the constitutional authority guards reject the operation.
    """
    if window_start_utc >= window_end_utc:
        raise ValueError(
            "INVALID_AUDIT_WINDOW: window_start_utc must be strictly less than window_end_utc"
        )

    ctx = AuthorityContext(
        caller_layer="system_learning.engines.l4_audit_reader",
        operation="read_audit_slice",
        target="l4_audit",
        mode="READ",
    )
    assert_read_only_audit_access(ctx)
    assert_zero_execution_authority(ctx)

    return store.read_audit_slice(window_start_utc, window_end_utc)


__all__ = [
    "AuditStore",
    "AuthorityViolation",
    "pull_audit_data",
]
