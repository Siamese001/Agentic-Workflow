from __future__ import annotations
"""
Outreach Engine Agents - Specialized Agents for Campaign Automation

Provides domain-specific agents for outreach campaigns:
- LeadQualityAgent: Validates lead quality
- ContactValidatorAgent: Validates contact information
- MessageComplianceAgent: Ensures message compliance
- TemplateOptimizerAgent: Optimizes message templates
- CampaignBalanceAgent: Balances campaign elements
- DeliverabilityAgent: Checks email deliverability
- OutreachTestPilot: Runs validation tests
- CampaignPlannerAgent: Strategic campaign planning
- OutreachReflectionAgent: Reflects on execution
"""

import re

from .OutreachAgent import OutreachAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin


class LeadQualityAgent(OutreachAgent):
    """Validates and scores lead quality."""

    async def execute(self) -> None:
        print(f"   [{self.name}] Analyzing lead quality...")

        leads = self.ctx.leads

        if not leads:
            print(f"   [{self.name}] ⚠️ No leads to analyze")
            self.record_result(True, "No leads to analyze")
            return

        quality_issues = []

        for i, lead in enumerate(leads):
            # Check required fields
            if not lead.get("company"):
                quality_issues.append(f"Lead {i}: Missing company")

            if not lead.get("contact_name") and not lead.get("email"):
                quality_issues.append(f"Lead {i}: Missing contact info")

            # Check for spam indicators
            if lead.get("email", "").endswith(".xyz"):
                quality_issues.append(f"Lead {i}: Suspicious email domain")

        if quality_issues:
            self.add_signal("LEAD_QUALITY_ISSUE")
            self.record_result(False, f"Quality issues: {len(quality_issues)}")
            print(f"   [{self.name}] ❌ Quality issues: {len(quality_issues)}")
        else:
            self.record_result(True, "All leads validated")
            print(f"   [{self.name}] ✅ Lead quality validated")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: apps_lic outreach-specific vs apps_rg resume-specific)
# - Intentional variant for application-specific optimization
# - Documented 2026-01-06


# DEPRECATED: Moved to OutreachTestPilotAgent.py (Jan 6, 2026)
# Import for backward compatibility
from .OutreachTestPilotAgent import OutreachTestPilotAgent as OutreachTestPilot

# Legacy class - use OutreachTestPilotAgent instead
class OutreachTestPilotDeprecatedAgent(OutreachAgent):
    """Runs validation tests on the campaign."""

    async def execute(self) -> None:
        print(f"   [{self.name}] Running validation tests...")

        test_results = []

        # Test 1: Campaign exists
        if self.ctx.current_campaign:
            test_results.append(("campaign_exists", True))
        else:
            test_results.append(("campaign_exists", False))

        # Test 2: Has leads or contacts
        if self.ctx.leads or self.ctx.contacts:
            test_results.append(("has_targets", True))
        else:
            test_results.append(("has_targets", False))

        # Test 3: Has messages
        if self.ctx.messages:
            test_results.append(("has_messages", True))
        else:
            test_results.append(("has_messages", False))

        # Test 4: Budget available
        if self.ctx.budget.check_budget():
            test_results.append(("budget_available", True))
        else:
            test_results.append(("budget_available", False))

        # Test 5: No critical signals
        critical_signals = ["COMPLIANCE_ISSUE", "DELIVERABILITY_ISSUE"]
        has_critical = any(self.ctx.has_signal(s) for s in critical_signals)
        test_results.append(("no_critical_signals", not has_critical))

        # Evaluate results
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)

        if passed == total:
            self.record_result(True, f"All {total} tests passed")
            print(f"   [{self.name}] ✅ All tests passed")
        else:
            failed_tests = [name for name, result in test_results if not result]
            self.add_signal("TEST_FAILURE")
            self.record_result(False, f"Failed: {failed_tests}")
            print(f"   [{self.name}] ❌ Failed tests: {failed_tests}")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
