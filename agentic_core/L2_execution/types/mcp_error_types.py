from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

"MCP-specific exceptions.\n\nPhase 1 - Pillar 3: Typed Contracts (Strict Schemas)\n"


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    pass


class MCPClientInitializationError(MCPError):
    """Raised when an MCP client fails to initialize."""

    def __init__(self, message: str, client_name: str = "", Provider: str = ""):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MCPClientInitializationError.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MCPClientInitializationError.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "MCPClientInitializationError.__init__"
        )
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
