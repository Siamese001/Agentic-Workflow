"""
CampaignBalanceAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from apps_lic.utils.lic_engine_validation_capability import LICEngineValidationCapability
from apps_lic.utils.LICAgentBase import LICAgentBase


@dataclass
class CampaignBalanceAgent(LICEngineValidationCapability, SubatomicTestingMixin, LICAgentBase):
    """
    Sovereign Campaign Balance Validator.

    Validates:
    - Lead to message template ratio
    - Campaign has required elements (name, goal)
    - Proper campaign structure
    """

    # LICEngineValidationCapability configuration
    SIGNAL_NAME: ClassVar[str] = "CAMPAIGN_BALANCE_ISSUE"
    VALIDATION_LABEL: ClassVar[str] = "Campaign balanced"

    # Sovereign Configuration
    balance_thresholds: dict[str, Any] = field(
        default_factory=lambda: {"max_leads_per_message": 100, "min_leads_per_message": 1},
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    async def execute(self) -> None:
        """
        Execute campaign balance validation.

        Checks:
        - Lead to message ratio (should be between 1:1 and 100:1)
        - Campaign has name and goal
        - Raises CAMPAIGN_BALANCE_ISSUE signal if issues found
        """
        self.run_validation()

    def _validate(self) -> list[str]:
        """Campaign-specific validation rules."""
        campaign = self.ctx.current_campaign
        leads = self.ctx.leads
        messages = self.ctx.messages

        issues: list[str] = []

        # Check lead to message ratio using sovereign thresholds
        if leads and messages:
            ratio = len(leads) / len(messages) if messages else 0
            max_ratio = self.balance_thresholds["max_leads_per_message"]
            min_ratio = self.balance_thresholds["min_leads_per_message"]

            if ratio > max_ratio:
                issues.append("Too many leads per message template")
            elif ratio < min_ratio:
                issues.append("More templates than leads")

        # Check campaign has required elements
        if not campaign.get("name"):
            issues.append("Campaign Missing name")

        if not campaign.get("goal"):
            issues.append("Campaign Missing goal")

        return issues

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, int]:
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
        """Heal violations detected by CampaignBalanceAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"CampaignBalanceAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"CampaignBalanceAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
