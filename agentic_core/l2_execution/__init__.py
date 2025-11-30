"""L2 Execution Layer - Task Execution and Coordination

This layer provides execution capabilities for both resume and outreach workflows.
Re-exports robust implementations from the engine modules to maintain architectural compliance.
"""

from __future__ import annotations

from .l2_execution import (
    ExecutionEngine,
    Task,
    ExecutionContext,
    ExecutionStatus,
    ExecutionPlan,
    ExecutionResult,
    get_execution_engine,
)

__all__ = [
    "ExecutionEngine",
    "Task",
    "ExecutionContext",
    "ExecutionStatus",
    "ExecutionPlan",
    "ExecutionResult",
    "get_execution_engine",
]
