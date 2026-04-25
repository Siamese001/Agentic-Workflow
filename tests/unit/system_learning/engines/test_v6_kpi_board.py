"""Unit tests for ``system_learning.engines.v6_kpi_board``.

Covers:
- Spec registry completeness (all 11 KPIs present, frozen).
- ``evaluate_sample`` semantics for LE / GE / EQ thresholds.
- ``V6KPIBoard.record`` / ``record_value`` happy path and validation.
- ``health_snapshot`` compound health logic — including missing-sample handling.
"""

from __future__ import annotations

import math

import pytest

from system_learning.engines.v6_kpi_board import (
    HEALTH_REQUIRED_KPIS,
    ThresholdDirection,
    V6_KPI_SPECS,
    V6HealthSnapshot,
    V6KPIBoard,
    V6KPIName,
    V6KPISample,
    V6KPISpec,
    V6KPIStatus,
    evaluate_sample,
)


class TestSpecRegistry:
    def test_all_11_kpis_present(self):
        assert len(V6_KPI_SPECS) == 11
        assert set(V6_KPI_SPECS.keys()) == set(V6KPIName)

    def test_registry_is_frozen(self):
        with pytest.raises(TypeError):
            V6_KPI_SPECS[V6KPIName.TRACE_INGEST_FRESHNESS] = None  # type: ignore[index]

    def test_spec_directions_are_valid(self):
        for spec in V6_KPI_SPECS.values():
            assert isinstance(spec.direction, ThresholdDirection)

    def test_health_required_subset(self):
        # All required KPIs must be in the spec registry.
        assert HEALTH_REQUIRED_KPIS.issubset(set(V6_KPI_SPECS.keys()))
        # Per v6 HEALTH DEFINITION, exactly 6 KPIs are required for compound health.
        assert len(HEALTH_REQUIRED_KPIS) == 6


class TestEvaluateSample:
    def test_le_green(self):
        sample = V6KPISample(
            name=V6KPIName.TRACE_INGEST_FRESHNESS,
            value=300.0,  # 5 min, well under 10 min threshold
            timestamp=0.0,
            source="test",
        )
        status = evaluate_sample(sample)
        assert status.is_green is True
        assert "GREEN" in status.reason

    def test_le_red(self):
        sample = V6KPISample(
            name=V6KPIName.TRACE_INGEST_FRESHNESS,
            value=900.0,  # 15 min, over 10 min threshold
            timestamp=0.0,
            source="test",
        )
        status = evaluate_sample(sample)
        assert status.is_green is False
        assert "RED" in status.reason

    def test_le_boundary_inclusive(self):
        sample = V6KPISample(
            name=V6KPIName.TRACE_INGEST_FRESHNESS,
            value=600.0,  # exactly 10 min
            timestamp=0.0,
            source="test",
        )
        assert evaluate_sample(sample).is_green is True

    def test_ge_green(self):
        sample = V6KPISample(
            name=V6KPIName.EVAL_COVERAGE_OF_RUNS,
            value=0.99,
            timestamp=0.0,
            source="test",
        )
        assert evaluate_sample(sample).is_green is True

    def test_ge_red(self):
        sample = V6KPISample(
            name=V6KPIName.EVAL_COVERAGE_OF_RUNS,
            value=0.50,
            timestamp=0.0,
            source="test",
        )
        assert evaluate_sample(sample).is_green is False

    def test_eq_green(self):
        sample = V6KPISample(
            name=V6KPIName.UWG_INK_PATH_UNIQUENESS,
            value=0.0,
            timestamp=0.0,
            source="test",
        )
        assert evaluate_sample(sample).is_green is True

    def test_eq_red(self):
        sample = V6KPISample(
            name=V6KPIName.UWG_INK_PATH_UNIQUENESS,
            value=1.0,  # one rogue writer == sovereignty breach
            timestamp=0.0,
            source="test",
        )
        assert evaluate_sample(sample).is_green is False


