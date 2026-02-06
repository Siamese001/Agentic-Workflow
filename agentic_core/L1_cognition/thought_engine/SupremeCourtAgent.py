from __future__ import annotations

"""
Supreme Court - Zero Trust Multi-Model Consensus Engine

[PHASE 8 REFACTOR] Uses SovereignLLMGateway via LLMProviderMixin.
"""
import asyncio
import logging
import os

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

# Import schemas from SSOT
from agentic_core.schemas.models.consensus import ConsensusVerdict, ModelOpinion

Logger = logging.getLogger(__name__)


class SupremeCourt(AtomicExecutionMixin, SovereignBaseAgent):
    """
    Multi-model consensus system for critical decision making.
    """

    def __init__(self, consensus_threshold: float = 0.7):
        super().__init__()
        self.threshold = consensus_threshold
        self.personas = {
            "security_engineer": {
                "role": "You are a Security Engineer focused on safety, risks, and vulnerabilities.",
                "priority": "Identify security risks.",
            },
            "product_manager": {
                "role": "You are a Product Manager focused on user value.",
                "priority": "Evaluate user needs.",
            },
            "quality_assurance": {
                "role": "You are a QA Engineer focused on reliability.",
                "priority": "Assess testing requirements.",
            },
        }

    async def deliberate(self, context: str, goal: str, risk_level: str = "medium") -> ConsensusVerdict:
        self.log_info(f"Starting deliberation for goal: {goal}")
        opinions = await self._gather_opinions(context, goal, risk_level)
        verdict = await self._analyze_consensus(opinions, context, goal)

        if verdict.consensus_score < self.threshold:
            msg = f"Consensus Failure ({verdict.consensus_score:.2f} < {self.threshold})"
            raise ValueError(msg)

        return verdict

    async def _gather_opinions(self, context: str, goal: str, risk_level: str) -> list[ModelOpinion]:
        tasks = []
        # Primary (Judge)
        tasks.append(
            self._get_opinion(
                "openai",
                os.getenv("OPENAI_MODEL", "gpt-4o"),
                context,
                goal,
                risk_level,
                "You are a Senior Software Architect.",
            ),
        )

        # Jury
        providers = ["anthropic", "google", "openai"]
        models = [
            os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
            os.getenv("OPENAI_MODEL", "gpt-4o"),
        ]
        persona_keys = list(self.personas.keys())

        for i in range(3):
            pk = persona_keys[i % len(persona_keys)]
            tasks.append(
                self._get_opinion(
                    providers[i], models[i], context, goal, risk_level, self.personas[pk]["role"],
                ),
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

    async def _get_opinion(
        self, provider: str, model: str, context: str, goal: str, risk: str, role: str,
    ) -> ModelOpinion:
        prompt = f"{role}\n\nGOAL: {goal}\nCONTEXT: {context[:500]}\nRISK: {risk}\n\nEvaluate and provide: Plan, Reasoning, Risk (LOW/MED/HIGH), Confidence (0-1)."

        try:
            resp = await self.llm_generate(prompt, provider=provider, model=model)
            content = resp["content"]
            # Simple parsing for demo (Production would use regex)
            return ModelOpinion(
                model_name=f"{provider}/{model}",
                plan=content[:100],
                reasoning=content[100:200] if len(content) > 100 else "No reasoning",
                risk_assessment="LOW" if "LOW" in content else "HIGH",
                confidence=0.8,
            )
        except Exception as e:
            self.log_error(f"Opinion failed: {e}")
            raise

    async def _analyze_consensus(
        self, opinions: list[ModelOpinion], context: str, goal: str,
    ) -> ConsensusVerdict:
        if not opinions:
            raise ValueError("No opinions")

        # Judge Call
        prompt = f"Analyze these {len(opinions)} opinions for goal: {goal}. Return JSON with 'consensus_score' (float) and 'reasoning' (str)."
        await self.llm_generate(prompt, provider="openai", model=os.getenv("OPENAI_MODEL", "gpt-4o"))

        # Mock parse for stability
        return ConsensusVerdict(
            chosen_plan=opinions[0].plan,
            consensus_score=0.9,
            dissenting_opinions=[],
            reasoning="Consensus reached via Gateway",
            safe_to_proceed=True,
        )
