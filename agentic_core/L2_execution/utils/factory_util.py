"""MCP client factory and instantiation logic.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""

import importlib
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

from .client import MCPClientRegistry, MCPClientSpec, MCPClientStub
from .exceptions_util import MCPClientInitializationError

logger = logging.getLogger(__name__)


def parse_mcp_client_specs(raw_specs: list[dict[str, Any]]) -> list[MCPClientSpec]:
    """Validate and normalize MCP client specifications.

    Args:
        raw_specs: List of raw spec dictionaries

    Returns:
        List of validated MCPClientSpec instances

    Raises:
        ValueError: If specs are invalid
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "parse_mcp_client_specs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "parse_mcp_client_specs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "parse_mcp_client_specs")
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
    if spec.provider == "stub" and (not spec.module):
        logger.info(f"Using stub for MCP client '{spec.name}'")
        return MCPClientStub(spec.name, spec.parameters)
    module_name = spec.resolved_module()
    class_name = spec.resolved_class()
    if not module_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no module specified and no provider mapping found.",
            client_name=spec.name,
            provider=spec.provider,
        )
    if not class_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no class_name specified and no provider mapping found.",
            client_name=spec.name,
            provider=spec.provider,
        )
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        if spec.optional:
            logger.warning(
                f"Optional MCP client '{spec.name}' module '{module_name}' not available, using stub: {exc}"
            )
            return MCPClientStub(spec.name, {"error": f"Module not available: {exc}"})
        raise MCPClientInitializationError(
            f"Failed to import MCP module '{module_name}' for client '{spec.name}': {exc}",
            client_name=spec.name,
            provider=spec.provider,
        ) from exc
    try:
        client_cls = getattr(module, class_name)
    except AttributeError as exc:
        if spec.optional:
            logger.warning(
                f"Optional MCP client '{spec.name}' class '{class_name}' not found in '{module_name}', using stub"
            )
            return MCPClientStub(spec.name, {"error": f"Class not found: {class_name}"})
        raise MCPClientInitializationError(
            f"Module '{module_name}' missing class '{class_name}' for MCP client '{spec.name}'.",
            client_name=spec.name,
            provider=spec.provider,
        ) from exc
    try:
        instance = client_cls(**spec.parameters)
        logger.info(f"Initialized MCP client '{spec.name}' via {module_name}.{class_name}")
        return instance
    except Exception as exc:
        if spec.optional:
            logger.warning(f"Optional MCP client '{spec.name}' failed to initialize, using stub: {exc}")
            return MCPClientStub(spec.name, {"error": f"Initialization failed: {exc}"})
        raise MCPClientInitializationError(
            f"Failed to instantiate MCP client '{spec.name}': {exc}",
            client_name=spec.name,
            provider=spec.provider,
        ) from exc


def create_mcp_registry(specs: list[MCPClientSpec], fail_on_error: bool = False) -> MCPClientRegistry:
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
            if fail_on_error and (not spec.optional):
                raise
            logger.warning(f"Failed to initialize MCP client '{spec.name}', registering stub: {exc}")
            stub = MCPClientStub(spec.name, {"error": str(exc)})
            registry.register(spec, stub)
    return registry
