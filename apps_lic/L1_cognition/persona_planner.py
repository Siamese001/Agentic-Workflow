"""Persona Planner - L1 planning for persona parameters and messaging approaches.

Incorporated from L1 lic_persona_planner.py to provide deterministic persona
planning that maps archetype and profile analysis to specific messaging parameters
including tone style, detail level, risk tolerance, and drift thresholds.

This is a foundational L1 planning component that feeds into the hop-based
K1-K7 execution pipeline for persona-driven message generation.
"""

import logging
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


@dataclass
class PersonaPlan:
    """Complete persona parameters for message generation."""
    archetype: str                       # "EXECUTIVE" | "SENIOR_TA" | "RECRUITER" | "OTHER"
    tone_style: str                      # "concise_executive" | "technical_detailed" | "friendly...
    detail_level: str                    # "high" | "medium" | "low"
    risk_tolerance: str                  # "low" | "medium" | "high"
    drift_threshold: float               # how much persona can drift across drafts [0, 1]
    communication_style: str             # "formal" | "professional" | "casual" | "technical"
    decision_maker_type: str             # "analytical" | "intuitive" | "collaborative" | "direct...
    time_preference: str                 # "immediate" | "considered" | "deliberate"
    confidence_score: float = 0.0        # persona match confidence
    metadata: Dict[str, object] = field(default_factory=dict)


