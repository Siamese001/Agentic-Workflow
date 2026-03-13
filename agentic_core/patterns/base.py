"""Base protocol for reasoning patterns.

Defines the BaseReasoningPattern ABC used by ReActStrategy and AgentEngine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseReasoningPattern(ABC):
    """Abstract base for all reasoning strategy patterns.

    Implementors decide the next (action, params) tuple given the current
    AgentState and available ToolRegistry.
    """

    @abstractmethod
    async def plan(self, state: Any, tools: Any) -> tuple[str, dict[str, Any]]:
        """Decide the next action.

        Args:
            state: Current AgentState.
            tools: Available ToolRegistry.

        Returns:
            (action_name, action_params) tuple.
        """
        ...
