from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "deterministic_loop_detector", "state_snapshot")


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
