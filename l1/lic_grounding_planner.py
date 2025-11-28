"""LIC Sender Grounding Planning - L1 Planning Layer

Implements HOP-3 sender grounding planning from legacy LIC system.
Plans extraction of sender capabilities from knowledge base.
Pure planning - no execution, IO, or LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum


class GroundingSource(Enum):
    """Sources for sender grounding information"""
    MASTER_RESUME = "master_resume"
    SENDER_KNOWLEDGE_BASE = "sender_knowledge_base"
    VOICE_PROFILE = "voice_profile"
    SKILL_INVENTORY = "skill_inventory"
    EXPERIENCE_HISTORY = "experience_history"


class CapabilityType(Enum):
    """Types of sender capabilities to extract"""
    TECHNICAL_SKILLS = "technical_skills"
    DOMAIN_EXPERTISE = "domain_expertise"
    LEADERSHIP_EXPERIENCE = "leadership_experience"
    PROJECT_ACHIEVEMENTS = "project_achievements"
    COMMUNICATION_STYLE = "communication_style"
    INDUSTRY_KNOWLEDGE = "industry_knowledge"


@dataclass
class ExtractionTarget:
    """Specific information to extract from grounding sources"""
    source_type: GroundingSource
    capability_type: CapabilityType
    extraction_fields: List[str]
    priority: str
    required: bool = True


@dataclass
class SenderGroundingPlan:
    """Complete sender grounding extraction plan"""
    # Core planning data
    mission_context: str
    recipient_archetype: str
    
    # Extraction configuration
    extraction_targets: List[ExtractionTarget]
    source_files: Dict[str, str]
    
    # Capability mapping
    technical_capabilities: List[str]
    domain_expertise_areas: List[str]
    leadership_qualifications: List[str]
    achievement_highlights: List[str]
    
    # Communication planning
    voice_tone_mapping: Dict[str, str]
    communication_strategy: str
    
    # Planning metadata
    plan_id: str
    created_at: str
    extraction_priority_order: List[str]
    expected_outputs: Dict[str, List[str]]
    
    # Grounding validation
    required_capabilities: Set[str]
    optional_capabilities: Set[str]


class LICGroundingPlanner:
    """
    L1 Planner for LIC HOP-3 Sender Grounding
    
    Creates plans for extracting sender capabilities from knowledge base
    to support personalized message generation.
    Pure deterministic planning - no external execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize grounding planner with configuration
        
        Args:
            config: Optional configuration for grounding extraction
        """
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default grounding configuration"""
        return {
            "sender_grounding_agent": {
                "source_files": {
                    "master_resume": "master_resume.json",
                    "sender_knowledge_base": "sender_knowledge_base.json", 
                    "voice_profile": "sender_voice_profile.json"
                },
                "extraction_targets": {
                    "technical_skills": {
                        "fields": ["skills", "technologies", "tools", "languages"],
                        "priority": "high",
                        "required": True
                    },
                    "domain_expertise": {
                        "fields": ["domains", "industries", "specializations"],
                        "priority": "high", 
                        "required": True
                    },
                    "leadership_experience": {
                        "fields": ["leadership", "management", "mentorship"],
                        "priority": "medium",
                        "required": False
                    },
                    "project_achievements": {
                        "fields": ["achievements", "impact", "results"],
                        "priority": "medium",
                        "required": False
                    },
                    "communication_style": {
                        "fields": ["communication", "style", "tone"],
                        "priority": "low",
                        "required": False
                    }
                }
            }
        }
    
    def plan_grounding_extraction(
        self,
        mission_context: str,
        recipient_archetype: str,
        plan_id: Optional[str] = None
    ) -> SenderGroundingPlan:
        """
        Create sender grounding extraction plan
        
        Args:
            mission_context: Context of the outreach mission
            recipient_archetype: Target recipient's archetype
            plan_id: Optional plan identifier
            
        Returns:
            Complete grounding extraction plan
        """
        # Generate plan ID if not provided
        if plan_id is None:
            import hashlib
            id_string = f"{mission_context}_{recipient_archetype}"
            plan_id = hashlib.md5(id_string.encode()).hexdigest()[:12]
        
        # Extract configuration
        agent_config = self.config["sender_grounding_agent"]
        source_files = agent_config["source_files"]
        extraction_config = agent_config["extraction_targets"]
        
        # Create extraction targets
        extraction_targets = self._create_extraction_targets(extraction_config)
        
        # Define capability categories based on archetype
        technical_capabilities = self._define_technical_capabilities(recipient_archetype)
        domain_expertise_areas = self._define_domain_expertise(recipient_archetype)
        leadership_qualifications = self._define_leadership_qualifications(recipient_archetype)
        achievement_highlights = self._define_achievement_highlights(recipient_archetype)
        
        # Plan voice tone mapping based on archetype
        voice_tone_mapping = self._create_voice_tone_mapping(recipient_archetype)
        communication_strategy = self._define_communication_strategy(recipient_archetype)
        
        # Determine extraction priority order
        extraction_priority_order = self._prioritize_extractions(recipient_archetype)
        
        # Define expected outputs
        expected_outputs = self._define_expected_outputs(recipient_archetype)
        
        # Define capability requirements
        required_capabilities, optional_capabilities = self._define_capability_requirements(recipient_archetype)
        
        # Get timestamp
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        return SenderGroundingPlan(
            mission_context=mission_context,
            recipient_archetype=recipient_archetype,
            extraction_targets=extraction_targets,
            source_files=source_files,
            technical_capabilities=technical_capabilities,
            domain_expertise_areas=domain_expertise_areas,
            leadership_qualifications=leadership_qualifications,
            achievement_highlights=achievement_highlights,
            voice_tone_mapping=voice_tone_mapping,
            communication_strategy=communication_strategy,
            plan_id=plan_id,
            created_at=created_at,
            extraction_priority_order=extraction_priority_order,
            expected_outputs=expected_outputs,
            required_capabilities=required_capabilities,
            optional_capabilities=optional_capabilities
        )
    
    def _create_extraction_targets(self, extraction_config: Dict[str, Any]) -> List[ExtractionTarget]:
        """Create extraction targets from configuration"""
        targets = []
        
        for capability_name, config in extraction_config.items():
            # Map capability name to enum
            try:
                capability_type = CapabilityType(capability_name)
            except ValueError:
                # Skip unknown capability types
                continue
            
            # Create extraction targets for each source
            for source_type in [GroundingSource.MASTER_RESUME, GroundingSource.SENDER_KNOWLEDGE_BASE]:
                target = ExtractionTarget(
                    source_type=source_type,
                    capability_type=capability_type,
                    extraction_fields=config["fields"],
                    priority=config["priority"],
                    required=config["required"]
                )
                targets.append(target)
        
        return targets
    
    def _define_technical_capabilities(self, archetype: str) -> List[str]:
        """Define technical capabilities to extract based on recipient archetype"""
        base_capabilities = [
            "programming_languages",
            "frameworks_libraries", 
            "databases",
            "cloud_platforms",
            "devops_tools",
            "methodologies"
        ]
        
        # Add archetype-specific capabilities
        if archetype == "technical_lead":
            base_capabilities.extend([
                "architecture_patterns",
                "system_design",
                "scalability_solutions",
                "performance_optimization"
            ])
        elif archetype == "executive":
            base_capabilities.extend([
                "technology_strategy",
                "digital_transformation",
                "innovation_management",
                "technical_leadership"
            ])
        elif archetype == "hiring_manager":
            base_capabilities.extend([
                "team_technologies",
                "development_practices",
                "technical_mentoring",
                "skill_assessment"
            ])
        
        return base_capabilities
    
    def _define_domain_expertise(self, archetype: str) -> List[str]:
        """Define domain expertise areas based on recipient archetype"""
        base_domains = [
            "software_development",
            "product_engineering",
            "data_analytics",
            "machine_learning"
        ]
        
        # Add archetype-specific domains
        if archetype == "executive":
            base_domains.extend([
                "business_strategy",
                "market_analysis",
                "competitive_intelligence",
                "financial_modeling"
            ])
        elif archetype == "technical_lead":
            base_domains.extend([
                "system_architecture",
            "infrastructure_design",
                "security_engineering",
                "performance_engineering"
            ])
        elif archetype == "recruiter":
            base_domains.extend([
                "talent_acquisition",
                "human_resources",
                "organizational_development",
                "workforce_planning"
            ])
        
        return base_domains
    
    def _define_leadership_qualifications(self, archetype: str) -> List[str]:
        """Define leadership qualifications based on recipient archetype"""
        base_leadership = [
            "project_management",
            "team_collaboration",
            "decision_making",
            "problem_solving"
        ]
        
        # Add archetype-specific leadership
        if archetype == "executive":
            base_leadership.extend([
                "strategic_planning",
                "executive_leadership",
                "change_management",
                "stakeholder_management"
            ])
        elif archetype == "hiring_manager":
            base_leadership.extend([
                "team_leadership",
                "talent_development",
                "performance_management",
                "resource_allocation"
            ])
        elif archetype == "technical_lead":
            base_leadership.extend([
                "technical_leadership",
                "architecture_decisions",
                "technology_roadmapping",
                "innovation_management"
            ])
        
        return base_leadership
    
    def _define_achievement_highlights(self, archetype: str) -> List[str]:
        """Define achievement categories based on recipient archetype"""
        base_achievements = [
            "project_successes",
            "performance_improvements",
            "cost_savings",
            "efficiency_gains"
        ]
        
        # Add archetype-specific achievements
        if archetype == "executive":
            base_achievements.extend([
                "revenue_growth",
                "market_expansion",
                "strategic_initiatives",
                "business_transformation"
            ])
        elif archetype == "technical_lead":
            base_achievements.extend([
                "technical_innovations",
                "scalability_achievements",
                "architecture_improvements",
                "performance_optimizations"
            ])
        elif archetype == "hiring_manager":
            base_achievements.extend([
                "team_building",
                "talent_acquisition",
                "process_improvements",
                "culture_development"
            ])
        
        return base_achievements
    
    def _create_voice_tone_mapping(self, archetype: str) -> Dict[str, str]:
        """Create voice tone mapping based on recipient archetype"""
        tone_mappings = {
            "executive": {
                "formality": "high",
                "directness": "high", 
                "strategic_focus": "business_value",
                "communication_style": "executive_briefing"
            },
            "hiring_manager": {
                "formality": "medium",
                "directness": "medium",
                "strategic_focus": "team_value",
                "communication_style": "collaborative"
            },
            "technical_lead": {
                "formality": "medium",
                "directness": "high",
                "strategic_focus": "technical_value",
                "communication_style": "technical_discussion"
            },
            "recruiter": {
                "formality": "low",
                "directness": "medium",
                "strategic_focus": "candidate_value",
                "communication_style": "professional_friendly"
            },
            "influencer": {
                "formality": "low",
                "directness": "medium",
                "strategic_focus": "innovation_value",
                "communication_style": "thought_leadership"
            },
            "peer": {
                "formality": "low",
                "directness": "high",
                "strategic_focus": "peer_value",
                "communication_style": "collaborative"
            }
        }
        
        return tone_mappings.get(archetype, tone_mappings["peer"])
    
    def _define_communication_strategy(self, archetype: str) -> str:
        """Define communication strategy based on recipient archetype"""
        strategies = {
            "executive": "Focus on business outcomes, strategic impact, and high-level value propositions with concise, data-driven messaging.",
            "hiring_manager": "Emphasize team collaboration, leadership capabilities, and specific contributions to team success and culture.",
            "technical_lead": "Highlight technical expertise, problem-solving capabilities, and specific technical achievements and innovations.",
            "recruiter": "Showcase professional qualifications, career progression, and alignment with opportunity requirements.",
            "influencer": "Demonstrate thought leadership, industry insights, and innovative perspectives on relevant trends.",
            "peer": "Focus on shared experiences, collaborative opportunities, and mutual professional interests."
        }
        
        return strategies.get(archetype, strategies["peer"])
    
    def _prioritize_extractions(self, archetype: str) -> List[str]:
        """Prioritize extraction order based on recipient archetype"""
        base_priority = [
            "technical_skills",
            "domain_expertise",
            "leadership_experience",
            "project_achievements",
            "communication_style"
        ]
        
        # Adjust priority based on archetype
        if archetype == "executive":
            base_priority = [
                "leadership_experience",
                "domain_expertise", 
                "technical_skills",
                "project_achievements",
                "communication_style"
            ]
        elif archetype == "technical_lead":
            base_priority = [
                "technical_skills",
                "domain_expertise",
                "project_achievements",
                "leadership_experience",
                "communication_style"
            ]
        
        return base_priority
    
    def _define_expected_outputs(self, archetype: str) -> Dict[str, List[str]]:
        """Define expected outputs from grounding extraction"""
        base_outputs = {
            "technical_capabilities": ["skills_list", "proficiency_levels", "experience_years"],
            "domain_expertise": ["domains_list", "expertise_depth", "industry_knowledge"],
            "leadership_qualifications": ["leadership_roles", "team_sizes", "management_experience"],
            "achievement_highlights": ["key_achievements", "quantified_impact", "recognition_awards"]
        }
        
        # Add archetype-specific outputs
        if archetype == "executive":
            base_outputs["strategic_capabilities"] = ["strategic_initiatives", "business_impact", "growth_metrics"]
        elif archetype == "technical_lead":
            base_outputs["technical_leadership"] = ["architecture_decisions", "technical_roadmaps", "innovation_projects"]
        
        return base_outputs
    
    def _define_capability_requirements(self, archetype: str) -> Tuple[Set[str], Set[str]]:
        """Define required and optional capabilities based on archetype"""
        required = {"technical_skills", "domain_expertise"}
        optional = {"leadership_experience", "project_achievements", "communication_style"}
        
        # Adjust based on archetype
        if archetype == "executive":
            required.add("leadership_experience")
        elif archetype == "technical_lead":
            required.add("project_achievements")
        
        return required, optional
    
    def validate_plan(self, plan: SenderGroundingPlan) -> List[str]:
        """
        Validate grounding plan for completeness and correctness
        
        Args:
            plan: Grounding plan to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not plan.mission_context:
            errors.append("mission_context is required")
        
        if not plan.recipient_archetype:
            errors.append("recipient_archetype is required")
        
        if not plan.extraction_targets:
            errors.append("extraction_targets cannot be empty")
        
        if not plan.source_files:
            errors.append("source_files cannot be empty")
        
        if not plan.plan_id:
            errors.append("plan_id is required")
        
        if not plan.technical_capabilities:
            errors.append("technical_capabilities cannot be empty")
        
        if not plan.domain_expertise_areas:
            errors.append("domain_expertise_areas cannot be empty")
        
        return errors
