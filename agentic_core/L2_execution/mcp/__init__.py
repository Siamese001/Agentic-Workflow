"""MCP Integration - Hardened Sovereign Module."""
from .client import MCPClient, MCPClientSpec
from .factory import parse_mcp_client_specs, instantiate_mcp_client, create_mcp_registry
from .providers import get_default_module, get_default_class
from .exceptions import MCPError, MCPClientInitializationError, MCPClientNotFoundError

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
