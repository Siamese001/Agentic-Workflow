"""
L1 Message Planner - Pure computation for structured message planning.

Implements pure planning logic to create structured message plans with
temperature schedules and constraints without any generation or execution.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from .outreach_dataclasses import (
    ArchetypeContext,
    MessagePlan,
    SECTION_TEMPERATURE_SCHEDULE
)


@dataclass
class MessageContent:
    """Pure data structure for message content planning."""
    recipient_name: str
    recipient_title: str
    company_name: str
    value_proposition: str
    key_points: List[str]
    personalization_elements: List[str]
    constraints: List[str]
    metadata: Dict[str, Any]


class MessagePlanner:
    """
    Pure L1 planner for message structure and generation parameters.
    
    Performs only computational planning to determine message structure,
    temperature schedules, and constraints without generating content.
    """
    
    def __init__(self):
        # Pure section templates - no external dependencies
        self._section_templates = self._build_section_templates()
        
        # Pure temperature adjustments based on archetype
        self._temperature_adjustments = {
            "technical_leader": {
                "subject": -0.1,  # More formal
                "hook": -0.1,     # More analytical
                "body": 0.0,      # Standard
                "cta": -0.1,      # More formal
                "signature": 0.0  # Standard
            },
            "business_executive": {
                "subject": -0.2,  # Very formal
                "hook": -0.1,     # Strategic
                "body": -0.1,     # Concise
                "cta": -0.1,      # Professional
                "signature": -0.1 # Formal
            },
            "hiring_manager": {
                "subject": 0.0,   # Standard
                "hook": 0.1,      # More engaging
                "body": 0.0,      # Standard
                "cta": 0.1,       # More action-oriented
                "signature": 0.1  # Warmer
            },
            "individual_contributor": {
                "subject": 0.1,   # More casual
                "hook": 0.2,      # More creative
                "body": 0.1,      # More conversational
                "cta": 0.0,       # Standard
                "signature": 0.2  # More personal
            }
        }
        
        # Pure constraint mappings
        self._constraint_mappings = {
            "technical_leader": [
                "technical_accuracy_required",
                "data_driven_claims",
                "avoid_hype_language",
                "include_specific_metrics"
            ],
            "business_executive": [
                "business_value_focus",
                "concise_messaging",
                "roi_claims_supported",
                "executive_tone_maintained"
            ],
            "hiring_manager": [
                "role_fit_emphasis",
                "team_culture_alignment",
                "availability_clarity",
                "professional_enthusiasm"
            ],
            "individual_contributor": [
                "technical_relevance",
                "skill_growth_opportunity",
                "collaborative_benefits",
                "authentic_tone"
            ]
        }
    
    def _build_section_templates(self) -> Dict[str, Dict[str, Any]]:
        """Build pure section templates for message planning."""
        return {
            "subject": {
                "max_length": 60,
                "required_elements": ["value_proposition"],
                "optional_elements": ["personalization", "urgency"],
                "style_guidelines": ["concise", "action_oriented"]
            },
            "hook": {
                "max_length": 150,
                "required_elements": ["context", "relevance"],
                "optional_elements": ["personalization", "achievement"],
                "style_guidelines": ["engaging", "specific"]
            },
            "body": {
                "max_length": 500,
                "required_elements": ["value_proposition", "evidence"],
                "optional_elements": ["technical_details", "company_info", "personalization"],
                "style_guidelines": ["structured", "persuasive"]
            },
            "cta": {
                "max_length": 100,
                "required_elements": ["action", "contact_info"],
                "optional_elements": ["urgency", "value_reinforcement"],
                "style_guidelines": ["clear", "actionable"]
            },
            "signature": {
                "max_length": 50,
                "required_elements": ["name", "title"],
                "optional_elements": ["company", "contact"],
                "style_guidelines": ["professional", "consistent"]
            }
        }
    
    def create_message_plan(
        self, 
        content: MessageContent, 
        archetype_context: ArchetypeContext
    ) -> MessagePlan:
        """
        Create structured message plan using pure computation.
        """
        # Plan sections
        sections = self._plan_sections(content, archetype_context)
        
        # Calculate temperature schedule
        temperature_schedule = self._calculate_temperature_schedule(archetype_context)
        
        # Determine constraints
        constraints = self._determine_constraints(content, archetype_context)
        
        # Estimate tokens
        estimated_tokens = self._estimate_tokens(sections)
        
        # Determine generation strategy
        generation_strategy = self._determine_generation_strategy(archetype_context)
        
        return MessagePlan(
            sections=sections,
            temperature_schedule=temperature_schedule,
            constraints=constraints,
            estimated_tokens=estimated_tokens,
            generation_strategy=generation_strategy,
            metadata={
                "archetype": archetype_context.archetype,
                "target_company": content.company_name,
                "planning_timestamp": self._get_current_timestamp(),
                "complexity_score": self._calculate_complexity_score(sections, constraints)
            }
        )
    
    def _plan_sections(
        self, 
        content: MessageContent, 
        archetype_context: ArchetypeContext
    ) -> Dict[str, str]:
        """Plan content for each message section."""
        sections = {}
        
        # Subject line planning
        sections["subject"] = self._plan_subject(content, archetype_context)
        
        # Hook planning
        sections["hook"] = self._plan_hook(content, archetype_context)
        
        # Body planning
        sections["body"] = self._plan_body(content, archetype_context)
        
        # CTA planning
        sections["cta"] = self._plan_cta(content, archetype_context)
        
        # Signature planning
        sections["signature"] = self._plan_signature(content, archetype_context)
        
        return sections
    
    def _plan_subject(
        self, 
        content: MessageContent, 
        archetype_context: ArchetypeContext
    ) -> str:
        """Plan subject line content."""
        # Base subject structure
        subject_parts = []
        
        # Add value proposition
        if content.value_proposition:
            subject_parts.append(content.value_proposition[:30])  # Truncate for subject
        
        # Add personalization if available
        if content.personalization_elements and archetype_context.tone_params.personalization_level != "low":
            personalization = content.personalization_elements[0]
            subject_parts.append(f"re: {personalization[:20]}")
        
        # Add company reference for executives
        if archetype_context.archetype == "business_executive":
            subject_parts.append(f"{content.company_name}")
        
        # Combine and format
        if len(subject_parts) == 1:
            return subject_parts[0]
        elif len(subject_parts) == 2:
            return f"{subject_parts[0]} | {subject_parts[1]}"
        else:
            return f"{subject_parts[0]}: {subject_parts[1]}"
    
    def _plan_hook(
        self, 
        content: MessageContent, 
        archetype_context: ArchetypeContext
    ) -> str:
        """Plan hook content."""
        hook_parts = []
        
        # Context establishment
        if archetype_context.archetype == "technical_leader":
            hook_parts.append(f"Noticed your work at {content.company_name}")
        elif archetype_context.archetype == "business_executive":
            hook_parts.append(f"Following {content.company_name}'s growth")
        elif archetype_context.archetype == "hiring_manager":
            hook_parts.append(f"Interested in your team at {content.company_name}")
        else:
            hook_parts.append(f"Connecting about {content.company_name}")
        
        # Add personalization
        if content.personalization_elements:
            hook_parts.append(content.personalization_elements[0])
        
        # Add relevance statement
        hook_parts.append("thought you might find this relevant")
        
        return " ".join(hook_parts)
    
    def _plan_body(
        self, 
        content: MessageContent, 
        archetype_context: ArchetypeContext
    ) -> str:
        """Plan body content structure."""
        body_parts = []
        
        # Opening based on archetype
        if archetype_context.archetype == "technical_leader":
            body_parts.append("I'm reaching out regarding technical leadership opportunities")
        elif archetype_context.archetype == "business_executive":
            body_parts.append("I'm writing to discuss potential business collaboration")
        elif archetype_context.archetype == "hiring_manager":
            body_parts.append("I'm interested in exploring opportunities with your team")
        else:
            body_parts.append("I'm reaching out to connect about potential collaboration")
        
        # Value proposition
        if content.value_proposition:
            body_parts.append(f"Key value: {content.value_proposition}")
        
        # Key points
        for point in content.key_points[:3]:  # Limit to 3 key points
            body_parts.append(f"• {point}")
        
        # Company-specific content
        if archetype_context.archetype in ["technical_leader", "business_executive"]:
            body_parts.append(f"Specific to {content.company_name}'s context")
        
        return " ".join(body_parts)
    
    def _plan_cta(
        self, 
        content: MessageContent, 
        archetype_context: ArchetypeContext
    ) -> str:
        """Plan call-to-action content."""
        cta_type = archetype_context.cta_params.cta_type
        
        if cta_type == "technical_discussion":
            return "Would you be open to a brief technical discussion next week?"
        elif cta_type == "business_meeting":
            return "I'd appreciate 15 minutes to discuss potential business value"
        elif cta_type == "interview_request":
            return "Are you available for a brief call to discuss potential fit?"
        elif cta_type == "collaboration_discussion":
            return "Would you be interested in exploring collaboration opportunities?"
        else:
            return "Would you be open to a brief conversation to learn more?"
    
    def _plan_signature(
        self, 
        content: MessageContent, 
        archetype_context: ArchetypeContext
    ) -> str:
        """Plan signature content."""
        # This would typically be the sender's info
        # For planning purposes, we'll create a template
        return "[Sender Name] | [Title] | [Contact Information]"
    
    def _calculate_temperature_schedule(
        self, 
        archetype_context: ArchetypeContext
    ) -> Dict[str, float]:
        """Calculate temperature schedule based on archetype and context."""
        base_schedule = SECTION_TEMPERATURE_SCHEDULE.copy()
        
        # Get archetype adjustments
        adjustments = self._temperature_adjustments.get(
            archetype_context.archetype, 
            {}
        )
        
        # Apply adjustments
        final_schedule = {}
        for section, base_temp in base_schedule.items():
            adjustment = adjustments.get(section, 0.0)
            final_temp = max(0.1, min(1.5, base_temp + adjustment))  # Clamp between 0.1 and 1.5
            final_schedule[section] = final_temp
        
        # Apply tone parameter adjustments
        if archetype_context.tone_params.enthusiasm_level == "high":
            final_schedule["hook"] += 0.1
            final_schedule["cta"] += 0.1
        elif archetype_context.tone_params.enthusiasm_level == "low":
            final_schedule["hook"] -= 0.1
            final_schedule["cta"] -= 0.1
        
        if archetype_context.tone_params.formality_level == "formal":
            final_schedule["subject"] -= 0.1
            final_schedule["signature"] -= 0.1
        elif archetype_context.tone_params.formality_level == "casual":
            final_schedule["hook"] += 0.1
            final_schedule["signature"] += 0.1
        
        return final_schedule
    
    def _determine_constraints(
        self, 
        content: MessageContent, 
        archetype_context: ArchetypeContext
    ) -> Dict[str, Any]:
        """Determine generation constraints based on content and archetype."""
        constraints = {}
        
        # Base constraints from archetype
        archetype_constraints = self._constraint_mappings.get(
            archetype_context.archetype, 
            []
        )
        
        # Content-specific constraints
        if content.constraints:
            archetype_constraints.extend(content.constraints)
        
        # Length constraints
        constraints["max_lengths"] = {
            section: template["max_length"]
            for section, template in self._section_templates.items()
        }
        
        # Style constraints
        constraints["style_requirements"] = {
            section: template["style_guidelines"]
            for section, template in self._section_templates.items()
        }
        
        # Content constraints
        constraints["content_requirements"] = archetype_constraints
        
        # Tone constraints
        constraints["tone_constraints"] = {
            "formality_level": archetype_context.tone_params.formality_level,
            "enthusiasm_level": archetype_context.tone_params.enthusiasm_level,
            "personalization_level": archetype_context.tone_params.personalization_level
        }
        
        # CTA constraints
        constraints["cta_constraints"] = {
            "type": archetype_context.cta_params.cta_type,
            "urgency_level": archetype_context.cta_params.urgency_level,
            "friction_reduction": archetype_context.cta_params.friction_reduction
        }
        
        return constraints
    
    def _estimate_tokens(self, sections: Dict[str, str]) -> int:
        """Estimate token count for planned message."""
        total_chars = sum(len(content) for content in sections.values())
        # Rough estimation: ~4 characters per token
        return int(total_chars / 4)
    
    def _determine_generation_strategy(self, archetype_context: ArchetypeContext) -> str:
        """Determine optimal generation strategy based on archetype."""
        if archetype_context.archetype == "technical_leader":
            return "sequential_with_validation"
        elif archetype_context.archetype == "business_executive":
            return "concise_priority"
        elif archetype_context.archetype == "hiring_manager":
            return "balanced_approach"
        else:
            return "sequential"
    
    def _calculate_complexity_score(
        self, 
        sections: Dict[str, str], 
        constraints: Dict[str, Any]
    ) -> float:
        """Calculate complexity score for the message plan."""
        # Base complexity from section count
        section_complexity = len(sections) * 0.2
        
        # Constraint complexity
        constraint_count = sum(len(constraints.get(key, [])) for key in ["content_requirements", "style_requirements"])
        constraint_complexity = min(constraint_count * 0.1, 0.5)
        
        # Content complexity
        content_complexity = sum(len(content) for content in sections.values()) / 1000.0
        content_complexity = min(content_complexity, 0.3)
        
        return min(section_complexity + constraint_complexity + content_complexity, 1.0)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for planning metadata."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def analyze_message_plan(
        self, 
        plan: MessagePlan, 
        archetype_context: ArchetypeContext
    ) -> Dict[str, Any]:
        """
        Analyze created message plan for optimization opportunities.
        """
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "optimization_suggestions": [],
            "quality_score": 0.0
        }
        
        # Analyze temperature schedule
        temp_variance = max(plan.temperature_schedule.values()) - min(plan.temperature_schedule.values())
        if temp_variance > 0.3:
            analysis["strengths"].append("Good temperature variation for creative control")
        elif temp_variance < 0.1:
            analysis["weaknesses"].append("Limited temperature variation may reduce creativity")
        
        # Analyze constraints
        constraint_count = 0
        for key, value in plan.constraints.items():
            if isinstance(value, list):
                constraint_count += len(value)
        
        if constraint_count > 10:
            analysis["weaknesses"].append("High constraint count may limit generation flexibility")
            analysis["optimization_suggestions"].append("Consider relaxing non-critical constraints")
        elif constraint_count < 3:
            analysis["optimization_suggestions"].append("Consider adding more specific guidance constraints")
        
        # Analyze token estimation
        if plan.estimated_tokens > 300:
            analysis["optimization_suggestions"].append("Consider more concise messaging for better engagement")
        elif plan.estimated_tokens < 100:
            analysis["weaknesses"].append("Message may be too brief to convey value effectively")
        
        # Calculate quality score
        quality_factors = [
            min(temp_variance / 0.3, 1.0) * 0.3,  # Temperature variation
            min(constraint_count / 8.0, 1.0) * 0.2,  # Appropriate constraint count
            min(plan.estimated_tokens / 200.0, 1.0) * 0.3,  # Appropriate length
            0.2  # Base score for having all required sections
        ]
        analysis["quality_score"] = sum(quality_factors)
        
        return analysis
