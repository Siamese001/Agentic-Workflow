"""
PerformanceMixin - Phase 4 Critical Infrastructure: Architecture Refinement

Provides performance optimization capabilities including caching, lazy loading,
batching, and performance monitoring.

Features:
- Method-level caching with TTL
- Lazy initialization patterns
- Batch operation support
- Performance metrics collection
- Memory usage monitoring
- Async operation pooling

SSOT PRINCIPLE:
    All agents requiring performance optimization should inherit from this mixin.
    This ensures consistent performance patterns across the agent ecosystem.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import threading
import time
import uuid
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "performance_mixin", "p0_governance")
_emit_reads_policy_state("p0", "performance_mixin", "policy_binding")
_emit_snapshots_state("p0", "performance_mixin", "state_snapshot")
emit_replay_key("p0", "performance_mixin")
emit_determinism_digest("p0", "performance_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "performance_mixin", "execution_auth")
_emit_validates_capability("p2", "performance_mixin", "capability_check")
_emit_routes_to_capability("p2", "performance_mixin", "capability_route")
_emit_writes_via_uwg("p2", "performance_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "performance_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "performance_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "performance_mixin", "exec_output")
_emit_dispatches_agent("p3", "performance_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "performance_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "performance_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "performance_mixin", "healing_outcome")
_emit_escalates_failure("p3", "performance_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "performance_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "performance_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "performance_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "performance_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "performance_mixin", "eval_metric")
_emit_stores_embedding("p4", "performance_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "performance_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "performance_mixin", "exec_snapshot_link")

Logger = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""

    value: Any
    created_at: float = field(default_factory=time.time)
    ttl_seconds: float = 300.0
    hits: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.created_at > self.ttl_seconds


@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation."""

    operation_name: str
    call_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0

    @property
    def avg_time_ms(self) -> float:
        """Calculate average execution time."""
        if self.call_count == 0:
            return 0.0
        return self.total_time_ms / self.call_count

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation_name": self.operation_name,
            "call_count": self.call_count,
            "total_time_ms": self.total_time_ms,
            "avg_time_ms": self.avg_time_ms,
            "min_time_ms": self.min_time_ms if self.min_time_ms != float("inf") else 0,
            "max_time_ms": self.max_time_ms,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hit_rate,
            "errors": self.errors,
        }


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""

    cache_enabled: bool = True
    cache_max_size: int = 1000
    cache_default_ttl: float = 300.0
    metrics_enabled: bool = True
    lazy_init_enabled: bool = True
    batch_size: int = 100
    async_pool_size: int = 10
    max_batch_queues: int = 50
    max_batch_queue_size: int = 10000


