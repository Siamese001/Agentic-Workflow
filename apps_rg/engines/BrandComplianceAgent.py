"""
BrandComplianceAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)

Ensures brand voice and professional tone in resume content.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin
from apps_rg.shared.core.agent_base import RGAgentBase


@dataclass
class BrandComplianceAgent(SubatomicTestingMixin, RGAgentBase):
    """
    Ensures brand voice and professional tone.

    Checks for:
    - Professional language
    - No informal/slang terms
    - Consistent voice (first/third person)
    - No forbidden phrases
    """

    FORBIDDEN_PHRASES = [
        "i am",
        "i'm",
        "my name is",  # First person in summary
        "responsible for",  # Weak phrasing
        "duties included",  # Passive
        "helped with",  # Vague
        "worked on",  # Vague
        "etc.",  # Unprofessional
        "stuff",  # Informal
        "things",  # Vague
        "very",  # Weak intensifier
        "really",  # Weak intensifier
    ]

    POWER_VERBS = [
        "achieved",
        "delivered",
        "drove",
        "led",
        "managed",
        "developed",
        "created",
        "implemented",
        "optimized",
        "increased",
        "reduced",
        "improved",
        "launched",
        "designed",
        "built",
    ]

    def __post_init__(self) -> None:
        """Initialize brand compliance agent."""
        super().__post_init__()

    async def execute(self) -> None:
        """
        Execute brand compliance check.

        Validates resume content for:
        - Professional language (no forbidden phrases)
        - Power verbs in experience section
        - Consistent professional tone

        Raises:
            BRAND_VIOLATION signal if issues found
        """
        self.log("Checking brand compliance...")

        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume to check")
            self.add_signal("BRAND_VIOLATION")
            return

        issues: list[str] = []
        suggestions: list[str] = []

        for section_name, content in resume.items():
            if section_name.startswith("_"):
                continue

            content_str = self._to_string(content).lower()

            # Check forbidden phrases
            for phrase in self.FORBIDDEN_PHRASES:
                if phrase in content_str:
                    issues.append(f"Forbidden phrase '{phrase}' in {section_name}")

            # Check for power verbs in experience
            if section_name == "experience":
                has_power_verb = any(verb in content_str for verb in self.POWER_VERBS)
                if not has_power_verb:
                    suggestions.append("Experience section could use more action verbs")

        if issues:
            self.record_fail(
                f"Brand violations: {len(issues)}",
                data={"issues": issues, "suggestions": suggestions},
            )
            self.add_signal("BRAND_VIOLATION")
        else:
            self.record_pass("Brand compliant", data={"suggestions": suggestions})
            self.remove_signal("BRAND_VIOLATION")

    def _to_string(self, content: Any) -> str:
        """
        Convert content to string for analysis.

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
