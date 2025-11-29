"""K3 Draft Executor - Third hop in the sequential K1-K7 execution pipeline.

Incorporated from L2 lic_k3_draft.py to create comprehensive message drafts
by integrating all L1 planners (fusion, grounding, persona, profile, research, message)
with K2 insights for archetype-optimized message generation.

This is the third execution phase in the hop-based architecture that follows:
L1 Planning → K1 Research → K2 Insights → K3 Draft → K4 Regeneration → K5 Validation → K6 CTA → K7 Assembly
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class DraftSection:
    """Individual message section with generation metadata."""
    section_type: str                    # "subject", "greeting", "hook", "value", "cta", "signature"
    content: str
    word_count: int
    tone_applied: str
    temperature_used: float
    sources_used: List[str]
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DraftOutput:
    """Output from K3 draft execution phase."""
    greeting: str
    subject_line: Optional[str]
    message_body: str
    cta_draft: str
    signature: str
    sections: Dict[str, DraftSection]
    word_count: int
    archetype_applied: str
    fusion_plan_used: bool
    persona_plan_used: bool
    grounding_plan_used: bool
    message_plan_used: bool
    confidence_score: float
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


class K3DraftExecutor:
    """K3 draft executor - third hop in sequential execution pipeline.
    
    Creates comprehensive message drafts by integrating all L1 planners
    with K2 insights for archetype-optimized message generation.
    """
    
    def __init__(self, 
                 template_plan: Optional[Dict[str, Any]] = None,
                 tone_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K3 draft executor."""
        self.template_plan = template_plan or {}
        self.tone_plan = tone_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Section generation templates
        self.section_templates = {
            "greeting": {
                "formal": ["Dear {name},", "Hello {name},"],
                "professional": ["Hi {name},"],
                "casual": ["Hey {name},"]
            },
            "subject": {
                "executive": ["Strategic discussion about {company}", "Value alignment opportunities at {company}"],
                "technical": ["Technical synergies in {role} role", "Innovation opportunities at {company}"],
                "recruiter": ["Opportunity discussion", "Exploring potential fit"]
            },
            "signature": {
                "formal": ["Best regards,", "Sincerely,"],
                "professional": ["Regards,", "Best,"],
                "casual": ["Thanks,", "Cheers,"]
            }
        }
        
        # Tone adaptation rules
        self.tone_adaptations = {
            "C_LEVEL": {
                "formality": "high",
                "conciseness": "high",
                "focus": "strategic",
                "language": "professional"
            },
            "EXECUTIVE": {
                "formality": "high",
                "conciseness": "medium",
                "focus": "business_impact",
                "language": "professional"
            },
            "SENIOR_TA": {
                "formality": "medium",
                "conciseness": "low",
                "focus": "technical",
                "language": "technical"
            },
            "RECRUITER": {
                "formality": "medium",
                "conciseness": "high",
                "focus": "opportunity",
                "language": "professional"
            }
        }
    
    def execute(
        self,
        *,
        fusion_plan: Optional[Any] = None,
        persona_plan: Optional[Any] = None,
        grounding_plan: Optional[Any] = None,
        profile_plan: Optional[Any] = None,
        research_plan: Optional[Any] = None,
        message_plan: Optional[Any] = None,
        insights_output: Optional[Any] = None,
        recipient_profile: Dict[str, Any],
        outreach_context: Dict[str, Any] = None,
    ) -> DraftOutput:
        """Execute K3 draft phase.
        
        Args:
            fusion_plan: Output from L1 fusion planner
            persona_plan: Output from L1 persona planner
            grounding_plan: Output from L1 grounding planner
            profile_plan: Output from L1 profile planner
            research_plan: Output from L1 research planner
            message_plan: Output from L1 message planner
            insights_output: Output from K2 insights executor
            recipient_profile: Target recipient profile data
            outreach_context: Additional context for drafting
            
        Returns:
            Complete message draft with sections and metadata
        """
        outreach_context = outreach_context or {}
        
        # 1. Determine archetype from profile or context
        archetype = self._determine_archetype(profile_plan, recipient_profile, outreach_context)
        
        # 2. Generate individual sections
        sections = self._generate_sections(
            archetype=archetype,
            fusion_plan=fusion_plan,
            persona_plan=persona_plan,
            grounding_plan=grounding_plan,
            message_plan=message_plan,
            insights_output=insights_output,
            recipient_profile=recipient_profile,
            outreach_context=outreach_context
        )
        
        # 3. Assemble complete message
        greeting = sections.get("greeting", DraftSection("", "", "", "", 0.0, [], 0.0)).content
        subject_line = sections.get("subject", DraftSection("", "", "", "", 0.0, [], 0.0)).content
        message_body = self._assemble_message_body(sections)
        cta_draft = sections.get("cta", DraftSection("", "", "", "", 0.0, [], 0.0)).content
        signature = sections.get("signature", DraftSection("", "", "", "", 0.0, [], 0.0)).content
        
        # 4. Calculate metrics
        word_count = sum(section.word_count for section in sections.values())
        confidence_score = self._calculate_draft_confidence(sections, insights_output)
        
        # 5. Build execution metadata
        execution_metadata = {
            "sections_generated": len(sections),
            "archetype": archetype,
            "fusion_plan_used": fusion_plan is not None,
            "persona_plan_used": persona_plan is not None,
            "grounding_plan_used": grounding_plan is not None,
            "message_plan_used": message_plan is not None,
            "insights_used": insights_output is not None,
            "total_word_count": word_count
        }
        
        # 6. Create draft output
        output = DraftOutput(
            greeting=greeting,
            subject_line=subject_line if subject_line else None,
            message_body=message_body,
            cta_draft=cta_draft,
            signature=signature,
            sections=sections,
            word_count=word_count,
            archetype_applied=archetype,
            fusion_plan_used=fusion_plan is not None,
            persona_plan_used=persona_plan is not None,
            grounding_plan_used=grounding_plan is not None,
            message_plan_used=message_plan is not None,
            confidence_score=confidence_score,
            execution_metadata=execution_metadata
        )
        
        # 7. Record telemetry (best-effort)
        self._safe_record_telemetry(output)
        
        return output
    
    def _determine_archetype(self, profile_plan: Optional[Any], recipient_profile: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Determine target archetype from available data."""
        # Priority: profile_plan > recipient_profile > context > default
        if profile_plan and hasattr(profile_plan, 'inferred_archetype'):
            return profile_plan.inferred_archetype
        elif recipient_profile.get("archetype"):
            return recipient_profile["archetype"]
        elif context.get("archetype"):
            return context["archetype"]
        else:
            return "OTHER"  # Default fallback
    
    def _generate_sections(
        self,
        archetype: str,
        fusion_plan: Optional[Any],
        persona_plan: Optional[Any],
        grounding_plan: Optional[Any],
        message_plan: Optional[Any],
        insights_output: Optional[Any],
        recipient_profile: Dict[str, Any],
        outreach_context: Dict[str, Any]
    ) -> Dict[str, DraftSection]:
        """Generate all message sections using integrated L1 plans."""
        sections = {}
        
        # Generate greeting
        sections["greeting"] = self._generate_greeting(recipient_profile, persona_plan, archetype)
        
        # Generate subject (if applicable)
        subject_section = self._generate_subject_line(recipient_profile, message_plan, archetype, outreach_context)
        if subject_section:
            sections["subject"] = subject_section
        
        # Generate hook
        sections["hook"] = self._generate_hook_section(fusion_plan, insights_output, message_plan, archetype)
        
        # Generate value proposition
        sections["value"] = self._generate_value_section(fusion_plan, grounding_plan, insights_output, message_plan, archetype)
        
        # Generate CTA
        sections["cta"] = self._generate_cta_section(fusion_plan, message_plan, archetype)
        
        # Generate signature
        sections["signature"] = self._generate_signature_section(persona_plan, archetype)
        
        return sections
    
    def _generate_greeting(self, recipient_profile: Dict[str, Any], persona_plan: Optional[Any], archetype: str) -> DraftSection:
        """Generate greeting section."""
        name = recipient_profile.get("first_name") or recipient_profile.get("name", "")
        
        # Determine formality level
        if persona_plan and hasattr(persona_plan, 'communication_style'):
            formality = persona_plan.communication_style
        else:
            formality = self.tone_adaptations.get(archetype, {}).get("formality", "professional")
        
        # Select appropriate template
        templates = self.section_templates["greeting"].get(formality, self.section_templates["greeting"]["professional"])
        greeting = templates[0].format(name=name)
        
        return DraftSection(
            section_type="greeting",
            content=greeting,
            word_count=len(greeting.split()),
            tone_applied=formality,
            temperature_used=0.5,
            sources_used=[],
            confidence_score=0.9,
            metadata={"formality": formality}
        )
    
    def _generate_subject_line(self, recipient_profile: Dict[str, Any], message_plan: Optional[Any], archetype: str, context: Dict[str, Any]) -> Optional[DraftSection]:
        """Generate subject line if needed."""
        message_type = context.get("message_type", "")
        if message_type not in ["INMAIL", "LONG_NEW"]:
            return None
        
        title = recipient_profile.get("title", "")
        company = recipient_profile.get("company", "")
        
        # Use message plan if available
        if message_plan and hasattr(message_plan, 'sections') and "subject" in message_plan.sections:
            subject_section_plan = message_plan.sections["subject"]
            templates = [
                f"Strategic discussion about {company}",
                f"Exploring synergies in {title} role",
                f"Value alignment opportunities",
                f"Growth initiatives at {company}"
            ]
        else:
            # Use archetype-specific templates
            focus = self.tone_adaptations.get(archetype, {}).get("focus", "professional")
            templates = self.section_templates["subject"].get(focus, self.section_templates["subject"]["professional"])
        
        selected_template = templates[0]
        
        # Ensure subject isn't too long
        if len(selected_template.split()) > 10:
            words = selected_template.split()
            selected_template = " ".join(words[:10])
        
        return DraftSection(
            section_type="subject",
            content=selected_template,
            word_count=len(selected_template.split()),
            tone_applied="professional",
            temperature_used=0.6,
            sources_used=[],
            confidence_score=0.8,
            metadata={"template_used": True}
        )
    
    def _generate_hook_section(self, fusion_plan: Optional[Any], insights_output: Optional[Any], message_plan: Optional[Any], archetype: str) -> DraftSection:
        """Generate hook/opening section."""
        hook_content = []
        sources_used = []
        
        # Use fusion plan if available
        if fusion_plan and hasattr(fusion_plan, 'sections'):
            fusion_hook = next((s for s in fusion_plan.sections if s.section_type == "hook"), None)
            if fusion_hook:
                hook_content.append(fusion_hook.opening_template)
                sources_used.append("fusion_planner")
        
        # Add insights if available
        if insights_output and hasattr(insights_output, 'key_insights'):
            top_insights = insights_output.key_insights[:2]
            for insight in top_insights:
                hook_content.append(f"I noticed {insight.lower()}")
            sources_used.append("k2_insights")
        
        # Apply tone adaptation
        base_text = " ".join(hook_content) if hook_content else "I hope this message finds you well."
        adapted_text = self._apply_tone_adaptation(base_text, archetype, "hook")
        
        return DraftSection(
            section_type="hook",
            content=adapted_text,
            word_count=len(adapted_text.split()),
            tone_applied=archetype,
            temperature_used=0.8,
            sources_used=sources_used,
            confidence_score=0.7,
            metadata={"fusion_used": fusion_plan is not None, "insights_used": insights_output is not None}
        )
    
    def _generate_value_section(self, fusion_plan: Optional[Any], grounding_plan: Optional[Any], insights_output: Optional[Any], message_plan: Optional[Any], archetype: str) -> DraftSection:
        """Generate value proposition section."""
        value_content = []
        sources_used = []
        
        # Use fusion plan value propositions
        if fusion_plan and hasattr(fusion_plan, 'value_propositions'):
            for value_prop in fusion_plan.value_propositions[:3]:
                value_content.append(f"- {value_prop.description}")
            sources_used.append("fusion_planner")
        
        # Add grounded claims if available
        if grounding_plan and hasattr(grounding_plan, 'allowed_claims'):
            grounded_claims = grounding_plan.allowed_claims[:2]
            for claim in grounded_claims:
                value_content.append(f"- {claim.description}")
            sources_used.append("grounding_planner")
        
        # Add insights evidence
        if insights_output and hasattr(insights_output, 'validated_claims'):
            validated_claims = insights_output.validated_claims[:2]
            for claim in validated_claims:
                value_content.append(f"- {claim}")
            sources_used.append("k2_insights")
        
        # Apply archetype-specific formatting
        base_text = "\n".join(value_content) if value_content else "I would like to discuss potential opportunities for collaboration."
        adapted_text = self._apply_tone_adaptation(base_text, archetype, "value")
        
        return DraftSection(
            section_type="value",
            content=adapted_text,
            word_count=len(adapted_text.split()),
            tone_applied=archetype,
            temperature_used=0.7,
            sources_used=sources_used,
            confidence_score=0.8,
            metadata={
                "fusion_used": fusion_plan is not None,
                "grounding_used": grounding_plan is not None,
                "insights_used": insights_output is not None
            }
        )
    
    def _generate_cta_section(self, fusion_plan: Optional[Any], message_plan: Optional[Any], archetype: str) -> DraftSection:
        """Generate call-to-action section."""
        cta_content = []
        sources_used = []
        
        # Use fusion plan CTA if available
        if fusion_plan and hasattr(fusion_plan, 'cta_strategy'):
            cta_strategy = fusion_plan.cta_strategy
            if cta_strategy == "formal_discussion":
                cta_content.append("Would you be available for a brief discussion next week?")
            elif cta_strategy == "technical_exchange":
                cta_content.append("I'd be interested in exchanging thoughts on technical challenges.")
            else:
                cta_content.append("Would you be open to exploring potential synergies?")
            sources_used.append("fusion_planner")
        else:
            # Use archetype-specific CTA
            focus = self.tone_adaptations.get(archetype, {}).get("focus", "professional")
            if focus == "strategic":
                cta_content.append("Would you be available for a strategic discussion next week?")
            elif focus == "technical":
                cta_content.append("I'd be interested in discussing technical opportunities.")
            else:
                cta_content.append("Would you be open to a brief conversation about potential collaboration?")
        
        base_text = " ".join(cta_content)
        adapted_text = self._apply_tone_adaptation(base_text, archetype, "cta")
        
        return DraftSection(
            section_type="cta",
            content=adapted_text,
            word_count=len(adapted_text.split()),
            tone_applied=archetype,
            temperature_used=0.7,
            sources_used=sources_used,
            confidence_score=0.8,
            metadata={"fusion_used": fusion_plan is not None}
        )
    
    def _generate_signature_section(self, persona_plan: Optional[Any], archetype: str) -> DraftSection:
        """Generate signature section."""
        # Determine formality level
        if persona_plan and hasattr(persona_plan, 'communication_style'):
            formality = persona_plan.communication_style
        else:
            formality = self.tone_adaptations.get(archetype, {}).get("formality", "professional")
        
        # Select appropriate template
        templates = self.section_templates["signature"].get(formality, self.section_templates["signature"]["professional"])
        signature = templates[0]
        
        return DraftSection(
            section_type="signature",
            content=signature,
            word_count=len(signature.split()),
            tone_applied=formality,
            temperature_used=0.4,
            sources_used=[],
            confidence_score=0.9,
            metadata={"formality": formality}
        )
    
    def _apply_tone_adaptation(self, base_text: str, archetype: str, section_type: str) -> str:
        """Apply archetype-specific tone adaptation to text."""
        tone_rules = self.tone_adaptations.get(archetype, {})
        
        adapted_text = base_text
        
        # Apply formality adjustments
        formality = tone_rules.get("formality", "professional")
        if formality == "high" and section_type in ["hook", "value"]:
            # Make more formal
            adapted_text = adapted_text.replace("I'm", "I am")
            adapted_text = adapted_text.replace("you're", "you are")
        
        # Apply conciseness adjustments
        conciseness = tone_rules.get("conciseness", "medium")
        if conciseness == "high" and section_type == "value":
            # Make more concise
            sentences = adapted_text.split(". ")
            if len(sentences) > 3:
                adapted_text = ". ".join(sentences[:3]) + "."
        
        # Apply focus adjustments
        focus = tone_rules.get("focus", "professional")
        if focus == "strategic" and section_type == "value":
            # Add strategic language
            if "strategic" not in adapted_text.lower():
                adapted_text = adapted_text.replace("opportunities", "strategic opportunities")
        elif focus == "technical" and section_type == "value":
            # Add technical language
            if "technical" not in adapted_text.lower():
                adapted_text = adapted_text.replace("solutions", "technical solutions")
        
        return adapted_text
    
    def _assemble_message_body(self, sections: Dict[str, DraftSection]) -> str:
        """Assemble complete message body from sections."""
        body_parts = []
        
        # Order of sections in message body
        section_order = ["hook", "value", "cta"]
        
        for section_name in section_order:
            if section_name in sections:
                section = sections[section_name]
                if section.content.strip():
                    body_parts.append(section.content.strip())
        
        # Join with appropriate spacing
        message_body = "\n\n".join(body_parts)
        
        return message_body
    
    def _calculate_draft_confidence(self, sections: Dict[str, DraftSection], insights_output: Optional[Any]) -> float:
        """Calculate overall confidence score for the draft."""
        if not sections:
            return 0.0
        
        # Average section confidence
        section_confidence = sum(section.confidence_score for section in sections.values()) / len(sections)
        
        # Insights bonus
        insights_bonus = 0.1 if insights_output and hasattr(insights_output, 'aggregate_confidence') else 0.0
        
        # Section completeness bonus
        expected_sections = ["greeting", "hook", "value", "cta", "signature"]
        completeness = len([s for s in expected_sections if s in sections]) / len(expected_sections)
        completeness_bonus = completeness * 0.1
        
        total_confidence = section_confidence + insights_bonus + completeness_bonus
        return round(min(total_confidence, 1.0), 3)
    
    def _safe_record_telemetry(self, output: DraftOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("k3_draft_executed", {
                    "sections_generated": len(output.sections),
                    "word_count": output.word_count,
                    "archetype": output.archetype_applied,
                    "confidence_score": output.confidence_score,
                    "fusion_plan_used": output.fusion_plan_used,
                    "persona_plan_used": output.persona_plan_used
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_draft_summary(self, output: DraftOutput) -> Dict[str, Any]:
        """Get a summary of the draft execution for debugging/telemetry."""
        return {
            "execution_id": "k3_draft",
            "sections_generated": len(output.sections),
            "word_count": output.word_count,
            "archetype_applied": output.archetype_applied,
            "confidence_score": output.confidence_score,
            "has_subject": output.subject_line is not None,
            "l1_plans_used": {
                "fusion": output.fusion_plan_used,
                "persona": output.persona_plan_used,
                "grounding": output.grounding_plan_used,
                "message": output.message_plan_used
            },
            "section_word_counts": {
                name: section.word_count for name, section in output.sections.items()
            }
        }
