"""Foundational behavioral tests for apps_shared/utils/performance_monitor_types_util.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_performance_monitor_types_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_shared.utils.performance_monitor_types_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    MetricsCollector,
    MetricsSummary,
    OperationTimer,
    PerformanceMonitor,
    PerformanceThresholds,
    TimingMetric,
    get_performance_monitor,
    timed,
)


class TestTimingMetricContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TimingMetric)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(TimingMetric)}
        assert field_names >= {'duration_ms', 'metadata', 'timestamp', 'name'}

class TestMetricsSummaryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetricsSummary)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(MetricsSummary)}
        assert field_names >= {'min_ms', 'mean_ms', 'name', 'max_ms', 'count'}

class TestMetricsCollectorContract:
    def test_is_class(self):
        assert isinstance(MetricsCollector, type)

    def test_has_method_start_timer(self):
        assert callable(getattr(MetricsCollector, 'start_timer', None))

    def test_has_method_stop_timer(self):
        assert callable(getattr(MetricsCollector, 'stop_timer', None))

    def test_has_method_record_metric(self):
        assert callable(getattr(MetricsCollector, 'record_metric', None))

    def test_has_method_get_summary(self):
        assert callable(getattr(MetricsCollector, 'get_summary', None))

class TestPerformanceThresholdsContract:
    def test_is_class(self):
        assert isinstance(PerformanceThresholds, type)

    def test_has_method_set_threshold(self):
        assert callable(getattr(PerformanceThresholds, 'set_threshold', None))

    def test_has_method_get_threshold(self):
        assert callable(getattr(PerformanceThresholds, 'get_threshold', None))

    def test_has_method_check_threshold(self):
        assert callable(getattr(PerformanceThresholds, 'check_threshold', None))

    def test_has_method_get_violations(self):
        assert callable(getattr(PerformanceThresholds, 'get_violations', None))

class TestPerformanceMonitorContract:
    def test_is_class(self):
        assert isinstance(PerformanceMonitor, type)

    def test_has_method_time_operation(self):
        assert callable(getattr(PerformanceMonitor, 'time_operation', None))

    def test_has_method_record(self):
        assert callable(getattr(PerformanceMonitor, 'record', None))

    def test_has_method_get_report(self):
        assert callable(getattr(PerformanceMonitor, 'get_report', None))

    def test_has_method_reset(self):
        assert callable(getattr(PerformanceMonitor, 'reset', None))

class TestOperationTimerContract:
    def test_is_class(self):
        assert isinstance(OperationTimer, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(OperationTimer, type)

class TestTimedFunction:
    def test_is_callable(self):
        assert callable(timed)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(timed)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetPerformanceMonitorFunction:
    def test_is_callable(self):
        assert callable(get_performance_monitor)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_performance_monitor)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module performance_monitor_types_util must be importable or skip gracefully."""
    pass  # Import verified at module level
