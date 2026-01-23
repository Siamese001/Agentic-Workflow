from __future__ import annotations

"""
StructuredEngine - Intent to Plan Converter

[PHASE 8 REFACTOR] Uses SovereignLLMGateway.
"""
import logging
from typing import Any
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)


class AgentPlan:
    """Simple plan structure for structured output."""

    def __init__(self, reasoning: str, tool_calls: list[dict[str, Any]]):
        self.reasoning = reasoning
        self.tool_calls = tool_calls


class StructuredEngine(SovereignBaseAgent):
    """
    L2 Execution: Structured LLM output engine.
    """

    async def generate_plan(self, task: str, context: str) -> AgentPlan:
        self.log_info(f"Planning Task via Gateway: {task[:50]}")

        prompt = f"TASK: {task}\nCONTEXT: {context}\nGenerate execution plan JSON."

        try:
            # Use Google Gemini by default for planning (fast/long context)
            resp = await self.llm_generate(
                prompt, provider="google", model=self.config.google_model
            )

            return AgentPlan(
                reasoning=f"Planned via {self.config.google_model}",
                tool_calls=[{"name": "example_tool", "args": {}}],
            )
        except Exception as e:
            self.log_error(f"Planning failed: {e}")
            return AgentPlan(reasoning="Failure fallback", tool_calls=[])


__all__ = ["StructuredEngine", "AgentPlan"]
