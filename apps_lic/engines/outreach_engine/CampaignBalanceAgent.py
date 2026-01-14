from dataclasses import dataclass
"""
CampaignBalanceAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

@dataclass
class CampaignBalanceAgent(HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, OutreachAgent):
    """Ensures campaign elements are balanced."""

    async def execute(self) -> None:
        print(f"   [{self.name}] Checking campaign balance...")

        campaign = self.ctx.current_campaign
        leads = self.ctx.leads
        messages = self.ctx.messages

        balance_issues = []

        # Check lead to message ratio
        if leads and messages:
            ratio = len(leads) / len(messages) if messages else 0
            if ratio > 100:
                balance_issues.append("Too many leads per message template")
            elif ratio < 1:
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

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
