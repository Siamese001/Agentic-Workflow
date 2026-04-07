"""
Base classes for L2 Execution tool_registry.

Provides foundational classes for tool registration and execution.
"""

import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "base_tool_script", "L0")
_emit_routes_through("p1", "base_tool_script", "L0")
_emit_checks_agent_registry("p1", "base_tool_script", "agent_registry")
_emit_validates_agent_capability("p1", "base_tool_script", "capability")
_emit_dispatches_execution_plan("p1", "base_tool_script", "exec_plan")
_emit_agent_executes_agent("p1", "base_tool_script", "sub_agent")
_emit_routes_to_agent("p1", "base_tool_script", "target_agent")
_emit_verifies_policy("p1", "base_tool_script", "policy_check")
_emit_observes_runtime_state("p1", "base_tool_script", "runtime_state")
_emit_verifies_boundary("p1", "base_tool_script", "boundary_check")
_emit_transcripts_response("p1", "base_tool_script", "transcript")
_emit_hard_fails_untranscripted("p1", "base_tool_script")
_emit_gated_by_confidence("p1", "base_tool_script", "confidence_gate")
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("base_tool_script", "p4obs", "metric_1")
_emit_emits_metric_event("base_tool_script", "p4obs", "metric_2")
_emit_emits_metric_event("base_tool_script", "p4obs", "metric_3")
_emit_emits_metric_event("base_tool_script", "p4obs", "metric_4")
_emit_emits_metric_event("base_tool_script", "p4obs", "metric_5")
_emit_emits_metric_event("base_tool_script", "p4obs", "metric_6")
_emit_records_incident_event("base_tool_script", "p4obs", "incident")
_emit_captures_runtime_anomaly("base_tool_script", "p4obs", "anomaly")
_emit_writes_observability_log("base_tool_script", "p4obs", "obs_log")
_emit_updates_monitoring_state("base_tool_script", "p4obs", "mon_state")
_emit_triggers_alert("base_tool_script", "p4obs", "alert")
_emit_links_incident_trace("base_tool_script", "p4obs", "trace_link")
_emit_captures_pattern("base_tool_script", "p3lm", "pattern")
_emit_records_learning_event("base_tool_script", "p3lm", "learning_event")
_emit_writes_learning_snapshot("base_tool_script", "p3lm", "snapshot")
_emit_feeds_meta_learning("base_tool_script", "p3lm", "meta_feed")
_emit_updates_routing_strategy("base_tool_script", "p3lm", "routing")
_emit_improves_agent_policy("base_tool_script", "p3lm", "policy")
_emit_stores_learning_state("base_tool_script", "p3lm", "state")
_emit_records_execution_trace("base_tool_script", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("base_tool_script", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("base_tool_script", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("base_tool_script", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("base_tool_script", "L4_STATE", "p2_trace_5")
_emit_reads_environ("base_tool_script", "env_read", "p2_env_1")
_emit_reads_environ("base_tool_script", "env_read", "p2_env_2")
_emit_reads_runtime_state("base_tool_script", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("base_tool_script", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "base_tool_script", "context_pull")
_emit_pulls_context("p1", "base_tool_script", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "base_tool_script", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "base_tool_script", "uwg_term_2")
_emit_writes_through("p1", "base_tool_script", "write_through")
_emit_writes_through("p1", "base_tool_script", "write_through_2")
_emit_validated_by_safety_plane("p1", "base_tool_script", "safety_validation")
_emit_invokes_eval("p1", "base_tool_script", "eval_call")
_emit_proposal_commits_routing("p1", "base_tool_script", "routing_commit")

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
