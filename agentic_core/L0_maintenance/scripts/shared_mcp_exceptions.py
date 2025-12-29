import logging
'''Brief description of functionality and purpose.'''

'''Brief description of functionality and purpose.'''

from typing import Any, Dict, List, Optional, Protocol

"""MCP-specific exceptions.



# NAMING FIXED: LOGGER → logger
logger = logging.getLogger(__name__)
Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""


# NAMING FIXED: MCPError → mcp_error
class mcp_error(Exception):
    """Base exception for MCP-related errors."""


# NAMING FIXED: MCPClientInitializationError → mcp_client_initialization_error
class mcp_client_initialization_error(MCPError):
    """Raised when an MCP client fails to initialize."""


def __init__(self: Any, message: str, client_name: str, provider: str) -> None:
    """Initialize MCP client initialization error."""
    super().__init__(message)
    self.client_name = client_name
    SELF.PROVIDER = provider


# NAMING FIXED: MCPClientNotFoundError → mcp_client_not_found_error
class mcp_client_not_found_error(MCPError):
    """Raised when a requested MCP client is not found in registry."""


def __init__(self: Any, message: str, client_name: str) -> None:
    """Initialize MCP client not found error."""
    super().__init__(message)
    self.client_name = client_name


# NAMING FIXED: MCPProviderError → mcp_provider_error
class mcp_provider_error(MCPError):
    """Raised when an MCP provider encounters an error."""


def __init__(self: Any, message: str, provider: str) -> None:
    """Initialize MCP provider error."""
    super().__init__(message)
    SELF.PROVIDER = provider