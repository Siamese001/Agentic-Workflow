#!/usr/bin/env python3
"""
Enhanced HTTP MCP Server - Advanced HTTP client with auth, retries, and async support.

Provides comprehensive HTTP capabilities for Windsurf with enterprise features.
Uses the canonical mcp_bootstrap pattern (FastMCP + @mcp.tool() + run_server)
to avoid the Windows stdio transport hangs caused by low-level Server + anyio.run.
"""

from __future__ import annotations

from tools.mcp.http_mcp.tools import register_http_tools
from tools.mcp.mcp_bootstrap import create_mcp_server, register_standard_health, run_server

mcp = create_mcp_server(
    "http",
    "Resilient HTTP client with retries, proxy awareness, bounded responses, and batch requests.",
)

register_http_tools(mcp)


def _http_health_extra() -> dict[str, object]:
    try:
        import aiohttp  # type: ignore[import-not-found]
        aiohttp_version = getattr(aiohttp, "__version__", "?")
    except ImportError:
        aiohttp_version = "unavailable"
    return {"aiohttp_version": aiohttp_version, "transport": "stdio"}


register_standard_health(mcp, "enhanced_http", extra=_http_health_extra)


if __name__ == "__main__":
    run_server(mcp)
