"""Unit tests for tools.priority.deferred_scope_scorer — ADR-031 v2 extension.

Covers two critical properties:
  1. Back-compat: v2 defaults produce the SAME score as v1 for all legacy inputs.
  2. New signals each move the score in the documented direction with the
     documented magnitude.
"""

from __future__ import annotations

import math

import pytest

from tools.priority.deferred_scope_scorer import (
    COMPLEXITY_PENALTY,
    ITEM_CLASS_MULTIPLIERS,
    REVERSIBILITY_BOOSTS,
    ScoreResult,
    score_deferred_scope,
)

# ---------------------------------------------------------------------------
# Back-compat invariant: v2 defaults = v1 behavior
# ---------------------------------------------------------------------------


def _v1_expected(layer_mult: float, fan_in: int, surface_boost: float, gap: float) -> float:
    return round(gap * layer_mult * (1.0 + math.log10(1.0 + fan_in)) * surface_boost, 2)


class TestBackCompat:
    """All legacy 4-arg calls must be bit-identical to pre-ADR-031 scoring."""

    @pytest.mark.parametrize(
        "layer,fan_in,surface,gap,expected",
        [
            ("L5", 12, "Security", 85.4, _v1_expected(2.0, 12, 1.5, 85.4)),
            ("L0", 50, "Write", 100.0, _v1_expected(2.0, 50, 1.4, 100.0)),
            ("L1", 0, "None", 99.7, _v1_expected(1.0, 0, 1.0, 99.7)),
            ("L6", 3, "Observability", 60.0, _v1_expected(0.75, 3, 1.1, 60.0)),
        ],
    )
    def test_legacy_formula_preserved(self, layer, fan_in, surface, gap, expected):
        r = score_deferred_scope(layer=layer, fan_in=fan_in, surface=surface, coverage_gap_pct=gap)
        assert r.impact_score == expected, (
            f"v2 defaults drifted from v1 for ({layer},{fan_in},{surface},{gap}): "
            f"got {r.impact_score}, expected {expected}"
        )

    def test_all_v2_defaults_are_neutral(self):
        r = score_deferred_scope(layer="L5", fan_in=12, surface="Security", coverage_gap_pct=85.4)
        assert r.prod_factor == 1.0
        assert r.trajectory_factor == 1.0
        assert r.reversibility_boost == 1.0
        assert r.item_class_multiplier == 1.0
        assert r.complexity_penalty == 1.0


# ---------------------------------------------------------------------------
# New signal behavior
# ---------------------------------------------------------------------------


BASELINE = dict(layer="L_TOOLS", fan_in=3, surface="Security", coverage_gap_pct=60.0)


def _baseline_score() -> float:
    return score_deferred_scope(**BASELINE).impact_score


class TestProdInvocations:
    def test_zero_is_neutral(self):
        r = score_deferred_scope(**BASELINE, prod_invocations=0)
        assert r.impact_score == _baseline_score()
        assert r.prod_factor == 1.0

    def test_high_invocations_promote(self):
        """SC-1 worked example: fan_in=3 kept, but high prod traffic should promote P3->P2."""
        baseline = score_deferred_scope(**BASELINE)
        hot = score_deferred_scope(**BASELINE, prod_invocations=5000)
        assert hot.impact_score > baseline.impact_score
        # 1 + log10(5001) ~ 4.699
        assert hot.prod_factor == pytest.approx(1.0 + math.log10(5001), rel=1e-3)

    def test_negative_clamps_to_zero(self):
        r = score_deferred_scope(**BASELINE, prod_invocations=-999)
        assert r.prod_factor == 1.0


class TestTrajectoryDefectRate:
    def test_zero_is_neutral(self):
        r = score_deferred_scope(**BASELINE, trajectory_defect_rate=0.0)
        assert r.trajectory_factor == 1.0

    def test_full_defect_doubles_factor(self):
        r = score_deferred_scope(**BASELINE, trajectory_defect_rate=1.0)
        assert r.trajectory_factor == 2.0

    def test_clamped_above_one(self):
        r = score_deferred_scope(**BASELINE, trajectory_defect_rate=99.0)
        assert r.trajectory_factor == 2.0

    def test_clamped_below_zero(self):
        r = score_deferred_scope(**BASELINE, trajectory_defect_rate=-0.5)
        assert r.trajectory_factor == 1.0


