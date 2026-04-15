"""Read-only Redis MCP tools."""

from __future__ import annotations

from typing import Any

from .client import get_active_db, get_connection_metadata, redis_lib, safe_connect
from .constants import (
    KEY_SCAN_COUNT,
    MAX_HASH_FIELDS,
    MAX_KEY_LIST_LIMIT,
    MAX_LIST_ITEMS,
    MAX_NAMESPACE_TOP_N,
    MAX_SET_MEMBERS,
    MAX_STRING_BYTES,
    MAX_ZSET_ITEMS,
    NAMESPACE_SCAN_CAP,
    NAMESPACE_SCAN_COUNT,
)
from .scan_utils import scan_keys


def _get_key_value(client: redis_lib.Redis, key: str, key_type: str) -> tuple[Any, bool, dict[str, Any]]:
    """Read one key with size-aware guards."""
    truncated = False
    extra: dict[str, Any] = {}

    if key_type == "string":
        size = client.strlen(key)
        if size > MAX_STRING_BYTES:
            return "<truncated>", True, {"value_bytes": size}
        return client.get(key), False, {}

    if key_type == "hash":
        field_count = client.hlen(key)
        if field_count > MAX_HASH_FIELDS:
            return client.hkeys(key), True, {}
        return client.hgetall(key), False, {}

    if key_type == "list":
        return client.lrange(key, 0, MAX_LIST_ITEMS - 1), False, {}

    if key_type == "set":
        member_count = client.scard(key)
        if member_count > MAX_SET_MEMBERS:
            _, members = client.sscan(key, count=MAX_SET_MEMBERS)
            return list(members)[:MAX_SET_MEMBERS], True, {}
        return list(client.smembers(key)), False, {}

    if key_type == "zset":
        return client.zrange(key, 0, MAX_ZSET_ITEMS - 1, withscores=True), False, {}

    return f"<unsupported type: {key_type}>", truncated, extra


def _build_unavailable_response(error: str) -> dict[str, Any]:
    return {"status": "unavailable", "error": error}


def register_read_tools(mcp: Any) -> None:
    """Register all read-only inspection tools onto the provided MCP server."""

    @mcp.tool()
    def redis_health() -> dict[str, Any]:
        """Ping Redis and return INFO stats: memory, keyspace, uptime, version."""
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        info = client.info()
        active_db = get_active_db()
        connection = get_connection_metadata()
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
            "host": connection["host"],
            "port": connection["port"],
            "db": connection["db"],
        }

    @mcp.tool()
    def redis_dbsize() -> dict[str, Any]:
        """Return total number of keys in the current Redis database."""
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)
        return {"status": "ok", "total_keys": client.dbsize()}

    @mcp.tool()
    def redis_namespace_stats(top_n: int = 20) -> dict[str, Any]:
        """Return key counts grouped by top-level namespace prefix.

        Args:
            top_n: Number of top namespaces to return (default 20).
        """
        requested_top_n = max(0, min(top_n, MAX_NAMESPACE_TOP_N))
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        scan_result = scan_keys(
            client,
            count=NAMESPACE_SCAN_COUNT,
            scan_cap=NAMESPACE_SCAN_CAP,
        )

        counts: dict[str, int] = {}
        for key in scan_result.keys:
            prefix = key.split(":")[0] if ":" in key else key[:16]
            counts[prefix] = counts.get(prefix, 0) + 1

        sorted_namespaces = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:requested_top_n]
        return {
            "status": "ok",
            "scanned_keys": scan_result.scanned_keys,
            "truncated": scan_result.truncated,
            "namespaces": [{"prefix": prefix, "count": count} for prefix, count in sorted_namespaces],
        }

    @mcp.tool()
    def redis_keys(pattern: str = "adg:*", limit: int = 50) -> dict[str, Any]:
        """SCAN for keys matching a pattern. Uses SCAN, not KEYS.

        Args:
            pattern: Redis key pattern (for example 'adg:node:*', 'coord:*', '*').
            limit: Max keys to return (default 50, max 200).
        """
        safe_limit = max(0, min(limit, MAX_KEY_LIST_LIMIT))
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        scan_result = scan_keys(
            client,
            match=pattern,
            count=KEY_SCAN_COUNT,
            result_limit=safe_limit,
        )
        return {
            "status": "ok",
            "pattern": pattern,
            "count": len(scan_result.keys),
            "keys": scan_result.keys,
        }

    @mcp.tool()
    def redis_get(key: str) -> dict[str, Any]:
        """GET the value for a single key. Auto-detects type.

        Supports string, hash, list, set, and zset.
        """
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        key_type = client.type(key)
        if key_type == "none":
            return {"status": "not_found", "key": key}

        value, truncated, extra = _get_key_value(client, key, key_type)
        return {
            "status": "ok",
            "key": key,
            "type": key_type,
            "ttl_seconds": client.ttl(key),
            "value": value,
            "truncated": truncated,
            **extra,
        }

    @mcp.tool()
    def redis_hgetall(key: str) -> dict[str, Any]:
        """HGETALL for a hash key.

        Useful for ADG node cache entries and coordination fabric state.
        """
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        key_type = client.type(key)
        if key_type == "none":
            return {"status": "not_found", "key": key}
        if key_type != "hash":
            return {"status": "error", "error": f"Key '{key}' is type '{key_type}', not hash"}

        field_count = client.hlen(key)
        if field_count > MAX_HASH_FIELDS:
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
        """Return TTL remaining for a key.

        -1 means no expiry.
        -2 means not found.
        """
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        ttl = client.ttl(key)
        interpretation = "no_expiry" if ttl == -1 else ("not_found" if ttl == -2 else f"expires_in_{ttl}s")
        return {
            "status": "ok",
            "key": key,
            "ttl_seconds": ttl,
            "interpretation": interpretation,
        }

    @mcp.tool()
    def redis_stats() -> dict[str, Any]:
        """Return selected Redis INFO sections."""
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        info = client.info("all")
        sections = {
            "server": {
                key: info[key]
                for key in ("redis_version", "uptime_in_seconds", "tcp_port", "os", "hz")
                if key in info
            },
            "memory": {
                key: info[key]
                for key in (
                    "used_memory_human",
                    "used_memory_peak_human",
                    "used_memory_rss_human",
                    "mem_fragmentation_ratio",
                    "maxmemory_human",
                    "maxmemory_policy",
                )
                if key in info
            },
            "persistence": {
                key: info[key]
                for key in (
                    "rdb_last_save_time",
                    "rdb_last_bgsave_status",
                    "aof_enabled",
                    "loading",
                )
                if key in info
            },
            "replication": {
                key: info[key] for key in ("role", "connected_slaves", "master_replid") if key in info
            },
            "clients": {
                key: info[key]
                for key in ("connected_clients", "blocked_clients", "tracking_clients")
                if key in info
            },
            "stats": {
                key: info[key]
                for key in (
                    "total_commands_processed",
                    "total_connections_received",
                    "keyspace_hits",
                    "keyspace_misses",
                    "evicted_keys",
                    "expired_keys",
                )
                if key in info
            },
            "keyspace": {key: value for key, value in info.items() if key.startswith("db")},
        }
        return {"status": "ok", "sections": sections}
