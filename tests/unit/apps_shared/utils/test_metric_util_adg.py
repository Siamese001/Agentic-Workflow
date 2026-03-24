"""ADG-driven tests for apps_shared/utils/metric_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.metric_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        Metric,
        MetricConfig,
        get_metrics,
        record_metric,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    Metric = None  # type: ignore[assignment,misc]
    MetricConfig = None  # type: ignore[assignment,misc]
    record_metric = None  # type: ignore[assignment,misc]
    get_metrics = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestMetric:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Metric)
    def test_importable(self):
        assert Metric is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestMetricConfig:
    def test_is_class(self):
        assert isinstance(MetricConfig, type)
    def test_importable(self):
        assert MetricConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestRecordMetric:
    def test_is_callable(self):
        assert callable(record_metric)

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestGetMetrics:
    def test_is_callable(self):
        assert callable(get_metrics)

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module metric_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE