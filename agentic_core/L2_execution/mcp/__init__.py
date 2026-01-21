from __future__ import annotations

"""MCP Integration - Hardened Sovereign Module."""
from .client import MCPClient, MCPClientSpec
from .exceptions import MCPClientInitializationError, MCPClientNotFoundError, MCPError
from .factory import create_mcp_registry, instantiate_mcp_client, parse_mcp_client_specs
from .providers import get_default_class, get_default_module

__all__ = [
    "MCPClient",
    "MCPClientSpec",
    "parse_mcp_client_specs",
    "instantiate_mcp_client",
    "create_mcp_registry",
    "MCPError",
    "MCPClientInitializationError",
    "MCPClientNotFoundError",
    "get_default_module",
    "get_default_class",
]
