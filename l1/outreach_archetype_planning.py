"""Defines core behaviors that drive high-signal executive outreach through archetype classification."""

from dataclasses import dataclass
from typing import Any, Dict, List

from l1.outreach_dataclasses import (
    OutreachMission,
    ArchetypeType,
    ArchetypeContext,
    ReasoningMode,
    ARCHETYPE_REGISTRY,
    EXECUTIVE_REASONING_PROFILES,
)


@dataclass
class RecipientProfile:
    """Captures recipient signals that drive personalized executive outreach strategies."""
    name: str
    title: str
    company: str
    industry: str
    seniority: str
    department: str
    skills: List[str]
    recent_activity: List[str]
    metadata: Dict[str, Any]


class OutreachArchetypePlanner:
    """Classifies recipients to optimize message relevance and executive reply probability."""
    
    def __init__(self):
        """Initializes planner with archetype registry for executive targeting logic."""
        # Use the corrected archetype registry from dataclasses
        self._archetype_registry = ARCHETYPE_REGISTRY
    
    def _classify_archetype(self, profile: RecipientProfile, mission: OutreachMission) -> str:
        """Maps recipient signals to archetype for targeted executive messaging."""
        title = profile.title.lower()
        department = profile.department.lower()
        seniority = profile.seniority.lower()
        
        # HSON: Targets recruitment decision makers with hiring-focused messaging -> increases reply probability
        if any(keyword in title for keyword in ["recruiter", "talent acquisition", "sourcer", "staffing"]):
            return ArchetypeType.RECRUITER
        
        # HSON: Identifies technical influencers for peer-to-peer credibility messaging -> boosts technical signal strength
        if any(keyword in title for keyword in ["senior", "principal", "staff", "lead"]) and \
           any(keyword in department for keyword in ["engineering", "technology", "software", "technical"]) and \
           "manager" not in title and "director" not in title:
            return ArchetypeType.SENIOR_TA
        
        # C-level patterns (more specific to avoid VP misclassification)
        if any(keyword in title for keyword in ["ceo", "cto", "cfo", "chief", "president"]) or \
           any(keyword in seniority for keyword in ["c-level", "c_suite"]):
            return ArchetypeType.C_LEVEL
        
        # HSON: Targets business decision makers with strategic impact messaging -> increases C-level reply probability
        if any(keyword in title for keyword in ["manager", "director", "head", "supervisor", "vp", "vice president"]) and \
           any(keyword in department for keyword in ["engineering", "technology", "software", "product", "technical", "business"]):
            return ArchetypeType.EXECUTIVE
        
        # Default fallback based on seniority
        if any(keyword in seniority for keyword in ["senior", "principal", "staff", "lead"]) and \
           "manager" not in title:
            return ArchetypeType.SENIOR_TA
        elif any(keyword in seniority for keyword in ["manager", "director", "vp", "executive"]):
            return ArchetypeType.EXECUTIVE
        else:
            return ArchetypeType.RECRUITER
    
    def build_archetype_context(
        self, 
        recipient: RecipientProfile, 
        mission: OutreachMission
    ) -> ArchetypeContext:
        """Builds executive-optimized context with reasoning parameters for high-signal messaging."""
        # Classify archetype using corrected logic
        archetype = self._classify_archetype(recipient, mission)
        
        # Get archetype definition from corrected registry
        archetype_type = ArchetypeType(archetype)
        definition = self._archetype_registry[archetype_type]
        
        # HSON: Boosts confidence for clear executive titles -> improves targeting precision
        confidence = self._calculate_classification_confidence(recipient, archetype)
        
        reasoning = f"Classified as {archetype} based on title '{recipient.title}' and department '{recipient.department}'"
        
        # HSON: Selects reasoning profile to match executive cognitive patterns -> increases engagement
        executive_profile = EXECUTIVE_REASONING_PROFILES[archetype_type]
        
        # Build context with parameters from registry and executive reasoning profile
        context = ArchetypeContext(
            archetype=archetype,
            confidence=confidence,
            reasoning=reasoning,
            rag_params=definition.rag_params,
            reasoning_params=definition.reasoning_params,
            signal_params=definition.signal_params,
            constraint_params=definition.constraint_params,
            tone_params=definition.tone_params,
            cta_params=definition.cta_params,
            executive_reasoning_profile=executive_profile,
            metadata={
                "recipient_title": recipient.title,
                "recipient_industry": recipient.industry,
                "mission_objective": mission.objective,
                "classification_score": confidence,
                "reasoning_intensity": executive_profile.reasoning_intensity,
                "available_reasoning_modes": [mode.value for mode in executive_profile.available_reasoning_modes]
            }
        )
        
        return context
    
    def _calculate_classification_confidence(self, recipient: RecipientProfile, archetype: str) -> float:
        """Computes targeting confidence to ensure message relevance for executive audiences."""
        base_confidence = 0.8
        
        # Boost confidence for clear title patterns
        title = recipient.title.lower()
        if any(keyword in title for keyword in ["recruiter", "talent acquisition"]):
            base_confidence = 0.95
        elif any(keyword in title for keyword in ["senior", "principal", "staff"]) and "manager" not in title:
            base_confidence = 0.9
        elif any(keyword in title for keyword in ["manager", "director"]) and "engineering" in recipient.department.lower():
            base_confidence = 0.85
        elif any(keyword in title for keyword in ["chief", "vp", "president"]):
            base_confidence = 0.9
        
        return min(base_confidence, 1.0)
    
    def analyze_archetype_fit(
        self, 
        context: ArchetypeContext, 
        mission: OutreachMission
    ) -> Dict[str, Any]:
        """
        Pure computational analysis of archetype fit for mission using correct archetypes.
        """
        fit_score = context.confidence
        
        # Adjust based on mission constraints using correct archetypes
        if mission.constraints:
            constraint_alignment = 0.0
            for constraint in mission.constraints:
                constraint_lower = constraint.lower()
                if constraint_lower in ["technical", "technology"] and context.archetype == ArchetypeType.SENIOR_TA:
                    constraint_alignment += 0.2
                elif constraint_lower in ["business", "revenue", "strategic"] and context.archetype == ArchetypeType.C_LEVEL:
                    constraint_alignment += 0.2
                elif constraint_lower in ["business", "revenue", "strategic"] and context.archetype == ArchetypeType.EXECUTIVE:
                    constraint_alignment += 0.2
                elif constraint_lower in ["hiring", "recruitment", "team"] and context.archetype == ArchetypeType.EXECUTIVE:
                    constraint_alignment += 0.2
                elif constraint_lower in ["screening", "job_fit"] and context.archetype == ArchetypeType.RECRUITER:
                    constraint_alignment += 0.2
            
            fit_score = min(fit_score + constraint_alignment, 1.0)
        
        return {
            "fit_score": fit_score,
            "recommended_approach": self._get_recommended_approach(context),
            "key_levers": self._identify_key_levers(context, mission),
            "risk_factors": self._identify_risk_factors(context, mission)
        }
    
    def _get_recommended_approach(self, context: ArchetypeContext) -> str:
        """Get recommended approach based on correct archetypes."""
        approaches = {
            ArchetypeType.RECRUITER: "Focus on job fit and screening efficiency",
            ArchetypeType.SENIOR_TA: "Emphasize technical depth and company specificity",
            ArchetypeType.EXECUTIVE: "Highlight business impact and strategic alignment",
            ArchetypeType.C_LEVEL: "Emphasize strategic outcomes and high signal density"
        }
        return approaches.get(context.archetype, "Professional and value-focused approach")
    
    def _identify_key_levers(self, context: ArchetypeContext, mission: OutreachMission) -> List[str]:
        """Identify key leverage points for outreach using correct archetypes."""
        levers = []
        
        if context.archetype == ArchetypeType.RECRUITER:
            levers.extend(["job fit", "screening efficiency", "candidate quality"])
        elif context.archetype == ArchetypeType.SENIOR_TA:
            levers.extend(["technical depth", "company specificity", "innovation potential"])
        elif context.archetype == ArchetypeType.EXECUTIVE:
            levers.extend(["business impact", "strategic alignment", "team outcomes"])
        elif context.archetype == ArchetypeType.C_LEVEL:
            levers.extend(["strategic outcomes", "competitive advantage", "business value"])
        
        return levers
    
    def _identify_risk_factors(self, context: ArchetypeContext, mission: OutreachMission) -> List[str]:
        """Identify potential risk factors in outreach using correct archetypes."""
        risks = []
        
        if context.confidence < 0.7:
            risks.append("Low archetype confidence may reduce personalization effectiveness")
        
        if len(mission.constraints) > 3:
            risks.append("Multiple constraints may limit message flexibility")
        
        if context.archetype == ArchetypeType.SENIOR_TA and mission.urgency == "high":
            risks.append("Senior technical authorities may require longer consideration cycles")
        
        if context.archetype == ArchetypeType.EXECUTIVE and len(mission.value_proposition) < 50:
            risks.append("Executive outreach requires strong business value proposition")
        
        if context.archetype == ArchetypeType.C_LEVEL and len(mission.value_proposition) < 50:
            risks.append("C-level outreach requires strong, concise strategic value proposition")
        
        return risks
    
    def plan_archetype_influence(
        self, 
        mission: OutreachMission,
        reasoning_mode: ReasoningMode = ReasoningMode.COT
    ) -> ArchetypeContext:
        """
        Plan archetype influence for a given mission with executive reasoning profiles.
        
        This is the primary entry point for archetype planning that returns
        an ArchetypeContext with all cross-cutting parameters configured and
        available reasoning modes from the ExecutiveReasoningProfile.
        
        Args:
            mission: The outreach mission to plan for
            reasoning_mode: The reasoning mode to use (cot, tot, react, reflexion, sc_k)
            
        Returns:
            ArchetypeContext with configured parameters for research and message planning
        """
        # Create a minimal recipient profile from mission data
        recipient = RecipientProfile(
            name="",
            title=mission.target_role,
            company=mission.target_company,
            industry="",
            seniority=self._infer_seniority(mission.target_role),
            department="",
            skills=[],
            recent_activity=[],
            metadata=mission.metadata
        )
        
        # Create local mission for internal processing
        local_mission = OutreachMission(
            objective=mission.objective,
            target_role=mission.target_role,
            value_proposition=mission.value_proposition,
            urgency=mission.urgency,
            personalization_points=mission.personalization_points,
            constraints=mission.constraints,
            metadata=mission.metadata
        )
        
        # Build archetype context with executive reasoning profile
        context = self.build_archetype_context(recipient, local_mission)
        
        # Update reasoning mode in context if available in executive profile
        if reasoning_mode in context.executive_reasoning_profile.available_reasoning_modes:
            context.reasoning_params.reasoning_mode = reasoning_mode
        else:
            # Use first available reasoning mode from profile
            context.reasoning_params.reasoning_mode = context.executive_reasoning_profile.available_reasoning_modes[0]
        
        return context
    
    def _infer_seniority(self, title: str) -> str:
        """Infer seniority level from job title."""
        title_lower = title.lower()
        if any(term in title_lower for term in ["cto", "ceo", "cfo", "chief", "president"]):
            return "executive"
        elif any(term in title_lower for term in ["vp", "vice president", "svp"]):
            return "vp"
        elif any(term in title_lower for term in ["director", "head of"]):
            return "director"
        elif any(term in title_lower for term in ["senior", "lead", "principal", "staff"]):
            return "senior"
        elif any(term in title_lower for term in ["manager"]):
            return "manager"
        else:
            return "individual_contributor"
    
    @staticmethod
    def get_reasoning_modes() -> List[ReasoningMode]:
        """Get available reasoning modes for L1 planning."""
        return [ReasoningMode.COT, ReasoningMode.TOT, ReasoningMode.REACT]
