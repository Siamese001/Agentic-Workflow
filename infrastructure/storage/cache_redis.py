"""
Provides Redis caching for résumé analysis results to improve processing speed and reduce costs.

Improves résumé processing efficiency by storing LLM outputs and analysis results for fast retrieval across similar job queries.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional


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


def _import_redis():
    """
    Imports Redis package safely to maintain résumé analysis stability when caching is optional.

    Improves résumé processing reliability by ensuring the analysis stack works even when Redis dependencies are unavailable.
    """

    try:  # pragma: no cover - import path is environment dependent
        import redis  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RedisClientError("redis package not installed") from exc
    return redis


def init_redis_client(url: Optional[str] = None, *, timeout_s: float = 1.0):
    """
    Creates Redis client for résumé analysis caching to speed up repeated job matching queries.

    Improves résumé processing efficiency by enabling fast storage and retrieval of analysis results across similar job applications.
    """

    url = url or os.getenv("REDIS_URL")
    if not url:
        raise RedisNotConfiguredError("REDIS_URL not configured")

    redis = _import_redis()

    try:
        client = redis.Redis.from_url(url, socket_timeout=timeout_s)
        # Lightweight health check; may raise on connection issues.
        client.ping()
    except Exception as exc:  # pragma: no cover - network dependent
        raise RedisClientError(f"Failed to connect to Redis at {url!r}: {exc}") from exc

    return client


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



