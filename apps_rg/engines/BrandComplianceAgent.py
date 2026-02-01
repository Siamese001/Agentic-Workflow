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

from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
from apps_shared.config.config_loader import load_agent_config


@dataclass
class BrandComplianceAgent(RGAgentBase):
    """
    Ensures brand voice and professional tone.

    Checks for:
    - Professional language
    - No informal/slang terms
    - Consistent voice (first/third person)
    - No forbidden phrases
    """

    def __post_init__(self) -> None:
        """Initialize brand compliance agent."""
        super().__post_init__()

        # Load configuration from centralized config system
        self._config = load_agent_config("brand_compliance")

        # Extract configuration values
        self.FORBIDDEN_PHRASES = self._config.get("forbidden_phrases", [])
        self.POWER_VERBS = self._config.get("power_verbs", [])
        self.compliance_rules = self._config.get("compliance_rules", {})
        self.require_power_verbs = self.compliance_rules.get(
            "require_power_verbs_in_experience", True
        )
        self.check_forbidden_all_sections = self.compliance_rules.get(
            "check_forbidden_phrases_all_sections", True
        )
        self.case_sensitive = self.compliance_rules.get("case_sensitive_checking", False)

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

            content_str = self._to_string(content)
            if not self.case_sensitive:
                content_str = content_str.lower()

            # Check forbidden phrases
            for phrase in self.FORBIDDEN_PHRASES:
                check_phrase = phrase if self.case_sensitive else phrase.lower()
                if check_phrase in content_str:
                    issues.append(f"Forbidden phrase '{phrase}' in {section_name}")

            # Check for power verbs in experience
            if section_name == "experience" and self.require_power_verbs:
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

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by BrandComplianceAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": (
                    f"BrandComplianceAgent heal() not yet implemented for {violation_type}"
                ),
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"BrandComplianceAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
