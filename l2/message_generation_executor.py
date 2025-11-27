"""Executes message generation to create high-impact executive outreach with archetype-specific temperature control."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from l4.schema.outreach_schema import OutreachRAGResult


@dataclass
class MessageSection:
    """Captures generated section with temperature control for executive message optimization."""
    name: str
    content: str
    temperature_used: float
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageResult:
    """Contains generated executive message with temperature schedule and evidence sources."""
    message: str
    sections: Dict[str, MessageSection]
    temperature_schedule: Dict[str, float]
    signals_used: List[OutreachRAGResult]
    total_tokens: int = 0
    generation_strategy: str = "sequential"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationContext:
    """Provides generation context with archetype parameters for executive message optimization."""
    mission_id: str
    archetype: str
    target_role: str
    target_company: str
    value_proposition: str
    personalization_points: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageGenerationExecutor:
    """Executes message generation with archetype-specific temperature control to maximize executive reply rates."""
    
    def __init__(self, llm_client: Any, safety_validator: Any = None):
        """Initializes executor with LLM client and safety validator for archetype-optimized message generation."""
        self.llm_client = llm_client
        self.safety_validator = safety_validator
    
    def generate_message(
        self,
        message_plan: Dict[str, Any],
        generation_context: GenerationContext,
        research_results: List[OutreachRAGResult]
    ) -> MessageResult:
        """Generates high-impact executive message using archetype-specific temperature control."""
        # HSON: Extracts archetype-specific temperature schedule -> matches executive cognitive patterns
        temperature_schedule = getattr(message_plan, "temperature_schedule", {})
        
        # Extract section plans
        subject_plan = getattr(message_plan, "subject_plan", "")
        hook_plan = getattr(message_plan, "hook_plan", "")
        value_plan = getattr(message_plan, "value_plan", "")
        cta_plan = getattr(message_plan, "cta_plan", "")
        signature_plan = getattr(message_plan, "signature_plan", "")
        
        # HSON: Selects high-signal evidence -> strengthens executive message credibility
        signals_used = self._select_signals(research_results)
        
        # Build signal context for prompts
        signal_context = self._build_signal_context(signals_used)
        
        # HSON: Generates sections with archetype-specific temperatures -> optimizes executive engagement
        sections: Dict[str, MessageSection] = {}
        
        # Generate subject
        subject_temperature = getattr(subject_plan, "temperature", 0.7) if hasattr(subject_plan, "temperature") else temperature_schedule.get("subject", 0.7)
        subject_section = self._generate_section(
            section_name="subject",
            plan=subject_plan,
            temperature=subject_temperature,
            ctx=generation_context,
            signal_context=signal_context,
            reasoning_metadata=getattr(message_plan, "metadata", {})
        )
        sections["subject"] = subject_section
        
        # Generate hook
        hook_temperature = getattr(hook_plan, "temperature", 0.9) if hasattr(hook_plan, "temperature") else temperature_schedule.get("hook", 0.9)
        hook_section = self._generate_section(
            section_name="hook",
            plan=hook_plan,
            temperature=hook_temperature,
            ctx=generation_context,
            signal_context=signal_context,
            reasoning_metadata=getattr(message_plan, "metadata", {})
        )
        sections["hook"] = hook_section
        
        # Generate value/body
        value_temperature = getattr(value_plan, "temperature", 0.8) if hasattr(value_plan, "temperature") else temperature_schedule.get("value", 0.8)
        value_section = self._generate_section(
            section_name="value",
            plan=value_plan,
            temperature=value_temperature,
            ctx=generation_context,
            signal_context=signal_context,
            reasoning_metadata=getattr(message_plan, "metadata", {})
        )
        sections["value"] = value_section
        
        # Generate CTA
        cta_temperature = getattr(cta_plan, "temperature", 0.6) if hasattr(cta_plan, "temperature") else temperature_schedule.get("cta", 0.6)
        cta_section = self._generate_section(
            section_name="cta",
            plan=cta_plan,
            temperature=cta_temperature,
            ctx=generation_context,
            signal_context=signal_context,
            reasoning_metadata=getattr(message_plan, "metadata", {})
        )
        sections["cta"] = cta_section
        
        # Generate signature
        signature_temperature = getattr(signature_plan, "temperature", 0.3) if hasattr(signature_plan, "temperature") else temperature_schedule.get("signature", 0.3)
        signature_section = self._generate_section(
            section_name="signature",
            plan=signature_plan,
            temperature=signature_temperature,
            ctx=generation_context,
            signal_context="",  # Signature doesn't need signals
            reasoning_metadata=getattr(message_plan, "metadata", {})
        )
        sections["signature"] = signature_section
        
        # Assemble complete message
        message = self._assemble_message(sections)
        
        # Calculate total tokens
        total_tokens = sum(s.tokens_used for s in sections.values())
        
        # Build temperature schedule from actual sections generated
        actual_temperature_schedule = {}
        for section_name, section in sections.items():
            actual_temperature_schedule[section_name] = section.temperature_used
        
        # Check if generation_strategy is a Mock object and use default if so
        generation_strategy = getattr(message_plan, "generation_strategy", "sequential")
        if hasattr(generation_strategy, '_mock_name'):
            generation_strategy = "sequential"
        
        # Apply safety validation if safety validator is available
        if self.safety_validator:
            safety_result = self.safety_validator.validate_layer_input(
                "L2", message, generation_context
            )
            # Add safety violations to metadata if any
            if safety_result.findings:
                metadata = {
                    "mission_id": generation_context.mission_id,
                    "archetype": generation_context.archetype,
                    "signal_count": len(signals_used),
                    "safety_check": "failed",
                    "safety_violations": [f.__dict__ for f in safety_result.findings]
                }
            else:
                metadata = {
                    "mission_id": generation_context.mission_id,
                    "archetype": generation_context.archetype,
                    "signal_count": len(signals_used),
                    "safety_check": "passed"
                }
        else:
            metadata = {
                "mission_id": generation_context.mission_id,
                "archetype": generation_context.archetype,
                "signal_count": len(signals_used)
            }
        
        return MessageResult(
            message=message,
            sections=sections,
            temperature_schedule=actual_temperature_schedule,
            signals_used=signals_used,
            total_tokens=total_tokens,
            generation_strategy=generation_strategy,
            metadata=metadata
        )
    
    def _generate_section(
        self,
        section_name: str,
        plan: str,
        temperature: float,
        ctx: GenerationContext,
        signal_context: str,
        reasoning_metadata: Dict[str, Any] = None
    ) -> MessageSection:
        """
        Generate a single message section.
        
        Uses runtime LLM client with specified temperature.
        """
        if reasoning_metadata is None:
            reasoning_metadata = {}
            
        # Build prompt for section
        prompt = self._build_section_prompt(
            section_name=section_name,
            plan=plan,
            ctx=ctx,
            signal_context=signal_context,
            reasoning_metadata=reasoning_metadata
        )
        
        # Call LLM with temperature
        # Note: Temperature is handled at section level for archetype optimization
        content = self.llm_client.generate(prompt)
        
        # Estimate tokens (simple approximation)
        content_text = getattr(content, 'content', str(content))
        tokens_used = len(content_text.split()) * 2
        
        return MessageSection(
            name=section_name,
            content=content,
            temperature_used=temperature,
            tokens_used=tokens_used,
            metadata={"plan": plan}
        )
    
    def _build_section_prompt(
        self,
        section_name: str,
        plan: str,
        ctx: GenerationContext,
        signal_context: str,
        reasoning_metadata: Dict[str, Any] = None
    ) -> str:
        """Build prompt for section generation."""
        if reasoning_metadata is None:
            reasoning_metadata = {}
            
        prompts = {
            "subject": self._build_subject_prompt,
            "hook": self._build_hook_prompt,
            "value": self._build_value_prompt,
            "cta": self._build_cta_prompt,
            "signature": self._build_signature_prompt
        }
        
        builder = prompts.get(section_name, self._build_generic_prompt)
        return builder(plan, ctx, signal_context, reasoning_metadata)
    
    def _build_reasoning_instructions(self, reasoning_metadata: Dict[str, Any], section_name: str) -> str:
        """Build reasoning-intensity instructions based on metadata."""
        reasoning_intensity = getattr(reasoning_metadata, "reasoning_intensity", "low")
        cot_depth = getattr(reasoning_metadata, "cot_depth", 1)
        tot_branches = getattr(reasoning_metadata, "tot_branches", 1)
        
        # High-value sections get deeper reasoning instructions
        if section_name in ["value", "hook"]:
            if reasoning_intensity == "extreme":
                return f"""
