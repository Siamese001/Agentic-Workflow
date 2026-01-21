"""MCP-specific exceptions.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    pass


class MCPClientInitializationError(MCPError):
    """Raised when an MCP client fails to initialize."""

    def __init__(self, message: str, client_name: str = "", provider: str = ""):
        super().__init__(message)
        self.client_name = client_name
        self.provider = provider


class MCPClientNotFoundError(MCPError):
    """Raised when a requested MCP client is not found in registry."""

    def __init__(self, message: str, client_name: str = ""):
        super().__init__(message)
        self.client_name = client_name


class MCPProviderError(MCPError):
    """Raised when an MCP provider encounters an error."""

    def __init__(self, message: str, provider: str = ""):
        super().__init__(message)
        self.provider = provider
