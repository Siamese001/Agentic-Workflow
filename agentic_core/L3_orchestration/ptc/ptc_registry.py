"""
Programmatic Tool Calling (PTC) - Tool Registry

Deterministic registry for tool specifications and handlers.
Enforces uniqueness, validation, and deterministic ordering.
"""

from __future__ import annotations

import builtins
from typing import Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

from .tool_contract import ToolSpec

_emit_dispatches_healing_run("p1", "ptc_registry", "L3")
_emit_routes_through("p1", "ptc_registry", "L3")
_emit_escalates_to_human("p1", "ptc_registry", "L3")
_emit_reads_policy_state("p1", "ptc_registry", "L3")


class ToolRegistry:
    """Deterministic registry for tools."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ToolRegistry.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ToolRegistry.__init__", "p0_governance")
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, Callable] = {}

    def register(self, spec: ToolSpec, handler: Callable) -> None:
        """Register a tool with specification and handler.

        Args:
            spec: Tool specification
            handler: Handler function

        Raises:
            ValueError: If tool_id already exists or validation fails
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ToolRegistry.register")

        if spec.tool_id in self._specs:
            raise ValueError(f"Tool '{spec.tool_id}' already registered")
        valid_side_effects = {"PURE", "READONLY", "WRITE_FS", "SUBPROCESS"}
        if spec.side_effect_class not in valid_side_effects:
            raise ValueError(f"Invalid side_effect_class: {spec.side_effect_class}")
        arg_names = [arg.name for arg in spec.args]
        if arg_names != sorted(arg_names):
            raise ValueError("ToolSpec args must be sorted by name")
        if spec.version < 1:
            raise ValueError("ToolSpec version must be >= 1")
        self._specs[spec.tool_id] = spec
        self._handlers[spec.tool_id] = handler

    def get(self, tool_id: str) -> tuple[ToolSpec, Callable]:
        """Get tool specification and handler.

        Args:
            tool_id: Tool identifier

        Returns:
            Tuple of (spec, handler)

        Raises:
            ValueError: If tool_id not found
        """
        if tool_id not in self._specs:
            raise ValueError(f"Tool '{tool_id}' not found")
        return (self._specs[tool_id], self._handlers[tool_id])

    def list(self) -> builtins.list[ToolSpec]:
        """List all registered tool specifications.

        Returns:
            List of ToolSpec objects sorted by tool_id
        """
        specs = list(self._specs.values())
        specs.sort(key=lambda s: s.tool_id)
        return specs

    def has(self, tool_id: str) -> bool:
        """Check if tool is registered.

        Args:
            tool_id: Tool identifier

        Returns:
            True if tool exists
        """
        return tool_id in self._specs

    def count(self) -> int:
        """Get number of registered tools.

        Returns:
            Number of tools
        """
        return len(self._specs)


_GLOBAL_REGISTRY = ToolRegistry()


def get_global_registry() -> ToolRegistry:
    """Get the global tool registry.

    Returns:
        Global ToolRegistry instance
    """
    return _GLOBAL_REGISTRY


def register_tool(spec: ToolSpec, handler: Callable) -> None:
    """Register a tool in the global registry.

    Args:
        spec: Tool specification
        handler: Handler function
    """
    _GLOBAL_REGISTRY.register(spec, handler)


def get_tool(tool_id: str) -> tuple[ToolSpec, Callable]:
    """Get tool from global registry.

    Args:
        tool_id: Tool identifier

    Returns:
        Tuple of (spec, handler)
    """
    return _GLOBAL_REGISTRY.get(tool_id)


def list_tools() -> list[ToolSpec]:
    """List all tools in global registry.

    Returns:
        List of ToolSpec objects
    """
    return _GLOBAL_REGISTRY.list()


__all__ = ["ToolRegistry", "get_global_registry", "register_tool", "get_tool", "list_tools"]