class TestReversibility:
    @pytest.mark.parametrize("value,expected", [("read", 1.0), ("action", 1.3), ("write", 1.5)])
    def test_canonical_values(self, value, expected):
        r = score_deferred_scope(**BASELINE, reversibility=value)
        assert r.reversibility_boost == expected

    def test_unknown_defaults_to_neutral(self):
        r = score_deferred_scope(**BASELINE, reversibility="quantum-entangled")
        assert r.reversibility_boost == 1.0

    def test_case_insensitive(self):
        r = score_deferred_scope(**BASELINE, reversibility="WRITE")
        assert r.reversibility_boost == REVERSIBILITY_BOOSTS["write"]


class TestItemClass:
    def test_regression_beats_capability(self):
        cap = score_deferred_scope(**BASELINE, item_class="capability")
        reg = score_deferred_scope(**BASELINE, item_class="regression")
        assert reg.impact_score > cap.impact_score
        # impact_score is rounded to 2 decimals, so use absolute tolerance.
        assert reg.impact_score == pytest.approx(cap.impact_score * 1.5, abs=0.01)

    def test_unknown_defaults_to_capability(self):
        r = score_deferred_scope(**BASELINE, item_class="fantasy")
        assert r.item_class_multiplier == ITEM_CLASS_MULTIPLIERS["capability"]


class TestComplexityPenalty:
    def test_flag_on_reduces_score(self):
        plain = score_deferred_scope(**BASELINE)
        penalized = score_deferred_scope(**BASELINE, adds_complexity=True)
        assert penalized.impact_score < plain.impact_score
        assert penalized.complexity_penalty == COMPLEXITY_PENALTY
        # impact_score is rounded to 2 decimals, so use absolute tolerance.
        assert penalized.impact_score == pytest.approx(plain.impact_score * COMPLEXITY_PENALTY, abs=0.01)

    def test_flag_off_is_neutral(self):
        r = score_deferred_scope(**BASELINE, adds_complexity=False)
        assert r.complexity_penalty == 1.0


# ---------------------------------------------------------------------------
# Worked example from ADR-031 §Illustration: SC-1 promotion
# ---------------------------------------------------------------------------


class TestADR031WorkedExample:
    """SC-1 audit->enforce promotion: today P3, should become P2 under v2 with
    realistic operational signals."""

    def test_sc1_today_is_p3(self):
        r = score_deferred_scope(layer="L_TOOLS", fan_in=3, surface="Security", coverage_gap_pct=60.0)
        assert r.band == "P3"

    def test_sc1_modest_signals_promote_to_p2(self):
        """Low prod traffic (5 invocations) + low defect rate is enough to promote to P2."""
        r = score_deferred_scope(
            layer="L_TOOLS",
            fan_in=3,
            surface="Security",
            coverage_gap_pct=60.0,
            prod_invocations=5,
            trajectory_defect_rate=0.02,
            reversibility="read",
            item_class="capability",
        )
        assert r.band == "P2", f"expected P2, got {r.band} impact={r.impact_score}"

    def test_sc1_heavy_signals_promote_to_p1(self):
        """Heavy prod traffic + regression + side-effect path correctly lands in P1.

        Demonstrates the scorer rewards operationally severe items even when
        structural fan-in is modest."""
        r = score_deferred_scope(
            layer="L_TOOLS",
            fan_in=3,
            surface="Security",
            coverage_gap_pct=60.0,
            prod_invocations=5000,
            trajectory_defect_rate=0.05,
            reversibility="action",
            item_class="regression",
        )
        assert r.band == "P1", f"expected P1, got {r.band} impact={r.impact_score}"


# ---------------------------------------------------------------------------
# ScoreResult shape stability
# ---------------------------------------------------------------------------


def test_score_result_is_frozen_dataclass():
    r = score_deferred_scope(**BASELINE)
    assert isinstance(r, ScoreResult)
    with pytest.raises((AttributeError, TypeError)):
        r.band = "P1"  # type: ignore[misc]


def test_all_fields_present():
    r = score_deferred_scope(**BASELINE)
    expected_fields = {
        "band",
        "impact_score",
        "layer_multiplier",
        "surface_boost",
        "fan_in_factor",
        "prod_factor",
        "trajectory_factor",
        "reversibility_boost",
        "item_class_multiplier",
        "complexity_penalty",
    }
    assert set(r.__dataclass_fields__.keys()) == expected_fields
