"""Fusion Planner - Advanced planning for resume + research signal fusion.

Incorporated from L1 lic_fusion_planner.py to provide structured message
blueprints that combine sender achievements with research signals into
compelling value propositions and section plans.

This bridges the gap between RAG research and template generation,
providing data-driven content structure for personalized outreach.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValueProposition:
    """A single value proposition combining resume achievement + research signal."""
    id: str                              # stable identifier (e.g. "vp_1")
    achievement_snippet: str             # concise resume-derived snippet
    signal_snippet: str                  # concise research signal snippet
    archetype_target: str                # e.g. "EXECUTIVE" | "SENIOR_TA" | "RECRUITER"
    priority: int                        # 1 = highest priority
    angle: str                           # e.g. "strategic", "operational", "technical"
    expected_impact: str                 # short description of why this matters
    relevance_score: float = 0.0         # calculated relevance score
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageSectionPlan:
    """Structured plan for one section of an outreach message."""
    section_type: str                    # "opening" | "body" | "cta"
    archetype_target: str
    value_proposition_ids: List[str]     # which ValueProposition IDs to use
    tone_guidance: str                   # e.g. "concise and executive", "signal-aware", etc.
    cta_guidance: Optional[str]          # for "cta" sections, explicit CTA guidance
    word_count_target: Optional[int]     # target word count for this section
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FusionPlan:
    """Full fusion blueprint from resume + signals → message."""
    role_title: str
    company_name: str
    archetype: str                       # primary archetype for this contact
    value_propositions: List[ValueProposition]
    sections: List[MessageSectionPlan]
    primary_cta_style: str               # e.g. "light_touch", "exploratory_call", "direct"
    fallback_cta_style: str              # used if CTA deemed too strong
    confidence_score: float = 0.0        # overall plan confidence
    metadata: Dict[str, Any] = field(default_factory=dict)


class FusionPlanner:
    """Advanced planner for resume + research signal fusion.
    
    Generates deterministic fusion plans that combine resume achievements
    with research signals into structured message blueprints.
    """
    
    def __init__(
        self,
        *,
        max_value_props: int = 5,
        max_body_sections: int = 2,
        enable_exec_strict_cta: bool = True,
        min_relevance_threshold: float = 0.6,
    ) -> None:
        """Initialize fusion planner with configuration."""
        self.max_value_props = max_value_props
        self.max_body_sections = max_body_sections
        self.enable_exec_strict_cta = enable_exec_strict_cta
        self.min_relevance_threshold = min_relevance_threshold
        
        logger.debug(f"Fusion Planner initialized: max_value_props={max_value_props}")
    
    def plan(
        self,
        *,
        role_title: str,
        company_name: str,
        archetype: str,
        resume_features: Dict[str, Any],
        research_signals: Dict[str, Any],
        rag_evidence: List[Any] = None,
    ) -> FusionPlan:
        """Generate a deterministic fusion plan from resume + signals.
        
        Args:
            role_title: Target role title
            company_name: Target company name
            archetype: Primary archetype for this contact
            resume_features: Pre-computed resume signals (achievements, metrics, themes)
            research_signals: LIC research outputs (company, market, product, funding)
            rag_evidence: Optional RAG evidence for additional context
            
        Returns:
            Complete fusion plan with value propositions and message sections
        """
        # 1. Extract and normalize achievements + signals
        achievements = self._extract_achievements(resume_features)
        signals = self._extract_signals(research_signals, rag_evidence)
        
        # 2. Generate candidate value propositions
        value_props = self._pair_achievements_and_signals(
            achievements, signals, archetype
        )
        
        # 3. Rank and trim to max_value_props
        value_props = self._rank_and_trim_value_props(value_props)
        
        # 4. Build opening/body/cta section plans
        sections = self._build_sections(value_props, archetype)
        
        # 5. Determine CTA styles
        primary_cta_style, fallback_cta_style = self._determine_cta_styles(
            archetype, self.enable_exec_strict_cta
        )
        
        # 6. Calculate confidence score
        confidence_score = self._calculate_confidence_score(value_props, signals)
        
        # 7. Build metadata
        metadata = {
            "archetype": archetype,
            "role_title": role_title,
            "company_name": company_name,
            "value_prop_count": len(value_props),
            "primary_cta_style": primary_cta_style,
            "fallback_cta_style": fallback_cta_style,
            "confidence_score": confidence_score,
        }
        
        # 8. Create fusion plan
        plan = FusionPlan(
            role_title=role_title,
            company_name=company_name,
            archetype=archetype,
            value_propositions=value_props,
            sections=sections,
            primary_cta_style=primary_cta_style,
            fallback_cta_style=fallback_cta_style,
            confidence_score=confidence_score,
            metadata=metadata,
        )
        
        return plan
    
    def _extract_achievements(self, resume_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract achievements from resume features."""
        achievements = []
        
        # Extract from structured resume data
        if "achievements" in resume_features:
            achievements.extend(resume_features["achievements"])
        
        # Extract from experience sections
        if "experience" in resume_features:
            for exp in resume_features["experience"]:
                if "description" in exp:
                    achievements.append({
                        "type": "experience",
                        "content": exp["description"],
                        "title": exp.get("title", ""),
                        "company": exp.get("company", ""),
                        "source": "resume_experience"
                    })
        
        # Extract from skills
        if "skills" in resume_features:
            skills = resume_features["skills"]
            if isinstance(skills, list) and len(skills) > 0:
                achievements.append({
                    "type": "skills",
                    "content": f"Proficient in {', '.join(skills[:5])}",  # Limit to top 5
                    "skills": skills,
                    "source": "resume_skills"
                })
        
        # Extract from summary
        if "summary" in resume_features:
            achievements.append({
                "type": "summary",
                "content": resume_features["summary"],
                "source": "resume_summary"
            })
        
        logger.debug(f"Extracted {len(achievements)} achievements from resume")
        return achievements
    
    def _extract_signals(self, research_signals: Dict[str, Any], rag_evidence: List[Any] = None) -> List[Dict[str, Any]]:
        """Extract signals from research outputs and RAG evidence."""
        signals = []
        
        # Extract from research signals
        if "company_info" in research_signals:
            signals.append({
                "type": "company",
                "content": research_signals["company_info"],
                "source": "research_company"
            })
        
        if "market_context" in research_signals:
            signals.append({
                "type": "market",
                "content": research_signals["market_context"],
                "source": "research_market"
            })
        
        if "product_info" in research_signals:
            signals.append({
                "type": "product",
                "content": research_signals["product_info"],
                "source": "research_product"
            })
        
        # Extract from RAG evidence
        if rag_evidence:
            for evidence in rag_evidence[:3]:  # Use top 3 evidence items
                signals.append({
                    "type": "rag",
                    "content": evidence.content if hasattr(evidence, 'content') else str(evidence),
                    "relevance_score": getattr(evidence, 'relevance_score', 0.8),
                    "source": "rag_evidence"
                })
        
        logger.debug(f"Extracted {len(signals)} signals from research")
        return signals
    
    def _pair_achievements_and_signals(
        self, 
        achievements: List[Dict[str, Any]], 
        signals: List[Dict[str, Any]], 
        archetype: str
    ) -> List[ValueProposition]:
        """Generate value propositions by pairing achievements with signals."""
        value_props = []
        
        # Get archetype-specific angles
        archetype_angles = self._get_archetype_angles(archetype)
        
        for i, achievement in enumerate(achievements):
            for j, signal in enumerate(signals):
                # Calculate relevance
                relevance = self._calculate_relevance(achievement, signal, archetype)
                
                if relevance >= self.min_relevance_threshold:
                    # Determine angle based on archetype and content
                    angle = self._determine_angle(achievement, signal, archetype_angles)
                    
                    # Create value proposition
                    vp = ValueProposition(
                        id=f"vp_{len(value_props) + 1}",
                        achievement_snippet=self._create_achievement_snippet(achievement),
                        signal_snippet=self._create_signal_snippet(signal),
                        archetype_target=archetype,
                        priority=len(value_props) + 1,
                        angle=angle,
                        expected_impact=self._create_impact_statement(achievement, signal, angle),
                        relevance_score=relevance,
                        metadata={
                            "achievement_source": achievement.get("source", "unknown"),
                            "signal_source": signal.get("source", "unknown"),
                            "relevance_factors": relevance
                        }
                    )
                    value_props.append(vp)
        
        logger.debug(f"Generated {len(value_props)} value propositions")
        return value_props
    
    def _rank_and_trim_value_props(self, value_props: List[ValueProposition]) -> List[ValueProposition]:
        """Rank value propositions by relevance and trim to max."""
        # Sort by relevance score (descending) then by priority (ascending)
        sorted_props = sorted(value_props, key=lambda x: (-x.relevance_score, x.priority))
        
        # Trim to max_value_props
        trimmed_props = sorted_props[:self.max_value_props]
        
        # Update priorities
        for i, vp in enumerate(trimmed_props):
            vp.priority = i + 1
        
        return trimmed_props
    
    def _build_sections(self, value_props: List[ValueProposition], archetype: str) -> List[MessageSectionPlan]:
        """Build section plans from value propositions."""
        sections = []
        
        if not value_props:
            return sections
        
        # Opening section - use top value proposition
        opening_plan = MessageSectionPlan(
            section_type="opening",
            archetype_target=archetype,
            value_proposition_ids=[value_props[0].id],
            tone_guidance=self._get_opening_tone(archetype),
            word_count_target=30,
            metadata={"primary_value_prop": True}
        )
        sections.append(opening_plan)
        
        # Body sections - use remaining value propositions
        body_props = value_props[1:self.max_body_sections + 1]
        if body_props:
            body_plan = MessageSectionPlan(
                section_type="body",
                archetype_target=archetype,
                value_proposition_ids=[vp.id for vp in body_props],
                tone_guidance=self._get_body_tone(archetype),
                word_count_target=60,
                metadata={"body_value_count": len(body_props)}
            )
            sections.append(body_plan)
        
        # CTA section
        cta_plan = MessageSectionPlan(
            section_type="cta",
            archetype_target=archetype,
            value_proposition_ids=[],
            tone_guidance=self._get_cta_tone(archetype),
            cta_guidance=self._get_cta_guidance(archetype),
            word_count_target=20,
            metadata={"cta_style": "standard"}
        )
        sections.append(cta_plan)
        
        return sections
    
    def _determine_cta_styles(self, archetype: str, enable_exec_strict: bool) -> tuple[str, str]:
        """Determine primary and fallback CTA styles."""
        if archetype == "C_LEVEL" and enable_exec_strict:
            return "peer_to_peer", "professional"
        elif archetype == "EXECUTIVE":
            return "strategic_value", "professional"
        elif archetype == "SENIOR_TA":
            return "technical_discussion", "consultative"
        elif archetype == "RECRUITER":
            return "opportunity_exploration", "warm_professional"
        else:
            return "standard", "friendly"
    
    def _calculate_confidence_score(self, value_props: List[ValueProposition], signals: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for the fusion plan."""
        if not value_props:
            return 0.0
        
        # Average relevance score of value propositions
        avg_relevance = sum(vp.relevance_score for vp in value_props) / len(value_props)
        
        # Signal quality factor
        signal_quality = min(len(signals) / 3.0, 1.0)  # Normalize to max 3 signals
        
        # Value proposition count factor
        vp_count_factor = min(len(value_props) / 3.0, 1.0)  # Normalize to max 3 VPs
        
        # Weighted combination
        confidence = (avg_relevance * 0.6 + signal_quality * 0.2 + vp_count_factor * 0.2)
        
        return round(confidence, 3)
    
    def _get_archetype_angles(self, archetype: str) -> List[str]:
        """Get archetype-specific content angles."""
        angle_map = {
            "C_LEVEL": ["strategic", "business_outcome", "market_leadership"],
            "EXECUTIVE": ["operational", "team_impact", "efficiency"],
            "SENIOR_TA": ["technical", "innovation", "scalability"],
            "RECRUITER": ["skill_alignment", "career_growth", "opportunity"]
        }
        return angle_map.get(archetype, ["general"])
    
    def _calculate_relevance(self, achievement: Dict[str, Any], signal: Dict[str, Any], archetype: str) -> float:
        """Calculate relevance score between achievement and signal."""
        # Simple relevance calculation - can be enhanced with NLP
        base_score = 0.5
        
        # Boost for matching content types
        if achievement.get("type") == "technical" and signal.get("type") in ["product", "rag"]:
            base_score += 0.3
        elif achievement.get("type") == "leadership" and signal.get("type") == "company":
            base_score += 0.3
        elif signal.get("type") == "rag":
            base_score += signal.get("relevance_score", 0.8) * 0.2
        
        # Archetype-specific boosts
        if archetype == "SENIOR_TA" and "technical" in str(achievement.get("content", "")).lower():
            base_score += 0.2
        elif archetype == "EXECUTIVE" and "leadership" in str(achievement.get("content", "")).lower():
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    def _determine_angle(self, achievement: Dict[str, Any], signal: Dict[str, Any], archetype_angles: List[str]) -> str:
        """Determine the content angle for a value proposition."""
        content = (achievement.get("content", "") + " " + signal.get("content", "")).lower()
        
        for angle in archetype_angles:
            if angle.lower() in content:
                return angle
        
        return archetype_angles[0] if archetype_angles else "general"
    
    def _create_achievement_snippet(self, achievement: Dict[str, Any]) -> str:
        """Create a concise snippet from achievement."""
        content = achievement.get("content", "")
        if len(content) > 100:
            return content[:97] + "..."
        return content
    
    def _create_signal_snippet(self, signal: Dict[str, Any]) -> str:
        """Create a concise snippet from signal."""
        content = signal.get("content", "")
        if len(content) > 100:
            return content[:97] + "..."
        return content
    
    def _create_impact_statement(self, achievement: Dict[str, Any], signal: Dict[str, Any], angle: str) -> str:
        """Create impact statement for value proposition."""
        impact_templates = {
            "strategic": "Aligns with strategic objectives and market positioning",
            "operational": "Improves operational efficiency and team performance",
            "technical": "Enhances technical capabilities and innovation capacity",
            "business_outcome": "Delivers measurable business outcomes and ROI",
            "team_impact": "Strengthens team capabilities and collaboration",
            "innovation": "Drives innovation and competitive advantage",
            "scalability": "Enables scalable solutions and growth",
            "skill_alignment": "Aligns skills with role requirements and career growth",
            "career_growth": "Supports career advancement and skill development",
            "opportunity": "Creates new opportunities for mutual benefit",
            "general": "Provides value and supports objectives"
        }
        
        return impact_templates.get(angle, impact_templates["general"])
    
    def _get_opening_tone(self, archetype: str) -> str:
        """Get tone guidance for opening section."""
        tone_map = {
            "C_LEVEL": "Peer-to-peer executive, concise and strategic",
            "EXECUTIVE": "Professional, value-focused and respectful",
            "SENIOR_TA": "Technical peer, consultative and knowledgeable",
            "RECRUITER": "Warm professional, opportunity-focused"
        }
        return tone_map.get(archetype, "Professional and direct")
    
    def _get_body_tone(self, archetype: str) -> str:
        """Get tone guidance for body section."""
        tone_map = {
            "C_LEVEL": "Business outcomes focused, metrics-driven",
            "EXECUTIVE": "Operational impact, team benefits",
            "SENIOR_TA": "Technical depth, problem-solving approach",
            "RECRUITER": "Skill alignment, career development"
        }
        return tone_map.get(archetype, "Informative and relevant")
    
    def _get_cta_tone(self, archetype: str) -> str:
        """Get tone guidance for CTA section."""
        tone_map = {
            "C_LEVEL": "Peer invitation, strategic discussion",
            "EXECUTIVE": "Professional invitation, value exploration",
            "SENIOR_TA": "Technical discussion, knowledge sharing",
            "RECRUITER": "Opportunity discussion, career conversation"
        }
        return tone_map.get(archetype, "Clear and professional")
    
    def _get_cta_guidance(self, archetype: str) -> str:
        """Get specific CTA guidance for archetype."""
        guidance_map = {
            "C_LEVEL": "Suggest strategic partnership or executive discussion",
            "EXECUTIVE": "Propose operational improvement discussion or team consultation",
            "SENIOR_TA": "Recommend technical discussion or architecture review",
            "RECRUITER": "Suggest opportunity exploration or skill alignment discussion"
        }
        return guidance_map.get(archetype, "Suggest follow-up discussion")
    
    def get_fusion_summary(self, plan: FusionPlan) -> Dict[str, Any]:
        """Get a summary of the fusion plan for debugging/telemetry."""
        return {
            "plan_id": f"fusion_{plan.role_title}_{plan.company_name}",
            "archetype": plan.archetype,
            "value_proposition_count": len(plan.value_propositions),
            "section_count": len(plan.sections),
            "primary_cta_style": plan.primary_cta_style,
            "confidence_score": plan.confidence_score,
            "top_angles": [vp.angle for vp in plan.value_propositions[:3]],
            "has_opening": any(s.section_type == "opening" for s in plan.sections),
            "has_body": any(s.section_type == "body" for s in plan.sections),
            "has_cta": any(s.section_type == "cta" for s in plan.sections)
        }
