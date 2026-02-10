"""
BatchingMixin - Focused Batching and Async Pooling Functionality

Phase 3 MRO Refactoring: Extracted from PerformanceMixin for single responsibility.

Provides:
- Batch queue operations
- Async operation pooling with semaphore
- Lazy initialization registry
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")

Logger = logging.getLogger(__name__)


@dataclass
class BatchingConfig:
    """Configuration for batching operations."""

    batch_size: int = 100
    async_pool_size: int = 10
    max_batch_queues: int = 50
    max_batch_queue_size: int = 10000
    lazy_init_enabled: bool = True


class BatchingMixin:
    """
    Mixin providing batch operations and async pooling.

    Phase 3 MRO Refactoring: Single responsibility - batching only.

    Usage:
        class MyAgent(BatchingMixin, SovereignBaseAgent):
            async def process_items(self, items):
                for item in items:
                    self.batch_add("processing", item)
                    if self.should_flush_batch("processing"):
                        batch = self.batch_flush("processing")
                        await self.process_batch(batch)
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize batching state."""
        super().__init__(**kwargs)

        self._batching_config = BatchingConfig()
        self._batch_queues: dict[str, list] = {}
        self._lazy_registry: dict[str, Callable] = {}
        self._lazy_initialized: dict[str, Any] = {}
        self._batching_lock = threading.RLock()
        self._async_semaphore: asyncio.Semaphore | None = None
        self._batching_initialized = True

        Logger.debug(f"[BATCH] {self.__class__.__name__} batching initialized")

    def configure_batching(
        self,
        batch_size: int | None = None,
        async_pool_size: int | None = None,
        max_batch_queues: int | None = None,
        max_batch_queue_size: int | None = None,
        lazy_init_enabled: bool | None = None,
    ) -> None:
        """Configure batching settings."""
        if batch_size is not None and batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if async_pool_size is not None and async_pool_size <= 0:
            raise ValueError("async_pool_size must be positive")
        if max_batch_queues is not None and max_batch_queues <= 0:
            raise ValueError("max_batch_queues must be positive")
        if max_batch_queue_size is not None and max_batch_queue_size <= 0:
            raise ValueError("max_batch_queue_size must be positive")

        with self._batching_lock:
            if batch_size is not None:
                self._batching_config.batch_size = batch_size
            if async_pool_size is not None:
                self._batching_config.async_pool_size = async_pool_size
                self._async_semaphore = None  # Reset semaphore
            if max_batch_queues is not None:
                self._batching_config.max_batch_queues = max_batch_queues
            if max_batch_queue_size is not None:
                self._batching_config.max_batch_queue_size = max_batch_queue_size
            if lazy_init_enabled is not None:
                self._batching_config.lazy_init_enabled = lazy_init_enabled

    # =========================================================================
    # Batch Operations
    # =========================================================================

    def batch_add(self, queue_name: str, item: Any) -> int:
        """Add item to a batch queue. Returns current queue size."""
        with self._batching_lock:
            if (
                queue_name not in self._batch_queues
                and len(self._batch_queues) >= self._batching_config.max_batch_queues
            ):
                raise ValueError(f"Maximum batch queues ({self._batching_config.max_batch_queues}) exceeded")

            if queue_name not in self._batch_queues:
                self._batch_queues[queue_name] = []

            if len(self._batch_queues[queue_name]) >= self._batching_config.max_batch_queue_size:
                raise ValueError(
                    f"Batch queue '{queue_name}' size limit "
                    f"({self._batching_config.max_batch_queue_size}) exceeded",
                )

            self._batch_queues[queue_name].append(item)
            return len(self._batch_queues[queue_name])

    def batch_flush(self, queue_name: str) -> list:
        """Flush and return all items from a batch queue."""
        with self._batching_lock:
            return self._batch_queues.pop(queue_name, [])

    def batch_size(self, queue_name: str) -> int:
        """Get current size of a batch queue."""
        with self._batching_lock:
            return len(self._batch_queues.get(queue_name, []))

    def should_flush_batch(self, queue_name: str) -> bool:
        """Check if batch queue should be flushed."""
        return self.batch_size(queue_name) >= self._batching_config.batch_size

    def batch_clear_all(self) -> int:
        """Clear all batch queues. Returns count of queues cleared."""
        with self._batching_lock:
            count = len(self._batch_queues)
            self._batch_queues.clear()
            return count

    # =========================================================================
    # Lazy Initialization
    # =========================================================================

    def register_lazy(self, name: str, initializer: Callable[[], Any]) -> None:
        """Register a lazy-initialized resource."""
        self._lazy_registry[name] = initializer

    def get_lazy(self, name: str) -> Any:
        """Get a lazy-initialized resource."""
        if not self._batching_config.lazy_init_enabled:
            if name in self._lazy_registry:
                return self._lazy_registry[name]()
            raise KeyError(f"Lazy resource not registered: {name}")

        with self._batching_lock:
            if name in self._lazy_initialized:
                return self._lazy_initialized[name]

            if name not in self._lazy_registry:
                raise KeyError(f"Lazy resource not registered: {name}")

            resource = self._lazy_registry[name]()
            self._lazy_initialized[name] = resource
            Logger.debug(f"[BATCH] Lazy initialized: {name}")
            return resource

    def is_lazy_initialized(self, name: str) -> bool:
        """Check if a lazy resource has been initialized."""
        return name in self._lazy_initialized

    # =========================================================================
    # Async Pooling
    # =========================================================================

    async def get_async_semaphore(self) -> asyncio.Semaphore:
        """Get or create async semaphore for pooling."""
        if self._async_semaphore is None:
            self._async_semaphore = asyncio.Semaphore(self._batching_config.async_pool_size)
        return self._async_semaphore

    async def run_pooled(self, coro) -> Any:
        """Run a coroutine with pool limiting."""
        semaphore = await self.get_async_semaphore()
        async with semaphore:
            return await coro

    # =========================================================================
    # Parallel Batch Execution (merged from batch_operation_mixin.py)
    # =========================================================================

    async def execute_batch(
        self,
        tasks: Iterable[Awaitable[T]],
        *,
        concurrency: int = 10,
        timeout: float | None = None,
        return_exceptions: bool = False,
    ) -> list[T]:
        """Execute awaitables with bounded concurrency via asyncio.TaskGroup.

        Args:
            tasks: Iterable of awaitables to execute.
            concurrency: Max concurrent tasks (semaphore limit).
            timeout: Overall timeout in seconds (None = no limit).
            return_exceptions: If True, exceptions are returned in the
                result list instead of being raised.

        Returns:
            Ordered list of results matching the input task order.
        """
        task_list = list(tasks)
        if not task_list:
            return []

        semaphore = asyncio.Semaphore(concurrency)
        results: list[Any] = [None] * len(task_list)

        async def _run(index: int, awaitable: Awaitable[T]) -> None:
            async with semaphore:
                results[index] = await awaitable

        async def _run_safe(index: int, awaitable: Awaitable[T]) -> None:
            async with semaphore:
                try:
                    results[index] = await awaitable
                except Exception as exc:
                    results[index] = exc

        runner = _run_safe if return_exceptions else _run

        async def _execute() -> None:
            async with asyncio.TaskGroup() as tg:
                for i, aw in enumerate(task_list):
                    tg.create_task(runner(i, aw))

        if timeout is not None:
            await asyncio.wait_for(_execute(), timeout=timeout)
        else:
            await _execute()

        return results

    async def batch_execute(
        self,
        tasks: list,
        max_workers: int = 5,
        sequential: bool = False,
    ) -> list[Any]:
        """Backwards-compat alias for legacy batch_operation_mixin callers.

        Prefer ``execute_batch`` for new code.
        """
        if sequential:
            results = []
            for task in tasks:
                try:
                    results.append(await task)
                except Exception as e:
                    results.append(e)
            return results

        return await self.execute_batch(
            tasks,
            concurrency=max_workers,
            timeout=120.0,
            return_exceptions=True,
        )

    # =========================================================================
    # Status
    # =========================================================================

    def get_batching_status(self) -> dict[str, Any]:
        """Get batching status."""
        with self._batching_lock:
            return {
                "batch_queues": {name: len(items) for name, items in self._batch_queues.items()},
                "lazy_registered": len(self._lazy_registry),
                "lazy_initialized": len(self._lazy_initialized),
                "config": {
                    "batch_size": self._batching_config.batch_size,
                    "async_pool_size": self._batching_config.async_pool_size,
                    "max_batch_queues": self._batching_config.max_batch_queues,
                },
            }


__all__ = ["BatchingMixin", "BatchingConfig"]
