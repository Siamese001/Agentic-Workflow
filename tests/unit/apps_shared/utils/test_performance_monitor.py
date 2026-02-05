"""
Unit tests for Performance Monitor.

Tests Phase 4B - Advanced Testing and Performance.
"""

import time

import pytest

from apps_shared.utils.performance_monitor_types import (
    MetricsCollector,
    PerformanceMonitor,
    PerformanceThresholds,
    TimingMetric,
    get_performance_monitor,
    timed,
)


class TestTimingMetric:
    """Test TimingMetric dataclass."""

    def test_metric_creation(self):
        """Test creating a timing metric."""
        metric = TimingMetric(
            name="test_op",
            duration_ms=100.5,
            metadata={"key": "value"},
        )

        assert metric.name == "test_op"
        assert metric.duration_ms == 100.5
        assert metric.metadata == {"key": "value"}
        assert metric.timestamp > 0


class TestMetricsCollector:
    """Test MetricsCollector functionality."""

    def test_start_stop_timer(self):
        """Test starting and stopping a timer."""
        collector = MetricsCollector()

        collector.start_timer("test_op")
        time.sleep(0.01)  # 10ms
        duration = collector.stop_timer("test_op")

        assert duration >= 10  # At least 10ms
        assert "test_op" in collector._metrics
        assert len(collector._metrics["test_op"]) == 1

    def test_stop_timer_not_started(self):
        """Test stopping a timer that wasn't started."""
        collector = MetricsCollector()

        duration = collector.stop_timer("nonexistent")
        assert duration == 0.0

    def test_record_metric(self):
        """Test recording a metric directly."""
        collector = MetricsCollector()

        collector.record_metric("test_op", 50.0, {"success": True})

        assert "test_op" in collector._metrics
        assert collector._metrics["test_op"][0].duration_ms == 50.0

    def test_get_summary(self):
        """Test getting summary statistics."""
        collector = MetricsCollector()

        for i in range(10):
            collector.record_metric("test_op", float(i * 10))

        summary = collector.get_summary("test_op")

        assert summary is not None
        assert summary.count == 10
        assert summary.min_ms == 0.0
        assert summary.max_ms == 90.0
        assert summary.mean_ms == 45.0

    def test_get_summary_nonexistent(self):
        """Test getting summary for nonexistent operation."""
        collector = MetricsCollector()

        summary = collector.get_summary("nonexistent")
        assert summary is None

    def test_get_all_summaries(self):
        """Test getting all summaries."""
        collector = MetricsCollector()

        collector.record_metric("op1", 10.0)
        collector.record_metric("op2", 20.0)

        summaries = collector.get_all_summaries()

        assert "op1" in summaries
        assert "op2" in summaries

    def test_clear_specific(self):
        """Test clearing specific operation metrics."""
        collector = MetricsCollector()

        collector.record_metric("op1", 10.0)
        collector.record_metric("op2", 20.0)

        collector.clear("op1")

        assert "op1" not in collector._metrics
        assert "op2" in collector._metrics

    def test_clear_all(self):
        """Test clearing all metrics."""
        collector = MetricsCollector()

        collector.record_metric("op1", 10.0)
        collector.record_metric("op2", 20.0)

        collector.clear()

        assert len(collector._metrics) == 0


class TestTimedDecorator:
    """Test timed decorator."""

    def test_timed_records_success(self):
        """Test timed decorator records successful execution."""
        collector = MetricsCollector()

        @timed(collector, "my_function")
        def my_function():
            time.sleep(0.01)
            return "result"

        result = my_function()

        assert result == "result"
        assert "my_function" in collector._metrics
        assert collector._metrics["my_function"][0].metadata["success"] is True

    def test_timed_records_failure(self):
        """Test timed decorator records failed execution."""
        collector = MetricsCollector()

        @timed(collector, "failing_function")
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        assert "failing_function" in collector._metrics
        assert collector._metrics["failing_function"][0].metadata["success"] is False

    def test_timed_uses_function_name(self):
        """Test timed decorator uses function name by default."""
        collector = MetricsCollector()

        @timed(collector)
        def auto_named_function():
            pass

        auto_named_function()

        assert "auto_named_function" in collector._metrics


