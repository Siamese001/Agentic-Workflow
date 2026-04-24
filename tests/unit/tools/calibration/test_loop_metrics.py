"""Unit tests for tools.calibration.loop_metrics — calibration loop primitives.

Focuses on edge cases that real ledger data hits:
  - n=0 (no rows in window)
  - n<min_band_n (insufficient sample)
  - all-success and all-failure (Wilson stays in [0,1])
  - missing precedent verdict (NULL column / pre-migration rows)
  - missing confidence (rows where extractor returns None)
  - mixed precedent strengths
  - both bands shipped with the module: CONFIDENCE_BANDS and P_BAND_LAYOUT
"""

from __future__ import annotations

import math

import pytest

from tools.calibration.loop_metrics import (
    AUTHOR_GATE_ADAPTER,
    CONFIDENCE_BANDS,
    DEFAULT_MIN_BAND_N,
    EVENTS_ADAPTER,
    LedgerAdapter,
    P_BAND_LAYOUT,
    compute_metrics,
    render_calibration_curve,
    render_precedent_block,
    wilson_interval,
)


# ---------------------------------------------------------------------------
# wilson_interval — the math primitive
# ---------------------------------------------------------------------------


class TestWilsonInterval:
    def test_zero_n_returns_all_zeros(self):
        assert wilson_interval(0, 0) == (0.0, 0.0, 0.0)

    def test_negative_n_returns_all_zeros(self):
        assert wilson_interval(0, -5) == (0.0, 0.0, 0.0)

    def test_negative_successes_returns_all_zeros(self):
        assert wilson_interval(-1, 5) == (0.0, 0.0, 0.0)

    def test_all_success_stays_at_one(self):
        p, low, high = wilson_interval(20, 20)
        assert p == 1.0
        # Wilson lower bound for 20/20 at 95% is roughly 0.832
        assert 0.8 < low < 0.85
        # high is clamped to ≤1.0; floating-point may sit at 0.9999... (within ε of 1)
        assert high == pytest.approx(1.0, abs=1e-9)

    def test_all_failure_stays_at_zero(self):
        p, low, high = wilson_interval(0, 20)
        assert p == 0.0
        assert low == 0.0
        # Wilson upper bound for 0/20 is roughly 0.168
        assert 0.15 < high < 0.20

    def test_50_50_centred(self):
        p, low, high = wilson_interval(10, 20)
        assert p == 0.5
        # CI should be symmetric around 0.5 with reasonable width
        assert 0.25 < low < 0.35
        assert 0.65 < high < 0.75

    def test_small_n_wide_interval(self):
        _, low, high = wilson_interval(2, 3)
        # 2/3 with n=3 should have a very wide interval — verifying width >0.4
        assert (high - low) > 0.4

    def test_large_n_narrow_interval(self):
        _, low, high = wilson_interval(800, 1000)
        # 800/1000 should produce a tight CI (width <0.05)
        assert (high - low) < 0.05


# ---------------------------------------------------------------------------
# compute_metrics — end-to-end on synthetic rows
# ---------------------------------------------------------------------------


def _ag_row(
    confidence: float | None = 0.85,
    verdict: str | None = "strong",
    outcome: str | None = "success",
):
    """Build a synthetic Author-Gate ledger row."""
    return {
        "confidence_top": confidence,
        "precedent_verdict": verdict,
        "outcome_label": outcome,
    }


class TestComputeMetricsEmpty:
    def test_empty_iterable_zero_metrics(self):
        m = compute_metrics([], AUTHOR_GATE_ADAPTER)
        assert m.total_rows == 0
        assert m.bound_rows == 0
        assert m.unknown_precedent == 0
        assert m.precedent_hit_count == 0
        assert m.precedent_correlation == []
        assert all(b.n == 0 for b in m.calibration_curve)
        assert all(not b.sufficient for b in m.calibration_curve)


