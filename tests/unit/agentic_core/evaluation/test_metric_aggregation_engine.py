"""Tests for agentic_core.L6_observability.evaluation.metric_aggregation_engine module.

Tests MetricAggregationEngine for time-series metric aggregation.
"""
from __future__ import annotations

import time

import pytest

from agentic_core.L6_observability.utils.evaluation.metric_aggregation_engine import (
    AggregatedMetrics,
    MetricAggregationEngine,
    MetricDataPoint,
    TimeWindow,
    get_metric_engine,
    reset_metric_engine,
)


class TestMetricDataPoint:
    """Test MetricDataPoint dataclass."""

    def test_datapoint_creation(self):
        """Test creating a metric data point."""
        dp = MetricDataPoint(
            metric_name="test_metric",
            value=0.95,
            timestamp_utc=1000.0,
            metadata={"source": "test"},
            weight=2.0,
        )
        assert dp.metric_name == "test_metric"
        assert dp.value == 0.95
        assert dp.timestamp_utc == 1000.0
        assert dp.metadata == {"source": "test"}
        assert dp.weight == 2.0

    def test_default_metadata(self):
        """Test default empty metadata."""
        dp = MetricDataPoint(
            metric_name="test",
            value=1.0,
            timestamp_utc=1000.0,
        )
        assert dp.metadata == {}

    def test_default_weight(self):
        """Test default weight of 1.0."""
        dp = MetricDataPoint(
            metric_name="test",
            value=1.0,
            timestamp_utc=1000.0,
        )
        assert dp.weight == 1.0


class TestMetricAggregationEngineBasic:
    """Test basic MetricAggregationEngine functionality."""

    def test_engine_creation(self):
        """Test creating an aggregation engine."""
        engine = MetricAggregationEngine(max_data_points=1000)
        assert engine._max_data_points == 1000

    def test_add_single_metric(self):
        """Test adding a single metric data point."""
        engine = MetricAggregationEngine()
        engine.add_metric("accuracy", 0.95, timestamp_utc=1000.0)

        stats = engine.get_stats()
        assert stats["total_metrics"] == 1
        assert stats["total_points_added"] == 1
        assert "accuracy" in stats["metric_names"]

    def test_add_multiple_metrics(self):
        """Test adding multiple metrics."""
        engine = MetricAggregationEngine()
        engine.add_metric("accuracy", 0.95, timestamp_utc=1000.0)
        engine.add_metric("f1", 0.87, timestamp_utc=1001.0)
        engine.add_metric("accuracy", 0.96, timestamp_utc=1002.0)

        stats = engine.get_stats()
        assert stats["total_metrics"] == 2
        assert stats["total_points_added"] == 3

    def test_add_metric_with_metadata(self):
        """Test adding metric with metadata."""
        engine = MetricAggregationEngine()
        engine.add_metric(
            "accuracy",
            0.95,
            timestamp_utc=1000.0,
            metadata={"model": "v1", "dataset": "test"},
        )

        # Verify through aggregation
        result = engine.get_aggregated_metrics("accuracy")
        assert result is not None
        assert result.count == 1

    def test_add_metric_with_weight(self):
        """Test adding weighted metric."""
        engine = MetricAggregationEngine()
        engine.add_metric("score", 0.8, timestamp_utc=1000.0, weight=2.0)
        engine.add_metric("score", 0.9, timestamp_utc=1001.0, weight=1.0)

        result = engine.get_aggregated_metrics("score")
        assert result is not None
        # Weighted mean: (0.8*2 + 0.9*1) / 3 = 0.833...
        assert result.weighted_mean == pytest.approx(0.833333, 0.001)

    def test_default_timestamp(self):
        """Test default timestamp uses current time."""
        engine = MetricAggregationEngine()
        before = time.time()
        engine.add_metric("test", 1.0)
        after = time.time()

        stats = engine.get_stats()
        assert stats["total_points_added"] == 1


