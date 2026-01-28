from __future__ import annotations

"""
Pitch Generator for Outreach Engine
Generates personalized outreach pitches
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

Logger: Any = logging.getLogger(__name__)

# ARCHITECTURAL MANIFEST: Explicitly declare primary exports
__all__ = ["PitchGenerator", "PitchResult"]


@dataclass
class PitchResult:
    """Result from pitch generation."""

    subject: str
    content: str
    metadata: dict[str, Any]


class PitchGenerator:
    """Generates personalized outreach pitches."""

    def __init__(self, llm_client=None):
        """
        Initialize pitch generator.

        Args:
            llm_client: Optional LLM client for generation
        """
        self.llm_client = llm_client

    def generate_pitch(self, context: dict[str, Any], relationships: dict[str, Any]) -> PitchResult:
        """
        Generate personalized pitch based on context and relationships.

        Args:
            context: Company context and news
            relationships: Contact history and relationships

        Returns:
            PitchResult with subject, content, and metadata
        """
        if self.llm_client:
            return self._generate_with_llm(context, relationships)
        else:
            return self._generate_with_template(context, relationships)

    def _generate_with_llm(
        self, context: dict[str, Any], relationships: dict[str, Any]
    ) -> PitchResult:
        """Generate pitch using LLM."""
        try:
            prompt = self._build_pitch_prompt(context, relationships)
            response = self.llm_client.generate(prompt)
            lines = response.text.strip().split("\n")
            subject = lines[0].replace("Subject:", "").strip() if lines else "Introduction"
            content = "\n".join(lines[1:]) if len(lines) > 1 else response.text
            return PitchResult(
                subject=subject,
                content=content,
                metadata={
                    "source": "llm",
                    "model": self.llm_client.model_name,
                    "tokens_used": getattr(response.usage, "total_tokens", 0),
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            Logger.error(f"LLM pitch generation failed: {e}")
            return self._generate_with_template(context, relationships)

    def _generate_with_template(
        self, context: dict[str, Any], relationships: dict[str, Any]
    ) -> PitchResult:
        """Generate pitch using template."""
        company_name = context.get("company_name", "the company")
        recent_news = context.get("recent_news", "recent developments")
        contact_name = relationships.get("contact_name", "there")
        mutual_connections = relationships.get("mutual_connections", [])
        subject = f"Introduction - {context.get('my_name', 'Your Name')} & {company_name}"
        content = f"Dear {contact_name},\n\nI hope this email finds you well. I've been following {company_name}'s work and was particularly impressed by {recent_news}.\n\n{('We share several mutual connections: ' + ', '.join(mutual_connections[:3]) + '.' if mutual_connections else '')}\n\nI believe my experience in {context.get('my_field', 'technology')} could be valuable to your team, especially given your focus on {context.get('company_focus', 'innovation')}.\n\nWould you be open to a brief conversation next week to explore potential synergies?\n\nBest regards,\n{context.get('my_name', 'Your Name')}\n{context.get('my_title', 'Your Title')}\n{context.get('my_contact', 'your@email.com')}\n"
        return PitchResult(
            subject=subject,
            content=content,
            metadata={
                "source": "template",
                "template": "professional_outreach",
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _build_pitch_prompt(self, context: dict[str, Any], relationships: dict[str, Any]) -> str:
        """Build prompt for LLM pitch generation."""
        return f"\nGenerate a professional outreach email based on the following:\n\nCOMPANY CONTEXT:\n{json.dumps(context, indent=2)}\n\nRELATIONSHIP CONTEXT:\n{json.dumps(relationships, indent=2)}\n\nRequirements:\n- Write a compelling subject line\n- Keep the email concise (150-200 words)\n- Personalize with recent company news or developments\n- Mention mutual connections if available\n- Include a clear call to action\n- Maintain professional but friendly tone\n- Avoid sales-heavy language\n\nFormat the response with the subject line first, followed by the email body.\n"

    def refine_pitch(self, pitch: PitchResult, error_reason: str) -> PitchResult:
        """
        Refine a pitch based on error feedback.

        Args:
            pitch: Original pitch to refine
            error_reason: Reason for refinement (e.g., "Too salesy", "Brand compliance issue")

        Returns:
            Refined PitchResult
        """
        if self.llm_client:
            return self._refine_with_llm(pitch, error_reason)
        else:
            return self._refine_with_rules(pitch, error_reason)

    def _refine_with_llm(self, pitch: PitchResult, error_reason: str) -> PitchResult:
        """Refine pitch using LLM."""
        try:
            prompt = f"\nRefine the following outreach email to address: {error_reason}\n\nORIGINAL EMAIL:\nSubject: {pitch.subject}\n\n{pitch.content}\n\nRefinement requirements:\n- Fix the specific issue mentioned\n- Maintain professional tone\n- Keep it concise\n- Ensure brand compliance\n- Avoid spam triggers\n\nProvide the refined email in the same format (subject first, then body).\n"
            response = self.llm_client.generate(prompt)
            lines = response.text.strip().split("\n")
            subject = lines[0].replace("Subject:", "").strip() if lines else pitch.subject
            content = "\n".join(lines[1:]) if len(lines) > 1 else response.text
            return PitchResult(
                subject=subject,
                content=content,
                metadata={
                    "source": "llm_refined",
                    "original_subject": pitch.subject,
                    "refinement_reason": error_reason,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            Logger.error(f"LLM pitch refinement failed: {e}")
            return self._refine_with_rules(pitch, error_reason)

    def _refine_with_rules(self, pitch: PitchResult, error_reason: str) -> PitchResult:
        """Refine pitch using rule-based approach."""
        content = pitch.content
        subject = pitch.subject
        if "salesy" in error_reason.lower():
            content = content.replace("excited to offer", "interested in discussing")
            content = content.replace("amazing opportunity", "potential collaboration")
            subject = subject.replace("Opportunity", "Introduction")
        if "brand" in error_reason.lower():
            content = content.replace("!!", "!")
            content = content.replace("$$$ ", "")
        if "spam" in error_reason.lower():
            content = content.replace("FREE", "complimentary")
            content = content.replace("ACT NOW", "Let me know if you're interested")
        return PitchResult(
            subject=subject,
            content=content,
            metadata={
                "source": "rule_refined",
                "original_subject": pitch.subject,
                "refinement_reason": error_reason,
                "timestamp": datetime.now().isoformat(),
            },
        )