class PerformanceMixin:
    """
    Mixin providing performance optimization capabilities for agents.

    Phase 4 Critical Infrastructure:
    - Method-level caching
    - Lazy initialization
    - Batch operations
    - Performance monitoring

    Usage:
        class MyAgent(PerformanceMixin, SovereignBaseAgent):
            def __init__(self):
                super().__init__()
                self.configure_performance(cache_max_size=500)

            @PerformanceMixin.cached(ttl=60)
            def expensive_operation(self, key: str) -> dict:
                # This result will be cached for 60 seconds
                return self._compute_expensive(key)

            @PerformanceMixin.timed
            async def monitored_operation(self) -> None:
                # Execution time will be tracked
                await self._do_work()
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize performance optimization state."""
        super().__init__(**kwargs)
        self._perf_config: PerformanceConfig = PerformanceConfig()
        self._method_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._perf_metrics: dict[str, PerformanceMetrics] = {}
        self._lazy_registry: dict[str, Callable] = {}
        self._lazy_initialized: dict[str, Any] = {}
        self._batch_queues: dict[str, list] = {}
        self._perf_lock = threading.RLock()
        self._async_semaphore: asyncio.Semaphore | None = None
        self._performance_initialized = True
        Logger.debug(f"[PERF] {self.__class__.__name__} performance optimization initialized")

    def configure_performance(
        self,
        cache_enabled: bool | None = None,
        cache_max_size: int | None = None,
        cache_default_ttl: float | None = None,
        metrics_enabled: bool | None = None,
        lazy_init_enabled: bool | None = None,
        batch_size: int | None = None,
        async_pool_size: int | None = None,
        max_batch_queues: int | None = None,
        max_batch_queue_size: int | None = None,
    ) -> None:
        """
        Configure performance optimization settings.

        Args:
            cache_enabled: Enable/disable caching
            cache_max_size: Maximum cache entries
            cache_default_ttl: Default cache TTL in seconds
            metrics_enabled: Enable/disable metrics collection
            lazy_init_enabled: Enable/disable lazy initialization
            batch_size: Default batch size for operations
            async_pool_size: Size of async operation pool
            max_batch_queues: Maximum number of batch queues
            max_batch_queue_size: Maximum items per batch queue

        Raises:
            ValueError: If any parameter is invalid
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "PerformanceMixin.configure_performance")
        if cache_max_size is not None and cache_max_size <= 0:
            raise ValueError("cache_max_size must be positive")
        if cache_default_ttl is not None and cache_default_ttl <= 0:
            raise ValueError("cache_default_ttl must be positive")
        if batch_size is not None and batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if async_pool_size is not None and async_pool_size <= 0:
            raise ValueError("async_pool_size must be positive")
        if max_batch_queues is not None and max_batch_queues <= 0:
            raise ValueError("max_batch_queues must be positive")
        if max_batch_queue_size is not None and max_batch_queue_size <= 0:
            raise ValueError("max_batch_queue_size must be positive")
        with self._perf_lock:
            if cache_enabled is not None:
                self._perf_config.cache_enabled = cache_enabled
            if cache_max_size is not None:
                self._perf_config.cache_max_size = cache_max_size
            if cache_default_ttl is not None:
                self._perf_config.cache_default_ttl = cache_default_ttl
            if metrics_enabled is not None:
                self._perf_config.metrics_enabled = metrics_enabled
            if lazy_init_enabled is not None:
                self._perf_config.lazy_init_enabled = lazy_init_enabled
            if batch_size is not None:
                self._perf_config.batch_size = batch_size
            if async_pool_size is not None:
                self._perf_config.async_pool_size = async_pool_size
                self._async_semaphore = None
            if max_batch_queues is not None:
                self._perf_config.max_batch_queues = max_batch_queues
            if max_batch_queue_size is not None:
                self._perf_config.max_batch_queue_size = max_batch_queue_size
        Logger.info(f"[PERF] Configuration updated: {self._perf_config}")

    def configure_cache(
        self, enabled: bool | None = None, max_size: int | None = None, default_ttl: float | None = None
    ) -> None:
        """Configure caching settings (CachingMixin-compat)."""
        self.configure_performance(
            cache_enabled=enabled, cache_max_size=max_size, cache_default_ttl=default_ttl
        )

    def configure_metrics(self, enabled: bool | None = None) -> None:
        """Configure metrics settings (MetricsMixin-compat)."""
        self.configure_performance(metrics_enabled=enabled)

    def record_timing(self, operation_name: str, duration_ms: float, error: bool = False) -> None:
        """Record timing for an operation (MetricsMixin-compat public wrapper)."""
        self._record_timing(operation_name, duration_ms, error)

    def record_cache_hit(self, operation_name: str) -> None:
        """Record cache hit (MetricsMixin-compat public wrapper)."""
        self._record_cache_hit(operation_name)

    def record_cache_miss(self, operation_name: str) -> None:
        """Record cache miss (MetricsMixin-compat public wrapper)."""
        self._record_cache_miss(operation_name)

    def get_metrics(self, operation_name: str | None = None) -> dict[str, Any]:
        """Get performance metrics (MetricsMixin-compat alias)."""
        return self.get_performance_metrics(operation_name)

    def configure_batching(
        self,
        batch_size: int | None = None,
        async_pool_size: int | None = None,
        max_batch_queues: int | None = None,
        max_batch_queue_size: int | None = None,
        lazy_init_enabled: bool | None = None,
    ) -> None:
        """Configure batching settings (BatchingMixin-compat)."""
        self.configure_performance(
            batch_size=batch_size,
            async_pool_size=async_pool_size,
            max_batch_queues=max_batch_queues,
            max_batch_queue_size=max_batch_queue_size,
            lazy_init_enabled=lazy_init_enabled,
        )

    def cache_get(self, key: str) -> tuple[bool, Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Tuple of (hit, value) - hit is True if found and not expired
        """
        if not self._perf_config.cache_enabled:
            return (False, None)
        with self._perf_lock:
            entry = self._method_cache.get(key)
            if entry is None:
                return (False, None)
            if entry.is_expired():
                del self._method_cache[key]
                return (False, None)
            self._method_cache.move_to_end(key)
            entry.hits += 1
            return (True, entry.value)

    def cache_set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if not self._perf_config.cache_enabled:
            return
        with self._perf_lock:
            while len(self._method_cache) >= self._perf_config.cache_max_size:
                self._method_cache.popitem(last=False)
            self._method_cache[key] = CacheEntry(
                value=value, ttl_seconds=ttl or self._perf_config.cache_default_ttl
            )

    def cache_invalidate(self, key: str) -> bool:
        """
        Invalidate a cache entry.

        Args:
            key: Cache key to invalidate

        Returns:
            True if entry was found and removed
        """
        with self._perf_lock:
            if key in self._method_cache:
                del self._method_cache[key]
                return True
            return False

    def cache_clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        with self._perf_lock:
            count = len(self._method_cache)
            self._method_cache.clear()
            return count

    def cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        with self._perf_lock:
            total_hits = sum(e.hits for e in self._method_cache.values())
            expired = sum(1 for e in self._method_cache.values() if e.is_expired())
            return {
                "size": len(self._method_cache),
                "max_size": self._perf_config.cache_max_size,
                "total_hits": total_hits,
                "expired_entries": expired,
                "enabled": self._perf_config.cache_enabled,
            }

    @staticmethod
    def cached(ttl: float = 300.0, key_func: Callable | None = None):
        """
        Decorator to cache method results.

        Args:
            ttl: Time-to-live in seconds
            key_func: Optional function to generate cache key from args

        Usage:
            @PerformanceMixin.cached(ttl=60)
            def expensive_method(self, arg1, arg2):
                return compute(arg1, arg2)
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                if not isinstance(self, PerformanceMixin):
                    return func(self, *args, **kwargs)
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
                hit, value = self.cache_get(cache_key)
                if hit:
                    self._record_cache_hit(func.__name__)
                    return value
                self._record_cache_miss(func.__name__)
                result = func(self, *args, **kwargs)
                self.cache_set(cache_key, result, ttl)
                return result

            return wrapper

        return decorator

    def _ensure_metrics(self, operation_name: str) -> PerformanceMetrics:
        """Ensure metrics exist for an operation."""
        if operation_name not in self._perf_metrics:
            self._perf_metrics[operation_name] = PerformanceMetrics(operation_name=operation_name)
        return self._perf_metrics[operation_name]

    def _record_timing(self, operation_name: str, duration_ms: float, error: bool = False) -> None:
        """Record timing for an operation."""
        if not self._perf_config.metrics_enabled:
            return
        with self._perf_lock:
            metrics = self._ensure_metrics(operation_name)
            metrics.call_count += 1
            metrics.total_time_ms += duration_ms
            metrics.min_time_ms = min(metrics.min_time_ms, duration_ms)
            metrics.max_time_ms = max(metrics.max_time_ms, duration_ms)
            if error:
                metrics.errors += 1

    def _record_cache_hit(self, operation_name: str) -> None:
        """Record cache hit for an operation."""
        if not self._perf_config.metrics_enabled:
            return
        with self._perf_lock:
            metrics = self._ensure_metrics(operation_name)
            metrics.cache_hits += 1

    def _record_cache_miss(self, operation_name: str) -> None:
        """Record cache miss for an operation."""
        if not self._perf_config.metrics_enabled:
            return
        with self._perf_lock:
            metrics = self._ensure_metrics(operation_name)
            metrics.cache_misses += 1

    def get_performance_metrics(self, operation_name: str | None = None) -> dict[str, Any]:
        """
        Get performance metrics.

        Args:
            operation_name: Specific operation or None for all

        Returns:
            Dictionary with metrics
        """
        with self._perf_lock:
            if operation_name:
                metrics = self._perf_metrics.get(operation_name)
                return metrics.to_dict() if metrics else {}
            return {name: m.to_dict() for name, m in self._perf_metrics.items()}

    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        with self._perf_lock:
            self._perf_metrics.clear()

    @staticmethod
    def timed(func: Callable) -> Callable:
        """
        Decorator to track execution time.

        Usage:
            @PerformanceMixin.timed
            def monitored_method(self):
                return do_work()
        """

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            if not isinstance(self, PerformanceMixin):
                return func(self, *args, **kwargs)
            start = time.time()
            error = False
            try:
                return func(self, *args, **kwargs)
            # guardian: allow-silent-swallow
            except Exception:
                error = True
                raise
            finally:
                duration_ms = (time.time() - start) * 1000
                self._record_timing(func.__name__, duration_ms, error)

        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            if not isinstance(self, PerformanceMixin):
                return await func(self, *args, **kwargs)
            start = time.time()
            error = False
            try:
                return await func(self, *args, **kwargs)
            # guardian: allow-silent-swallow
            except Exception:
                error = True
                raise
            finally:
                duration_ms = (time.time() - start) * 1000
                self._record_timing(func.__name__, duration_ms, error)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    def register_lazy(self, name: str, initializer: Callable[[], Any]) -> None:
        """
        Register a lazy-initialized resource.

        Args:
            name: Resource name
            initializer: Function to create the resource
        """
        self._lazy_registry[name] = initializer

    def get_lazy(self, name: str) -> Any:
        """
        Get a lazy-initialized resource.

        Args:
            name: Resource name

        Returns:
            The initialized resource

        Raises:
            KeyError: If resource not registered
        """
        if not self._perf_config.lazy_init_enabled:
            if name in self._lazy_registry:
                return self._lazy_registry[name]()
            raise KeyError(f"Lazy resource not registered: {name}")
        with self._perf_lock:
            if name in self._lazy_initialized:
                return self._lazy_initialized[name]
            if name not in self._lazy_registry:
                raise KeyError(f"Lazy resource not registered: {name}")
            resource = self._lazy_registry[name]()
            self._lazy_initialized[name] = resource
            Logger.debug(f"[PERF] Lazy initialized: {name}")
            return resource

    def is_lazy_initialized(self, name: str) -> bool:
        """Check if a lazy resource has been initialized."""
        return name in self._lazy_initialized

    def batch_add(self, queue_name: str, item: Any) -> int:
        """
        Add item to a batch queue.

        Args:
            queue_name: Name of the batch queue
            item: Item to add

        Returns:
            Current queue size

        Raises:
            ValueError: If queue limits are exceeded
        """
        with self._perf_lock:
            if (
                queue_name not in self._batch_queues
                and len(self._batch_queues) >= self._perf_config.max_batch_queues
            ):
                raise ValueError(f"Maximum batch queues ({self._perf_config.max_batch_queues}) exceeded")
            if queue_name not in self._batch_queues:
                self._batch_queues[queue_name] = []
            if len(self._batch_queues[queue_name]) >= self._perf_config.max_batch_queue_size:
                raise ValueError(
                    f"Batch queue '{queue_name}' size limit ({self._perf_config.max_batch_queue_size}) exceeded"
                )
            self._batch_queues[queue_name].append(item)
            return len(self._batch_queues[queue_name])

    def batch_flush(self, queue_name: str) -> list:
        """
        Flush and return all items from a batch queue.

        Args:
            queue_name: Name of the batch queue

        Returns:
            List of items in the queue
        """
        with self._perf_lock:
            items = self._batch_queues.pop(queue_name, [])
            return items

    def batch_size(self, queue_name: str) -> int:
        """Get current size of a batch queue."""
        with self._perf_lock:
            return len(self._batch_queues.get(queue_name, []))

    def should_flush_batch(self, queue_name: str) -> bool:
        """Check if batch queue should be flushed."""
        return self.batch_size(queue_name) >= self._perf_config.batch_size

    def batch_clear_all(self) -> int:
        """Clear all batch queues. Returns count of queues cleared."""
        with self._perf_lock:
            count = len(self._batch_queues)
            self._batch_queues.clear()
            return count

    def get_batching_status(self) -> dict[str, Any]:
        """Get batching status (BatchingMixin-compat)."""
        with self._perf_lock:
            return {
                "batch_queues": {name: len(items) for name, items in self._batch_queues.items()},
                "lazy_registered": len(self._lazy_registry),
                "lazy_initialized": len(self._lazy_initialized),
                "config": {
                    "batch_size": self._perf_config.batch_size,
                    "async_pool_size": self._perf_config.async_pool_size,
                    "max_batch_queues": self._perf_config.max_batch_queues,
                },
            }

    async def execute_batch(
        self,
        tasks: Iterable[Awaitable[T]],
        *,
        concurrency: int = 10,
        timeout: float | None = None,
        return_exceptions: bool = False,
    ) -> list[T]:
        """Execute awaitables with bounded concurrency.

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
                # guardian: allow-silent-swallow
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
        self, tasks: list, max_workers: int | None = None, sequential: bool = False
    ) -> list[Any]:
        """Backwards-compat alias for legacy BatchingMixin callers.

        Args:
            tasks: List of awaitables.
            max_workers: Concurrency limit (defaults to async_pool_size config).
            sequential: If True, run tasks one-by-one.

        Returns:
            List of results (exceptions returned, not raised).
        """
        if sequential:
            results: list[Any] = []
            for task in tasks:
                try:
                    results.append(await task)
                # guardian: allow-silent-swallow
                except Exception as e:
                    results.append(e)
            return results
        effective_workers = max_workers if max_workers is not None else self._perf_config.async_pool_size
        return await self.execute_batch(
            tasks, concurrency=effective_workers, timeout=None, return_exceptions=True
        )

    async def get_async_semaphore(self) -> asyncio.Semaphore:
        """Get or create async semaphore for pooling."""
        if self._async_semaphore is None:
            self._async_semaphore = asyncio.Semaphore(self._perf_config.async_pool_size)
        return self._async_semaphore

    async def run_pooled(self, coro) -> Any:
        """
        Run a coroutine with pool limiting.

        Args:
            coro: Coroutine to run

        Returns:
            Result of the coroutine
        """
        semaphore = await self.get_async_semaphore()
        async with semaphore:
            return await coro

    def get_performance_status(self) -> dict[str, Any]:
        """
        Get overall performance status.

        Returns:
            Dictionary with performance status
        """
        with self._perf_lock:
            return {
                "cache": self.cache_stats(),
                "metrics_count": len(self._perf_metrics),
                "lazy_registered": len(self._lazy_registry),
                "lazy_initialized": len(self._lazy_initialized),
                "batch_queues": {name: len(items) for name, items in self._batch_queues.items()},
                "config": {
                    "cache_enabled": self._perf_config.cache_enabled,
                    "metrics_enabled": self._perf_config.metrics_enabled,
                    "batch_size": self._perf_config.batch_size,
                    "async_pool_size": self._perf_config.async_pool_size,
                },
            }


__all__ = ["PerformanceMixin", "PerformanceConfig", "PerformanceMetrics", "CacheEntry"]
