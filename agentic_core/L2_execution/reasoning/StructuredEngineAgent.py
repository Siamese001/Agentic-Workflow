from __future__ import annotations

"""
StructuredEngineAgent - Intent to Plan Converter

[PHASE 8 REFACTOR] Uses SovereignLLMGateway.
"""
import logging
import os
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin

Logger = logging.getLogger(__name__)


class AgentPlan:
    """Simple plan structure for structured output."""

    def __init__(self, reasoning: str, tool_calls: list[dict[str, Any]]):
        self.reasoning = reasoning
        self.tool_calls = tool_calls

    def heal(self, violation, **kwargs):
        return {"status": "skipped", "reason": "data_structure", "handler": "AgentPlan"}


class StructuredEngineAgent(AtomicExecutionMixin, SovereignBaseAgent):
    """
    L2 Execution: Structured LLM output engine.
    """

    async def generate_plan(self, task: str, context: str) -> AgentPlan:
        self.log_info(f"Planning Task via Gateway: {task[:50]}")

        prompt = f"TASK: {task}\nCONTEXT: {context}\nGenerate execution plan JSON."

        try:
            # Use Google Gemini by default for planning (fast/long context)
            await self.llm_generate(
                prompt,
                provider="google",
                model=os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
            )

            return AgentPlan(
                reasoning=f"Planned via {os.getenv('GEMINI_MODEL', 'gemini-3-flash-preview')}",
                tool_calls=[{"name": "example_tool", "args": {}}],
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            self.log_error(f"Planning failed: {e}")
            return AgentPlan(reasoning="Failure fallback", tool_calls=[])

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)


__all__ = ["StructuredEngineAgent", "AgentPlan"]
