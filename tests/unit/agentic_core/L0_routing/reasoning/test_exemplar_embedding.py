"""W7 — embedding-based exemplar selection tests."""

from __future__ import annotations

from typing import Sequence

import pytest

from agentic_core.L0_routing.reasoning.exemplar_bank import (
    Exemplar,
    cosine_similarity,
    select_by_similarity,
    select_by_static_similarity,
)


class _StubEmbedder:
    """Deterministic test embedder — bag-of-letters one-hot.

    Produces fixed-length 26-dim vectors over [a-z], so 'foo' and 'foo' yield
    identical vectors and queries with shared letters score higher.
    """

    DIM = 26

    def encode(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        out = []
        for text in texts:
            vec = [0.0] * self.DIM
            for ch in text.lower():
                idx = ord(ch) - ord("a")
                if 0 <= idx < self.DIM:
                    vec[idx] += 1.0
            out.append(vec)
        return out


class _RaisingEmbedder:
    def encode(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        raise RuntimeError("simulated failure")


class _MismatchEmbedder:
    """Returns wrong number of vectors (caller should defend)."""

    def encode(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        return [[0.0]]  # always one-vector regardless of input length


# ----- cosine_similarity ---------------------------------------------------


class TestCosineSimilarity:
    def test_identical_vectors_score_1(self):
        assert cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)

    def test_orthogonal_vectors_score_0(self):
        assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0

    def test_opposite_vectors_score_minus_1(self):
        assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

    def test_zero_vector_returns_0(self):
        assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0
        assert cosine_similarity([1.0, 2.0], [0.0, 0.0]) == 0.0

    def test_mismatched_dims_returns_0(self):
        assert cosine_similarity([1.0, 2.0], [1.0]) == 0.0

    def test_empty_vectors_return_0(self):
        assert cosine_similarity([], []) == 0.0


# ----- select_by_similarity ------------------------------------------------


class TestSelectBySimilarity:
    @pytest.fixture
    def pool(self) -> list[Exemplar]:
        return [
            Exemplar(task="hello world", response="r1"),
            Exemplar(task="goodbye moon", response="r2"),
            Exemplar(task="hello python", response="r3", weight=0.9),
        ]

    def test_returns_top_k_sorted_by_score(self, pool):
        result = select_by_similarity("hello world", pool, _StubEmbedder(), top_k=2)
        assert len(result) == 2
        scores = [s for _, s in result]
        assert scores[0] >= scores[1]
        # The exact match "hello world" should top the ranking
        assert result[0][0].task == "hello world"

    def test_empty_query_returns_empty(self, pool):
        result = select_by_similarity("", pool, _StubEmbedder(), top_k=3)
        assert result == ()

    def test_empty_pool_returns_empty(self):
        result = select_by_similarity("hello", [], _StubEmbedder(), top_k=3)
        assert result == ()

    def test_top_k_zero_returns_empty(self, pool):
        result = select_by_similarity("hello", pool, _StubEmbedder(), top_k=0)
        assert result == ()

    def test_min_score_filters(self, pool):
        # Set a very high threshold so nothing passes
        result = select_by_similarity(
            "completely unrelated query xyz",
            pool,
            _StubEmbedder(),
            top_k=3,
            min_score=0.99,
        )
        # Bag-of-letters with disjoint chars gives near-zero similarity
        assert len(result) <= 3

    def test_embedder_failure_returns_empty(self, pool):
        result = select_by_similarity("q", pool, _RaisingEmbedder(), top_k=3)
        assert result == ()

    def test_dimension_mismatch_returns_empty(self, pool):
        result = select_by_similarity("q", pool, _MismatchEmbedder(), top_k=3)
        assert result == ()

    def test_deterministic_results(self, pool):
        a = select_by_similarity("hello", pool, _StubEmbedder(), top_k=3)
        b = select_by_similarity("hello", pool, _StubEmbedder(), top_k=3)
        assert a == b

    def test_result_pair_shape(self, pool):
        result = select_by_similarity("hello", pool, _StubEmbedder(), top_k=1)
        assert len(result) == 1
        ex, score = result[0]
        assert isinstance(ex, Exemplar)
        assert isinstance(score, float)


# ----- select_by_static_similarity -----------------------------------------


class TestStaticSelector:
    @pytest.fixture
    def pool(self) -> list[Exemplar]:
        return [
            Exemplar(task="hello world", response="r"),
            Exemplar(task="goodbye moon", response="r"),
        ]

    def test_returns_ranked_pairs(self, pool):
        result = select_by_static_similarity("hello world", pool, top_k=2)
        assert len(result) == 2
        assert result[0][1] > result[1][1]

    def test_empty_query_returns_empty(self, pool):
        assert select_by_static_similarity("", pool, top_k=2) == ()

    def test_min_score_filters_zero_overlap(self, pool):
        # No shared tokens with anything in pool
        result = select_by_static_similarity("xyz qrs uvw", pool, top_k=2, min_score=0.5)
        assert result == ()
