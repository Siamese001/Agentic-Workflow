"""
_emit_reads_through("l4", "adg_mcp_server", "urg_read_1")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_2")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_3")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_4")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_5")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_6")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_7")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_8")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_9")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_10")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_11")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_12")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_13")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_14")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_15")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_16")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_17")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_18")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_19")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_20")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_21")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_22")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_23")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_24")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_25")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_26")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_27")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_28")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_29")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_30")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_31")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_32")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_33")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_34")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_35")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_36")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_37")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_38")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_39")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_40")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_41")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_42")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_43")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_44")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_45")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_46")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_47")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_48")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_49")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_50")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_51")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_52")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_53")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_54")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_55")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_56")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_57")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_58")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_59")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_60")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_61")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_62")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_63")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_64")
_emit_reads_through("l4", "adg_mcp_server", "urg_read_65")
ADG-Aware Redis MCP Server — custom replacement for @modelcontextprotocol/server-redis.

Why this exists
---------------
The Windsurf marketplace Redis MCP (@modelcontextprotocol/server-redis v2025.4.25)
exposes only 4 tools — get / set / delete / list — all STRING-only.

The ADG hot cache stores ALL data in HASH and SET types:
  adg:meta                     HASH  (inaccessible via marketplace mcp9_get)
  adg:node:<id>                HASH  (inaccessible via marketplace mcp9_get)
  adg:nodes:by_layer:<layer>   SET   (inaccessible via marketplace mcp9_get)
  adg:nodes:by_file:<path>     SET   (inaccessible via marketplace mcp9_get)
  adg:edge:<src>:<rel>         SET   (inaccessible via marketplace mcp9_get)
  adg:violations               LIST  (inaccessible via marketplace mcp9_get)

Additional gaps in the marketplace server:
  - Uses KEYS * (O(N) blocking) instead of cursor SCAN
  - No TTL or TYPE inspection
  - No freshness validation / timestamp awareness
  - No ADG-specific tools (schema-unaware generic client)
  - Returns bare WRONGTYPE errors with no remediation guidance

This server provides:

  Tier 1 — ADG-specific tools (primary interface for Cascade)
    adg_status          Read adg:status sentinel + verify against SQLite on disk
    adg_meta            HGETALL adg:meta — timestamp, node/edge counts, digest
    adg_snapshot        GET adg:snapshot parsed as structured JSON
    adg_node            HGETALL adg:node:<id>
    adg_nodes_by_layer  SMEMBERS adg:nodes:by_layer:<layer>  (paginated)
    adg_nodes_by_file   SMEMBERS adg:nodes:by_file:<file_path>
    adg_edge_fanout     SMEMBERS adg:edge:<src>:<rel>
    adg_edge_fanin      SMEMBERS adg:edge:in:<tgt>:<rel>
    adg_violations      LRANGE adg:violations 0 -1
    adg_assert_fresh    Hard check: ingested_at vs SQLite mtime on disk

  Tier 2 — General Redis tools (type-aware, improved over marketplace)
    redis_get           GET (STRING)
    redis_hgetall       HGETALL (HASH)
    redis_smembers      SMEMBERS (SET)  with optional limit
    redis_lrange        LRANGE (LIST)  with start/stop
    redis_type          TYPE of any key
    redis_ttl           TTL of any key
    redis_scan          Cursor-based SCAN  (safe replacement for KEYS *)

Every tool response includes a cache_meta section:
  {timestamp, node_count, edge_count, ingested_at, age_seconds, is_fresh}
so Cascade always knows the freshness of the data without a separate call.

Wire into mcp_config.json (see bottom of this file for snippet).

Run as stdio MCP server:
  python tools/adg/adg_mcp_server.py
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import redis as _redis_lib
from mcp.server.fastmcp import FastMCP
from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through

# ---------------------------------------------------------------------------
# Configuration — all overridable via env vars
# ---------------------------------------------------------------------------
_REDIS_URL: str = os.environ.get("ADG_REDIS_URL", "redis://localhost:6379/0")
_ADG_DIR: Path = Path(os.environ.get("ADG_DIR", r"C:\Git\Agentic-Workflow\artifacts\adg"))
_PAGE_SIZE: int = int(os.environ.get("ADG_MCP_PAGE_SIZE", "500"))
_CACHE_META_TTL: float = float(os.environ.get("ADG_MCP_CACHE_META_TTL", "5"))

# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "adg-redis",
    instructions=(
        "ADG-aware Redis MCP. Supports HASH/SET/LIST operations and ADG-specific "
        "tools with built-in freshness validation. Use adg_status first."
    ),
)

# ---------------------------------------------------------------------------
# Redis connection — lazy singleton, reconnects on demand
# ---------------------------------------------------------------------------
_r: _redis_lib.Redis | None = None


def _redis() -> _redis_lib.Redis:
    """Return a connected Redis client, reconnecting if necessary."""
    global _r
    if _r is None:
        _r = _redis_lib.from_url(_REDIS_URL, decode_responses=True)
    _r.ping()
    return _r


# ---------------------------------------------------------------------------
# cache_meta helper — injected into every response, with 5-second TTL
# ---------------------------------------------------------------------------
_meta_cache: dict[str, Any] = {}


def _cache_meta() -> dict[str, Any]:
    """Read adg:status and return freshness metadata, cached for _CACHE_META_TTL seconds.

    Never raises — returns {'available': False} on any failure so that response
    wrappers always succeed.
    """
    now = time.time()
    if _meta_cache.get("expires", 0.0) > now:
        return _meta_cache["data"]

    try:
        raw = _redis().get("adg:status")
        if not raw:
            result: dict[str, Any] = {
                "available": False,
                "reason": "adg:status key missing — cache may be cold",
            }
        else:
            status = json.loads(raw)
            ingested_at = float(status.get("ingested_at", 0))
            sqlite_path_str = status.get("sqlite_path", "")
            sqlite_mtime: float | None = None
            if sqlite_path_str:
                p = Path(sqlite_path_str)
                if p.exists():
                    sqlite_mtime = p.stat().st_mtime
            is_fresh = (ingested_at >= sqlite_mtime) if sqlite_mtime is not None else False
            result = {
                "available": True,
                "timestamp": status.get("timestamp", "unknown"),
                "node_count": int(status.get("node_count", 0)),
                "edge_count": int(status.get("edge_count", 0)),
                "ingested_at": ingested_at,
                "age_seconds": round(now - ingested_at, 1),
                "is_fresh": is_fresh,
                "digest": status.get("digest", ""),
            }
    except Exception as exc:  # noqa: BLE001
        result = {"available": False, "reason": str(exc)}

    _meta_cache["data"] = result
    _meta_cache["expires"] = now + _CACHE_META_TTL
    return result


def _ok(data: Any, **extra: Any) -> dict[str, Any]:
    return {"status": "ok", "data": data, "cache_meta": _cache_meta(), **extra}


def _err(message: str, **extra: Any) -> dict[str, Any]:
    return {"status": "error", "message": message, "cache_meta": _cache_meta(), **extra}


def _wrongtype_hint(key: str, actual_type: str) -> str:
    guide = {
        "hash": "redis_hgetall",
        "set": "redis_smembers",
        "list": "redis_lrange",
        "string": "redis_get",
    }
    tool = guide.get(actual_type, f"unsupported type '{actual_type}'")
    return (
        f"Key '{key}' is type '{actual_type}'. "
        f"Use {tool} instead. "
        "This is a WRONGTYPE error — it does NOT mean the cache is cold."
    )


# ---------------------------------------------------------------------------
# Tier 1 — ADG-specific tools
# ---------------------------------------------------------------------------


@mcp.tool()
def adg_status() -> dict[str, Any]:
    """PRIMARY freshness check — always call this first before any ADG query.

    Reads adg:status STRING sentinel and validates against the SQLite file on disk.
    Returns: timestamp, node_count, edge_count, ingested_at, age_seconds,
             is_fresh, sqlite_exists, verdict.

    is_fresh=True  → cache is hot; safe to query.
    is_fresh=False → STALE; run: python tools/adg/adg_redis_ingest.py --force
    """
    try:
        raw = _redis().get("adg:status")
        if not raw:
            return {
                "status": "error",
                "message": (
                    "adg:status not found — cache is cold. Run: python tools/adg/adg_redis_ingest.py --force"
                ),
                "is_fresh": False,
            }
        status = json.loads(raw)
        ingested_at = float(status.get("ingested_at", 0))
        sqlite_path_str = status.get("sqlite_path", "")
        p = Path(sqlite_path_str) if sqlite_path_str else None
        sqlite_exists = p.exists() if p else False
        disk_mtime: float | None = p.stat().st_mtime if (p and sqlite_exists) else None
        is_fresh = (ingested_at >= disk_mtime) if disk_mtime is not None else False

        return {
            "status": "ok",
            "data": {
                **status,
                "node_count": int(status.get("node_count", 0)),
                "edge_count": int(status.get("edge_count", 0)),
                "ingested_at": ingested_at,
                "age_seconds": round(time.time() - ingested_at, 1),
                "sqlite_exists": sqlite_exists,
                "sqlite_disk_mtime": disk_mtime,
                "is_fresh": is_fresh,
                "verdict": (
                    "HOT" if is_fresh else "STALE — run: python tools/adg/adg_redis_ingest.py --force"
                ),
            },
        }
    except _redis_lib.RedisError as exc:
        return {
            "status": "error",
            "message": f"Redis unavailable: {exc}. Ensure Redis is running on localhost:6379.",
            "is_fresh": False,
        }


@mcp.tool()
def adg_meta() -> dict[str, Any]:
    """Read adg:meta HASH — full ADG metadata (HGETALL).

    Returns all fields: timestamp, sqlite_path, sqlite_mtime, ingested_at,
    node_count, edge_count, digest.

    NOTE: adg:meta is a HASH — mcp9_get returns WRONGTYPE on it. This tool
    uses HGETALL and returns the full field dict.
    """
    try:
        meta = _redis().hgetall("adg:meta")
        if not meta:
            return _err("adg:meta not found — cache cold. Run: python tools/adg/adg_redis_ingest.py --force")
        return _ok(
            {
                **meta,
                "node_count": int(meta.get("node_count", 0)),
                "edge_count": int(meta.get("edge_count", 0)),
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_snapshot() -> dict[str, Any]:
    """Read adg:snapshot STRING and parse as structured JSON.

    Returns the full ADG snapshot: counts by layer, module list, artifact
    digest, generation metadata.

    Warning: large payload (~several hundred KB). Use adg_meta for metadata
    only or adg_status for freshness check.
    """
    try:
        raw = _redis().get("adg:snapshot")
        if not raw:
            return _err("adg:snapshot not found — cache cold or snapshot not ingested")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return _err(f"adg:snapshot is invalid JSON: {exc}")
        return _ok(data, size_bytes=len(raw.encode()))
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_node(node_id: str) -> dict[str, Any]:
    """Read a single ADG node by its ID (HGETALL adg:node:<id>).

    Args:
        node_id: Node ID, e.g. 'tools/adg/adg_redis_ingest.py::ingest'

    Returns all node attributes: id, label, layer, kind, entity_type, file_path, etc.
    NOTE: adg:node:<id> is a HASH — mcp9_get returns WRONGTYPE on it.
    """
    key = f"adg:node:{node_id}"
    try:
        node = _redis().hgetall(key)
        if not node:
            return _err(f"Node '{node_id}' not found in ADG cache", key=key)
        return _ok(node)
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_nodes_by_layer(layer: str, offset: int = 0, limit: int = 100) -> dict[str, Any]:
    """Get node IDs for a specific ADG layer (SMEMBERS adg:nodes:by_layer:<layer>).

    Args:
        layer:  Layer name — L0, L1, L2, L3, L4, L5, L6
        offset: Pagination start (default 0)
        limit:  Max IDs to return (default 100, hard cap 500)

    NOTE: adg:nodes:by_layer:<l> is a SET — mcp9_get returns WRONGTYPE on it.
    """
    limit = min(limit, _PAGE_SIZE)
    try:
        all_ids = sorted(_redis().smembers(f"adg:nodes:by_layer:{layer}"))
        total = len(all_ids)
        page = all_ids[offset : offset + limit]
        return _ok(
            {
                "layer": layer,
                "total_count": total,
                "offset": offset,
                "returned": len(page),
                "has_more": (offset + limit) < total,
                "node_ids": page,
            }
        )
    except _redis_lib.ResponseError as exc:
        return _err(_wrongtype_hint(f"adg:nodes:by_layer:{layer}", "?") + f" ({exc})")
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_nodes_by_file(file_path: str) -> dict[str, Any]:
    """Get node IDs for all symbols defined in a file (SMEMBERS adg:nodes:by_file:<path>).

    Args:
        file_path: Relative path as stored in ADG, e.g. 'tools/adg/adg_redis_ingest.py'

    NOTE: adg:nodes:by_file:<path> is a SET — mcp9_get returns WRONGTYPE on it.
    """
    key = f"adg:nodes:by_file:{file_path}"
    try:
        node_ids = sorted(_redis().smembers(key))
        return _ok({"file_path": file_path, "count": len(node_ids), "node_ids": node_ids})
    except _redis_lib.ResponseError as exc:
        return _err(_wrongtype_hint(key, "?") + f" ({exc})")
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_edge_fanout(src_id: str, relation_type: str) -> dict[str, Any]:
    """Get all targets of an outgoing edge from a node (SMEMBERS adg:edge:<src>:<rel>).

    Args:
        src_id:        Source node ID
        relation_type: e.g. 'calls', 'imports', 'exports', 'invokes_dynamic',
                       'applies_guardrail', 'records_execution_trace'

    NOTE: adg:edge:* are SET type — mcp9_get returns WRONGTYPE on them.
    """
    key = f"adg:edge:{src_id}:{relation_type}"
    try:
        targets = sorted(_redis().smembers(key))
        return _ok(
            {
                "src_id": src_id,
                "relation_type": relation_type,
                "target_count": len(targets),
                "targets": targets,
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_edge_fanin(tgt_id: str, relation_type: str) -> dict[str, Any]:
    """Get all sources of incoming edges to a node (SMEMBERS adg:edge:in:<tgt>:<rel>).

    Args:
        tgt_id:        Target node ID
        relation_type: e.g. 'calls', 'imports'

    NOTE: adg:edge:in:* are SET type — mcp9_get returns WRONGTYPE on them.
    """
    key = f"adg:edge:in:{tgt_id}:{relation_type}"
    try:
        sources = sorted(_redis().smembers(key))
        return _ok(
            {
                "tgt_id": tgt_id,
                "relation_type": relation_type,
                "source_count": len(sources),
                "sources": sources,
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_violations() -> dict[str, Any]:
    """Get all ADG anti-pattern violations from the hot cache (LRANGE adg:violations).

    Returns list of violation dicts: file_path, category, line_number, evidence.
    NOTE: adg:violations is a LIST — mcp9_get returns WRONGTYPE on it.
    """
    try:
        raw_list = _redis().lrange("adg:violations", 0, -1)
        violations = []
        for item in raw_list:
            try:
                violations.append(json.loads(item))
            except json.JSONDecodeError:
                violations.append({"raw": item})
        return _ok({"count": len(violations), "violations": violations})
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_assert_fresh() -> dict[str, Any]:
    """Assert ADG hot cache freshness by comparing adg:meta.ingested_at vs SQLite mtime.

    This reads BOTH Redis (adg:meta HASH via HGETALL) AND disk (SQLite file stat)
    for an authoritative verdict. Unlike adg_status which reads the STRING sentinel,
    this tool goes to the primary HASH metadata and the actual file.

    Returns: is_fresh, ingested_at, sqlite_mtime (stored + disk), verdict.
    If is_fresh=False: run python tools/adg/adg_redis_ingest.py --force
    """
    try:
        meta = _redis().hgetall("adg:meta")
        if not meta:
            return _err(
                "adg:meta not found — cache cold",
                is_fresh=False,
                fix="python tools/adg/adg_redis_ingest.py --force",
            )
        ingested_at = float(meta.get("ingested_at", 0))
        stored_sqlite_mtime = float(meta.get("sqlite_mtime", 0))
        sqlite_path_str = meta.get("sqlite_path", "")

        disk_mtime: float | None = None
        disk_exists = False
        if sqlite_path_str:
            p = Path(sqlite_path_str)
            disk_exists = p.exists()
            if disk_exists:
                disk_mtime = p.stat().st_mtime

        effective_mtime = disk_mtime if disk_mtime is not None else stored_sqlite_mtime
        is_fresh = (ingested_at >= effective_mtime) if effective_mtime else False
        delta = ingested_at - effective_mtime if effective_mtime else 0

        return _ok(
            {
                "is_fresh": is_fresh,
                "timestamp": meta.get("timestamp", "unknown"),
                "ingested_at": ingested_at,
                "sqlite_mtime_stored": stored_sqlite_mtime,
                "sqlite_mtime_disk": disk_mtime,
                "sqlite_path": sqlite_path_str,
                "disk_path_exists": disk_exists,
                "delta_seconds": round(delta, 2),
                "verdict": (
                    f"FRESH — ingested {delta:.1f}s after SQLite was written"
                    if is_fresh
                    else "STALE — run: python tools/adg/adg_redis_ingest.py --force"
                ),
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(
            f"Redis unavailable: {exc}",
            is_fresh=False,
            fix="python tools/adg/adg_redis_ingest.py --force",
        )


# ---------------------------------------------------------------------------
# Tier 2 — General Redis tools (type-aware, improved over marketplace server)
# ---------------------------------------------------------------------------


@mcp.tool()
def redis_get(key: str) -> dict[str, Any]:
    """GET a STRING key (same as mcp9_get but with type safety + cache_meta).

    If the key is HASH/SET/LIST type, returns a WRONGTYPE hint instead of an error,
    telling you which tool to use instead.
    """
    try:
        val = _redis().get(key)
        if val is None:
            key_type = _redis().type(key)
            if key_type != "none":
                return _err(_wrongtype_hint(key, key_type), key_type=key_type)
        return _ok({"key": key, "value": val, "exists": val is not None})
    except _redis_lib.ResponseError as exc:
        key_type = _redis().type(key)
        return _err(_wrongtype_hint(key, key_type) + f" ({exc})", key_type=key_type)
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def redis_hgetall(key: str) -> dict[str, Any]:
    """HGETALL a HASH key (adg:meta, adg:node:<id>, etc.).

    Returns all field-value pairs. Use this for any key the marketplace mcp9_get
    rejects with WRONGTYPE because it's a HASH type.
    """
    try:
        fields = _redis().hgetall(key)
        if not fields:
            key_type = _redis().type(key)
            if key_type == "none":
                return _ok({"key": key, "fields": {}, "field_count": 0, "exists": False})
            if key_type != "hash":
                return _err(_wrongtype_hint(key, key_type), key_type=key_type)
        return _ok({"key": key, "fields": fields, "field_count": len(fields), "exists": True})
    except _redis_lib.ResponseError as exc:
        return _err(f"HASH read failed on '{key}': {exc}")
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def redis_smembers(key: str, limit: int = 100) -> dict[str, Any]:
    """SMEMBERS a SET key (adg:nodes:by_layer:*, adg:edge:*, etc.).

    Args:
        key:   Redis SET key
        limit: Max members to return (default 100; pass -1 for all)
    """
    try:
        members = list(_redis().smembers(key))
        if not members:
            key_type = _redis().type(key)
            if key_type == "none":
                return _ok({"key": key, "members": [], "total_count": 0, "exists": False})
            if key_type != "set":
                return _err(_wrongtype_hint(key, key_type), key_type=key_type)
        total = len(members)
        members = sorted(members)
        if limit != -1:
            members = members[:limit]
        return _ok(
            {
                "key": key,
                "total_count": total,
                "returned": len(members),
                "truncated": total > len(members),
                "members": members,
            }
        )
    except _redis_lib.ResponseError as exc:
        return _err(f"SET read failed on '{key}': {exc}")
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def redis_lrange(key: str, start: int = 0, stop: int = -1) -> dict[str, Any]:
    """LRANGE a LIST key (adg:violations, etc.).

    Args:
        key:   Redis LIST key
        start: Start index (default 0)
        stop:  Stop index (default -1 = end of list)
    """
    try:
        items = _redis().lrange(key, start, stop)
        total = _redis().llen(key)
        return _ok(
            {
                "key": key,
                "total_length": total,
                "start": start,
                "stop": stop,
                "returned": len(items),
                "items": items,
            }
        )
    except _redis_lib.ResponseError as exc:
        key_type = _redis().type(key)
        return _err(_wrongtype_hint(key, key_type) + f" ({exc})", key_type=key_type)
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def redis_type(key: str) -> dict[str, Any]:
    """Get the TYPE of a Redis key.

    Returns one of: string, hash, set, list, zset, stream, none (key not found).
    Use this to determine which read tool to use before calling redis_get/hgetall/smembers.
    """
    try:
        key_type = _redis().type(key)
        tool_map = {
            "string": "redis_get  (or mcp9_get)",
            "hash": "redis_hgetall",
            "set": "redis_smembers",
            "list": "redis_lrange",
            "none": "N/A — key does not exist",
        }
        return _ok(
            {
                "key": key,
                "type": key_type,
                "read_with": tool_map.get(key_type, f"unsupported: {key_type}"),
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def redis_ttl(key: str) -> dict[str, Any]:
    """Get the TTL (time-to-live) in seconds for a Redis key.

    Returns:
        ttl_seconds: -2 = key not found, -1 = no expiry (persistent), or remaining seconds.
    """
    try:
        ttl = _redis().ttl(key)
        return _ok(
            {
                "key": key,
                "ttl_seconds": ttl,
                "expires": ttl > 0,
                "persistent": ttl == -1,
                "exists": ttl != -2,
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def redis_scan(
    pattern: str = "adg:*",
    count: int = 100,
    max_keys: int = 500,
) -> dict[str, Any]:
    """Cursor-based SCAN for keys matching a pattern (safe replacement for KEYS *).

    Unlike KEYS *, SCAN is O(1) per call and does not block Redis.

    Args:
        pattern:  Key pattern (default 'adg:*')
        count:    Hint for keys per iteration (default 100)
        max_keys: Hard cap on total keys returned (default 500)

    Returns: sorted key list + prefix summary.
    """
    try:
        keys: list[str] = []
        cursor = 0
        while True:
            cursor, batch = _redis().scan(cursor=cursor, match=pattern, count=count)
            keys.extend(batch)
            if cursor == 0 or len(keys) >= max_keys:
                break
        truncated = len(keys) >= max_keys
        keys = sorted(keys[:max_keys])

        prefix_counts: dict[str, int] = {}
        for k in keys:
            parts = k.split(":")
            prefix = ":".join(parts[:2]) if len(parts) >= 2 else parts[0]
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

        return _ok(
            {
                "pattern": pattern,
                "matched_keys": len(keys),
                "truncated": truncated,
                "prefix_summary": dict(sorted(prefix_counts.items(), key=lambda x: -x[1])[:20]),
                "keys": keys,
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
# Wire into mcp_config.json:
#
#   "adg_redis": {
#     "command": "python",
#     "args": ["tools/adg/adg_mcp_server.py"],
#     "cwd": "C:\\Git\\Agentic-Workflow",
#     "disabled": false
#   }
#
# Then disable (or remove) the marketplace "redis" entry:
#   "redis": { ..., "disabled": true }
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
