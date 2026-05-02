"""Tests for apps_rg.integrations.pool_first_selector."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from apps_rg.integrations.length_budget import LengthBudget
from apps_rg.integrations.pool_first_selector import pool_first_select


@dataclass
class _StubVerdict:
    accepted: bool
    composite: float
    first_failed_gate: str | None = None


@dataclass
class _StubScorer:
    """Deterministic scorer: maps text -> (accepted, composite)."""

    table: dict

    def score_candidate(self, text, **_):
        accepted, composite = self.table.get(text, (False, 0.0))
        return _StubVerdict(accepted=accepted, composite=composite)


def test_pool_first_picks_highest_composite_passing_threshold() -> None:
    scorer = _StubScorer(
        table={
            "seed bullet": (True, 0.86),
            "variant_a": (True, 0.92),
            "variant_b": (True, 0.81),  # below 0.85 threshold
        }
    )
    choice = pool_first_select(
        seed="seed bullet",
        variants=["variant_a", "variant_b"],
        scorer=scorer,  # type: ignore[arg-type]
        budget=None,
        threshold=0.85,
    )
    assert choice is not None
    assert choice.text == "variant_a"


def test_pool_first_returns_none_when_nothing_passes_hard_gates() -> None:
    scorer = _StubScorer(table={"seed": (False, 0.0), "v": (False, 0.0)})
    choice = pool_first_select(
        seed="seed",
        variants=["v"],
        scorer=scorer,  # type: ignore[arg-type]
        budget=None,
    )
    assert choice is None


def test_pool_first_returns_none_when_all_below_threshold() -> None:
    scorer = _StubScorer(
        table={"seed": (True, 0.80), "v": (True, 0.84)}
    )
    choice = pool_first_select(
        seed="seed",
        variants=["v"],
        scorer=scorer,  # type: ignore[arg-type]
        budget=None,
        threshold=0.85,
    )
    assert choice is None


def test_pool_first_dedupes_seed_in_variants() -> None:
    scorer = _StubScorer(table={"seed": (True, 0.90)})
    choice = pool_first_select(
        seed="seed",
        variants=["seed", "seed"],
        scorer=scorer,  # type: ignore[arg-type]
        budget=None,
    )
    # Should only score 'seed' once and return it.
    assert choice is not None
    assert choice.text == "seed"


def test_pool_first_skips_empty_strings() -> None:
    scorer = _StubScorer(table={"a": (True, 0.90)})
    choice = pool_first_select(
        seed="",
        variants=["", "a"],
        scorer=scorer,  # type: ignore[arg-type]
        budget=None,
    )
    assert choice is not None
    assert choice.text == "a"
