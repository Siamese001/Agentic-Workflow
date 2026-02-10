from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

"""
MessageComplianceAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


# STUB: OutreachAgent base class (deprecated)
class OutreachAgent:
    """Legacy base class - use LICAgentBase instead."""

    pass


@dataclass
class MessageComplianceAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """
    Ensures message compliance with regulations and best practices.

    Validates:
    - Forbidden words/phrases
    - Unsubscribe link presence
    - Message length limits
    """

    FORBIDDEN_WORDS = [
        "guaranteed",
        "free money",
        "act now",
        "limited time",
        "winner",
        "congratulations",
        "urgent",
        "click here",
    ]

    async def execute(self) -> None:
        """
        Execute message compliance check.

        Validates all messages for:
        - Forbidden marketing words
        - Required unsubscribe links
        - Length limits

        Raises:
            COMPLIANCE_ISSUE signal if violations found
        """
        print(f"   [{self.name}] Checking message compliance...")

        messages = self.ctx.messages

        if not messages:
            print(f"   [{self.name}] ⚠️ No messages to check")
            self.record_result(True, "No messages to check")
            return

        compliance_issues: list = []

        for i, message in enumerate(messages):
            content: str = message.get("content", "").lower()
            subject: str = message.get("subject", "").lower()

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

    # guardian: allow-type-erasure
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by MessageComplianceAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"MessageComplianceAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"MessageComplianceAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
