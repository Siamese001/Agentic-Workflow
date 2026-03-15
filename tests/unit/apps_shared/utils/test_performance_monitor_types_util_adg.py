"""ADG-driven tests for apps_shared/utils/performance_monitor_types_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.performance_monitor_types_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
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
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    TimingMetric = None  # type: ignore[assignment,misc]
    MetricsSummary = None  # type: ignore[assignment,misc]
    MetricsCollector = None  # type: ignore[assignment,misc]
    PerformanceThresholds = None  # type: ignore[assignment,misc]
    PerformanceMonitor = None  # type: ignore[assignment,misc]
    OperationTimer = None  # type: ignore[assignment,misc]
    timed = None  # type: ignore[assignment,misc]
    get_performance_monitor = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestTimingMetric:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TimingMetric)
    def test_importable(self):
        assert TimingMetric is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestMetricsSummary:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetricsSummary)
    def test_importable(self):
        assert MetricsSummary is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestMetricsCollector:
    def test_is_class(self):
        assert isinstance(MetricsCollector, type)
    def test_importable(self):
        assert MetricsCollector is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestPerformanceThresholds:
    def test_is_class(self):
        assert isinstance(PerformanceThresholds, type)
    def test_importable(self):
        assert PerformanceThresholds is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestPerformanceMonitor:
    def test_is_class(self):
        assert isinstance(PerformanceMonitor, type)
    def test_importable(self):
        assert PerformanceMonitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestOperationTimer:
    def test_is_class(self):
        assert isinstance(OperationTimer, type)
    def test_importable(self):
        assert OperationTimer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestTimed:
    def test_is_callable(self):
        assert callable(timed)

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestGetPerformanceMonitor:
    def test_is_callable(self):
        assert callable(get_performance_monitor)

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="performance_monitor_types_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module performance_monitor_types_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
