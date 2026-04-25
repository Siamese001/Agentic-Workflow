"""Unit tests for ``EmbeddingSemanticChunker``.

All tests use a deterministic stub embedder — no real embedding model is
loaded. This keeps tests fast (<1s) and hermetic.
"""

from __future__ import annotations

import math

import pytest

from agentic_core.knowledge.chunking.chunking_modes import (
    ChunkingEngine,
    EmbeddingSemanticChunker,
    _cosine_distance,
    _percentile,
)


# ---------------------------------------------------------------------------
# Stub embedders
# ---------------------------------------------------------------------------


def _topic_stub(groups: list[str]) -> list[list[float]]:
    """Deterministic embedder that encodes which "topic" each group is about.

    Two topics — 'alpha' and 'beta'. Each group is mapped to one of two
    orthogonal unit vectors based on which topic word it contains. This lets
    tests reason about boundaries without floating-point fuzziness.
    """
    out: list[list[float]] = []
    for g in groups:
        low = g.lower()
        if "alpha" in low and "beta" not in low:
            out.append([1.0, 0.0, 0.0])
        elif "beta" in low and "alpha" not in low:
            out.append([0.0, 1.0, 0.0])
        else:
            # Mixed / neither — put it on a third axis so distance from both
            # topic vectors is large.
            out.append([0.0, 0.0, 1.0])
    return out


def _identity_stub(groups: list[str]) -> list[list[float]]:
    """Every group gets the same vector → every distance = 0."""
    return [[1.0, 0.0] for _ in groups]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


ALPHA_BETA_TEXT = (
    "Alpha systems define sovereignty. Alpha systems operate on L0 routing. "
    "Alpha systems enforce constitutional rules.\n\n"
    "Beta protocols govern execution. Beta protocols run under L2. "
    "Beta protocols emit traces to L6."
)


# ---------------------------------------------------------------------------
# Tests for internal helpers
# ---------------------------------------------------------------------------


