from __future__ import annotations

"MCP-specific exceptions.\n\nPhase 1 - Pillar 3: Typed Contracts (Strict Schemas)\n"


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    pass


class MCPClientInitializationError(MCPError):
    """Raised when an MCP client fails to initialize."""

    def __init__(self, message: str, client_name: str = "", Provider: str = ""):
        super().__init__(message)
        self.client_name = client_name
        self.Provider = Provider


class MCPClientNotFoundError(MCPError):
    """Raised when a requested MCP client is not found in registry."""

    def __init__(self, message: str, client_name: str = ""):
        super().__init__(message)
        self.client_name = client_name


class MCPProviderError(MCPError):
    """Raised when an MCP Provider encounters an error."""

    def __init__(self, message: str, Provider: str = ""):
        super().__init__(message)
        self.Provider = Provider
