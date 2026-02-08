"""
ATSCompatibilityAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
Converted to Facade: 2026-01-31 (Phase 2 Consolidation)
Refactored: 2026-02-08 (Cluster 2 — RGValidationCapability extraction)

Facade/Strategy indirection removed — domain logic now lives directly in
collect_issues() while the validation harness is provided by
RGValidationCapability.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from apps_rg.utils.rg_validation_capability import RGValidationCapability
from apps_rg.utils.RGAgentBase import RGAgentBase
from apps_shared.config.config_loader_config import load_agent_config


@dataclass
class ATSCompatibilityAgent(RGValidationCapability, RGAgentBase):
    """
    Validates ATS (Applicant Tracking System) compatibility.

    Checks:
    - No complex formatting
    - Standard section headers
    - Keyword optimization
    - No tables/graphics references
    """

    VALIDATION_SIGNAL = "ATS_FAILURE"
    VALIDATION_LOG_PREFIX = "Checking ATS compatibility..."
    VALIDATION_PASS_MESSAGE = "ATS compatible"
    VALIDATION_FAIL_PREFIX = "ATS issues"

    def __post_init__(self) -> None:
        """Initialize ATS compatibility agent."""
        super().__post_init__()

        # Load configuration from centralized config system
        self._config = load_agent_config("ats_compatibility")

        self.STANDARD_HEADERS = self._config.get("standard_headers", {})
        self.ATS_UNFRIENDLY_PATTERNS = self._config.get("ats_unfriendly_patterns", [])
        self.allowed_non_standard_sections = self._config.get("allowed_non_standard_sections", [])
        self.keyword_config = self._config.get("keyword_optimization", {})
        self.min_score_threshold = self.keyword_config.get("min_score_threshold", 0.3)
        self.stop_words = set(self.keyword_config.get("stop_words", []))

    async def execute(self) -> None:
        """
        Execute ATS compatibility check via RGValidationCapability harness.

        Validates resume for:
        - ATS-unfriendly formatting patterns
        - Standard section headers
        - Keyword optimization against job description

        Raises:
            ATS_FAILURE signal if compatibility issues found
        """
        await self.run_validation()

    async def collect_issues(self) -> list[str]:
        """Collect ATS compatibility issues from the current resume."""
        resume = getattr(self.ctx, "current_resume", None) if hasattr(self, "ctx") else None
        job_desc = getattr(self.ctx, "JobDescription", None) if hasattr(self, "ctx") else None

        if not resume:
            return ["No resume to check"]

        issues: list[str] = []

        # Check for ATS-unfriendly patterns
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

            if not is_standard and normalized not in self.allowed_non_standard_sections:
                issues.append(f"Non-standard section header: {section_name}")

        # Check keyword optimization if job description available
        if job_desc:
            score = self._calculate_keyword_score(resume, job_desc)
            if score < self.min_score_threshold:
                issues.append(f"Low keyword match ({score:.0%})")

        return issues

    def _calculate_keyword_score(self, resume: dict[str, Any], job_desc: str) -> float:
        """
        Calculate keyword match score between resume and job description.

        Args:
            resume: Resume data dictionary
            job_desc: Job description text

        Returns:
            Float between 0.0 and 1.0 representing keyword match percentage
        """
        job_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", job_desc.lower()))
        job_words -= self.stop_words

        if not job_words:
            return 1.0

        resume_text = json.dumps(resume).lower()
        matches = sum(1 for word in job_words if word in resume_text)
        return matches / len(job_words)

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> dict[str, int]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run, execute, **kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by ATSCompatibilityAgent."""
        return self.make_heal_result(violation)
