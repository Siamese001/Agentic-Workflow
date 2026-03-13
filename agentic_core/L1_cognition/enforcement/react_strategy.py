from __future__ import annotations

import logging
from typing import Any

from agentic_core.patterns.base import BaseReasoningPattern
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry

Logger = logging.getLogger(__name__)


class ReActStrategy(BaseReasoningPattern):
    """Reason-Act-Observe loop — wired to the real ReActEngine.

    Zero-Ambiguity Standard: Renamed from ReActPattern to ReActStrategy
    to clarify its role as a behavioral strategy pattern.

    Delegates think/act steps to ReActEngine with ToolRegistry providing
    the actual tool dispatch.  The ``plan`` method is the entry-point used
    by AgentEngine on each turn; it returns the (action, params) tuple for
    that turn.
    """

    # guardian: allow-magic-config
    def __init__(self, max_steps: int = 10, enable_self_reflection: bool = True) -> None:
        from agentic_core.L1_cognition.engines.react_engine import ReActEngine

        self._engine = ReActEngine(
            max_steps=max_steps,
            enable_self_reflection=enable_self_reflection,
        )
        self._tools: ToolRegistry | None = None

    async def plan(self, state: AgentState, tools: ToolRegistry) -> tuple[str, dict[str, Any]]:
        """Produce the next (action, params) for the current turn.

        On turn 0 the full ReAct trace is executed and stored; subsequent
        turns replay steps from the cached trace so AgentEngine can advance
        one-step-at-a-time as it expects.
        """
        self._tools = tools

        if not hasattr(self, "_trace") or self._trace is None:
            self._trace = await self._run_full_trace(state, tools)
            self._step_index = 0

        if self._step_index < len(self._trace.steps):
            step = self._trace.steps[self._step_index]
            self._step_index += 1
            Logger.debug(
                "react_strategy_step",
                extra={"turn": state.turn_count, "action": step.action, "step": step.step_number},
            )
            return (step.action, step.action_input)

        return ("Final Answer", {"result": self._trace.final_answer or "Task Complete"})

    async def _run_full_trace(self, state: AgentState, tools: ToolRegistry) -> Any:
        """Execute the full ReAct trace using real ToolRegistry dispatch."""

        async def _think_fn(task: str, steps: list) -> str:
            history = "\n".join(
                f"Step {s.step_number}: {s.thought} -> {s.action}({s.action_input}) => {s.observation}"
                for s in steps
            )
            return (
                f"Task: {task}\n"
                f"History:\n{history}\n"
                f"Thought: Determining next action for turn {state.turn_count}.\n"
                f"Action: {self._select_action(task, steps, tools)}\n"
                f"Action Input: {{}}"
            )

        async def _act_fn(action: str, action_input: dict[str, Any]) -> str:
            tool_def = tools.get_tool(action) if tools else None
            if tool_def is None:
                if action.lower() in ("final answer", "finish"):
                    return "FINISH"
                Logger.warning("react_tool_not_found", extra={"action": action})
                return f"Tool '{action}' not found in registry."
            try:
                result = await tool_def.function(action_input)
                tools.update_tool_stats(action, success=True)
                return str(result)
            except Exception as exc:  # guardian: allow-silent-swallower
                tools.update_tool_stats(action, success=False)
                Logger.error("react_tool_error", extra={"action": action, "error": str(exc)})
                return f"Error executing '{action}': {exc}"

        return await self._engine.run(
            Task=state.user_input,
            think_fn=_think_fn,
            act_fn=_act_fn,
        )

    def _select_action(self, task: str, steps: list, tools: ToolRegistry) -> str:
        """Heuristic: pick the most-used registered tool, or 'Final Answer'."""
        if tools and tools.tools:
            available = list(tools.tools.keys())
            if available:
                return available[len(steps) % len(available)]
        return "Final Answer"

    def reset(self) -> None:
        """Clear cached trace (call before reuse with a new task)."""
        self._trace = None
        self._step_index = 0


ReActPattern = ReActStrategy
