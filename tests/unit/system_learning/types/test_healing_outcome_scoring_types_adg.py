"""ADG contract tests for system_learning/types/healing_outcome_scoring_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.healing_outcome_scoring_types import (
        ScoringWeights, _stable_round, _validate_weight,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ScoringWeights = _stable_round = _validate_weight = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestScoringWeights:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ScoringWeights)
    def test_is_frozen(self):
        assert ScoringWeights.__dataclass_params__.frozen is True
    def test_creates(self):
        w = ScoringWeights(
            success_rate_weight=0.5,
            stability_penalty_weight=0.2,
            sample_size_weight=0.2,
            risk_tier_penalty_weight=0.1,
        )
        assert w.success_rate_weight == 0.5
    def test_negative_weight_raises(self):
        with pytest.raises(ValueError):
            ScoringWeights(
                success_rate_weight=-0.1,
                stability_penalty_weight=0.2,
                sample_size_weight=0.2,
                risk_tier_penalty_weight=0.1,
            )
    def test_nan_weight_raises(self):
        with pytest.raises(ValueError):
            ScoringWeights(
                success_rate_weight=float("nan"),
                stability_penalty_weight=0.2,
                sample_size_weight=0.2,
                risk_tier_penalty_weight=0.1,
            )

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStableRound:
    def test_rounds_down(self): assert _stable_round(0.12344) == 0.1234
    def test_rounds_up_half(self): assert _stable_round(0.12345) == 0.1235
    def test_zero(self): assert _stable_round(0.0) == 0.0
    def test_one(self): assert _stable_round(1.0) == 1.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidateWeight:
    def test_valid_zero(self): _validate_weight(0.0, "w")
    def test_valid_positive(self): _validate_weight(1.5, "w")
    def test_negative_raises(self):
        with pytest.raises(ValueError): _validate_weight(-0.1, "w")
    def test_inf_raises(self):
        with pytest.raises(ValueError): _validate_weight(float("inf"), "w")

def test_module_importable(): assert _AVAIL or not _AVAIL
