from __future__ import annotations
from dataclasses import dataclass
"""
OutreachTestPilotAgent - Campaign validation testing agent.

Extracted from LeadQualityAgent.py for one-file-per-agent pattern (Jan 6, 2026).
Renamed from OutreachTestPilot for consistent Agent suffix.
"""
from typing import Any, Dict

from .OutreachAgent import OutreachAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin


@dataclass
class OutreachTestPilotAgent(SubatomicTestingMixin, OutreachAgent, MCPHardenedMixin):
    """
    Runs validation tests on the campaign.

    Tests:
    - Campaign exists
    - Has leads or contacts
    - Has messages
    - Budget available
    - No critical signals
    """

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

    def heal_repository(self) -> Dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository()
