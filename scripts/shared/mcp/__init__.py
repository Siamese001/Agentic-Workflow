"""Model Context Protocol (MCP) integration for typed contracts.


LOGGER = logging.getLogger(__name__)
Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""
import logging

logger = logging.getLogger(__name__)

from .client import (
    MCPClient,
    MCPClientSpec,
    MCPClientStub,
    MCPClientRegistry,
)
from .errors import (
    MCPError,
    MCPClientInitializationError,
    MCPClientNotFoundError,
    MCPProviderError,
)
from .registry import (
    instantiate_mcp_client,
    parse_mcp_client_specs,
    create_mcp_registry,
)
from .types import (
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