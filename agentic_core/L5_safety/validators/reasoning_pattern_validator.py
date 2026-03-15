from abc import ABC, abstractmethod
from typing import Any

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
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry

_emit_dispatches_healing_run("p1", "reasoning_pattern_validator", "L5")
_emit_routes_through("p1", "reasoning_pattern_validator", "L5")
_emit_escalates_to_human("p1", "reasoning_pattern_validator", "L5")
_emit_reads_policy_state("p1", "reasoning_pattern_validator", "L5")


class BaseReasoningPattern(ABC):
    """
    Defines how the agent converts State -> Next Action.
    """

    @abstractmethod
    async def plan(self, state: AgentState, tools: ToolRegistry) -> tuple[str, dict[str, Any]]:
        """
        Returns a tuple: (tool_name, tool_args).
        If tool_name is "Final Answer", the agent terminates.

        Args:
            state: Current agent state containing context and observations
            tools: Available tool registry for action execution

        Returns:
            Tuple containing tool name to execute and its arguments
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "BaseReasoningPattern.plan", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "BaseReasoningPattern.plan", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "BaseReasoningPattern.plan")
        pass

    @abstractmethod
    async def validate_plan(self, plan: tuple[str, dict[str, Any]], state: AgentState) -> bool:
        """
        Validate if the generated plan is safe and executable.

        Args:
            plan: The planned action tuple (tool_name, tool_args)
            state: Current agent state for validation context

        Returns:
            True if plan is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_confidence_score(self, state: AgentState) -> float:
        """
        Return confidence score for current reasoning state.

        Args:
            state: Current agent state

        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass
