"""
Provides Redis caching for résumé analysis results to improve processing speed and reduce costs.

Improves résumé processing efficiency by storing LLM outputs and analysis results for fast retrieval across similar job queries.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from providers.redis_client import RedisClient, init_redis_client


class RedisNotConfiguredError(RuntimeError):
    """
    Indicates résumé caching is unavailable so analysis can continue without performance optimization.

    Improves résumé processing reliability by gracefully handling cache unavailability without breaking analysis workflows.
    """


class RedisClientError(RuntimeError):
    """
    Wraps Redis connection issues to maintain résumé analysis stability during cache failures.

    Improves résumé processing reliability by providing clear error handling for cache-related problems without disrupting workflows.
    """


def init_redis_client(url: Optional[str] = None, *, timeout_s: float = 1.0):
    """
    Creates Redis client for résumé analysis caching to speed up repeated job matching queries.

    Improves résumé processing performance by using provider client instead of direct SDK imports.
    """
    from providers.redis_client import init_redis_client as provider_init_redis_client
    return provider_init_redis_client(url, timeout_s=timeout_s)


def redis_healthcheck(client) -> bool:
    """
    Checks Redis cache availability to ensure résumé analysis can rely on cached results for optimal performance.

    Improves résumé processing reliability by verifying cache connectivity before attempting to store or retrieve analysis results.
    """
    try:
        return bool(client.ping())
    except Exception:  # pragma: no cover - network dependent
        return False


def get_llm_cache(client, key: str) -> Optional[Any]:
    """
    Retrieves cached résumé analysis results to speed up repeated job matching queries and reduce processing costs.

    Improves résumé processing efficiency by reusing previous LLM reasoning and drafting results for similar job applications.
    """

    try:
        raw = client.get(key)
    except Exception as exc:  # pragma: no cover - network dependent
        raise RedisClientError(f"Redis GET failed for key={key!r}: {exc}") from exc

    if raw is None:
        return None

    try:
        return json.loads(raw)
    except Exception:
        # Fallback: return raw bytes if JSON decoding fails.
        return raw


def set_llm_cache(
    client,
    key: str,
    value: Any,
    *,
    ttl_s: Optional[int] = 3600,
) -> None:
    """
    Stores résumé analysis results in cache to speed up future job matching queries and reduce processing costs.

    Improves résumé processing efficiency by saving LLM reasoning and drafting results for reuse across similar job applications.
    """

    try:
        payload = json.dumps(value)
    except TypeError as exc:
        raise RedisClientError(f"Value for key={key!r} is not JSON serialisable: {exc}") from exc

    try:
        if ttl_s is None:
            client.set(key, payload)
        else:
            client.setex(key, ttl_s, payload)
    except Exception as exc:  # pragma: no cover - network dependent
        raise RedisClientError(f"Redis SET failed for key={key!r}: {exc}") from exc



