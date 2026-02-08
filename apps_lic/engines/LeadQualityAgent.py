"""
Lead Quality Specialist - LIC Sovereign Agent for Lead Validation.

Validates lead quality for outreach campaigns.
Hardened for inclusion in HOP-1 / HOP-2 foundations.
"""

from __future__ import annotations

from dataclasses import dataclass

from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from apps_lic.shared.core.LICAgentBase import LICAgentBase


@dataclass
class LeadQualityAgent(SubatomicTestingMixin, LICAgentBase):
    """
    LIC Sovereign Lead Quality Specialist.
    Hardened for inclusion in HOP-1 / HOP-2 foundations.

    Validates:
    - Required fields (company, contact info)
    - Email domain quality
    - Spam indicators
    """

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute lead quality validation.

        Validates all leads for:
        - Required fields presence
        - Contact information completeness
        - Suspicious email domains
        """
        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})

        mission_input = buffer.read("mission_input") or {}
        leads = mission_input.get("leads", [])

        if not leads:
            print(f"   [{self.name}] ⚠️ No leads to analyze")
            self.record_result(True, "No leads to analyze")
            return

        quality_issues: list = []

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

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by LeadQualityAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"LeadQualityAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"LeadQualityAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: apps_lic outreach-specific vs apps_rg resume-specific)
# - Intentional variant for application-specific optimization
# - Documented 2026-01-06


# DEPRECATED: Moved to OutreachTestPilotAgent.py (Jan 6, 2026)
# Import for backward compatibility

# OutreachTestPilotDeprecatedAgent extracted to OutreachTestPilotDeprecatedAgent.py (Phase B Task 2)
