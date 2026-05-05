"""Unit tests for BGE-M3 embedder.

Tests cover:
- Singleton pattern
- Expected dimensions (1024)
- Normalization (vectors should have unit length)
- Determinism (same input → same output)
- Fail-soft behavior (empty list on error, not exception)
"""

import numpy as np
import pytest

from tools.embedders.bge_m3_embedder import (
    EXPECTED_DIMS,
    MODEL_NAME,
    BgeM3Embedder,
    embed_text,
    embed_texts,
    get_embedder,
)


class TestBgeM3Embedder:
    """Tests for BgeM3Embedder class."""

    def test_singleton_pattern(self) -> None:
        """Multiple instantiations return same object."""
        embedder1 = BgeM3Embedder()
        embedder2 = BgeM3Embedder()
        assert embedder1 is embedder2

    def test_expected_dimensions_constant(self) -> None:
        """EXPECTED_DIMS should be 1024 for BGE-M3."""
        assert EXPECTED_DIMS == 1024

    def test_model_name_constant(self) -> None:
        """MODEL_NAME should be BAAI/bge-m3."""
        assert MODEL_NAME == "BAAI/bge-m3"

    def test_embedder_dims_attribute(self) -> None:
        """Embedder instance has correct dims attribute."""
        embedder = BgeM3Embedder()
        assert embedder.dims == 1024

    def test_get_embedder_returns_singleton(self) -> None:
        """get_embedder() returns same instance."""
        e1 = get_embedder()
        e2 = get_embedder()
        assert e1 is e2


class TestEmbedFunction:
    """Tests for embed_text() convenience function."""

    @pytest.mark.skipif(
        not BgeM3Embedder().is_available(),
        reason="BGE-M3 model not available (requires sentence-transformers)",
    )
    def test_embed_returns_1024_dimensions(self) -> None:
        """Single text embedding returns 1024-dim vector."""
        result = embed_text("Tell me about a time you showed leadership.")
        assert len(result) == 1024

    @pytest.mark.skipif(
        not BgeM3Embedder().is_available(),
        reason="BGE-M3 model not available",
    )
    def test_embed_normalization(self) -> None:
        """Embeddings should be normalized (unit length)."""
        result = embed_text("Leadership behavioral question")
        vec = np.array(result)
        norm = np.linalg.norm(vec)
        assert abs(norm - 1.0) < 1e-5, f"Vector not normalized: norm={norm}"

    @pytest.mark.skipif(
        not BgeM3Embedder().is_available(),
        reason="BGE-M3 model not available",
    )
    def test_embed_determinism(self) -> None:
        """Same input should produce same embedding."""
        text = "Describe a challenging team situation."
        result1 = embed_text(text)
        result2 = embed_text(text)
        assert result1 == result2

    def test_embed_fail_soft_empty_string(self) -> None:
        """Empty string should return empty list (fail-soft)."""
        # This may work or fail depending on model availability
        # but should never raise
        try:
            result = embed_text("")
            assert isinstance(result, list)
        except Exception as exc:  # noqa: BLE001
            pytest.fail(f"embed_text should never raise: {exc}")


class TestEmbedBatchFunction:
    """Tests for embed_texts() batch function."""

    @pytest.mark.skipif(
        not BgeM3Embedder().is_available(),
        reason="BGE-M3 model not available",
    )
    def test_embed_batch_returns_correct_count(self) -> None:
        """Batch embedding returns same count as input."""
        texts = [
            "Question one about leadership",
            "Question two about teamwork",
            "Question three about conflict",
        ]
        results = embed_texts(texts, show_progress=False)
        assert len(results) == len(texts)

    @pytest.mark.skipif(
        not BgeM3Embedder().is_available(),
        reason="BGE-M3 model not available",
    )
    def test_embed_batch_all_1024_dims(self) -> None:
        """All batch results have 1024 dimensions."""
        texts = ["Question A", "Question B", "Question C"]
        results = embed_texts(texts, show_progress=False)
        for i, vec in enumerate(results):
            assert len(vec) == 1024, f"Vector {i} has wrong dimensions: {len(vec)}"

    @pytest.mark.skipif(
        not BgeM3Embedder().is_available(),
        reason="BGE-M3 model not available",
    )
    def test_embed_batch_normalization(self) -> None:
        """All batch embeddings are normalized."""
        texts = ["Question one", "Question two"]
        results = embed_texts(texts, show_progress=False)
        for i, vec in enumerate(results):
            arr = np.array(vec)
            norm = np.linalg.norm(arr)
            assert abs(norm - 1.0) < 1e-5, f"Vector {i} not normalized: norm={norm}"

    def test_embed_batch_empty_list(self) -> None:
        """Empty list returns empty list."""
        results = embed_texts([])
        assert results == []

    def test_embed_batch_fail_soft_on_error(self) -> None:
        """Batch should return list of empty lists on model failure."""
        # If model unavailable, should return empty lists not raise
        try:
            results = embed_texts(["text one", "text two"], show_progress=False)
            assert isinstance(results, list)
            assert len(results) == 2
        except Exception as exc:  # noqa: BLE001
            pytest.fail(f"embed_texts should never raise: {exc}")


class TestEmbedderAvailability:
    """Tests for embedder availability check."""

    def test_is_available_returns_bool(self) -> None:
        """is_available() returns boolean."""
        embedder = BgeM3Embedder()
        result = embedder.is_available()
        assert isinstance(result, bool)
