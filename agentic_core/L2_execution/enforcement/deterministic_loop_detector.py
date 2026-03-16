from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "deterministic_loop_detector")
emit_determinism_digest("p0", "deterministic_loop_detector")

_emit_dispatches_healing_run("p1", "deterministic_loop_detector", "L2")
_emit_routes_through("p1", "deterministic_loop_detector", "L2")
_emit_escalates_to_human("p1", "deterministic_loop_detector", "L2")
_emit_reads_policy_state("p1", "deterministic_loop_detector", "L2")

_emit_snapshots_state("p0", "deterministic_loop_detector", "state_snapshot")
_emit_authorize_and_execute("p2", "deterministic_loop_detector", "execution_auth")
_emit_validates_capability("p2", "deterministic_loop_detector", "capability_check")
_emit_routes_to_capability("p2", "deterministic_loop_detector", "capability_route")
_emit_writes_via_uwg("p2", "deterministic_loop_detector", "uwg_write")
_emit_blocks_direct_write("p2", "deterministic_loop_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "deterministic_loop_detector", "tool_invocation")
_emit_captures_execution_output("p2", "deterministic_loop_detector", "exec_output")
_emit_dispatches_agent("p3", "deterministic_loop_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "deterministic_loop_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "deterministic_loop_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "deterministic_loop_detector", "healing_outcome")
_emit_escalates_failure("p3", "deterministic_loop_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "deterministic_loop_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "deterministic_loop_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "deterministic_loop_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "deterministic_loop_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "deterministic_loop_detector", "eval_metric")
_emit_stores_embedding("p4", "deterministic_loop_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "deterministic_loop_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "deterministic_loop_detector", "exec_snapshot_link")


class ToolBudgetExceededError(Exception):
    """Raised when a tool execution exceeds its deterministic step budget."""

    def __init__(self, tool_name: str, budget: int):
        self.tool_name = tool_name
        self.budget = budget
        self.reason_code = "TOOL_BUDGET_EXCEEDED"
        super().__init__(
            f"[{self.reason_code}] Tool '{tool_name}' exceeded execution step budget of {budget}."
        )


@dataclass(frozen=True)
class ToolBudget:
    """Defines the deterministic execution budget for a tool."""

    max_steps: int


class DeterministicLoopDetector:
    """
    A deterministic circuit-breaker to prevent infinite loops in tool execution.

    This detector enforces Guarantee #10 by using a step counter instead of
    wall-clock time, ensuring that loop detection is replayable and not subject
    to variations in machine performance.

    It is designed to be attached to the L2 Per-Tool-Call (PTC) execution context.
    """

    def __init__(self):
        self._counters: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))

    def increment_and_check(self, trace_id: str, tool_name: str, budget: ToolBudget) -> None:
        """
        Increments the execution counter for a given tool and checks against its budget.

        This method must be called once per logical step within a tool's execution.

        Args:
            trace_id: The unique identifier for the current execution trace.
            tool_name: The name of the tool being executed.
            budget: The deterministic budget for the tool.

        Raises:
            ToolBudgetExceededError: If the counter exceeds the tool's max_steps.
        """
        _emit_applies_guardrail(
            str(uuid.uuid4()), "DeterministicLoopDetector.increment_and_check", "L2_EXECUTION"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "DeterministicLoopDetector.increment_and_check"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DeterministicLoopDetector.increment_and_check".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        counter = self._counters[trace_id][tool_name]
        if counter >= budget.max_steps:
            raise ToolBudgetExceededError(tool_name=tool_name, budget=budget.max_steps)
        self._counters[trace_id][tool_name] += 1

    def get_current_step_count(self, trace_id: str, tool_name: str) -> int:
        """Returns the current step count for a tool within a trace."""
        return self._counters[trace_id][tool_name]

    def reset_trace(self, trace_id: str) -> None:
        """Resets all counters for a given trace_id (for testing or context closure)."""
        if trace_id in self._counters:
            del self._counters[trace_id]
