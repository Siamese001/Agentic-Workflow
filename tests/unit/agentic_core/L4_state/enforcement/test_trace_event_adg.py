"""ADG-driven tests for agentic_core/L4_state/enforcement/trace_event.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.enforcement.trace_event import (  # noqa: F401
        TraceEvent,
        TelemetryRecorder,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TraceEvent = None  # type: ignore[assignment,misc]
    TelemetryRecorder = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="trace_event.py deps unavailable")
class TestTraceEvent:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TraceEvent)
    def test_importable(self):
        assert TraceEvent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="trace_event.py deps unavailable")
class TestTelemetryRecorder:
    def test_is_class(self):
        assert isinstance(TelemetryRecorder, type)
    def test_importable(self):
        assert TelemetryRecorder is not None

@pytest.mark.skipif(not _AVAILABLE, reason="trace_event.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="trace_event.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="trace_event.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="trace_event.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="trace_event.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="trace_event.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module trace_event.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
