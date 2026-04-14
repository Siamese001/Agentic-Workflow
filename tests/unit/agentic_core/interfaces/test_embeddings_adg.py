"""Behavioral tests for agentic_core/interfaces/embeddings.py (phase: input validation, fail-fast)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


@pytest.mark.unit
class TestEmbeddingsInterface:
    # --- happy path ---

    def test_normalize_top_k_valid_passthrough(self):
        from agentic_core.interfaces.embeddings import _normalize_top_k

        assert _normalize_top_k(1) == 1
        assert _normalize_top_k(10) == 10
        assert _normalize_top_k(20) == 20

    def test_query_similarity_returns_results(self):
        from agentic_core.interfaces.embeddings import SimilarityResult, query_similarity

        mock_cache = MagicMock()
        mock_cache.query.return_value = [
            {"content_hash": "abc", "score": 0.9, "content": "hello world long text"},
        ]
        mock_mod = MagicMock()
        mock_mod.SovereignSemanticCache.return_value = mock_cache
        key = "agentic_core.L4_state.utils.memory.sovereign_semantic_cache"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = mock_mod
            results = query_similarity("find something")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert len(results) == 1
        assert isinstance(results[0], SimilarityResult)
        assert results[0].content_hash == "abc"
        assert results[0].similarity_score == 0.9

    # --- failure path ---

    def test_normalize_top_k_clamps_to_max(self):
        from agentic_core.interfaces.embeddings import _normalize_top_k

        assert _normalize_top_k(21) == 20
        assert _normalize_top_k(999) == 20

    def test_query_similarity_cache_import_error_returns_empty(self):
        from agentic_core.interfaces.embeddings import query_similarity

        key = "agentic_core.L4_state.utils.memory.sovereign_semantic_cache"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = None  # blocks import → ImportError branch
            result = query_similarity("find something")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert result == []

    def test_query_similarity_cache_runtime_error_returns_empty(self):
        from agentic_core.interfaces.embeddings import query_similarity

        mock_cache = MagicMock()
        mock_cache.query.side_effect = RuntimeError("backend down")
        mock_mod = MagicMock()
        mock_mod.SovereignSemanticCache.return_value = mock_cache
        key = "agentic_core.L4_state.utils.memory.sovereign_semantic_cache"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = mock_mod
            result = query_similarity("find something")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert result == []

    # --- edge cases ---

    def test_normalize_top_k_clamps_zero_and_negative(self):
        from agentic_core.interfaces.embeddings import _normalize_top_k

        assert _normalize_top_k(0) == 1
        assert _normalize_top_k(-5) == 1

    def test_query_similarity_empty_string_returns_empty(self):
        from agentic_core.interfaces.embeddings import query_similarity

        assert query_similarity("") == []

    def test_query_similarity_whitespace_only_returns_empty(self):
        from agentic_core.interfaces.embeddings import query_similarity

        assert query_similarity("   \t\n") == []

    def test_query_similarity_malformed_rows_skipped(self):
        from agentic_core.interfaces.embeddings import SimilarityResult, query_similarity

        mock_cache = MagicMock()
        mock_cache.query.return_value = [
            "not_a_dict",
            None,
            42,
            {"content_hash": "good", "score": 0.7, "content": "valid"},
        ]
        mock_mod = MagicMock()
        mock_mod.SovereignSemanticCache.return_value = mock_cache
        key = "agentic_core.L4_state.utils.memory.sovereign_semantic_cache"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = mock_mod
            results = query_similarity("test")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert len(results) == 1
        assert isinstance(results[0], SimilarityResult)
        assert results[0].content_hash == "good"

    def test_query_similarity_attribute_error_returns_empty(self):
        from agentic_core.interfaces.embeddings import query_similarity

        mock_cache = MagicMock()
        mock_cache.query.side_effect = AttributeError("query method not found")
        mock_mod = MagicMock()
        mock_mod.SovereignSemanticCache.return_value = mock_cache
        key = "agentic_core.L4_state.utils.memory.sovereign_semantic_cache"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = mock_mod
            result = query_similarity("find something")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert result == []

    def test_content_preview_truncated_at_preview_chars(self):
        """G3: content longer than _PREVIEW_CHARS is sliced; result length == _PREVIEW_CHARS."""
        from agentic_core.interfaces.embeddings import _PREVIEW_CHARS, query_similarity

        long_content = "a" * (_PREVIEW_CHARS + 100)
        mock_cache = MagicMock()
        mock_cache.query.return_value = [
            {"content_hash": "h1", "score": 0.8, "content": long_content},
        ]
        mock_mod = MagicMock()
        mock_mod.SovereignSemanticCache.return_value = mock_cache
        key = "agentic_core.L4_state.utils.memory.sovereign_semantic_cache"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = mock_mod
            results = query_similarity("test truncation")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert len(results) == 1
        assert len(results[0].content_preview) == _PREVIEW_CHARS
        assert results[0].content_preview == "a" * _PREVIEW_CHARS


@pytest.mark.unit
class TestEmbeddingsShimInterface:
    """G6: embeddings_shim.py must match embeddings.py exception handling."""

    def test_attribute_error_from_cache_returns_empty(self):
        """G6: embeddings_shim catches AttributeError from cache.query — returns [] not raises."""
        import sys

        from agentic_core.interfaces.embeddings_shim import query_similarity as shim_query

        mock_cache = MagicMock()
        mock_cache.query.side_effect = AttributeError("query method missing")
        mock_mod = MagicMock()
        mock_mod.SovereignSemanticCache.return_value = mock_cache
        key = "agentic_core.L4_state.utils.memory.sovereign_semantic_cache"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = mock_mod
            result = shim_query("find something")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert result == []