class TestMetricAggregation:
    """Test metric aggregation calculations."""

    def test_aggregation_basic_stats(self):
        """Test basic aggregation statistics."""
        engine = MetricAggregationEngine()
        values = [0.1, 0.2, 0.3, 0.4, 0.5]
        for i, v in enumerate(values):
            engine.add_metric("metric", v, timestamp_utc=1000.0 + i)

        result = engine.get_aggregated_metrics("metric")
        assert result is not None
        assert result.metric_name == "metric"
        assert result.count == 5
        assert result.mean == pytest.approx(0.3, 0.001)
        assert result.min_value == 0.1
        assert result.max_value == 0.5

    def test_aggregation_median(self):
        """Test median calculation."""
        engine = MetricAggregationEngine()
        values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]  # Even number
        for i, v in enumerate(values):
            engine.add_metric("metric", v, timestamp_utc=1000.0 + i)

        result = engine.get_aggregated_metrics("metric")
        assert result is not None
        assert result.median == pytest.approx(0.35, 0.001)

    def test_aggregation_percentiles(self):
        """Test percentile calculations."""
        engine = MetricAggregationEngine()
        for i in range(100):
            engine.add_metric("metric", float(i), timestamp_utc=1000.0 + i)

        result = engine.get_aggregated_metrics("metric")
        assert result is not None
        assert result.p95 == pytest.approx(94.05, 0.1)
        assert result.p99 == pytest.approx(98.01, 0.1)

    def test_aggregation_std_dev(self):
        """Test standard deviation calculation."""
        engine = MetricAggregationEngine()
        values = [0.0, 0.0, 0.0]  # No variance
        for i, v in enumerate(values):
            engine.add_metric("metric", v, timestamp_utc=1000.0 + i)

        result = engine.get_aggregated_metrics("metric")
        assert result is not None
        assert result.std_dev == 0.0

    def test_empty_metric_returns_none(self):
        """Test getting aggregation for non-existent metric returns None."""
        engine = MetricAggregationEngine()
        result = engine.get_aggregated_metrics("non_existent")
        assert result is None


class TestTimeWindows:
    """Test time window filtering."""

    def test_all_time_window(self):
        """Test ALL_TIME window includes all data."""
        engine = MetricAggregationEngine()
        current_time = time.time()
        engine.add_metric("metric", 0.5, timestamp_utc=current_time - 86400 * 30)  # 30 days ago
        engine.add_metric("metric", 0.6, timestamp_utc=current_time)

        result = engine.get_aggregated_metrics("metric", TimeWindow.ALL_TIME)
        assert result is not None
        assert result.count == 2

    def test_last_day_window(self):
        """Test LAST_DAY window filters old data."""
        engine = MetricAggregationEngine()
        current_time = time.time()
        engine.add_metric("metric", 0.5, timestamp_utc=current_time - 86400 * 2)  # 2 days ago
        engine.add_metric("metric", 0.6, timestamp_utc=current_time - 3600)  # 1 hour ago

        result = engine.get_aggregated_metrics("metric", TimeWindow.LAST_DAY)
        assert result is not None
        assert result.count == 1
        assert result.mean == pytest.approx(0.6, 0.001)

    def test_last_hour_window(self):
        """Test LAST_HOUR window."""
        engine = MetricAggregationEngine()
        current_time = time.time()
        engine.add_metric("metric", 0.5, timestamp_utc=current_time - 7200)  # 2 hours ago
        engine.add_metric("metric", 0.6, timestamp_utc=current_time - 1800)  # 30 min ago

        result = engine.get_aggregated_metrics("metric", TimeWindow.LAST_HOUR)
        assert result is None  # 30 min ago is outside last hour from current_time

    def test_window_seconds_calculation(self):
        """Test time window to seconds conversion."""
        assert MetricAggregationEngine._get_window_seconds(TimeWindow.LAST_HOUR) == 3600.0
        assert MetricAggregationEngine._get_window_seconds(TimeWindow.LAST_DAY) == 86400.0
        assert MetricAggregationEngine._get_window_seconds(TimeWindow.LAST_WEEK) == 604800.0
        assert MetricAggregationEngine._get_window_seconds(TimeWindow.LAST_MONTH) == 2592000.0
        assert MetricAggregationEngine._get_window_seconds(TimeWindow.ALL_TIME) == float("inf")


class TestMetricSummary:
    """Test metric summary functionality."""

    def test_summary_multiple_metrics(self):
        """Test summary for multiple metrics."""
        engine = MetricAggregationEngine()
        engine.add_metric("accuracy", 0.9, timestamp_utc=1000.0)
        engine.add_metric("f1", 0.85, timestamp_utc=1001.0)
        engine.add_metric("precision", 0.88, timestamp_utc=1002.0)

        summary = engine.get_metric_summary(TimeWindow.ALL_TIME)
        assert len(summary) == 3
        assert "accuracy" in summary
        assert "f1" in summary
        assert "precision" in summary

    def test_summary_empty_engine(self):
        """Test summary for empty engine."""
        engine = MetricAggregationEngine()
        summary = engine.get_metric_summary()
        assert summary == {}


