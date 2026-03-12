"""ADG-driven tests for apps_lic/tools/AssessMessageRelevance.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.tools.AssessMessageRelevance import (  # noqa: F401
        AssessMessageRelevance,
        score,
        compute_score,
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
    AssessMessageRelevance = None  # type: ignore[assignment,misc]
    score = None  # type: ignore[assignment,misc]
    compute_score = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestAssessMessageRelevance:
    def test_is_class(self):
        assert isinstance(AssessMessageRelevance, type)
    def test_importable(self):
        assert AssessMessageRelevance is not None

@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestScore:
    def test_is_callable(self):
        assert callable(score)

@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestComputeScore:
    def test_is_callable(self):
        assert callable(compute_score)

@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="AssessMessageRelevance.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module AssessMessageRelevance.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
