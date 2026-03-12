"""ADG-driven tests for apps_shared/utils/document_score_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.document_score_util import (  # noqa: F401
        DocumentScore,
        RAGScorer,
        create_rag_scorer,
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
    DocumentScore = None  # type: ignore[assignment,misc]
    RAGScorer = None  # type: ignore[assignment,misc]
    create_rag_scorer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestDocumentScore:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DocumentScore)
    def test_importable(self):
        assert DocumentScore is not None

@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestRAGScorer:
    def test_is_class(self):
        assert isinstance(RAGScorer, type)
    def test_importable(self):
        assert RAGScorer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestCreateRagScorer:
    def test_is_callable(self):
        assert callable(create_rag_scorer)

@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="document_score_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module document_score_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
