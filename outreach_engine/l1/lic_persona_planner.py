"""LIC Persona Planner - L1 pure planning for persona parameters.

Implements nuclear prompt requirements for deterministic persona planning:
- Define target persona parameters for messaging (tone, risk tolerance, detail depth)
- Pure L1 mapping from archetype + profile/grounding → persona parameters
- Store computed persona profile used by L3 persona drift controller
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class LICPersonaPlan:
    """Complete persona parameters for message generation."""
    archetype: str                       # "EXECUTIVE" | "SENIOR_TA" | "RECRUITER" | "OTHER"
    tone_style: str                      # "concise_executive" | "technical_detailed" | "friendly_recruiter" | "neutral"
    detail_level: str                    # "high" | "medium" | "low"
    risk_tolerance: str                  # "low" | "medium" | "high"
    drift_threshold: float               # how much persona can drift across drafts [0, 1]
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICPersonaPlanner:
    """L1 pure planner for persona parameter generation.
    
    Generates deterministic persona plans by mapping archetype and
    profile/grounding analysis to specific messaging parameters.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize LIC persona planner."""
        self.telemetry_bus = telemetry_bus
        
        # Archetype persona mappings
        self.executive_persona = {
            "tone_style": "concise_executive",
            "detail_level": "low",
            "risk_tolerance": "low",
            "drift_threshold": 0.2,
        }
        
        self.senior_ta_persona = {
            "tone_style": "technical_detailed",
            "detail_level": "high",
            "risk_tolerance": "medium",
            "drift_threshold": 0.3,
        }
        
        self.recruiter_persona = {
            "tone_style": "friendly_recruiter",
            "detail_level": "medium",
            "risk_tolerance": "medium",
            "drift_threshold": 0.4,
        }
        
        self.other_persona = {
            "tone_style": "neutral",
            "detail_level": "medium",
            "risk_tolerance": "medium",
            "drift_threshold": 0.3,
        }
    
    def plan(
        self,
        *,
        archetype: str,
        profile_plan: Optional[Dict[str, Any]] = None,
        grounding_plan: Optional[Dict[str, Any]] = None,
        outreach_context: Dict[str, Any],
    ) -> LICPersonaPlan:
        """Generate a deterministic persona parameter plan.
        
        Args:
            archetype: Target archetype for messaging
            profile_plan: Optional profile analysis plan
            grounding_plan: Optional grounding analysis plan
            outreach_context: Context data for persona customization
            
        Returns:
            Complete persona plan with tone, detail, risk, and drift parameters
        """
        # 1. Get base persona parameters for archetype
        base_params = self._get_base_persona_params(archetype)
        
        # 2. Adjust based on profile analysis
        profile_adjustments = self._get_profile_adjustments(profile_plan, archetype)
        
        # 3. Adjust based on grounding analysis
        grounding_adjustments = self._get_grounding_adjustments(grounding_plan, archetype)
        
        # 4. Apply explicit persona overrides from context
        context_overrides = self._extract_context_overrides(outreach_context)
        
        # 5. Merge all adjustments
        final_params = self._merge_persona_params(
            base_params, profile_adjustments, grounding_adjustments, context_overrides
        )
        
        # 6. Build metadata
        metadata = {
            "base_archetype": archetype,
            "has_profile_adjustments": bool(profile_adjustments),
            "has_grounding_adjustments": bool(grounding_adjustments),
            "has_context_overrides": bool(context_overrides),
        }
        
        # 7. Create persona plan
        plan = LICPersonaPlan(
            archetype=archetype,
            tone_style=final_params["tone_style"],
            detail_level=final_params["detail_level"],
            risk_tolerance=final_params["risk_tolerance"],
            drift_threshold=final_params["drift_threshold"],
            metadata=metadata,
        )
        
        # 8. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)
        
        return plan
    
    def _get_base_persona_params(self, archetype: str) -> Dict[str, Any]:
        """Get base persona parameters for archetype."""
        archetype_upper = archetype.upper()
        
        if archetype_upper == "EXECUTIVE":
            return self.executive_persona.copy()
        elif archetype_upper == "SENIOR_TA":
            return self.senior_ta_persona.copy()
        elif archetype_upper == "RECRUITER":
            return self.recruiter_persona.copy()
        else:
            return self.other_persona.copy()
    
    def _get_profile_adjustments(self, profile_plan: Optional[Dict[str, Any]], archetype: str) -> Dict[str, Any]:
        """Get persona adjustments based on profile analysis."""
        if not profile_plan:
            return {}
        
        adjustments = {}
        confidence = profile_plan.get("confidence_score", 0.5)
        seniority = profile_plan.get("seniority_level", "IC")
        
        # Adjust detail level based on seniority
        if seniority in ["C_LEVEL", "VP"]:
            adjustments["detail_level"] = "low"
        elif seniority in ["DIRECTOR", "SR_MANAGER"]:
            adjustments["detail_level"] = "medium"
        else:
            adjustments["detail_level"] = "high"
        
        # Adjust risk tolerance based on confidence
        if confidence >= 0.8:
            adjustments["risk_tolerance"] = "low"
        elif confidence >= 0.5:
            adjustments["risk_tolerance"] = "medium"
        else:
            adjustments["risk_tolerance"] = "high"
        
        # Adjust drift threshold based on confidence
        if confidence >= 0.8:
            adjustments["drift_threshold"] = 0.1
        elif confidence >= 0.5:
            adjustments["drift_threshold"] = 0.3
        else:
            adjustments["drift_threshold"] = 0.5
        
        return adjustments
    
    def _get_grounding_adjustments(self, grounding_plan: Optional[Dict[str, Any]], archetype: str) -> Dict[str, Any]:
        """Get persona adjustments based on grounding analysis."""
        if not grounding_plan:
            return {}
        
        adjustments = {}
        risk_flags = grounding_plan.get("risk_flags", [])
        alignment_notes = grounding_plan.get("persona_alignment_notes", [])
        
        # Adjust risk tolerance based on risk flags
        if "overclaim_seniority" in risk_flags or "overclaim_breadth" in risk_flags:
            adjustments["risk_tolerance"] = "low"
            adjustments["drift_threshold"] = 0.1
        
        # Adjust detail level based on alignment notes
        if any("technical" in note.lower() for note in alignment_notes):
            adjustments["detail_level"] = "high"
        elif any("executive" in note.lower() for note in alignment_notes):
            adjustments["detail_level"] = "low"
        
        # Adjust tone based on verification concerns
        if "unverified" in " ".join(risk_flags).lower():
            adjustments["tone_style"] = "conservative"
        
        return adjustments
    
    def _extract_context_overrides(self, outreach_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract explicit persona overrides from outreach context."""
        overrides = {}
        
        # Check for explicit tone override
        if "tone_override" in outreach_context:
            tone = outreach_context["tone_override"]
            valid_tones = ["concise_executive", "technical_detailed", "friendly_recruiter", "neutral", "conservative"]
            if tone in valid_tones:
                overrides["tone_style"] = tone
        
        # Check for explicit detail level override
        if "detail_override" in outreach_context:
            detail = outreach_context["detail_override"]
            if detail in ["high", "medium", "low"]:
                overrides["detail_level"] = detail
        
        # Check for explicit risk tolerance override
        if "risk_tolerance_override" in outreach_context:
            risk = outreach_context["risk_tolerance_override"]
            if risk in ["low", "medium", "high"]:
                overrides["risk_tolerance"] = risk
        
        # Check for explicit drift threshold override
        if "drift_threshold_override" in outreach_context:
            threshold = outreach_context["drift_threshold_override"]
            if isinstance(threshold, (int, float)) and 0 <= threshold <= 1:
                overrides["drift_threshold"] = float(threshold)
        
        return overrides
    
    def _merge_persona_params(
        self,
        base_params: Dict[str, Any],
        profile_adjustments: Dict[str, Any],
        grounding_adjustments: Dict[str, Any],
        context_overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge persona parameters with precedence: context > grounding > profile > base."""
        merged = base_params.copy()
        
        # Apply profile adjustments
        merged.update(profile_adjustments)
        
        # Apply grounding adjustments
        merged.update(grounding_adjustments)
        
        # Apply context overrides (highest precedence)
        merged.update(context_overrides)
        
        # Validate final parameters
        merged = self._validate_persona_params(merged)
        
        return merged
    
    def _validate_persona_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize persona parameters."""
        validated = params.copy()
        
        # Validate tone_style
        valid_tones = ["concise_executive", "technical_detailed", "friendly_recruiter", "neutral", "conservative"]
        if validated.get("tone_style") not in valid_tones:
            validated["tone_style"] = "neutral"
        
        # Validate detail_level
        if validated.get("detail_level") not in ["high", "medium", "low"]:
            validated["detail_level"] = "medium"
        
        # Validate risk_tolerance
        if validated.get("risk_tolerance") not in ["low", "medium", "high"]:
            validated["risk_tolerance"] = "medium"
        
        # Validate drift_threshold
        drift_threshold = validated.get("drift_threshold", 0.3)
        if not isinstance(drift_threshold, (int, float)) or not (0 <= drift_threshold <= 1):
            drift_threshold = 0.3
        validated["drift_threshold"] = float(drift_threshold)
        
        return validated
    
    def _safe_record_telemetry(self, plan: LICPersonaPlan) -> None:
        """Record telemetry event safely without breaking planning."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_persona_plan_created",
                layer="L1",
                payload={
                    "archetype": plan.archetype,
                    "tone_style": plan.tone_style,
                    "detail_level": plan.detail_level,
                    "risk_tolerance": plan.risk_tolerance,
                    "drift_threshold": plan.drift_threshold,
                },
            )
        except Exception:
            # Telemetry failures should never break planning logic
            logger.debug("Failed to record telemetry for LIC persona plan")
