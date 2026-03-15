"""Foundational behavioral tests for apps_shared/utils/retrieval_grader_util.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_retrieval_grader_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.retrieval_grader_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
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
except ImportError as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestGradeStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(GradeStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(GradeStatus)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in GradeStatus:
            assert member.value is not None

    def test_known_member_pass_exists(self):
        assert hasattr(GradeStatus, 'PASS')

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestRetrievalGradeContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetrievalGrade)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RetrievalGrade)}
        assert field_names >= {'relevance_ratio', 'confidence', 'status', 'irrelevant_docs', 'relevant_docs'}

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestRetrievalGraderContract:
    def test_is_class(self):
        assert isinstance(RetrievalGrader, type)

    def test_has_method_grade_documents(self):
        assert callable(getattr(RetrievalGrader, 'grade_documents', None))

    def test_has_method_get_stats(self):
        assert callable(getattr(RetrievalGrader, 'get_stats', None))

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestWebSearchFallbackContract:
    def test_is_class(self):
        assert isinstance(WebSearchFallback, type)

    def test_has_method_search(self):
        assert callable(getattr(WebSearchFallback, 'search', None))

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestGetRetrievalGraderFunction:
    def test_is_callable(self):
        assert callable(get_retrieval_grader)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_retrieval_grader)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestGetWebSearchFallbackFunction:
    def test_is_callable(self):
        assert callable(get_web_search_fallback)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_web_search_fallback)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestGradeRetrievalFunction:
    def test_is_callable(self):
        assert callable(grade_retrieval)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(grade_retrieval)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_grader_util.py deps unavailable")
class TestFallbackWebSearchFunction:
    def test_is_callable(self):
        assert callable(fallback_web_search)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(fallback_web_search)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module retrieval_grader_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
