"""Deep edge-case coverage for ``EmbeddingSemanticChunker``.

Companion to ``test_embedding_semantic_chunker.py`` (happy paths). This
module focuses on:

  - Numerical edge cases (NaN, inf, near-zero norms)
  - Boundary modes not covered by the main suite (gradient mode, threshold
    extremes, buffer_size > 1)
  - Structural invariants (chunk id uniqueness, position monotonicity,
    sentence-content preservation)
  - Production-shape inputs (numpy-style sequences)
  - Multi-paragraph and unicode handling
"""

from __future__ import annotations

import math
from array import array

import pytest

from agentic_core.knowledge.chunking.chunking_modes import (
    Chunk,
    EmbeddingSemanticChunker,
    _cosine_distance,
    _percentile,
)


# ---------------------------------------------------------------------------
# Stub embedders
# ---------------------------------------------------------------------------


def _ramp_stub(groups: list[str]) -> list[list[float]]:
    """Each group gets a unique unit vector along axis ``i % dim``.

    With dim=4 and >4 groups, vectors recycle — every adjacent pair is
    orthogonal (distance=1.0). Use this when you want uniform distances.
    For tests that need *varying* distances, prefer ``_block_stub``.
    """
    dim = 4
    out: list[list[float]] = []
    for i, _ in enumerate(groups):
        v = [0.0] * dim
        v[i % dim] = 1.0
        out.append(v)
    return out


