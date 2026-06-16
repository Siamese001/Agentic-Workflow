"""Deterministic governance shield for apps_lic outreach.

The shield no longer initializes or calls any local LLM runtime. It provides a
small rule-backed audit surface used by the control plane.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from apps_lic.utils.lic_agent_base_util import LICAgentBase


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class RiskProfile:
    level: RiskLevel
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class SafetyProtocol:
    level: RiskLevel
    controls: tuple[str, ...]
    blocked: bool = False


@dataclass
class GovernanceShieldAgent(LICAgentBase):
    """Rule-backed governance shield for outreach drafts."""

    risk_thresholds: dict[str, float] = field(
        default_factory=lambda: {"max_confidence_score": 0.95, "min_safety_level": 0.8},
    )

    def __post_init__(self) -> None:
        super().__post_init__()
        self.naive_patterns = {
            "absolute_accuracy": (
                "100% accurate",
                "perfect accuracy",
                "zero errors",
                "flawless performance",
                "always correct",
            ),
            "unsupported_claims": (
                "guaranteed",
                "proven to",
                "will transform",
                "revolutionary",
            ),
            "sales_pitch": (
                "synergies",
                "discuss opportunities",
                "enhance your initiatives",
                "my expertise",
            ),
        }

    def evaluate(self, content: str) -> dict[str, Any]:
        """Return a compact deterministic shield verdict."""
        flags = self._flags(content)
        return {
            "passed": not flags,
            "flags": list(flags),
            "risk_level": self._risk_level(flags).value,
            "recommended_text": self.audit_outreach(content),
        }

    def generate_safety_protocol(self, risk_profile: RiskProfile) -> SafetyProtocol:
        controls = ["no_auto_send", "claim_grounding_required", "human_review_available"]
        if risk_profile.level == RiskLevel.HIGH:
            controls.append("block_until_evidence_review")
        return SafetyProtocol(
            level=risk_profile.level,
            controls=tuple(controls),
            blocked=risk_profile.level == RiskLevel.HIGH,
        )

    def audit_outreach(self, email_draft: str) -> str:
        """Replace naive or salesy phrasing with restrained alternatives."""
        content = str(email_draft or "")
        replacements = {
            "100% accurate": "designed for measurable accuracy",
            "perfect accuracy": "high-confidence performance with validation",
            "zero errors": "reduced error risk with review controls",
            "flawless performance": "reliable performance with monitoring",
            "always correct": "validated before use",
            "guaranteed": "intended",
            "will transform": "can support",
            "revolutionary": "material",
            "synergies": "fit",
            "discuss opportunities": "compare fit",
            "enhance your initiatives": "support the work",
            "my expertise": "my background",
        }
        for pattern, replacement in replacements.items():
            content = re.sub(re.escape(pattern), replacement, content, flags=re.IGNORECASE)
        return content

    async def analyze_governance(self, content: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Async deterministic governance analysis for callers expecting awaitable output."""
        del context
        verdict = self.evaluate(content)
        return {
            "success": True,
            "analysis": verdict,
            "model_used": "deterministic_governance_shield",
            "latency_ms": 0.0,
        }

    def _flags(self, content: str) -> tuple[str, ...]:
        lowered = str(content or "").lower()
        flags: list[str] = []
        for group, patterns in self.naive_patterns.items():
            if any(pattern.lower() in lowered for pattern in patterns):
                flags.append(group)
        return tuple(dict.fromkeys(flags))

    @staticmethod
    def _risk_level(flags: tuple[str, ...]) -> RiskLevel:
        if {"absolute_accuracy", "unsupported_claims"} & set(flags):
            return RiskLevel.HIGH
        if flags:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW


def create_governance_shield_agent() -> GovernanceShieldAgent:
    """Create a GovernanceShieldAgent instance."""
    return GovernanceShieldAgent()


__all__ = [
    "GovernanceShieldAgent",
    "RiskLevel",
    "RiskProfile",
    "SafetyProtocol",
    "create_governance_shield_agent",
]