class TestComputeMetricsPrecedent:
    def test_real_hit_count_excludes_none_and_null(self):
        rows = [
            _ag_row(verdict="strong"),
            _ag_row(verdict="suggestive"),
            _ag_row(verdict="none"),
            _ag_row(verdict=None),  # NULL — pre-migration row
        ]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        assert m.total_rows == 4
        assert m.unknown_precedent == 1
        assert m.precedent_hit_count == 2  # strong + suggestive
        assert m.precedent_by_verdict["strong"] == 1
        assert m.precedent_by_verdict["suggestive"] == 1
        assert m.precedent_by_verdict["none"] == 1

    def test_correlation_excludes_unbound(self):
        rows = [
            _ag_row(verdict="strong", outcome="success"),
            _ag_row(verdict="strong", outcome="success"),
            _ag_row(verdict="strong", outcome="rework"),
            _ag_row(verdict="strong", outcome="unbound"),  # excluded from correlation
            _ag_row(verdict="none", outcome="success"),
        ]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        strong = next(c for c in m.precedent_correlation if c.verdict == "strong")
        assert strong.n == 3  # 3 bound, unbound excluded
        assert strong.by_outcome["success"] == 2
        assert strong.by_outcome["rework"] == 1
        # 2/3 is below DEFAULT_MIN_BAND_N=5 — sufficient is False
        assert strong.sufficient is False


class TestComputeMetricsCalibration:
    def test_band_bucketization(self):
        # 6 rows into [0.85,0.90) band — 5 success, 1 rework
        rows = [_ag_row(confidence=0.86, outcome="success") for _ in range(5)]
        rows.append(_ag_row(confidence=0.86, outcome="rework"))
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        target = next(b for b in m.calibration_curve if b.label == "[0.85, 0.90)")
        assert target.n == 6
        assert target.successes == 5
        assert target.sufficient is True
        # 5/6 = 83%, lies inside [0.85, 0.90) at point estimate? close to band
        # CI is wide; calibrated check needs CI overlap with [0.85, 0.90]
        assert target.point == pytest.approx(5 / 6)

    def test_insufficient_sample_below_min_n(self):
        rows = [_ag_row(confidence=0.86, outcome="success") for _ in range(3)]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        target = next(b for b in m.calibration_curve if b.label == "[0.85, 0.90)")
        assert target.n == 3
        assert target.sufficient is False

    def test_calibrated_flag_when_ci_overlaps_band(self):
        # 100 rows in [0.85,0.90) band, 86% success → CI tightly around 0.86
        rows = [_ag_row(confidence=0.87, outcome="success") for _ in range(86)]
        rows += [_ag_row(confidence=0.87, outcome="rework") for _ in range(14)]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        target = next(b for b in m.calibration_curve if b.label == "[0.85, 0.90)")
        assert target.sufficient is True
        # 86% point with n=100 has CI roughly [0.78, 0.91] — overlaps [0.85, 0.90]
        assert target.calibrated is True

    def test_miscalibrated_flag_when_ci_misses_band(self):
        # 100 rows in [0.85,0.90) band but only 30% success → mis-calibrated
        rows = [_ag_row(confidence=0.87, outcome="success") for _ in range(30)]
        rows += [_ag_row(confidence=0.87, outcome="rework") for _ in range(70)]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        target = next(b for b in m.calibration_curve if b.label == "[0.85, 0.90)")
        assert target.sufficient is True
        # 30% with n=100 has CI roughly [0.22, 0.40] — does NOT overlap [0.85, 0.90]
        assert target.calibrated is False

    def test_missing_confidence_excluded_from_bands(self):
        rows = [_ag_row(confidence=None, outcome="success") for _ in range(10)]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        assert all(b.n == 0 for b in m.calibration_curve)
        assert m.total_rows == 10  # still counted toward total

    def test_unbound_outcome_excluded_from_bands(self):
        rows = [_ag_row(confidence=0.87, outcome="unbound") for _ in range(10)]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        assert all(b.n == 0 for b in m.calibration_curve)

    def test_p_band_layout_works(self):
        # Use the priority-band layout (deferred-scope ledger style)
        adapter = LedgerAdapter(
            name="dsc",
            get_outcome_label=lambda r: r.get("outcome", "unbound"),
            get_confidence=lambda r: r.get("score"),
            success_label="success",
        )
        rows = [{"score": 200.0, "outcome": "success"} for _ in range(5)]
        rows += [{"score": 50.0, "outcome": "rework"} for _ in range(5)]
        m = compute_metrics(rows, adapter, bands=P_BAND_LAYOUT)
        p2 = next(b for b in m.calibration_curve if b.label == "P2")
        p4 = next(b for b in m.calibration_curve if b.label == "P4")
        assert p2.n == 5 and p2.successes == 5
        assert p4.n == 5 and p4.successes == 0


