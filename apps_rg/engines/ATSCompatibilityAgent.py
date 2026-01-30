"""
ATSCompatibilityAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin
from apps_rg.shared.core.agent_base import RGAgentBase


@dataclass
class ATSCompatibilityAgent(SubatomicTestingMixin, RGAgentBase):
    """
    Validates ATS (Applicant Tracking System) compatibility.

    Checks:
    - No complex formatting
    - Standard section headers
    - Keyword optimization
    - No tables/graphics references
    """

    STANDARD_HEADERS = {
        "summary": ["summary", "professional summary", "profile", "objective"],
        "experience": ["experience", "work experience", "employment history", "work history"],
        "skills": ["skills", "technical skills", "core competencies", "expertise"],
        "education": ["education", "academic background", "qualifications"],
    }

    ATS_UNFRIENDLY_PATTERNS = [
        r"[│┃┆┇┊┋]",  # Box drawing characters
        r"[★☆●○◆◇■□▪▫]",  # Decorative bullets
        r"[\u2500-\u257F]",  # Box drawing
        r"<table",  # HTML tables
        r"<img",  # Images
    ]

    def __post_init__(self) -> None:
        """Initialize ATS compatibility agent."""
        super().__post_init__()

    async def execute(self) -> None:
        """
        Execute ATS compatibility check.

        Validates resume for:
        - ATS-unfriendly formatting patterns
        - Standard section headers
        - Keyword optimization against job description

        Raises:
            ATS_FAILURE signal if compatibility issues found
        """
        self.log("Checking ATS compatibility...")

        resume = self.ctx.current_resume
        job_desc = self.ctx.JobDescription

        if not resume:
            self.record_fail("No resume to check")
            self.add_signal("ATS_FAILURE")
            return

        issues: list[str] = []

        # Check for ATS-unfriendly patterns (use ensure_ascii=False to preserve unicode)
        full_content: str = json.dumps(resume, ensure_ascii=False)
        for pattern in self.ATS_UNFRIENDLY_PATTERNS:
            if re.search(pattern, full_content):
                issues.append(f"ATS-unfriendly pattern found: {pattern}")

        # Check section headers
        for section_name in resume.keys():
            if section_name.startswith("_"):
                continue

            normalized: str = section_name.lower().strip()
            is_standard: bool = False

            for standard_section, variants in self.STANDARD_HEADERS.items():
                if normalized in variants or normalized == standard_section:
                    is_standard = True
                    break

            if not is_standard and normalized not in [
                "contact",
                "projects",
                "certifications",
                "achievements",
            ]:
                issues.append(f"Non-standard section header: {section_name}")

        # Check keyword optimization if job description available
        if job_desc:
            keyword_score = self._calculate_keyword_score(resume, job_desc)
            if keyword_score < 0.3:
                issues.append(f"Low keyword match ({keyword_score:.0%})")

        if issues:
            self.record_fail(f"ATS issues: {len(issues)}", data=issues)
            self.add_signal("ATS_FAILURE")
        else:
            self.record_pass("ATS compatible")
            self.remove_signal("ATS_FAILURE")

    def _calculate_keyword_score(self, resume: dict[str, Any], job_desc: str) -> float:
        """
        Calculate keyword match score between resume and job description.

        Args:
            resume: Resume data dictionary
            job_desc: Job description text

        Returns:
            Float between 0.0 and 1.0 representing keyword match percentage
        """
        # Extract keywords from job description
        job_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", job_desc.lower()))

        # Common words to ignore
        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "you",
            "are",
            "will",
            "have",
            "this",
            "that",
            "from",
            "they",
            "been",
            "were",
            "being",
            "their",
            "would",
            "could",
            "should",
            "about",
            "which",
            "when",
            "what",
            "where",
            "there",
            "here",
        }
        job_words -= stop_words

        if not job_words:
            return 1.0

        # Check resume content
        resume_text = json.dumps(resume).lower()
        matches = sum(1 for word in job_words if word in resume_text)

        return matches / len(job_words)

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, int]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            **kwargs: Additional healing parameters

        Returns:
            Dict with healing summary (violations, fixed, errors)
        """
        return super().heal_repository(dry_run, execute, **kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by ATSCompatibilityAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"ATSCompatibilityAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"ATSCompatibilityAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
