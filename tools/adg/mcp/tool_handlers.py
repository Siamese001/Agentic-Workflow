"""Tool implementations for the ADG SQLite MCP server."""

from __future__ import annotations

from typing import Any, Callable

from tools.adg.mcp.runtime import LOG, runtime
from tools.adg.mcp.validators import require_non_empty_str, require_positive_limit

JsonDict = dict[str, Any]
Operation = Callable[[], JsonDict]


def _run_tool(error_label: str, operation: Operation) -> JsonDict:
    """Run a tool action and convert uncaught failures into MCP-safe error objects."""
    try:
        return operation()
    except Exception as exc:  # guardian: allow-broad-exception -- MCP tool resilience: log error and return error object to prevent server crash
        LOG.error("%s failed: %s", error_label, exc)
        return {"status": "error", "message": str(exc)}


def adg_health() -> JsonDict:
    """PRIMARY health check. Always call this first."""

    def operation() -> JsonDict:
        report = runtime.diagnostics.full_report()
        return {"status": "ok", "data": report}

    return _run_tool("Health check", operation)


def adg_status() -> JsonDict:
    """Get ADG snapshot status."""

    def operation() -> JsonDict:
        response = runtime.service.get_status()
        return {
            "status": response.status,
            "data": response.data,
            "backend_used": response.backend_used,
        }

    return _run_tool("Status query", operation)


def adg_node(node_id: str) -> JsonDict:
    """Get node by ID."""

    def operation() -> JsonDict:
        cleaned_node_id = require_non_empty_str("node_id", node_id)
        response = runtime.service.get_node(cleaned_node_id)
        return {
            "status": response.status,
            "data": response.data,
            "backend_used": response.backend_used,
        }

    return _run_tool("Node query", operation)


def adg_nodes_by_layer(layer: str, limit: int = 100) -> JsonDict:
    """Get nodes by layer."""

    def operation() -> JsonDict:
        cleaned_layer = require_non_empty_str("layer", layer)
        cleaned_limit = require_positive_limit(limit)
        response = runtime.service.get_nodes_by_layer(cleaned_layer, cleaned_limit)
        return {
            "status": response.status,
            "data": response.data,
            "backend_used": response.backend_used,
        }

    return _run_tool("Nodes by layer query", operation)


def adg_nodes_by_file(file_path: str, limit: int = 100) -> JsonDict:
    """Get nodes by file path."""

    def operation() -> JsonDict:
        cleaned_file_path = require_non_empty_str("file_path", file_path)
        cleaned_limit = require_positive_limit(limit)
        response = runtime.service.get_nodes_by_file(cleaned_file_path, cleaned_limit)
        return {
            "status": response.status,
            "data": response.data,
            "backend_used": response.backend_used,
        }

    return _run_tool("Nodes by file query", operation)


def adg_find_node(name: str, limit: int = 10) -> JsonDict:
    """Find nodes by human-readable ADG name."""

    def operation() -> JsonDict:
        cleaned_name = require_non_empty_str("name", name)
        cleaned_limit = require_positive_limit(limit)
        response = runtime.service.find_node(cleaned_name, cleaned_limit)
        return {
            "status": response.status,
            "data": response.data,
            "backend_used": response.backend_used,
        }

    return _run_tool("Find node query", operation)


def adg_edge_fanout(src_id: str, relation_type: str, limit: int = 30) -> JsonDict:
    """Get outgoing edges from src_id via relation_type."""

    def operation() -> JsonDict:
        cleaned_src_id = require_non_empty_str("src_id", src_id)
        cleaned_relation_type = require_non_empty_str("relation_type", relation_type)
        cleaned_limit = require_positive_limit(limit)
        response = runtime.service.get_edge_fanout(cleaned_src_id, cleaned_relation_type, cleaned_limit)
        return {
            "status": response.status,
            "data": response.data,
            "backend_used": response.backend_used,
        }

    return _run_tool("Edge fanout query", operation)


def adg_edge_fanin(tgt_id: str, relation_type: str, limit: int = 30) -> JsonDict:
    """Get incoming edges to tgt_id via relation_type."""

    def operation() -> JsonDict:
        cleaned_tgt_id = require_non_empty_str("tgt_id", tgt_id)
        cleaned_relation_type = require_non_empty_str("relation_type", relation_type)
        cleaned_limit = require_positive_limit(limit)
        response = runtime.service.get_edge_fanin(cleaned_tgt_id, cleaned_relation_type, cleaned_limit)
        return {
            "status": response.status,
            "data": response.data,
            "backend_used": response.backend_used,
        }

    return _run_tool("Edge fanin query", operation)


def adg_violations(limit: int = 100) -> JsonDict:
    """Get anti-pattern violations."""

    def operation() -> JsonDict:
        cleaned_limit = require_positive_limit(limit)
        response = runtime.service.get_violations(cleaned_limit)
        return {
            "status": response.status,
            "data": response.data,
            "backend_used": response.backend_used,
        }

    return _run_tool("Violations query", operation)


def adg_close_connections() -> JsonDict:
    """Close ADG backend connections to release SQLite file locks."""
    return _run_tool("Close connections", runtime.close_connections)


def adg_reopen_connections() -> JsonDict:
    """Reopen ADG backend connections after an explicit close."""
    return _run_tool("Reopen connections", runtime.reopen_connections)


def adg_runtime_info() -> JsonDict:
    """Return process-level runtime identity for verifying restarts."""
    return _run_tool("Runtime info", runtime.runtime_info)


def adg_reload() -> JsonDict:
    """Reload the latest ADG SQLite snapshot if current connection is stale."""
    return _run_tool("Auto-reload", runtime.reload_latest_snapshot)
