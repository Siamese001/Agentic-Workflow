"""Redis MCP server construction and execution."""

from __future__ import annotations

from typing import Any

from tools.mcp.mcp_bootstrap import create_mcp_server, run_server

from .admin_tools import register_admin_tools
from .constants import SERVER_DESCRIPTION, SERVER_NAME
from .read_tools import register_read_tools


def build_mcp_server() -> Any:
    """Create the Redis MCP server and register all tools."""
    mcp = create_mcp_server(
        SERVER_NAME,
        SERVER_DESCRIPTION,
    )
    register_read_tools(mcp)
    register_admin_tools(mcp)
    return mcp


def run_mcp_server(mcp: Any) -> None:
    """Run the provided MCP server."""
    run_server(mcp)
