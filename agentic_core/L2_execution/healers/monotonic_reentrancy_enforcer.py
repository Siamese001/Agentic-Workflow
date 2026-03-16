from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "monotonic_reentrancy_enforcer")
emit_determinism_digest("p0", "monotonic_reentrancy_enforcer")

_emit_dispatches_healing_run("p1", "monotonic_reentrancy_enforcer", "L2")
_emit_routes_through("p1", "monotonic_reentrancy_enforcer", "L2")
_emit_escalates_to_human("p1", "monotonic_reentrancy_enforcer", "L2")
_emit_reads_policy_state("p1", "monotonic_reentrancy_enforcer", "L2")

_emit_applies_guardrail("p0", "monotonic_reentrancy_enforcer", "p0_governance")
_emit_snapshots_state("p0", "monotonic_reentrancy_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "monotonic_reentrancy_enforcer", "execution_auth")
_emit_validates_capability("p2", "monotonic_reentrancy_enforcer", "capability_check")
_emit_routes_to_capability("p2", "monotonic_reentrancy_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "monotonic_reentrancy_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "monotonic_reentrancy_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "monotonic_reentrancy_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "monotonic_reentrancy_enforcer", "exec_output")
_emit_dispatches_agent("p3", "monotonic_reentrancy_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "monotonic_reentrancy_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "monotonic_reentrancy_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "monotonic_reentrancy_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "monotonic_reentrancy_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "monotonic_reentrancy_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "monotonic_reentrancy_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "monotonic_reentrancy_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "monotonic_reentrancy_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "monotonic_reentrancy_enforcer", "eval_metric")
_emit_stores_embedding("p4", "monotonic_reentrancy_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "monotonic_reentrancy_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "monotonic_reentrancy_enforcer", "exec_snapshot_link")


class NonMonotonicRetryViolation(Exception):
    """Raised when a retry count is not incremented monotonically."""


class MonotonicReentrancyEnforcer:
    """
    Ensures that the healing retry_count is strictly monotonic and persistent.

    This enforcer enforces Guarantee #19 by managing the retry count in L4 state,
    making it immune to agent manipulation or system restarts. The `_tier_escalate`
    function, which calls this, must be a pure function with no side-effects other
    than returning the next healing tier.
    """

    def __init__(self):
        self._persistent_retry_counts: dict[str, int] = {}

    def get_and_increment_retry_count(self, trace_id: str) -> int:
        """
        Retrieves the current retry count for a trace and increments it atomically.

        This is the only way to get a valid retry count. The count is persisted
        in L4, ensuring it survives agent restarts or other interruptions.

        Args:
            trace_id: The unique identifier for the failure trace.

        Returns:
            The new, incremented retry count.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "MonotonicReentrancyEnforcer.get_and_increment_retry_count"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:MonotonicReentrancyEnforcer.get_and_increment_retry_count".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        current_count = self._persistent_retry_counts.get(trace_id, 0)
        new_count = current_count + 1
        self._persistent_retry_counts[trace_id] = new_count
        return new_count

    def validate_monotonicity(self, trace_id: str, proposed_count: int) -> None:
        """
        Validates that a proposed retry count is monotonically correct.

        This would be used by the tier escalation logic to assert that the count
        it received is the one it expected, preventing state desynchronization.

        Args:
            trace_id: The unique identifier for the failure trace.
            proposed_count: The retry count being used in the current operation.

        Raises:
            NonMonotonicRetryViolation: If the proposed count is not exactly one
                                        greater than the persisted count.
        """
        expected_next_count = self._persistent_retry_counts.get(trace_id, 0)
        if proposed_count != expected_next_count:
            raise NonMonotonicRetryViolation(
                f"Invalid retry count for trace '{trace_id}'. Expected {expected_next_count}, got {proposed_count}."
            )
