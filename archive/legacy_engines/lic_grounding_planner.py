"""Grounding Planner - L1 planning for sender capability analysis and grounding.

Incorporated from L1 lic_grounding_planner.py to provide deterministic grounding
analysis for sender capabilities, identifying safe claims vs potential overclaims
to ensure message content is properly grounded in factual data.

This is a foundational L1 planning component that feeds into the hop-based
K1-K7 execution pipeline.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SenderCapability:
    """Individual sender capability extracted from resume features."""
    id: str                              # stable identifier
    description: str                     # capability description
    verification_level: str              # "high", "medium", "unverified"
    strength_score: float               # capability strength [0, 1]
    seniority_claim: str                 # "executive", "manager", "ic", "unknown"
    risk_flags: List[str]                # identified risk flags
    source: str                          # source of capability (achievement, skill, experience)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GroundingPlan:
    """Complete sender grounding analysis plan."""
    allowed_claims: List[SenderCapability]    # capabilities that can be claimed
    disallowed_claims: List[SenderCapability] # capabilities that should not be claimed
    persona_alignment_notes: List[str]       # alignment observations
    risk_flags: List[str]                    # overall risk flags
    confidence_score: float = 0.0            # overall grounding confidence
    metadata: Dict[str, Any] = field(default_factory=dict)


class GroundingPlanner:
    """L1 pure planner for sender capability analysis and grounding.
    
    Generates deterministic grounding plans by analyzing resume features
    and identifying safe claims vs potential overclaims.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize grounding planner."""
        self.telemetry_bus = telemetry_bus
        
        # Seniority claim indicators
        self.executive_indicators = {
            "led", "managed", "directed", "oversaw", "executive", "leadership",
            "vp", "director", "head", "chief", "c-level", "president",
            "strategic", "board", "governance", "enterprise"
        }
        
        self.manager_indicators = {
            "managed", "led", "coordinated", "supervised", "mentored",
            "team lead", "manager", "supervisor", "team", "group"
        }
        
        self.ic_indicators = {
            "developed", "implemented", "built", "created", "designed",
            "engineered", "programmed", "analyzed", "optimized", "technical"
        }
        
        # Risk flag patterns
        self.overclaim_patterns = [
            "led the entire company", "ran all operations", "managed whole organization",
            "responsible for all", "owned the entire", "controlled the complete",
            "single-handedly", "solely responsible", "only person"
        ]
        
        self.unverified_patterns = [
            "estimated", "approximately", "roughly", "about", "potential",
            "could have", "might have", "estimated to", "believed to"
        ]
        
        # Verification indicators
        self.high_verification_indicators = {
            "achieved", "completed", "delivered", "implemented", "launched",
            "increased", "decreased", "improved", "reduced", "generated"
        }
        
        self.medium_verification_indicators = {
            "contributed", "assisted", "supported", "helped", "participated",
            "involved in", "collaborated on", "worked on"
        }
    
    def plan(
        self,
        *,
        resume_features: Dict[str, Any],
        outreach_context: Dict[str, Any],
    ) -> GroundingPlan:
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
        
        # 6. Calculate confidence score
        confidence_score = self._calculate_confidence_score(allowed_claims, disallowed_claims)
        
        # 7. Build metadata
        metadata = {
            "total_capabilities": len(analyzed_capabilities),
            "allowed_claims": len(allowed_claims),
            "disallowed_claims": len(disallowed_claims),
            "risk_flag_count": len(risk_flags),
            "confidence_score": confidence_score,
            "target_archetype": outreach_context.get("archetype", "unknown")
        }
        
        # 8. Create grounding plan
        plan = GroundingPlan(
            allowed_claims=allowed_claims,
            disallowed_claims=disallowed_claims,
            persona_alignment_notes=alignment_notes,
            risk_flags=risk_flags,
            confidence_score=confidence_score,
            metadata=metadata,
        )
        
        # 9. Record telemetry (best-effort)
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
            elif isinstance(achievement, str):
                capabilities.append({
                    "id": f"achievement_{i}",
                    "description": achievement,
                    "source": "achievement",
                    "impact_type": "general",
                    "seniority_signal": "unknown",
                })
        
        # Extract from skills
        skills = resume_features.get("skills", [])
        for i, skill in enumerate(skills):
            capabilities.append({
                "id": f"skill_{i}",
                "description": skill,
                "source": "skill",
                "impact_type": "technical",
                "seniority_signal": "ic",
            })
        
        # Extract from experience
        experience = resume_features.get("experience", [])
        for i, exp in enumerate(experience):
            if isinstance(exp, dict):
                description = exp.get("description", "")
                title = exp.get("title", "")
                capabilities.append({
                    "id": f"experience_{i}",
                    "description": f"{title}: {description}",
                    "source": "experience",
                    "impact_type": "operational",
                    "seniority_signal": self._infer_seniority_from_title(title),
                })
        
        # Extract from summary
        summary = resume_features.get("summary", "")
        if summary:
            capabilities.append({
                "id": "summary_0",
                "description": summary,
                "source": "summary",
                "impact_type": "general",
                "seniority_signal": "unknown",
            })
        
        logger.debug(f"Extracted {len(capabilities)} capabilities from resume features")
        return capabilities
    
    def _analyze_capabilities(self, capabilities: List[Dict[str, Any]]) -> List[SenderCapability]:
        """Analyze each capability for risk and verification level."""
        analyzed = []
        
        for cap in capabilities:
            description = cap["description"].lower()
            
            # Determine verification level
            verification_level = self._determine_verification_level(description)
            
            # Calculate strength score
            strength_score = self._calculate_strength_score(description, verification_level)
            
            # Determine seniority claim
            seniority_claim = self._determine_seniority_claim(description, cap.get("seniority_signal", "unknown"))
            
            # Identify risk flags
            risk_flags = self._identify_risk_flags(description)
            
            # Create analyzed capability
            analyzed_cap = SenderCapability(
                id=cap["id"],
                description=cap["description"],
                verification_level=verification_level,
                strength_score=strength_score,
                seniority_claim=seniority_claim,
                risk_flags=risk_flags,
                source=cap["source"],
                metadata={
                    "impact_type": cap.get("impact_type", "general"),
                    "original_seniority_signal": cap.get("seniority_signal", "unknown")
                }
            )
            analyzed.append(analyzed_cap)
        
        return analyzed
    
    def _classify_claims(self, capabilities: List[SenderCapability]) -> tuple[List[SenderCapability], List[SenderCapability]]:
        """Separate allowed vs disallowed claims."""
        allowed = []
        disallowed = []
        
        for cap in capabilities:
            # Disallow if high risk or unverified with low strength
            if (cap.verification_level == "unverified" and cap.strength_score < 0.3) or \
               len(cap.risk_flags) > 0 or \
               cap.strength_score < 0.2:
                disallowed.append(cap)
            else:
                allowed.append(cap)
        
        # Sort by strength score (highest first)
        allowed.sort(key=lambda x: x.strength_score, reverse=True)
        disallowed.sort(key=lambda x: x.strength_score, reverse=True)
        
        return allowed, disallowed
    
    def _generate_alignment_notes(self, capabilities: List[SenderCapability], context: Dict[str, Any]) -> List[str]:
        """Generate persona alignment observations."""
        notes = []
        archetype = context.get("archetype", "").upper()
        
        # Count seniority claims
        executive_claims = sum(1 for cap in capabilities if cap.seniority_claim == "executive")
        manager_claims = sum(1 for cap in capabilities if cap.seniority_claim == "manager")
        ic_claims = sum(1 for cap in capabilities if cap.seniority_claim == "ic")
        
        # Generate alignment notes based on archetype
        if archetype == "C_LEVEL":
            if executive_claims >= 2:
                notes.append("Strong executive alignment - multiple leadership claims")
            elif executive_claims == 1:
                notes.append("Moderate executive alignment - single leadership claim")
            else:
                notes.append("Weak executive alignment - lacks clear leadership evidence")
        
        elif archetype == "EXECUTIVE":
            if manager_claims >= 2 or executive_claims >= 1:
                notes.append("Good executive alignment - management/leadership evidence")
            else:
                notes.append("Limited executive alignment - insufficient management evidence")
        
        elif archetype == "SENIOR_TA":
            if ic_claims >= 2:
                notes.append("Strong technical alignment - multiple technical claims")
            else:
                notes.append("Moderate technical alignment - limited technical evidence")
        
        elif archetype == "RECRUITER":
            notes.append("Neutral alignment - recruiter archetype flexible on capabilities")
        
        # Add verification quality note
        high_verified = sum(1 for cap in capabilities if cap.verification_level == "high")
        if high_verified >= len(capabilities) * 0.7:
            notes.append("High verification quality - most claims well-supported")
        elif high_verified >= len(capabilities) * 0.4:
            notes.append("Moderate verification quality - mix of supported claims")
        else:
            notes.append("Low verification quality - many claims lack strong support")
        
        return notes
    
    def _collect_risk_flags(self, capabilities: List[SenderCapability]) -> List[str]:
        """Collect overall risk flags from all capabilities."""
        all_risks = []
        for cap in capabilities:
            all_risks.extend(cap.risk_flags)
        
        # Remove duplicates and return
        return list(set(all_risks))
    
    def _calculate_confidence_score(self, allowed: List[SenderCapability], disallowed: List[SenderCapability]) -> float:
        """Calculate overall grounding confidence score."""
        total = len(allowed) + len(disallowed)
        if total == 0:
            return 0.0
        
        # Weight allowed claims higher
        allowed_weight = len(allowed) * 1.0
        disallowed_weight = len(disallowed) * 0.2
        
        confidence = (allowed_weight + disallowed_weight) / (total * 1.0)
        return round(min(confidence, 1.0), 3)
    
    def _determine_verification_level(self, description: str) -> str:
        """Determine verification level from description."""
        if any(indicator in description for indicator in self.high_verification_indicators):
            return "high"
        elif any(indicator in description for indicator in self.medium_verification_indicators):
            return "medium"
        elif any(indicator in description for indicator in self.unverified_patterns):
            return "unverified"
        else:
            return "medium"  # Default to medium
    
    def _calculate_strength_score(self, description: str, verification_level: str) -> float:
        """Calculate capability strength score."""
        base_scores = {
            "high": 0.8,
            "medium": 0.5,
            "unverified": 0.2
        }
        
        base_score = base_scores.get(verification_level, 0.5)
        
        # Boost for specific metrics or outcomes
        if any(word in description for word in ["%", "doubled", "tripled", "reduced by", "increased by"]):
            base_score += 0.2
        
        # Boost for action verbs
        if any(word in description for word in ["achieved", "delivered", "completed", "launched"]):
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _determine_seniority_claim(self, description: str, signal: str) -> str:
        """Determine seniority claim from description and signal."""
        description_lower = description.lower()
        
        # Check for executive indicators
        if any(indicator in description_lower for indicator in self.executive_indicators):
            return "executive"
        
        # Check for manager indicators
        elif any(indicator in description_lower for indicator in self.manager_indicators):
            return "manager"
        
        # Check for IC indicators
        elif any(indicator in description_lower for indicator in self.ic_indicators):
            return "ic"
        
        # Use signal if available
        elif signal in ["executive", "manager", "ic"]:
            return signal
        
        else:
            return "unknown"
    
    def _identify_risk_flags(self, description: str) -> List[str]:
        """Identify risk flags in description."""
        risks = []
        description_lower = description.lower()
        
        # Check for overclaim patterns
        for pattern in self.overclaim_patterns:
            if pattern in description_lower:
                risks.append("overclaim")
                break
        
        # Check for unverified patterns
        for pattern in self.unverified_patterns:
            if pattern in description_lower:
                risks.append("unverified")
                break
        
        # Check for absolute claims
        if any(word in description_lower for word in ["always", "never", "only", "every", "all"]):
            risks.append("absolute_claim")
        
        return risks
    
    def _infer_seniority_from_title(self, title: str) -> str:
        """Infer seniority from job title."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["chief", "vp", "vice president", "director", "head"]):
            return "executive"
        elif any(word in title_lower for word in ["manager", "lead", "supervisor"]):
            return "manager"
        elif any(word in title_lower for word in ["engineer", "developer", "analyst", "specialist"]):
            return "ic"
        else:
            return "unknown"
    
    def _safe_record_telemetry(self, plan: GroundingPlan) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("grounding_plan_created", {
                    "allowed_claims": len(plan.allowed_claims),
                    "disallowed_claims": len(plan.disallowed_claims),
                    "risk_flags": len(plan.risk_flags),
                    "confidence_score": plan.confidence_score
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_grounding_summary(self, plan: GroundingPlan) -> Dict[str, Any]:
        """Get a summary of the grounding plan for debugging/telemetry."""
        return {
            "plan_id": f"grounding_{len(plan.allowed_claims)}_{len(plan.disallowed_claims)}",
            "allowed_claims": len(plan.allowed_claims),
            "disallowed_claims": len(plan.disallowed_claims),
            "risk_flags": plan.risk_flags,
            "confidence_score": plan.confidence_score,
            "top_capabilities": [
                {
                    "id": cap.id,
                    "description": cap.description[:100] + "..." if len(cap.description) > 100 else cap.description,
                    "strength": cap.strength_score,
                    "verification": cap.verification_level
                }
                for cap in plan.allowed_claims[:3]
            ],
            "alignment_notes_count": len(plan.persona_alignment_notes)
        }
