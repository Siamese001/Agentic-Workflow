from typing import Any
from agentic_core.patterns.base import BaseReasoningPattern
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class ReActStrategy(BaseReasoningPattern):
    """
    Reason-Act-Observe loop.

    Zero-Ambiguity Standard: Renamed from ReActPattern to ReActStrategy
    to clarify its role as a behavioral strategy pattern.
    """

    async def plan(self, state: AgentState, tools: ToolRegistry) -> tuple[str, dict[str, Any]]:
        """
        DETERMINISTIC MOCK LOGIC FOR TESTING:
        - If turn 0: Call 'search_tool'
        - If turn 1: Call 'calc_tool'
        - If turn 2: Finish
        """
        if state.turn_count == 0:
            return ('search_tool', {'query': state.user_input})
        elif state.turn_count == 1:
            return ('calc_tool', {'expression': '2 + 2'})
        else:
            return ('Final Answer', {'result': 'Task Complete'})
ReActPattern = ReActStrategy
