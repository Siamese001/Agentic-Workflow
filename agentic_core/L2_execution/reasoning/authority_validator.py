"""
Authority validation for prompt assembly.

Enforces the authority hierarchy: S0 > I0 > D0 > C0 > U0
and validates slot ordering constraints.
"""

from typing import Sequence

from .compiled_artifact import AuthorityLevel, AuthoritySlot


class AuthorityValidator:
    """
    Validates authority slot ordering and hierarchy.

    Per taxonomy:
    - Slot order must be: S0 → I0 → D0 → C0 → U0
    - No slot may appear out of order
    - C0/U0 slots cannot carry routing/safety/execution fields
    """

    # Canonical slot order (W3: E0/M0/H0 inserted between C0 and U0).
    # Rationale: exemplars/meta-cognitive/healing slots are informational
    # (lower authority than D0 binding constraints, higher than raw U0 intent)
    # and per Anthropic/OpenAI best practice appear AFTER grounding context
    # but BEFORE the actual user turn.
    SLOT_ORDER = ["S0", "I0", "D0", "C0", "E0", "M0", "H0", "U0"]

    # Authority level mapping for comparison.
    AUTHORITY_RANK = {
        AuthorityLevel.ABSOLUTE: 8,  # S0
        AuthorityLevel.GOVERNED: 7,  # I0
        AuthorityLevel.BINDING: 6,  # D0
        AuthorityLevel.INFO: 5,  # C0
        AuthorityLevel.EXEMPLAR: 4,  # E0
        AuthorityLevel.META_COGNITIVE: 3,  # M0
        AuthorityLevel.HEALING: 2,  # H0
        AuthorityLevel.ZERO: 1,  # U0
    }

    def __init__(self) -> None:
        self.errors: list[str] = []

    def validate_slots(self, slots: Sequence[AuthoritySlot]) -> bool:
        """
        Validate a sequence of authority slots.

        Returns True if valid, False otherwise (errors stored in self.errors).
        """
        self.errors.clear()

        if not slots:
            self.errors.append("No slots provided")
            return False

        # Check for required S0 slot
        s0_slots = [s for s in slots if s.slot_type == "S0"]
        if not s0_slots:
            self.errors.append("Missing required S0 (ABSOLUTE) slot")

        # Check slot ordering
        slot_codes = [s.slot_type.upper() for s in slots]

        # Verify order constraint: slots must appear in SLOT_ORDER sequence
        order_idx = -1
        for code in slot_codes:
            try:
                expected_idx = self.SLOT_ORDER.index(code)
                if expected_idx < order_idx:
                    self.errors.append(
                        f"Slot {code} appears out of order. Expected order: {' -> '.join(self.SLOT_ORDER)}",
                    )
                order_idx = expected_idx
            except ValueError:
                self.errors.append(f"Unknown slot type: {code}")

        # Check for duplicate slot types (only one of each allowed per taxonomy)
        seen_types: set[str] = set()
        for code in slot_codes:
            if code in seen_types:
                self.errors.append(f"Duplicate slot type: {code}")
            seen_types.add(code)

        # Validate individual slot security invariants
        for slot in slots:
            self._validate_slot_invariants(slot)

        return len(self.errors) == 0

    def _validate_slot_invariants(self, slot: AuthoritySlot) -> None:
        """Validate security invariants for individual slots."""
        # Informational slots (C0/U0/E0/M0/H0) cannot carry routing/safety/execution/auth fields.
        if slot.slot_type in ("C0", "U0", "E0", "M0", "H0"):
            forbidden = ["route_mode", "safety_threshold", "execution_tier", "auth_token"]
            for key in forbidden:
                if key in slot.metadata:
                    self.errors.append(f"Slot {slot.slot_type} carries forbidden metadata key: {key}")

    def validate_authority_chain(self, slots: Sequence[AuthoritySlot]) -> bool:
        """
        Validate that authority flows correctly through the chain.

        Higher authority slots should not depend on lower authority slots.
        """
        if not self.validate_slots(slots):
            return False

        # Check authority monotonicity (should decrease S0→I0→D0→C0→U0)
        prev_rank = float("inf")
        for slot in slots:
            rank = self.AUTHORITY_RANK.get(slot.authority_level, 0)
            if rank > prev_rank:
                self.errors.append(
                    f"Authority inversion detected: {slot.slot_type} "
                    f"({slot.authority_level.name}) has higher authority than previous slot",
                )
            prev_rank = rank

        return len(self.errors) == 0

    def get_errors(self) -> list[str]:
        """Return validation errors from last validation."""
        return list(self.errors)

    def assert_valid(self, slots: Sequence[AuthoritySlot]) -> None:
        """Assert that slots are valid, raising detailed error if not."""
        if not self.validate_slots(slots):
            raise AuthorityValidationError(f"Authority validation failed: {'; '.join(self.errors)}")

    @classmethod
    def canonical_order(cls, slots: Sequence[AuthoritySlot]) -> list[AuthoritySlot]:
        """Reorder slots to canonical order (S0,I0,D0,C0,U0)."""
        order_map = {code: idx for idx, code in enumerate(cls.SLOT_ORDER)}
        return sorted(slots, key=lambda s: order_map.get(s.slot_type.upper(), 99))


class AuthorityValidationError(Exception):
    """Raised when authority validation fails."""

    pass
