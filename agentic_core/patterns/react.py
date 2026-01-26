# ReAct Pattern Implementation (Mocked for Phase 3)
# Strategy: Simulate reasoning without a live LLM for architectural testing

from typing import Dict, Any, Tuple
from agentic_core.patterns.base import BaseReasoningPattern
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry

class ReActPattern(BaseReasoningPattern):
    """
    Reason-Act-Observe loop.
    """
    
    async def plan(self, state: AgentState, tools: ToolRegistry) -> Tuple[str, Dict[str, Any]]:
        """
        DETERMINISTIC MOCK LOGIC FOR TESTING:
        - If turn 0: Call 'search_tool'
        - If turn 1: Call 'calc_tool'
        - If turn 2: Finish
        """
        if state.turn_count == 0:
            return "search_tool", {"query": state.user_input}
        
        elif state.turn_count == 1:
            # Simulate using info from previous turn
            return "calc_tool", {"expression": "2 + 2"}
        
        else:
            return "Final Answer", {"result": "Task Complete"}
