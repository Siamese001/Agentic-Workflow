"""
L1 Outreach Archetype Planner - Pure computation for archetype classification.

Implements pure reasoning to classify recipient archetypes and build
cross-cutting parameter context without any execution logic or external calls.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from .outreach_dataclasses import (
    ArchetypeContext,
    SignalParameters,
    RagParameters,
    ReasoningParameters,
    ConstraintParameters,
    ToneParameters,
    CtaParameters
)


@dataclass
class RecipientProfile:
    """Pure data structure for recipient profile analysis."""
    name: str
    title: str
    company: str
    industry: str
    seniority: str
    department: str
    skills: List[str]
    recent_activity: List[str]
    metadata: Dict[str, Any]


@dataclass
class OutreachMission:
    """Pure data structure for outreach mission definition."""
    objective: str
    target_role: str
    value_proposition: str
    urgency: str
    personalization_points: List[str]
    constraints: List[str]
    metadata: Dict[str, Any]


class OutreachArchetypePlanner:
    """
    Pure L1 planner for outreach archetype classification and context building.
    
    Performs only computational reasoning on provided data without any
    external calls, state writes, or execution logic.
    """
    
    def __init__(self):
        # Pure archetype registry - no external loading
        self._archetype_registry = self._build_archetype_registry()
    
    def _build_archetype_registry(self) -> Dict[str, Dict[str, Any]]:
        """Build pure in-memory archetype registry without external loading."""
        return {
            "technical_leader": {
                "keywords": ["cto", "vp engineering", "chief technology", "head of engineering", "director of technology"],
                "industries": ["software", "technology", "fintech", "healthcare it"],
                "signal_params": SignalParameters(
                    min_signal_score=0.8,
                    signal_types=["quantitative", "strategic"],
                    max_age_days=180,
                    weight_recent=1.1,
                    weight_quantitative=2.0
                ),
                "rag_params": RagParameters(
                    top_k=15,
                    score_threshold=0.75,
                    source_weights={"technical": 1.5, "company": 1.2}
                ),
                "reasoning_params": ReasoningParameters(
                    reasoning_style="analytical",
                    confidence_threshold=0.85,
                    max_reasoning_depth=4,
                    use_analogical=True,
                    use_causal=True
                ),
                "constraint_params": ConstraintParameters(
                    strict_constraints=["technical_accuracy", "data_driven"],
                    soft_constraints=["brevity", "formality"],
                    constraint_weights={"technical_accuracy": 2.0}
                ),
                "tone_params": ToneParameters(
                    formality_level="professional",
                    enthusiasm_level="low",
                    confidence_level="high",
                    personalization_level="technical",
                    industry_specific=True
                ),
                "cta_params": CtaParameters(
                    cta_type="technical_discussion",
                    urgency_level="medium",
                    value_proposition_focus="technical_value",
                    friction_reduction=True
                )
            },
            "business_executive": {
                "keywords": ["ceo", "president", "chief executive", "vp", "director", "business development"],
                "industries": ["enterprise", "consulting", "finance", "healthcare"],
                "signal_params": SignalParameters(
                    min_signal_score=0.7,
                    signal_types=["strategic", "recent_activity"],
                    max_age_days=90,
                    weight_recent=1.5,
                    weight_quantitative=1.2
                ),
                "rag_params": RagParameters(
                    top_k=10,
                    score_threshold=0.7,
                    source_weights={"business": 1.5, "financial": 1.3}
                ),
                "reasoning_params": ReasoningParameters(
                    reasoning_style="strategic",
                    confidence_threshold=0.8,
                    max_reasoning_depth=3,
                    use_analogical=True,
                    use_causal=False
                ),
                "constraint_params": ConstraintParameters(
                    strict_constraints=["business_value", "concise"],
                    soft_constraints=["formality", "relationship_building"],
                    constraint_weights={"business_value": 2.0}
                ),
                "tone_params": ToneParameters(
                    formality_level="formal",
                    enthusiasm_level="moderate",
                    confidence_level="high",
                    personalization_level="business",
                    industry_specific=True
                ),
                "cta_params": CtaParameters(
                    cta_type="business_meeting",
                    urgency_level="low",
                    value_proposition_focus="roi",
                    friction_reduction=True
                )
            },
            "hiring_manager": {
                "keywords": ["hiring manager", "recruiter", "talent acquisition", "hr", "people"],
                "industries": ["all"],
                "signal_params": SignalParameters(
                    min_signal_score=0.6,
                    signal_types=["recent_activity", "quantitative"],
                    max_age_days=60,
                    weight_recent=1.8,
                    weight_quantitative=1.0
                ),
                "rag_params": RagParameters(
                    top_k=8,
                    score_threshold=0.65,
                    source_weights={"hiring": 1.5, "company": 1.0}
                ),
                "reasoning_params": ReasoningParameters(
                    reasoning_style="practical",
                    confidence_threshold=0.75,
                    max_reasoning_depth=2,
                    use_analogical=False,
                    use_causal=True
                ),
                "constraint_params": ConstraintParameters(
                    strict_constraints=["role_fit", "availability"],
                    soft_constraints=["culture_fit", "enthusiasm"],
                    constraint_weights={"role_fit": 1.8}
                ),
                "tone_params": ToneParameters(
                    formality_level="professional",
                    enthusiasm_level="moderate",
                    confidence_level="confident",
                    personalization_level="role_specific",
                    industry_specific=False
                ),
                "cta_params": CtaParameters(
                    cta_type="interview_request",
                    urgency_level="medium",
                    value_proposition_focus="candidate_value",
                    friction_reduction=True
                )
            },
            "individual_contributor": {
                "keywords": ["engineer", "developer", "analyst", "specialist", "consultant"],
                "industries": ["software", "technology", "data", "analytics"],
                "signal_params": SignalParameters(
                    min_signal_score=0.7,
                    signal_types=["quantitative", "technical"],
                    max_age_days=120,
                    weight_recent=1.2,
                    weight_quantitative=1.8
                ),
                "rag_params": RagParameters(
                    top_k=12,
                    score_threshold=0.7,
                    source_weights={"technical": 1.8, "project": 1.3}
                ),
                "reasoning_params": ReasoningParameters(
                    reasoning_style="analytical",
                    confidence_threshold=0.8,
                    max_reasoning_depth=3,
                    use_analogical=False,
                    use_causal=True
                ),
                "constraint_params": ConstraintParameters(
                    strict_constraints=["technical_relevance", "skill_match"],
                    soft_constraints=["innovation", "growth"],
                    constraint_weights={"technical_relevance": 1.5}
                ),
                "tone_params": ToneParameters(
                    formality_level="casual_professional",
                    enthusiasm_level="moderate",
                    confidence_level="confident",
                    personalization_level="skill_based",
                    industry_specific=True
                ),
                "cta_params": CtaParameters(
                    cta_type="collaboration_discussion",
                    urgency_level="low",
                    value_proposition_focus="technical_growth",
                    friction_reduction=False
                )
            }
        }
    
    def classify_archetype(
        self, 
        recipient: RecipientProfile, 
        mission: OutreachMission
    ) -> tuple[str, float, str]:
        """
        Pure computational archetype classification.
        
        Returns: (archetype, confidence, reasoning)
        """
        scores = {}
        
        # Score each archetype based on keyword matching
        for archetype, config in self._archetype_registry.items():
            score = 0.0
            matches = []
            
            # Title keyword matching
            title_lower = recipient.title.lower()
            for keyword in config["keywords"]:
                if keyword in title_lower:
                    score += 2.0
                    matches.append(f"title contains '{keyword}'")
            
            # Industry matching
            if recipient.industry.lower() in [ind.lower() for ind in config["industries"]]:
                score += 1.0
                matches.append(f"industry match: {recipient.industry}")
            
            # Seniority matching
            if archetype in ["technical_leader", "business_executive"] and recipient.seniority in ["executive", "senior", "vp", "director"]:
                score += 1.0
                matches.append(f"seniority match: {recipient.seniority}")
            
            # Skills matching
            if archetype == "technical_leader" and any(skill in ["architecture", "leadership", "strategy"] for skill in recipient.skills):
                score += 1.0
                matches.append("leadership skills detected")
            elif archetype == "individual_contributor" and any(skill in ["programming", "development", "analysis"] for skill in recipient.skills):
                score += 1.0
                matches.append("technical skills detected")
            
            # Mission alignment
            mission_lower = mission.objective.lower()
            if archetype == "technical_leader" and any(term in mission_lower for term in ["technology", "architecture", "engineering"]):
                score += 0.5
                matches.append("mission alignment")
            elif archetype == "business_executive" and any(term in mission_lower for term in ["business", "revenue", "growth"]):
                score += 0.5
                matches.append("business mission alignment")
            
            scores[archetype] = (score, matches)
        
        # Find best archetype
        best_archetype = max(scores.keys(), key=lambda k: scores[k][0])
        best_score, best_matches = scores[best_archetype]
        
        # Normalize confidence (max possible score is around 5-6)
        confidence = min(best_score / 5.0, 1.0)
        reasoning = f"Selected based on: {', '.join(best_matches)}" if best_matches else "Default selection"
        
        return best_archetype, confidence, reasoning
    
    def build_archetype_context(
        self, 
        recipient: RecipientProfile, 
        mission: OutreachMission
    ) -> ArchetypeContext:
        """
        Build complete archetype context using pure computation.
        """
        # Classify archetype
        archetype, confidence, reasoning = self.classify_archetype(recipient, mission)
        
        # Get archetype configuration
        config = self._archetype_registry.get(archetype, self._archetype_registry["individual_contributor"])
        
        # Build context with cross-cutting parameters
        context = ArchetypeContext(
            archetype=archetype,
            confidence=confidence,
            reasoning=reasoning,
            rag_params=config["rag_params"],
            reasoning_params=config["reasoning_params"],
            signal_params=config["signal_params"],
            constraint_params=config["constraint_params"],
            tone_params=config["tone_params"],
            cta_params=config["cta_params"],
            metadata={
                "recipient_title": recipient.title,
                "recipient_industry": recipient.industry,
                "mission_objective": mission.objective,
                "classification_score": confidence
            }
        )
        
        return context
    
    def analyze_archetype_fit(
        self, 
        context: ArchetypeContext, 
        mission: OutreachMission
    ) -> Dict[str, Any]:
        """
        Pure computational analysis of archetype fit for mission.
        """
        fit_score = context.confidence
        
        # Adjust based on mission constraints
        if mission.constraints:
            constraint_alignment = 0.0
            for constraint in mission.constraints:
                if constraint.lower() in ["technical", "technology"] and context.archetype == "technical_leader":
                    constraint_alignment += 0.2
                elif constraint.lower() in ["business", "revenue"] and context.archetype == "business_executive":
                    constraint_alignment += 0.2
                elif constraint.lower() in ["hiring", "recruitment"] and context.archetype == "hiring_manager":
                    constraint_alignment += 0.2
            
            fit_score = min(fit_score + constraint_alignment, 1.0)
        
        return {
            "fit_score": fit_score,
            "recommended_approach": self._get_recommended_approach(context),
            "key_levers": self._identify_key_levers(context, mission),
            "risk_factors": self._identify_risk_factors(context, mission)
        }
    
    def _get_recommended_approach(self, context: ArchetypeContext) -> str:
        """Get recommended approach based on archetype."""
        approaches = {
            "technical_leader": "Focus on technical innovation and architectural impact",
            "business_executive": "Emphasize business value and ROI",
            "hiring_manager": "Highlight candidate fit and team value",
            "individual_contributor": "Emphasize technical growth and collaboration"
        }
        return approaches.get(context.archetype, "Professional and value-focused approach")
    
    def _identify_key_levers(self, context: ArchetypeContext, mission: OutreachMission) -> List[str]:
        """Identify key leverage points for outreach."""
        levers = []
        
        if context.archetype == "technical_leader":
            levers.extend(["technical innovation", "scalability", "team leadership"])
        elif context.archetype == "business_executive":
            levers.extend(["business impact", "revenue growth", "competitive advantage"])
        elif context.archetype == "hiring_manager":
            levers.extend(["role fit", "team dynamics", "hiring efficiency"])
        else:
            levers.extend(["skill development", "project impact", "collaboration"])
        
        return levers
    
    def _identify_risk_factors(self, context: ArchetypeContext, mission: OutreachMission) -> List[str]:
        """Identify potential risk factors in outreach."""
        risks = []
        
        if context.confidence < 0.7:
            risks.append("Low archetype confidence may reduce personalization effectiveness")
        
        if len(mission.constraints) > 3:
            risks.append("Multiple constraints may limit message flexibility")
        
        if context.archetype == "technical_leader" and mission.urgency == "high":
            risks.append("Technical leaders may require longer consideration cycles")
        
        return risks
