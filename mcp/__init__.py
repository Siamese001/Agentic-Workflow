"""
MCP (Model Context Protocol) Implementation
"""

from .mcp_client import (
    MCPClient,
    call_external_service,
    get_tool_schemas,
    check_mcp_access,
    get_mcp_client
)

__all__ = [
    'MCPClient',
    'call_external_service',
    'get_tool_schemas',
    'check_mcp_access',
    'get_mcp_client'
]
