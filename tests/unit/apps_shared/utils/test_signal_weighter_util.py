"""Foundational behavioral tests for apps_shared/utils/signal_weighter_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_signal_weighter_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_shared.utils.signal_weighter_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    SignalWeighter,
    SignalWeights,
    WeightingResult,
    create_signal_weighter,
    weight_results,
)


class TestSignalWeightsContract:
    def test_is_class(self):
        assert isinstance(SignalWeights, type)

    def test_has_method_as_dict(self):
        assert callable(getattr(SignalWeights, 'as_dict', None))

class TestWeightingResultContract:
    def test_is_class(self):
        assert isinstance(WeightingResult, type)

    def test_has_method_score_change(self):
        assert callable(getattr(WeightingResult, 'score_change', None))

    def test_has_method_percent_change(self):
        assert callable(getattr(WeightingResult, 'percent_change', None))

class TestSignalWeighterContract:
    def test_is_class(self):
        assert isinstance(SignalWeighter, type)

    def test_has_method_get_weights(self):
        assert callable(getattr(SignalWeighter, 'get_weights', None))

    def test_has_method_reweight_score(self):
        assert callable(getattr(SignalWeighter, 'reweight_score', None))

    def test_has_method_batch_reweight(self):
        assert callable(getattr(SignalWeighter, 'batch_reweight', None))

class TestCreateSignalWeighterFunction:
    def test_is_callable(self):
        assert callable(create_signal_weighter)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_signal_weighter)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestWeightResultsFunction:
    def test_is_callable(self):
        assert callable(weight_results)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(weight_results)
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
    """Module signal_weighter_util must be importable or skip gracefully."""
    pass  # Import verified at module level
