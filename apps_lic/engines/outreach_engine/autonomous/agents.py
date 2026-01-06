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

from .outreach_base import OutreachAgent


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


class ContactValidatorAgent(OutreachAgent):
    """Validates contact information."""

    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    async def execute(self) -> None:
        print(f"   [{self.name}] Validating contacts...")

        contacts = self.ctx.contacts

        if not contacts:
            print(f"   [{self.name}] ⚠️ No contacts to validate")
            self.record_result(True, "No contacts to validate")
            return

        invalid_contacts = []

        for i, contact in enumerate(contacts):
            email = contact.get("email", "")

            if not email:
                invalid_contacts.append(f"Contact {i}: Missing email")
            elif not self.EMAIL_PATTERN.match(email):
                invalid_contacts.append(f"Contact {i}: Invalid email format")

        if invalid_contacts:
            self.add_signal("CONTACT_VALIDATION_FAILED")
            self.record_result(False, f"Invalid contacts: {len(invalid_contacts)}")
            print(f"   [{self.name}] ❌ Invalid contacts: {len(invalid_contacts)}")
        else:
            self.record_result(True, "All contacts validated")
            print(f"   [{self.name}] ✅ Contacts validated")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class MessageComplianceAgent(OutreachAgent):
    """Ensures message compliance with regulations and best practices."""

    FORBIDDEN_WORDS = [
        "guaranteed", "free money", "act now", "limited time",
        "winner", "congratulations", "urgent", "click here",
    ]

    async def execute(self) -> None:
        print(f"   [{self.name}] Checking message compliance...")

        messages = self.ctx.messages

        if not messages:
            print(f"   [{self.name}] ⚠️ No messages to check")
            self.record_result(True, "No messages to check")
            return

        compliance_issues = []

        for i, message in enumerate(messages):
            content = message.get("content", "").lower()
            subject = message.get("subject", "").lower()

            # Check for forbidden words
            for word in self.FORBIDDEN_WORDS:
                if word in content or word in subject:
                    compliance_issues.append(f"Message {i}: Contains '{word}'")

            # Check for unsubscribe link
            if "unsubscribe" not in content:
                compliance_issues.append(f"Message {i}: Missing unsubscribe link")

            # Check message length
            if len(content) > 5000:
                compliance_issues.append(f"Message {i}: Too long ({len(content)} chars)")

        if compliance_issues:
            self.add_signal("COMPLIANCE_ISSUE")
            self.record_result(False, f"Compliance issues: {len(compliance_issues)}")
            print(f"   [{self.name}] ❌ Compliance issues: {len(compliance_issues)}")
        else:
            self.record_result(True, "All messages compliant")
            print(f"   [{self.name}] ✅ Messages compliant")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: apps_lic outreach-specific vs apps_rg resume-specific)
# - Intentional variant for application-specific optimization
# - Documented 2026-01-06

class TemplateOptimizerAgent(OutreachAgent):
    """Optimizes message templates for engagement."""

    async def execute(self) -> None:
        print(f"   [{self.name}] Optimizing templates...")

        messages = self.ctx.messages

        if not messages:
            self.record_result(True, "No templates to optimize")
            return

        optimizations = []

        for i, message in enumerate(messages):
            content = message.get("content", "")
            subject = message.get("subject", "")

            # Check subject line length
            if len(subject) > 60:
                optimizations.append(f"Message {i}: Subject too long")
            elif len(subject) < 10:
                optimizations.append(f"Message {i}: Subject too short")

            # Check personalization
            if "{name}" not in content and "{company}" not in content:
                optimizations.append(f"Message {i}: Missing personalization")

            # Check call to action
            cta_words = ["schedule", "call", "meet", "discuss", "connect"]
            has_cta = any(word in content.lower() for word in cta_words)
            if not has_cta:
                optimizations.append(f"Message {i}: Missing call to action")

        if optimizations:
            self.add_signal("TEMPLATE_NEEDS_OPTIMIZATION")
            self.record_result(False, f"Optimizations needed: {len(optimizations)}")
            print(f"   [{self.name}] ⚠️ Optimizations needed: {len(optimizations)}")
        else:
            self.record_result(True, "Templates optimized")
            print(f"   [{self.name}] ✅ Templates optimized")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


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