class TestV6KPIBoard:
    def test_record_and_latest(self):
        board = V6KPIBoard()
        sample = V6KPISample(
            name=V6KPIName.EVAL_COVERAGE_OF_RUNS,
            value=0.99,
            timestamp=1000.0,
            source="test",
        )
        board.record(sample)
        assert board.latest(V6KPIName.EVAL_COVERAGE_OF_RUNS) is sample

    def test_record_value_helper(self):
        board = V6KPIBoard()
        sample = board.record_value(
            V6KPIName.TRACE_INGEST_FRESHNESS,
            120.0,
            source="otel_consumer",
            timestamp=42.0,
        )
        assert isinstance(sample, V6KPISample)
        assert sample.value == 120.0
        assert sample.source == "otel_consumer"
        assert board.latest(V6KPIName.TRACE_INGEST_FRESHNESS) is sample

    def test_record_replaces_prior(self):
        board = V6KPIBoard()
        s1 = board.record_value(
            V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE, 0.005, source="t", timestamp=1.0
        )
        s2 = board.record_value(
            V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE, 0.02, source="t", timestamp=2.0
        )
        latest = board.latest(V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE)
        assert latest is s2
        assert latest is not s1

    def test_record_rejects_non_sample(self):
        board = V6KPIBoard()
        with pytest.raises(TypeError):
            board.record({"name": "trace_ingest_freshness", "value": 0.0})  # type: ignore[arg-type]

    def test_latest_missing_returns_none(self):
        board = V6KPIBoard()
        assert board.latest(V6KPIName.SATURATION_WATCH) is None

    def test_evaluate_all_only_recorded(self):
        board = V6KPIBoard()
        board.record_value(V6KPIName.EVAL_COVERAGE_OF_RUNS, 0.99, source="t")
        statuses = board.evaluate_all()
        assert set(statuses.keys()) == {V6KPIName.EVAL_COVERAGE_OF_RUNS}
        assert statuses[V6KPIName.EVAL_COVERAGE_OF_RUNS].is_green is True

    def test_reset(self):
        board = V6KPIBoard()
        board.record_value(V6KPIName.EVAL_COVERAGE_OF_RUNS, 0.99, source="t")
        board.reset()
        assert board.all_latest() == {}


class TestHealthSnapshot:
    def _green_board(self) -> V6KPIBoard:
        board = V6KPIBoard()
        # All 6 required KPIs green
        board.record_value(V6KPIName.TRACE_INGEST_FRESHNESS, 60.0, source="t")
        board.record_value(V6KPIName.EVAL_COVERAGE_OF_RUNS, 0.99, source="t")
        board.record_value(V6KPIName.JUDGE_HUMAN_KAPPA_FRESHNESS, 86400.0, source="t")
        board.record_value(V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION, 0.95, source="t")
        board.record_value(V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE, 0.005, source="t")
        board.record_value(V6KPIName.UWG_INK_PATH_UNIQUENESS, 0.0, source="t")
        return board

    def test_all_green_is_healthy(self):
        snap = self._green_board().health_snapshot(now=1000.0)
        assert isinstance(snap, V6HealthSnapshot)
        assert snap.is_healthy is True
        assert snap.missing == ()
        assert "healthy" in snap.reason

    def test_missing_sample_blocks_health(self):
        board = self._green_board()
        # Drop one required KPI (test hook — protected access intentional)
        board._latest.pop(V6KPIName.UWG_INK_PATH_UNIQUENESS)  # pylint: disable=protected-access
        snap = board.health_snapshot(now=1000.0)
        assert snap.is_healthy is False
        assert V6KPIName.UWG_INK_PATH_UNIQUENESS in snap.missing
        assert "missing samples" in snap.reason

    def test_red_kpi_blocks_health(self):
        board = self._green_board()
        # Make one required KPI red
        board.record_value(V6KPIName.UWG_INK_PATH_UNIQUENESS, 3.0, source="t")
        snap = board.health_snapshot(now=1000.0)
        assert snap.is_healthy is False
        assert "red KPIs" in snap.reason
        assert "uwg_ink_path_uniqueness" in snap.reason

    def test_custom_required_set(self):
        board = V6KPIBoard()
        # Only require coverage; report it green.
        board.record_value(V6KPIName.EVAL_COVERAGE_OF_RUNS, 0.99, source="t")
        snap = board.health_snapshot(
            required=[V6KPIName.EVAL_COVERAGE_OF_RUNS], now=1.0
        )
        assert snap.is_healthy is True

    def test_empty_board_unhealthy(self):
        snap = V6KPIBoard().health_snapshot(now=1.0)
        assert snap.is_healthy is False
        assert len(snap.missing) == len(HEALTH_REQUIRED_KPIS)


