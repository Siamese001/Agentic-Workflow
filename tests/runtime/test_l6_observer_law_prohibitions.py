"""ObserverLawValidator — one test per prohibition (W4.P2).

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f
"""
from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.future_run_promotion import ObserverLawReceipt
from agentic_core.L6_system_learning.future_run_promotion.promotion_gauntlet import ObserverLawValidator

PROHIBITIONS = [
    ("x3_emitted", "no_x3_emission"),
    ("cache_write_attempted", "no_cache_write"),
    ("vector_store_write_attempted", "no_vector_store_write"),
    ("l4_write_attempted", "no_l4_write"),
    ("current_run_reroute_attempted", "no_reroute_attempt"),
    ("current_run_reexecute_attempted", "no_reexecute_attempt"),
    ("mutation_attempted", "no_current_run_mutation"),
]


@pytest.mark.parametrize("violation_key,receipt_field", PROHIBITIONS)
def test_observer_law_blocks_each_prohibition(
    violation_key: str,
    receipt_field: str,
) -> None:
    v = ObserverLawValidator()
    outputs = {violation_key: True}
    receipt = v.validate("sess-1", "run-1", outputs)
    assert getattr(receipt, receipt_field) is False
    if violation_key != "mutation_attempted":
        assert receipt.evidence_refs


def test_observer_law_clean_run_all_true() -> None:
    v = ObserverLawValidator()
    receipt = v.validate("sess-2", "run-2", {})
    assert receipt.no_x3_emission is True
    assert receipt.no_cache_write is True
    assert receipt.no_vector_store_write is True
    assert receipt.no_l4_write is True
    assert receipt.no_reroute_attempt is True
    assert receipt.no_reexecute_attempt is True
    assert receipt.no_current_run_mutation is True
    assert not receipt.evidence_refs


def test_observer_law_receipt_is_frozen() -> None:
    from dataclasses import is_dataclass

    assert is_dataclass(ObserverLawReceipt)
    assert ObserverLawReceipt.__dataclass_params__.frozen is True
