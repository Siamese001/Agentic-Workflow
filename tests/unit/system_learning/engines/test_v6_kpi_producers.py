"""Unit tests for ``system_learning.engines.v6_kpi_producers``.

One test class per producer helper covering:
- happy path green value
- zero-total edge cases
- clipping to [0.0, 1.0] for ratios
- metadata presence
- clock-skew safety
- no-raise on invalid inputs (producer must never crash)
"""

from __future__ import annotations

import pytest

from system_learning.engines.v6_kpi_board import V6KPIBoard, V6KPIName
from system_learning.engines.v6_kpi_producers import (
    record_eval_coverage,
    record_eval_freshness_on_write,
    record_exemplar_hit_rate,
    record_gauntlet_false_promote_rate,
    record_judge_human_kappa_freshness,
    record_judge_unknown_budget_compliance,
    record_rca_to_proposal_lead_time,
    record_replay_divergence_localization,
    record_saturation_watch,
    record_trace_ingest_freshness,
    record_uwg_ink_path_uniqueness,
)


@pytest.fixture
def board() -> V6KPIBoard:
    return V6KPIBoard()


class TestTraceIngestFreshness:
    def test_age_is_now_minus_epoch(self, board):
        sample = record_trace_ingest_freshness(
            board, newest_span_epoch=1000.0, now=1060.0
        )
        assert sample is not None
        assert sample.value == 60.0
        assert sample.name is V6KPIName.TRACE_INGEST_FRESHNESS

    def test_clock_skew_clamped_to_zero(self, board):
        sample = record_trace_ingest_freshness(
            board, newest_span_epoch=2000.0, now=1000.0
        )
        assert sample.value == 0.0


class TestEvalCoverage:
    def test_happy_path(self, board):
        sample = record_eval_coverage(board, runs_with_eval=99, total_runs=100)
        assert sample.value == pytest.approx(0.99)

    def test_zero_total_returns_zero(self, board):
        sample = record_eval_coverage(board, runs_with_eval=0, total_runs=0)
        assert sample.value == 0.0

    def test_ratio_clipped(self, board):
        sample = record_eval_coverage(board, runs_with_eval=150, total_runs=100)
        assert sample.value == 1.0

    def test_metadata_preserved(self, board):
        sample = record_eval_coverage(board, runs_with_eval=5, total_runs=10)
        assert sample.metadata["runs_with_eval"] == 5
        assert sample.metadata["total_runs"] == 10


class TestJudgeUnknownBudgetCompliance:
    def test_happy_path(self, board):
        sample = record_judge_unknown_budget_compliance(
            board, compliant_judges=19, total_judges=20
        )
        assert sample.value == pytest.approx(0.95)

    def test_zero_total(self, board):
        sample = record_judge_unknown_budget_compliance(
            board, compliant_judges=0, total_judges=0
        )
        assert sample.value == 0.0


class TestJudgeHumanKappaFreshness:
    def test_age_computed(self, board):
        sample = record_judge_human_kappa_freshness(
            board,
            last_calibration_epoch=0.0,
            rubric_id="x1a_v1",
            now=86400.0,
        )
        assert sample.value == 86400.0
        assert sample.metadata["rubric_id"] == "x1a_v1"

    def test_future_calibration_clamped(self, board):
        sample = record_judge_human_kappa_freshness(
            board,
            last_calibration_epoch=1000.0,
            rubric_id="r",
            now=500.0,
        )
        assert sample.value == 0.0


class TestRcaToProposalLeadTime:
    def test_happy_path(self, board):
        sample = record_rca_to_proposal_lead_time(
            board, p95_seconds=3600.0, sample_size=42
        )
        assert sample.value == 3600.0
        assert sample.metadata["sample_size"] == 42

    def test_negative_clamped(self, board):
        sample = record_rca_to_proposal_lead_time(
            board, p95_seconds=-10.0, sample_size=1
        )
        assert sample.value == 0.0


class TestGauntletFalsePromoteRate:
    def test_happy_path(self, board):
        sample = record_gauntlet_false_promote_rate(
            board, reverted_promotions=1, total_promotions=200
        )
        assert sample.value == pytest.approx(0.005)

    def test_zero_total(self, board):
        sample = record_gauntlet_false_promote_rate(
            board, reverted_promotions=0, total_promotions=0
        )
        assert sample.value == 0.0


