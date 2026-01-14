from dataclasses import dataclass
"""
ContactValidatorAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

@dataclass
class ContactValidatorAgent(OutreachAgent, MCPHardenedMixin):
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