class DeliverabilityAgent(OutreachAgent):
    """Checks email deliverability factors."""

    async def execute(self) -> None:
        print(f"   [{self.name}] Checking deliverability...")

        messages = self.ctx.messages

        if not messages:
            self.record_result(True, "No messages to check")
            return

        deliverability_issues = []

        for i, message in enumerate(messages):
            content = message.get("content", "")

            # Check for spam triggers
            spam_triggers = ["$$$", "!!!", "CAPS LOCK", "FREE", "BUY NOW"]
            for trigger in spam_triggers:
                if trigger in content:
                    deliverability_issues.append(f"Message {i}: Spam trigger '{trigger}'")

            # Check link count
            link_count = content.count("http")
            if link_count > 3:
                deliverability_issues.append(f"Message {i}: Too many links ({link_count})")

            # Check image count (placeholder check)
            img_count = content.count("<img")
            if img_count > 2:
                deliverability_issues.append(f"Message {i}: Too many images ({img_count})")

        if deliverability_issues:
            self.add_signal("DELIVERABILITY_ISSUE")
            self.record_result(False, f"Deliverability issues: {len(deliverability_issues)}")
            print(f"   [{self.name}] ❌ Deliverability issues: {len(deliverability_issues)}")
        else:
            self.record_result(True, "Deliverability OK")
            print(f"   [{self.name}] ✅ Deliverability OK")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class OutreachTestPilot(OutreachAgent):
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


class CampaignPlannerAgent(OutreachAgent):
    """Strategic campaign planning agent."""

    async def execute(self) -> None:
        print(f"   [{self.name}] Planning campaign strategy...")

        campaign = self.ctx.current_campaign
        leads = self.ctx.leads

        # Analyze campaign needs
        recommendations = []

        if not campaign.get("schedule"):
            recommendations.append("Add send schedule")

        if not campaign.get("follow_up_sequence"):
            recommendations.append("Add follow-up sequence")

        if len(leads) > 100 and not campaign.get("segmentation"):
            recommendations.append("Add lead segmentation")

        if not campaign.get("tracking"):
            recommendations.append("Enable tracking")

        # Use LLM for advanced planning if available
        if self.ctx.intelligence_enabled and leads:
            prompt = f"""
Analyze this outreach campaign and provide strategic recommendations:

Campaign: {campaign.get('name', 'Unnamed')}
Goal: {campaign.get('goal', 'Not specified')}
Target Company: {self.ctx.target_company}
Lead Count: {len(leads)}

Provide 3 specific recommendations to improve campaign effectiveness.
"""
            llm_response = await self.call_llm(prompt)
            if llm_response:
                recommendations.append(f"LLM Insight: {llm_response[:200]}")

        if recommendations:
            self.ctx.current_campaign["recommendations"] = recommendations

        self.record_result(True, f"Generated {len(recommendations)} recommendations")
        print(f"   [{self.name}] ✅ Strategy planned ({len(recommendations)} recommendations)")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class OutreachReflectionAgent(OutreachAgent):
    """Reflects on execution and suggests improvements."""

    async def execute(self) -> None:
        print(f"   [{self.name}] Reflecting on execution...")

        # Analyze results
        passed_agents = []
        failed_agents = []

        for agent_name, result in self.ctx.results.items():
            if result.get("passed", False):
                passed_agents.append(agent_name)
            else:
                failed_agents.append(agent_name)

        # Analyze signals
        active_signals = list(self.ctx.signals)

        # Determine if more cycles needed
        if active_signals or failed_agents:
            print(f"   [{self.name}] 🔄 More cycles needed (signals: {len(active_signals)})")
        else:
            print(f"   [{self.name}] ✅ Campaign ready for execution")

        self.record_result(True, f"Passed: {len(passed_agents)}, Failed: {len(failed_agents)}")
        print(f"   [{self.name}] ✅ Reflection complete")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
