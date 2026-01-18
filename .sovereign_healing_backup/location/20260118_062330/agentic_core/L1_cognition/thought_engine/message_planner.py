from __future__ import annotations
"""Message Planner - L1 planning for comprehensive message structure and content.

Incorporated from L1 message_planning.py to provide Archetype-specific message
structure planning with section templates, temperature adjustments, and
constraint management for maximizing executive reply rates.

This is a foundational L1 planning component that integrates with other L1
planners and feeds into the hop-based K3 draft execution phase.
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)

@dataclass
class MessageSection:
    """Individual message section with planning parameters."""
    section_type: str
    max_length: int
    required_elements: List[str]
    optional_elements: List[str]
    style_guidelines: List[str]
    temperature_adjustment: float = 0.0
    content_strategy: str = 'standard'
    word_count_target: Optional[int] = None
    metadata: Dict[str, object] = field(default_factory=dict)

@dataclass
class MessagePlan:
    """Complete message structure plan with Archetype-specific parameters."""
    Archetype: str
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
    """Structures messages with Archetype-specific parameters to increase reply probability.

    Generates deterministic message plans using section templates, temperature
    adjustments, and Archetype-specific constraints.
    """

    def __init__(self, telemetry_bus: Optional[Any]=None) -> None:
        """Initialize message planner with Archetype-specific templates."""
        self.telemetry_bus = telemetry_bus
        self.temperature_adjustments = {'RECRUITER': {'subject': -0.1, 'hook': 0.0, 'value': -0.1, 'cta': 0.0, 'signature': 0.0}, 'SENIOR_TA': {'subject': 0.0, 'hook': 0.1, 'value': 0.0, 'cta': -0.1, 'signature': 0.0}, 'EXECUTIVE': {'subject': -0.1, 'hook': 0.0, 'value': 0.0, 'cta': 0.1, 'signature': 0.1}, 'C_LEVEL': {'subject': -0.2, 'hook': -0.1, 'value': -0.1, 'cta': -0.1, 'signature': -0.1}}
        self.constraint_mappings = {'RECRUITER': ['brevity_required', 'no_unverified_claims', 'job_fit_focus', 'tone_professional_and_short'], 'SENIOR_TA': ['role_alignment_required', 'avoid_strategic_language', 'must_include_company_specificity'], 'EXECUTIVE': ['business_impact_required', 'team_outcomes_required', 'no_buzzwords', 'specific_metrics_required'], 'C_LEVEL': ['strategic_alignment_required', 'quantifiable_outcomes_required', 'no_filler_language', 'high_signal_density_required']}
        self.section_templates = self._build_section_templates()
        self.default_priority = ['subject', 'hook', 'value', 'cta', 'signature']

    def _build_section_templates(self) -> Dict[str, Dict[str, object]]:
        """Build section templates for message planning."""
        return {'subject': {'max_length': 60, 'required_elements': ['value_proposition'], 'optional_elements': ['personalization', 'urgency'], 'style_guidelines': ['concise', 'action_oriented'], 'word_count_target': 10}, 'hook': {'max_length': 150, 'required_elements': ['context', 'relevance'], 'optional_elements': ['personalization', 'achievement'], 'style_guidelines': ['engaging', 'specific'], 'word_count_target': 25}, 'value': {'max_length': 500, 'required_elements': ['value_proposition', 'evidence'], 'optional_elements': ['business_impact', 'technical_details', 'company_info'], 'style_guidelines': ['structured', 'persuasive'], 'word_count_target': 80}, 'cta': {'max_length': 100, 'required_elements': ['action', 'contact_info'], 'optional_elements': ['urgency', 'value_reinforcement'], 'style_guidelines': ['clear', 'actionable'], 'word_count_target': 15}, 'signature': {'max_length': 50, 'required_elements': ['name', 'title'], 'optional_elements': ['company', 'contact'], 'style_guidelines': ['professional', 'consistent'], 'word_count_target': 8}}

    def plan(self, *, content: MessageContent, Archetype: str, PersonaPlan: Optional[Any]=None, grounding_plan: Optional[Any]=None, fusion_plan: Optional[Any]=None, outreach_context: Dict[str, object]=None) -> MessagePlan:
        """Generate a comprehensive message structure plan.
        Args:
            content: Message content signals and requirements
            Archetype: Target Archetype for message optimization
            PersonaPlan: Optional persona planning results
            grounding_plan: Optional grounding analysis results
            fusion_plan: Optional fusion planning results
            outreach_context: Additional context for planning

        Returns:
            Complete message plan with sections, constraints, and parameters
        """
        outreach_context: Any = outreach_context or {}
        sections: Any = self._plan_sections(content, Archetype, PersonaPlan, grounding_plan, fusion_plan)
        temperature_schedule: Any = self._calculate_temperature_schedule(Archetype)
        constraints: Any = self._determine_constraints(content, Archetype, grounding_plan)
        priority_order: Any = self._determine_priority_order(Archetype, outreach_context)
        total_target_length: Any = sum((section.max_length for section in sections.values()))
        confidence_score: Any = self._calculate_confidence_score(sections, content, Archetype)
        metadata: Any = {'Archetype': Archetype, 'section_count': len(sections), 'constraint_count': len(constraints), 'total_target_length': total_target_length, 'persona_integration': PersonaPlan is not None, 'grounding_integration': grounding_plan is not None, 'fusion_integration': fusion_plan is not None}
        plan: Any = MessagePlan(Archetype=Archetype, sections=sections, temperature_schedule=temperature_schedule, constraints=constraints, priority_order=priority_order, total_target_length=total_target_length, confidence_score=confidence_score, metadata=metadata)
        self._safe_record_telemetry(plan)
        return plan

    def _plan_sections(self, content: MessageContent, Archetype: str, PersonaPlan: Optional[Any]=None, grounding_plan: Optional[Any]=None, fusion_plan: Optional[Any]=None) -> Dict[str, MessageSection]:
        """Plan individual message sections with Archetype-specific parameters."""
        sections = {}
        for section_name, template in self.section_templates.items():
            section = MessageSection(section_type=section_name, max_length=template['max_length'], required_elements=template['required_elements'], optional_elements=template['optional_elements'], style_guidelines=template['style_guidelines'], word_count_target=template['word_count_target'], temperature_adjustment=self.temperature_adjustments.get(Archetype, {}).get(section_name, 0.0))
            if PersonaPlan:
                section = self._apply_persona_refinements(section, PersonaPlan, Archetype)
            if grounding_plan:
                section = self._apply_grounding_constraints(section, grounding_plan)
            if fusion_plan:
                section = self._apply_fusion_strategy(section, fusion_plan, section_name)
            section.content_strategy = self._determine_content_strategy(section_name, Archetype)
            sections[section_name] = section
        return sections

    def _apply_persona_refinements(self, section: MessageSection, PersonaPlan: object, Archetype: str) -> MessageSection:
        """Apply persona-based refinements to section."""
        if hasattr(PersonaPlan, 'detail_level'):
            if PersonaPlan.detail_level == 'high' and section.section_type == 'value':
                section.max_length = int(section.max_length * 1.2)
                section.word_count_target = int(section.word_count_target * 1.2)
            elif PersonaPlan.detail_level == 'low' and section.section_type in ['hook', 'value']:
                section.max_length = int(section.max_length * 0.8)
                section.word_count_target = int(section.word_count_target * 0.8)
        if hasattr(PersonaPlan, 'communication_style'):
            if PersonaPlan.communication_style == 'formal' and section.section_type == 'subject':
                section.style_guidelines.append('formal_tone')
            elif PersonaPlan.communication_style == 'technical' and section.section_type == 'value':
                section.optional_elements.append('technical_details')
        return section

    def _apply_grounding_constraints(self, section: MessageSection, grounding_plan: object) -> MessageSection:
        """Apply grounding-based constraints to section."""
        if hasattr(grounding_plan, 'risk_flags') and grounding_plan.risk_flags:
            if 'overclaim' in grounding_plan.risk_flags:
                section.metadata['constraints'] = getattr(section, 'metadata', {}).get('constraints', [])
                section.metadata['constraints'].append('avoid_unverified_claims')
                section.style_guidelines.append('conservative_language')
        if hasattr(grounding_plan, 'confidence_score') and grounding_plan.confidence_score < 0.5:
            if section.section_type == 'value':
                section.style_guidelines.append('evidence_based')
                section.required_elements.append('verification_source')
        return section

    def _apply_fusion_strategy(self, section: MessageSection, fusion_plan: object, section_name: str) -> MessageSection:
        """Apply fusion-based content strategy to section."""
        if hasattr(fusion_plan, 'sections'):
            fusion_section = next((s for s in fusion_plan.sections if s.section_type == section_name), None)
            if fusion_section:
                section.metadata['fusion_guidance'] = fusion_section.tone_guidance
                section.metadata['fusion_value_props'] = fusion_section.value_proposition_ids
                if 'concise' in fusion_section.tone_guidance:
                    section.max_length = int(section.max_length * 0.9)
                elif 'detailed' in fusion_section.tone_guidance:
                    section.max_length = int(section.max_length * 1.1)
        return section

    def _determine_content_strategy(self, section_name: str, Archetype: str) -> str:
        """Determine content strategy for section based on Archetype."""
        strategies = {'RECRUITER': {'subject': 'job_focus', 'hook': 'opportunity_highlight', 'value': 'skill_alignment', 'cta': 'discussion_invite', 'signature': 'professional'}, 'SENIOR_TA': {'subject': 'technical_value', 'hook': 'problem_solution', 'value': 'technical_depth', 'cta': 'technical_discussion', 'signature': 'technical_authority'}, 'EXECUTIVE': {'subject': 'business_impact', 'hook': 'strategic_relevance', 'value': 'business_outcomes', 'cta': 'strategic_discussion', 'signature': 'executive_presence'}, 'C_LEVEL': {'subject': 'strategic_imperative', 'hook': 'executive_priority', 'value': 'quantifiable_impact', 'cta': 'executive_action', 'signature': 'c_level_authority'}}
        return strategies.get(Archetype, {}).get(section_name, 'standard')

    def _calculate_temperature_schedule(self, Archetype: str) -> Dict[str, float]:
        """Calculate temperature schedule for Archetype."""
        base_schedule = {'subject': 0.7, 'hook': 0.8, 'value': 0.6, 'cta': 0.7, 'signature': 0.5}
        adjustments = self.temperature_adjustments.get(Archetype, {})
        schedule = {}
        for section_name, base_temp in base_schedule.items():
            adjustment = adjustments.get(section_name, 0.0)
            schedule[section_name] = max(0.1, min(1.0, base_temp + adjustment))
        return schedule

    def _determine_constraints(self, content: MessageContent, Archetype: str, grounding_plan: Optional[Any]=None) -> List[str]:
        """Determine Archetype-specific constraints."""
        base_constraints = self.constraint_mappings.get(Archetype, []).copy()
        if content.constraints:
            base_constraints.extend(content.constraints)
        if grounding_plan and hasattr(grounding_plan, 'risk_flags'):
            if grounding_plan.risk_flags:
                base_constraints.append('risk_aware_language')
        seen = set()
        unique_constraints = []
        for constraint in base_constraints:
            if constraint not in seen:
                seen.add(constraint)
                unique_constraints.append(constraint)
        return unique_constraints

    def _determine_priority_order(self, Archetype: str, context: Dict[str, object]) -> List[str]:
        """Determine section priority order based on Archetype and context."""
        base_order = self.default_priority.copy()
        if Archetype == 'C_LEVEL':
            if 'value' in base_order:
                base_order.remove('value')
                base_order.insert(2, 'value')
        elif Archetype == 'RECRUITER':
            if 'cta' in base_order:
                base_order.remove('cta')
                base_order.insert(3, 'cta')
        if context.get('priority_override'):
            base_order = context['priority_override']
        return base_order

    def _calculate_confidence_score(self, sections: Dict[str, MessageSection], content: MessageContent, Archetype: str) -> float:
        """Calculate overall confidence score for message plan."""
        base_score = 0.7
        if content.value_proposition and content.key_points:
            base_score += 0.1
        if Archetype in ['EXECUTIVE', 'C_LEVEL', 'SENIOR_TA', 'RECRUITER']:
            base_score += 0.1
        complete_sections = sum((1 for s in sections.values() if s.required_elements))
        base_score += complete_sections / len(sections) * 0.1
        return round(min(base_score, 1.0), 3)

    def _safe_record_telemetry(self, plan: MessagePlan) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record('message_plan_created', {'Archetype': plan.Archetype, 'section_count': len(plan.sections), 'constraint_count': len(plan.constraints), 'confidence_score': plan.confidence_score})
        except Exception as e:
            LOGGER.debug(f'Failed to record telemetry: {e}')

    def get_message_summary(self, plan: MessagePlan) -> Dict[str, object]:
        """Get a summary of the message plan for debugging/telemetry."""
        return {'plan_id': f'message_{plan.Archetype}_{plan.confidence_score:.2f}', 'Archetype': plan.Archetype, 'section_count': len(plan.sections), 'constraint_count': len(plan.constraints), 'total_target_length': plan.total_target_length, 'confidence_score': plan.confidence_score, 'priority_order': plan.priority_order, 'content_strategies': [s.content_strategy for s in plan.sections.values()], 'temperature_range': {'min': min(plan.temperature_schedule.values()), 'max': max(plan.temperature_schedule.values())}}

    def validate_message_plan(self, plan: MessagePlan) -> List[str]:
        """Validate message plan and return warnings."""
        warnings: Any = []
        required_sections: Any = ['subject', 'hook', 'value', 'cta', 'signature']
        missing_sections: Any = [s for s in required_sections if s not in plan.sections]
        if missing_sections:
            warnings.append(f'Missing required sections: {missing_sections}')
        for section, temp in plan.temperature_schedule.items():
            if temp < 0.2:
                warnings.append(f'Very low temperature for {section}: {temp}')
            elif temp > 0.9:
                warnings.append(f'Very high temperature for {section}: {temp}')
        if 'brevity_required' in plan.constraints and plan.total_target_length > 800:
            warnings.append('Brevity constraint conflicts with large target length')
        return warnings