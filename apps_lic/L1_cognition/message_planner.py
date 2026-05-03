"""Message Planner - L1 planning for comprehensive message structure and content.

Incorporated from L1 message_planning.py to provide archetype-specific message
structure planning with section templates, temperature adjustments, and
constraint management for maximizing executive reply rates.

This is a foundational L1 planning component that integrates with other L1
planners and feeds into the hop-based K3 draft execution phase.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class MessageSection:
    """Individual message section with planning parameters."""
    section_type: str                    # "subject", "hook", "value", "cta", "signature"
    max_length: int
    required_elements: List[str]
    optional_elements: List[str]
    style_guidelines: List[str]
    temperature_adjustment: float = 0.0
    content_strategy: str = "standard"
    word_count_target: Optional[int] = None
    metadata: Dict[str, object] = field(default_factory=dict)

@dataclass
class MessagePlan:
    """Complete message structure plan with archetype-specific parameters."""
    archetype: str
    sections: Dict[str, MessageSection]
    temperature_schedule: Dict[str, float]
    constraints: List[str]
    priority_order: List[str]
    total_target_length: int
    confidence_score: float = 0.0
    metadata: Dict[str, object] = field(default_factory=dict)

@dataclass
class MessageContent:
    """Content signals that drive high-impact messaging strategies."""
    recipient_name: str
    recipient_title: str
    company_name: str
    value_proposition: str
    key_points: List[str]
    personalization_elements: List[str]
    constraints: List[str]
    metadata: Dict[str, object] = field(default_factory=dict)

class MessagePlanner:
    """Structures messages with archetype-specific parameters to increase reply probability.

    Generates deterministic message plans using section templates, temperature
    adjustments, and archetype-specific constraints.
    """

    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize message planner with archetype-specific templates."""
        self.telemetry_bus = telemetry_bus

        self.temperature_adjustments = {
            "RECRUITER": {
                "subject": -0.1,  # More formal
                "hook": 0.0,       # Standard
                "value": -0.1,     # Concise
                "cta": 0.0,        # Standard
                "signature": 0.0   # Standard
            },
            "SENIOR_TA": {
                "subject": 0.0,   # Standard
                "hook": 0.1,      # More engaging
                "value": 0.0,     # Standard
                "cta": -0.1,      # More formal
                "signature": 0.0  # Standard
            },
            "executive": {
                "subject": -0.1,  # More formal
                "hook": 0.0,      # Strategic
                "value": 0.0,     # Business-focused
                "cta": 0.1,       # More action-oriented
                "signature": 0.1  # Warmer
            },
            "C_LEVEL": {
                "subject": -0.2,  # Very formal
                "hook": -0.1,     # Strategic
                "value": -0.1,    # Concise
                "cta": -0.1,      # Professional
                "signature": -0.1 # Formal
            }
        }

        # Archetype-specific constraints
        self.constraint_mappings = {
            "RECRUITER": [
                "brevity_required",
                "no_unverified_claims",
                "job_fit_focus",
                "tone_professional_and_short"
            ],
            "SENIOR_TA": [
                "role_alignment_required",
                "avoid_strategic_language",
                "must_include_company_specificity"
            ],
            "executive": [
                "business_impact_required",
                "team_outcomes_required",
                "no_buzzwords",
                "specific_metrics_required"
            ],
            "C_LEVEL": [
                "strategic_alignment_required",
                "quantifiable_outcomes_required",
                "no_filler_language",
                "high_signal_density_required"
            ]
        }

        # Section templates
        self.section_templates = self._build_section_templates()

        # Section priority order
        self.default_priority = ["subject", "hook", "value", "cta", "signature"]

    def _build_section_templates(self) -> Dict[str, Dict[str, object]]:
        """Build section templates for message planning."""
        return {
            "subject": {
                "max_length": 60,
                "required_elements": ["value_proposition"],
                "optional_elements": ["personalization", "urgency"],
                "style_guidelines": ["concise", "action_oriented"],
                "word_count_target": 10
            },
            "hook": {
                "max_length": 150,
                "required_elements": ["context", "relevance"],
                "optional_elements": ["personalization", "achievement"],
                "style_guidelines": ["engaging", "specific"],
                "word_count_target": 25
            },
            "value": {
                "max_length": 500,
                "required_elements": ["value_proposition", "evidence"],
                "optional_elements": ["business_impact", "technical_details", "company_info"],
                "style_guidelines": ["structured", "persuasive"],
                "word_count_target": 80
            },
            "cta": {
                "max_length": 100,
                "required_elements": ["action", "contact_info"],
                "optional_elements": ["urgency", "value_reinforcement"],
                "style_guidelines": ["clear", "actionable"],
                "word_count_target": 15
            },
            "signature": {
                "max_length": 50,
                "required_elements": ["name", "title"],
                "optional_elements": ["company", "contact"],
                "style_guidelines": ["professional", "consistent"],
                "word_count_target": 8
            }
        }

    def plan(
        self,
        *,
        content: MessageContent,
        archetype: str,
        persona_plan: Optional[Any] = None,
        grounding_plan: Optional[Any] = None,
        fusion_plan: Optional[Any] = None,
        outreach_context: Dict[str, object] = None,
    ) -> MessagePlan:
        """Generate a comprehensive message structure plan.

        Args:
            content: Message content signals and requirements
            archetype: Target archetype for message optimization
            persona_plan: Optional persona planning results
            grounding_plan: Optional grounding analysis results
            fusion_plan: Optional fusion planning results
            outreach_context: Additional context for planning

        Returns:
            Complete message plan with sections, constraints, and parameters
        """
        outreach_context = outreach_context or {}

        # 1. Plan sections with archetype-specific content
        sections = self._plan_sections(content,
            archetype,
            persona_plan,
            grounding_plan,
            fusion_plan)

        # 2. Calculate temperature schedule for archetype
        temperature_schedule = self._calculate_temperature_schedule(archetype)

        # 3. Determine archetype-specific constraints
        constraints = self._determine_constraints(content, archetype, grounding_plan)

        # 4. Set section priority order
        priority_order = self._determine_priority_order(archetype, outreach_context)

        # 5. Calculate total target length
        total_target_length = sum(section.max_length for section in sections.values())

        # 6. Calculate confidence score
        confidence_score = self._calculate_confidence_score(sections, content, archetype)

        # 7. Build metadata
        metadata = {
            "archetype": archetype,
            "section_count": len(sections),
            "constraint_count": len(constraints),
            "total_target_length": total_target_length,
            "persona_integration": persona_plan is not None,
            "grounding_integration": grounding_plan is not None,
            "fusion_integration": fusion_plan is not None
        }

        # 8. Create message plan
        plan = MessagePlan(
            archetype=archetype,
            sections=sections,
            temperature_schedule=temperature_schedule,
            constraints=constraints,
            priority_order=priority_order,
            total_target_length=total_target_length,
            confidence_score=confidence_score,
            metadata=metadata,
        )

        # 9. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)

        return plan

    def _plan_sections(
        self,
        content: MessageContent,
        archetype: str,
        persona_plan: Optional[Any] = None,
        grounding_plan: Optional[Any] = None,
        fusion_plan: Optional[Any] = None
    ) -> Dict[str, MessageSection]:
        """Plan individual message sections with archetype-specific parameters."""
        sections = {}

        for section_name, template in self.section_templates.items():
            # Create base section from template
            section = MessageSection(
                section_type=section_name,
                max_length=template["max_length"],
                required_elements=template["required_elements"],
                optional_elements=template["optional_elements"],
                style_guidelines=template["style_guidelines"],
                word_count_target=template["word_count_target"],
                temperature_adjustment=self.temperature_adjustments.get(archetype,
                    {}).get(section_name,
                    0.0)
            )

            # Apply persona-based refinements
            if persona_plan:
                section = self._apply_persona_refinements(section, persona_plan, archetype)

            # Apply grounding-based constraints
            if grounding_plan:
                section = self._apply_grounding_constraints(section, grounding_plan)

            # Apply fusion-based content strategy
            if fusion_plan:
                section = self._apply_fusion_strategy(section, fusion_plan, section_name)

            # Apply archetype-specific content strategy
            section.content_strategy = self._determine_content_strategy(section_name, archetype)

            sections[section_name] = section

        return sections

    def _apply_persona_refinements(self,
        section: MessageSection,
        persona_plan: object,
        archetype: str) -> MessageSection:
        """Apply persona-based refinements to section."""
        # Adjust based on persona parameters
        if hasattr(persona_plan, 'detail_level'):
            if persona_plan.detail_level == "high" and section.section_type == "value":
                section.max_length = int(section.max_length * 1.2)  # Allow more detail
                section.word_count_target = int(section.word_count_target * 1.2)
            elif persona_plan.detail_level == "low" and section.section_type in ["hook", "value"]:
                section.max_length = int(section.max_length * 0.8)  # Be more concise
                section.word_count_target = int(section.word_count_target * 0.8)

        if hasattr(persona_plan, 'communication_style'):
            if persona_plan.communication_style == "formal" and section.section_type == "subject":
                section.style_guidelines.append("formal_tone")
            elif persona_plan.communication_style == "technical" and section.section_type == "value":
                section.optional_elements.append("technical_details")

        return section

    def _apply_grounding_constraints(self,
        section: MessageSection,
        grounding_plan: object) -> MessageSection:
        """Apply grounding-based constraints to section."""
        if hasattr(grounding_plan, 'risk_flags') and grounding_plan.risk_flags:
            # Add constraint to avoid risky claims
            if "overclaim" in grounding_plan.risk_flags:
                section.constraints = getattr(section, 'constraints', [])
                section.constraints.append("avoid_unverified_claims")
                section.style_guidelines.append("conservative_language")

        if hasattr(grounding_plan, 'confidence_score') and grounding_plan.confidence_score < 0.5:
            # Lower confidence = more conservative approach
            if section.section_type == "value":
                section.style_guidelines.append("evidence_based")
                section.required_elements.append("verification_source")

        return section

    def _apply_fusion_strategy(self,
        section: MessageSection,
        fusion_plan: object,
        section_name: str) -> MessageSection:
        """Apply fusion-based content strategy to section."""
        if hasattr(fusion_plan, 'sections'):
            # Find corresponding fusion section
            fusion_section = next(
                (s for s in fusion_plan.sections if s.section_type == section_name),
                None,
            )
            if fusion_section:
                section.metadata["fusion_guidance"] = fusion_section.tone_guidance
                section.metadata["fusion_value_props"] = fusion_section.value_proposition_ids

                # Adjust based on fusion guidance
                if "concise" in fusion_section.tone_guidance:
                    section.max_length = int(section.max_length * 0.9)
                elif "detailed" in fusion_section.tone_guidance:
                    section.max_length = int(section.max_length * 1.1)

        return section

    def _determine_content_strategy(self, section_name: str, archetype: str) -> str:
        """Determine content strategy for section based on archetype."""
        strategies = {
            "RECRUITER": {
                "subject": "job_focus",
                "hook": "opportunity_highlight",
                "value": "skill_alignment",
                "cta": "discussion_invite",
                "signature": "professional"
            },
            "SENIOR_TA": {
                "subject": "technical_value",
                "hook": "problem_solution",
                "value": "technical_depth",
                "cta": "technical_discussion",
                "signature": "technical_authority"
            },
            "executive": {
                "subject": "business_impact",
                "hook": "strategic_relevance",
                "value": "business_outcomes",
                "cta": "strategic_discussion",
                "signature": "executive_presence"
            },
            "C_LEVEL": {
                "subject": "strategic_imperative",
                "hook": "executive_priority",
                "value": "quantifiable_impact",
                "cta": "executive_action",
                "signature": "c_level_authority"
            }
        }

        return strategies.get(archetype, {}).get(section_name, "standard")

    def _calculate_temperature_schedule(self, archetype: str) -> Dict[str, float]:
        """Calculate temperature schedule for archetype."""
        base_schedule = {
            "subject": 0.7,
            "hook": 0.8,
            "value": 0.6,
            "cta": 0.7,
            "signature": 0.5
        }

        # Apply archetype adjustments
        adjustments = self.temperature_adjustments.get(archetype, {})
        schedule = {}

        for section, base_temp in base_schedule.items():
            adjustment = adjustments.get(section, 0.0)
            schedule[section] = max(0.1, min(1.0, base_temp + adjustment))

        return schedule

    def _determine_constraints(self,
        content: MessageContent,
        archetype: str,
        grounding_plan: Optional[Any] = None) -> List[str]:
        """Determine archetype-specific constraints."""
        base_constraints = self.constraint_mappings.get(archetype, []).copy()

        # Add content-specific constraints
        if content.constraints:
            base_constraints.extend(content.constraints)

        # Add grounding-based constraints
        if grounding_plan and hasattr(grounding_plan, 'risk_flags'):
            if grounding_plan.risk_flags:
                base_constraints.append("risk_aware_language")

        # Remove duplicates while preserving order
        seen = set()
        unique_constraints = []
        for constraint in base_constraints:
            if constraint not in seen:
                seen.add(constraint)
                unique_constraints.append(constraint)

        return unique_constraints

    def _determine_priority_order(self, archetype: str, context: Dict[str, object]) -> List[str]:
        """Determine section priority order based on archetype and context."""
        base_order = self.default_priority.copy()

        # Adjust based on archetype
        if archetype == "C_LEVEL":
            # Move value proposition earlier for C-level
            if "value" in base_order:
                base_order.remove("value")
                base_order.insert(2, "value")  # After hook
        elif archetype == "RECRUITER":
            # Move cta earlier for recruiters
            if "cta" in base_order:
                base_order.remove("cta")
                base_order.insert(3, "cta")  # After value

        # Apply context overrides
        if context.get("priority_override"):
            base_order = context["priority_override"]

        return base_order

    def _calculate_confidence_score(self,
        sections: Dict[str,
        MessageSection],
        content: MessageContent,
        archetype: str) -> float:
        """Calculate overall confidence score for message plan."""
        base_score = 0.7

        # Boost for complete content
        if content.value_proposition and content.key_points:
            base_score += 0.1

        # Boost for archetype match
        if archetype in ["executive", "C_LEVEL", "SENIOR_TA", "RECRUITER"]:
            base_score += 0.1

        # Adjust based on section completeness
        complete_sections = sum(1 for s in sections.values() if s.required_elements)
        base_score += (complete_sections / len(sections)) * 0.1

        return round(min(base_score, 1.0), 3)

    def _safe_record_telemetry(self, plan: MessagePlan) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("message_plan_created", {
                    "archetype": plan.archetype,
                    "section_count": len(plan.sections),
                    "constraint_count": len(plan.constraints),
                    "confidence_score": plan.confidence_score
                })
        except Exception as e:  # guardian: allow-broad-exception -- telemetry emission must not break planner flow; logger.debug records failure
            logger.debug(f"Failed to record telemetry: {e}")

    def get_message_summary(self, plan: MessagePlan) -> Dict[str, object]:
        """Get a summary of the message plan for debugging/telemetry."""
        return {
            "plan_id": f"message_{plan.archetype}_{plan.confidence_score:.2f}",
            "archetype": plan.archetype,
            "section_count": len(plan.sections),
            "constraint_count": len(plan.constraints),
            "total_target_length": plan.total_target_length,
            "confidence_score": plan.confidence_score,
            "priority_order": plan.priority_order,
            "content_strategies": [s.content_strategy for s in plan.sections.values()],
            "temperature_range": {
                "min": min(plan.temperature_schedule.values()),
                "max": max(plan.temperature_schedule.values())
            }
        }

    def validate_message_plan(self, plan: MessagePlan) -> List[str]:
        """Validate message plan and return warnings."""
        warnings = []

        # Check for missing required sections
        required_sections = ["subject", "hook", "value", "cta", "signature"]
        missing_sections = [s for s in required_sections if s not in plan.sections]
        if missing_sections:
            warnings.append(f"Missing required sections: {missing_sections}")

        # Check for temperature extremes
        for section, temp in plan.temperature_schedule.items():
            if temp < 0.2:
                warnings.append(f"Very low temperature for {section}: {temp}")
            elif temp > 0.9:
                warnings.append(f"Very high temperature for {section}: {temp}")

        # Check for constraint conflicts
        if "brevity_required" in plan.constraints and plan.total_target_length > 800:
            warnings.append("Brevity constraint conflicts with large target length")

        return warnings
