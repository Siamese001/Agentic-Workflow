"""
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

import glob
import json
import logging
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

import redis as _redis_lib
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Diagnostic logging to stderr (visible in IDE logs, never pollutes stdio)
# ---------------------------------------------------------------------------
logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format="[adg_mcp %(levelname)s %(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
_log = logging.getLogger("adg_mcp")

# ---------------------------------------------------------------------------
# Configuration — all overridable via env vars
# ---------------------------------------------------------------------------
from tools.adg.shared_modules.path_resolver import get_adg_dir

_REDIS_URL: str = os.environ.get("ADG_REDIS_URL", "redis://localhost:6379/0")
_ADG_DIR: Path = get_adg_dir()
_PAGE_SIZE: int = int(os.environ.get("ADG_MCP_PAGE_SIZE", "500"))
_CACHE_META_TTL: float = float(os.environ.get("ADG_MCP_CACHE_META_TTL", "5"))

# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------
_log.info("Creating FastMCP instance...")
mcp = FastMCP(
    "adg-redis",
    instructions=(
        "ADG-aware Redis MCP. Supports HASH/SET/LIST operations and ADG-specific "
        "tools with built-in freshness validation. Use adg_status first."
    ),
)
_log.info("FastMCP instance created")

# ---------------------------------------------------------------------------
# Redis connection — lazy singleton, reconnects on demand
# ---------------------------------------------------------------------------
_r: _redis_lib.Redis | None = None


def _redis() -> _redis_lib.Redis:
    """Return a connected Redis client, reconnecting if necessary.

    Resets the singleton on ping failure so the next call reconnects
    rather than re-using a broken socket.
    """
    global _r
    if _r is None:
        _log.debug("Creating Redis connection to %s ...", _REDIS_URL)
        _r = _redis_lib.from_url(
            _REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        _log.debug("Redis client created")
    try:
        _log.debug("Pinging Redis...")
        _r.ping()
        _log.debug("Redis ping OK")
    except _redis_lib.RedisError as exc:
        _log.error("Redis ping failed: %s", exc)
        _r = None
        raise
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

        projection_coherent = status.get("projection_coherent", False)
        if isinstance(projection_coherent, str):
            projection_coherent = projection_coherent.lower() == "true"
        verdict_parts = []
        if is_fresh:
            verdict_parts.append("HOT")
        else:
            verdict_parts.append("STALE — run: python tools/adg/adg_redis_ingest.py --force")
        if not projection_coherent:
            verdict_parts.append("PROJECTION MISMATCH — re-ingest required")

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
                "projection_coherent": projection_coherent,
                "sqlite_digest": status.get("sqlite_digest", ""),
                "redis_digest": status.get("redis_digest", ""),
                "verdict": " | ".join(verdict_parts),
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
def adg_edge_fanout(
    src_id: str,
    relation_type: str,
    resolve: bool = True,
    limit: int = 200,
) -> dict[str, Any]:
    """Get all outgoing edges from a node (SMEMBERS adg:edge:<src>:<rel>).

    Adjacency sets store edge_ids (v2). If resolve=True (default), fetches
    full edge metadata via pipeline and extracts target node IDs.

    Args:
        src_id:        Source node ID
        relation_type: e.g. 'calls', 'imports', 'exports', 'invokes_dynamic',
                       'applies_guardrail', 'records_execution_trace'
        resolve:       Resolve edge_ids to full metadata (default True)
        limit:         Max edges to resolve (default 200)

    NOTE: adg:edge:* are SET type — mcp9_get returns WRONGTYPE on them.
    """
    key = f"adg:edge:{src_id}:{relation_type}"
    try:
        edge_ids = sorted(_redis().smembers(key))
        total = len(edge_ids)
        page = edge_ids[:limit]

        if resolve and page:
            pipe = _redis().pipeline(transaction=False)
            for eid in page:
                pipe.hgetall(f"adg:edge_detail:{eid}")
            details = pipe.execute()
            edges = []
            targets = []
            for eid, detail in zip(page, details):
                if detail:
                    edges.append(detail)
                    tgt = detail.get("dst_id", "")
                    if tgt and tgt not in targets:
                        targets.append(tgt)
            return _ok(
                {
                    "src_id": src_id,
                    "relation_type": relation_type,
                    "total_edge_count": total,
                    "returned": len(page),
                    "target_count": len(targets),
                    "targets": sorted(targets),
                    "edges": edges,
                }
            )
        return _ok(
            {
                "src_id": src_id,
                "relation_type": relation_type,
                "total_edge_count": total,
                "returned": len(page),
                "edge_ids": page,
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_edge_fanin(
    tgt_id: str,
    relation_type: str,
    resolve: bool = True,
    limit: int = 200,
) -> dict[str, Any]:
    """Get all incoming edges to a node (SMEMBERS adg:edge:in:<tgt>:<rel>).

    Adjacency sets store edge_ids (v2). If resolve=True (default), fetches
    full edge metadata via pipeline and extracts source node IDs.

    Args:
        tgt_id:        Target node ID
        relation_type: e.g. 'calls', 'imports'
        resolve:       Resolve edge_ids to full metadata (default True)
        limit:         Max edges to resolve (default 200)

    NOTE: adg:edge:in:* are SET type — mcp9_get returns WRONGTYPE on them.
    """
    key = f"adg:edge:in:{tgt_id}:{relation_type}"
    try:
        edge_ids = sorted(_redis().smembers(key))
        total = len(edge_ids)
        page = edge_ids[:limit]

        if resolve and page:
            pipe = _redis().pipeline(transaction=False)
            for eid in page:
                pipe.hgetall(f"adg:edge_detail:{eid}")
            details = pipe.execute()
            edges = []
            sources = []
            for eid, detail in zip(page, details):
                if detail:
                    edges.append(detail)
                    src = detail.get("src_id", "")
                    if src and src not in sources:
                        sources.append(src)
            return _ok(
                {
                    "tgt_id": tgt_id,
                    "relation_type": relation_type,
                    "total_edge_count": total,
                    "returned": len(page),
                    "source_count": len(sources),
                    "sources": sorted(sources),
                    "edges": edges,
                }
            )
        return _ok(
            {
                "tgt_id": tgt_id,
                "relation_type": relation_type,
                "total_edge_count": total,
                "returned": len(page),
                "edge_ids": page,
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_violations(
    limit: int = 200,
    offset: int = 0,
    category: str = "",
    severity: str = "",
) -> dict[str, Any]:
    """Get ADG anti-pattern violations from the hot cache (LRANGE adg:violations).

    v2: adg:violations LIST stores violation IDs. Full metadata is in
    adg:violation:<id> HASHes, resolved via pipeline.

    Args:
        limit:    Max violations to return (default 200, max 500). Use pagination
                  to avoid payload hangs — the full list can be 5000+ entries.
        offset:   Start index into the violations list (default 0).
        category: Optional filter — e.g. 'violates', 'antipattern'. Empty = all.
        severity: Optional filter — e.g. 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'. Empty = all.

    Returns list of violation dicts: id, file_path, category, severity, evidence, line_no.
    NOTE: adg:violations is a LIST — mcp9_get returns WRONGTYPE on it.
    """
    _MAX_LIMIT = 500
    limit = min(max(1, limit), _MAX_LIMIT)

    try:
        total_count = _redis().llen("adg:violations")
        if total_count == 0:
            return _ok({"total": 0, "offset": offset, "limit": limit, "count": 0, "violations": []})

        # Fetch a window — if filtering, over-fetch to fill limit after filtering
        fetch_end = offset + (limit * 4 if (category or severity) else limit) - 1
        fetch_end = min(fetch_end, total_count - 1)
        vid_list = _redis().lrange("adg:violations", offset, fetch_end)

        pipe = _redis().pipeline(transaction=False)
        for vid in vid_list:
            pipe.hgetall(f"adg:violation:{vid}")
        results = pipe.execute()

        violations = []
        for vid, detail in zip(vid_list, results):
            if detail:
                row = {
                    k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v
                    for k, v in detail.items()
                }
                if category and row.get("category", "") != category:
                    continue
                if severity and row.get("severity", "").upper() != severity.upper():
                    continue
                violations.append(row)
            else:
                # Backward compat: try parsing vid as JSON (old v1 format)
                # Skip if category/severity filter is active — raw stubs have no metadata
                if category or severity:
                    continue
                try:
                    parsed = json.loads(vid)
                    violations.append(parsed)
                except (json.JSONDecodeError, TypeError):
                    violations.append({"id": vid.decode() if isinstance(vid, bytes) else vid, "raw": True})
            if len(violations) >= limit:
                break

        return _ok(
            {
                "total": total_count,
                "offset": offset,
                "limit": limit,
                "count": len(violations),
                "violations": violations,
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_edge_detail(edge_id: str) -> dict[str, Any]:
    """Read full metadata for a single edge by its ID (HGETALL adg:edge_detail:<edge_id>).

    Zero-loss: every field from the SQLite edges table is preserved.
    Returns: id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol.

    Args:
        edge_id: Edge ID (integer stored as string), e.g. '12345'
    """
    key = f"adg:edge_detail:{edge_id}"
    try:
        edge = _redis().hgetall(key)
        if not edge:
            return _err(f"Edge '{edge_id}' not found in ADG cache", key=key)
        return _ok(edge)
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


@mcp.tool()
def adg_module_context(module_id: str) -> dict[str, Any]:
    """Get precomputed module context from Redis (zero fan-out, O(1) lookup).

    Returns: module metadata (layer, entity_type, resolved_path), edge counts
    by relation, neighbors by relation, context digest.

    This is the HOT PATH for module analysis — uses only precomputed Redis data.
    Must be derivable entirely from Redis WITHOUT fan-out calls.
    For provenance requiring SQLite evidence, use adg_source_context instead.

    Args:
        module_id: Module node ID (integer stored as string)
    """
    try:
        node = _redis().hgetall(f"adg:node:{module_id}")
        if not node:
            return _err(f"Module '{module_id}' not found in ADG cache")

        context_raw = _redis().get(f"adg:module_context:{module_id}")
        context_digest = _redis().get(f"adg:module_context_digest:{module_id}")

        if context_raw:
            context = json.loads(context_raw)
        else:
            context = {"edge_counts": {}, "neighbors": {}}

        return _ok(
            {
                "module_id": module_id,
                "layer": node.get("layer", ""),
                "entity_type": node.get("entity_type", ""),
                "resolved_path": node.get("resolved_path", ""),
                "adg_name": node.get("adg_name", ""),
                "edge_counts": context.get("edge_counts", {}),
                "neighbors": context.get("neighbors", {}),
                "context_digest": context_digest or "",
            }
        )
    except _redis_lib.RedisError as exc:
        return _err(f"Redis unavailable: {exc}")


def _get_sqlite_conn() -> sqlite3.Connection:
    """Get a connection to the latest ADG SQLite database."""
    candidates = sorted(
        glob.glob(str(_ADG_DIR / "adg_indexed_*.sqlite")),
        key=os.path.getmtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"No adg_indexed_*.sqlite in {_ADG_DIR}")
    conn = sqlite3.connect(candidates[0])
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def adg_source_context(edge_id: str) -> dict[str, Any]:
    """Pull provenance context for an edge from SQLite ONLY (not Redis).

    This is the JUDGE-SAFE escalation path. Any governance or evaluation
    pathway that requires provenance MUST use this tool, not Redis-only tools.

    Returns: edge metadata, source/target node names and types, layer info.

    Args:
        edge_id: Edge ID (integer stored as string), e.g. '12345'
    """
    try:
        conn = _get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT e.*, src.adg_name AS src_name, dst.adg_name AS dst_name, "
            "src.entity_type AS src_type, dst.entity_type AS dst_type, "
            "src.layer AS src_layer, dst.layer AS dst_layer "
            "FROM edges e "
            "JOIN nodes src ON src.id = e.src_id "
            "JOIN nodes dst ON dst.id = e.dst_id "
            "WHERE e.id = ?",
            (int(edge_id),),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return _err(f"Edge {edge_id} not found in SQLite", provenance="sqlite")
        result = {k: str(v) if v is not None else "" for k, v in dict(row).items()}
        return _ok(result, provenance="sqlite")
    except FileNotFoundError as exc:
        return _err(str(exc), provenance="sqlite")
    except Exception as exc:  # noqa: BLE001
        return _err(f"SQLite error: {exc}", provenance="sqlite")


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

    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access


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
    _log.info("Starting adg_mcp_server (stdio transport)...")
    mcp.run(transport="stdio")
    _log.info("Server exited")
