"""
Phase 8 — Wave 1 Tests: CitationBundle model + deterministic validation.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.citation_bundle_types import (
    CitationBundle,
    build_citation_bundle,
)
from agentic_core.L4_state.types.retrieval_anchor_types import RetrievalAnchor

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"
_RH = "a" * 64


def _make_anchor(
    source_doc_id: str = "doc-A",
    chunk_id: str = "chunk-1",
    char_start: int = 0,
    char_end: int = 10,
    version_hash: str = "vh-1",
) -> RetrievalAnchor:
    return RetrievalAnchor(
        source_doc_id=source_doc_id,
        chunk_id=chunk_id,
        char_start=char_start,
        char_end=char_end,
        retrieved_at_utc=_TS,
        version_hash=version_hash,
    )


def _make_bundle(anchors: list[RetrievalAnchor] | None = None, **overrides) -> CitationBundle:
    defaults: dict = {
        "schema_version": 1,
        "request_hash": _RH,
        "anchors": anchors if anchors is not None else [_make_anchor()],
    }
    defaults.update(overrides)
    return CitationBundle(**defaults)


class TestCitationBundleHashStable:
    def test_citation_bundle_hash_stable(self):
        """Same inputs produce the same citation_hash on repeated construction."""
        b1 = _make_bundle()
        b2 = _make_bundle()
        assert b1.citation_hash == b2.citation_hash
        assert len(b1.citation_hash) == 64

    def test_hash_changes_with_request_hash(self):
        b1 = _make_bundle(request_hash="a" * 64)
        b2 = _make_bundle(request_hash="b" * 64)
        assert b1.citation_hash != b2.citation_hash

    def test_hash_changes_with_anchors(self):
        b1 = _make_bundle(anchors=[_make_anchor(chunk_id="chunk-X")])
        b2 = _make_bundle(anchors=[_make_anchor(chunk_id="chunk-Y")])
        assert b1.citation_hash != b2.citation_hash

    def test_hash_changes_with_version_hash(self):
        b1 = _make_bundle(anchors=[_make_anchor(version_hash="vh-1")])
        b2 = _make_bundle(anchors=[_make_anchor(version_hash="vh-2")])
        assert b1.citation_hash != b2.citation_hash

    def test_citation_hash_excluded_from_canonical_bytes(self):
        b = _make_bundle()
        assert b"citation_hash" not in b.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        b1 = _make_bundle()
        b2 = _make_bundle()
        assert b1.canonical_bytes() == b2.canonical_bytes()

    def test_volatile_field_excluded_from_canonical_bytes(self):
        """retrieved_at_utc is volatile — must not appear in canonical_bytes."""
        b = _make_bundle()
        assert b"retrieved_at_utc" not in b.canonical_bytes()

    def test_hash_stable_across_different_retrieved_at(self):
        """Two anchors differing only in retrieved_at_utc must produce the same hash."""
        a1 = RetrievalAnchor(
            source_doc_id="doc-A",
            chunk_id="chunk-1",
            char_start=0,
            char_end=10,
            retrieved_at_utc="2026-01-01T00:00:00Z",
            version_hash="vh-1",
        )
        a2 = RetrievalAnchor(
            source_doc_id="doc-A",
            chunk_id="chunk-1",
            char_start=0,
            char_end=10,
            retrieved_at_utc="2026-02-01T00:00:00Z",
            version_hash="vh-1",
        )
        b1 = _make_bundle(anchors=[a1])
        b2 = _make_bundle(anchors=[a2])
        assert b1.citation_hash == b2.citation_hash


class TestCitationBundleRequiresAnchorsWhenRetrievalUsed:
    def test_citation_bundle_requires_anchors_when_retrieval_used(self):
        """
        CitationBundle with empty anchors list is structurally valid
        (the enforcement of non-empty is done by enforce_citations_for_retrieval).
        But build_citation_bundle with non-empty anchors must succeed.
        """
        b = build_citation_bundle(request_hash=_RH, anchors=[_make_anchor()])
        assert len(b.anchors) == 1

    def test_empty_anchors_list_is_allowed_in_bundle(self):
        """CitationBundle itself allows empty anchors — enforcement is at the seam."""
        b = _make_bundle(anchors=[])
        assert b.anchors == []
        assert len(b.citation_hash) == 64

    def test_multiple_anchors_stored(self):
        anchors = [
            _make_anchor(chunk_id="chunk-1"),
            _make_anchor(chunk_id="chunk-2"),
        ]
        b = _make_bundle(anchors=anchors)
        assert len(b.anchors) == 2

    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            _make_bundle(schema_version=99)

    def test_empty_request_hash_raises(self):
        with pytest.raises(ValueError, match="request_hash"):
            _make_bundle(request_hash="")

    def test_non_list_anchors_raises(self):
        with pytest.raises(TypeError, match="anchors"):
            CitationBundle(
                schema_version=1,
                request_hash=_RH,
                anchors="not-a-list",  # type: ignore[arg-type]
            )


class TestAnchorOrderingDeterministic:
    def test_anchor_ordering_deterministic(self):
        """
        Anchors in canonical_bytes must be sorted by (source_doc_id, chunk_id, char_start)
        regardless of construction order.
        """
        anchors_unsorted = [
            _make_anchor(source_doc_id="doc-Z", chunk_id="chunk-1", char_start=0, char_end=5),
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-1", char_start=0, char_end=5),
            _make_anchor(source_doc_id="doc-M", chunk_id="chunk-1", char_start=0, char_end=5),
        ]
        anchors_sorted = [
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-1", char_start=0, char_end=5),
            _make_anchor(source_doc_id="doc-M", chunk_id="chunk-1", char_start=0, char_end=5),
            _make_anchor(source_doc_id="doc-Z", chunk_id="chunk-1", char_start=0, char_end=5),
        ]
        b1 = _make_bundle(anchors=anchors_unsorted)
        b2 = _make_bundle(anchors=anchors_sorted)
        assert b1.citation_hash == b2.citation_hash

    def test_anchors_stored_sorted_by_source_doc_id(self):
        anchors = [
            _make_anchor(source_doc_id="doc-Z"),
            _make_anchor(source_doc_id="doc-A"),
        ]
        b = _make_bundle(anchors=anchors)
        doc_ids = [a.source_doc_id for a in b.anchors]
        assert doc_ids == sorted(doc_ids)

    def test_anchors_sorted_by_chunk_id_within_doc(self):
        anchors = [
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-Z"),
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-A"),
        ]
        b = _make_bundle(anchors=anchors)
        chunk_ids = [a.chunk_id for a in b.anchors]
        assert chunk_ids == sorted(chunk_ids)

    def test_anchors_sorted_by_char_start_within_chunk(self):
        anchors = [
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-1", char_start=50, char_end=60),
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-1", char_start=10, char_end=20),
        ]
        b = _make_bundle(anchors=anchors)
        starts = [a.char_start for a in b.anchors]
        assert starts == sorted(starts)

    def test_to_dict_contains_all_fields(self):
        b = _make_bundle()
        d = b.to_dict()
        assert "schema_version" in d
        assert "request_hash" in d
        assert "anchors" in d
        assert "citation_hash" in d

    def test_factory_produces_valid_bundle(self):
        b = build_citation_bundle(request_hash=_RH, anchors=[_make_anchor()])
        assert isinstance(b, CitationBundle)
        assert len(b.citation_hash) == 64
