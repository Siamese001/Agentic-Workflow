"""
Phase 2 Wave 2 — RetrievalAnchor Tests

Tests that:
- RetrievalAnchor requires all fields
- AnchoredResult pairs content with anchor
- enforce_anchor_coverage blocks unanchored retrieval use
- Negative: reasoning without anchors raises AnchorViolationError
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.retrieval_anchor_types import (
    AnchoredResult,
    AnchorViolationError,
    RetrievalAnchor,
    enforce_anchor_coverage,
)

pytestmark = pytest.mark.unit_min_deps


def _make_anchor(
    source_doc_id: str = "doc-001",
    chunk_id: str = "chunk-001",
    char_start: int = 0,
    char_end: int = 100,
    version_hash: str = "abc123",
) -> RetrievalAnchor:
    return RetrievalAnchor(
        source_doc_id=source_doc_id,
        chunk_id=chunk_id,
        char_start=char_start,
        char_end=char_end,
        retrieved_at_utc=RetrievalAnchor.now_utc(),
        version_hash=version_hash,
    )


class TestRetrievalAnchor:
    def test_retrieval_returns_anchors(self):
        anchor = _make_anchor()
        result = AnchoredResult(content="some retrieved text", anchor=anchor)
        assert result.anchor.source_doc_id == "doc-001"
        assert result.anchor.chunk_id == "chunk-001"
        assert result.anchor.char_start == 0
        assert result.anchor.char_end == 100
        assert result.anchor.version_hash == "abc123"
        assert result.anchor.retrieved_at_utc

    def test_anchor_to_dict_has_all_fields(self):
        anchor = _make_anchor()
        d = anchor.to_dict()
        assert set(d.keys()) == {
            "source_doc_id",
            "chunk_id",
            "char_start",
            "char_end",
            "retrieved_at_utc",
            "version_hash",
        }

    def test_anchor_rejects_empty_source_doc_id(self):
        with pytest.raises(ValueError, match="source_doc_id"):
            RetrievalAnchor(
                source_doc_id="",
                chunk_id="chunk-001",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_empty_chunk_id(self):
        with pytest.raises(ValueError, match="chunk_id"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_inverted_offsets(self):
        with pytest.raises(ValueError, match="char_end"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="chunk-001",
                char_start=100,
                char_end=50,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_empty_version_hash(self):
        with pytest.raises(ValueError, match="version_hash"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="chunk-001",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="",
            )


class TestAnchorCoverageEnforcement:
    def test_empty_retrieval_context_passes_with_no_anchors(self):
        enforce_anchor_coverage([], [])

    def test_reasoning_requires_anchors_when_retrieval_present(self):
        anchor = _make_anchor()
        result = AnchoredResult(content="text", anchor=anchor)
        with pytest.raises(AnchorViolationError) as exc_info:
            enforce_anchor_coverage([result], [])
        assert AnchorViolationError.VIOLATION_CODE in str(exc_info.value)
        assert "empty" in str(exc_info.value)

    def test_reasoning_without_anchors_is_rejected(self):
        anchor = _make_anchor(chunk_id="chunk-A")
        result = AnchoredResult(content="text", anchor=anchor)
        with pytest.raises(AnchorViolationError) as exc_info:
            enforce_anchor_coverage([result], [])
        assert "MISSING_RETRIEVAL_ANCHOR" in str(exc_info.value)

    def test_uncovered_chunk_raises_violation(self):
        anchor_a = _make_anchor(chunk_id="chunk-A")
        anchor_b = _make_anchor(chunk_id="chunk-B")
        result_a = AnchoredResult(content="text-a", anchor=anchor_a)
        result_b = AnchoredResult(content="text-b", anchor=anchor_b)
        with pytest.raises(AnchorViolationError, match="chunk-B"):
            enforce_anchor_coverage([result_a, result_b], [anchor_a])

    def test_full_coverage_passes(self):
        anchor_a = _make_anchor(chunk_id="chunk-A")
        anchor_b = _make_anchor(chunk_id="chunk-B")
        result_a = AnchoredResult(content="text-a", anchor=anchor_a)
        result_b = AnchoredResult(content="text-b", anchor=anchor_b)
        enforce_anchor_coverage([result_a, result_b], [anchor_a, anchor_b])

    def test_violation_error_code_is_constant(self):
        assert AnchorViolationError.VIOLATION_CODE == "MISSING_RETRIEVAL_ANCHOR"
