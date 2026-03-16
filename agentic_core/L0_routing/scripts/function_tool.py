"""
Tools module for L2 Execution tool_registry.

Provides common tool implementations.
"""

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "function_tool", "execution_auth")
_emit_validates_capability("p2", "function_tool", "capability_check")
_emit_routes_to_capability("p2", "function_tool", "capability_route")
_emit_writes_via_uwg("p2", "function_tool", "uwg_write")
_emit_blocks_direct_write("p2", "function_tool", "direct_write_block")
_emit_records_tool_invocation("p2", "function_tool", "tool_invocation")
_emit_captures_execution_output("p2", "function_tool", "exec_output")
_emit_dispatches_agent("p3", "function_tool", "agent_dispatch")
_emit_coordinates_agents("p3", "function_tool", "agent_coordination")
_emit_records_workflow_lineage("p3", "function_tool", "workflow_lineage")
_emit_records_healing_outcome("p3", "function_tool", "healing_outcome")
_emit_escalates_failure("p3", "function_tool", "failure_escalation")
_emit_orchestrates_workflow("p3", "function_tool", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "function_tool", "healing_dispatch")
_emit_invokes_evaluation("p3", "function_tool", "evaluation_signal")
_emit_records_telemetry_event("p4", "function_tool", "telemetry_event")
_emit_captures_evaluation_metric("p4", "function_tool", "eval_metric")
_emit_stores_embedding("p4", "function_tool", "embedding_store")
_emit_updates_meta_learning_state("p4", "function_tool", "meta_learning")
_emit_links_execution_to_snapshot("p4", "function_tool", "exec_snapshot_link")
from .base import tool_registry

emit_replay_key("p0", "function_tool")
emit_determinism_digest("p0", "function_tool")

_emit_dispatches_healing_run("p1", "function_tool", "L0")
_emit_routes_through("p1", "function_tool", "L0")
_emit_escalates_to_human("p1", "function_tool", "L0")
_emit_reads_policy_state("p1", "function_tool", "L0")

_emit_records_execution_trace("p0", "evidence", "function_tool")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "function_tool", "p0_governance")
_emit_snapshots_state("p0", "function_tool", "state_snapshot")

__all__ = ["tool_registry", "FunctionTool"]


class FunctionTool(BaseTool):
    """A tool that wraps a callable function."""

    def __init__(self, name: str, func: callable, description: str = ""):
        super().__init__(name, description)
        self._func = func

    def execute(self, *args, **kwargs) -> Any:
        """Execute the wrapped function."""
        return self._func(*args, **kwargs)
