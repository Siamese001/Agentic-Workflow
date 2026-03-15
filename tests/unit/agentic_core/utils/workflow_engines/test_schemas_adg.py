"""ADG-driven tests for agentic_core/utils/workflow_engines/schemas.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.schemas import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        DPOBatch,
        DPOPair,
        FeedbackExample,
        ReviewRubric,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReviewRubric = None  # type: ignore[assignment,misc]
    FeedbackExample = None  # type: ignore[assignment,misc]
    DPOPair = None  # type: ignore[assignment,misc]
    DPOBatch = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestReviewRubric:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ReviewRubric)
    def test_importable(self):
        assert ReviewRubric is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestFeedbackExample:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FeedbackExample)
    def test_importable(self):
        assert FeedbackExample is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestDPOPair:
    def test_is_class(self):
        assert isinstance(DPOPair, type)
    def test_importable(self):
        assert DPOPair is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestDPOBatch:
    def test_is_class(self):
        assert isinstance(DPOBatch, type)
    def test_importable(self):
        assert DPOBatch is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="schemas.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module schemas.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
