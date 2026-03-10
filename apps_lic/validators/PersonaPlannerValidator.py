from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Persona Planner - L1 planning for persona parameters and messaging approaches.

Incorporated from L1 lic_persona_planner.py to provide deterministic persona
planning that maps Archetype and profile analysis to specific messaging parameters
including tone style, detail level, risk tolerance, and drift thresholds.

This is a foundational L1 planning component that feeds into the hop-based
K1-K7 execution pipeline for persona-driven message generation.
"""

Logger: Any = logging.getLogger(__name__)


@dataclass
class PersonaPlan:
    """Complete persona parameters for message generation."""

    Archetype: str
    tone_style: str
    detail_level: str
    risk_tolerance: str
    drift_threshold: float
    communication_style: str
    decision_maker_type: str
    time_preference: str
    confidence_score: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)


class PersonaPlanner:
    """L1 pure planner for persona parameter generation.

    Generates deterministic persona plans by mapping Archetype and
    profile/grounding analysis to specific messaging parameters.
    """

    def __init__(self, telemetry_bus: Any | None = None) -> None:
        """Initialize persona planner."""
        self.telemetry_bus = telemetry_bus
        self.executive_persona = {
            "tone_style": "concise_executive",
            "detail_level": "low",
            "risk_tolerance": "low",
            "drift_threshold": 0.2,
            "communication_style": "formal",
            "decision_maker_type": "analytical",
            "time_preference": "immediate",
        }
        self.senior_ta_persona = {
            "tone_style": "technical_detailed",
            "detail_level": "high",
            "risk_tolerance": "medium",
            "drift_threshold": 0.3,
            "communication_style": "technical",
            "decision_maker_type": "analytical",
            "time_preference": "considered",
        }
        self.recruiter_persona = {
            "tone_style": "friendly_recruiter",
            "detail_level": "medium",
            "risk_tolerance": "medium",
            "drift_threshold": 0.4,
            "communication_style": "professional",
            "decision_maker_type": "collaborative",
            "time_preference": "considered",
        }
        self.default_persona = {
            "tone_style": "neutral",
            "detail_level": "medium",
            "risk_tolerance": "medium",
            "drift_threshold": 0.3,
            "communication_style": "professional",
            "decision_maker_type": "collaborative",
            "time_preference": "deliberate",
        }
        self.seniority_adjustments = {
            "C_LEVEL": {
                "detail_level": "low",
                "risk_tolerance": "low",
                "time_preference": "immediate",
                "drift_threshold": 0.15,
            },
            "SENIOR": {
                "detail_level": "medium",
                "risk_tolerance": "medium",
                "time_preference": "considered",
                "drift_threshold": 0.25,
            },
            "MID_LEVEL": {
                "detail_level": "high",
                "risk_tolerance": "medium",
                "time_preference": "deliberate",
                "drift_threshold": 0.35,
            },
            "JUNIOR": {
                "detail_level": "high",
                "risk_tolerance": "high",
                "time_preference": "deliberate",
                "drift_threshold": 0.4,
            },
        }
        self.industry_adjustments = {
            "technology": {"detail_level": "high", "communication_style": "technical"},
            "finance": {"risk_tolerance": "low", "communication_style": "formal"},
            "healthcare": {"risk_tolerance": "low", "detail_level": "medium"},
            "consulting": {"communication_style": "professional", "detail_level": "high"},
            "sales": {"tone_style": "friendly_recruiter", "time_preference": "immediate"},
        }

    def plan(
        self,
        *,
        Archetype: str,
        recipient_profile: dict[str, object],
        grounding_plan: Any | None = None,
        outreach_context: dict[str, object] = None,
    ) -> PersonaPlan:
        """Generate a deterministic persona plan.

        Args:
            Archetype: Primary Archetype for this contact
            recipient_profile: Recipient profile data
            grounding_plan: Optional grounding analysis results
            outreach_context: Additional context for planning

        Returns:
            Complete persona plan with messaging parameters
        """
        outreach_context: Any = outreach_context or {}
        base_persona: Any = self._get_base_persona(Archetype)
        seniority_adjusted: Any = self._apply_seniority_adjustments(base_persona, recipient_profile)
        industry_adjusted: Any = self._apply_industry_adjustments(
            seniority_adjusted,
            recipient_profile,
            outreach_context,
        )
        final_persona: Any = self._apply_grounding_refinements(industry_adjusted, grounding_plan)
        confidence_score: Any = self._calculate_confidence_score(Archetype, recipient_profile, final_persona)
        metadata: Any = {
            "Archetype": Archetype,
            "base_persona": base_persona["tone_style"],
            "seniority": recipient_profile.get("seniority", "unknown"),
            "industry": recipient_profile.get("industry", "unknown"),
            "confidence_score": confidence_score,
            "adjustments_applied": self._count_adjustments(base_persona, final_persona),
        }
        plan: Any = PersonaPlan(
            Archetype=Archetype,
            tone_style=final_persona["tone_style"],
            detail_level=final_persona["detail_level"],
            risk_tolerance=final_persona["risk_tolerance"],
            drift_threshold=final_persona["drift_threshold"],
            communication_style=final_persona["communication_style"],
            decision_maker_type=final_persona["decision_maker_type"],
            time_preference=final_persona["time_preference"],
            confidence_score=confidence_score,
            metadata=metadata,
        )
        self._safe_record_telemetry(plan)
        return plan

    def _get_base_persona(self, Archetype: str) -> dict[str, object]:
        """Get base persona mapping for Archetype."""
        archetype_map = {
            "C_LEVEL": self.executive_persona,
            "EXECUTIVE": self.executive_persona,
            "SENIOR_TA": self.senior_ta_persona,
            "RECRUITER": self.recruiter_persona,
        }
        base = archetype_map.get(Archetype.upper(), self.default_persona.copy())
        Logger.debug(f"Base persona for {Archetype}: {base['tone_style']}")
        return base

    def _apply_seniority_adjustments(
        self,
        persona: dict[str, object],
        profile: dict[str, object],
    ) -> dict[str, object]:
        """Apply seniority-based adjustments to persona."""
        seniority = profile.get("seniority", "").upper()
        adjustments = self.seniority_adjustments.get(seniority, {})
        adjusted = persona.copy()
        for key, value in adjustments.items():
            if key in adjusted:
                adjusted[key] = value
        Logger.debug(f"Applied seniority adjustments for {seniority}: {len(adjustments)} changes")
        return adjusted

    def _apply_industry_adjustments(
        self,
        persona: dict[str, object],
        profile: dict[str, object],
        context: dict[str, object],
    ) -> dict[str, object]:
        """Apply industry-specific adjustments to persona."""
        industry = (
            profile.get("industry", "").lower()
            or context.get("industry", "").lower()
            or profile.get("company_industry", "").lower()
        )
        adjustments = {}
        for ind_key, ind_adj in self.industry_adjustments.items():
            if ind_key in industry:
                adjustments.update(ind_adj)
                break
        adjusted = persona.copy()
        for key, value in adjustments.items():
            if key in adjusted:
                adjusted[key] = value
        Logger.debug(f"Applied industry adjustments for {industry}: {len(adjustments)} changes")
        return adjusted

    def _apply_grounding_refinements(
        self,
        persona: dict[str, object],
        grounding_plan: Any | None,
    ) -> dict[str, object]:
        """Apply grounding-based refinements to persona."""
        if not grounding_plan:
            return persona
        refined = persona.copy()
        if hasattr(grounding_plan, "confidence_score"):
            confidence = grounding_plan.confidence_score
            if confidence < 0.5:
                if refined["risk_tolerance"] == "high":
                    refined["risk_tolerance"] = "medium"
                elif refined["risk_tolerance"] == "medium":
                    refined["risk_tolerance"] = "low"
            elif confidence > 0.8:
                if refined["risk_tolerance"] == "low":
                    refined["risk_tolerance"] = "medium"
        if hasattr(grounding_plan, "allowed_claims"):
            claim_count = len(grounding_plan.allowed_claims)
            if claim_count > 5:
                if refined["detail_level"] == "low":
                    refined["detail_level"] = "medium"
            elif claim_count < 2:
                if refined["detail_level"] == "high":
                    refined["detail_level"] = "medium"
        Logger.debug("Applied grounding-based refinements")
        return refined

    def _calculate_confidence_score(
        self,
        Archetype: str,
        profile: dict[str, object],
        persona: dict[str, object],
    ) -> float:
        """Calculate persona match confidence score."""
        base_score = 0.7
        if Archetype.upper() in ["C_LEVEL", "EXECUTIVE", "SENIOR_TA", "RECRUITER"]:
            base_score += 0.2
        if profile.get("seniority") and profile.get("industry"):
            base_score += 0.1
        seniority = profile.get("seniority", "").upper()
        if seniority in self.seniority_adjustments:
            base_score += 0.05
        return round(min(base_score, 1.0), 3)

    def _count_adjustments(self, base: dict[str, object], final: dict[str, object]) -> int:
        """Count how many adjustments were made to base persona."""
        count = 0
        for key in base:
            if base.get(key) != final.get(key):
                count += 1
        return count

    def _safe_record_telemetry(self, plan: PersonaPlan) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record(
                    "persona_plan_created",
                    {
                        "Archetype": plan.Archetype,
                        "tone_style": plan.tone_style,
                        "detail_level": plan.detail_level,
                        "risk_tolerance": plan.risk_tolerance,
                        "confidence_score": plan.confidence_score,
                    },
                )
        except Exception as e:
            Logger.debug(f"Failed to record telemetry: {e}")

    def get_persona_summary(self, plan: PersonaPlan) -> dict[str, object]:
        """Get a summary of the persona plan for debugging/telemetry."""
        return {
            "plan_id": f"persona_{plan.Archetype}_{plan.tone_style}",
            "Archetype": plan.Archetype,
            "tone_style": plan.tone_style,
            "detail_level": plan.detail_level,
            "risk_tolerance": plan.risk_tolerance,
            "communication_style": plan.communication_style,
            "decision_maker_type": plan.decision_maker_type,
            "time_preference": plan.time_preference,
            "drift_threshold": plan.drift_threshold,
            "confidence_score": plan.confidence_score,
            "adjustments_count": plan.metadata.get("adjustments_applied", 0),
        }

    def validate_persona_consistency(self, plan: PersonaPlan) -> list[str]:
        """Validate persona parameter consistency and return warnings."""
        warnings: Any = []
        if plan.detail_level == "high" and plan.risk_tolerance == "low" and (plan.Archetype == "EXECUTIVE"):
            warnings.append("High detail level with low risk tolerance may not suit executive audience")
        if plan.communication_style == "formal" and plan.tone_style == "friendly_recruiter":
            warnings.append("Formal communication conflicts with friendly recruiter tone")
        if plan.time_preference == "immediate" and plan.detail_level == "high":
            warnings.append("Immediate time preference may conflict with high detail level")
        if plan.drift_threshold > 0.5:
            warnings.append("High drift threshold may lead to persona inconsistency")
        return warnings