class TestMetricTrend:
    """Test metric trend analysis."""

    def test_trend_basic(self):
        """Test basic trend calculation."""
        engine = MetricAggregationEngine()
        current_time = time.time()
        for i in range(10):
            engine.add_metric("metric", float(i), timestamp_utc=current_time - 3600 + i * 100)

        trend = engine.get_metric_trend("metric", num_buckets=5, time_window=TimeWindow.LAST_DAY)
        assert len(trend) <= 5
        # Each point should be (timestamp, average_value)
        for ts, val in trend:
            assert isinstance(ts, float)
            assert isinstance(val, float)

    def test_trend_empty_metric(self):
        """Test trend for non-existent metric returns empty list."""
        engine = MetricAggregationEngine()
        trend = engine.get_metric_trend("non_existent")
        assert trend == []

    def test_trend_no_data_in_window(self):
        """Test trend when no data in window."""
        engine = MetricAggregationEngine()
        current_time = time.time()
        # Add old data outside last day
        engine.add_metric("metric", 0.5, timestamp_utc=current_time - 86400 * 2)

        trend = engine.get_metric_trend("metric", time_window=TimeWindow.LAST_DAY)
        assert trend == []


class TestClearing:
    """Test clearing metrics."""

    def test_clear_single_metric(self):
        """Test clearing a single metric."""
        engine = MetricAggregationEngine()
        engine.add_metric("metric1", 0.5, timestamp_utc=1000.0)
        engine.add_metric("metric2", 0.6, timestamp_utc=1001.0)

        engine.clear_metric("metric1")

        stats = engine.get_stats()
        assert stats["total_metrics"] == 1
        assert "metric2" in stats["metric_names"]

    def test_clear_all_metrics(self):
        """Test clearing all metrics."""
        engine = MetricAggregationEngine()
        engine.add_metric("metric1", 0.5, timestamp_utc=1000.0)
        engine.add_metric("metric2", 0.6, timestamp_utc=1001.0)

        engine.clear_all_metrics()

        stats = engine.get_stats()
        assert stats["total_metrics"] == 0
        assert stats["total_points_added"] == 0
        assert stats["current_points"] == 0


class TestFIFOBehavior:
    """Test FIFO (first in, first out) behavior when max points reached."""

    def test_fifo_removes_oldest(self):
        """Test that oldest points are removed when max is reached."""
        engine = MetricAggregationEngine(max_data_points=3)
        engine.add_metric("metric", 0.1, timestamp_utc=1000.0)
        engine.add_metric("metric", 0.2, timestamp_utc=1001.0)
        engine.add_metric("metric", 0.3, timestamp_utc=1002.0)
        engine.add_metric("metric", 0.4, timestamp_utc=1003.0)  # Should evict 0.1

        result = engine.get_aggregated_metrics("metric")
        assert result is not None
        assert result.count == 3
        assert result.min_value == 0.2  # 0.1 was evicted


class TestGlobalEngine:
    """Test global metric engine singleton."""

    def test_get_metric_engine_singleton(self):
        """Test global engine is a singleton."""
        reset_metric_engine()
        engine1 = get_metric_engine()
        engine2 = get_metric_engine()
        assert engine1 is engine2

    def test_reset_metric_engine(self):
        """Test resetting global engine."""
        reset_metric_engine()
        engine1 = get_metric_engine()
        engine1.add_metric("test", 1.0, timestamp_utc=1000.0)

        reset_metric_engine()
        engine2 = get_metric_engine()

        # Should be a fresh engine
        stats = engine2.get_stats()
        assert stats["total_points_added"] == 0


class TestAggregatedMetricsStructure:
    """Test AggregatedMetrics dataclass structure."""

    def test_aggregated_metrics_fields(self):
        """Test all required fields are present."""
        agg = AggregatedMetrics(
            metric_name="test",
            count=10,
            mean=0.5,
            median=0.5,
            p95=0.9,
            p99=0.95,
            min_value=0.1,
            max_value=0.9,
            std_dev=0.1,
            weighted_mean=0.52,
            time_window=TimeWindow.LAST_DAY,
            start_time_utc=1000.0,
            end_time_utc=2000.0,
        )

        assert agg.metric_name == "test"
        assert agg.count == 10
        assert agg.mean == 0.5
        assert agg.median == 0.5
        assert agg.p95 == 0.9
        assert agg.p99 == 0.95
        assert agg.min_value == 0.1
        assert agg.max_value == 0.9
        assert agg.std_dev == 0.1
        assert agg.weighted_mean == 0.52
        assert agg.time_window == TimeWindow.LAST_DAY
        assert agg.start_time_utc == 1000.0
        assert agg.end_time_utc == 2000.0
