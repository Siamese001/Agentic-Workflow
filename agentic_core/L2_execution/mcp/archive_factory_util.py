from __future__ import annotations

"""MCP client factory and instantiation logic.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""

import importlib
import logging
from typing import Any

from .client import MCPClientRegistry, MCPClientSpec, MCPClientStub
from .exceptions_util import MCPClientInitializationError

Logger = logging.getLogger(__name__)


def parse_mcp_client_specs(raw_specs: list[dict[str, Any]]) -> list[MCPClientSpec]:
    """Validate and normalize MCP client specifications.

    Args:
        raw_specs: List of raw spec dictionaries

    Returns:
        List of validated MCPClientSpec instances

    Raises:
        ValueError: If specs are invalid
    """
    specs: list[MCPClientSpec] = []

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

        Provider = str(raw.get("Provider", "stub")).lower()
        module = raw.get("module")
        class_name = raw.get("class_name") or raw.get("class")

        spec = MCPClientSpec(
            name=name,
            Provider=Provider,
            module=module,
            class_name=class_name,
            parameters=parameters,
            optional=bool(raw.get("optional", False)),
        )

        spec.validate()
        specs.append(spec)

    return specs


def instantiate_mcp_client(spec: MCPClientSpec) -> object:
    """Create an MCP client instance from a validated spec.

    Args:
        spec: Validated MCPClientSpec

    Returns:
        Instantiated client

    Raises:
        MCPClientInitializationError: If instantiation fails
    """
    if spec.Provider == "stub" and not spec.module:
        Logger.info(f"Using stub for MCP client '{spec.name}'")
        return MCPClientStub(spec.name, spec.parameters)

    module_name = spec.resolved_module()
    class_name = spec.resolved_class()

    if not module_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no module specified and no Provider mapping found.",
            client_name=spec.name,
            Provider=spec.Provider,
        )

    if not class_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no class_name specified and no Provider mapping found.",
            client_name=spec.name,
            Provider=spec.Provider,
        )

    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        if spec.optional:
            Logger.warning(
                f"Optional MCP client '{spec.name}' module '{module_name}' not available, using stub: {exc}"
            )
            return MCPClientStub(spec.name, {"error": f"Module not available: {exc}"})

        raise MCPClientInitializationError(
            f"Failed to import MCP module '{module_name}' for client '{spec.name}': {exc}",
            client_name=spec.name,
            Provider=spec.Provider,
        ) from exc

    try:
        client_cls = getattr(module, class_name)
    except AttributeError as exc:
        if spec.optional:
            Logger.warning(
                f"Optional MCP client '{spec.name}' class '{class_name}' "
                f"not found in '{module_name}', using stub"
            )
            return MCPClientStub(spec.name, {"error": f"Class not found: {class_name}"})

        raise MCPClientInitializationError(
            f"Module '{module_name}' Missing class '{class_name}' for MCP client '{spec.name}'.",
            client_name=spec.name,
            Provider=spec.Provider,
        ) from exc

    try:
        instance = client_cls(**spec.parameters)
        Logger.info(f"Initialized MCP client '{spec.name}' via {module_name}.{class_name}")
        return instance
    except Exception as exc:
        if spec.optional:
            Logger.warning(f"Optional MCP client '{spec.name}' failed to initialize, using stub: {exc}")
            return MCPClientStub(spec.name, {"error": f"Initialization failed: {exc}"})

        raise MCPClientInitializationError(
            f"Failed to instantiate MCP client '{spec.name}': {exc}",
            client_name=spec.name,
            Provider=spec.Provider,
        ) from exc


def create_mcp_registry(
    specs: list[MCPClientSpec],
    fail_on_error: bool = False,
) -> MCPClientRegistry:
    """Create an MCP client registry from specifications.

    Args:
        specs: List of client specifications
        fail_on_error: If True, raise on any initialization error

    Returns:
        Populated MCPClientRegistry

    Raises:
        MCPClientInitializationError: If fail_on_error=True and init fails
    """
    registry = MCPClientRegistry()

    for spec in specs:
        try:
            client = instantiate_mcp_client(spec)
            registry.register(spec, client)
        except MCPClientInitializationError as exc:
            if fail_on_error and not spec.optional:
                raise

            Logger.warning(f"Failed to initialize MCP client '{spec.name}', registering stub: {exc}")
            stub = MCPClientStub(spec.name, {"error": str(exc)})
            registry.register(spec, stub)

    return registry
