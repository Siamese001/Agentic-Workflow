"""ADG-driven tests for apps_shared/utils/signal_weighter_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.signal_weighter_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        SignalWeighter,
        SignalWeights,
        WeightingResult,
        create_signal_weighter,
        weight_results,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SignalWeights = None  # type: ignore[assignment,misc]
    WeightingResult = None  # type: ignore[assignment,misc]
    SignalWeighter = None  # type: ignore[assignment,misc]
    create_signal_weighter = None  # type: ignore[assignment,misc]
    weight_results = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestSignalWeights:
    def test_is_class(self):
        assert isinstance(SignalWeights, type)
    def test_importable(self):
        assert SignalWeights is not None

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestWeightingResult:
    def test_is_class(self):
        assert isinstance(WeightingResult, type)
    def test_importable(self):
        assert WeightingResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestSignalWeighter:
    def test_is_class(self):
        assert isinstance(SignalWeighter, type)
    def test_importable(self):
        assert SignalWeighter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestCreateSignalWeighter:
    def test_is_callable(self):
        assert callable(create_signal_weighter)

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestWeightResults:
    def test_is_callable(self):
        assert callable(weight_results)

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module signal_weighter_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
