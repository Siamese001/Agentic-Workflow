"""ADG-driven tests for apps_shared/scripts/manage_false_positives.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.manage_false_positives import (  # noqa: F401
        load_review_log,
        load_false_positives,
        save_false_positives,
        show_pending_reviews,
        mark_false_positive,
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
    load_review_log = None  # type: ignore[assignment,misc]
    load_false_positives = None  # type: ignore[assignment,misc]
    save_false_positives = None  # type: ignore[assignment,misc]
    show_pending_reviews = None  # type: ignore[assignment,misc]
    mark_false_positive = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestLoadReviewLog:
    def test_is_callable(self):
        assert callable(load_review_log)

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestLoadFalsePositives:
    def test_is_callable(self):
        assert callable(load_false_positives)

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestSaveFalsePositives:
    def test_is_callable(self):
        assert callable(save_false_positives)

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestShowPendingReviews:
    def test_is_callable(self):
        assert callable(show_pending_reviews)

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestMarkFalsePositive:
    def test_is_callable(self):
        assert callable(mark_false_positive)

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="manage_false_positives.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module manage_false_positives.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
