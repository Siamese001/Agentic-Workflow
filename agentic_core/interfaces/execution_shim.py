"""Execution interfaces - Stub implementation for test compatibility."""

from enum import Enum
from typing import Any


class ExecutionStatus(Enum):
    """Execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionContext:
    """Execution context."""

    def __init__(self, trace_id: str, request_id: str | None = None):
        self.trace_id = trace_id
        self.request_id = request_id
        self.status = ExecutionStatus.PENDING

    def update_status(self, status: ExecutionStatus) -> None:
        """Update execution status."""
        self.status = status


class ExecutionResult:
    """Execution result."""

    def __init__(self, success: bool, data: Any | None = None, error: str | None = None):
        self.success = success
        self.data = data
        self.error = error


__all__ = [
    "ExecutionContext",
    "ExecutionResult",
    "ExecutionStatus",
]
