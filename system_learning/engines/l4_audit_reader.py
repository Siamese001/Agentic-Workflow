"""L4 audit reader — read-only access to audit surfaces with authority guards.

System Learning has zero execution authority.  All reads from L4 audit
surfaces are validated through constitutional authority invariants before
the store is consulted.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

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
from system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    AuthorityViolation,  # re-exported for callers
    assert_read_only_audit_access,
    assert_zero_execution_authority,
)

_emit_records_execution_trace("p0", "evidence", "l4_audit_reader")
_emit_applies_guardrail("p0", "l4_audit_reader", "p0_governance")
_emit_reads_policy_state("p0", "l4_audit_reader", "policy_binding")
_emit_snapshots_state("p0", "l4_audit_reader", "state_snapshot")
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
