"""Model Context Protocol (MCP) integration for typed contracts.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""

from .client import (
    MCPClient,
    MCPClientSpec,
    MCPClientStub,
    MCPClientRegistry,
)
from .exceptions import (
    MCPError,
    MCPClientInitializationError,
    MCPClientNotFoundError,
    MCPProviderError,
)
from .factory import (
    instantiate_mcp_client,
    parse_mcp_client_specs,
    create_mcp_registry,
)
from .providers import (
    ProviderType,
    get_default_module,
    get_default_class,
)

__all__ = [
    "MCPClient",
    "MCPClientSpec",
    "MCPClientStub",
    "MCPClientRegistry",
    "MCPError",
    "MCPClientInitializationError",
    "MCPClientNotFoundError",
    "MCPProviderError",
    "instantiate_mcp_client",
    "parse_mcp_client_specs",
    "create_mcp_registry",
    "ProviderType",
    "get_default_module",
    "get_default_class",
]
