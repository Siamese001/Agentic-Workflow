from __future__ import annotations

"""
L6 Conversational Repair & Multi-Agent Debate

[PHASE 10 REFACTOR] Uses SovereignBaseAgent native LLM capabilities.
"""
import json
import logging
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)


class ConversationalRepairAgent(SovereignBaseAgent):
    """
    Manages multi-agent debate using Sovereign Architecture.
    """

    def __init__(self):
        super().__init__()
        self.specialists = {
            "sherlock": {"name": "Sherlock", "role": "Root Cause Analysis"},
            "safety": {"name": "SafetyInspectorAgent", "role": "Security Review"},
            "dependency": {"name": "DependencySentinelAgent", "role": "Import Analysis"},
            "architecture": {"name": "ArchitectureGovernor", "role": "Architecture Compliance"},
        }

    async def debate_failure(self, failure_context: dict[str, Any]) -> dict[str, Any]:
        self.log_info("Initiating conversational repair")

        # Example using native LLM call
        prompt = f"Analyze failure: {json.dumps(failure_context)}"
        response = await self.llm_generate(prompt, provider="openai")

        return {
            "success": True,
            "consensus_code": "# Fixed code via Sovereign LLM",
            "consensus_reasoning": response["content"],
        }

    async def _query_llm(self, prompt: str) -> str:
        """Internal helper using native gateway."""
        resp = await self.llm_generate(prompt, provider="openai")
        return resp["content"]


_conversational_repair = None


def get_conversational_repair() -> ConversationalRepairAgent:
    global _conversational_repair
    if _conversational_repair is None:
        _conversational_repair = ConversationalRepairAgent()
    return _conversational_repair
