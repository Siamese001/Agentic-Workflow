"""C3 Healing Router - Tier-based routing.

10C-REQ-137: Route to Local Agent, Qwen_vLLM, or Gemini_2.5_Pro based on confidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .confidence_scorer import ConfidenceScore, HealTier
from .failure_signal import FailureSignal


@dataclass
class RoutingDecision:
    """Healing routing decision."""

    tier: HealTier
    target_model: str
    timeout_seconds: int
    max_tokens: int
    requires_sandbox: bool
    reasoning: str


class HealingRouter:
    """C3 Healing router based on confidence tiers.

    10C-REQ-137: High->Local Agent Medium->Qwen_vLLM Low->Gemini_2.5_Pro.

    **HITL DECISION REQUIRED**: Model assignments and resource limits.
    """

    # HITL-10C-003: Model assignments require stakeholder approval
    TIER_CONFIG: dict[HealTier, dict[str, Any]] = {
        HealTier.HIGH: {
            "model": "local_deterministic",
            "timeout": 5,
            "max_tokens": 1000,
            "sandbox": False,
        },
        HealTier.MEDIUM: {
            "model": "qwen_vllm",
            "timeout": 30,
            "max_tokens": 4000,
            "sandbox": True,
        },
        HealTier.LOW: {
            "model": "gemini_2.5_pro",
            "timeout": 60,
            "max_tokens": 8000,
            "sandbox": True,
        },
        HealTier.HITL: {
            "model": "human_review",
            "timeout": 86400,  # 24 hours
            "max_tokens": 0,
            "sandbox": False,
        },
    }

    def __init__(self) -> None:
        self._tier_stats: dict[HealTier, int] = {tier: 0 for tier in HealTier}

    def route(self, score: ConfidenceScore, signal: FailureSignal) -> RoutingDecision:
        """Route healing to appropriate tier."""
        config = self.TIER_CONFIG.get(score.tier, self.TIER_CONFIG[HealTier.HITL])

        self._tier_stats[score.tier] += 1

        return RoutingDecision(
            tier=score.tier,
            target_model=config["model"],
            timeout_seconds=config["timeout"],
            max_tokens=config["max_tokens"],
            requires_sandbox=config["sandbox"],
            reasoning=score.reasoning,
        )

    def get_tier_stats(self) -> dict[str, int]:
        """Get routing statistics by tier."""
        return {tier.name: count for tier, count in self._tier_stats.items()}

    def update_tier_config(
        self,
        tier: HealTier,
        model: str | None = None,
        timeout: int | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """Update tier configuration.

        HITL-10C-003: Changes require approval.
        """
        if model:
            self.TIER_CONFIG[tier]["model"] = model
        if timeout:
            self.TIER_CONFIG[tier]["timeout"] = timeout
        if max_tokens:
            self.TIER_CONFIG[tier]["max_tokens"] = max_tokens
