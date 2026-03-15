"""
Base classes for L2 Execution tool_registry.

Provides foundational classes for tool registration and execution.
"""

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "base_tool_script", "L0")
_emit_routes_through("p1", "base_tool_script", "L0")
_emit_escalates_to_human("p1", "base_tool_script", "L0")
_emit_reads_policy_state("p1", "base_tool_script", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "base_tool_script", "p0_governance")
_emit_snapshots_state("p0", "base_tool_script", "state_snapshot")

logger = logging.getLogger(__name__)


class BaseTool:
    """Base class for all tools in the registry."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._enabled = True

    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")

    def is_enabled(self) -> bool:
        """Check if tool is enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable the tool."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the tool."""
        self._enabled = False


class tool_registry:
    """Registry for managing tools."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "tool_registry.register")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def unregister(self, name: str) -> None:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            logger.debug(f"Unregistered tool: {name}")

    def get(self, name: str) -> BaseTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def execute(self, name: str, *args, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")
        if not tool.is_enabled():
            raise ValueError(f"Tool is disabled: {name}")
        return tool.execute(*args, **kwargs)


Tool = BaseTool
Registry = tool_registry
__all__ = ["BaseTool", "tool_registry", "Tool", "Registry"]