class TestPerformanceThresholds:
    """Test PerformanceThresholds functionality."""

    def test_set_and_get_threshold(self):
        """Test setting and getting thresholds."""
        thresholds = PerformanceThresholds()

        thresholds.set_threshold("fast_op", 100.0)
        thresholds.set_threshold("slow_op", 5000.0)

        assert thresholds.get_threshold("fast_op") == 100.0
        assert thresholds.get_threshold("slow_op") == 5000.0

    def test_default_threshold(self):
        """Test default threshold is used for unknown operations."""
        thresholds = PerformanceThresholds()

        threshold = thresholds.get_threshold("unknown_op")
        assert threshold == 1000.0  # Default

    def test_check_threshold_pass(self):
        """Test threshold check passes when under limit."""
        thresholds = PerformanceThresholds()
        thresholds.set_threshold("test_op", 100.0)

        assert thresholds.check_threshold("test_op", 50.0) is True

    def test_check_threshold_fail(self):
        """Test threshold check fails when over limit."""
        thresholds = PerformanceThresholds()
        thresholds.set_threshold("test_op", 100.0)

        assert thresholds.check_threshold("test_op", 150.0) is False

    def test_get_violations(self):
        """Test getting threshold violations."""
        thresholds = PerformanceThresholds()
        thresholds.set_threshold("fast_op", 50.0)

        collector = MetricsCollector()
        collector.record_metric("fast_op", 100.0)  # Violation
        collector.record_metric("fast_op", 30.0)  # OK

        violations = thresholds.get_violations(collector)

        assert len(violations) == 1
        assert violations[0][0] == "fast_op"
        assert violations[0][1] == 100.0


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""

    def test_initialization(self):
        """Test monitor initialization."""
        monitor = PerformanceMonitor("test")

        assert monitor.name == "test"
        assert monitor.collector is not None
        assert monitor.thresholds is not None

    def test_record(self):
        """Test recording metrics."""
        monitor = PerformanceMonitor("test")

        monitor.record("test_op", 50.0, {"key": "value"})

        assert "test_op" in monitor.collector._metrics

    def test_time_operation_context(self):
        """Test time_operation context manager."""
        monitor = PerformanceMonitor("test")

        with monitor.time_operation("timed_op") as timer:
            time.sleep(0.01)

        assert timer.duration_ms >= 10
        assert "timed_op" in monitor.collector._metrics

    def test_get_report(self):
        """Test generating a report."""
        monitor = PerformanceMonitor("test")

        monitor.record("op1", 50.0)
        monitor.record("op1", 100.0)
        monitor.record("op2", 25.0)

        report = monitor.get_report()

        assert report["monitor_name"] == "test"
        assert "op1" in report["operations"]
        assert "op2" in report["operations"]
        assert report["total_operations"] == 3

    def test_get_report_with_violations(self):
        """Test report includes violations."""
        monitor = PerformanceMonitor("test")
        monitor.thresholds.set_threshold("fast_op", 50.0)

        monitor.record("fast_op", 100.0)  # Violation

        report = monitor.get_report()

        assert len(report["violations"]) == 1

    def test_reset(self):
        """Test resetting the monitor."""
        monitor = PerformanceMonitor("test")

        monitor.record("test_op", 50.0)
        monitor.reset()

        assert len(monitor.collector._metrics) == 0


class TestOperationTimer:
    """Test OperationTimer context manager."""

    def test_timer_records_duration(self):
        """Test timer records duration on exit."""
        monitor = PerformanceMonitor("test")

        with monitor.time_operation("test_op") as timer:
            time.sleep(0.01)

        assert timer.duration_ms >= 10

    def test_timer_records_success(self):
        """Test timer records success status."""
        monitor = PerformanceMonitor("test")

        with monitor.time_operation("test_op"):
            pass

        metric = monitor.collector._metrics["test_op"][0]
        assert metric.metadata["success"] is True

    def test_timer_records_failure(self):
        """Test timer records failure status on exception."""
        monitor = PerformanceMonitor("test")

        try:
            with monitor.time_operation("failing_op"):
                raise ValueError("Test error")
        except ValueError:
            pass

        metric = monitor.collector._metrics["failing_op"][0]
        assert metric.metadata["success"] is False


class TestGetPerformanceMonitor:
    """Test get_performance_monitor singleton."""

    def test_singleton_instance(self):
        """Test that get_performance_monitor returns singleton."""
        import apps_shared.utils.performance_monitor_types as pm_module

        pm_module._global_monitor = None

        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()

        assert monitor1 is monitor2

        pm_module._global_monitor = None
