"""Execution interfaces - Stub implementation for test compatibility."""

from dataclasses import dataclass
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


@dataclass(frozen=True)
class ExecutionCycle:
    """Execution lifecycle cycle record."""

    cid: str
    attempt: int = 1


class CIDRegistry:
    """In-memory registry that issues and tracks execution cycles by CID."""

    def __init__(self) -> None:
        self._attempts: dict[str, int] = {}

    def new_cycle(self, cid: str) -> ExecutionCycle:
        """Register a new attempt for *cid* and return its cycle record."""
        attempt = self._attempts.get(cid, 0) + 1
        self._attempts[cid] = attempt
        return ExecutionCycle(cid=cid, attempt=attempt)


__all__ = [
    "CIDRegistry",
    "ExecutionContext",
    "ExecutionCycle",
    "ExecutionResult",
    "ExecutionStatus",
]
