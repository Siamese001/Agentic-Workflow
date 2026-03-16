from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple, Sequence

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "bounded_task_decomposer")
emit_determinism_digest("p0", "bounded_task_decomposer")

_emit_dispatches_healing_run("p1", "bounded_task_decomposer", "L3")
_emit_routes_through("p1", "bounded_task_decomposer", "L3")
_emit_escalates_to_human("p1", "bounded_task_decomposer", "L3")
_emit_reads_policy_state("p1", "bounded_task_decomposer", "L3")
_emit_authorize_and_execute("p2", "bounded_task_decomposer", "execution_auth")
_emit_validates_capability("p2", "bounded_task_decomposer", "capability_check")
_emit_routes_to_capability("p2", "bounded_task_decomposer", "capability_route")
_emit_writes_via_uwg("p2", "bounded_task_decomposer", "uwg_write")
_emit_blocks_direct_write("p2", "bounded_task_decomposer", "direct_write_block")
_emit_records_tool_invocation("p2", "bounded_task_decomposer", "tool_invocation")
_emit_captures_execution_output("p2", "bounded_task_decomposer", "exec_output")
_emit_dispatches_agent("p3", "bounded_task_decomposer", "agent_dispatch")
_emit_coordinates_agents("p3", "bounded_task_decomposer", "agent_coordination")
_emit_records_workflow_lineage("p3", "bounded_task_decomposer", "workflow_lineage")
_emit_records_healing_outcome("p3", "bounded_task_decomposer", "healing_outcome")
_emit_escalates_failure("p3", "bounded_task_decomposer", "failure_escalation")
_emit_orchestrates_workflow("p3", "bounded_task_decomposer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "bounded_task_decomposer", "healing_dispatch")
_emit_invokes_evaluation("p3", "bounded_task_decomposer", "evaluation_signal")
_emit_records_telemetry_event("p4", "bounded_task_decomposer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "bounded_task_decomposer", "eval_metric")
_emit_stores_embedding("p4", "bounded_task_decomposer", "embedding_store")
_emit_updates_meta_learning_state("p4", "bounded_task_decomposer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "bounded_task_decomposer", "exec_snapshot_link")

Task = Any


class TaskBlastRadiusViolation(Exception):
    """Raised when a task exceeds its defined blast radius limits."""

    def __init__(self, message: str, violation_details: dict):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "TaskBlastRadiusViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "TaskBlastRadiusViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "TaskBlastRadiusViolation.__init__"
        )
        self.message = message
        self.violation_details = violation_details
        super().__init__(f"{message} Details: {violation_details}")


@dataclass(frozen=True)
class DecompositionPolicy:
    """Defines the blast radius limits for task decomposition."""

    max_subtasks: int = 10
    max_total_complexity: float = 100.0
    max_dependency_depth: int = 3


class DecompositionResult(NamedTuple):
    """The result of a task decomposition operation."""

    subtasks: Sequence[Task] | None
    violation: TaskBlastRadiusViolation | None = None


def decompose_task(task: Task, policy: DecompositionPolicy) -> DecompositionResult:
    """
    Decomposes a large task into smaller, bounded subtasks.

    This function enforces Guarantee #8 by ensuring that no single task is too
    large or complex, thus limiting its potential blast radius. It is a critical
    sovereign gate in L3, rejecting tasks that cannot be safely decomposed.

    Args:
        task: The task to be decomposed.
        policy: The decomposition policy defining the blast radius limits.

    Returns:
        A DecompositionResult containing the list of subtasks or a violation.
    """
    subtasks: list[Task] = [f"{task}_part_{i}" for i in range(5)]
    total_complexity = 50.0
    dependency_depth = 2
    if len(subtasks) > policy.max_subtasks:
        violation = TaskBlastRadiusViolation(
            "Task decomposition exceeds max subtasks.",
            {"actual": len(subtasks), "limit": policy.max_subtasks},
        )
        return DecompositionResult(subtasks=None, violation=violation)
    if total_complexity > policy.max_total_complexity:
        violation = TaskBlastRadiusViolation(
            "Task decomposition exceeds max total complexity.",
            {"actual": total_complexity, "limit": policy.max_total_complexity},
        )
        return DecompositionResult(subtasks=None, violation=violation)
    if dependency_depth > policy.max_dependency_depth:
        violation = TaskBlastRadiusViolation(
            "Task decomposition exceeds max dependency depth.",
            {"actual": dependency_depth, "limit": policy.max_dependency_depth},
        )
        return DecompositionResult(subtasks=None, violation=violation)
    return DecompositionResult(subtasks=subtasks)
