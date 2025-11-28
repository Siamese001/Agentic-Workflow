"""LIC Message Executor - L2 execution for final message generation.

Implements nuclear prompt requirements for deterministic message execution:
- Take LICFusionPlan + persona/grounding output and call LLMs/tools to generate final text
- L2 only: no planning logic, prompt assembly + LLM/tool calls only
- Async interface with proper awaits, no safety filtering (handled by L5)
"""

from typing import Any, Dict, List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class LICMessageExecutor:
    """L2 executor for LIC message generation.
    
    Generates final message text by assembling prompts from fusion plans
    and calling configured LLM clients with proper async handling.
    """
    
    def __init__(
        self,
        *,
        llm_client: Optional[Any] = None,
        telemetry_bus: Optional[Any] = None,
    ) -> None:
        """Initialize LIC message executor with dependencies."""
        self.llm_client = llm_client
        self.telemetry_bus = telemetry_bus
        
        if not self.llm_client:
            logger.warning("No LLM client provided to message executor")
    
    async def generate_message(
        self,
        fusion_plan: Dict[str, Any],
        persona_plan: Dict[str, Any],
        grounding_plan: Dict[str, Any],
    ) -> str:
        """Generate final outreach message from plans.
        
        Args:
            fusion_plan: LICFusionPlan from L1 with sections and value propositions
            persona_plan: LICPersonaPlan from L1 with tone and style parameters
            grounding_plan: LICGroundingPlan from L1 with allowed claims
            
        Returns:
            Generated message text (no safety filtering)
        """
        try:
            # 1. Assemble prompt from fusion plan and context
            prompt = self._assemble_prompt(fusion_plan, persona_plan, grounding_plan)
            
            # 2. Call LLM client for message generation
            message_text = await self._call_llm_for_generation(prompt, persona_plan)
            
            # 3. Post-process message (formatting, basic cleanup)
            message_text = self._post_process_message(message_text, fusion_plan)
            
            # 4. Record telemetry (best-effort)
            self._safe_record_telemetry(fusion_plan, persona_plan, message_text)
            
            return message_text
            
        except Exception as e:
            logger.error(f"Message generation failed: {e}")
            return f"Error generating message: {str(e)}"
    
    def _assemble_prompt(
        self,
        fusion_plan: Dict[str, Any],
        persona_plan: Dict[str, Any],
        grounding_plan: Dict[str, Any],
    ) -> str:
        """Assemble complete prompt from all plan components."""
        # Extract key components
        role_title = fusion_plan.get("role_title", "")
        company_name = fusion_plan.get("company_name", "")
        archetype = fusion_plan.get("archetype", "")
        sections = fusion_plan.get("sections", [])
        value_props = fusion_plan.get("value_propositions", [])
        
        # Extract persona parameters
        tone_style = persona_plan.get("tone_style", "neutral")
        detail_level = persona_plan.get("detail_level", "medium")
        risk_tolerance = persona_plan.get("risk_tolerance", "medium")
        
        # Extract grounding constraints
        allowed_claims = grounding_plan.get("allowed_claims", [])
        disallowed_claims = grounding_plan.get("disallowed_claims", [])
        
        # Build prompt sections
        prompt_parts = []
        
        # 1. Context and objective
        prompt_parts.append(f"# OUTREACH MESSAGE GENERATION")
        prompt_parts.append(f"Role: {role_title}")
        prompt_parts.append(f"Company: {company_name}")
        prompt_parts.append(f"Target Archetype: {archetype}")
        prompt_parts.append("")
        
        # 2. Persona guidance
        prompt_parts.append("## PERSONA GUIDELINES")
        prompt_parts.append(f"Tone Style: {tone_style}")
        prompt_parts.append(f"Detail Level: {detail_level}")
        prompt_parts.append(f"Risk Tolerance: {risk_tolerance}")
        prompt_parts.append("")
        
        # 3. Value propositions
        prompt_parts.append("## KEY VALUE PROPOSITIONS")
        for i, vp in enumerate(value_props[:5]):  # Limit to top 5
            if isinstance(vp, dict):
                achievement = vp.get("achievement_snippet", "")
                signal = vp.get("signal_snippet", "")
                angle = vp.get("angle", "")
                prompt_parts.append(f"{i+1}. {achievement} → {signal} (angle: {angle})")
        prompt_parts.append("")
        
        # 4. Message structure
        prompt_parts.append("## MESSAGE STRUCTURE")
        for section in sections:
            if isinstance(section, dict):
                section_type = section.get("section_type", "")
                tone_guidance = section.get("tone_guidance", "")
                cta_guidance = section.get("cta_guidance", "")
                
                prompt_parts.append(f"### {section_type.upper()}")
                if tone_guidance:
                    prompt_parts.append(f"Tone: {tone_guidance}")
                if cta_guidance:
                    prompt_parts.append(f"CTA: {cta_guidance}")
                prompt_parts.append("")
        
        # 5. Grounding constraints
        if allowed_claims or disallowed_claims:
            prompt_parts.append("## GROUNDING CONSTRAINTS")
            
            if allowed_claims:
                prompt_parts.append("Allowed claims:")
                for claim in allowed_claims[:3]:  # Limit to top 3
                    if isinstance(claim, dict):
                        description = claim.get("description", "")
                        prompt_parts.append(f"- {description}")
                prompt_parts.append("")
            
            if disallowed_claims:
                prompt_parts.append("Avoid these claims:")
                for claim in disallowed_claims[:3]:  # Limit to top 3
                    if isinstance(claim, dict):
                        description = claim.get("description", "")
                        prompt_parts.append(f"- {description}")
                prompt_parts.append("")
        
        # 6. Generation instructions
        prompt_parts.append("## GENERATION INSTRUCTIONS")
        prompt_parts.append("Generate a professional outreach message that:")
        prompt_parts.append("- Incorporates the key value propositions naturally")
        prompt_parts.append("- Follows the specified message structure")
        prompt_parts.append("- Matches the persona tone and style guidelines")
        prompt_parts.append("- Respects grounding constraints")
        prompt_parts.append("- Is concise and impactful")
        prompt_parts.append("")
        prompt_parts.append("Generate only the message content, no explanations.")
        
        return "\n".join(prompt_parts)
    
    async def _call_llm_for_generation(self, prompt: str, persona_plan: Dict[str, Any]) -> str:
        """Call LLM client for message generation."""
        if not self.llm_client:
            return "No LLM client available for message generation"
        
        try:
            # Configure LLM parameters based on persona
            temperature = self._get_temperature_for_persona(persona_plan)
            max_tokens = self._get_max_tokens_for_persona(persona_plan)
            
            # Call LLM with async await
            response = await self.llm_client.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                # Add other LLM parameters as needed
            )
            
            # Extract generated text from response
            if isinstance(response, dict):
                generated_text = response.get("text", response.get("content", ""))
            else:
                generated_text = str(response)
            
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"LLM generation error: {str(e)}"
    
    def _get_temperature_for_persona(self, persona_plan: Dict[str, Any]) -> float:
        """Get appropriate temperature setting based on persona."""
        risk_tolerance = persona_plan.get("risk_tolerance", "medium")
        
        if risk_tolerance == "low":
            return 0.3  # More conservative, predictable output
        elif risk_tolerance == "high":
            return 0.8  # More creative, varied output
        else:
            return 0.5  # Balanced creativity and consistency
    
    def _get_max_tokens_for_persona(self, persona_plan: Dict[str, Any]) -> int:
        """Get appropriate max tokens based on persona detail level."""
        detail_level = persona_plan.get("detail_level", "medium")
        
        if detail_level == "low":
            return 200   # Concise, executive-style messages
        elif detail_level == "high":
            return 500   # Detailed, technical messages
        else:
            return 350   # Balanced length
    
    def _post_process_message(self, message_text: str, fusion_plan: Dict[str, Any]) -> str:
        """Post-process generated message for formatting and cleanup."""
        if not message_text:
            return message_text
        
        # Basic cleanup
        processed = message_text.strip()
        
        # Remove any markdown formatting if present
        processed = processed.replace("**", "").replace("*", "")
        
        # Ensure proper spacing
        processed = " ".join(processed.split())
        
        # Add proper paragraph breaks (simple heuristic)
        processed = processed.replace(". ", ".\n\n")
        processed = processed.replace("? ", "?\n\n")
        processed = processed.replace("! ", "!\n\n")
        
        # Limit excessive newlines
        while "\n\n\n" in processed:
            processed = processed.replace("\n\n\n", "\n\n")
        
        return processed.strip()
    
    def _safe_record_telemetry(
        self,
        fusion_plan: Dict[str, Any],
        persona_plan: Dict[str, Any],
        message_text: str,
    ) -> None:
        """Record telemetry event safely without breaking execution."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_message_generation_completed",
                layer="L2",
                payload={
                    "company_name": fusion_plan.get("company_name", ""),
                    "role_title": fusion_plan.get("role_title", ""),
                    "archetype": fusion_plan.get("archetype", ""),
                    "tone_style": persona_plan.get("tone_style", ""),
                    "detail_level": persona_plan.get("detail_level", ""),
                    "message_length": len(message_text),
                    "sections_count": len(fusion_plan.get("sections", [])),
                    "value_props_count": len(fusion_plan.get("value_propositions", [])),
                },
            )
        except Exception:
            # Telemetry failures should never break execution logic
            logger.debug("Failed to record telemetry for LIC message generation")
