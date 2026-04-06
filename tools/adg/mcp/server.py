"""ADG MCP Server — SQLite-first with optional Redis cache.

This server follows the hardened design:
- SQLite = mandatory canonical source (L4 authority)
- Redis = optional read-through cache only
- Clean transport, no import-time backend wiring
"""

from __future__ import annotations

import atexit
import logging
import os
import signal
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

    SQLite-only query.
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

    SQLite-only query.
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
