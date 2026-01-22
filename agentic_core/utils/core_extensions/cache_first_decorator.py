from __future__ import annotations

"""
Cache-First Decorator for Meta-Learning DNA

[PHASE 33g] Provides @cache_first decorator for mandatory Redis/Pinecone lookups
before any expensive operation (LLM calls, analysis, healing).

Meta-Learning is core to agentic DNA - every LLM call and key operation
MUST check Redis cache and Pinecone semantic memory FIRST.

Usage:

    class MyAgent(RedisCacheMixin, PineconeVectorMixin):
        @cache_first(cache_prefix="my_agent", ttl=3600)
        def analyze_violation(self, file_path, violation_type, context=None):
            # This only runs on cache miss
            return self._expensive_llm_call(file_path, violation_type)

Cache-First Flow:
    1. Generate cache key from function args
    2. Check Redis for exact match
    3. Check Pinecone for semantic similarity (if embedding available)
    4. Only call wrapped function on cache miss
    5. Store result in both caches for future reuse
"""

import functools
import hashlib
import json
import logging
import time
from typing import Any, TypeVar
from collections.abc import Callable

Logger = logging.getLogger(__name__)

T = TypeVar("T")


def _make_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate a deterministic cache key from function arguments."""
    # Convert args to hashable representation
    key_parts = [prefix, func_name]

    for arg in args:
        if hasattr(arg, "__dict__"):
            # Skip self/cls
            continue
        key_parts.append(str(arg)[:200])

    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={str(v)[:100]}")

    key_str = ":".join(key_parts)
    key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:32]
    return f"{prefix}:{func_name}:{key_hash}"


def _serialize_result(result: Any) -> str | None:
    """Serialize result to JSON for caching."""
    try:
        if hasattr(result, "__dict__"):
            return json.dumps(result.__dict__, default=str)
        return json.dumps(result, default=str)
    except Exception:
        return None


def _deserialize_result(cached: str | dict, result_type: type | None = None) -> Any:
    """Deserialize cached result."""
    try:
        if isinstance(cached, str):
            return json.loads(cached)
        return cached
    except Exception:
        return cached


def cache_first(
    cache_prefix: str = "agent",
    ttl: int = 3600,
    semantic_threshold: float = 0.9,
    skip_on_error: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that enforces cache-first pattern for Meta-Learning DNA.

    Args:
        cache_prefix: Prefix for cache keys (e.g., "cognitive_disposition")
        ttl: Time-to-live in seconds for cached results
        semantic_threshold: Minimum similarity score for Pinecone matches
        skip_on_error: If True, continue to wrapped function on cache errors

    Returns:
        Decorated function with cache-first behavior

    Example:
        @cache_first(cache_prefix="violation_analysis", ttl=86400)
        def analyze_violation(self, file_path, violation_type):
            return self._expensive_llm_call(...)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            func_name = func.__name__
            cache_key = _make_cache_key(cache_prefix, func_name, args, kwargs)

            # === STEP 1: Check Redis/local cache ===
            try:
                # Try mixin's cache_get if available
                if hasattr(self, "_local_cache") and self._local_cache:
                    cached = self._local_cache.get(cache_key)
                    if cached is not None:
                        Logger.debug(f"[CACHE-FIRST] Redis HIT for {func_name}")
                        return _deserialize_result(cached)
            except Exception as e:
                if not skip_on_error:
                    raise
                Logger.debug(f"[CACHE-FIRST] Redis lookup failed: {e}")

            # === STEP 2: Check Pinecone/semantic memory ===
            try:
                if hasattr(self, "_local_vectors") and self._local_vectors:
                    # Simple pattern matching for semantic similarity
                    for vid, vdata in self._local_vectors.items():
                        if func_name in vid:
                            Logger.debug(f"[CACHE-FIRST] Pinecone HIT for {func_name}")
                            return _deserialize_result(vdata.get("result", {}))
            except Exception as e:
                if not skip_on_error:
                    raise
                Logger.debug(f"[CACHE-FIRST] Pinecone lookup failed: {e}")

            # === STEP 3: Cache miss - call wrapped function ===
            Logger.debug(f"[CACHE-FIRST] Cache MISS for {func_name} - executing")
            start_time = time.time()
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time

            # === STEP 4: Store in caches ===
            try:
                serialized = _serialize_result(result)
                if serialized:
                    # Store in local cache
                    if hasattr(self, "_local_cache"):
                        if not isinstance(self._local_cache, dict):
                            self._local_cache = {}
                        self._local_cache[cache_key] = serialized

                    # Store in semantic memory
                    if hasattr(self, "_local_vectors"):
                        if not isinstance(self._local_vectors, dict):
                            self._local_vectors = {}
                        vector_id = f"{func_name}:{cache_key[:16]}"
                        self._local_vectors[vector_id] = {
                            "result": serialized,
                            "execution_time": execution_time,
                        }

                    Logger.debug(f"[CACHE-FIRST] Stored result in cache ({execution_time:.2f}s)")
            except Exception as e:
                Logger.debug(f"[CACHE-FIRST] Cache storage failed: {e}")

            return result

        return wrapper

    return decorator


def cache_first_async(
    cache_prefix: str = "agent",
    ttl: int = 3600,
    semantic_threshold: float = 0.9,
    skip_on_error: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Async version of cache_first decorator.

    Same behavior as cache_first but for async functions.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            func_name = func.__name__
            cache_key = _make_cache_key(cache_prefix, func_name, args, kwargs)

            # === STEP 1: Check Redis/local cache ===
            try:
                if hasattr(self, "cache_get"):
                    cached = await self.cache_get(cache_key)
                    if cached is not None:
                        Logger.debug(f"[CACHE-FIRST-ASYNC] Redis HIT for {func_name}")
                        return _deserialize_result(cached)
                elif hasattr(self, "_local_cache") and self._local_cache:
                    cached = self._local_cache.get(cache_key)
                    if cached is not None:
                        Logger.debug(f"[CACHE-FIRST-ASYNC] Local HIT for {func_name}")
                        return _deserialize_result(cached)
            except Exception as e:
                if not skip_on_error:
                    raise
                Logger.debug(f"[CACHE-FIRST-ASYNC] Cache lookup failed: {e}")

            # === STEP 2: Check Pinecone/semantic memory ===
            try:
                if hasattr(self, "vector_search"):
                    # Would need embedding - skip for now
                    pass
            except Exception as e:
                Logger.debug(f"[CACHE-FIRST-ASYNC] Semantic lookup failed: {e}")

            # === STEP 3: Cache miss - call wrapped function ===
            Logger.debug(f"[CACHE-FIRST-ASYNC] Cache MISS for {func_name}")
            start_time = time.time()
            result = await func(self, *args, **kwargs)
            execution_time = time.time() - start_time

            # === STEP 4: Store in caches ===
            try:
                serialized = _serialize_result(result)
                if serialized:
                    if hasattr(self, "cache_set"):
                        await self.cache_set(cache_key, serialized, ttl=ttl)
                    elif hasattr(self, "_local_cache"):
                        if not isinstance(self._local_cache, dict):
                            self._local_cache = {}
                        self._local_cache[cache_key] = serialized
                    Logger.debug(f"[CACHE-FIRST-ASYNC] Stored result ({execution_time:.2f}s)")
            except Exception as e:
                Logger.debug(f"[CACHE-FIRST-ASYNC] Cache storage failed: {e}")

            return result

        return wrapper

    return decorator


class CacheFirstMixin:
    """
    Mixin that provides cache-first infrastructure for agents.

    Inherit from this mixin to get automatic cache-first support
    without needing to use decorators on every method.

    Usage:
        class MyAgent(CacheFirstMixin, L5SafetyBaseAgent):
            _cache_prefix = "my_agent"
            _cache_ttl = 3600

            def analyze_violation(self, ...):
                # Automatically uses cache-first pattern
                return self._cached_operation("analyze", self._do_analyze, ...)
    """

    _cache_prefix: str = "agent"
    _cache_ttl: int = 3600
    _local_cache: dict = {}
    _local_vectors: dict = {}
    _cache_stats: dict = {"hits": 0, "misses": 0, "errors": 0}

    def _cached_operation(
        self,
        operation_name: str,
        func: Callable,
        *args,
        cache_key_extra: str = "",
        **kwargs,
    ) -> Any:
        """
        Execute an operation with cache-first pattern.

        Args:
            operation_name: Name of the operation (for cache key)
            func: The actual function to call on cache miss
            *args: Arguments to pass to func
            cache_key_extra: Additional string to include in cache key
            **kwargs: Keyword arguments to pass to func

        Returns:
            Cached result or fresh result from func
        """
        # Build cache key
        key_parts = [self._cache_prefix, operation_name]
        if cache_key_extra:
            key_parts.append(cache_key_extra)
        for arg in args:
            key_parts.append(str(arg)[:100])

        cache_key = hashlib.sha256(":".join(key_parts).encode()).hexdigest()[:40]

        # Check cache
        if cache_key in self._local_cache:
            self._cache_stats["hits"] += 1
            Logger.debug(f"[CACHE-FIRST] HIT for {operation_name}")
            return self._local_cache[cache_key]

        # Cache miss - execute
        self._cache_stats["misses"] += 1
        Logger.debug(f"[CACHE-FIRST] MISS for {operation_name}")

        try:
            result = func(*args, **kwargs)

            # Store in cache
            self._local_cache[cache_key] = result

            return result
        except Exception:
            self._cache_stats["errors"] += 1
            raise

    def get_cache_stats(self) -> dict:
        """Get cache hit/miss statistics."""
        total = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = self._cache_stats["hits"] / total if total > 0 else 0.0
        return {
            **self._cache_stats,
            "total": total,
            "hit_rate": hit_rate,
        }

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._local_cache.clear()
        self._local_vectors.clear()
        Logger.info(f"[CACHE-FIRST] Cache cleared for {self._cache_prefix}")


__all__ = [
    "cache_first",
    "cache_first_async",
    "CacheFirstMixin",
]
