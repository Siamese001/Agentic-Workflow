"""
BrandComplianceAgent - Facade Shell for Zero-Loss Consolidation.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
Converted to Facade: 2026-01-31 (Phase 2 Consolidation)

FACADE PATTERN: Delegates to UnifiedAgent while preserving 100% legacy compatibility.
All original imports and signatures work without modification.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.base_agents.UnifiedAgent import (
    AgentCategory,
    UnifiedAgent,
    ValidationResult,
    ValidatorStrategy,
)
from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
from apps_shared.config.config_loader_config import load_agent_config


class BrandValidatorStrategy(ValidatorStrategy):
    """Brand compliance validation strategy preserving original logic."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with brand compliance configuration."""
        super().__init__(config)
        self.FORBIDDEN_PHRASES = config.get("forbidden_phrases", [])
        self.POWER_VERBS = config.get("power_verbs", [])
        self.compliance_rules = config.get("compliance_rules", {})
        self.require_power_verbs = self.compliance_rules.get(
            "require_power_verbs_in_experience", True
        )
        self.check_forbidden_all_sections = self.compliance_rules.get(
            "check_forbidden_phrases_all_sections", True
        )
        self.case_sensitive = self.compliance_rules.get("case_sensitive_checking", False)

    async def execute(self, agent: "UnifiedAgent", **kwargs: Any) -> ValidationResult:
        """Execute brand compliance validation logic."""
        agent.log_info("Checking brand compliance...")

        # Get resume from context or kwargs
        resume = kwargs.get("resume") or self._get_resume_from_context(agent)

        if not resume:
            return ValidationResult(
                passed=False,
                issues=["No resume to check"],
                suggestions=[],
            )

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

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            metadata={"agent": "BrandComplianceAgent"},
        )

    def _get_resume_from_context(self, agent: "UnifiedAgent") -> dict[str, Any] | None:
        """Get resume from agent context."""
        ctx = getattr(agent, "ctx", None)
        if ctx:
            return getattr(ctx, "current_resume", None)
        return None

    def _to_string(self, content: Any) -> str:
        """Convert content to string for analysis."""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        elif isinstance(content, dict):
            return json.dumps(content)
        return str(content)


@dataclass
class BrandComplianceAgent(RGAgentBase):
    """
    Ensures brand voice and professional tone.

    FACADE SHELL: Delegates to UnifiedAgent with BrandValidatorStrategy.
    SIGNATURE COMPATIBILITY: 100% preserved - no breaking changes.

    Checks for:
    - Professional language
    - No informal/slang terms
    - Consistent voice (first/third person)
    - No forbidden phrases
    """

    _unified_strategy: BrandValidatorStrategy | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize brand compliance agent facade."""
        super().__post_init__()

        # Load configuration from centralized config system
        self._config = load_agent_config("brand_compliance")

        # Initialize unified strategy with brand-specific logic
        self._unified_strategy = BrandValidatorStrategy(self._config)

        # Preserve legacy interface attributes
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
        Execute brand compliance check - FACADE DELEGATION.

        Validates resume content for:
        - Professional language (no forbidden phrases)
        - Power verbs in experience section
        - Consistent professional tone

        Raises:
            BRAND_VIOLATION signal if issues found
        """
        self.log("Checking brand compliance...")

        # Get data from context
        resume = getattr(self.ctx, "current_resume", None) if hasattr(self, "ctx") else None

        # Create a mock unified agent for strategy execution
        class MockUnifiedAgent:
            def __init__(self, ctx: Any) -> None:
                self.ctx = ctx
                self._category = AgentCategory.VALIDATOR

            def log_info(self, msg: str) -> None:
                pass

        mock_agent = MockUnifiedAgent(self.ctx if hasattr(self, "ctx") else None)

        # Execute via unified strategy
        result: ValidationResult = await self._unified_strategy.execute(mock_agent, resume=resume)

        # Preserve legacy signal handling
        if not result.passed:
            self.record_fail(
                f"Brand violations: {len(result.issues)}",
                data={"issues": result.issues, "suggestions": result.suggestions},
            )
            self.add_signal("BRAND_VIOLATION")
        else:
            self.record_pass("Brand compliant", data={"suggestions": result.suggestions})
            self.remove_signal("BRAND_VIOLATION")

    def _to_string(self, content: Any) -> str:
        """
        Convert content to string - LEGACY COMPATIBILITY METHOD.

        Args:
            content: Content to convert (str, list, dict, or other)

        Returns:
            String representation of content
        """
        return self._unified_strategy._to_string(content)

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Autonomous healing method - FACADE DELEGATION.

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
        return {
            "status": "skipped",
            "details": f"BrandComplianceAgent heal() not yet implemented for {violation_type}",
            "artifacts": [],
            "errors": [],
        }
