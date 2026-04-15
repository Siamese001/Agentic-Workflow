"""Redis client bootstrap, pooling, and safe connection helpers."""

from __future__ import annotations

import sys
from typing import cast

from .config import RedisConnectionConfig

try:
    import redis as redis_lib
except ImportError:
    print("redis package not found. Install with: pip install redis", file=sys.stderr)
    sys.exit(1)

_pool: redis_lib.ConnectionPool | None = None


def get_client() -> redis_lib.Redis:
    """Return a Redis client backed by a lazy singleton connection pool."""
    global _pool
    if _pool is None:
        config = RedisConnectionConfig.from_env()
        _pool = redis_lib.ConnectionPool(
            host=config.host,
            port=config.port,
            db=config.db,
            decode_responses=True,
            socket_timeout=config.timeout_seconds,
            socket_connect_timeout=config.timeout_seconds,
        )
    return redis_lib.Redis(connection_pool=cast(redis_lib.ConnectionPool, _pool))


def reset_pool() -> None:
    """Reset the connection pool. Intended for tests only."""
    global _pool
    if _pool is not None:
        _pool.disconnect()
    _pool = None


def safe_connect() -> tuple[redis_lib.Redis | None, str | None]:
    """Return a live Redis client or a user-safe error string."""
    try:
        client = get_client()
        client.ping()
        return client, None
    except redis_lib.ConnectionError as exc:
        return None, f"Redis connection refused: {exc}"
    except Exception as exc:  # guardian: allow-broad-except -- outer safety net for unexpected Redis errors
        return None, f"Redis error: {exc}"


def get_active_db() -> int:
    """Return the currently selected Redis DB from environment."""
    return RedisConnectionConfig.from_env().db


def get_connection_metadata() -> dict[str, int | str]:
    """Return host/port/db details for response payloads."""
    config = RedisConnectionConfig.from_env()
    return {
        "host": config.host,
        "port": config.port,
        "db": config.db,
    }


__all__ = [
    "get_active_db",
    "get_client",
    "get_connection_metadata",
    "redis_lib",
    "reset_pool",
    "safe_connect",
]
