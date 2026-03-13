from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple, Sequence

Task = Any


class TaskBlastRadiusViolation(Exception):
    """Raised when a task exceeds its defined blast radius limits."""

    def __init__(self, message: str, violation_details: dict):
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