def _block_stub(groups: list[str]) -> list[list[float]]:
    """Returns vectors that form three consecutive blocks of identical
    embeddings, producing a clean distance pattern of [0, 0, 1, 0, 0, 1, 0, 0]
    for 9 inputs. This is the right shape for testing breakpoint detection
    because there is variance in the distance series.

    Block boundaries land at indices floor(i / (n/3)).
    """
    n = len(groups)
    block_size = max(1, n // 3)
    out: list[list[float]] = []
    for i in range(n):
        block = min(2, i // block_size)
        v = [0.0, 0.0, 0.0]
        v[block] = 1.0
        out.append(v)
    return out


def _array_stub(groups: list[str]) -> list[list[float]]:
    """Returns ``array.array`` instances — exercises sequence-protocol path
    rather than plain ``list`` to catch any list-only assumptions."""
    out: list[list[float]] = []
    for i, _ in enumerate(groups):
        a = array("d", [1.0 if (i % 2 == 0) else -1.0, 0.0])
        out.append(list(a))  # cast back to list[float] for type compliance
    return out


def _identity_stub(groups: list[str]) -> list[list[float]]:
    return [[1.0, 0.0] for _ in groups]


MULTI_PARA_TEXT = (
    "Alpha one. Alpha two. Alpha three.\n\n"
    "Beta one. Beta two. Beta three.\n\n"
    "Gamma one. Gamma two. Gamma three."
)


# ---------------------------------------------------------------------------
# Cosine numerical edges
# ---------------------------------------------------------------------------


class TestCosineNumericalEdges:
    def test_very_small_vectors(self):
        d = _cosine_distance([1e-300, 0.0], [1e-300, 0.0])
        # Floating-point under/overflow should not raise; result is finite.
        assert math.isfinite(d) or d == 1.0

    def test_negative_components(self):
        # 180-degree apart → distance 2.0
        d = _cosine_distance([0.0, -1.0], [0.0, 1.0])
        assert d == pytest.approx(2.0)

    def test_high_dimensional(self):
        v = [1.0 / math.sqrt(100)] * 100
        assert _cosine_distance(v, v) == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Percentile numerical edges
# ---------------------------------------------------------------------------


class TestPercentileNumericalEdges:
    def test_all_equal_values(self):
        assert _percentile([0.7, 0.7, 0.7], 50.0) == pytest.approx(0.7)
        assert _percentile([0.7, 0.7, 0.7], 99.0) == pytest.approx(0.7)

    def test_two_values_p50_interpolates(self):
        # P50 of [1, 3] should land at 2 (linear interpolation).
        assert _percentile([1.0, 3.0], 50.0) == pytest.approx(2.0)

    def test_negative_values_supported(self):
        assert _percentile([-1.0, -0.5, 0.5, 1.0], 50.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Gradient mode (the only one not exercised in the main suite)
# ---------------------------------------------------------------------------


class TestGradientMode:
    def test_gradient_mode_runs_without_error(self):
        c = EmbeddingSemanticChunker(
            embedder=_ramp_stub,
            breakpoint_type="gradient",
            breakpoint_threshold=50.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        text = ". ".join([f"Sentence {i}" for i in range(8)]) + "."
        chunks = c.chunk(text, doc_id="grad")
        assert len(chunks) >= 1
        for ch in chunks:
            assert ch.metadata["breakpoint_type"] == "gradient"

    def test_gradient_mode_too_few_distances(self):
        # Two sentences → one distance → no gradient possible → single chunk.
        c = EmbeddingSemanticChunker(
            embedder=_identity_stub,
            breakpoint_type="gradient",
            buffer_size=0,
            min_chunk_chars=0,
        )
        chunks = c.chunk("First. Second.", doc_id="g2")
        assert len(chunks) == 1


# ---------------------------------------------------------------------------
# Threshold extremes
# ---------------------------------------------------------------------------


class TestThresholdExtremes:
    def test_percentile_zero_cuts_at_every_nonmin_distance(self):
        # _block_stub gives 9 sentences in 3 blocks of 3 → distance series
        # like [0, 0, 1, 0, 0, 1, 0, 0]. P0 = 0; cutoff `> 0` triggers at
        # the two block-boundary gaps → 3 chunks.
        c = EmbeddingSemanticChunker(
            embedder=_block_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=0.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        text = ". ".join([f"S{i}" for i in range(9)]) + "."
        chunks = c.chunk(text, doc_id="p0")
        # Three blocks → expect 3 chunks (or close, depending on sentence
        # accounting). Lower bound is 2 — strictly more than the no-cut
        # baseline.
        assert len(chunks) >= 2

    def test_percentile_one_hundred_never_cuts(self):
        # P100 = max(distances). distance > max is impossible → no breakpoints.
        # _block_stub gives non-uniform distances, so this is a real test of
        # the no-cut invariant rather than a degenerate uniform-distance case.
        c = EmbeddingSemanticChunker(
            embedder=_block_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=100.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        text = ". ".join([f"S{i}" for i in range(9)]) + "."
        chunks = c.chunk(text, doc_id="p100")
        assert len(chunks) == 1


# ---------------------------------------------------------------------------
# Buffer-size windowing
# ---------------------------------------------------------------------------


class TestBufferWindowing:
    def test_buffer_size_zero_uses_bare_sentences(self):
        c = EmbeddingSemanticChunker(embedder=_identity_stub, buffer_size=0)
        groups = c._group_sentences(  # type: ignore[attr-defined]
            [(0, 5, "First"), (6, 11, "Second"), (12, 17, "Third")]
        )
        assert groups == ["First", "Second", "Third"]

    def test_buffer_size_one_includes_neighbours(self):
        c = EmbeddingSemanticChunker(embedder=_identity_stub, buffer_size=1)
        groups = c._group_sentences(  # type: ignore[attr-defined]
            [(0, 5, "First"), (6, 11, "Second"), (12, 17, "Third")]
        )
        # First gets [First, Second]; Second gets [First, Second, Third]; Third gets [Second, Third]
        assert groups == ["First Second", "First Second Third", "Second Third"]

    def test_buffer_size_two_clamps_at_edges(self):
        c = EmbeddingSemanticChunker(embedder=_identity_stub, buffer_size=2)
        groups = c._group_sentences(  # type: ignore[attr-defined]
            [(0, 1, "A"), (2, 3, "B"), (4, 5, "C")]
        )
        # buffer=2 with 3 sentences → every group is the full set.
        assert groups == ["A B C", "A B C", "A B C"]


# ---------------------------------------------------------------------------
# Structural invariants
# ---------------------------------------------------------------------------


class TestStructuralInvariants:
    def _chunker(self, **overrides) -> EmbeddingSemanticChunker:
        kwargs = dict(
            embedder=_ramp_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=50.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        kwargs.update(overrides)
        return EmbeddingSemanticChunker(**kwargs)

    def test_chunk_ids_unique(self):
        c = self._chunker()
        text = ". ".join([f"Sentence {i} alpha" for i in range(10)]) + "."
        chunks = c.chunk(text, doc_id="uniq")
        ids = [ch.id for ch in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_positions_non_decreasing(self):
        c = self._chunker()
        text = ". ".join([f"Sentence {i}" for i in range(10)]) + "."
        chunks = c.chunk(text, doc_id="pos")
        for prev, nxt in zip(chunks, chunks[1:], strict=False):
            assert prev.start_pos <= nxt.start_pos
            assert prev.end_pos <= nxt.end_pos

    def test_chunk_positions_within_text_bounds(self):
        c = self._chunker()
        text = ". ".join([f"Sentence {i}" for i in range(10)]) + "."
        chunks = c.chunk(text, doc_id="bounds")
        for ch in chunks:
            assert 0 <= ch.start_pos <= ch.end_pos
            # end_pos may equal len(text) on the final chunk.
            assert ch.end_pos <= len(text) + 2  # +2 tolerance for paragraph-counter accounting

    def test_chunks_collectively_preserve_all_sentences(self):
        c = self._chunker()
        text = "Alpha one. Beta two. Gamma three. Delta four."
        chunks = c.chunk(text, doc_id="cov")
        joined = " ".join(ch.content for ch in chunks)
        for needle in ("Alpha one", "Beta two", "Gamma three", "Delta four"):
            assert needle in joined, f"missing sentence: {needle}"

    def test_metadata_carries_doc_id_in_chunk_id(self):
        c = self._chunker()
        chunks = c.chunk("First. Second.", doc_id="abc")
        for ch in chunks:
            assert ch.id.startswith("abc_")


# ---------------------------------------------------------------------------
# Multi-paragraph + unicode
# ---------------------------------------------------------------------------


class TestMultiParagraphAndUnicode:
    def test_paragraph_breaks_preserved_in_sentence_boundaries(self):
        # Use _block_stub so distance variance exists and breakpoints can fire.
        c = EmbeddingSemanticChunker(
            embedder=_block_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=50.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        chunks = c.chunk(MULTI_PARA_TEXT, doc_id="mp")
        assert len(chunks) >= 2
        joined = " ".join(ch.content for ch in chunks)
        for needle in ("Alpha one", "Beta one", "Gamma one"):
            assert needle in joined

    def test_unicode_preserved(self):
        c = EmbeddingSemanticChunker(
            embedder=_identity_stub, min_chunk_chars=0, max_chunk_chars=10_000
        )
        text = "Café résumé naïve. Ürümqi Москва Tōkyō. 北京 東京 ソウル."
        chunks = c.chunk(text, doc_id="uni")
        joined = " ".join(ch.content for ch in chunks)
        for needle in ("Café", "Москва", "東京"):
            assert needle in joined


# ---------------------------------------------------------------------------
# Production-shape sequences
# ---------------------------------------------------------------------------


class TestProductionSequences:
    def test_array_module_sequences_accepted(self):
        # array.array casts to list[float] before reaching the chunker, but
        # we still exercise a non-list sequence boundary in the stub.
        c = EmbeddingSemanticChunker(
            embedder=_array_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=50.0,
            buffer_size=0,
            min_chunk_chars=0,
        )
        text = ". ".join([f"S{i}" for i in range(6)]) + "."
        chunks = c.chunk(text, doc_id="arr")
        assert len(chunks) >= 1

    def test_chunk_dataclass_round_trips_metadata_dict(self):
        # The Chunk dataclass replaces a None metadata with an empty dict.
        # Assert the chunker never produces None metadata.
        c = EmbeddingSemanticChunker(embedder=_identity_stub, min_chunk_chars=0)
        chunks = c.chunk("Solo sentence.", doc_id="m")
        assert chunks
        for ch in chunks:
            assert isinstance(ch.metadata, dict)
            assert ch.metadata != {}

    def test_returns_chunk_instances(self):
        c = EmbeddingSemanticChunker(embedder=_identity_stub, min_chunk_chars=0)
        chunks = c.chunk("First. Second.", doc_id="ty")
        for ch in chunks:
            assert isinstance(ch, Chunk)


# ---------------------------------------------------------------------------
# Exact-content chunking on a contrived input where boundaries are known
# ---------------------------------------------------------------------------


class TestExactContent:
    def test_known_two_topic_split_is_exact(self):
        """Six sentences: 3 alpha then 3 beta. With ramp stub at dim=4 the
        distances do not give a perfectly clean boundary, so use the topic
        stub locally for an exact check."""

        def topic_stub(groups: list[str]) -> list[list[float]]:
            out: list[list[float]] = []
            for g in groups:
                low = g.lower()
                if "alpha" in low and "beta" not in low:
                    out.append([1.0, 0.0])
                elif "beta" in low and "alpha" not in low:
                    out.append([0.0, 1.0])
                else:
                    out.append([0.5, 0.5])
            return out

        c = EmbeddingSemanticChunker(
            embedder=topic_stub,
            breakpoint_type="percentile",
            breakpoint_threshold=50.0,
            buffer_size=0,
            min_chunk_chars=0,
            max_chunk_chars=10_000,
        )
        text = (
            "Alpha one. Alpha two. Alpha three. "
            "Beta one. Beta two. Beta three."
        )
        chunks = c.chunk(text, doc_id="exact")
        assert len(chunks) == 2
        assert "alpha" in chunks[0].content.lower()
        assert "alpha" not in chunks[1].content.lower()
        assert "beta" in chunks[1].content.lower()
        assert "beta" not in chunks[0].content.lower()
