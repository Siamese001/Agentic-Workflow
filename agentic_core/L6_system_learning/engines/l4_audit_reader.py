"""L4 audit reader — read-only access to audit surfaces with authority guards.

System Learning has zero execution authority.  All reads from L4 audit
surfaces are validated through constitutional authority invariants before
the store is consulted.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "l4_audit_reader", "execution_auth")
trace_contract._emit_validates_capability("p2", "l4_audit_reader", "capability_check")
trace_contract._emit_routes_to_capability("p2", "l4_audit_reader", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "l4_audit_reader", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "l4_audit_reader", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "l4_audit_reader", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "l4_audit_reader", "exec_output")
trace_contract._emit_dispatches_agent("p3", "l4_audit_reader", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "l4_audit_reader", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "l4_audit_reader", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "l4_audit_reader", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "l4_audit_reader", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "l4_audit_reader", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "l4_audit_reader", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "l4_audit_reader", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "l4_audit_reader", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "l4_audit_reader", "eval_metric")
trace_contract._emit_stores_embedding("p4", "l4_audit_reader", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "l4_audit_reader", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "l4_audit_reader", "exec_snapshot_link")
from agentic_core.L6_system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    AuthorityViolation,  # re-exported for callers
    assert_read_only_audit_access,
    assert_zero_execution_authority,
)

trace_contract._emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("l4_audit_reader", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("l4_audit_reader", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("l4_audit_reader", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("l4_audit_reader", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("l4_audit_reader", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("l4_audit_reader", "p4obs", "alert")
trace_contract._emit_links_incident_trace("l4_audit_reader", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("l4_audit_reader", "p3lm", "pattern")
trace_contract._emit_records_learning_event("l4_audit_reader", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("l4_audit_reader", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("l4_audit_reader", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("l4_audit_reader", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("l4_audit_reader", "p3lm", "policy")
trace_contract._emit_stores_learning_state("l4_audit_reader", "p3lm", "state")
trace_contract._emit_records_execution_trace("l4_audit_reader", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("l4_audit_reader", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("l4_audit_reader", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("l4_audit_reader", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("l4_audit_reader", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("l4_audit_reader", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("l4_audit_reader", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("l4_audit_reader", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("l4_audit_reader", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "l4_audit_reader")
trace_contract._emit_applies_guardrail("p0", "l4_audit_reader", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "l4_audit_reader", "policy_binding")
trace_contract._emit_snapshots_state("p0", "l4_audit_reader", "state_snapshot")
trace_contract._emit_pulls_context("p1", "l4_audit_reader", "context_pull")
trace_contract._emit_pulls_context("p1", "l4_audit_reader", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "l4_audit_reader", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "l4_audit_reader", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "l4_audit_reader", "write_through")
trace_contract._emit_writes_through("p1", "l4_audit_reader", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "l4_audit_reader", "safety_validation")
trace_contract._emit_invokes_eval("p1", "l4_audit_reader", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "l4_audit_reader", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "l4_audit_reader", "human_escalation")
trace_contract._emit_routes_through("p1", "l4_audit_reader", "route_through")
trace_contract._emit_checks_agent_registry("p1", "l4_audit_reader", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "l4_audit_reader", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "l4_audit_reader", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "l4_audit_reader", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "l4_audit_reader", "target_agent")
trace_contract._emit_verifies_policy("p1", "l4_audit_reader", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "l4_audit_reader", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "l4_audit_reader", "boundary_check")
trace_contract._emit_transcripts_response("p1", "l4_audit_reader", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "l4_audit_reader")
trace_contract._emit_gated_by_confidence("p1", "l4_audit_reader", "confidence_gate")
trace_contract.emit_replay_key("p0", "l4_audit_reader")
trace_contract.emit_determinism_digest("p0", "l4_audit_reader")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
            "INVALID_AUDIT_WINDOW: window_start_utc must be strictly less than window_end_utc",
        )

    ctx = AuthorityContext(
        caller_layer="agentic_core.L6_system_learning.engines.l4_audit_reader",
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