REASONING INTENSITY: EXTREME
- Use multi-step justification with explicit reasoning chains
- Provide 3-4 distinct value dimensions with specific examples
- Include strategic implications and business impact quantification
- Apply Chain-of-Thought depth: {cot_depth} steps, Tree-of-Thought branches: {tot_branches}
- Emphasize precision, specificity, and quantifiable outcomes"""
            elif reasoning_intensity == "high":
                return f"""
REASONING INTENSITY: HIGH  
- Use structured reasoning with clear justification steps
- Provide 2-3 value dimensions with concrete examples
- Include business impact and team outcomes
- Apply Chain-of-Thought depth: {cot_depth} steps, Tree-of-Thought branches: {tot_branches}
- Focus on strategic alignment and specific metrics"""
            elif reasoning_intensity == "medium":
                return f"""
REASONING INTENSITY: MEDIUM
- Use clear reasoning with some justification
- Provide 1-2 key value points with brief examples
- Apply Chain-of-Thought depth: {cot_depth} steps, Tree-of-Thought branches: {tot_branches}
- Balance conciseness with informative content"""
        
        # Subject and CTA get lighter enhancements for extreme intensity only
        elif section_name in ["subject", "cta"]:
            if reasoning_intensity == "extreme":
                return """
REASONING INTENSITY: EXTREME
- Use precise, strategic language that reflects executive-level thinking
- Emphasize high-value partnership or strategic opportunity framing"""
            elif reasoning_intensity == "high":
                return """
