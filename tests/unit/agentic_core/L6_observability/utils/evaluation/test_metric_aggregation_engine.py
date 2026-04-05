"""
tests/unit/agentic_core/L6_observability/evaluation/test_metric_aggregation_engine.py

Unit tests for Wave 1.4: Metric Aggregation Engine

Tests:
- Metric data point storage
- Aggregated metrics calculation
- Time window filtering
- Weighted averaging
- Percentile calculations
- Metric trends
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

    def test_data_point_creation(self):
        """Test creating a metric data point."""
        dp = MetricDataPoint(
            metric_name="test_metric",
            value=0.85,
            timestamp_utc=1700000000.0,
            metadata={"source": "test"},
            weight=1.5,
        )

        assert dp.metric_name == "test_metric"
        assert dp.value == 0.85
        assert dp.timestamp_utc == 1700000000.0
        assert dp.metadata["source"] == "test"
        assert dp.weight == 1.5


class TestMetricAggregationEngine:
    """Test suite for MetricAggregationEngine."""

    def test_add_metric(self):
        """Test adding metrics."""
        engine = MetricAggregationEngine()

        engine.add_metric("accuracy", 0.85, timestamp_utc=1700000000.0)
        engine.add_metric("accuracy", 0.90, timestamp_utc=1700000001.0)

        stats = engine.get_stats()
        assert stats["total_points_added"] == 2
        assert stats["current_points"] == 2
        assert "accuracy" in stats["metric_names"]

    def test_fifo_max_data_points(self):
        """Test FIFO enforcement of max data points."""
        engine = MetricAggregationEngine(max_data_points=5)

        # Add 10 points
        for i in range(10):
            engine.add_metric("test_metric", float(i), timestamp_utc=1700000000.0 + i)

        stats = engine.get_stats()
        assert stats["current_points"] == 5  # Only last 5 kept
        assert stats["total_points_added"] == 10

    def test_aggregated_metrics_calculation(self):
        """Test aggregated metrics calculation."""
        engine = MetricAggregationEngine()

        # Add metrics with known values
        values = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for i, val in enumerate(values):
            engine.add_metric("test_metric", val, timestamp_utc=1700000000.0 + i)

        aggregated = engine.get_aggregated_metrics("test_metric", TimeWindow.ALL_TIME)

        assert aggregated is not None
        assert aggregated.count == 6
        assert aggregated.mean == pytest.approx(0.75)
        assert aggregated.median == pytest.approx(0.75)
        assert aggregated.min_value == 0.5
        assert aggregated.max_value == 1.0

    def test_percentile_calculations(self):
        """Test percentile calculations."""
        engine = MetricAggregationEngine()

        # Add 100 values from 0.0 to 0.99
        for i in range(100):
            engine.add_metric("test_metric", i / 100.0, timestamp_utc=1700000000.0 + i)

        aggregated = engine.get_aggregated_metrics("test_metric", TimeWindow.ALL_TIME)

        assert aggregated is not None
        assert aggregated.p95 >= 0.94  # 95th percentile should be ~0.95
        assert aggregated.p99 >= 0.98  # 99th percentile should be ~0.99

    def test_weighted_averaging(self):
        """Test weighted averaging."""
        engine = MetricAggregationEngine()

        # Add metrics with different weights
        engine.add_metric("test_metric", 0.5, timestamp_utc=1700000000.0, weight=1.0)
        engine.add_metric("test_metric", 0.9, timestamp_utc=1700000001.0, weight=3.0)

        aggregated = engine.get_aggregated_metrics("test_metric", TimeWindow.ALL_TIME)

        assert aggregated is not None
        # Weighted mean = (0.5*1 + 0.9*3) / (1+3) = 3.2/4 = 0.8
        assert aggregated.weighted_mean == pytest.approx(0.8)
        # Regular mean = (0.5 + 0.9) / 2 = 0.7
        assert aggregated.mean == pytest.approx(0.7)

    def test_time_window_filtering(self):
        """Test time window filtering."""
        engine = MetricAggregationEngine()
        current_time = time.time()

        # Add metrics at different times
        engine.add_metric("test_metric", 0.5, timestamp_utc=current_time - 7200)  # 2 hours ago
        engine.add_metric("test_metric", 0.7, timestamp_utc=current_time - 1800)  # 30 min ago
        engine.add_metric("test_metric", 0.9, timestamp_utc=current_time - 300)   # 5 min ago

        # Last hour should only include last 2 points
        aggregated_hour = engine.get_aggregated_metrics("test_metric", TimeWindow.LAST_HOUR)
        assert aggregated_hour is not None
        assert aggregated_hour.count == 2

        # All time should include all 3 points
        aggregated_all = engine.get_aggregated_metrics("test_metric", TimeWindow.ALL_TIME)
        assert aggregated_all is not None
        assert aggregated_all.count == 3

    def test_metric_summary(self):
        """Test getting summary of all metrics."""
        engine = MetricAggregationEngine()

        engine.add_metric("accuracy", 0.85, timestamp_utc=1700000000.0)
        engine.add_metric("latency", 100.0, timestamp_utc=1700000000.0)
        engine.add_metric("cost", 0.05, timestamp_utc=1700000000.0)

        summary = engine.get_metric_summary(TimeWindow.ALL_TIME)

        assert len(summary) == 3
        assert "accuracy" in summary
        assert "latency" in summary
        assert "cost" in summary
        assert isinstance(summary["accuracy"], AggregatedMetrics)

    def test_metric_trend(self):
        """Test metric trend calculation."""
        engine = MetricAggregationEngine()

        # Add metrics over time with increasing values
        for i in range(20):
            engine.add_metric("test_metric", float(i), timestamp_utc=1700000000.0 + i * 100)

        trend = engine.get_metric_trend("test_metric", num_buckets=5, time_window=TimeWindow.ALL_TIME)

        assert len(trend) <= 5  # Should have at most 5 buckets
        # Trend should show increasing values
        if len(trend) > 1:
            assert trend[-1][1] > trend[0][1]

    def test_clear_metric(self):
        """Test clearing a specific metric."""
        engine = MetricAggregationEngine()

        engine.add_metric("metric1", 0.5, timestamp_utc=1700000000.0)
        engine.add_metric("metric2", 0.7, timestamp_utc=1700000000.0)

        engine.clear_metric("metric1")

        stats = engine.get_stats()
        assert "metric1" not in stats["metric_names"]
        assert "metric2" in stats["metric_names"]

    def test_clear_all_metrics(self):
        """Test clearing all metrics."""
        engine = MetricAggregationEngine()

        engine.add_metric("metric1", 0.5, timestamp_utc=1700000000.0)
        engine.add_metric("metric2", 0.7, timestamp_utc=1700000000.0)

        engine.clear_all_metrics()

        stats = engine.get_stats()
        assert stats["total_metrics"] == 0
        assert stats["current_points"] == 0
        assert stats["total_points_added"] == 0

    def test_empty_metric_returns_none(self):
        """Test querying non-existent metric returns None."""
        engine = MetricAggregationEngine()

        aggregated = engine.get_aggregated_metrics("nonexistent", TimeWindow.ALL_TIME)

        assert aggregated is None

    def test_standard_deviation(self):
        """Test standard deviation calculation."""
        engine = MetricAggregationEngine()

        # Add metrics with known std dev
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for val in values:
            engine.add_metric("test_metric", val, timestamp_utc=1700000000.0)

        aggregated = engine.get_aggregated_metrics("test_metric", TimeWindow.ALL_TIME)

        assert aggregated is not None
        # Std dev of [1,2,3,4,5] ≈ 1.58
        assert aggregated.std_dev > 0.0
        assert aggregated.std_dev == pytest.approx(1.58, abs=0.1)


class TestGlobalInstance:
    """Test global instance management."""

    def test_singleton_pattern(self):
        """Test metric engine singleton pattern."""
        reset_metric_engine()

        engine1 = get_metric_engine()
        engine2 = get_metric_engine()

        assert engine1 is engine2

        reset_metric_engine()
        engine3 = get_metric_engine()

        assert engine3 is not engine1


class TestIntegration:
    """Integration tests for metric aggregation."""

    def test_realistic_evaluation_metrics(self):
        """Test with realistic evaluation metrics."""
        engine = MetricAggregationEngine()

        # Simulate evaluation metrics over time
        metrics = [
            ("faithfulness", 0.85),
            ("faithfulness", 0.90),
            ("faithfulness", 0.88),
            ("groundedness", 0.92),
            ("groundedness", 0.89),
            ("relevancy", 0.95),
            ("relevancy", 0.93),
        ]

        current_time = time.time()
        for i, (name, value) in enumerate(metrics):
            engine.add_metric(name, value, timestamp_utc=current_time + i)

        # Get summary
        summary = engine.get_metric_summary(TimeWindow.ALL_TIME)

        assert len(summary) == 3
        assert summary["faithfulness"].count == 3
        assert summary["groundedness"].count == 2
        assert summary["relevancy"].count == 2

        # Check faithfulness stats
        faith_stats = summary["faithfulness"]
        assert faith_stats.mean == pytest.approx((0.85 + 0.90 + 0.88) / 3)
        assert faith_stats.min_value == 0.85
        assert faith_stats.max_value == 0.90


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
