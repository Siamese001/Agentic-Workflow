"""
SectionBalanceAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
Refactored: 2026-02-08 (Cluster 2 — RGValidationCapability extraction)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_rg.utils.rg_validation_capability import RGValidationCapability
from apps_rg.utils.RGAgentBase import RGAgentBase


@dataclass
class SectionBalanceAgent(RGValidationCapability, RGAgentBase):
    """
    Ensures proper section balance and prioritization.

    Checks:
    - Section lengths are proportional
    - Important sections are present
    - Order matches job requirements
    """

    VALIDATION_SIGNAL = "BALANCE_ISSUE"
    VALIDATION_LOG_PREFIX = "Checking section balance..."
    VALIDATION_PASS_MESSAGE = "Section balance is good"
    VALIDATION_FAIL_PREFIX = "Balance issues"

    REQUIRED_SECTIONS = ["summary", "experience", "skills"]
    RECOMMENDED_SECTIONS = ["education", "projects", "certifications"]

    MAX_SECTION_RATIOS = {
        "summary": 0.40,  # Max 40% of total
        "experience": 0.70,  # Max 70% of total
        "skills": 0.40,  # Max 40% of total
        "education": 0.30,  # Max 30% of total
    }

    def __post_init__(self) -> None:
        """Initialize section balance agent."""
        super().__post_init__()

    async def execute(self) -> None:
        """
        Execute section balance check via RGValidationCapability harness.

        Validates resume for:
        - Required sections presence
        - Section length proportions
        - Content balance across sections

        Raises:
            BALANCE_ISSUE signal if sections are imbalanced
        """
        await self.run_validation()

    async def collect_issues(self) -> list[str]:
        """Collect section balance issues from the current resume."""
        resume = self.ctx.current_resume
        if not resume:
            return ["No resume to check"]

        issues: list[str] = []

        # Check required sections
        for section in self.REQUIRED_SECTIONS:
            if section not in resume or not resume[section]:
                issues.append(f"Missing required section: {section}")

        # Calculate total content length
        total_length = sum(len(self.content_to_string(v)) for k, v in resume.items() if not k.startswith("_"))

        if total_length == 0:
            return ["Resume has no content"]

        # Check section ratios
        for section, max_ratio in self.MAX_SECTION_RATIOS.items():
            if section in resume:
                section_length = len(self.content_to_string(resume[section]))
                ratio = section_length / total_length
                if ratio > max_ratio:
                    issues.append(f"{section} is too long ({ratio:.0%} > {max_ratio:.0%})")

        return issues

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by SectionBalanceAgent."""
        return self.make_heal_result(violation)
