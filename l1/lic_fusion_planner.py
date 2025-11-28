"""LIC Resume→Message Fusion Planning - L1 Planning Layer

Implements resume→message fusion planning from legacy LIC system.
Plans fusion of sender capabilities with message generation strategy.
Pure planning - no execution, IO, or LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class FusionStrategy(Enum):
    """Resume→message fusion strategies"""
    CAPABILITY_HIGHLIGHT = "capability_highlight"
    ACHIEVEMENT_NARRATIVE = "achievement_narrative"
    SKILLS_ALIGNMENT = "skills_alignment"
    EXPERIENCE_MAPPING = "experience_mapping"
    VALUE_PROPOSITION = "value_proposition"


class MessageComponent(Enum):
    """Message components that can receive fused content"""
    HOOK = "hook"
    VALUE_PROP = "value_prop"
    EVIDENCE = "evidence"
    CTA = "cta"
    CLOSING = "closing"


@dataclass
class FusionMapping:
    """Maps resume content to specific message components"""
    resume_source: str
    message_component: MessageComponent
    fusion_strategy: FusionStrategy
    content_template: str
    priority: int
    required: bool = True


@dataclass
class CapabilityAlignment:
    """Alignment between sender capabilities and recipient needs"""
    sender_capability: str
    recipient_need: str
    alignment_strength: float
    evidence_points: List[str]
    integration_approach: str


@dataclass
class ResumeFusionPlan:
    """Complete resume→message fusion plan"""
    # Core planning data
    mission_context: str
    recipient_archetype: str
    
    # Resume analysis
    key_capabilities: List[str]
    core_achievements: List[str]
    relevant_experience: List[str]
    technical_skills: List[str]
    
    # Fusion strategy
    fusion_mappings: List[FusionMapping]
    capability_alignments: List[CapabilityAlignment]
    
    # Message structure
    hook_strategy: str
    value_prop_strategy: str
    evidence_strategy: str
    cta_strategy: str
    
    # Content planning
    fused_content_templates: Dict[str, str]
    integration_points: List[str]
    
    # Planning metadata
    plan_id: str
    created_at: str
    fusion_priority_order: List[str]
    expected_impact_score: float
    
    # Validation criteria
    required_fusions: List[str]
    optional_fusions: List[str]


class LICFusionPlanner:
    """
    L1 Planner for LIC Resume→Message Fusion
    
    Creates plans for fusing sender resume capabilities with personalized
    message generation strategies based on recipient archetype.
    Pure deterministic planning - no external execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize fusion planner with configuration
        
        Args:
            config: Optional configuration for fusion strategies
        """
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default fusion configuration"""
        return {
            "fusion_agent": {
                "fusion_strategies": {
                    "capability_highlight": {
                        "components": ["hook", "value_prop"],
                        "template": "Leveraging {capability} to address {recipient_need}",
                        "priority": "high"
                    },
                    "achievement_narrative": {
                        "components": ["evidence"],
                        "template": "Achieved {achievement} resulting in {impact}",
                        "priority": "high"
                    },
                    "skills_alignment": {
                        "components": ["value_prop", "evidence"],
                        "template": "Applying {skill} to solve {challenge}",
                        "priority": "medium"
                    },
                    "experience_mapping": {
                        "components": ["evidence", "closing"],
                        "template": "From {experience} gained {insight}",
                        "priority": "medium"
                    },
                    "value_proposition": {
                        "components": ["hook", "cta"],
                        "template": "Delivering {value} through {approach}",
                        "priority": "high"
                    }
                }
            }
        }
    
    def plan_resume_fusion(
        self,
        mission_context: str,
        recipient_archetype: str,
        resume_capabilities: Dict[str, List[str]],
        plan_id: Optional[str] = None
    ) -> ResumeFusionPlan:
        """
        Create resume→message fusion plan
        
        Args:
            mission_context: Context of the outreach mission
            recipient_archetype: Target recipient's archetype
            resume_capabilities: Structured resume capabilities
            plan_id: Optional plan identifier
            
        Returns:
            Complete fusion plan
        """
        # Generate plan ID if not provided
        if plan_id is None:
            import hashlib
            id_string = f"{mission_context}_{recipient_archetype}_fusion"
            plan_id = hashlib.md5(id_string.encode()).hexdigest()[:12]
        
        # Extract key capabilities from resume
        key_capabilities = resume_capabilities.get("technical_skills", [])
        core_achievements = resume_capabilities.get("achievements", [])
        relevant_experience = resume_capabilities.get("experience", [])
        technical_skills = resume_capabilities.get("technologies", [])
        
        # Create fusion mappings based on archetype
        fusion_mappings = self._create_fusion_mappings(recipient_archetype)
        
        # Create capability alignments
        capability_alignments = self._create_capability_alignments(
            key_capabilities, recipient_archetype
        )
        
        # Define message component strategies
        hook_strategy = self._define_hook_strategy(recipient_archetype)
        value_prop_strategy = self._define_value_prop_strategy(recipient_archetype)
        evidence_strategy = self._define_evidence_strategy(recipient_archetype)
        cta_strategy = self._define_cta_strategy(recipient_archetype)
        
        # Create fused content templates
        fused_content_templates = self._create_fusion_templates(recipient_archetype)
        
        # Define integration points
        integration_points = self._define_integration_points(recipient_archetype)
        
        # Determine fusion priority order
        fusion_priority_order = self._prioritize_fusions(recipient_archetype)
        
        # Calculate expected impact score
        expected_impact_score = self._calculate_impact_score(
            key_capabilities, recipient_archetype
        )
        
        # Define validation criteria
        required_fusions, optional_fusions = self._define_fusion_requirements(recipient_archetype)
        
        # Get timestamp
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        return ResumeFusionPlan(
            mission_context=mission_context,
            recipient_archetype=recipient_archetype,
            key_capabilities=key_capabilities,
            core_achievements=core_achievements,
            relevant_experience=relevant_experience,
            technical_skills=technical_skills,
            fusion_mappings=fusion_mappings,
            capability_alignments=capability_alignments,
            hook_strategy=hook_strategy,
            value_prop_strategy=value_prop_strategy,
            evidence_strategy=evidence_strategy,
            cta_strategy=cta_strategy,
            fused_content_templates=fused_content_templates,
            integration_points=integration_points,
            plan_id=plan_id,
            created_at=created_at,
            fusion_priority_order=fusion_priority_order,
            expected_impact_score=expected_impact_score,
            required_fusions=required_fusions,
            optional_fusions=optional_fusions
        )
    
    def _create_fusion_mappings(self, archetype: str) -> List[FusionMapping]:
        """Create fusion mappings based on recipient archetype"""
        mappings = []
        
        # Base mappings for all archetypes
        base_mappings = [
            FusionMapping(
                resume_source="technical_skills",
                message_component=MessageComponent.VALUE_PROP,
                fusion_strategy=FusionStrategy.CAPABILITY_HIGHLIGHT,
                content_template="Leveraging {skill} expertise to drive {outcome}",
                priority=1,
                required=True
            ),
            FusionMapping(
                resume_source="achievements",
                message_component=MessageComponent.EVIDENCE,
                fusion_strategy=FusionStrategy.ACHIEVEMENT_NARRATIVE,
                content_template="Achieved {achievement} resulting in {impact}",
                priority=2,
                required=True
            )
        ]
        
        mappings.extend(base_mappings)
        
        # Add archetype-specific mappings
        if archetype == "executive":
            mappings.extend([
                FusionMapping(
                    resume_source="leadership_experience",
                    message_component=MessageComponent.HOOK,
                    fusion_strategy=FusionStrategy.VALUE_PROPOSITION,
                    content_template="Delivering {value} through strategic {approach}",
                    priority=1,
                    required=True
                ),
                FusionMapping(
                    resume_source="business_impact",
                    message_component=MessageComponent.CTA,
                    fusion_strategy=FusionStrategy.EXPERIENCE_MAPPING,
                    content_template="From {experience} gained strategic {insight}",
                    priority=3,
                    required=False
                )
            ])
        elif archetype == "technical_lead":
            mappings.extend([
                FusionMapping(
                    resume_source="technical_skills",
                    message_component=MessageComponent.HOOK,
                    fusion_strategy=FusionStrategy.SKILLS_ALIGNMENT,
                    content_template="Applying {skill} to solve {technical_challenge}",
                    priority=1,
                    required=True
                ),
                FusionMapping(
                    resume_source="project_experience",
                    message_component=MessageComponent.EVIDENCE,
                    fusion_strategy=FusionStrategy.EXPERIENCE_MAPPING,
                    content_template="From {project} delivered {solution}",
                    priority=2,
                    required=True
                )
            ])
        elif archetype == "hiring_manager":
            mappings.extend([
                FusionMapping(
                    resume_source="team_leadership",
                    message_component=MessageComponent.VALUE_PROP,
                    fusion_strategy=FusionStrategy.CAPABILITY_HIGHLIGHT,
                    content_template="Building {team_type} teams through {leadership_approach}",
                    priority=1,
                    required=True
                ),
                FusionMapping(
                    resume_source="mentoring_experience",
                    message_component=MessageComponent.CTA,
                    fusion_strategy=FusionStrategy.VALUE_PROPOSITION,
                    content_template="Contributing {mentorship_value} to team {growth}",
                    priority=3,
                    required=False
                )
            ])
        
        return mappings
    
    def _create_capability_alignments(
        self,
        capabilities: List[str],
        archetype: str
    ) -> List[CapabilityAlignment]:
        """Create alignments between sender capabilities and recipient needs"""
        alignments = []
        
        # Define recipient needs by archetype
        recipient_needs = {
            "executive": [
                "strategic_leadership", "business_growth", "market_expansion",
                "operational_excellence", "innovation_driving"
            ],
            "hiring_manager": [
                "team_building", "talent_development", "process_improvement",
                "project_delivery", "culture_enhancement"
            ],
            "technical_lead": [
                "technical_solutions", "architecture_design", "innovation",
                "performance_optimization", "scalability"
            ],
            "recruiter": [
                "candidate_qualifications", "career_progression", "skill_assessment",
                "opportunity_matching", "professional_development"
            ]
        }
        
        # Create alignments for each capability
        for capability in capabilities[:10]:  # Limit to top 10 capabilities
            for need in recipient_needs.get(archetype, []):
                # Simple alignment strength calculation
                alignment_strength = self._calculate_alignment_strength(capability, need)
                
                if alignment_strength > 0.5:  # Only include meaningful alignments
                    evidence_points = self._generate_evidence_points(capability, need)
                    integration_approach = self._define_integration_approach(capability, need, archetype)
                    
                    alignment = CapabilityAlignment(
                        sender_capability=capability,
                        recipient_need=need,
                        alignment_strength=alignment_strength,
                        evidence_points=evidence_points,
                        integration_approach=integration_approach
                    )
                    alignments.append(alignment)
        
        # Sort by alignment strength and limit to top alignments
        alignments.sort(key=lambda x: x.alignment_strength, reverse=True)
        return alignments[:15]  # Limit to top 15 alignments
    
    def _calculate_alignment_strength(self, capability: str, need: str) -> float:
        """Calculate alignment strength between capability and need"""
        # Simple keyword-based alignment calculation
        capability_words = set(capability.lower().split('_'))
        need_words = set(need.lower().split('_'))
        
        # Calculate overlap
        overlap = len(capability_words & need_words)
        total_words = len(capability_words | need_words)
        
        if total_words == 0:
            return 0.0
        
        # Base similarity score
        similarity = overlap / total_words
        
        # Apply some domain-specific boosting
        if "leadership" in capability and "leadership" in need:
            similarity += 0.2
        elif "technical" in capability and "technical" in need:
            similarity += 0.2
        elif "team" in capability and "team" in need:
            similarity += 0.15
        
        return min(similarity, 1.0)
    
    def _generate_evidence_points(self, capability: str, need: str) -> List[str]:
        """Generate evidence points for capability-need alignment"""
        evidence_templates = [
            f"Proven track record in {capability.replace('_', ' ')}",
            f"Successfully applied {capability.replace('_', ' ')} to address {need.replace('_', ' ')}",
            f"Quantified results in {capability.replace('_', ' ')} domain",
            f"Recognition for excellence in {capability.replace('_', ' ')}"
        ]
        
        return evidence_templates[:3]  # Return top 3 evidence points
    
    def _define_integration_approach(self, capability: str, need: str, archetype: str) -> str:
        """Define how to integrate capability into message"""
        approaches = {
            "executive": "Strategic integration with business metrics and ROI focus",
            "hiring_manager": "Collaborative integration with team impact and culture fit",
            "technical_lead": "Technical integration with specific solutions and innovations",
            "recruiter": "Professional integration with career progression and skill development"
        }
        
        base_approach = approaches.get(archetype, "Direct capability highlighting")
        return f"{base_approach} for {capability} addressing {need}"
    
    def _define_hook_strategy(self, archetype: str) -> str:
        """Define hook strategy based on archetype"""
        strategies = {
            "executive": "Lead with strategic value proposition and high-level business impact",
            "hiring_manager": "Open with team leadership and collaborative achievements",
            "technical_lead": "Start with technical innovation and problem-solving capabilities",
            "recruiter": "Begin with professional qualifications and career alignment",
            "influencer": "Hook with thought leadership and industry insights",
            "peer": "Open with shared experience and collaborative opportunities"
        }
        
        return strategies.get(archetype, strategies["peer"])
    
    def _define_value_prop_strategy(self, archetype: str) -> str:
        """Define value proposition strategy based on archetype"""
        strategies = {
            "executive": "Focus on strategic outcomes, business growth, and competitive advantages",
            "hiring_manager": "Emphasize team building, process improvements, and leadership impact",
            "technical_lead": "Highlight technical solutions, innovations, and engineering excellence",
            "recruiter": "Showcase professional development, skill progression, and opportunity fit",
            "influencer": "Demonstrate industry expertise, innovation, and thought leadership",
            "peer": "Focus on mutual value, collaboration, and shared professional interests"
        }
        
        return strategies.get(archetype, strategies["peer"])
    
    def _define_evidence_strategy(self, archetype: str) -> str:
        """Define evidence strategy based on archetype"""
        strategies = {
            "executive": "Provide quantified business impact, strategic achievements, and market results",
            "hiring_manager": "Show team performance, process improvements, and leadership examples",
            "technical_lead": "Present technical innovations, project outcomes, and problem-solving results",
            "recruiter": "Demonstrate career progression, skill development, and professional achievements",
            "influencer": "Share industry recognition, innovative contributions, and thought leadership examples",
            "peer": "Provide collaborative successes, shared projects, and mutual accomplishments"
        }
        
        return strategies.get(archetype, strategies["peer"])
    
    def _define_cta_strategy(self, archetype: str) -> str:
        """Define call-to-action strategy based on archetype"""
        strategies = {
            "executive": "Strategic discussion invitation focused on business opportunities",
            "hiring_manager": "Collaborative conversation about team and role alignment",
            "technical_lead": "Technical discussion about solutions and innovations",
            "recruiter": "Professional discussion about opportunity fit and next steps",
            "influencer": "Thought leadership exchange and industry collaboration",
            "peer": "Collaborative discussion about shared interests and opportunities"
        }
        
        return strategies.get(archetype, strategies["peer"])
    
    def _create_fusion_templates(self, archetype: str) -> Dict[str, str]:
        """Create content templates for fused message components"""
        templates = {
            "executive": {
                "hook": "Driving {strategic_outcome} through {leadership_approach} and {business_value}",
                "value_prop": "Leveraging {capability} to achieve {business_metric} and {competitive_advantage}",
                "evidence": "Led {initiative} resulting in {quantified_impact} and {market_position}",
                "cta": "Let's discuss how {strategic_approach} can accelerate your {business_objective}"
            },
            "hiring_manager": {
                "hook": "Building {team_type} teams through {leadership_style} and {collaboration_approach}",
                "value_prop": "Applying {management_skill} to enhance {team_performance} and {culture_development}",
                "evidence": "Mentored {team_size} team members achieving {performance_improvement} and {retention_rate}",
                "cta": "I'd like to share how {team_approach} can strengthen your {hiring_objective}"
            },
            "technical_lead": {
                "hook": "Solving {technical_challenge} with {innovative_approach} and {engineering_excellence}",
                "value_prop": "Applying {technical_skill} to deliver {solution_type} and {performance_gain}",
                "evidence": "Architected {system_type} achieving {scalability_metric} and {reliability_improvement}",
                "cta": "Let's explore how {technical_solution} can address your {engineering_challenge}"
            }
        }
        
        return templates.get(archetype, templates["hiring_manager"])
    
    def _define_integration_points(self, archetype: str) -> List[str]:
        """Define integration points for resume content in messages"""
        base_points = [
            "opening_hook_capability",
            "value_proposition_skills",
            "evidence_achievements",
            "closing_value_reinforcement"
        ]
        
        # Add archetype-specific points
        if archetype == "executive":
            base_points.extend([
                "strategic_metrics_insertion",
                "business_impact_quantification"
            ])
        elif archetype == "technical_lead":
            base_points.extend([
                "technical_solution_insertion",
                "innovation_highlight"
            ])
        elif archetype == "hiring_manager":
            base_points.extend([
                "team_leadership_examples",
                "culture_contributions"
            ])
        
        return base_points
    
    def _prioritize_fusions(self, archetype: str) -> List[str]:
        """Prioritize fusion strategies based on archetype"""
        base_priority = [
            "capability_highlight",
            "achievement_narrative",
            "value_proposition",
            "skills_alignment",
            "experience_mapping"
        ]
        
        # Adjust priority based on archetype
        if archetype == "executive":
            base_priority = [
                "value_proposition",
                "capability_highlight",
                "achievement_narrative",
                "experience_mapping",
                "skills_alignment"
            ]
        elif archetype == "technical_lead":
            base_priority = [
                "skills_alignment",
                "capability_highlight",
                "achievement_narrative",
                "experience_mapping",
                "value_proposition"
            ]
        
        return base_priority
    
    def _calculate_impact_score(self, capabilities: List[str], archetype: str) -> float:
        """Calculate expected impact score for fusion plan"""
        # Base score by archetype
        base_scores = {
            "executive": 0.8,
            "hiring_manager": 0.7,
            "technical_lead": 0.7,
            "recruiter": 0.6,
            "influencer": 0.5,
            "peer": 0.5
        }
        
        base_score = base_scores.get(archetype, 0.5)
        
        # Adjust based on capability count and diversity
        capability_factor = min(len(capabilities) / 10.0, 1.0)  # Cap at 1.0
        diversity_factor = len(set(capabilities)) / max(len(capabilities), 1)
        
        # Calculate final score
        final_score = base_score * (0.7 + 0.2 * capability_factor + 0.1 * diversity_factor)
        
        return min(final_score, 1.0)
    
    def _define_fusion_requirements(self, archetype: str) -> Tuple[List[str], List[str]]:
        """Define required and optional fusions based on archetype"""
        required = ["capability_highlight", "achievement_narrative"]
        optional = ["skills_alignment", "experience_mapping", "value_proposition"]
        
        # Adjust based on archetype
        if archetype == "executive":
            required.append("value_proposition")
        elif archetype == "technical_lead":
            required.append("skills_alignment")
        
        return required, optional
    
    def validate_plan(self, plan: ResumeFusionPlan) -> List[str]:
        """
        Validate fusion plan for completeness and correctness
        
        Args:
            plan: Fusion plan to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not plan.mission_context:
            errors.append("mission_context is required")
        
        if not plan.recipient_archetype:
            errors.append("recipient_archetype is required")
        
        if not plan.fusion_mappings:
            errors.append("fusion_mappings cannot be empty")
        
        if not plan.capability_alignments:
            errors.append("capability_alignments cannot be empty")
        
        if not plan.plan_id:
            errors.append("plan_id is required")
        
        if not plan.key_capabilities:
            errors.append("key_capabilities cannot be empty")
        
        if plan.expected_impact_score < 0.0 or plan.expected_impact_score > 1.0:
            errors.append("expected_impact_score must be between 0.0 and 1.0")
        
        return errors
