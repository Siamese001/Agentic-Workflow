#!/usr/bin/env python3
"""
Core Utilities for Resume Engine
Provides draft generation, scoring, and file operations
"""
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

logger = logging.getLogger(__name__)


@dataclass
class DraftResult:
    """Result from draft generation."""
    content: str
    source: str
    metadata: Dict[str, Any] = None


class DraftGenerator:
    """Generates cover letter drafts using LLM."""

    def __init__(self, llm_client=None):
        """
        Initialize draft generator.

        Args:
            llm_client: LLM client for generation
        """
        self.llm_client = llm_client

    def generate_draft_llm(self, profile: Dict[str, Any],
                          job_desc: str,
                          template: Dict[str, Any]) -> DraftResult:
        """
        Generate cover letter draft using LLM.

        Args:
            profile: User profile data
            job_desc: Job description text
            template: Cover letter template

        Returns:
            Generated draft with metadata
        """
        if self.llm_client:
            # Use real LLM client
            return self._generate_with_llm(profile, job_desc, template)
        else:
            # Use template-based generation
            return self._generate_with_template(profile, job_desc, template)

    def _generate_with_llm(self, profile: Dict[str, Any],
                          job_desc: str,
                          template: Dict[str, Any]) -> DraftResult:
        """Generate draft using real LLM."""
        try:
            prompt = self._build_prompt(profile, job_desc, template)
            response = self.llm_client.generate(prompt)

            return DraftResult(
                content=response.text,
                source="llm",
                metadata={
                    "model": self.llm_client.model_name,
                    "tokens_used": response.usage.total_tokens,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_with_template(profile, job_desc, template)

    def _generate_with_template(self, profile: Dict[str, Any],
                               job_desc: str,
                               template: Dict[str, Any]) -> DraftResult:
        """Generate draft using template."""
        structure = template.get("structure", {})

        # Extract job details
        company = self._extract_company(job_desc)
        position = self._extract_position(job_desc)

        # Build draft from template
        draft_parts = []

        # Header
        header = structure.get("header", "").format(
            name=profile.get("name", ""),
            title=profile.get("title", ""),
            contact=self._format_contact(profile.get("contact", {})),
            date=datetime.now().strftime("%B %d, %Y")
        )
        draft_parts.append(header)

        # Greeting
        greeting = structure.get("greeting", "").format(
            hiring_manager="Hiring Manager"
        )
        draft_parts.append(greeting)

        # Introduction
        intro = structure.get("introduction", "").format(
            position=position,
            company=company
        )
        draft_parts.append(intro)

        # Body paragraphs
        body = structure.get("body", [])
        for i, paragraph_template in enumerate(body):
            paragraph = paragraph_template.format(
                experience=profile.get("experience", ""),
                field=profile.get("field", "software engineering"),
                skills=", ".join(profile.get("skills", [])),
                previous_company=profile.get("previous_company", "previous role"),
                achievement=self._format_achievement(profile.get("achievements", [])),
                company_value=company,
                company_culture="innovative culture"
            )
            draft_parts.append(paragraph)

        # Closing
        closing = structure.get("closing", "")
        draft_parts.append(closing)

        # Signature
        signature = structure.get("signature", "").format(
            name=profile.get("name", "")
        )
        draft_parts.append(signature)

        content = "\n\n".join(draft_parts)

        return DraftResult(
            content=content,
            source="template",
            metadata={
                "template": template.get("name"),
                "timestamp": datetime.now().isoformat()
            }
        )

    def _build_prompt(self, profile: Dict[str, Any],
                     job_desc: str,
                     template: Dict[str, Any]) -> str:
        """Build prompt for LLM generation."""
        return f"""
Generate a professional cover letter based on the following:

USER PROFILE:
{json.dumps(profile, indent=2)}

JOB DESCRIPTION:
{job_desc}

TEMPLATE STYLE:
{json.dumps(template.get("structure", {}), indent=2)}

Requirements:
- Follow the template structure
- Personalize with user profile details
- Address key points from job description
- Keep it professional and concise
- Highlight relevant skills and experience
"""

    def _extract_company(self, job_desc: str) -> str:
        """Extract company name from job description."""
        # Look for common patterns
        patterns = [
            r'at\s+([A-Z][a-zA-Z\s&]+?)(?:\s+(?:is|we are|are a)|\n|$)',
            r'([A-Z][a-zA-Z\s&]+?)(?:\s+(?:Inc\.|LLC|Ltd\.|Corporation))',
            r'company[:\s]+([A-Z][a-zA-Z\s&]+?)(?:\n|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, job_desc, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "the company"

    def _extract_position(self, job_desc: str) -> str:
        """Extract position from job description."""
        patterns = [
            r'(?:position|role|title)[:\s]+([A-Z][a-zA-Z\s]+?)(?:\n|$)',
            r'(?:seeking|hiring|looking for)\s+(?:a\s+)?([a-zA-Z\s]+?)(?:\n|$)',
            r'([A-Z][a-z]+\s+(?:Developer|Engineer|Manager|Analyst|Specialist))'
        ]

        for pattern in patterns:
            match = re.search(pattern, job_desc, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "the position"

    def _format_contact(self, contact: Dict[str, str]) -> str:
        """Format contact information."""
        parts = []
        if contact.get("email"):
            parts.append(contact["email"])
        if contact.get("phone"):
            parts.append(contact["phone"])
        if contact.get("linkedin"):
            parts.append(contact["linkedin"])
        return " | ".join(parts)

    def _format_achievement(self, achievements: list) -> str:
        """Format achievements for template."""
        if not achievements:
            return "developed innovative solutions"
        return achievements[0] if achievements else "developed innovative solutions"


class SemanticScorer:
    """Scores draft quality using semantic analysis."""

    def __init__(self):
        """Initialize semantic scorer."""
        self.quality_thresholds = {
            "excellent": 0.9,
            "good": 0.7,
            "acceptable": 0.5,
            "poor": 0.3
        }

    def semantic_score_draft(self, draft: str) -> Dict[str, Any]:
        """
        Score draft quality semantically.

        Args:
            draft: Draft text to score

        Returns:
            Scoring result with quality metrics
        """
        if not draft:
            return {
                "quality": 0.0,
                "grade": "poor",
                "reason": "Empty draft",
                "metrics": {}
            }

        # Calculate various quality metrics
        metrics = {
            "length_score": self._score_length(draft),
            "structure_score": self._score_structure(draft),
            "keyword_score": self._score_keywords(draft),
            "readability_score": self._score_readability(draft),
            "professionalism_score": self._score_professionalism(draft)
        }

        # Calculate overall quality
        quality = sum(metrics.values()) / len(metrics)
        grade = self._get_grade(quality)
        reason = self._generate_reason(metrics, grade)

        return {
            "quality": quality,
            "grade": grade,
            "reason": reason,
            "metrics": metrics
        }

    def _score_length(self, draft: str) -> float:
        """Score draft length."""
        word_count = len(draft.split())

        if word_count < 100:
            return 0.3
        elif word_count < 200:
            return 0.7
        elif word_count < 400:
            return 1.0
        else:
            return 0.8  # Too long

    def _score_structure(self, draft: str) -> float:
        """Score draft structure."""
        required_elements = [
            r"Dear\s+\w+,",  # Greeting
            r"Sincerely|Best regards|Regards",  # Closing
            r"\n\n",  # Paragraphs
        ]

        score = 0.0
        for element in required_elements:
            if re.search(element, draft, re.IGNORECASE):
                score += 1.0 / len(required_elements)

        return score

    def _score_keywords(self, draft: str) -> float:
        """Score presence of professional keywords."""
        positive_keywords = [
            "experience", "skills", "developed", "implemented",
            "achieved", "managed", "led", "created", "improved"
        ]

        draft_lower = draft.lower()
        found_keywords = sum(1 for kw in positive_keywords if kw in draft_lower)

        return min(found_keywords / 5, 1.0)  # Normalize to 0-1

    def _score_readability(self, draft: str) -> float:
        """Score readability based on sentence length."""
        sentences = re.split(r'[.!?]+', draft)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # Ideal average sentence length is 15-20 words
        if 10 <= avg_length <= 25:
            return 1.0
        elif 5 <= avg_length <= 35:
            return 0.8
        else:
            return 0.5

    def _score_professionalism(self, draft: str) -> float:
        """Score professionalism of language."""
        unprofessional = [
            "hey", "yo", "what's up", "awesome", "cool",
            "wanna", "gonna", "kinda", "sorta"
        ]

        draft_lower = draft.lower()
        unprofessional_count = sum(1 for word in unprofessional if word in draft_lower)

        # Penalize unprofessional language
        penalty = min(unprofessional_count * 0.2, 0.8)
        return max(1.0 - penalty, 0.2)

    def _get_grade(self, quality: float) -> str:
        """Get grade from quality score."""
        if quality >= self.quality_thresholds["excellent"]:
            return "excellent"
        elif quality >= self.quality_thresholds["good"]:
            return "good"
        elif quality >= self.quality_thresholds["acceptable"]:
            return "acceptable"
        else:
            return "poor"

    def _generate_reason(self, metrics: Dict[str, float], grade: str) -> str:
        """Generate reason for score."""
        weak_metrics = [k for k, v in metrics.items() if v < 0.6]

        if not weak_metrics:
            return f"Excellent quality across all metrics"

        return f"Needs improvement in: {', '.join(weak_metrics)}"


class FileManager:
    """Handles file operations for drafts."""

    @staticmethod
    def write_file(path: str, content: str) -> bool:
        """
        Write content to file.

        Args:
            path: File path
            content: Content to write

        Returns:
            True if successful
        """
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"File written successfully: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write file {path}: {e}")
            return False

    @staticmethod
    def read_file(path: str) -> Optional[str]:
        """
        Read content from file.

        Args:
            path: File path

        Returns:
            File content or None if failed
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            return None


# Process registration for P5 compliance
def register_process(agent_name: str, pid: int) -> None:
    """Register process for P5 watchdog monitoring."""
    logger.info(f"P5_REGISTER: {agent_name} (PID: {pid})")


def log_action(action: str, details: Optional[Dict] = None) -> None:
    """Log action for P5 compliance."""
    log_entry = f"ACTION: {action}"
    if details:
        log_entry += f" | {details}"
    logger.info(log_entry)
