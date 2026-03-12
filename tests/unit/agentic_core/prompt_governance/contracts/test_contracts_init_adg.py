"""ADG-driven tests for prompt_governance/contracts/__init__.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.prompt_governance.contracts import (
    AirlockViolationError,
    CitationAnchorContract,
    RetrievalContextContract,
    SLOT_ORDER,
    SlotC0,
    SlotD0,
    SlotI0,
    SlotS0,
    SlotU0,
    TelemetryEnvelopeContract,
)


class TestContractsInit:
    def test_airlock_violation_error_is_exception(self):
        assert issubclass(AirlockViolationError, Exception)

    def test_slot_order_is_sequence(self):
        assert hasattr(SLOT_ORDER, "__iter__")
        assert len(list(SLOT_ORDER)) > 0

    def test_slot_classes_importable(self):
        for cls in (SlotC0, SlotD0, SlotI0, SlotS0, SlotU0):
            assert cls is not None

    def test_context_contracts_importable(self):
        for cls in (CitationAnchorContract, RetrievalContextContract, TelemetryEnvelopeContract):
            assert cls is not None
