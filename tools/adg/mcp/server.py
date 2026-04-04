"""ADG MCP Server — SQLite-first with optional Redis cache.

This server follows the hardened design:
- SQLite = mandatory canonical source (L4 authority)
- Redis = optional read-through cache only
- Clean transport, no import-time backend wiring
"""
from __future__ import annotations

import json
import logging
import sys
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from tools.adg.core.service import ADGService
from tools.adg.mcp.health import HealthDiagnostics

# ---------------------------------------------------------------------------
# Diagnostic logging to stderr (visible in IDE logs, never pollutes stdio)
# ---------------------------------------------------------------------------
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[adg_mcp %(levelname)s %(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
_log = logging.getLogger("adg_mcp")

# ---------------------------------------------------------------------------
# Global service instance (initialized at startup, not import)
# ---------------------------------------------------------------------------
_service: Optional[ADGService] = None
_health: Optional[HealthDiagnostics] = None


def _init_service() -> ADGService:
    """Initialize ADGService with SQLite mandatory, Redis optional."""
    global _service, _health
    
    if _service is None:
        _log.info("Initializing ADGService...")
        _service = ADGService()
        _health = HealthDiagnostics(_service)
        _log.info("ADGService ready: %s", _service.health().mode)
    
    return _service


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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
        _log.error("Nodes by file query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_edge_fanout(src_id: str, relation_type: str, 
                    limit: int = 30) -> dict[str, Any]:
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
    except Exception as e:
        _log.error("Edge fanout query failed: %s", e)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def adg_edge_fanin(tgt_id: str, relation_type: str,
                   limit: int = 30) -> dict[str, Any]:
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
    except Exception as e:
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
    except Exception as e:
        _log.error("Violations query failed: %s", e)
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
    _log.info("Starting adg_mcp server (stdio transport)...")
    
    # Pre-initialize service to fail fast if SQLite missing
    try:
        _init_service()
    except Exception as e:
        _log.error("FATAL: Could not initialize ADGService: %s", e)
        sys.exit(1)
    
    mcp.run(transport="stdio")
    _log.info("Server exited")
