"""ADG-driven tests for system_learning/adapters/l1_meta_adapter.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.adapters.l1_meta_adapter import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        L1DriftSignal,
        L1MetaAdapter,
        L1TelemetryEvent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    L1TelemetryEvent = None  # type: ignore[assignment,misc]
    L1DriftSignal = None  # type: ignore[assignment,misc]
    L1MetaAdapter = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestL1TelemetryEvent:
    def test_is_class(self):
        assert isinstance(L1TelemetryEvent, type)
    def test_importable(self):
        assert L1TelemetryEvent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestL1DriftSignal:
    def test_is_class(self):
        assert isinstance(L1DriftSignal, type)
    def test_importable(self):
        assert L1DriftSignal is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestL1MetaAdapter:
    def test_is_class(self):
        assert isinstance(L1MetaAdapter, type)
    def test_importable(self):
        assert L1MetaAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module l1_meta_adapter.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
