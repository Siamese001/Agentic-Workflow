"""Priority Violation Guard — Enforces optimization priority constraints.

Prevents optimization operations from violating priority constraints
and ensures proper stack ordering of optimization tasks.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, List, Optional, Set

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        # Stack of active operations with their priorities
        self._operation_stack: List[tuple[str, OptimizationPriority]] = []
        # Set of operations that have been validated
        self._validated_operations: Set[str] = set()
        # Registry of priority violations
        self._violations: List[Dict[str, any]] = []

    def can_start_operation(
        self,
        operation_id: str,
        priority: OptimizationPriority,
        required_priority: Optional[OptimizationPriority] = None,
    ) -> tuple[bool, str]:
        """Check if an operation can start based on priority constraints.

        Args:
            operation_id: Unique identifier for the operation.
            priority: Priority of the operation.
            required_priority: Minimum priority required for this operation.

        Returns:
            (can_start, reason) tuple
        """
        # Check if operation is already running
        if any(op_id == operation_id for op_id, _ in self._operation_stack):
            return False, f"Operation {operation_id} is already running"

        # Check required priority
        if required_priority and priority.value < required_priority.value:
            return False, (
                f"Operation {operation_id} has priority {priority.name} "
                f"but requires at least {required_priority.name}"
            )

        # Check stack priority constraints
        if self._operation_stack:
            # Get the highest priority operation on the stack
            top_priority = max(self._operation_stack, key=lambda x: x[1].value)[1]

            # New operation must have equal or higher priority
            if priority.value < top_priority.value:
                top_operations = [op_id for op_id, p in self._operation_stack if p == top_priority]
                return False, (
                    f"Operation {operation_id} priority {priority.name} is lower than "
                    f"active operation(s) {top_operations} with priority {top_priority.name}"
                )

        return True, "Operation can start"

    def start_operation(
        self,
        operation_id: str,
        priority: OptimizationPriority,
        required_priority: Optional[OptimizationPriority] = None,
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

    def get_active_operations(self) -> List[tuple[str, OptimizationPriority]]:
        """Get the current stack of active operations.

        Returns:
            List of (operation_id, priority) tuples.
        """
        return self._operation_stack.copy()

    def get_violations(self) -> List[Dict[str, any]]:
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

    def get_stack_summary(self) -> Dict[str, any]:
        """Get a summary of the current operation stack.

        Returns:
            Dictionary with stack statistics.
        """
        if not self._operation_stack:
            return {
                "stack_depth": 0,
                "highest_priority": None,
                "operations": [],
            }

        highest_priority = max(self._operation_stack, key=lambda x: x[1].value)[1]

        return {
            "stack_depth": len(self._operation_stack),
            "highest_priority": highest_priority.name,
            "operations": [(op_id, p.name) for op_id, p in self._operation_stack],
        }


# Global instance for system-wide priority enforcement
_priority_violation_guard: Optional[PriorityViolationGuard] = None


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