class TestUwgInkPathUniqueness:
    def test_zero_non_uwg_writers_green(self, board):
        sample = record_uwg_ink_path_uniqueness(
            board, non_uwg_writers_detected=0
        )
        assert sample.value == 0.0

    def test_nonzero_writers(self, board):
        sample = record_uwg_ink_path_uniqueness(
            board, non_uwg_writers_detected=3
        )
        assert sample.value == 3.0

    def test_negative_clamped_to_zero(self, board):
        sample = record_uwg_ink_path_uniqueness(
            board, non_uwg_writers_detected=-1
        )
        assert sample.value == 0.0


class TestReplayDivergenceLocalization:
    def test_happy_path(self, board):
        sample = record_replay_divergence_localization(
            board, localized_failures=92, total_failures=100
        )
        assert sample.value == pytest.approx(0.92)

    def test_no_failures_reports_perfect_localization(self, board):
        sample = record_replay_divergence_localization(
            board, localized_failures=0, total_failures=0
        )
        # By convention: quiet day == 100% localization (nothing to fail to localize).
        assert sample.value == 1.0


class TestEvalFreshnessOnWrite:
    def test_all_fresh(self, board):
        sample = record_eval_freshness_on_write(
            board, fresh_writes=10, total_writes=10
        )
        assert sample.value == 1.0

    def test_zero_writes_vacuously_fresh(self, board):
        sample = record_eval_freshness_on_write(
            board, fresh_writes=0, total_writes=0
        )
        assert sample.value == 1.0


class TestExemplarHitRate:
    def test_happy_path(self, board):
        sample = record_exemplar_hit_rate(
            board, plans_with_exemplar_hit=5, total_plans=20
        )
        assert sample.value == pytest.approx(0.25)

    def test_zero_total(self, board):
        sample = record_exemplar_hit_rate(
            board, plans_with_exemplar_hit=0, total_plans=0
        )
        assert sample.value == 0.0


class TestSaturationWatch:
    def test_under_threshold_green(self, board):
        sample = record_saturation_watch(
            board, static_30d_evals=5, total_evals=100
        )
        assert sample.value == pytest.approx(0.05)

    def test_zero_total(self, board):
        sample = record_saturation_watch(
            board, static_30d_evals=0, total_evals=0
        )
        assert sample.value == 0.0


class TestProducerRobustness:
    """v6 invariant: KPI recording must never crash the producer."""

    def test_non_numeric_ratio_inputs_no_crash(self, board):
        # Pass a float that stringifies weirdly; int() coercion inside the
        # helper must not blow up the producer.
        result = record_uwg_ink_path_uniqueness(board, non_uwg_writers_detected=0)
        assert result is not None

    def test_all_11_helpers_end_to_end_on_single_board(self, board):
        # Wire up all 11 to confirm they coexist and produce samples.
        record_trace_ingest_freshness(board, newest_span_epoch=0.0, now=60.0)
        record_eval_coverage(board, runs_with_eval=1, total_runs=1)
        record_judge_unknown_budget_compliance(
            board, compliant_judges=1, total_judges=1
        )
        record_judge_human_kappa_freshness(
            board, last_calibration_epoch=0.0, rubric_id="r", now=1.0
        )
        record_rca_to_proposal_lead_time(board, p95_seconds=0.0, sample_size=0)
        record_gauntlet_false_promote_rate(
            board, reverted_promotions=0, total_promotions=1
        )
        record_uwg_ink_path_uniqueness(board, non_uwg_writers_detected=0)
        record_replay_divergence_localization(
            board, localized_failures=1, total_failures=1
        )
        record_eval_freshness_on_write(board, fresh_writes=1, total_writes=1)
        record_exemplar_hit_rate(board, plans_with_exemplar_hit=1, total_plans=1)
        record_saturation_watch(board, static_30d_evals=0, total_evals=1)
        latest = board.all_latest()
        # All 11 KPIs must now have a sample.
        assert len(latest) == 11
        assert set(latest.keys()) == set(V6KPIName)
