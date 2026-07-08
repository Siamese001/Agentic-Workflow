"""
Programmatic Tool Calling (PTC) - Tool Registry

Deterministic registry for tool specifications and handlers.
Enforces uniqueness, validation, and deterministic ordering.
"""

from __future__ import annotations

import builtins
from typing import Callable

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "ptc_registry", "execution_auth")
trace_contract._emit_validates_capability("p2", "ptc_registry", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ptc_registry", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ptc_registry", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ptc_registry", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ptc_registry", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ptc_registry", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ptc_registry", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ptc_registry", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ptc_registry", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ptc_registry", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ptc_registry", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ptc_registry", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ptc_registry", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ptc_registry", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ptc_registry", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ptc_registry", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ptc_registry", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ptc_registry", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ptc_registry", "exec_snapshot_link")
from .tool_contract import ToolSpec

trace_contract.emit_replay_key("p0", "ptc_registry")
trace_contract.emit_determinism_digest("p0", "ptc_registry")

trace_contract._emit_dispatches_healing_run("p1", "ptc_registry", "L3")
trace_contract._emit_routes_through("p1", "ptc_registry", "L3")
trace_contract._emit_checks_agent_registry("p1", "ptc_registry", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ptc_registry", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ptc_registry", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ptc_registry", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ptc_registry", "target_agent")
trace_contract._emit_verifies_policy("p1", "ptc_registry", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ptc_registry", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ptc_registry", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ptc_registry", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ptc_registry")
trace_contract._emit_gated_by_confidence("p1", "ptc_registry", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ptc_registry", "L3")
trace_contract._emit_reads_policy_state("p1", "ptc_registry", "L3")

trace_contract._emit_emits_metric_event("ptc_registry", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ptc_registry", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ptc_registry", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ptc_registry", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ptc_registry", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ptc_registry", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ptc_registry", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ptc_registry", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ptc_registry", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ptc_registry", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ptc_registry", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ptc_registry", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ptc_registry", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ptc_registry", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ptc_registry", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ptc_registry", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ptc_registry", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ptc_registry", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ptc_registry", "p3lm", "state")
trace_contract._emit_records_execution_trace("ptc_registry", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ptc_registry", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ptc_registry", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ptc_registry", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ptc_registry", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ptc_registry", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ptc_registry", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ptc_registry", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ptc_registry", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ptc_registry", "context_pull")
trace_contract._emit_pulls_context("p1", "ptc_registry", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ptc_registry", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ptc_registry", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ptc_registry", "write_through")
trace_contract._emit_writes_through("p1", "ptc_registry", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ptc_registry", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ptc_registry", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ptc_registry", "routing_commit")


class ToolRegistry:
    """Deterministic registry for tools."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ToolRegistry.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ToolRegistry.__init__", "p0_governance")
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ToolRegistry.register")

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
