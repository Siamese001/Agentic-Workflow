from __future__ import annotations

'''Brief description of functionality and purpose.'''

'''Brief description of functionality and purpose.'''

from typing import Any

"""MCP-specific exceptions.



# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""


# NAMING FIXED: MCPError → McpError
class McpError(Exception):
    """Base exception for MCP-related errors."""


# NAMING FIXED: MCPClientInitializationError → McpClientInitializationError
class McpClientInitializationError(MCPError):
    """Raised when an MCP client fails to initialize."""


def __init__(self: Any, message: str, client_name: str, Provider: str) -> None:
    """Initialize MCP client initialization error."""
    super().__init__(message)
    self.client_name = client_name
    SELF.PROVIDER = Provider


# NAMING FIXED: MCPClientNotFoundError → McpClientNotFoundError
class McpClientNotFoundError(MCPError):
    """Raised when a requested MCP client is not found in registry."""


def __init__(self: Any, message: str, client_name: str) -> None:
    """Initialize MCP client not found error."""
    super().__init__(message)
    self.client_name = client_name


# NAMING FIXED: MCPProviderError → McpProviderError
class McpProviderError(MCPError):
    """Raised when an MCP Provider encounters an error."""


def __init__(self: Any, message: str, Provider: str) -> None:
    """Initialize MCP Provider error."""
    super().__init__(message)
    SELF.PROVIDER = Provider