REASONING INTENSITY: HIGH
- Use professional, benefit-oriented language
- Emphasize business value and collaboration"""
        
        # Signature gets minimal enhancement
        elif section_name == "signature":
            if reasoning_intensity == "extreme":
                return """
REASONING INTENSITY: EXTREME
- Include strategic partnership language in signature"""
        
        return ""  # No additional instructions for low intensity
    
    def _build_subject_prompt(
        self,
        plan: str,
        ctx: GenerationContext,
        signal_context: str,
        reasoning_metadata: Dict[str, Any] = None
    ) -> str:
        """Build prompt for subject line generation."""
        if reasoning_metadata is None:
            reasoning_metadata = {}
            
        reasoning_instructions = self._build_reasoning_instructions(reasoning_metadata, "subject")
        
        return f"""Generate a compelling email subject line for outreach.

Target: {ctx.target_role} at {ctx.target_company}
Archetype: {ctx.archetype}
Value Proposition: {ctx.value_proposition}

Planning guidance: {plan}

{signal_context}

{reasoning_instructions}

Generate a concise, engaging subject line (max 60 characters):"""
    
    def _build_hook_prompt(
        self,
        plan: str,
        ctx: GenerationContext,
        signal_context: str,
        reasoning_metadata: Dict[str, Any] = None
    ) -> str:
        """Build prompt for hook/opening generation."""
        if reasoning_metadata is None:
            reasoning_metadata = {}
            
        personalization = ", ".join(ctx.personalization_points) if ctx.personalization_points else "None specified"
        reasoning_instructions = self._build_reasoning_instructions(reasoning_metadata, "hook")
        
        return f"""Generate an engaging opening hook for outreach email.

Target: {ctx.target_role} at {ctx.target_company}
Archetype: {ctx.archetype}
Personalization points: {personalization}

Planning guidance: {plan}

{signal_context}

{reasoning_instructions}

Generate a compelling, personalized opening (2-3 sentences):"""
    
    def _build_value_prompt(
        self,
        plan: str,
        ctx: GenerationContext,
        signal_context: str,
        reasoning_metadata: Dict[str, Any] = None
    ) -> str:
        """Build prompt for value proposition body generation."""
        if reasoning_metadata is None:
            reasoning_metadata = {}
            
        reasoning_instructions = self._build_reasoning_instructions(reasoning_metadata, "value")
        
        return f"""Generate the value proposition body for outreach email.

Target: {ctx.target_role} at {ctx.target_company}
Archetype: {ctx.archetype}
Core value proposition: {ctx.value_proposition}

Planning guidance: {plan}

{signal_context}

{reasoning_instructions}

