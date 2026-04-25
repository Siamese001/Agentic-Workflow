"""Unit tests for ``agentic_core.L6_observability.regret_accounting``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` W13.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.regret_accounting import (
    DecisionRegretSample,
    RegretLedger,
    aggregate_regret_by_layer,
    per_decision_regret,
)


def test_per_decision_regret_clamps_at_zero() -> None:
    """If chosen reward >= best alternative, regret = 0."""
    s = per_decision_regret(
        decision_id="d1",
        decision_layer="L0_routing",
        chosen_reward=0.9,
        best_alternative_reward=0.8,
    )
    assert s.regret == 0.0


def test_per_decision_regret_positive_delta() -> None:
    s = per_decision_regret(
        decision_id="d2",
        decision_layer="L3_orchestration",
        chosen_reward=0.4,
        best_alternative_reward=0.9,
    )
    assert s.regret == pytest.approx(0.5)


def test_per_decision_regret_unknown_layer_raises() -> None:
    with pytest.raises(ValueError):
        per_decision_regret(
            decision_id="d",
            decision_layer="L99_invalid",
            chosen_reward=0.5,
            best_alternative_reward=0.8,
        )


def test_aggregate_empty_returns_empty() -> None:
    assert aggregate_regret_by_layer([]) == {}


def test_aggregate_groups_by_layer() -> None:
    samples = [
        DecisionRegretSample("a", "L0_routing", 0.3, 0.9),  # regret 0.6
        DecisionRegretSample("b", "L0_routing", 0.8, 0.8),  # regret 0.0
        DecisionRegretSample("c", "L3_orchestration", 0.2, 0.5),  # regret 0.3
    ]
    agg = aggregate_regret_by_layer(samples)
    assert agg["L0_routing"].n_samples == 2
    assert agg["L0_routing"].sum_regret == pytest.approx(0.6)
    assert agg["L0_routing"].mean_regret == pytest.approx(0.3)
    assert agg["L3_orchestration"].n_samples == 1
    assert agg["L3_orchestration"].sum_regret == pytest.approx(0.3)


def test_layer_regret_summary_zero_division_safe() -> None:
    samples: list[DecisionRegretSample] = []
    agg = aggregate_regret_by_layer(samples)
    assert agg == {}


def test_ledger_records_and_aggregates() -> None:
    ledger = RegretLedger()
    ledger.record(DecisionRegretSample("a", "L0_routing", 0.4, 0.9))
    ledger.record(DecisionRegretSample("b", "L5_safety", 0.5, 0.7))
    ledger.record(DecisionRegretSample("c", "L0_routing", 0.6, 0.8))
    assert ledger.total_regret() == pytest.approx(0.5 + 0.2 + 0.2)
    by_layer = ledger.by_layer()
    assert by_layer["L0_routing"].sum_regret == pytest.approx(0.7)
    assert by_layer["L5_safety"].sum_regret == pytest.approx(0.2)


def test_ledger_top_offenders_descending() -> None:
    ledger = RegretLedger()
    ledger.record(DecisionRegretSample("a", "L0_routing", 0.0, 1.0))  # 1.0
    ledger.record(DecisionRegretSample("b", "L5_safety", 0.5, 0.7))  # 0.2
    ledger.record(DecisionRegretSample("c", "L3_orchestration", 0.0, 0.5))  # 0.5
    top = ledger.top_offenders(k=3)
    assert [s.decision_layer for s in top] == [
        "L0_routing",
        "L3_orchestration",
        "L5_safety",
    ]


def test_ledger_top_offenders_invalid_k_raises() -> None:
    ledger = RegretLedger()
    with pytest.raises(ValueError):
        ledger.top_offenders(k=0)


def test_ledger_reset_clears() -> None:
    ledger = RegretLedger()
    ledger.record(DecisionRegretSample("a", "L0_routing", 0.0, 1.0))
    ledger.reset()
    assert ledger.total_regret() == 0.0
    assert ledger.by_layer() == {}
