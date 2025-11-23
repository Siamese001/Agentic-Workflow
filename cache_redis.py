"""Redis-backed caching utilities (v10_10 · META layer).

This module encapsulates all direct interactions with Redis so that
L1–L5 layers and agents remain pure. It is safe to import even if the
`redis` package is not installed: imports are performed lazily inside
helper functions and surfaced as explicit errors.

Responsibilities:
    • Provide a thin, testable abstraction over a Redis client.
    • Support exact LLM response caching (key → JSON/text payload).
    • Provide basic health checks.

Non-responsibilities:
    • No knowledge of prompts, agents, or workflow plans.
    • No business logic for cache key construction.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional


class RedisNotConfiguredError(RuntimeError):
    """Raised when Redis usage is requested but not configured/enabled."""


class RedisClientError(RuntimeError):
    """Raised when the underlying Redis client cannot be created or used."""


def _import_redis():
    """Import the redis package lazily.

    This helper ensures the module can be imported even if `redis` is not
    installed, while still providing a clear error at call time.
    """

    try:  # pragma: no cover - import path is environment dependent
        import redis  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RedisClientError("redis package not installed") from exc
    return redis


def init_redis_client(url: Optional[str] = None, *, timeout_s: float = 1.0):
    """Initialise a synchronous Redis client.

    Parameters
    ----------
    url:
        Redis connection URL. If omitted, REDIS_URL is read from the
        environment. If still missing, :class:`RedisNotConfiguredError`
        is raised.
    timeout_s:
        Socket/connect timeout in seconds.
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
    """Return True if the Redis client responds to PING, False otherwise."""

    try:
        return bool(client.ping())
    except Exception:  # pragma: no cover - network dependent
        return False


def get_llm_cache(client, key: str) -> Optional[Any]:
    """Fetch a cached LLM payload by key.

    The value is expected to be JSON-encoded; failures to decode will
    result in ``None``.
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
    """Store a cached LLM payload by key.

    The value is JSON-encoded before writing. Errors are surfaced as
    :class:`RedisClientError`.
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
