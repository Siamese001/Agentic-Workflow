"""
MCP client registry utilities for v10.7.

This version fixes:
 - provider→module routing
 - proper stub fallback
 - module/class resolution
 - structured error propagation
 - compatibility with context._load_mcp_config()
 - alignment with instantiate_mcp_client() expectations
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .exceptions import MCPClientInitializationError

logger = logging.getLogger("core_v10_7.mcp")


# ---------------------------------------------------------------------------
# Provider → Default module/class maps (v10.7 standardization)
# ---------------------------------------------------------------------------

DEFAULT_PROVIDER_MODULES = {
    "redis": "redis",
    "chromadb": "chromadb",
    "openai": "mcp_openai",  # Example: MCP OpenAI wrapper module
    "http": "mcp_http_client",
}

DEFAULT_PROVIDER_CLASSES = {
    "redis": "RedisMCPClient",
    "chromadb": "ChromaMCPClient",
    "openai": "OpenAIMCPClient",
    "http": "HTTPMCPClient",
}


# ---------------------------------------------------------------------------
# MCPClientSpec (unchanged conceptually, but validated more strictly)
# ---------------------------------------------------------------------------

@dataclass
class MCPClientSpec:
    """Typed representation of a configured MCP client."""

    name: str
    provider: str = "stub"
    module: Optional[str] = None
    class_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    optional: bool = False

    def resolved_module(self) -> Optional[str]:
        """Return explicit module or provider-mapped default."""
        if self.module:
            return self.module
        return DEFAULT_PROVIDER_MODULES.get(self.provider)

    def resolved_class(self) -> Optional[str]:
        """Return explicit class_name or provider-mapped default."""
        if self.class_name:
            return self.class_name
        return DEFAULT_PROVIDER_CLASSES.get(self.provider)


# ---------------------------------------------------------------------------
# Stub fallback client
# ---------------------------------------------------------------------------

class MCPClientStub:
    """
    Safe fallback MCP client.

    All MCP tools using this stub will receive a structured response:
      {"error": "<reason>", "stub": true, ...parameters}
    """

    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.parameters = parameters or {}

    def __call__(self, *args, **kwargs):
        """All calls simply return a structured stub result."""
        return {
            "stub": True,
            "client": self.name,
            "parameters": self.parameters,
            "args": args,
            "kwargs": kwargs,
            "error": self.parameters.get("error", "Stubbed MCP client."),
        }

    def __repr__(self) -> str:
        details = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"<MCPClientStub name={self.name} {details}>"


# ---------------------------------------------------------------------------
# Spec parser
# ---------------------------------------------------------------------------

def parse_mcp_client_specs(raw_specs: List[Dict[str, Any]]) -> List[MCPClientSpec]:
    """Validate and normalise MCP client specifications."""

    specs: List[MCPClientSpec] = []
    for raw in raw_specs:
        if not isinstance(raw, dict):
            raise ValueError("Each MCP client entry must be a mapping.")

        name = raw.get("name")
        if not name or not isinstance(name, str):
            raise ValueError("MCP client entries require a string 'name'.")

        parameters = raw.get("parameters", {})
        if parameters is None:
            parameters = {}
        if not isinstance(parameters, dict):
            raise ValueError(f"MCP client '{name}' parameters must be a mapping.")

        provider = str(raw.get("provider", "stub")).lower()
        module = raw.get("module")
        class_name = raw.get("class_name") or raw.get("class")

        spec = MCPClientSpec(
            name=name,
            provider=provider,
            module=module,
            class_name=class_name,
            parameters=parameters,
            optional=bool(raw.get("optional", False)),
        )
        specs.append(spec)

    return specs


# ---------------------------------------------------------------------------
# MCP client instantiation (fixed and fully aligned with context.py)
# ---------------------------------------------------------------------------

def instantiate_mcp_client(spec: MCPClientSpec) -> Any:
    """
    Create an MCP client instance from a validated spec.

    v10.7 fixes:
      - provider→default module resolution
      - class_name resolution
      - explicit logging
      - clean error propagation
    """

    # STUB path
    if spec.provider == "stub" and not spec.module:
        logger.info(f"[MCP] Using stub for '{spec.name}'.")
        return MCPClientStub(spec.name, spec.parameters)

    # Resolve module and class_name
    module_name = spec.resolved_module()
    class_name = spec.resolved_class()

    if not module_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no module specified and no provider mapping found."
        )

    if not class_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no class_name specified and no provider mapping found."
        )

    # Import module
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise MCPClientInitializationError(
            f"Failed to import MCP module '{module_name}' for client '{spec.name}': {exc}"
        ) from exc

    # Get class
    try:
        client_cls = getattr(module, class_name)
    except AttributeError as exc:
        raise MCPClientInitializationError(
            f"Module '{module_name}' missing class '{class_name}' "
            f"for MCP client '{spec.name}'."
        ) from exc

    # Instantiate client
    try:
        instance = client_cls(**spec.parameters)
        logger.info(f"[MCP] Initialized client '{spec.name}' via {module_name}.{class_name}")
        return instance
    except Exception as exc:
        raise MCPClientInitializationError(
            f"Failed to instantiate MCP client '{spec.name}': {exc}"
        ) from exc


__all__ = [
    "MCPClientSpec",
    "MCPClientStub",
    "parse_mcp_client_specs",
    "instantiate_mcp_client",
]
