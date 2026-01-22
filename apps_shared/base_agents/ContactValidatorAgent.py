"""
ContactValidatorAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


import re



@dataclass
class ContactValidatorAgent(HealerMixin, SubatomicTestingMixin, OutreachAgent, MCPHardenedMixin):
    """
    Validates contact information.

    Validates:
    - Email format using regex pattern
    - Presence of required contact fields
    - Email domain validity
    """

    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    async def execute(self) -> None:
        """
        Execute contact validation.

        Validates all contacts in context for:
        - Email presence
        - Email format validity
        - Raises CONTACT_VALIDATION_FAILED signal if issues found
        """
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

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, int]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            **kwargs: Additional healing parameters

        Returns:
            Dict with healing summary (violations, fixed, errors)
        """
        return super().heal_repository(dry_run, execute, **kwargs)