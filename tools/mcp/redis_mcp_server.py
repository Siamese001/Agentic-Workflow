"""
Redis MCP Server — Cache/State Inspection and Management

Provides MCP tool access to the Redis cache fabric used by:
- ADG hot cache (node/edge lookups, namespace: adg:*)
- Sovereign orchestrator coordination (L3 orchestration fabric)
- Tool embedding cache (L4 state seam)

All reads go through direct redis-py; writes are scoped to safe
flush/invalidation operations only — no arbitrary SET calls.

Tools (10 core)
---------------
- redis_health:         Ping + INFO stats (memory, keyspace, uptime)
- redis_keys:           SCAN namespace with pattern, returns up to 100 keys
- redis_get:            GET a single key (string, hash, list auto-detected)
- redis_hgetall:        HGETALL a hash key (e.g. ADG node cache entries)
- redis_ttl:            TTL remaining on a key
- redis_dbsize:         Total key count across all namespaces
- redis_namespace_stats: Key count per namespace prefix
- redis_del_key:        DEL a single specific key (targeted invalidation)
- redis_flush_namespace: DEL all keys matching a pattern (e.g. adg:node:*)
- redis_stats:          Full INFO sections: memory, persistence, replication

Integration
-----------
- Connects to localhost:6379 by default (REDIS_HOST/REDIS_PORT/REDIS_DB env override)
- Env vars read inline in _get_client(); agentic_core.config.redis_config is NOT imported
- Follows FastMCP server pattern used by enhanced_http_server.py and otel_mcp_server.py
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import redis as redis_lib
except ImportError:
    print("redis package not found. Install with: pip install redis", file=sys.stderr)
    sys.exit(1)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

logger = logging.getLogger(__name__)

mcp = FastMCP("redis-mcp")

# ─────────────────────────────────────────────────────────────────────────────
# Connection pool (lazy singleton — P3-A)
# ─────────────────────────────────────────────────────────────────────────────

_pool: redis_lib.ConnectionPool | None = None


def _get_client() -> redis_lib.Redis:
    global _pool
    if _pool is None:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        timeout = float(os.getenv("REDIS_TIMEOUT", "5"))  # float: supports sub-second values
        _pool = redis_lib.ConnectionPool(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            socket_timeout=timeout,
            socket_connect_timeout=timeout,
        )
    return redis_lib.Redis(connection_pool=_pool)


def _reset_pool() -> None:
    """Reset the connection pool. For test teardown only — not an MCP tool."""
    global _pool
    if _pool is not None:
        _pool.disconnect()
    _pool = None


def _safe_connect() -> tuple[redis_lib.Redis | None, str | None]:
    try:
        client = _get_client()
        client.ping()
        return client, None
    except redis_lib.ConnectionError as e:
        return None, f"Redis connection refused: {e}"
    except Exception as e:  # guardian: allow-broad-except -- outer safety net for unexpected Redis errors
        return None, f"Redis error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────────────────────────────────────


@mcp.tool()
def redis_health() -> dict[str, Any]:
    """Ping Redis and return INFO stats: memory, keyspace, uptime, version."""
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    info = client.info()
    active_db = int(os.getenv("REDIS_DB", "0"))  # P0-B: reflect actual active DB
    return {
        "status": "ok",
        "redis_version": info.get("redis_version"),
        "uptime_seconds": info.get("uptime_in_seconds"),
        "connected_clients": info.get("connected_clients"),
        "used_memory_human": info.get("used_memory_human"),
        "used_memory_peak_human": info.get("used_memory_peak_human"),
        "keyspace": info.get(f"db{active_db}", {}),
        "total_commands_processed": info.get("total_commands_processed"),
        "role": info.get("role"),
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
    }


@mcp.tool()
def redis_dbsize() -> dict[str, Any]:
    """Return total number of keys in the current Redis database."""
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}
    return {"status": "ok", "total_keys": client.dbsize()}


@mcp.tool()
def redis_namespace_stats(top_n: int = 20) -> dict[str, Any]:
    """Return key counts grouped by top-level namespace prefix (e.g. adg:, coord:, embed:).

    Args:
        top_n: Number of top namespaces to return (default 20).
    """
    top_n = min(top_n, 100)  # P2-A: hard cap to prevent oversized responses
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    counts: dict[str, int] = {}
    cursor = 0
    scanned = 0
    while True:
        cursor, keys = client.scan(cursor, count=500)
        scanned += len(keys)
        for key in keys:
            prefix = key.split(":")[0] if ":" in key else key[:16]
            counts[prefix] = counts.get(prefix, 0) + 1
        if cursor == 0:
            break
        if scanned > 50000:
            break

    sorted_ns = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return {
        "status": "ok",
        "scanned_keys": scanned,
        "truncated": scanned >= 50000,
        "namespaces": [{"prefix": k, "count": v} for k, v in sorted_ns],
    }


@mcp.tool()
def redis_keys(pattern: str = "adg:*", limit: int = 50) -> dict[str, Any]:
    """SCAN for keys matching a pattern. Safe — uses SCAN not KEYS.

    Args:
        pattern: Redis key pattern (e.g. 'adg:node:*', 'coord:*', '*'). Default 'adg:*'.
        limit:   Max keys to return (default 50, max 200).
    """
    limit = min(limit, 200)
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    results: list[str] = []
    cursor = 0
    while len(results) < limit:
        cursor, keys = client.scan(cursor, match=pattern, count=100)
        results.extend(keys)
        if cursor == 0:
            break

    results = results[:limit]
    return {
        "status": "ok",
        "pattern": pattern,
        "count": len(results),
        "keys": results,
    }


@mcp.tool()
def redis_get(key: str) -> dict[str, Any]:
    """GET the value for a single key. Auto-detects type (string/hash/list/set/zset).

    Args:
        key: Redis key to retrieve.
    """
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    # P1-A: type() returns "none" for missing keys — no separate exists() round-trip needed
    key_type = client.type(key)
    if key_type == "none":
        return {"status": "not_found", "key": key}

    ttl = client.ttl(key)
    truncated = False

    if key_type == "string":
        # P2-B: guard large strings to avoid oversized MCP responses
        size = client.strlen(key)
        if size > 65536:
            value = "<truncated>"
            truncated = True
            extra: dict[str, Any] = {"value_bytes": size}
        else:
            value = client.get(key)
            extra = {}
    elif key_type == "hash":
        # P2-B: guard large hashes — return field names only when > 500 fields
        field_count = client.hlen(key)
        if field_count > 500:
            value = client.hkeys(key)
            truncated = True
        else:
            value = client.hgetall(key)
        extra = {}
    elif key_type == "list":
        value = client.lrange(key, 0, 99)
        extra = {}
    elif key_type == "set":
        # P2-B: guard large sets — cap at 500 members via SSCAN
        member_count = client.scard(key)
        if member_count > 500:
            _, members = client.sscan(key, count=500)
            value = list(members)[:500]
            truncated = True
        else:
            value = list(client.smembers(key))
        extra = {}
    elif key_type == "zset":
        value = client.zrange(key, 0, 99, withscores=True)
        extra = {}
    else:
        value = f"<unsupported type: {key_type}>"
        extra = {}

    return {
        "status": "ok",
        "key": key,
        "type": key_type,
        "ttl_seconds": ttl,
        "value": value,
        "truncated": truncated,
        **extra,
    }


@mcp.tool()
def redis_hgetall(key: str) -> dict[str, Any]:
    """HGETALL for a hash key. Useful for ADG node cache entries and coord fabric state.

    Args:
        key: Redis hash key.
    """
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    # P1-A: type() encodes missing key as "none" — no exists() pre-check needed
    key_type = client.type(key)
    if key_type == "none":
        return {"status": "not_found", "key": key}
    if key_type != "hash":
        return {"status": "error", "error": f"Key '{key}' is type '{key_type}', not hash"}

    # P2-B: guard large hashes — return field names only when > 500 fields
    field_count = client.hlen(key)
    if field_count > 500:
        return {
            "status": "ok",
            "key": key,
            "ttl_seconds": client.ttl(key),
            "fields": client.hkeys(key),
            "truncated": True,
        }

    return {
        "status": "ok",
        "key": key,
        "ttl_seconds": client.ttl(key),
        "fields": client.hgetall(key),
        "truncated": False,
    }


@mcp.tool()
def redis_ttl(key: str) -> dict[str, Any]:
    """Return TTL remaining (seconds) for a key. -1 = no expiry, -2 = not found.

    Args:
        key: Redis key.
    """
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    # P1-A: ttl() returns -2 for missing keys — exists() round-trip is redundant and racy
    ttl = client.ttl(key)
    return {
        "status": "ok",
        "key": key,
        "ttl_seconds": ttl,
        "interpretation": "no_expiry" if ttl == -1 else ("not_found" if ttl == -2 else f"expires_in_{ttl}s"),
    }


@mcp.tool()
def redis_del_key(key: str) -> dict[str, Any]:
    """DEL a single specific key (targeted cache invalidation).

    Args:
        key: Exact Redis key to delete.
    """
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    # P1-A: delete() returns count of removed keys — exists() pre-check is redundant and racy
    deleted = client.delete(key)
    return {
        "status": "ok",
        "key": key,
        "existed": bool(deleted),
        "deleted": bool(deleted),
    }


@mcp.tool()
def redis_flush_namespace(pattern: str, dry_run: bool = True) -> dict[str, Any]:
    """DEL all keys matching a pattern. Defaults to dry_run=True for safety.

    Args:
        pattern:  Redis key pattern (e.g. 'adg:node:*', 'coord:lock:*').
        dry_run:  If True (default), only lists matching keys without deleting.
    """
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    matching: list[str] = []
    cursor = 0
    while True:
        cursor, keys = client.scan(cursor, match=pattern, count=200)
        matching.extend(keys)
        if cursor == 0:
            break
        if len(matching) > 5000:
            break

    if dry_run:
        return {
            "status": "ok",
            "dry_run": True,
            "pattern": pattern,
            "matching_count": len(matching),
            "sample": matching[:20],
            "message": "Set dry_run=False to actually delete",
        }

    # NOTE: reduced TOCTOU — batching shrinks the race window vs. a single bulk DEL, but
    # keys added between SCAN completion and pipeline execution are still silently missed.
    # Full elimination (Lua atomic scan+delete) is deferred to a follow-on hardening pass.
    deleted = 0
    if matching:
        pipe = client.pipeline(transaction=False)
        for i in range(0, len(matching), 500):
            pipe.delete(*matching[i : i + 500])
        results = pipe.execute()
        deleted = sum(results)

    return {
        "status": "ok",
        "dry_run": False,
        "pattern": pattern,
        "deleted_count": deleted,
        "truncated": len(matching) >= 5000,  # P1-B: surface scan cap on live-delete path
    }


@mcp.tool()
def redis_stats() -> dict[str, Any]:
    """Return full Redis INFO: memory, persistence, replication, clients, stats sections."""
    client, err = _safe_connect()
    if err:
        return {"status": "unavailable", "error": err}

    info = client.info("all")
    sections = {
        "server": {
            k: info[k] for k in ("redis_version", "uptime_in_seconds", "tcp_port", "os", "hz") if k in info
        },
        "memory": {
            k: info[k]
            for k in (
                "used_memory_human",
                "used_memory_peak_human",
                "used_memory_rss_human",
                "mem_fragmentation_ratio",
                "maxmemory_human",
                "maxmemory_policy",
            )
            if k in info
        },
        "persistence": {
            k: info[k]
            for k in (
                "rdb_last_save_time",
                "rdb_last_bgsave_status",
                "aof_enabled",
                "loading",
            )
            if k in info
        },
        "replication": {k: info[k] for k in ("role", "connected_slaves", "master_replid") if k in info},
        "clients": {
            k: info[k] for k in ("connected_clients", "blocked_clients", "tracking_clients") if k in info
        },
        "stats": {
            k: info[k]
            for k in (
                "total_commands_processed",
                "total_connections_received",
                "keyspace_hits",
                "keyspace_misses",
                "evicted_keys",
                "expired_keys",
            )
            if k in info
        },
        "keyspace": {k: v for k, v in info.items() if k.startswith("db")},
    }
    return {"status": "ok", "sections": sections}


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger.info("Starting Redis MCP Server")
    mcp.run()
