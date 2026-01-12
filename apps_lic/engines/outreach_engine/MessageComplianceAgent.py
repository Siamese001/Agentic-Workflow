"""
MessageComplianceAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

class MessageComplianceAgent(OutreachAgent, MCPHardenedMixin):
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
