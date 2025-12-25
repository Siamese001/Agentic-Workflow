#!/usr/bin/env python3
"""
Pitch Generator for Outreach Engine
Generates personalized outreach pitches
"""
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol

logger = logging.getLogger(__name__)


@dataclass
class PitchResult:
    """Result from pitch generation."""
    subject: str
    content: str
    metadata: Dict[str, Any]


class PitchGenerator:
    """Generates personalized outreach pitches."""

    def __init__(self, llm_client=None):
        """
        Initialize pitch generator.

        Args:
            llm_client: Optional LLM client for generation
        """
        self.llm_client = llm_client

    def generate_pitch(self, context: Dict[str, Any],
                      relationships: Dict[str, Any]) -> PitchResult:
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

    def _generate_with_llm(self, context: Dict[str, Any],
                          relationships: Dict[str, Any]) -> PitchResult:
        """Generate pitch using LLM."""
        try:
            prompt = self._build_pitch_prompt(context, relationships)
            response = self.llm_client.generate(prompt)

            # Parse response into subject and content
            lines = response.text.strip().split('\n')
            subject = lines[0].replace('Subject:', '').strip() if lines else "Introduction"
            content = '\n'.join(lines[1:]) if len(lines) > 1 else response.text

            return PitchResult(
                subject=subject,
                content=content,
                metadata={
                    "source": "llm",
                    "model": self.llm_client.model_name,
                    "tokens_used": getattr(response.usage, 'total_tokens', 0),
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"LLM pitch generation failed: {e}")
            return self._generate_with_template(context, relationships)

    def _generate_with_template(self, context: Dict[str, Any],
                               relationships: Dict[str, Any]) -> PitchResult:
        """Generate pitch using template."""
        company_name = context.get("company_name", "the company")
        recent_news = context.get("recent_news", "recent developments")
        contact_name = relationships.get("contact_name", "there")
        mutual_connections = relationships.get("mutual_connections", [])

        # Build subject
        subject = f"Introduction - {context.get('my_name', 'Your Name')} & {company_name}"

        # Build content
        content = f"""Dear {contact_name},

I hope this email finds you well. I've been following {company_name}'s work and was particularly impressed by {recent_news}.

{'We share several mutual connections: ' + ', '.join(mutual_connections[:3]) + '.' if mutual_connections else ''}

I believe my experience in {context.get('my_field', 'technology')} could be valuable to your team, especially given your focus on {context.get('company_focus', 'innovation')}.

Would you be open to a brief conversation next week to explore potential synergies?

Best regards,
{context.get('my_name', 'Your Name')}
{context.get('my_title', 'Your Title')}
{context.get('my_contact', 'your@email.com')}
"""

        return PitchResult(
            subject=subject,
            content=content,
            metadata={
                "source": "template",
                "template": "professional_outreach",
                "timestamp": datetime.now().isoformat()
            }
        )

    def _build_pitch_prompt(self, context: Dict[str, Any],
                           relationships: Dict[str, Any]) -> str:
        """Build prompt for LLM pitch generation."""
        return f"""
Generate a professional outreach email based on the following:

COMPANY CONTEXT:
{json.dumps(context, indent=2)}

RELATIONSHIP CONTEXT:
{json.dumps(relationships, indent=2)}

Requirements:
- Write a compelling subject line
- Keep the email concise (150-200 words)
- Personalize with recent company news or developments
- Mention mutual connections if available
- Include a clear call to action
- Maintain professional but friendly tone
- Avoid sales-heavy language

Format the response with the subject line first, followed by the email body.
"""

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
            prompt = f"""
Refine the following outreach email to address: {error_reason}

ORIGINAL EMAIL:
Subject: {pitch.subject}

{pitch.content}

Refinement requirements:
- Fix the specific issue mentioned
- Maintain professional tone
- Keep it concise
- Ensure brand compliance
- Avoid spam triggers

Provide the refined email in the same format (subject first, then body).
"""
            response = self.llm_client.generate(prompt)

            # Parse response
            lines = response.text.strip().split('\n')
            subject = lines[0].replace('Subject:', '').strip() if lines else pitch.subject
            content = '\n'.join(lines[1:]) if len(lines) > 1 else response.text

            return PitchResult(
                subject=subject,
                content=content,
                metadata={
                    "source": "llm_refined",
                    "original_subject": pitch.subject,
                    "refinement_reason": error_reason,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"LLM pitch refinement failed: {e}")
            return self._refine_with_rules(pitch, error_reason)

    def _refine_with_rules(self, pitch: PitchResult, error_reason: str) -> PitchResult:
        """Refine pitch using rule-based approach."""
        content = pitch.content
        subject = pitch.subject

        # Apply refinement rules based on error reason
        if "salesy" in error_reason.lower():
            content = content.replace("excited to offer", "interested in discussing")
            content = content.replace("amazing opportunity", "potential collaboration")
            subject = subject.replace("Opportunity", "Introduction")

        if "brand" in error_reason.lower():
            # Ensure professional tone
            content = content.replace("!!", "!")
            content = content.replace("$$$ ", "")

        if "spam" in error_reason.lower():
            # Remove spam triggers
            content = content.replace("FREE", "complimentary")
            content = content.replace("ACT NOW", "Let me know if you're interested")

        return PitchResult(
            subject=subject,
            content=content,
            metadata={
                "source": "rule_refined",
                "original_subject": pitch.subject,
                "refinement_reason": error_reason,
                "timestamp": datetime.now().isoformat()
            }
        )
