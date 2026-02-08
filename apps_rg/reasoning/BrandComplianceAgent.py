"""
BrandComplianceAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
Converted to Facade: 2026-01-31 (Phase 2 Consolidation)
Refactored: 2026-02-08 (Cluster 2 — RGValidationCapability extraction)

Facade/Strategy indirection removed — domain logic now lives directly in
collect_issues() while the validation harness is provided by
RGValidationCapability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_rg.utils.rg_validation_capability import RGValidationCapability
from apps_rg.utils.RGAgentBase import RGAgentBase
from apps_shared.config.config_loader_config import load_agent_config


@dataclass
class BrandComplianceAgent(RGValidationCapability, RGAgentBase):
    """
    Ensures brand voice and professional tone.

    Checks for:
    - Professional language
    - No informal/slang terms
    - Consistent voice (first/third person)
    - No forbidden phrases
    """

    VALIDATION_SIGNAL = "BRAND_VIOLATION"
    VALIDATION_LOG_PREFIX = "Checking brand compliance..."
    VALIDATION_PASS_MESSAGE = "Brand compliant"
    VALIDATION_FAIL_PREFIX = "Brand violations"

    def __post_init__(self) -> None:
        """Initialize brand compliance agent."""
        super().__post_init__()

        # Load configuration from centralized config system
        self._config = load_agent_config("brand_compliance")

        self.FORBIDDEN_PHRASES = self._config.get("forbidden_phrases", [])
        self.POWER_VERBS = self._config.get("power_verbs", [])
        self.compliance_rules = self._config.get("compliance_rules", {})
        self.require_power_verbs = self.compliance_rules.get("require_power_verbs_in_experience", True)
        self.check_forbidden_all_sections = self.compliance_rules.get(
            "check_forbidden_phrases_all_sections",
            True,
        )
        self.case_sensitive = self.compliance_rules.get("case_sensitive_checking", False)

    async def execute(self) -> None:
        """
        Execute brand compliance check via RGValidationCapability harness.

        Validates resume content for:
        - Professional language (no forbidden phrases)
        - Power verbs in experience section
        - Consistent professional tone

        Raises:
            BRAND_VIOLATION signal if issues found
        """
        await self.run_validation()

    async def collect_issues(self) -> list[str]:
        """Collect brand compliance issues from the current resume."""
        resume = getattr(self.ctx, "current_resume", None) if hasattr(self, "ctx") else None

        if not resume:
            return ["No resume to check"]

        issues: list[str] = []

        for section_name, content in resume.items():
            if section_name.startswith("_"):
                continue

            content_str = self.content_to_string(content)
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
                    issues.append("Experience section could use more action verbs")

        return issues

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run, execute, **kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by BrandComplianceAgent."""
        return self.make_heal_result(violation)
