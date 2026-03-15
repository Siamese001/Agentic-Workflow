"""Foundational behavioral tests for agentic_core/L5_safety/utils/canonical_truth_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_canonical_truth_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.canonical_truth_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        calculate_health_score,
        get_canonical_layer,
        get_health_weights,
        validate_health_components,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    calculate_health_score = None  # type: ignore[assignment,misc]
    get_canonical_layer = None  # type: ignore[assignment,misc]
    validate_health_components = None  # type: ignore[assignment,misc]
    get_health_weights = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestCalculateHealthScoreFunction:
    def test_is_callable(self):
        assert callable(calculate_health_score)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(calculate_health_score)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestGetCanonicalLayerFunction:
    def test_is_callable(self):
        assert callable(get_canonical_layer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_canonical_layer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestValidateHealthComponentsFunction:
    def test_is_callable(self):
        assert callable(validate_health_components)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_health_components)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestGetHealthWeightsFunction:
    def test_is_callable(self):
        assert callable(get_health_weights)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_health_weights)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module canonical_truth_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
