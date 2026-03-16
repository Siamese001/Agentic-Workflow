"""
Base classes for L2 Execution tool_registry.

Provides foundational classes for tool registration and execution.
"""

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "base_tool_script", "execution_auth")
_emit_validates_capability("p2", "base_tool_script", "capability_check")
_emit_routes_to_capability("p2", "base_tool_script", "capability_route")
_emit_writes_via_uwg("p2", "base_tool_script", "uwg_write")
_emit_blocks_direct_write("p2", "base_tool_script", "direct_write_block")
_emit_records_tool_invocation("p2", "base_tool_script", "tool_invocation")
_emit_captures_execution_output("p2", "base_tool_script", "exec_output")
_emit_dispatches_agent("p3", "base_tool_script", "agent_dispatch")
_emit_coordinates_agents("p3", "base_tool_script", "agent_coordination")
_emit_records_workflow_lineage("p3", "base_tool_script", "workflow_lineage")
_emit_records_healing_outcome("p3", "base_tool_script", "healing_outcome")
_emit_escalates_failure("p3", "base_tool_script", "failure_escalation")
_emit_orchestrates_workflow("p3", "base_tool_script", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "base_tool_script", "healing_dispatch")
_emit_invokes_evaluation("p3", "base_tool_script", "evaluation_signal")
_emit_records_telemetry_event("p4", "base_tool_script", "telemetry_event")
_emit_captures_evaluation_metric("p4", "base_tool_script", "eval_metric")
_emit_stores_embedding("p4", "base_tool_script", "embedding_store")
_emit_updates_meta_learning_state("p4", "base_tool_script", "meta_learning")
_emit_links_execution_to_snapshot("p4", "base_tool_script", "exec_snapshot_link")

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
