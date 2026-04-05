"""
Tests for slot ordering and authority validation.
"""

import pytest

from agentic_core.L2_execution.reasoning import (
    AuthorityLevel,
    AuthoritySlot,
    AuthorityValidator,
)


class TestAuthoritySlotOrdering:
    """Test canonical slot order: S0 → I0 → D0 → C0 → U0"""

    def test_canonical_order_s0_i0_d0_c0_u0(self):
        """Test that canonical order produces correct sequence."""
        slots = [
            AuthoritySlot("U0", "user intent", AuthorityLevel.ZERO, "L1"),
            AuthoritySlot("S0", "system rules", AuthorityLevel.ABSOLUTE, "L4"),
            AuthoritySlot("I0", "identity", AuthorityLevel.GOVERNED, "L4"),
            AuthoritySlot("D0", "constraints", AuthorityLevel.BINDING, "L5"),
            AuthoritySlot("C0", "context", AuthorityLevel.INFO, "L1"),
        ]

        ordered = AuthorityValidator.canonical_order(slots)
        codes = [s.slot_type for s in ordered]

        assert codes == ["S0", "I0", "D0", "C0", "U0"]

    def test_s0_must_be_first(self):
        """Test that S0 must be present and first."""
        slots = [
            AuthoritySlot("I0", "identity", AuthorityLevel.GOVERNED, "L4"),
            AuthoritySlot("U0", "user intent", AuthorityLevel.ZERO, "L1"),
        ]

        validator = AuthorityValidator()
        assert not validator.validate_slots(slots)
        assert "Missing required S0" in str(validator.get_errors())

    def test_out_of_order_rejected(self):
        """Test that out-of-order slots are rejected."""
        slots = [
            AuthoritySlot("S0", "system rules", AuthorityLevel.ABSOLUTE, "L4"),
            AuthoritySlot("U0", "user intent", AuthorityLevel.ZERO, "L1"),
            AuthoritySlot("I0", "identity", AuthorityLevel.GOVERNED, "L4"),
        ]

        validator = AuthorityValidator()
        assert not validator.validate_slots(slots)
        errors = validator.get_errors()
        assert any("out of order" in e for e in errors)

    def test_duplicates_rejected(self):
        """Test that duplicate slot types are rejected."""
        slots = [
            AuthoritySlot("S0", "system rules", AuthorityLevel.ABSOLUTE, "L4"),
            AuthoritySlot("S0", "more rules", AuthorityLevel.ABSOLUTE, "L4"),
        ]

        validator = AuthorityValidator()
        assert not validator.validate_slots(slots)
        errors = validator.get_errors()
        assert any("Duplicate" in e for e in errors)


class TestAuthorityLevelValidation:
    """Test authority level hierarchy validation."""

    def test_slot_type_matches_authority_level(self):
        """Test that slot type must match authority level."""
        # This should fail because S0 is ABSOLUTE, not GOVERNED
        with pytest.raises(ValueError):
            AuthoritySlot("S0", "content", AuthorityLevel.GOVERNED, "L4")

    def test_correct_slot_authority_pairs(self):
        """Test all valid slot/authority pairs."""
        pairs = [
            ("S0", AuthorityLevel.ABSOLUTE),
            ("I0", AuthorityLevel.GOVERNED),
            ("D0", AuthorityLevel.BINDING),
            ("C0", AuthorityLevel.INFO),
            ("U0", AuthorityLevel.ZERO),
        ]

        for code, level in pairs:
            slot = AuthoritySlot(code, f"{code} content", level, "L4")
            assert slot.slot_code == code.upper()
            assert slot.authority_level == level


class TestSlotSecurityInvariants:
    """Test security invariants for C0/U0 slots."""

    def test_c0_cannot_carry_route_mode(self):
        """Test that C0 slot cannot carry route_mode metadata."""
        with pytest.raises(ValueError, match="cannot carry route_mode"):
            AuthoritySlot("C0", "context", AuthorityLevel.INFO, "L1", metadata={"route_mode": "fast"})

    def test_c0_cannot_carry_auth_token(self):
        """Test that C0 slot cannot carry auth_token."""
        with pytest.raises(ValueError, match="cannot carry auth_token"):
            AuthoritySlot("C0", "context", AuthorityLevel.INFO, "L1", metadata={"auth_token": "secret"})

    def test_u0_cannot_carry_safety_threshold(self):
        """Test that U0 slot cannot carry safety_threshold."""
        with pytest.raises(ValueError, match="cannot carry safety_threshold"):
            AuthoritySlot(
                "U0", "user intent", AuthorityLevel.ZERO, "L1", metadata={"safety_threshold": "low"}
            )

    def test_s0_can_carry_any_metadata(self):
        """Test that S0 slot can carry routing/safety metadata."""
        slot = AuthoritySlot(
            "S0",
            "system rules",
            AuthorityLevel.ABSOLUTE,
            "L4",
            metadata={"route_mode": "strict", "auth_token": "valid"},
        )
        assert slot.metadata["route_mode"] == "strict"

    def test_i0_can_carry_any_metadata(self):
        """Test that I0 slot can carry routing/safety metadata."""
        slot = AuthoritySlot(
            "I0", "identity", AuthorityLevel.GOVERNED, "L4", metadata={"execution_tier": "high"}
        )
        assert slot.metadata["execution_tier"] == "high"


class TestAuthorityLevelFromCode:
    """Test authority level mapping from slot codes."""

    def test_from_slot_code(self):
        """Test mapping from slot codes to authority levels."""
        assert AuthorityLevel.from_slot_code("S0") == AuthorityLevel.ABSOLUTE
        assert AuthorityLevel.from_slot_code("I0") == AuthorityLevel.GOVERNED
        assert AuthorityLevel.from_slot_code("D0") == AuthorityLevel.BINDING
        assert AuthorityLevel.from_slot_code("C0") == AuthorityLevel.INFO
        assert AuthorityLevel.from_slot_code("U0") == AuthorityLevel.ZERO

    def test_from_slot_code_case_insensitive(self):
        """Test that slot code mapping is case insensitive."""
        assert AuthorityLevel.from_slot_code("s0") == AuthorityLevel.ABSOLUTE
        assert AuthorityLevel.from_slot_code("i0") == AuthorityLevel.GOVERNED
        assert AuthorityLevel.from_slot_code("d0") == AuthorityLevel.BINDING
        assert AuthorityLevel.from_slot_code("c0") == AuthorityLevel.INFO
        assert AuthorityLevel.from_slot_code("u0") == AuthorityLevel.ZERO
