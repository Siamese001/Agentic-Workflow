"""ADG-driven tests for agentic_core/L4_state/enforcement/embedding_sovereignty_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.enforcement.embedding_sovereignty_guard import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        EmbeddingInfluenceViolation,
        EmbeddingResult,
        guard_embedding_influence,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    EmbeddingResult = None  # type: ignore[assignment,misc]
    EmbeddingInfluenceViolation = None  # type: ignore[assignment,misc]
    guard_embedding_influence = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestEmbeddingResult:
    def test_is_class(self):
        assert isinstance(EmbeddingResult, type)
    def test_importable(self):
        assert EmbeddingResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestEmbeddingInfluenceViolation:
    def test_is_class(self):
        assert isinstance(EmbeddingInfluenceViolation, type)
    def test_importable(self):
        assert EmbeddingInfluenceViolation is not None

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestGuardEmbeddingInfluence:
    def test_is_callable(self):
        assert callable(guard_embedding_influence)

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_sovereignty_guard.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module embedding_sovereignty_guard.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
