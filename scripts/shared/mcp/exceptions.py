from typing import Any
"""MCP-specific exceptions.



logger = logging.getLogger(__name__)
Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""

class MCPError(Exception):
    """Base exception for MCP-related errors."""

class MCPClientInitializationError(MCPError):
    """Raised when an MCP client fails to initialize."""

def __init__(self: Any, message: str, client_name: str, provider: str) -> None:
        """Initialize MCP client initialization error."""
        super().__init__(message)
        self.client_name = client_name
        self.provider = provider

class MCPClientNotFoundError(MCPError):
    """Raised when a requested MCP client is not found in registry."""

def __init__(self: Any, message: str, client_name: str) -> None:
        """Initialize MCP client not found error."""
        super().__init__(message)
        self.client_name = client_name

class MCPProviderError(MCPError):
    """Raised when an MCP provider encounters an error."""

def __init__(self: Any, message: str, provider: str) -> None:
        """Initialize MCP provider error."""
        super().__init__(message)
        self.provider = provider
