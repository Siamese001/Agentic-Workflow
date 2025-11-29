"""LIC Grounding Planner - L1 pure planning for sender capability analysis.

Implements nuclear prompt requirements for deterministic grounding planning:
- Analyze sender capabilities and align them with LIC archetype + role
- Identify potential overclaims and tag capabilities by verification level
- Pure L1 planning with no external calls or execution
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class LICSenderCapability:
    """Individual sender capability extracted from resume features."""
    id: str                              # stable identifier
    description: str                     # capability description
    verification_level: str              # "high", "medium", "unverified"
    strength_score: float               # capability strength [0, 1]
    seniority_claim: str                 # "executive", "manager", "ic", "unknown"
    risk_flags: List[str]                # identified risk flags
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LICGroundingPlan:
    """Complete sender grounding analysis plan."""
    allowed_claims: List[LICSenderCapability]    # capabilities that can be claimed
    disallowed_claims: List[LICSenderCapability] # capabilities that should not be claimed
    persona_alignment_notes: List[str]           # alignment observations
    risk_flags: List[str]                        # overall risk flags
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICGroundingPlanner:
    """L1 pure planner for sender capability analysis and grounding.
    
    Generates deterministic grounding plans by analyzing resume features
    and identifying safe claims vs potential overclaims.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize LIC grounding planner."""
        self.telemetry_bus = telemetry_bus
        
        # Seniority claim indicators
        self.executive_indicators = {
            "led", "managed", "directed", "oversaw", "executive", "leadership",
            "vp", "director", "head", "chief", "c-level", "president"
        }
        
        self.manager_indicators = {
            "managed", "led", "coordinated", "supervised", "mentored",
            "team lead", "manager", "supervisor"
        }
        
        self.ic_indicators = {
            "developed", "implemented", "built", "created", "designed",
            "engineered", "programmed", "analyzed", "optimized"
        }
        
        # Risk flag patterns
        self.overclaim_patterns = [
            "led the entire company", "ran all operations", "managed whole organization",
            "responsible for all", "owned the entire", "controlled the complete"
        ]
        
        self.unverified_patterns = [
            "estimated", "approximately", "roughly", "about", "potential",
            "could have", "might have", "estimated to"
        ]
    
    def plan(
        self,
        *,
        resume_features: Dict[str, Any],
        outreach_context: Dict[str, Any],
    ) -> LICGroundingPlan:
        """Generate a deterministic grounding analysis plan.
        
        Args:
            resume_features: Pre-computed resume signals (achievements, skills, etc.)
            outreach_context: Context data including target archetype and role
            
        Returns:
            Complete grounding plan with allowed/disallowed claims and risk flags
        """
        # 1. Extract capabilities from resume features
        capabilities = self._extract_capabilities(resume_features)
        
        # 2. Analyze each capability for risk and verification
        analyzed_capabilities = self._analyze_capabilities(capabilities)
        
        # 3. Separate allowed vs disallowed claims
        allowed_claims, disallowed_claims = self._classify_claims(analyzed_capabilities)
        
        # 4. Generate persona alignment notes
        alignment_notes = self._generate_alignment_notes(analyzed_capabilities, outreach_context)
        
        # 5. Collect overall risk flags
        risk_flags = self._collect_risk_flags(analyzed_capabilities)
        
        # 6. Build metadata
        metadata = {
            "total_capabilities": len(analyzed_capabilities),
            "allowed_claims": len(allowed_claims),
            "disallowed_claims": len(disallowed_claims),
            "risk_flag_count": len(risk_flags),
        }
        
        # 7. Create grounding plan
        plan = LICGroundingPlan(
            allowed_claims=allowed_claims,
            disallowed_claims=disallowed_claims,
            persona_alignment_notes=alignment_notes,
            risk_flags=risk_flags,
            metadata=metadata,
        )
        
        # 8. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)
        
        return plan
    
    def _extract_capabilities(self, resume_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract raw capabilities from resume features."""
        capabilities = []
        
        # Extract from achievements
        achievements = resume_features.get("achievements", [])
        for i, achievement in enumerate(achievements):
            if isinstance(achievement, dict):
                capabilities.append({
                    "id": f"achievement_{i}",
                    "description": achievement.get("text", ""),
                    "source": "achievement",
                    "impact_type": achievement.get("impact_type", "general"),
                    "seniority_signal": achievement.get("seniority_signal", "unknown"),
                })
        
        # Extract from skills
        skills = resume_features.get("skills", [])
        for i, skill in enumerate(skills):
            capabilities.append({
                "id": f"skill_{i}",
                "description": skill,
                "source": "skill",
                "impact_type": "skill",
                "seniority_signal": "unknown",
            })
        
        # Extract from experience summary
        summary = resume_features.get("summary", "")
        if summary:
            capabilities.append({
                "id": "summary_0",
                "description": summary,
                "source": "summary",
                "impact_type": "general",
                "seniority_signal": "unknown",
            })
        
        return capabilities
    
    def _analyze_capabilities(self, capabilities: List[Dict[str, Any]]) -> List[LICSenderCapability]:
        """Analyze capabilities for verification level and risk flags."""
        analyzed = []
        
        for cap in capabilities:
            description = cap["description"].lower()
            
            # Determine verification level
            verification_level = self._determine_verification_level(description, cap)
            
            # Calculate strength score
            strength_score = self._calculate_strength_score(description, cap)
            
            # Determine seniority claim
            seniority_claim = self._determine_seniority_claim(description, cap)
            
            # Identify risk flags
            risk_flags = self._identify_risk_flags(description, cap)
            
            analyzed_capability = LICSenderCapability(
                id=cap["id"],
                description=cap["description"],
                verification_level=verification_level,
                strength_score=strength_score,
                seniority_claim=seniority_claim,
                risk_flags=risk_flags,
                metadata={
                    "source": cap["source"],
                    "impact_type": cap["impact_type"],
                    "raw_seniority_signal": cap["seniority_signal"],
                },
            )
            
            analyzed.append(analyzed_capability)
        
        return analyzed
    
    def _determine_verification_level(self, description: str, cap: Dict[str, Any]) -> str:
        """Determine verification level for a capability."""
        # High verification for specific, measurable achievements
        if any(char in description for char in ["%", "$", "x", "k", "m"]):
            return "high"
        
        # High verification for achievement source with seniority signal
        if cap["source"] == "achievement" and cap["seniority_signal"] != "unknown":
            return "high"
        
        # Medium verification for skills and general claims
        if cap["source"] in ["skill", "achievement"]:
            return "medium"
        
        # Low verification for summary claims
        if cap["source"] == "summary":
            return "unverified"
        
        # Check for unverified patterns
        if any(pattern in description for pattern in self.unverified_patterns):
            return "unverified"
        
        return "medium"
    
    def _calculate_strength_score(self, description: str, cap: Dict[str, Any]) -> float:
        """Calculate strength score for a capability."""
        score = 0.5  # Base score
        
        # Boost for metrics and quantification
        if any(char in description for char in ["%", "$", "x", "k", "m"]):
            score += 0.3
        
        # Boost for action verbs
        action_verbs = ["led", "built", "created", "developed", "implemented", "achieved"]
        if any(verb in description for verb in action_verbs):
            score += 0.1
        
        # Boost for seniority-aligned claims
        if cap["seniority_signal"] != "unknown":
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_seniority_claim(self, description: str, cap: Dict[str, Any]) -> str:
        """Determine seniority claim from description."""
        # Use explicit seniority signal if available
        if cap["seniority_signal"] != "unknown":
            return cap["seniority_signal"]
        
        # Analyze description for seniority indicators
        if any(indicator in description for indicator in self.executive_indicators):
            return "executive"
        elif any(indicator in description for indicator in self.manager_indicators):
            return "manager"
        elif any(indicator in description for indicator in self.ic_indicators):
            return "ic"
        
        return "unknown"
    
    def _identify_risk_flags(self, description: str, cap: Dict[str, Any]) -> List[str]:
        """Identify risk flags for a capability."""
        risk_flags = []
        
        # Check for overclaim patterns
        if any(pattern in description for pattern in self.overclaim_patterns):
            risk_flags.append("overclaim_breadth")
        
        # Check for seniority mismatches
        if cap["seniority_signal"] == "ic" and any(indicator in description for indicator in self.executive_indicators):
            risk_flags.append("overclaim_seniority")
        
        # Check for unverified metrics
        if any(pattern in description for pattern in self.unverified_patterns):
            risk_flags.append("unverified_metric")
        
        # Check for vague claims
        vague_indicators = ["various", "multiple", "several", "many", "numerous"]
        if any(indicator in description for indicator in vague_indicators):
            risk_flags.append("vague_claim")
        
        return risk_flags
    
    def _classify_claims(self, capabilities: List[LICSenderCapability]) -> Tuple[List[LICSenderCapability], List[LICSenderCapability]]:
        """Classify capabilities into allowed vs disallowed claims."""
        allowed = []
        disallowed = []
        
        for cap in capabilities:
            # Disallowed if high-risk flags present
            if any(flag in cap.risk_flags for flag in ["overclaim_breadth", "overclaim_seniority"]):
                disallowed.append(cap)
            # Disallowed if very low verification and low strength
            elif cap.verification_level == "unverified" and cap.strength_score < 0.3:
                disallowed.append(cap)
            # Otherwise allowed
            else:
                allowed.append(cap)
        
        return allowed, disallowed
    
    def _generate_alignment_notes(self, capabilities: List[LICSenderCapability], outreach_context: Dict[str, Any]) -> List[str]:
        """Generate persona alignment notes."""
        notes = []
        
        target_archetype = outreach_context.get("archetype", "").upper()
        
        # Count seniority claims
        executive_claims = sum(1 for cap in capabilities if cap.seniority_claim == "executive")
        manager_claims = sum(1 for cap in capabilities if cap.seniority_claim == "manager")
        ic_claims = sum(1 for cap in capabilities if cap.seniority_claim == "ic")
        
        # Generate archetype-specific notes
        if target_archetype == "EXECUTIVE":
            if executive_claims == 0:
                notes.append("No executive-level leadership claims detected")
            elif executive_claims < 2:
                notes.append("Limited executive leadership experience")
            else:
                notes.append("Strong executive leadership profile")
        
        elif target_archetype == "SENIOR_TA":
            if ic_claims == 0:
                notes.append("No technical implementation claims detected")
            elif manager_claims > executive_claims:
                notes.append("Profile leans more toward management than technical leadership")
            else:
                notes.append("Strong technical leadership profile")
        
        elif target_archetype == "RECRUITER":
            if manager_claims > 0:
                notes.append("Management experience relevant for recruiting role")
            else:
                notes.append("Focus on individual contributor experience")
        
        # Add risk-related notes
        high_risk_caps = [cap for cap in capabilities if cap.risk_flags]
        if len(high_risk_caps) > len(capabilities) * 0.3:
            notes.append("High proportion of risky claims detected")
        
        # Add verification notes
        high_verification_caps = [cap for cap in capabilities if cap.verification_level == "high"]
        if len(high_verification_caps) > len(capabilities) * 0.5:
            notes.append("Strong verification of key claims")
        elif len(high_verification_caps) < len(capabilities) * 0.2:
            notes.append("Limited verification of claims")
        
        return notes
    
    def _collect_risk_flags(self, capabilities: List[LICSenderCapability]) -> List[str]:
        """Collect all unique risk flags from capabilities."""
        all_flags = set()
        for cap in capabilities:
            all_flags.update(cap.risk_flags)
        return list(all_flags)
    
    def _safe_record_telemetry(self, plan: LICGroundingPlan) -> None:
        """Record telemetry event safely without breaking planning."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_grounding_plan_created",
                layer="L1",
                payload={
                    "total_capabilities": plan.metadata["total_capabilities"],
                    "allowed_claims": plan.metadata["allowed_claims"],
                    "disallowed_claims": plan.metadata["disallowed_claims"],
                    "risk_flag_count": plan.metadata["risk_flag_count"],
                },
            )
        except Exception:
            # Telemetry failures should never break planning logic
            logger.debug("Failed to record telemetry for LIC grounding plan")
