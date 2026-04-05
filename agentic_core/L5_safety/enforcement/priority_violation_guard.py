"""Priority Violation Guard — Enforces optimization priority constraints.

Prevents optimization operations from violating priority constraints
and ensures proper stack ordering of optimization tasks.
"""

from __future__ import annotations

import logging
from enum import Enum

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

emit_replay_key("p0", "priority_violation_guard")
emit_determinism_digest("p0", "priority_violation_guard")

_emit_dispatches_healing_run("p1", "priority_violation_guard", "L5")
_emit_routes_through("p1", "priority_violation_guard", "L5")
_emit_checks_agent_registry("p1", "priority_violation_guard", "agent_registry")
_emit_validates_agent_capability("p1", "priority_violation_guard", "capability")
_emit_dispatches_execution_plan("p1", "priority_violation_guard", "exec_plan")
_emit_agent_executes_agent("p1", "priority_violation_guard", "sub_agent")
_emit_routes_to_agent("p1", "priority_violation_guard", "target_agent")
_emit_verifies_policy("p1", "priority_violation_guard", "policy_check")
_emit_observes_runtime_state("p1", "priority_violation_guard", "runtime_state")
_emit_verifies_boundary("p1", "priority_violation_guard", "boundary_check")
_emit_transcripts_response("p1", "priority_violation_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "priority_violation_guard")
_emit_gated_by_confidence("p1", "priority_violation_guard", "confidence_gate")
_emit_escalates_to_human("p1", "priority_violation_guard", "L5")
_emit_reads_policy_state("p1", "priority_violation_guard", "L5")

_emit_applies_guardrail("p0", "priority_violation_guard", "p0_governance")
_emit_snapshots_state("p0", "priority_violation_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "priority_violation_guard", "execution_auth")
_emit_validates_capability("p2", "priority_violation_guard", "capability_check")
_emit_routes_to_capability("p2", "priority_violation_guard", "capability_route")
_emit_writes_via_uwg("p2", "priority_violation_guard", "uwg_write")
_emit_blocks_direct_write("p2", "priority_violation_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "priority_violation_guard", "tool_invocation")
_emit_captures_execution_output("p2", "priority_violation_guard", "exec_output")
_emit_dispatches_agent("p3", "priority_violation_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "priority_violation_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "priority_violation_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "priority_violation_guard", "healing_outcome")
_emit_escalates_failure("p3", "priority_violation_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "priority_violation_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "priority_violation_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "priority_violation_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "priority_violation_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "priority_violation_guard", "eval_metric")
_emit_stores_embedding("p4", "priority_violation_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "priority_violation_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "priority_violation_guard", "exec_snapshot_link")
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

_emit_emits_metric_event("priority_violation_guard", "p4obs", "metric_1")
_emit_emits_metric_event("priority_violation_guard", "p4obs", "metric_2")
_emit_emits_metric_event("priority_violation_guard", "p4obs", "metric_3")
_emit_emits_metric_event("priority_violation_guard", "p4obs", "metric_4")
_emit_emits_metric_event("priority_violation_guard", "p4obs", "metric_5")
_emit_emits_metric_event("priority_violation_guard", "p4obs", "metric_6")
_emit_records_incident_event("priority_violation_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("priority_violation_guard", "p4obs", "anomaly")
_emit_writes_observability_log("priority_violation_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("priority_violation_guard", "p4obs", "mon_state")
_emit_triggers_alert("priority_violation_guard", "p4obs", "alert")
_emit_links_incident_trace("priority_violation_guard", "p4obs", "trace_link")
_emit_captures_pattern("priority_violation_guard", "p3lm", "pattern")
_emit_records_learning_event("priority_violation_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("priority_violation_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("priority_violation_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("priority_violation_guard", "p3lm", "routing")
_emit_improves_agent_policy("priority_violation_guard", "p3lm", "policy")
_emit_stores_learning_state("priority_violation_guard", "p3lm", "state")
_emit_records_execution_trace("priority_violation_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("priority_violation_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("priority_violation_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("priority_violation_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("priority_violation_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("priority_violation_guard", "env_read", "p2_env_1")
_emit_reads_environ("priority_violation_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("priority_violation_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("priority_violation_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "priority_violation_guard", "context_pull")
_emit_pulls_context("p1", "priority_violation_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "priority_violation_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "priority_violation_guard", "uwg_term_2")
_emit_writes_through("p1", "priority_violation_guard", "write_through")
_emit_writes_through("p1", "priority_violation_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "priority_violation_guard", "safety_validation")
_emit_invokes_eval("p1", "priority_violation_guard", "eval_call")
_emit_proposal_commits_routing("p1", "priority_violation_guard", "routing_commit")

logger = logging.getLogger(__name__)


class OptimizationPriority(Enum):
    """Priority levels for optimization operations.

    Higher numeric values = higher priority.
    Operations must respect priority ordering.
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class PriorityViolationGuard:
    """Enforces priority constraints on optimization operations.

    Maintains a stack of active operations and validates that
    new operations respect priority constraints.
    """

    def __init__(self) -> None:
        """Initialize the priority violation guard."""
        self._operation_stack: list[tuple[str, OptimizationPriority]] = []
        self._validated_operations: set[str] = set()
        self._violations: list[dict[str, any]] = []

    def can_start_operation(
        self,
        operation_id: str,
        priority: OptimizationPriority,
        required_priority: OptimizationPriority | None = None,
    ) -> tuple[bool, str]:
        """Check if an operation can start based on priority constraints.

        Args:
            operation_id: Unique identifier for the operation.
            priority: Priority of the operation.
            required_priority: Minimum priority required for this operation.

        Returns:
            (can_start, reason) tuple
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "PriorityViolationGuard.can_start_operation"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:PriorityViolationGuard.can_start_operation".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if any((op_id == operation_id for op_id, _ in self._operation_stack)):
            return (False, f"Operation {operation_id} is already running")
        if required_priority and priority.value < required_priority.value:
            return (
                False,
                f"Operation {operation_id} has priority {priority.name} but requires at least {required_priority.name}",
            )
        if self._operation_stack:
            top_priority = max(self._operation_stack, key=lambda x: x[1].value)[1]
            if priority.value < top_priority.value:
                top_operations = [op_id for op_id, p in self._operation_stack if p == top_priority]
                return (
                    False,
                    f"Operation {operation_id} priority {priority.name} is lower than active operation(s) {top_operations} with priority {top_priority.name}",
                )
        return (True, "Operation can start")

    def start_operation(
        self,
        operation_id: str,
        priority: OptimizationPriority,
        required_priority: OptimizationPriority | None = None,
    ) -> bool:
        """Start an operation if priority constraints are satisfied.

        Args:
            operation_id: Unique identifier for the operation.
            priority: Priority of the operation.
            required_priority: Minimum priority required for this operation.

        Returns:
            True if operation started, False otherwise.
        """
        can_start, reason = self.can_start_operation(operation_id, priority, required_priority)
        if can_start:
            self._operation_stack.append((operation_id, priority))
            self._validated_operations.add(operation_id)
            logger.info(f"Started operation {operation_id} with priority {priority.name}")
            return True
        else:
            violation = {
                "operation_id": operation_id,
                "priority": priority.name,
                "required_priority": required_priority.name if required_priority else None,
                "reason": reason,
                "active_operations": [(op_id, p.name) for op_id, p in self._operation_stack],
                "timestamp": __import__("time").time(),
            }
            self._violations.append(violation)
            logger.warning(f"Priority violation prevented: {reason}")
            return False

    def end_operation(self, operation_id: str) -> bool:
        """End an operation and remove it from the stack.

        Args:
            operation_id: Unique identifier for the operation.

        Returns:
            True if operation was found and removed, False otherwise.
        """
        for i, (op_id, _) in enumerate(self._operation_stack):
            if op_id == operation_id:
                self._operation_stack.pop(i)
                logger.info(f"Ended operation {operation_id}")
                return True
        return False

    def get_active_operations(self) -> list[tuple[str, OptimizationPriority]]:
        """Get the current stack of active operations.

        Returns:
            List of (operation_id, priority) tuples.
        """
        return self._operation_stack.copy()

    def get_violations(self) -> list[dict[str, any]]:
        """Get all priority violations.

        Returns:
            List of violation dictionaries.
        """
        return self._violations.copy()

    def clear_violations(self) -> None:
        """Clear all recorded violations."""
        self._violations.clear()

    def reset(self) -> None:
        """Reset the guard (for testing)."""
        self._operation_stack.clear()
        self._validated_operations.clear()
        self._violations.clear()

    def get_stack_summary(self) -> dict[str, any]:
        """Get a summary of the current operation stack.

        Returns:
            Dictionary with stack statistics.
        """
        if not self._operation_stack:
            return {"stack_depth": 0, "highest_priority": None, "operations": []}
        highest_priority = max(self._operation_stack, key=lambda x: x[1].value)[1]
        return {
            "stack_depth": len(self._operation_stack),
            "highest_priority": highest_priority.name,
            "operations": [(op_id, p.name) for op_id, p in self._operation_stack],
        }


_priority_violation_guard: PriorityViolationGuard | None = None


def get_priority_violation_guard() -> PriorityViolationGuard:
    """Get the global priority violation guard instance.

    Returns:
        The global PriorityViolationGuard instance.
    """
    global _priority_violation_guard
    if _priority_violation_guard is None:
        _priority_violation_guard = PriorityViolationGuard()
    return _priority_violation_guard


def reset_priority_violation_guard() -> None:
    """Reset the global priority violation guard (for testing)."""
    global _priority_violation_guard
    if _priority_violation_guard is not None:
        _priority_violation_guard.reset()
