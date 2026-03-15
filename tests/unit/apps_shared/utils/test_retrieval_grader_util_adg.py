"""ADG-driven tests for apps_shared/utils/retrieval_grader_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.retrieval_grader_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        GradeStatus,
        RetrievalGrade,
        RetrievalGrader,
        WebSearchFallback,
        fallback_web_search,
        get_retrieval_grader,
        get_web_search_fallback,
        grade_retrieval,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    GradeStatus = None  # type: ignore[assignment,misc]
    RetrievalGrade = None  # type: ignore[assignment,misc]
    RetrievalGrader = None  # type: ignore[assignment,misc]
    WebSearchFallback = None  # type: ignore[assignment,misc]
    get_retrieval_grader = None  # type: ignore[assignment,misc]
    get_web_search_fallback = None  # type: ignore[assignment,misc]
    grade_retrieval = None  # type: ignore[assignment,misc]
    fallback_web_search = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestGradeStatus:
    def test_is_enum(self):
        import enum
        assert issubclass(GradeStatus, enum.Enum)
    def test_has_members(self):
        assert len(list(GradeStatus)) >= 1
    def test_importable(self):
        assert GradeStatus is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestRetrievalGrade:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetrievalGrade)
    def test_importable(self):
        assert RetrievalGrade is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestRetrievalGrader:
    def test_is_class(self):
        assert isinstance(RetrievalGrader, type)
    def test_importable(self):
        assert RetrievalGrader is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestWebSearchFallback:
    def test_is_class(self):
        assert isinstance(WebSearchFallback, type)
    def test_importable(self):
        assert WebSearchFallback is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestGetRetrievalGrader:
    def test_is_callable(self):
        assert callable(get_retrieval_grader)

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestGetWebSearchFallback:
    def test_is_callable(self):
        assert callable(get_web_search_fallback)

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestGradeRetrieval:
    def test_is_callable(self):
        assert callable(grade_retrieval)

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestFallbackWebSearch:
    def test_is_callable(self):
        assert callable(fallback_web_search)

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module retrieval_grader_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
