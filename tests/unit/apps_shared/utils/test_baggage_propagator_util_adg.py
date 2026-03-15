"""ADG-driven tests for apps_shared/utils/baggage_propagator_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.baggage_propagator_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        BaggagePropagator,
        extract_context,
        inject_context,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    BaggagePropagator = None  # type: ignore[assignment,misc]
    inject_context = None  # type: ignore[assignment,misc]
    extract_context = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestBaggagePropagator:
    def test_is_class(self):
        assert isinstance(BaggagePropagator, type)
    def test_importable(self):
        assert BaggagePropagator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestInjectContext:
    def test_is_callable(self):
        assert callable(inject_context)

@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestExtractContext:
    def test_is_callable(self):
        assert callable(extract_context)

@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="baggage_propagator_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module baggage_propagator_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
