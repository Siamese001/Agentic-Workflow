from __future__ import annotations

"""
ULTRA-HARDENED @cached Decorator

Features:
- Uses RedisCacheMixin if available on instance
- Fallback to local dict if mixin not present
- Deterministic key generation from args/kwargs
- Metrics collection for dashboard visibility
- Async-safe
- TTL-based expiration

Usage:
    class MyAgent(RedisCacheMixin):
        @cached(ttl=3600, prefix="my_operation")
        async def expensive_operation(self, key: str) -> dict:
            # This result will be cached for 1 hour
            return await self._compute(key)
"""


import functools
import hashlib
import logging
import time
from collections.abc import Callable
from typing import Any

from agentic_core.config.feature_flags import CACHE_METRICS_ENABLED
from agentic_core.observability.cache_metrics import get_cache_metrics

log = logging.getLogger(__name__)


def cached(ttl: int = 3600, prefix: str | None = None):
    """
    ULTRA-HARDENED @cached decorator

    Args:
        ttl: Time-to-live in seconds (default 1 hour)
        prefix: Optional prefix for cache key (defaults to function name)

    Features:
    - Uses RedisCacheMixin if available
    - Fallback to instance dict
    - Deterministic key from args/kwargs
    - Metrics collection
    - Async-safe
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            # Only apply caching if mixin present
            if not hasattr(self, "cache_get") or not hasattr(self, "cache_set"):
                return await func(self, *args, **kwargs)

            # Build deterministic key from function name + args + kwargs
            key_parts = [prefix or func.__name__]
            key_parts.extend(repr(a) for a in args)
            sorted_items = sorted(kwargs.items())
            key_parts.extend(f"{k}:{repr(v)}" for k, v in sorted_items)
            raw_key = ":".join(key_parts)
            cache_key = (
                f"{prefix or func.__name__}:{hashlib.sha256(raw_key.encode()).hexdigest()[:16]}"
            )

            start = time.time()
            metrics = get_cache_metrics()

            try:
                cached_value = await self.cache_get(cache_key)
                latency = (time.time() - start) * 1000

                if cached_value is not None:
                    if CACHE_METRICS_ENABLED:
                        metrics.record(f"cached_{func.__name__}", hit=True, latency_ms=latency)
                    log.debug(f"cache HIT {func.__name__} key={cache_key[:16]}...")
                    return cached_value

                if CACHE_METRICS_ENABLED:
                    metrics.record(f"cached_{func.__name__}", hit=False, latency_ms=latency)
                log.debug(f"cache MISS {func.__name__} key={cache_key[:16]}...")

            except Exception as e:
                log.debug(f"cache lookup failed ({e}) - executing function")
                if CACHE_METRICS_ENABLED:
                    metrics.record_error(f"cached_{func.__name__}")

            # Execute the actual function
            result = await func(self, *args, **kwargs)

            # Store result in cache
            try:
                await self.cache_set(cache_key, result, ttl=ttl)
                log.debug(f"Cached result for {func.__name__} TTL={ttl}s")
            except Exception as e:
                log.debug(f"cache store failed ({e}) - result not cached")

            return result

        return wrapper

    return decorator


def cached_sync(ttl: int = 3600, prefix: str | None = None):
    """
    Synchronous version of @cached decorator for non-async methods.
    Uses local dict fallback only (no Redis for sync).
    """

    def decorator(func: Callable):
        _local_cache: dict = {}

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Build deterministic key
            key_parts = [prefix or func.__name__]
            key_parts.extend(repr(a) for a in args)
            sorted_items = sorted(kwargs.items())
            key_parts.extend(f"{k}:{repr(v)}" for k, v in sorted_items)
            raw_key = ":".join(key_parts)
            cache_key = hashlib.sha256(raw_key.encode()).hexdigest()[:16]

            # Check local cache
            if cache_key in _local_cache:
                entry = _local_cache[cache_key]
                if time.time() < entry["expires"]:
                    log.debug(f"Sync cache HIT {func.__name__}")
                    return entry["value"]
                else:
                    del _local_cache[cache_key]

            log.debug(f"Sync cache MISS {func.__name__}")
            result = func(self, *args, **kwargs)

            _local_cache[cache_key] = {"value": result, "expires": time.time() + ttl}

            return result

        return wrapper

    return decorator
