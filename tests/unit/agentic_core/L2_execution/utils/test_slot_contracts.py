"""Test SlotContracts functionality - 10-slot taxonomy validation."""

from __future__ import annotations

import pytest

pytest.importorskip(
    "agentic_core.prompt_governance.contracts.slot_contracts",
    reason="slot_contracts tests require prompt governance runtime modules",
)


@pytest.mark.unit
class TestSlotContracts:
    """Test 10-slot taxonomy dataclasses and validation."""

    def test_slot_order_defined(self):
        """Test SLOT_ORDER has all 10 slots in correct order."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

        assert SLOT_ORDER == ("S0", "D0", "M0", "I0", "E0", "C0", "Y0", "U0", "H0", "R0")

    def test_all_slot_dataclasses_exist(self):
        """Test all 10 slot dataclasses are importable and frozen."""
        from dataclasses import is_dataclass

        from agentic_core.prompt_governance.contracts.slot_contracts import (
            SlotC0,
            SlotD0,
            SlotE0,
            SlotH0,
            SlotI0,
            SlotM0,
            SlotR0,
            SlotS0,
            SlotU0,
            SlotY0,
        )

        slots = [SlotS0, SlotD0, SlotM0, SlotI0, SlotE0, SlotC0, SlotY0, SlotU0, SlotH0, SlotR0]
        for slot_class in slots:
            assert is_dataclass(slot_class)
            assert slot_class.__dataclass_params__.frozen

    def test_slot_s0_creation(self):
        """Test SlotS0 creation with content."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SlotS0

        slot = SlotS0(content="system state")
        assert slot.content == "system state"

    def test_slot_d0_creation_with_authority(self):
        """Test SlotD0 requires authority parameter."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SlotD0

        slot = SlotD0(content="directives", authority="BINDING")
        assert slot.content == "directives"
        assert slot.authority == "BINDING"

    def test_slot_e0_creation(self):
        """Test SlotE0 (exemplars) creation."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SlotE0

        slot = SlotE0(content="golden context example")
        assert slot.content == "golden context example"

    def test_slot_h0_requires_reentry_default(self):
        """Test SlotH0 has requires_reentry=True default."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SlotH0

        slot = SlotH0(content="healing proposal")
        assert slot.content == "healing proposal"
        assert slot.requires_reentry is True

    def test_slot_h0_requires_reentry_override(self):
        """Test SlotH0 allows requires_reentry override."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SlotH0

        slot = SlotH0(content="healing proposal", requires_reentry=False)
        assert slot.requires_reentry is False

    def test_slot_c0_accepts_dict_content(self):
        """Test SlotC0 accepts dict content."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SlotC0

        slot = SlotC0(content={"key": "value", "nested": {"a": 1}})
        assert slot.content == {"key": "value", "nested": {"a": 1}}

    def test_validate_slot_order_valid(self):
        """Test validate_slot_order passes for valid slot order."""
        from agentic_core.prompt_governance.contracts.slot_contracts import validate_slot_order

        prompt = "<SLOT_S0></SLOT_S0><SLOT_D0></SLOT_D0><SLOT_M0></SLOT_M0><SLOT_I0></SLOT_I0><SLOT_E0></SLOT_E0><SLOT_C0></SLOT_C0><SLOT_Y0></SLOT_Y0><SLOT_U0></SLOT_U0><SLOT_H0></SLOT_H0><SLOT_R0></SLOT_R0>"
        validate_slot_order(prompt)  # Should not raise

    def test_validate_slot_order_missing_slot(self):
        """Test validate_slot_order raises for missing slot."""
        from agentic_core.prompt_governance.contracts.slot_contracts import (
            SlotOrderViolation,
            validate_slot_order,
        )

        prompt = "<SLOT_S0></SLOT_S0><SLOT_D0></SLOT_D0>"  # Missing M0-R0
        with pytest.raises(SlotOrderViolation) as exc_info:
            validate_slot_order(prompt)
        assert "SLOT_MISSING" in str(exc_info.value)

    def test_validate_slot_order_misordered(self):
        """Test validate_slot_order raises for misordered slots."""
        from agentic_core.prompt_governance.contracts.slot_contracts import (
            SlotOrderViolation,
            validate_slot_order,
        )

        # Include all slots but D0 before S0 (misordered)
        prompt = "<SLOT_D0></SLOT_D0><SLOT_S0></SLOT_S0><SLOT_M0></SLOT_M0><SLOT_I0></SLOT_I0><SLOT_E0></SLOT_E0><SLOT_C0></SLOT_C0><SLOT_Y0></SLOT_Y0><SLOT_U0></SLOT_U0><SLOT_H0></SLOT_H0><SLOT_R0></SLOT_R0>"
        with pytest.raises(SlotOrderViolation) as exc_info:
            validate_slot_order(prompt)
        assert "SLOT_ORDER_VIOLATED" in str(exc_info.value)

    def test_slotorder_exception_is_exception(self):
        """Test SlotOrderViolation is an Exception."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SlotOrderViolation

        assert issubclass(SlotOrderViolation, Exception)
        exc = SlotOrderViolation("test message")
        assert str(exc) == "test message"
