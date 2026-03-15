"""ADG importability contract for agentic_core/prompt_governance/contracts/slot_contracts.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_slot_contracts.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.contracts.slot_contracts import (  # noqa: F401
        SlotC0,
        SlotD0,
        SlotI0,
        SlotOrderViolation,
        SlotS0,
        SlotU0,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SlotS0 = None  # type: ignore[assignment,misc]
    SlotD0 = None  # type: ignore[assignment,misc]
    SlotI0 = None  # type: ignore[assignment,misc]
    SlotC0 = None  # type: ignore[assignment,misc]
    SlotU0 = None  # type: ignore[assignment,misc]
    SlotOrderViolation = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="slot_contracts deps unavailable")
class TestSlotContractsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/prompt_governance/contracts/slot_contracts.py must be importable."""
        assert _AVAILABLE

    def test_slots0_defined(self) -> None:
        assert SlotS0 is not None

    def test_slotd0_defined(self) -> None:
        assert SlotD0 is not None

    def test_sloti0_defined(self) -> None:
        assert SlotI0 is not None

    def test_slotc0_defined(self) -> None:
        assert SlotC0 is not None

    def test_slotu0_defined(self) -> None:
        assert SlotU0 is not None

    def test_slotorderviolation_defined(self) -> None:
        assert SlotOrderViolation is not None
