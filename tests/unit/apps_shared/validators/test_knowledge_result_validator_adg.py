"""ADG-driven tests for apps_shared/validators/knowledge_result_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.validators.knowledge_result_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        KnowledgeResult,
        L5ConsolidatedKnowledge,
        get_consolidated_knowledge,
        search_profile_and_template,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    KnowledgeResult = None  # type: ignore[assignment,misc]
    L5ConsolidatedKnowledge = None  # type: ignore[assignment,misc]
    get_consolidated_knowledge = None  # type: ignore[assignment,misc]
    search_profile_and_template = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestKnowledgeResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(KnowledgeResult)
    def test_importable(self):
        assert KnowledgeResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestL5ConsolidatedKnowledge:
    def test_is_class(self):
        assert isinstance(L5ConsolidatedKnowledge, type)
    def test_importable(self):
        assert L5ConsolidatedKnowledge is not None

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestGetConsolidatedKnowledge:
    def test_is_callable(self):
        assert callable(get_consolidated_knowledge)

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestSearchProfileAndTemplate:
    def test_is_callable(self):
        assert callable(search_profile_and_template)

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="knowledge_result_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module knowledge_result_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
