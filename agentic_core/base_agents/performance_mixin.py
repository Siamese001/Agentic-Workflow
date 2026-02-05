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
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

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
    # [HARDENING] Memory protection limits
    max_batch_queues: int = 50  # Maximum number of batch queues
    max_batch_queue_size: int = 10000  # Maximum items per batch queue


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

        # Performance configuration
        self._perf_config: PerformanceConfig = PerformanceConfig()

        # LRU Cache storage
        self._method_cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # Performance metrics
        self._perf_metrics: dict[str, PerformanceMetrics] = {}

        # Lazy initialization registry
        self._lazy_registry: dict[str, Callable] = {}
        self._lazy_initialized: dict[str, Any] = {}

        # Batch operation queues
        self._batch_queues: dict[str, list] = {}

        # Thread safety
        self._perf_lock = threading.RLock()

        # Async semaphore for pooling
        self._async_semaphore: asyncio.Semaphore | None = None

        # Initialization flag
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
        # [HARDENING] Validate inputs
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
                self._async_semaphore = None  # Reset semaphore
            if max_batch_queues is not None:
                self._perf_config.max_batch_queues = max_batch_queues
            if max_batch_queue_size is not None:
                self._perf_config.max_batch_queue_size = max_batch_queue_size

        Logger.info(f"[PERF] Configuration updated: {self._perf_config}")

    # =========================================================================
    # Caching
    # =========================================================================

    def cache_get(self, key: str) -> tuple[bool, Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Tuple of (hit, value) - hit is True if found and not expired
        """
        if not self._perf_config.cache_enabled:
            return False, None

        with self._perf_lock:
            entry = self._method_cache.get(key)
            if entry is None:
                return False, None

            if entry.is_expired():
                del self._method_cache[key]
                return False, None

            # Move to end (LRU)
            self._method_cache.move_to_end(key)
            entry.hits += 1
            return True, entry.value

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
            # Evict if at capacity
            while len(self._method_cache) >= self._perf_config.cache_max_size:
                self._method_cache.popitem(last=False)

            self._method_cache[key] = CacheEntry(
                value=value,
                ttl_seconds=ttl or self._perf_config.cache_default_ttl,
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

                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"

                # Check cache
                hit, value = self.cache_get(cache_key)
                if hit:
                    self._record_cache_hit(func.__name__)
                    return value

                # Execute and cache
                self._record_cache_miss(func.__name__)
                result = func(self, *args, **kwargs)
                self.cache_set(cache_key, result, ttl)
                return result

            return wrapper

        return decorator

    # =========================================================================
    # Performance Metrics
    # =========================================================================

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
            except Exception:
                error = True
                raise
            finally:
                duration_ms = (time.time() - start) * 1000
                self._record_timing(func.__name__, duration_ms, error)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    # =========================================================================
    # Lazy Initialization
    # =========================================================================

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

            # Initialize
            resource = self._lazy_registry[name]()
            self._lazy_initialized[name] = resource
            Logger.debug(f"[PERF] Lazy initialized: {name}")
            return resource

    def is_lazy_initialized(self, name: str) -> bool:
        """Check if a lazy resource has been initialized."""
        return name in self._lazy_initialized

    # =========================================================================
    # Batch Operations
    # =========================================================================

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
            # [HARDENING] Check queue count limit
            if (
                queue_name not in self._batch_queues
                and len(self._batch_queues) >= self._perf_config.max_batch_queues
            ):
                raise ValueError(
                    f"Maximum batch queues ({self._perf_config.max_batch_queues}) exceeded"
                )

            if queue_name not in self._batch_queues:
                self._batch_queues[queue_name] = []

            # [HARDENING] Check queue size limit
            if len(self._batch_queues[queue_name]) >= self._perf_config.max_batch_queue_size:
                raise ValueError(
                    f"Batch queue '{queue_name}' size limit "
                    f"({self._perf_config.max_batch_queue_size}) exceeded"
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

    # =========================================================================
    # Async Pooling
    # =========================================================================

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

    # =========================================================================
    # Status
    # =========================================================================

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


__all__ = [
    "PerformanceMixin",
    "PerformanceConfig",
    "PerformanceMetrics",
    "CacheEntry",
]
