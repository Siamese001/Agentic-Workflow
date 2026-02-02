# Main Execution Loop
# Strategy: Orchestrates the Observe-Think-Act cycle with safety limits

from agentic_core.patterns.base import BaseReasoningPattern
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry


class AgentEngine:
    def __init__(self, pattern: BaseReasoningPattern, tools: ToolRegistry, max_turns: int = 5):
        self.pattern = pattern
        self.tools = tools
        self.max_turns = max_turns

    async def run(self, user_input: str, task_id: str = "default") -> AgentState:
        """
        Executes the agent loop until completion or max_turns.
        """
        state = AgentState(task_id=task_id, user_input=user_input)

        while not state.is_terminated:
            # 1. Check Limits
            if state.turn_count >= self.max_turns:
                state.is_terminated = True
                state.termination_reason = "MAX_TURNS_REACHED"
                break

            # 2. Plan (Think)
            # The pattern analyzes state and decides next tool
            tool_name, tool_args = await self.pattern.plan(state, self.tools)
            state.add_message("assistant", f"Thought: I should use {tool_name} with {tool_args}")

            # 3. Terminate if requested
            if tool_name == "Final Answer":
                state.is_terminated = True
                state.termination_reason = "COMPLETED"
                state.add_message("assistant", f"Final Answer: {tool_args.get('result')}")
                break

            # 4. Execute (Act)
            tool = self.tools.get(tool_name)
            if not tool:
                observation = f"Error: Tool '{tool_name}' not found."
            else:
                try:
                    observation = await tool.run(**tool_args)
                except Exception as e:
                    observation = f"Error executing {tool_name}: {str(e)}"

            # 5. Observe
            state.add_message("system", f"Observation: {observation}")
            state.increment_turn()

        return state