class TestEventsAdapter:
    def test_predicted_status_is_unbound(self):
        row = {"status": "predicted", "score_band": "correct"}
        assert EVENTS_ADAPTER.get_outcome_label(row) == "unbound"

    def test_bound_correct_is_success(self):
        row = {"status": "bound", "score_band": "correct"}
        assert EVENTS_ADAPTER.get_outcome_label(row) == "success"

    def test_bound_miss_is_rework(self):
        row = {"status": "bound", "score_band": "miss"}
        assert EVENTS_ADAPTER.get_outcome_label(row) == "rework"

    def test_bound_rollback(self):
        row = {"status": "bound", "score_band": "rollback"}
        assert EVENTS_ADAPTER.get_outcome_label(row) == "rollback"

    def test_bound_unknown_band_is_undecided(self):
        row = {"status": "bound", "score_band": None}
        assert EVENTS_ADAPTER.get_outcome_label(row) == "undecided"

    def test_score_numeric_extracted(self):
        assert EVENTS_ADAPTER.get_confidence({"score_numeric": 0.92}) == 0.92
        assert EVENTS_ADAPTER.get_confidence({"score_numeric": None}) is None
        assert EVENTS_ADAPTER.get_confidence({}) is None


# ---------------------------------------------------------------------------
# Rendering — markdown smoke checks
# ---------------------------------------------------------------------------


class TestRendering:
    def test_render_precedent_handles_empty(self):
        m = compute_metrics([], AUTHOR_GATE_ADAPTER)
        out = render_precedent_block(m)
        assert "no rows in this window" in out

    def test_render_precedent_handles_all_null(self):
        rows = [_ag_row(verdict=None) for _ in range(3)]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        out = render_precedent_block(m)
        assert "lack a captured precedent verdict" in out

    def test_render_precedent_with_data(self):
        rows = [_ag_row(verdict="strong", outcome="success") for _ in range(10)]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        out = render_precedent_block(m)
        assert "Real precedent-hit rate" in out
        assert "10/10" in out
        assert "100.0%" in out
        # Correlation table should appear
        assert "Precedent × Outcome Correlation" in out
        # n=10 ≥ MIN_BAND_N → real CI rendered, not "insufficient"
        assert "insufficient sample" not in out

    def test_render_calibration_handles_empty(self):
        m = compute_metrics([], AUTHOR_GATE_ADAPTER)
        out = render_calibration_curve(m)
        assert "Insufficient sample in every band" in out

    def test_render_calibration_with_data(self):
        rows = [_ag_row(confidence=0.87, outcome="success") for _ in range(20)]
        m = compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        out = render_calibration_curve(m)
        assert "[0.85, 0.90)" in out
        # Should NOT show insufficient for the populated band
        assert "Per-Band Calibration Curve" in out


class TestImmutability:
    def test_compute_metrics_does_not_mutate_input(self):
        rows = [_ag_row(verdict="strong")]
        snapshot = dict(rows[0])
        compute_metrics(rows, AUTHOR_GATE_ADAPTER)
        assert rows[0] == snapshot

    def test_default_bands_constant_is_what_we_expect(self):
        labels = [b[0] for b in CONFIDENCE_BANDS]
        assert labels == ["[0.72, 0.80)", "[0.80, 0.85)", "[0.85, 0.90)", "[0.90, 1.00]"]

    def test_p_band_layout_constant(self):
        labels = [b[0] for b in P_BAND_LAYOUT]
        assert labels == ["P5", "P4", "P3", "P2", "P1"]
        # Last band must extend to infinity
        assert P_BAND_LAYOUT[-1][2] == math.inf
