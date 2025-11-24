"""Provides Redis-based caching so repeated resume improvement runs can reuse LLM outputs, reducing latency and cost without changing business logic."""

from __future__ import annotations

import json
import os
from typing import Any, Optional


class RedisNotConfiguredError(RuntimeError):
    """Signals that caching is unavailable so resume runs can fall back instead of failing silently."""


class RedisClientError(RuntimeError):
    """Wraps low-level Redis issues so they can be surfaced cleanly in logs and monitoring."""


def _import_redis():
    """Imports the redis package lazily so the rest of the resume stack stays import-safe even when caching is disabled."""

    try:  # pragma: no cover - import path is environment dependent
        import redis  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RedisClientError("redis package not installed") from exc
    return redis


def init_redis_client(url: Optional[str] = None, *, timeout_s: float = 1.0):
    """Creates a Redis client for caching so repeated resume work can be served faster and more cheaply when configuration allows it."""

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
    """Checks whether the Redis cache is reachable so the system knows if it can safely rely on cached resume results."""

    try:
        return bool(client.ping())
    except Exception:  # pragma: no cover - network dependent
        return False


def get_llm_cache(client, key: str) -> Optional[Any]:
    """Fetches a cached LLM payload by key so repeated resume runs can reuse earlier reasoning or drafting instead of recomputing it."""

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
    """Stores a cached LLM payload by key so future resume runs can avoid paying again for the same model call."""

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
