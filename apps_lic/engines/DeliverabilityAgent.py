"""
DeliverabilityAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


@dataclass
class DeliverabilityAgent(SubatomicTestingMixin, OutreachAgent, MCPHardenedMixin):
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
