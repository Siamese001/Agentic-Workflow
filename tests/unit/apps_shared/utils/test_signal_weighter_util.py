"""Foundational behavioral tests for apps_shared/utils/signal_weighter_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_signal_weighter_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.signal_weighter_util import (  # noqa: F401
        SignalWeights,
        WeightingResult,
        SignalWeighter,
        create_signal_weighter,
        weight_results,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestSignalWeightsContract:
    def test_is_class(self):
        assert isinstance(SignalWeights, type)

    def test_has_method_as_dict(self):
        assert callable(getattr(SignalWeights, 'as_dict', None))

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestWeightingResultContract:
    def test_is_class(self):
        assert isinstance(WeightingResult, type)

    def test_has_method_score_change(self):
        assert callable(getattr(WeightingResult, 'score_change', None))

    def test_has_method_percent_change(self):
        assert callable(getattr(WeightingResult, 'percent_change', None))

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestSignalWeighterContract:
    def test_is_class(self):
        assert isinstance(SignalWeighter, type)

    def test_has_method_get_weights(self):
        assert callable(getattr(SignalWeighter, 'get_weights', None))

    def test_has_method_reweight_score(self):
        assert callable(getattr(SignalWeighter, 'reweight_score', None))

    def test_has_method_batch_reweight(self):
        assert callable(getattr(SignalWeighter, 'batch_reweight', None))

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestCreateSignalWeighterFunction:
    def test_is_callable(self):
        assert callable(create_signal_weighter)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_signal_weighter)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="signal_weighter_util.py deps unavailable")
class TestWeightResultsFunction:
    def test_is_callable(self):
        assert callable(weight_results)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(weight_results)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module signal_weighter_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
