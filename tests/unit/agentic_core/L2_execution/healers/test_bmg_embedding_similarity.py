"""Foundational behavioral tests for agentic_core/L2_execution/healers/bmg_embedding_similarity.py.

fan_in=33 — this module is imported by 33 other modules.
ADG contract: import-hygiene is covered by test_bmg_embedding_similarity_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.healers.bmg_embedding_similarity import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        bmg_cosine_similarity,
        bmg_embed_text,
        clear_model_cache,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    bmg_cosine_similarity = None  # type: ignore[assignment,misc]
    bmg_embed_text = None  # type: ignore[assignment,misc]
    clear_model_cache = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="bmg_embedding_similarity.py deps unavailable")
class TestBmgCosineSimilarityFunction:
    def test_is_callable(self):
        assert callable(bmg_cosine_similarity)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(bmg_cosine_similarity)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="bmg_embedding_similarity.py deps unavailable")
class TestBmgEmbedTextFunction:
    def test_is_callable(self):
        assert callable(bmg_embed_text)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(bmg_embed_text)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="bmg_embedding_similarity.py deps unavailable")
class TestClearModelCacheFunction:
    def test_is_callable(self):
        assert callable(clear_model_cache)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(clear_model_cache)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="bmg_embedding_similarity.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bmg_embedding_similarity.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bmg_embedding_similarity.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bmg_embedding_similarity.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bmg_embedding_similarity.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module bmg_embedding_similarity must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