class TestV6KPISpecValues:
    """Lock down the verbatim thresholds from v6 lines 234-244."""

    def test_trace_ingest_freshness_10_minutes(self):
        spec = V6_KPI_SPECS[V6KPIName.TRACE_INGEST_FRESHNESS]
        assert math.isclose(spec.threshold or 0, 600.0)
        assert spec.direction is ThresholdDirection.LE
        assert spec.phase == "6A"

    def test_eval_coverage_98_percent(self):
        spec = V6_KPI_SPECS[V6KPIName.EVAL_COVERAGE_OF_RUNS]
        assert math.isclose(spec.threshold or 0, 0.98)
        assert spec.direction is ThresholdDirection.GE

    def test_judge_unknown_budget_95_percent(self):
        spec = V6_KPI_SPECS[V6KPIName.JUDGE_UNKNOWN_BUDGET_COMPLIANCE]
        assert math.isclose(spec.threshold or 0, 0.95)
        assert spec.direction is ThresholdDirection.GE

    def test_kappa_freshness_7_days(self):
        spec = V6_KPI_SPECS[V6KPIName.JUDGE_HUMAN_KAPPA_FRESHNESS]
        assert math.isclose(spec.threshold or 0, 7.0 * 86400.0)
        assert spec.direction is ThresholdDirection.LE

    def test_rca_lead_time_24h(self):
        spec = V6_KPI_SPECS[V6KPIName.RCA_TO_PROPOSAL_LEAD_TIME]
        assert math.isclose(spec.threshold or 0, 24.0 * 3600.0)
        assert spec.direction is ThresholdDirection.LE

    def test_false_promote_1_percent(self):
        spec = V6_KPI_SPECS[V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE]
        assert math.isclose(spec.threshold or 0, 0.01)
        assert spec.direction is ThresholdDirection.LE

    def test_uwg_uniqueness_zero(self):
        spec = V6_KPI_SPECS[V6KPIName.UWG_INK_PATH_UNIQUENESS]
        assert spec.threshold == 0.0
        assert spec.direction is ThresholdDirection.EQ

    def test_replay_localization_90_percent(self):
        spec = V6_KPI_SPECS[V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION]
        assert math.isclose(spec.threshold or 0, 0.90)
        assert spec.direction is ThresholdDirection.GE

    def test_eval_freshness_on_write_100(self):
        spec = V6_KPI_SPECS[V6KPIName.EVAL_FRESHNESS_ON_WRITE]
        assert math.isclose(spec.threshold or 0, 1.0)
        assert spec.direction is ThresholdDirection.GE

    def test_exemplar_hit_20_percent(self):
        spec = V6_KPI_SPECS[V6KPIName.EXEMPLAR_HIT_RATE]
        assert math.isclose(spec.threshold or 0, 0.20)
        assert spec.direction is ThresholdDirection.GE

    def test_saturation_watch_10_percent(self):
        spec = V6_KPI_SPECS[V6KPIName.SATURATION_WATCH]
        assert math.isclose(spec.threshold or 0, 0.10)
        assert spec.direction is ThresholdDirection.LE
