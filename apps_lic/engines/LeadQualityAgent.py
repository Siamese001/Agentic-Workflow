"""
Outreach Engine Agents - Specialized Agents for Campaign Automation

Provides domain-specific agents for outreach campaigns:
- LeadQualityAgent: Validates lead quality
- ContactValidatorAgent: Validates contact information
- MessageComplianceAgent: Ensures message compliance
- RgTemplateOptimizerAgent: Optimizes message templates
- CampaignBalanceAgent: Balances campaign elements
- DeliverabilityAgent: Checks email deliverability
- OutreachTestPilot: Runs validation tests
- CampaignPlannerAgent: Strategic campaign planning
- LicReflectionAgent: Reflects on execution
"""

from .OutreachAgent import OutreachAgent


@dataclass
class LeadQualityAgent(OutreachAgent):
    """
    Validates and scores lead quality.

    Validates:
    - Required fields (company, contact info)
    - Email domain quality
    - Spam indicators
    """

    async def execute(self) -> None:
        """
        Execute lead quality validation.

        Validates all leads for:
        - Required fields presence
        - Contact information completeness
        - Suspicious email domains

        Raises:
            LEAD_QUALITY_ISSUE signal if validation fails
        """
        print(f"   [{self.name}] Analyzing lead quality...")

        leads = self.ctx.leads

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


# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: apps_lic outreach-specific vs apps_rg resume-specific)
# - Intentional variant for application-specific optimization
# - Documented 2026-01-06


# DEPRECATED: Moved to OutreachTestPilotAgent.py (Jan 6, 2026)
# Import for backward compatibility

# OutreachTestPilotDeprecatedAgent extracted to OutreachTestPilotDeprecatedAgent.py (Phase B Task 2)
