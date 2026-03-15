"""MCP client specifications and registry.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
Migrated from archives/legacy_resume_gen/Agentic-Workflow-10_7_main/core_v10_7/mcp.py
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

from .providers import get_default_class, get_default_module

logger = logging.getLogger(__name__)


class MCPClient(Protocol):
    """Protocol defining the MCP client interface.

    All MCP clients must implement this protocol for type safety.
    """

    def __call__(self, *args: object, **kwargs: object) -> dict[str, object]:
        """Execute the client operation.

        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments

        Returns:
            Dict with operation result
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MCPClient.__call__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MCPClient.__call__", "p0_governance")
        ...


@dataclass
class MCPClientSpec:
    """Typed representation of a configured MCP client.

    This is the canonical schema for MCP client configuration,
    enforcing strict typing and validation.

    Attributes:
        name: Unique client identifier
        provider: Provider type (redis, chromadb, openai, etc.)
        module: Optional explicit Python module path
        class_name: Optional explicit class name
        parameters: Client initialization parameters
        optional: Whether this client is optional (won't fail if unavailable)
    """

    name: str
    provider: str = "stub"
    module: str | None = None
    class_name: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    optional: bool = False

    def resolved_module(self) -> str | None:
        """Return explicit module or provider-mapped default.

        Returns:
            Module path or None for stub
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "MCPClientSpec.resolved_module")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MCPClientSpec.resolved_module".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.module:
            return self.module
        return get_default_module(self.provider)

    def resolved_class(self) -> str | None:
        """Return explicit class_name or provider-mapped default.

        Returns:
            Class name or None
        """
        if self.class_name:
            return self.class_name
        return get_default_class(self.provider)

    def validate(self) -> None:
        """Validate the spec configuration.

        Raises:
            ValueError: If spec is invalid
        """
        if not self.name:
            raise ValueError("MCPClientSpec requires a non-empty 'name'")
        if not isinstance(self.parameters, dict):
            raise ValueError(f"MCPClientSpec '{self.name}' parameters must be a dict")
        if self.provider != "stub":
            if not self.resolved_module():
                raise ValueError(
                    f"MCPClientSpec '{self.name}': no module specified and no default for provider '{self.provider}'"
                )
            if not self.resolved_class():
                raise ValueError(
                    f"MCPClientSpec '{self.name}': no class_name specified and no default for provider '{self.provider}'"
                )


class MCPClientStub:
    """Safe fallback MCP client.

    All MCP tools using this stub will receive a structured response
    indicating the client is stubbed. This prevents runtime failures
    while maintaining type safety.
    """

    def __init__(self, name: str, parameters: dict[str, Any] | None = None):
        """Initialize stub client.

        Args:
            name: Client name
            parameters: Optional parameters (for logging/debugging)
        """
        self.name = name
        self.parameters = parameters or {}
        logger.info("mcp_stub_created", extra={"client_name": name, "parameters": parameters})

    def __call__(self, *args, **kwargs) -> dict[str, Any]:
        """All calls return a structured stub result.

        Returns:
            Dict with stub=True and error message
        """
        return {
            "stub": True,
            "client": self.name,
            "parameters": self.parameters,
            "args": args,
            "kwargs": kwargs,
            "error": self.parameters.get("error", "Stubbed MCP client."),
        }

    def __repr__(self) -> str:
        """String representation."""
        details = ", ".join((f"{k}={v}" for k, v in self.parameters.items()))
        return f"<MCPClientStub name={self.name} {details}>"


class MCPClientRegistry:
    """Registry for managing MCP clients.

    Provides centralized access to all configured MCP clients
    with type-safe retrieval.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._clients: dict[str, MCPClient] = {}
        self._specs: dict[str, MCPClientSpec] = {}

    def register(self, name: str, client: MCPClient) -> None:
        """Register a client instance.

        Args:
            name: Client name
            client: Instantiated client
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "MCPClientRegistry.register")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MCPClientRegistry.register".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._clients[name] = client
        spec.validate()
        self._specs[spec.name] = spec
        self._clients[spec.name] = client
        logger.info(
            "mcp_client_registered",
            extra={
                "client_name": spec.name,
                "provider": spec.provider,
                "is_stub": isinstance(client, MCPClientStub),
            },
        )

    def get(self, name: str) -> Any | None:
        """Get a client by name.

        Args:
            name: Client name

        Returns:
            Client instance or None if not found
        """
        return self._clients.get(name)

    def get_spec(self, name: str) -> MCPClientSpec | None:
        """Get a client spec by name.

        Args:
            name: Client name

        Returns:
            Client spec or None if not found
        """
        return self._specs.get(name)

    def has(self, name: str) -> bool:
        """Check if a client exists.

        Args:
            name: Client name

        Returns:
            True if client exists
        """
        return name in self._clients

    def list_clients(self) -> list[str]:
        """List all registered client names.

        Returns:
            List of client names
        """
        return list(self._clients.keys())

    def is_stub(self, name: str) -> bool:
        """Check if a client is a stub.

        Args:
            name: Client name

        Returns:
            True if client is a stub
        """
        client = self.get(name)
        return isinstance(client, MCPClientStub)

    def clear(self) -> None:
        """Clear all registered clients."""
        self._clients.clear()
        self._specs.clear()