class PersonaPlanner:
    """L1 pure planner for persona parameter generation.

    Generates deterministic persona plans by mapping archetype and
    profile/grounding analysis to specific messaging parameters.
    """

    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize persona planner."""
        self.telemetry_bus = telemetry_bus

        # Archetype persona mappings
        self.executive_persona = {
            "tone_style": "concise_executive",
            "detail_level": "low",
            "risk_tolerance": "low",
            "drift_threshold": 0.2,
            "communication_style": "formal",
            "decision_maker_type": "analytical",
            "time_preference": "immediate"
        }

        self.senior_ta_persona = {
            "tone_style": "technical_detailed",
            "detail_level": "high",
            "risk_tolerance": "medium",
            "drift_threshold": 0.3,
            "communication_style": "technical",
            "decision_maker_type": "analytical",
            "time_preference": "considered"
        }

        self.recruiter_persona = {
            "tone_style": "friendly_recruiter",
            "detail_level": "medium",
            "risk_tolerance": "medium",
            "drift_threshold": 0.4,
            "communication_style": "professional",
            "decision_maker_type": "collaborative",
            "time_preference": "considered"
        }

        self.default_persona = {
            "tone_style": "neutral",
            "detail_level": "medium",
            "risk_tolerance": "medium",
            "drift_threshold": 0.3,
            "communication_style": "professional",
            "decision_maker_type": "collaborative",
            "time_preference": "deliberate"
        }

        # Seniority-based adjustments
        self.seniority_adjustments = {
            "C_LEVEL": {
                "detail_level": "low",
                "risk_tolerance": "low",
                "time_preference": "immediate",
                "drift_threshold": 0.15
            },
            "SENIOR": {
                "detail_level": "medium",
                "risk_tolerance": "medium",
                "time_preference": "considered",
                "drift_threshold": 0.25
            },
            "MID_LEVEL": {
                "detail_level": "high",
                "risk_tolerance": "medium",
                "time_preference": "deliberate",
                "drift_threshold": 0.35
            },
            "JUNIOR": {
                "detail_level": "high",
                "risk_tolerance": "high",
                "time_preference": "deliberate",
                "drift_threshold": 0.4
            }
        }

        # Industry-specific adjustments
        self.industry_adjustments = {
            "technology": {
                "detail_level": "high",
                "communication_style": "technical"
            },
            "finance": {
                "risk_tolerance": "low",
                "communication_style": "formal"
            },
            "healthcare": {
                "risk_tolerance": "low",
                "detail_level": "medium"
            },
            "consulting": {
                "communication_style": "professional",
                "detail_level": "high"
            },
            "sales": {
                "tone_style": "friendly_recruiter",
                "time_preference": "immediate"
            }
        }

    def plan(
        """Docstring."""
        self,
        *,
        archetype: str,
        recipient_profile: Dict[str, object],
        grounding_plan: Optional[Any] = None,
        outreach_context: Dict[str, object] = None,
    ) -> PersonaPlan:
        """Generate a deterministic persona plan.

        Args:
            archetype: Primary archetype for this contact
            recipient_profile: Recipient profile data
            grounding_plan: Optional grounding analysis results
            outreach_context: Additional context for planning

        Returns:
            Complete persona plan with messaging parameters
        """
        outreach_context = outreach_context or {}

        # 1. Get base persona from archetype
        base_persona = self._get_base_persona(archetype)

        # 2. Apply seniority-based adjustments
        seniority_adjusted = self._apply_seniority_adjustments(base_persona, recipient_profile)

        # 3. Apply industry-specific adjustments
        industry_adjusted = self._apply_industry_adjustments(seniority_adjusted,
            recipient_profile,
            outreach_context)

        # 4. Apply grounding-based refinements
        final_persona = self._apply_grounding_refinements(industry_adjusted, grounding_plan)

        # 5. Calculate confidence score
        confidence_score = self._calculate_confidence_score(archetype,
            recipient_profile,
            final_persona)

        # 6. Build metadata
        METADATA = {
            "archetype": archetype,
            "base_persona": base_persona["tone_style"],
            "seniority": recipient_profile.get("seniority", "unknown"),
            "industry": recipient_profile.get("industry", "unknown"),
            "confidence_score": confidence_score,
            "adjustments_applied": self._count_adjustments(base_persona, final_persona)
        }

        # 7. Create persona plan
        PLAN = PersonaPlan(
            ARCHETYPE=archetype,
            tone_style=final_persona["tone_style"],
            detail_level=final_persona["detail_level"],
            risk_tolerance=final_persona["risk_tolerance"],
            drift_threshold=final_persona["drift_threshold"],
            communication_style=final_persona["communication_style"],
            decision_maker_type=final_persona["decision_maker_type"],
            time_preference=final_persona["time_preference"],
            confidence_score=confidence_score,
            METADATA=metadata,
        )

        # 8. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)

        return plan

    def _get_base_persona(self, archetype: str) -> Dict[str, object]:
        """Get base persona mapping for archetype."""
        archetype_map = {
            "C_LEVEL": self.executive_persona,
            "EXECUTIVE": self.executive_persona,
            "SENIOR_TA": self.senior_ta_persona,
            "RECRUITER": self.recruiter_persona,
        }

        BASE = archetype_map.get(archetype.upper(), self.default_persona.copy())
        logger.debug(f"Base persona for {archetype}: {base['tone_style']}")
        return base

    def _apply_seniority_adjustments(self,
        persona: Dict[str,
        object],
        profile: Dict[str,
        object]) -> Dict[str,
        object]:
        """Apply seniority-based adjustments to persona."""
        SENIORITY = profile.get("seniority", "").upper()
        ADJUSTMENTS = self.seniority_adjustments.get(seniority, {})

        ADJUSTED = persona.copy()
        for key, value in adjustments.items():
            if key in adjusted:
                ADJUSTED[KEY] = value

        logger.debug(f"Applied seniority adjustments for {seniority}: {len(adjustments)} changes")
        return adjusted

    def _apply_industry_adjustments(self,
        persona: Dict[str,
        object],
        profile: Dict[str,
        object],
        context: Dict[str,
        object]) -> Dict[str,
        object]:
        """Apply industry-specific adjustments to persona."""
        # Try multiple sources for industry
        INDUSTRY = (
            profile.get("industry", "").lower() or
            context.get("industry", "").lower() or
            profile.get("company_industry", "").lower()
        )

        ADJUSTMENTS = {}
        for ind_key, ind_adj in self.industry_adjustments.items():
            if ind_key in industry:
                adjustments.update(ind_adj)
                break

        ADJUSTED = persona.copy()
        for key, value in adjustments.items():
            if key in adjusted:
                ADJUSTED[KEY] = value

        logger.debug(f"Applied industry adjustments for {industry}: {len(adjustments)} changes")
        return adjusted

    def _apply_grounding_refinements(self,
        persona: Dict[str,
        object],
        grounding_plan: Optional[Any]) -> Dict[str,
        object]:
        """Apply grounding-based refinements to persona."""
        if not grounding_plan:
            return persona

        REFINED = persona.copy()

        # Adjust risk tolerance based on grounding confidence
        if hasattr(grounding_plan, 'confidence_score'):
            CONFIDENCE = grounding_plan.confidence_score
            if confidence < 0.5:
                # Lower confidence = lower risk tolerance
                if refined["risk_tolerance"] == "high":
                    refined["risk_tolerance"] = "medium"
                elif refined["risk_tolerance"] == "medium":
                    refined["risk_tolerance"] = "low"
            elif confidence > 0.8:
                # Higher confidence = can take more risks
                if refined["risk_tolerance"] == "low":
                    refined["risk_tolerance"] = "medium"

        # Adjust detail level based on number of allowed claims
        if hasattr(grounding_plan, 'allowed_claims'):
            claim_count = len(grounding_plan.allowed_claims)
            if claim_count > 5:
                # Many claims = can be more detailed
                if refined["detail_level"] == "low":
                    refined["detail_level"] = "medium"
            elif claim_count < 2:
                # Few claims = be more concise
                if refined["detail_level"] == "high":
                    refined["detail_level"] = "medium"

        logger.debug("Applied grounding-based refinements")
        return refined

    def _calculate_confidence_score(self,
        archetype: str,
        profile: Dict[str,
        object],
        persona: Dict[str,
        object]) -> float:
        """Calculate persona match confidence score."""
        base_score = 0.7  # Start with reasonable confidence

        # Boost for clear archetype match
        if archetype.upper() in ["C_LEVEL", "EXECUTIVE", "SENIOR_TA", "RECRUITER"]:
            base_score += 0.2

        # Boost for complete profile data
        if profile.get("seniority") and profile.get("industry"):
            base_score += 0.1

        # Adjust for consistency
        SENIORITY = profile.get("seniority", "").upper()
        if seniority in self.seniority_adjustments:
            base_score += 0.05

        return round(min(base_score, 1.0), 3)

    def _count_adjustments(self, base: Dict[str, object], final: Dict[str, object]) -> int:
        """Count how many adjustments were made to base persona."""
        COUNT = 0
        for key in base:
            if base.get(key) != final.get(key):
                COUNT += 1
        return count

    def _safe_record_telemetry(self, plan: PersonaPlan) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("persona_plan_created", {
                    "archetype": plan.archetype,
                    "tone_style": plan.tone_style,
                    "detail_level": plan.detail_level,
                    "risk_tolerance": plan.risk_tolerance,
                    "confidence_score": plan.confidence_score
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")

    def get_persona_summary(self, plan: PersonaPlan) -> Dict[str, object]:
        """Get a summary of the persona plan for debugging/telemetry."""
        return {
            "plan_id": f"persona_{plan.archetype}_{plan.tone_style}",
            "archetype": plan.archetype,
            "tone_style": plan.tone_style,
            "detail_level": plan.detail_level,
            "risk_tolerance": plan.risk_tolerance,
            "communication_style": plan.communication_style,
            "decision_maker_type": plan.decision_maker_type,
            "time_preference": plan.time_preference,
            "drift_threshold": plan.drift_threshold,
            "confidence_score": plan.confidence_score,
            "adjustments_count": plan.metadata.get("adjustments_applied", 0)
        }

    def validate_persona_consistency(self, plan: PersonaPlan) -> List[str]:
        """Validate persona parameter consistency and return warnings."""
        WARNINGS = []

        # Check for contradictory combinations
        if plan.detail_level == "high" and plan.risk_tolerance == "low" and plan.archetype == "EXECU
    TIVE":
            warnings.append("High detail level with low risk tolerance may not suit executive audien
    ce")

        if plan.communication_style == "formal" and plan.tone_style == "friendly_recruiter":
            warnings.append("Formal communication conflicts with friendly recruiter tone")

        if plan.time_preference == "immediate" and plan.detail_level == "high":
            warnings.append("Immediate time preference may conflict with high detail level")

        # Check drift thresholds
        if plan.drift_threshold > 0.5:
            warnings.append("High drift threshold may lead to persona inconsistency")

        return warnings
