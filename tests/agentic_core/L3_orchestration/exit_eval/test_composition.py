"""Tests for composition modes (binary / weighted / hybrid)."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.composition import (
    CompositionMode,
    compose,
)
from agentic_core.L3_orchestration.exit_eval.dimension import (
    DimensionResult,
    GraderClass,
)


def _d(
    name: str,
    score: float,
    *,
    weight: float = 1.0,
    threshold: float = 0.5,
    is_hard_gate: bool = False,
    abstain: bool = False,
) -> DimensionResult:
    return DimensionResult(
        name=name,
        score=score,
        weight=weight,
        threshold=threshold,
        passed=(not abstain) and score >= threshold,
        grader_class=GraderClass.CODE_BASED,
        abstain=abstain,
        is_hard_gate=is_hard_gate,
    )


class TestBinaryComposition:
    def test_all_pass(self) -> None:
        r = compose(
            [_d("a", 1.0), _d("b", 0.8, threshold=0.7)],
            mode=CompositionMode.BINARY,
        )
        assert r.passed
        assert r.aggregate_score is None

    def test_one_fails(self) -> None:
        r = compose(
            [_d("a", 1.0), _d("b", 0.3, threshold=0.7)],
            mode=CompositionMode.BINARY,
        )
        assert not r.passed
        assert "b" in r.hard_gate_failures

    def test_abstain_blocks_pass(self) -> None:
        r = compose(
            [_d("a", 1.0), _d("b", 0.0, abstain=True)],
            mode=CompositionMode.BINARY,
        )
        assert not r.passed


class TestWeightedComposition:
    def test_pass_above_threshold(self) -> None:
        r = compose(
            [
                _d("a", 1.0, weight=0.6),
                _d("b", 0.6, weight=0.4, threshold=0.5),
            ],
            mode=CompositionMode.WEIGHTED,
            aggregate_threshold=0.75,
        )
        # weighted avg = 1.0*0.6 + 0.6*0.4 = 0.84 >= 0.75
        assert r.passed
        assert r.aggregate_score == pytest.approx(0.84, abs=1e-9)

    def test_fail_below_threshold(self) -> None:
        r = compose(
            [_d("a", 0.4, weight=0.5), _d("b", 0.5, weight=0.5)],
            mode=CompositionMode.WEIGHTED,
            aggregate_threshold=0.75,
        )
        assert not r.passed
        assert r.weighted_pass is False

    def test_abstain_blocks_even_when_weighted_passes(self) -> None:
        r = compose(
            [_d("a", 1.0, weight=0.5), _d("b", 1.0, weight=0.5, abstain=True)],
            mode=CompositionMode.WEIGHTED,
            aggregate_threshold=0.5,
        )
        assert not r.passed

    def test_requires_aggregate_threshold(self) -> None:
        with pytest.raises(ValueError, match="aggregate_threshold"):
            compose(
                [_d("a", 1.0)],
                mode=CompositionMode.WEIGHTED,
                aggregate_threshold=None,
            )


class TestHybridComposition:
    def test_hard_fails_denies(self) -> None:
        r = compose(
            [
                _d("hard", 0.0, is_hard_gate=True, threshold=1.0),
                _d("soft", 1.0),
            ],
            mode=CompositionMode.HYBRID,
            aggregate_threshold=0.5,
        )
        assert not r.passed
        assert "hard" in r.hard_gate_failures

    def test_hard_pass_soft_fail(self) -> None:
        r = compose(
            [
                _d("hard", 1.0, is_hard_gate=True, threshold=1.0),
                _d("soft", 0.3, threshold=0.5),
            ],
            mode=CompositionMode.HYBRID,
            aggregate_threshold=0.75,
        )
        # hard ok, weighted soft = 0.3 < 0.75
        assert not r.passed
        assert r.weighted_pass is False

    def test_all_pass(self) -> None:
        r = compose(
            [
                _d("hard", 1.0, is_hard_gate=True, threshold=1.0),
                _d("soft", 0.9, weight=1.0),
            ],
            mode=CompositionMode.HYBRID,
            aggregate_threshold=0.75,
        )
        assert r.passed


def test_empty_results_raises() -> None:
    with pytest.raises(ValueError):
        compose([], mode=CompositionMode.BINARY)
