"""
CampaignBalanceAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_lic.shared.core.agent_base import LICAgentBase

from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class CampaignBalanceAgent(SubatomicTestingMixin, LICAgentBase):
    """
    Sovereign Campaign Balance Validator.

    Validates:
    - Lead to message template ratio
    - Campaign has required elements (name, goal)
    - Proper campaign structure
    """

    # Sovereign Configuration
    balance_thresholds: dict[str, Any] = field(
        default_factory=lambda: {"max_leads_per_message": 100, "min_leads_per_message": 1}
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
        print(f"   [{self.name}] Checking campaign balance...")

        campaign = self.ctx.current_campaign
        leads = self.ctx.leads
        messages = self.ctx.messages

        balance_issues = []

        # Check lead to message ratio using sovereign thresholds
        if leads and messages:
            ratio = len(leads) / len(messages) if messages else 0
            max_ratio = self.balance_thresholds["max_leads_per_message"]
            min_ratio = self.balance_thresholds["min_leads_per_message"]

            if ratio > max_ratio:
                balance_issues.append("Too many leads per message template")
            elif ratio < min_ratio:
                balance_issues.append("More templates than leads")

        # Check campaign has required elements
        if not campaign.get("name"):
            balance_issues.append("Campaign Missing name")

        if not campaign.get("goal"):
            balance_issues.append("Campaign Missing goal")

        if balance_issues:
            self.add_signal("CAMPAIGN_BALANCE_ISSUE")
            self.record_result(False, f"Balance issues: {len(balance_issues)}")
            print(f"   [{self.name}] ❌ Balance issues: {len(balance_issues)}")
        else:
            self.record_result(True, "Campaign balanced")
            print(f"   [{self.name}] ✅ Campaign balanced")

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
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
