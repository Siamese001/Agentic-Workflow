"""
Trait System - Decorator-based Capability Injection

Phase 5 MRO Refactoring: Future-proof alternative to mixin inheritance.

Instead of deep inheritance hierarchies:
    class MyAgent(CachingMixin, MetricsMixin, BatchingMixin, SovereignBaseAgent):
        pass

Use traits for cleaner composition:
    @with_traits(CachingTrait, MetricsTrait)
    class MyAgent(LightweightBase):
        pass

Benefits:
- No MRO complexity from multiple inheritance
- Explicit capability declaration
- Easy to test traits in isolation
- Runtime capability inspection
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

Logger = logging.getLogger(__name__)
T = TypeVar("T")


class Trait(ABC):
    """
    Base class for traits that can be applied to agents.

    Traits inject methods and state into a class at decoration time,
    avoiding the complexity of multiple inheritance MRO.
    """

    @classmethod
    @abstractmethod
    def apply(cls, target_cls: type) -> type:
        """
        Apply this trait to a target class.

        Args:
            target_cls: The class to modify

        Returns:
            The modified class
        """
        pass

    @classmethod
    def get_trait_name(cls) -> str:
        """Get the name of this trait."""
        return cls.__name__


class CachingTrait(Trait):
    """
    Trait providing LRU caching with TTL.

    Equivalent to CachingMixin but applied via decorator.
    """

    @classmethod
    def apply(cls, target_cls: type) -> type:
        """Apply caching capabilities to target class."""
        import threading
        from collections import OrderedDict

        from agentic_core.mixins.caching_mixin import CacheConfig, CacheEntry

        original_post_init = getattr(target_cls, "__post_init__", None)

        def new_post_init(self):
            self._cache_config = CacheConfig()
            self._cache_store = OrderedDict()
            self._cache_lock = threading.RLock()
            self._caching_trait_applied = True
            if original_post_init:
                original_post_init(self)

        def cache_get(self, key: str) -> tuple[bool, Any]:
            if not self._cache_config.enabled:
                return (False, None)
            with self._cache_lock:
                entry = self._cache_store.get(key)
                if entry is None or entry.is_expired():
                    if entry:
                        del self._cache_store[key]
                    return (False, None)
                self._cache_store.move_to_end(key)
                entry.hits += 1
                return (True, entry.value)

        def cache_set(self, key: str, value: Any, ttl: float | None = None) -> None:
            if not self._cache_config.enabled:
                return
            with self._cache_lock:
                while len(self._cache_store) >= self._cache_config.max_size:
                    self._cache_store.popitem(last=False)
                self._cache_store[key] = CacheEntry(
                    value=value, ttl_seconds=ttl or self._cache_config.default_ttl
                )

        def cache_clear(self) -> int:
            with self._cache_lock:
                count = len(self._cache_store)
                self._cache_store.clear()
                return count

        target_cls.__post_init__ = new_post_init
        target_cls.cache_get = cache_get
        target_cls.cache_set = cache_set
        target_cls.cache_clear = cache_clear
        if not hasattr(target_cls, "_applied_traits"):
            target_cls._applied_traits = []
        target_cls._applied_traits.append("CachingTrait")
        return target_cls


class MetricsTrait(Trait):
    """
    Trait providing performance metrics collection.

    Equivalent to MetricsMixin but applied via decorator.
    """

    @classmethod
    def apply(cls, target_cls: type) -> type:
        """Apply metrics capabilities to target class."""
        import threading

        from agentic_core.mixins.metrics_mixin import MetricsConfig, PerformanceMetrics

        original_post_init = getattr(target_cls, "__post_init__", None)

        def new_post_init(self):
            self._metrics_config = MetricsConfig()
            self._metrics_store = {}
            self._metrics_lock = threading.RLock()
            self._metrics_trait_applied = True
            if original_post_init:
                original_post_init(self)

        def record_timing(self, operation_name: str, duration_ms: float, error: bool = False) -> None:
            if not self._metrics_config.enabled:
                return
            with self._metrics_lock:
                if operation_name not in self._metrics_store:
                    self._metrics_store[operation_name] = PerformanceMetrics(operation_name=operation_name)
                metrics = self._metrics_store[operation_name]
                metrics.call_count += 1
                metrics.total_time_ms += duration_ms
                metrics.min_time_ms = min(metrics.min_time_ms, duration_ms)
                metrics.max_time_ms = max(metrics.max_time_ms, duration_ms)
                if error:
                    metrics.errors += 1

        def get_metrics(self, operation_name: str | None = None) -> dict[str, Any]:
            with self._metrics_lock:
                if operation_name:
                    metrics = self._metrics_store.get(operation_name)
                    return metrics.to_dict() if metrics else {}
                return {n: m.to_dict() for n, m in self._metrics_store.items()}

        def reset_metrics(self) -> None:
            with self._metrics_lock:
                self._metrics_store.clear()

        target_cls.__post_init__ = new_post_init
        target_cls.record_timing = record_timing
        target_cls.get_metrics = get_metrics
        target_cls.reset_metrics = reset_metrics
        if not hasattr(target_cls, "_applied_traits"):
            target_cls._applied_traits = []
        target_cls._applied_traits.append("MetricsTrait")
        return target_cls


class BatchingTrait(Trait):
    """
    Trait providing batch operations and async pooling.

    Equivalent to BatchingMixin but applied via decorator.
    """

    @classmethod
    def apply(cls, target_cls: type) -> type:
        """Apply batching capabilities to target class."""
        import asyncio
        import threading

        original_post_init = getattr(target_cls, "__post_init__", None)

        def new_post_init(self):
            self._batch_queues = {}
            # guardian: allow-magic-config
            self._batch_size = 100
            # guardian: allow-magic-config
            self._max_batch_queues = 50
            self._batching_lock = threading.RLock()
            self._async_semaphore = None
            self._async_pool_size = 10
            self._batching_trait_applied = True
            if original_post_init:
                original_post_init(self)

        def batch_add(self, queue_name: str, item: Any) -> int:
            with self._batching_lock:
                if queue_name not in self._batch_queues and len(self._batch_queues) >= self._max_batch_queues:
                    raise ValueError(f"Maximum batch queues ({self._max_batch_queues}) exceeded")
                if queue_name not in self._batch_queues:
                    self._batch_queues[queue_name] = []
                self._batch_queues[queue_name].append(item)
                return len(self._batch_queues[queue_name])

        def batch_flush(self, queue_name: str) -> list:
            with self._batching_lock:
                return self._batch_queues.pop(queue_name, [])

        def should_flush_batch(self, queue_name: str) -> bool:
            with self._batching_lock:
                return len(self._batch_queues.get(queue_name, [])) >= self._batch_size

        async def run_pooled(self, coro) -> Any:
            if self._async_semaphore is None:
                self._async_semaphore = asyncio.Semaphore(self._async_pool_size)
            async with self._async_semaphore:
                return await coro

        target_cls.__post_init__ = new_post_init
        target_cls.batch_add = batch_add
        target_cls.batch_flush = batch_flush
        target_cls.should_flush_batch = should_flush_batch
        target_cls.run_pooled = run_pooled
        if not hasattr(target_cls, "_applied_traits"):
            target_cls._applied_traits = []
        target_cls._applied_traits.append("BatchingTrait")
        return target_cls


def with_traits(*traits: type[Trait]) -> Callable[[type[T]], type[T]]:
    """
    Decorator to apply traits to a class.

    Usage:
        @with_traits(CachingTrait, MetricsTrait)
        class MyAgent(LightweightBase):
            pass

    Args:
        *traits: Trait classes to apply

    Returns:
        Decorator function
    """

    def decorator(cls: type[T]) -> type[T]:
        result = cls
        for trait in traits:
            result = trait.apply(result)
            Logger.debug(f"[TRAIT] Applied {trait.get_trait_name()} to {cls.__name__}")
        return result

    return decorator


def get_applied_traits(obj: Any) -> list[str]:
    """Get list of traits applied to an object or class."""
    if isinstance(obj, type):
        return getattr(obj, "_applied_traits", [])
    return getattr(obj.__class__, "_applied_traits", [])


def has_trait(obj: Any, trait_name: str) -> bool:
    """Check if an object or class has a specific trait applied."""
    return trait_name in get_applied_traits(obj)


__all__ = [
    "Trait",
    "CachingTrait",
    "MetricsTrait",
    "BatchingTrait",
    "with_traits",
    "get_applied_traits",
    "has_trait",
]