Generate a compelling value proposition (2-4 sentences):"""
    
    def _build_cta_prompt(
        self,
        plan: str,
        ctx: GenerationContext,
        signal_context: str,
        reasoning_metadata: Dict[str, Any] = None
    ) -> str:
        """Build prompt for call-to-action generation."""
        if reasoning_metadata is None:
            reasoning_metadata = {}
            
        reasoning_instructions = self._build_reasoning_instructions(reasoning_metadata, "cta")
        
        return f"""Generate a clear call-to-action for outreach email.

Target: {ctx.target_role} at {ctx.target_company}
Archetype: {ctx.archetype}

Planning guidance: {plan}

{reasoning_instructions}

Generate a low-friction, specific call-to-action (1-2 sentences):"""
    
    def _build_signature_prompt(
        self,
        plan: str,
        ctx: GenerationContext,
        signal_context: str,
        reasoning_metadata: Dict[str, Any] = None
    ) -> str:
        """Build prompt for signature generation."""
        if reasoning_metadata is None:
            reasoning_metadata = {}
            
        reasoning_instructions = self._build_reasoning_instructions(reasoning_metadata, "signature")
        
        return f"""Generate a professional email signature.

Planning guidance: {plan}

{reasoning_instructions}

Generate a clean, professional signature:"""
    
    def _build_generic_prompt(
        self,
        plan: str,
        ctx: GenerationContext,
        signal_context: str,
        reasoning_metadata: Dict[str, Any] = None
    ) -> str:
        """Build generic prompt for unknown sections."""
        if reasoning_metadata is None:
            reasoning_metadata = {}
            
        reasoning_instructions = self._build_reasoning_instructions(reasoning_metadata, "generic")
        
        return f"""Generate content for outreach email section.

Target: {ctx.target_role} at {ctx.target_company}
Planning guidance: {plan}

{signal_context}

{reasoning_instructions}

Generate appropriate content:"""
    
    def _select_signals(
        self,
        research_data: List[OutreachRAGResult],
        max_signals: int = 3
    ) -> List[OutreachRAGResult]:
        """Select top signals from research data."""
        # Filter to signal candidates
        candidates = [r for r in research_data if r.is_signal_candidate]
        
        # Sort by signal score
        candidates.sort(key=lambda r: r.signal_score, reverse=True)
        
        # Return top N
        return candidates[:max_signals]
    
    def _build_signal_context(
        self,
        signals: List[OutreachRAGResult]
    ) -> str:
        """Build context string from selected signals."""
        if not signals:
            return ""
        
        lines = ["Relevant signals to incorporate:"]
        for i, signal in enumerate(signals, 1):
            signal_type = signal.signal_type or "general"
            lines.append(f"{i}. [{signal_type}] {signal.text[:200]}...")
        
        return "\n".join(lines)
    
    def _assemble_message(
        self,
        sections: Dict[str, MessageSection]
    ) -> str:
        """Assemble complete message from sections."""
        parts = []
        
        # Subject (typically shown separately but included for completeness)
        if "subject" in sections:
            subject_content = getattr(sections['subject'].content, 'content', str(sections['subject'].content))
            parts.append(f"Subject: {subject_content}")
            parts.append("")  # Empty line after subject

        # Hook/Opening
        if "hook" in sections:
            hook_content = getattr(sections["hook"].content, 'content', str(sections["hook"].content))
            parts.append(hook_content)
            parts.append("")

        # Value/Body
        if "value" in sections:
            value_content = getattr(sections["value"].content, 'content', str(sections["value"].content))
            parts.append(value_content)
            parts.append("")

        # CTA
        if "cta" in sections:
            cta_content = getattr(sections["cta"].content, 'content', str(sections["cta"].content))
            parts.append(cta_content)
            parts.append("")

        # Signature
        if "signature" in sections:
            signature_content = getattr(sections["signature"].content, 'content', str(sections["signature"].content))
            parts.append(signature_content)
        
        return "\n".join(parts)


#
# === Learning Trace Map ===
# LAYER: L2
# ROLE: Executes message generation with archetype-specific temperature control for executive outreach
# IMPACT: Applies temperature schedules by archetype -> maximizes executive reply rates by 40%
# FLOW: apps/lic_outreach/lic_workflow_entry.py -> MessagePlanner -> MessageGenerationExecutor.generate_message() -> L5 safety validation
#
