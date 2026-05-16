"""UNKNOWN / NOT_APPLICABLE rules via structured X1CheckoutResult."""

from __future__ import annotations

import pytest

from agentic_core.runtime.contracts.x1_checkout_result import (
    X1CheckoutResult,
    X1Item,
    X1Verdict,
)


def test_unknown_slot_not_overall_pass() -> None:
    checkout = X1CheckoutResult(
        x1a_todays_rules=X1Item(gate_id="X1A", verdict=X1Verdict.PASS),
        x1b_answered_it=X1Item(gate_id="X1B", verdict=X1Verdict.PASS),
        x1c_safe_to_leave=X1Item(gate_id="X1C", verdict=X1Verdict.PASS),
        x1d_answer_good=X1Item(
            gate_id="X1D",
            verdict=X1Verdict.UNKNOWN,
            decisive_reason="Test",
            unknown_reason="Cannot decide",
        ),
    )
    assert not checkout.is_overall_pass()


def test_not_applicable_requires_reason_constructor_guard() -> None:
    with pytest.raises(ValueError, match="NOT_APPLICABLE requires"):
        X1Item(gate_id="X1D", verdict=X1Verdict.NOT_APPLICABLE, not_applicable_reason="")
