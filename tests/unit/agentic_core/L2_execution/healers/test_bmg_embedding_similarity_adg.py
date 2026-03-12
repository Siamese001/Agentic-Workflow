"""ADG-driven tests for agentic_core/L2_execution/healers/bmg_embedding_similarity.py — fan_in=14.

Tests cover the contractual interface without requiring ML dependencies.
Model-dependent tests are skipped if sentence-transformers is unavailable.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestBmgPublicAPI:
    """Public symbols must be importable and have correct signatures."""

    def test_bmg_cosine_similarity_importable(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_cosine_similarity
        assert callable(bmg_cosine_similarity)

    def test_bmg_embed_text_importable(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text
        assert callable(bmg_embed_text)

    def test_clear_model_cache_importable(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import clear_model_cache
        assert callable(clear_model_cache)

    def test_all_exports_present(self):
        import agentic_core.L2_execution.healers.bmg_embedding_similarity as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"


class TestBmgContractWithoutModel:
    """Guard clauses fire correctly before any model load attempt."""

    def test_empty_candidates_raises_value_error(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_cosine_similarity
        with pytest.raises(ValueError, match="candidates must be non-empty"):
            bmg_cosine_similarity("query", [])

    def test_clear_model_cache_is_idempotent(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import clear_model_cache
        clear_model_cache()
        clear_model_cache()  # second call must not raise


class TestBmgWithModel:
    """Model-dependent tests — skipped if sentence-transformers is unavailable."""

    @pytest.fixture(autouse=True)
    def require_sentence_transformers(self):
        pytest.importorskip("sentence_transformers", reason="sentence-transformers not installed")

    def test_cosine_similarity_returns_float_in_range(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import (
            bmg_cosine_similarity,
            clear_model_cache,
        )
        clear_model_cache()
        result = bmg_cosine_similarity("hello world", ["hello world", "foo bar"])
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_identical_strings_high_similarity(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import (
            bmg_cosine_similarity,
            clear_model_cache,
        )
        clear_model_cache()
        result = bmg_cosine_similarity("test string", ["test string"])
        assert result > 0.95

    def test_embed_text_returns_list_of_floats(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import (
            bmg_embed_text,
            clear_model_cache,
        )
        clear_model_cache()
        vec = bmg_embed_text("hello")
        assert isinstance(vec, list)
        assert len(vec) > 0
        assert all(isinstance(v, float) for v in vec)

    def test_embed_text_vector_is_normalized(self):
        import math
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text
        vec = bmg_embed_text("normalize me")
        norm = math.sqrt(sum(v * v for v in vec))
        assert abs(norm - 1.0) < 1e-4
