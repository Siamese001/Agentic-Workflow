"""ADG MCP Server — SQLite-first with optional Redis cache.

This server follows the hardened design:
- SQLite = mandatory canonical source (L4 authority)
- Redis = optional read-through cache only
- Clean transport, no import-time backend wiring
"""

from __future__ import annotations

import atexit
import hashlib
import logging
import os
import signal
import time
import uuid
from typing import Any

from mcp.server.fastmcp import FastMCP
from tools.adg.core.service import ADGService
from tools.adg.mcp.health import HealthDiagnostics

# ---------------------------------------------------------------------------
# Diagnostic logging to file (never pollutes stdio transport)
# ---------------------------------------------------------------------------
_log_file = os.path.expanduser("~/adg_mcp_server.log")
logging.basicConfig(filename=_log_file, level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
_log = logging.getLogger("adg_mcp")

# ---------------------------------------------------------------------------
# Process identity — set once at module load (i.e. true process start, not reconnect)
# ---------------------------------------------------------------------------
_STARTUP_TIME: float = time.time()
_STARTUP_NONCE: str = uuid.uuid4().hex[:12]  # unique per OS process spawn


# Fingerprint covers the full loaded server stack, not just this file.
# A changed fingerprint after restart proves dependency edits were picked up.
def _compute_stack_fingerprints() -> tuple[dict[str, str], str]:
    """Return per-file md5[:10] fingerprints and a combined fingerprint."""
    import pathlib

    _repo = pathlib.Path(__file__).resolve().parents[3]
    _files = {
        "server.py": __file__,
        "service.py": str(_repo / "tools/adg/core/service.py"),
        "sqlite_backend.py": str(_repo / "tools/adg/core/sqlite_backend.py"),
        "models.py": str(_repo / "tools/adg/core/models.py"),
    }
    per_file: dict[str, str] = {}
    combined = hashlib.md5()
    for label, path in _files.items():
        try:
            content = open(path, encoding="utf-8").read().encode()
        except OSError:
            content = b""
        digest = hashlib.md5(content).hexdigest()[:10]
        per_file[label] = digest
        combined.update(content)
    return per_file, combined.hexdigest()[:10]


_STACK_FINGERPRINTS, _COMBINED_FINGERPRINT = _compute_stack_fingerprints()

# ---------------------------------------------------------------------------
# Global service instance (initialized at startup, not import)
# ---------------------------------------------------------------------------
_service: ADGService | None = None
_health: HealthDiagnostics | None = None


def _init_service() -> ADGService:
    """Initialize ADGService with SQLite mandatory, Redis optional."""
    global _service, _health

    if _service is None:
        _log.info("Initializing ADGService...")
        _service = ADGService()
        _health = HealthDiagnostics(_service)
        _log.info("ADGService ready: %s", _service.health().mode)

    return _service


def _shutdown_service() -> None:
    """Gracefully shutdown ADGService and release all connections."""
    global _service, _health
    if _service:
        _log.info("Shutting down ADGService...")
        _service.close()
        _service = None
        _health = None
        _log.info("ADGService shutdown complete")


# Register shutdown handlers
atexit.register(_shutdown_service)
signal.signal(signal.SIGTERM, lambda sig, frame: _shutdown_service())
signal.signal(signal.SIGINT, lambda sig, frame: _shutdown_service())


# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------
_log.info("Creating FastMCP instance...")
mcp = FastMCP(
    "adg-sqlite",
    instructions=(
        "ADG SQLite-first MCP server. SQLite is canonical source, "
        "Redis is optional cache. Use adg_health first to check status."
    ),
)
_log.info("FastMCP instance created")


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def adg_health() -> dict[str, Any]:
    """PRIMARY health check — always call this first.

    Returns: mode, sqlite status, redis status, cache capability,
    schema version, ADG snapshot ID.
    """
    try:
        svc = _init_service()
        report = _health.full_report()
        return {"status": "ok", "data": report}
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Health check failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_status() -> dict[str, Any]:
    """Get ADG snapshot status.

    Returns: timestamp, node_count, edge_count, sqlite_path.
    """
    try:
        svc = _init_service()
        resp = svc.get_status()
        return {
            "status": resp.status,
            "data": resp.data,
            "backend_used": resp.backend_used,
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Status query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_node(node_id: str) -> dict[str, Any]:
    """Get node by ID.

    Tries Redis cache first (75ms timeout), falls back to SQLite.
    Returns node attributes with backend_used metadata.
    """
    try:
        svc = _init_service()
        resp = svc.get_node(node_id)
        return {
            "status": resp.status,
            "data": resp.data,
            "backend_used": resp.backend_used,
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Node query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_nodes_by_layer(layer: str, limit: int = 100) -> dict[str, Any]:
    """Get nodes by layer.

    SQLite-only query (lists not cached in Redis).
    """
    try:
        svc = _init_service()
        resp = svc.get_nodes_by_layer(layer, limit)
        return {
            "status": resp.status,
            "data": resp.data,
            "backend_used": resp.backend_used,
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Nodes by layer query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_nodes_by_file(file_path: str, limit: int = 100) -> dict[str, Any]:
    """Get nodes by file path.

    Tries Redis cache first (lazy warm on miss), falls back to SQLite.
    """
    try:
        svc = _init_service()
        resp = svc.get_nodes_by_file(file_path, limit)
        return {
            "status": resp.status,
            "data": resp.data,
            "backend_used": resp.backend_used,
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Nodes by file query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_find_node(name: str, limit: int = 10) -> dict[str, Any]:
    """Find nodes by adg_name — exact match first, then prefix match.

    Use this to resolve a human-readable ADG name (e.g.
    'ADG::Module::tools/adg/core/service.py') to a node id without
    needing the opaque integer id upfront.
    """
    try:
        svc = _init_service()
        resp = svc.find_node(name, limit)
        return {
            "status": resp.status,
            "data": resp.data,
            "backend_used": resp.backend_used,
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Find node query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_edge_fanout(src_id: str, relation_type: str, limit: int = 30) -> dict[str, Any]:
    """Get outgoing edges from src_id via relation_type.

    Tries Redis cache first, falls back to SQLite with cache backfill.
    """
    try:
        svc = _init_service()
        resp = svc.get_edge_fanout(src_id, relation_type, limit)
        return {
            "status": resp.status,
            "data": resp.data,
            "backend_used": resp.backend_used,
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Edge fanout query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_edge_fanin(tgt_id: str, relation_type: str, limit: int = 30) -> dict[str, Any]:
    """Get incoming edges to tgt_id via relation_type.

    Tries Redis cache first (lazy warm on miss), falls back to SQLite.
    """
    try:
        svc = _init_service()
        resp = svc.get_edge_fanin(tgt_id, relation_type, limit)
        return {
            "status": resp.status,
            "data": resp.data,
            "backend_used": resp.backend_used,
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Edge fanin query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_violations(limit: int = 100) -> dict[str, Any]:
    """Get anti-pattern violations.

    SQLite-only query.
    """
    try:
        svc = _init_service()
        resp = svc.get_violations(limit)
        return {
            "status": resp.status,
            "data": resp.data,
            "backend_used": resp.backend_used,
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Violations query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_close_connections() -> dict[str, Any]:
    """Close ADG backend connections to release SQLite file locks without restarting IDE.

    Use this before running full ADG generation when lock checks report files in use.
    Connections can be reopened with adg_reopen_connections() or automatically on next query.
    """
    global _service, _health
    try:
        if _service is None:
            return {
                "status": "ok",
                "data": {
                    "closed": False,
                    "message": "No active ADG service instance to close.",
                },
            }

        _service.close()
        _service = None
        _health = None
        return {
            "status": "ok",
            "data": {
                "closed": True,
                "message": "ADG connections closed. SQLite file locks released.",
            },
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Close connections failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_reopen_connections() -> dict[str, Any]:
    """Reopen ADG backend connections after adg_close_connections()."""
    try:
        svc = _init_service()
        svc.reopen()
        return {
            "status": "ok",
            "data": {
                "reopened": True,
                "message": "ADG connections reopened.",
            },
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Reopen connections failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_runtime_info() -> dict[str, Any]:
    """Return process-level runtime identity for verifying restarts.

    Returns pid, startup_nonce (unique per OS process spawn, not per reconnect),
    source_fingerprint (md5 of server.py at load time), sqlite_path, snapshot_id.
    A changed pid or nonce after a Windsurf MCP restart proves a fresh process
    is serving. Use adg_reload for SQLite snapshot/data refresh only.
    """
    import datetime

    try:
        svc = _init_service()
        h = svc.health()
        _, sqlite_meta = svc._sqlite.health()
        return {
            "status": "ok",
            "data": {
                "pid": os.getpid(),
                "startup_time": datetime.datetime.fromtimestamp(_STARTUP_TIME).isoformat(),
                "startup_nonce": _STARTUP_NONCE,
                "stack_fingerprints": _STACK_FINGERPRINTS,
                "combined_fingerprint": _COMBINED_FINGERPRINT,
                "sqlite_path": sqlite_meta.get("path"),
                "snapshot_id": h.adg_snapshot_id,
                "redis_enabled": h.cache_hit_capable,
            },
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Runtime info failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_reload() -> dict[str, Any]:
    """Auto-reload ADG SQLite snapshot if a newer file exists on disk.

    DATA RELOAD ONLY — repoints the connection to the latest snapshot file.
    This does NOT restart the server process or reload edited source code.
    To pick up code changes, restart the MCP server via Windsurf MCP Settings.

    Checks if the current snapshot is stale and reloads to the latest one.
    Returns status indicating whether reload occurred or was unnecessary.
    """
    try:
        svc = _init_service()
        # HealthStatus is a Pydantic BaseModel, not a NamedTuple — use _sqlite.health()
        # directly to get the stale/path metadata that lives in the SQLite backend.
        _sqlite_status, sqlite_meta = svc._sqlite.health()

        is_stale = sqlite_meta.get("is_stale", False)
        current_path = sqlite_meta.get("path")
        latest_path = sqlite_meta.get("latest_path")

        if not is_stale:
            return {
                "status": "ok",
                "data": {
                    "reloaded": False,
                    "message": "Already using latest snapshot.",
                    "current_path": current_path,
                    "redis_cleared": False,
                },
            }

        # Capture old snapshot id before reopen so we can clean Redis
        old_snapshot_id = svc._adg_snapshot_id

        # Reload to latest snapshot
        _log.info(f"Reloading ADG from {current_path} to {latest_path}")
        svc.reopen()

        # Verify reload
        _sqlite_status_new, new_meta = svc._sqlite.health()
        new_snapshot_id = svc._adg_snapshot_id

        # Clear old Redis snapshot keys to free memory and prevent stale-key confusion.
        # Best-effort — reload must succeed even if Redis clear fails.
        redis_cleared = False
        if old_snapshot_id != new_snapshot_id and svc._redis._available:
            try:
                svc._redis.clear_snapshot(old_snapshot_id)
                redis_cleared = True
                _log.info("Cleared Redis keys for old snapshot %s", old_snapshot_id)
            except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: Redis clear is best-effort; reload succeeds regardless
                _log.warning("Redis clear_snapshot failed for %s: %s", old_snapshot_id, e)

        return {
            "status": "ok",
            "data": {
                "reloaded": True,
                "message": "Reloaded to latest snapshot.",
                "old_path": current_path,
                "new_path": new_meta.get("path"),
                "old_snapshot_id": old_snapshot_id,
                "new_snapshot_id": new_snapshot_id,
                "redis_cleared": redis_cleared,
                "redis_cache_state": "cleared_old_snapshot" if redis_cleared else "cold",
            },
        }
    except Exception as e:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        _log.error("Auto-reload failed: %s", e)
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
# Wire into mcp_config.json:
#
#   "adg_sqlite": {
#     "command": "python",
#     "args": ["-m", "tools.adg.mcp.server"],
#     "cwd": "C:\\Git\\Agentic-Workflow",
#     "disabled": false
#   }
#
# Then disable (or remove) the old "adg_redis" entry:
#   "adg_redis": { ..., "disabled": true }
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Lazy init - don't block startup
    mcp.run(transport="stdio")
