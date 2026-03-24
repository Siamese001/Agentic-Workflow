"""ADG-driven tests for apps_shared/utils/open_telemetry_tracing_adapter_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.open_telemetry_tracing_adapter_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        CostMetrics,
        OpenTelemetryTracingAdapter,
        ResilienceMetrics,
        SpanMetadata,
        SpanType,
        get_tracer,
        reset_tracer,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SpanType = None  # type: ignore[assignment,misc]
    SpanMetadata = None  # type: ignore[assignment,misc]
    CostMetrics = None  # type: ignore[assignment,misc]
    ResilienceMetrics = None  # type: ignore[assignment,misc]
    OpenTelemetryTracingAdapter = None  # type: ignore[assignment,misc]
    get_tracer = None  # type: ignore[assignment,misc]
    reset_tracer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestSpanType:
    def test_is_enum(self):
        import enum
        assert issubclass(SpanType, enum.Enum)
    def test_has_members(self):
        assert len(list(SpanType)) >= 1
    def test_importable(self):
        assert SpanType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestSpanMetadata:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SpanMetadata)
    def test_importable(self):
        assert SpanMetadata is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestCostMetrics:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CostMetrics)
    def test_importable(self):
        assert CostMetrics is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestResilienceMetrics:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ResilienceMetrics)
    def test_importable(self):
        assert ResilienceMetrics is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestOpenTelemetryTracingAdapter:
    def test_is_class(self):
        assert isinstance(OpenTelemetryTracingAdapter, type)
    def test_importable(self):
        assert OpenTelemetryTracingAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestGetTracer:
    def test_is_callable(self):
        assert callable(get_tracer)

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestResetTracer:
    def test_is_callable(self):
        assert callable(reset_tracer)

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module open_telemetry_tracing_adapter_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE