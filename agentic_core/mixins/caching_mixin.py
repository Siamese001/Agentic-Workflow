"""
CachingMixin - Focused Caching Functionality

Phase 3 MRO Refactoring: Extracted from PerformanceMixin for single responsibility.

Provides:
- LRU cache with TTL
- Thread-safe cache operations
- @cached decorator for method-level caching
"""

from __future__ import annotations

import functools
import logging
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Logger = logging.getLogger(__name__)


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
class CacheConfig:
    """Configuration for caching."""

    enabled: bool = True
    max_size: int = 1000
    default_ttl: float = 300.0


class CachingMixin:
    """
    Mixin providing LRU caching with TTL support.

    Phase 3 MRO Refactoring: Single responsibility - caching only.

    Usage:
        class MyAgent(CachingMixin, SovereignBaseAgent):
            @CachingMixin.cached(ttl=60)
            def expensive_operation(self, key: str) -> dict:
                return self._compute_expensive(key)
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize caching state."""
        super().__init__(**kwargs)
        self._cache_config = CacheConfig()
        self._cache_store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._cache_lock = threading.RLock()
        self._caching_initialized = True
        Logger.debug(f"[CACHE] {self.__class__.__name__} caching initialized")

    def configure_cache(
        self, enabled: bool | None = None, max_size: int | None = None, default_ttl: float | None = None
    ) -> None:
        """Configure caching settings."""
        if max_size is not None and max_size <= 0:
            raise ValueError("max_size must be positive")
        if default_ttl is not None and default_ttl <= 0:
            raise ValueError("default_ttl must be positive")
        with self._cache_lock:
            if enabled is not None:
                self._cache_config.enabled = enabled
            if max_size is not None:
                self._cache_config.max_size = max_size
            if default_ttl is not None:
                self._cache_config.default_ttl = default_ttl

    def cache_get(self, key: str) -> tuple[bool, Any]:
        """Get value from cache. Returns (hit, value)."""
        if not self._cache_config.enabled:
            return (False, None)
        with self._cache_lock:
            entry = self._cache_store.get(key)
            if entry is None:
                return (False, None)
            if entry.is_expired():
                del self._cache_store[key]
                return (False, None)
            self._cache_store.move_to_end(key)
            entry.hits += 1
            return (True, entry.value)

    def cache_set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in cache."""
        if not self._cache_config.enabled:
            return
        with self._cache_lock:
            while len(self._cache_store) >= self._cache_config.max_size:
                self._cache_store.popitem(last=False)
            self._cache_store[key] = CacheEntry(
                value=value, ttl_seconds=ttl or self._cache_config.default_ttl
            )

    def cache_invalidate(self, key: str) -> bool:
        """Invalidate a cache entry. Returns True if entry was found."""
        with self._cache_lock:
            if key in self._cache_store:
                del self._cache_store[key]
                return True
            return False

    def cache_clear(self) -> int:
        """Clear all cache entries. Returns count of entries cleared."""
        with self._cache_lock:
            count = len(self._cache_store)
            self._cache_store.clear()
            return count

    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._cache_lock:
            total_hits = sum(e.hits for e in self._cache_store.values())
            expired = sum(1 for e in self._cache_store.values() if e.is_expired())
            return {
                "size": len(self._cache_store),
                "max_size": self._cache_config.max_size,
                "total_hits": total_hits,
                "expired_entries": expired,
                "enabled": self._cache_config.enabled,
            }

    @staticmethod
    def cached(ttl: float = 300.0, key_func: Callable | None = None):
        """
        Decorator to cache method results.

        Args:
            ttl: Time-to-live in seconds
            key_func: Optional function to generate cache key from args
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                if not isinstance(self, CachingMixin):
                    return func(self, *args, **kwargs)
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
                hit, value = self.cache_get(cache_key)
                if hit:
                    return value
                result = func(self, *args, **kwargs)
                self.cache_set(cache_key, result, ttl)
                return result

            return wrapper

        return decorator


__all__ = ["CachingMixin", "CacheConfig", "CacheEntry"]