class TestCosineDistance:
    def test_identical_vectors_distance_zero(self):
        assert _cosine_distance([1.0, 0.0], [1.0, 0.0]) == pytest.approx(0.0)

    def test_orthogonal_vectors_distance_one(self):
        assert _cosine_distance([1.0, 0.0], [0.0, 1.0]) == pytest.approx(1.0)

    def test_opposite_vectors_distance_two(self):
        assert _cosine_distance([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(2.0)

    def test_empty_inputs_return_max_distance(self):
        assert _cosine_distance([], [1.0]) == 1.0
        assert _cosine_distance([1.0], []) == 1.0

    def test_zero_norm_returns_max_distance(self):
        assert _cosine_distance([0.0, 0.0], [1.0, 0.0]) == 1.0

    def test_mismatched_dims_return_max_distance(self):
        assert _cosine_distance([1.0, 0.0], [1.0, 0.0, 0.0]) == 1.0


class TestPercentile:
    def test_empty_returns_zero(self):
        assert _percentile([], 50.0) == 0.0

    def test_single_value(self):
        assert _percentile([5.0], 99.0) == 5.0

    def test_median_of_sorted(self):
        # median of 1..5 = 3
        assert _percentile([5.0, 1.0, 3.0, 2.0, 4.0], 50.0) == pytest.approx(3.0)

    def test_p100_is_max(self):
        assert _percentile([0.1, 0.9, 0.5], 100.0) == pytest.approx(0.9)

    def test_p0_is_min(self):
        assert _percentile([0.1, 0.9, 0.5], 0.0) == pytest.approx(0.1)

    def test_clamps_out_of_range(self):
        # 150 gets clamped to 100 → max
        assert _percentile([0.1, 0.9], 150.0) == pytest.approx(0.9)
        # -50 clamps to 0 → min
        assert _percentile([0.1, 0.9], -50.0) == pytest.approx(0.1)


# ---------------------------------------------------------------------------
# EmbeddingSemanticChunker — construction
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_requires_embedder(self):
        with pytest.raises(ValueError, match="non-None embedder"):
            EmbeddingSemanticChunker(embedder=None)  # type: ignore[arg-type]

    def test_rejects_negative_buffer_size(self):
        with pytest.raises(ValueError, match="buffer_size"):
            EmbeddingSemanticChunker(embedder=_identity_stub, buffer_size=-1)

    def test_rejects_inverted_bounds(self):
        with pytest.raises(ValueError, match="min_chunk_chars"):
            EmbeddingSemanticChunker(embedder=_identity_stub, min_chunk_chars=500, max_chunk_chars=100)

    def test_default_threshold_per_mode(self):
        assert (
            EmbeddingSemanticChunker(
                embedder=_identity_stub, breakpoint_type="percentile"
            ).breakpoint_threshold
            == 95.0
        )
        assert (
            EmbeddingSemanticChunker(embedder=_identity_stub, breakpoint_type="stdev").breakpoint_threshold
            == 3.0
        )
        assert (
            EmbeddingSemanticChunker(embedder=_identity_stub, breakpoint_type="iqr").breakpoint_threshold
            == 1.5
        )


# ---------------------------------------------------------------------------
# EmbeddingSemanticChunker — chunking behaviour
# ---------------------------------------------------------------------------


class TestChunkingBehaviour:
    def test_empty_text_returns_empty(self):
        c = EmbeddingSemanticChunker(embedder=_identity_stub)
        assert c.chunk("", doc_id="d1") == []
        assert c.chunk("   \n\n   ", doc_id="d1") == []

    def test_single_sentence_returns_single_chunk(self):
        c = EmbeddingSemanticChunker(embedder=_identity_stub, min_chunk_chars=0)
        chunks = c.chunk("Just one sentence here.", doc_id="solo")
        assert len(chunks) == 1
        assert chunks[0].content.startswith("Just one sentence")
        assert chunks[0].chunk_type == "embedding_semantic"

    def test_topic_shift_creates_boundary(self):
        # With the topic stub, alpha-sentences and beta-sentences are
        # orthogonal (distance=1.0) while same-topic pairs are distance=0.
        # Percentile=50 puts the cutoff between 0 and 1 → one boundary only.
        c = EmbeddingSemanticChunker(
            embedder=_topic_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=50.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        chunks = c.chunk(ALPHA_BETA_TEXT, doc_id="ab")
        assert len(chunks) == 2, f"expected alpha/beta split, got {len(chunks)}"
        assert "alpha" in chunks[0].content.lower()
        assert "beta" in chunks[1].content.lower()
        # No alpha/beta cross-contamination.
        assert "beta" not in chunks[0].content.lower()
        assert "alpha" not in chunks[1].content.lower()

    def test_uniform_embeddings_yield_single_chunk(self):
        # When every distance is 0, percentile threshold can never trigger.
        c = EmbeddingSemanticChunker(
            embedder=_identity_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=95.0,
            buffer_size=0,
            min_chunk_chars=0,
        )
        chunks = c.chunk(ALPHA_BETA_TEXT, doc_id="uni")
        assert len(chunks) == 1

    def test_max_chunk_chars_enforced(self):
        # Force splitting on length even with uniform embeddings.
        c = EmbeddingSemanticChunker(
            embedder=_identity_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=95.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=80,  # roughly one sentence each
        )
        chunks = c.chunk(ALPHA_BETA_TEXT, doc_id="mx")
        assert len(chunks) >= 3
        for ch in chunks:
            assert len(ch.content) <= 200  # loose upper bound incl. join spaces

    def test_min_chunk_chars_merges_small_runs(self):
        # Aggressive threshold → many small runs → min_chunk_chars=1000 forces
        # them back into a single chunk.
        c = EmbeddingSemanticChunker(
            embedder=_topic_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=10.0,  # cut very eagerly
            buffer_size=0,
            min_chunk_chars=1000,
            max_chunk_chars=10_000,
        )
        chunks = c.chunk(ALPHA_BETA_TEXT, doc_id="mn")
        assert len(chunks) == 1

    def test_embedder_size_mismatch_raises(self):
        def bad_embedder(groups: list[str]) -> list[list[float]]:
            return [[1.0]]  # wrong length regardless of input

        c = EmbeddingSemanticChunker(embedder=bad_embedder, min_chunk_chars=0)
        with pytest.raises(ValueError, match="returned"):
            c.chunk(ALPHA_BETA_TEXT, doc_id="bad")

    def test_stdev_mode(self):
        c = EmbeddingSemanticChunker(
            embedder=_topic_stub,
            breakpoint_type="stdev",
            breakpoint_threshold=0.0,  # cut at mean
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        chunks = c.chunk(ALPHA_BETA_TEXT, doc_id="sd")
        assert len(chunks) >= 2  # at least the alpha/beta split

    def test_iqr_mode(self):
        c = EmbeddingSemanticChunker(
            embedder=_topic_stub,
            breakpoint_type="iqr",
            breakpoint_threshold=0.0,  # cut above Q3
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        chunks = c.chunk(ALPHA_BETA_TEXT, doc_id="iqr")
        assert len(chunks) >= 2

    def test_metadata_shape(self):
        c = EmbeddingSemanticChunker(
            embedder=_topic_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=50.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        chunks = c.chunk(ALPHA_BETA_TEXT, doc_id="meta")
        assert chunks
        md = chunks[0].metadata
        assert md["strategy"] == "embedding_semantic"
        assert md["breakpoint_type"] == "percentile"
        assert md["breakpoint_threshold"] == 50.0
        assert md["buffer_size"] == 0
        assert md["sentence_count"] >= 1
        assert chunks[0].id.startswith("meta_embsem_")


# ---------------------------------------------------------------------------
# ChunkingEngine integration
# ---------------------------------------------------------------------------


class TestEngineRegistration:
    def test_register_and_dispatch(self):
        engine = ChunkingEngine(default_strategy="semantic_object")
        engine.register_chunker(
            "embedding_semantic",
            EmbeddingSemanticChunker(
                embedder=_topic_stub,
                breakpoint_type="percentile",
                breakpoint_threshold=50.0,
                buffer_size=0,
                min_chunk_chars=0,
                max_chunk_chars=10_000,
            ),
        )
        chunks = engine.chunk(ALPHA_BETA_TEXT, doc_id="eng", strategy="embedding_semantic")
        assert len(chunks) == 2
        assert all(c.chunk_type == "embedding_semantic" for c in chunks)

    def test_get_chunker_returns_registered_instance(self):
        engine = ChunkingEngine()
        chunker = EmbeddingSemanticChunker(embedder=_identity_stub)
        engine.register_chunker("embedding_semantic", chunker)
        assert engine.get_chunker("embedding_semantic") is chunker


# ---------------------------------------------------------------------------
# Cosine sanity: verify topic stub vectors have the expected geometry.
# ---------------------------------------------------------------------------


def test_topic_stub_vectors_orthogonal():
    a = _topic_stub(["alpha rules"])[0]
    b = _topic_stub(["beta rules"])[0]
    assert math.isclose(_cosine_distance(a, b), 1.0)
    assert math.isclose(_cosine_distance(a, a), 0.0)


# ---------------------------------------------------------------------------
# Bootstrap helper
# ---------------------------------------------------------------------------


class TestBootstrap:
    def test_bootstrap_with_injected_embedder_skips_model_load(self):
        engine = ChunkingEngine()
        chunker = engine.bootstrap_embedding_semantic(embedder=_topic_stub)
        # Registered under canonical name and reusable.
        assert engine.get_chunker("embedding_semantic") is chunker
        chunks = engine.chunk(ALPHA_BETA_TEXT, doc_id="bs", strategy="embedding_semantic")
        assert len(chunks) >= 1

    def test_bootstrap_without_sentence_transformers_raises(self, monkeypatch):
        # Force the lazy import to fail and assert a RuntimeError with a
        # helpful message bubbles up — never a swallowed ImportError.
        import builtins

        real_import = builtins.__import__

        def fail_st(name, *args, **kwargs):
            if name.startswith("sentence_transformers"):
                raise ImportError("simulated absence")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fail_st)
        engine = ChunkingEngine()
        with pytest.raises(RuntimeError, match="sentence-transformers"):
            engine.bootstrap_embedding_semantic()  # no embedder → triggers lazy import
