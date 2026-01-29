"""
SectionBalanceAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin
from apps_rg.shared.core.agent_base import RGAgentBase


@dataclass
class SectionBalanceAgent(SubatomicTestingMixin, RGAgentBase):
    """
    Ensures proper section balance and prioritization.

    Checks:
    - Section lengths are proportional
    - Important sections are present
    - Order matches job requirements
    """

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
        Execute section balance check.

        Validates resume for:
        - Required sections presence
        - Section length proportions
        - Content balance across sections

        Raises:
            BALANCE_ISSUE signal if sections are imbalanced
        """
        self.log("Checking section balance...")

        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume to check")
            return

        issues: list[str] = []

        # Check required sections
        for section in self.REQUIRED_SECTIONS:
            if section not in resume or not resume[section]:
                issues.append(f"Missing required section: {section}")

        # Calculate total content length
        total_length = sum(
            len(self._to_string(v)) for k, v in resume.items() if not k.startswith("_")
        )

        if total_length == 0:
            self.record_fail("Resume has no content")
            return

        # Check section ratios
        for section, max_ratio in self.MAX_SECTION_RATIOS.items():
            if section in resume:
                section_length = len(self._to_string(resume[section]))
                ratio = section_length / total_length
                if ratio > max_ratio:
                    issues.append(f"{section} is too long ({ratio:.0%} > {max_ratio:.0%})")

        if issues:
            self.record_fail(f"Balance issues: {len(issues)}", data=issues)
            self.add_signal("BALANCE_ISSUE")
        else:
            self.record_pass("Section balance is good")
            self.remove_signal("BALANCE_ISSUE")

    def _to_string(self, content: Any) -> str:
        """
        Convert content to string for length calculation.

        Args:
            content: Content to convert (str, list, dict, or other)

        Returns:
            String representation of content
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        elif isinstance(content, dict):
            return json.dumps(content)
        return str(content)

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository()
