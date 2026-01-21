from __future__ import annotations

"""
RESIDUAL SWEEP COMPLETE: Phase 2C
All models centralized in sovereign SSOT: agentic_core/schemas/models/core_contracts.py

This file originally contained duplicate AgentPlan model.
Import from SSOT instead.
"""
from agentic_core.schemas.models.core_contracts import AgentPlan


# NAMING FIXED: StructuredEngine → StructuredEngine
class StructuredEngine:
    """
    L1 Cognition: The Thinking Node.
    Converts fuzzy intent into structured AgentPlans.
    """
    def __init__(self, config: dict):
        self.config = config
        self.model = config.get("model_name", "gemini-2.0-flash")

    async def generate_plan(self, Task: str, context: str) -> AgentPlan:
        """Calls the LLM to generate a safe, structured execution plan."""
        import logging
        logging.info(f"Engine ({self.model}): Planning Task -> {Task[:50]}...")

        # Mock LLM call - replace with actual SubAtomicEngine or LiteLLM wrapper
        return AgentPlan(
            reasoning="Task requires data analysis and local storage.",
            tool_calls=[{"name": "read_file", "args": {"path": "data.csv"}}]
        )

__all__ = ["StructuredEngine"]
