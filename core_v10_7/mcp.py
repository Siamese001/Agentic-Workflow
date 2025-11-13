"""MCP client registry utilities for v10.7."""
from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .exceptions import MCPClientInitializationError

logger = logging.getLogger("core_v10_7")


@dataclass
class MCPClientSpec:
    """Typed representation of a configured MCP client."""

    name: str
    provider: str = "stub"
    module: Optional[str] = None
    class_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    optional: bool = False


class MCPClientStub:
    """Fallback stub MCP client used when no implementation exists."""

    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.parameters = parameters or {}

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        details = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"<MCPClientStub name={self.name} {details}>"


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

        spec = MCPClientSpec(
            name=name,
            provider=str(raw.get("provider", "stub")),
            module=raw.get("module"),
            class_name=raw.get("class_name") or raw.get("class"),
            parameters=parameters,
            optional=bool(raw.get("optional", False)),
        )
        specs.append(spec)

    return specs


def instantiate_mcp_client(spec: MCPClientSpec) -> Any:
    """Create an MCP client instance from a validated spec."""

    if spec.provider == "stub" and not spec.module:
        return MCPClientStub(spec.name, spec.parameters)

    if spec.module:
        module = importlib.import_module(spec.module)
        class_name = spec.class_name or spec.provider
        try:
            client_cls = getattr(module, class_name)
        except AttributeError as exc:
            raise AttributeError(
                f"Module '{spec.module}' missing class '{class_name}' for MCP client '{spec.name}'"
            ) from exc

        try:
            return client_cls(**spec.parameters)
        except Exception as exc:  # pragma: no cover - instantiation errors are logged upstream
            raise MCPClientInitializationError(
                f"Failed to instantiate MCP client '{spec.name}': {exc}"
            ) from exc

    raise MCPClientInitializationError(
        f"Invalid MCP client spec for '{spec.name}'. Expected either 'module' or 'provider'."
    )


__all__ = [
    "MCPClientSpec",
    "MCPClientStub",
    "parse_mcp_client_specs",
    "instantiate_mcp_client",
]
