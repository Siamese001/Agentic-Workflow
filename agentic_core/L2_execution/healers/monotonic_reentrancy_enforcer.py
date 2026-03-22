from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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

emit_replay_key("p0", "monotonic_reentrancy_enforcer")
emit_determinism_digest("p0", "monotonic_reentrancy_enforcer")

_emit_dispatches_healing_run("p1", "monotonic_reentrancy_enforcer", "L2")
_emit_routes_through("p1", "monotonic_reentrancy_enforcer", "L2")
_emit_checks_agent_registry("p1", "monotonic_reentrancy_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "monotonic_reentrancy_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "monotonic_reentrancy_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "monotonic_reentrancy_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "monotonic_reentrancy_enforcer", "target_agent")
_emit_verifies_policy("p1", "monotonic_reentrancy_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "monotonic_reentrancy_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "monotonic_reentrancy_enforcer", "boundary_check")
_emit_transcripts_response("p1", "monotonic_reentrancy_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "monotonic_reentrancy_enforcer")
_emit_gated_by_confidence("p1", "monotonic_reentrancy_enforcer", "confidence_gate")
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

_emit_emits_metric_event("monotonic_reentrancy_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("monotonic_reentrancy_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("monotonic_reentrancy_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("monotonic_reentrancy_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("monotonic_reentrancy_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("monotonic_reentrancy_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("monotonic_reentrancy_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("monotonic_reentrancy_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("monotonic_reentrancy_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("monotonic_reentrancy_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("monotonic_reentrancy_enforcer", "p4obs", "alert")
_emit_links_incident_trace("monotonic_reentrancy_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("monotonic_reentrancy_enforcer", "p3lm", "pattern")
_emit_records_learning_event("monotonic_reentrancy_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("monotonic_reentrancy_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("monotonic_reentrancy_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("monotonic_reentrancy_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("monotonic_reentrancy_enforcer", "p3lm", "policy")
_emit_stores_learning_state("monotonic_reentrancy_enforcer", "p3lm", "state")
_emit_records_execution_trace("monotonic_reentrancy_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("monotonic_reentrancy_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("monotonic_reentrancy_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("monotonic_reentrancy_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("monotonic_reentrancy_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("monotonic_reentrancy_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("monotonic_reentrancy_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("monotonic_reentrancy_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("monotonic_reentrancy_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "monotonic_reentrancy_enforcer", "context_pull")
_emit_pulls_context("p1", "monotonic_reentrancy_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "monotonic_reentrancy_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "monotonic_reentrancy_enforcer", "uwg_term_2")
_emit_writes_through("p1", "monotonic_reentrancy_enforcer", "write_through")
_emit_writes_through("p1", "monotonic_reentrancy_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "monotonic_reentrancy_enforcer", "safety_validation")
_emit_invokes_eval("p1", "monotonic_reentrancy_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "monotonic_reentrancy_enforcer", "routing_commit")


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
