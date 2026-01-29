# Reasoning Pattern Interface
# Strategy: Pluggable "Brains" (ReAct, CoT, etc.)

from abc import ABC, abstractmethod
from typing import Any
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry


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
