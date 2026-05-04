"""Bulkhead Manager - Stub implementation for test compatibility."""

from enum import Enum
from typing import Any, Callable


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class BulkheadManager:
    """Stub bulkhead manager."""

    def __init__(self):
        self._bulkheads = {}
        self._metrics = {}

    async def create_bulkhead(
        self, name: str, max_concurrency: int, queue_size: int, priority: TaskPriority
    ) -> None:
        """Create a bulkhead."""
        self._bulkheads[name] = {
            "max_concurrency": max_concurrency,
            "queue_size": queue_size,
            "priority": priority,
        }
        self._metrics[name] = {"executed": 0, "rejected": 0}

    async def execute(
        self,
        func: Callable,
        *args,
        bulkhead_name: str = "default",
        priority: TaskPriority = TaskPriority.MEDIUM,
        **kwargs,
    ):
        """Execute function within bulkhead."""
        if bulkhead_name in self._metrics:
            self._metrics[bulkhead_name]["executed"] += 1
        return await func(*args, **kwargs)

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all bulkhead metrics."""
        return self._metrics.copy()


_bulkhead_manager: BulkheadManager | None = None


async def get_bulkhead_manager() -> BulkheadManager:
    """Get global bulkhead manager instance."""
    global _bulkhead_manager
    if _bulkhead_manager is None:
        _bulkhead_manager = BulkheadManager()
    return _bulkhead_manager


__all__ = ["BulkheadManager", "TaskPriority", "get_bulkhead_manager"]
