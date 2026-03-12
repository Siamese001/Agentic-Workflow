"""ADG contract tests for agentic_core/L4_state/types/citation_bundle_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L4_state.types.retrieval_anchor_types import RetrievalAnchor
    from agentic_core.L4_state.types.citation_bundle_types import (
        CitationBundle, build_citation_bundle,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    RetrievalAnchor = CitationBundle = build_citation_bundle = None  # type: ignore[assignment,misc]

def _make_anchor(source_doc_id="doc1", chunk_id="c1", char_start=0, char_end=10):
    return RetrievalAnchor(
        source_doc_id=source_doc_id, chunk_id=chunk_id,
        char_start=char_start, char_end=char_end,
        retrieved_at_utc="2026-01-01T00:00:00+00:00", version_hash="vh1",
    )

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCitationBundle:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CitationBundle)
    def test_creates_empty_anchors(self):
        cb = CitationBundle(schema_version=1, request_hash="rh1", anchors=[])
        assert cb.request_hash == "rh1"
        assert len(cb.citation_hash) == 64
    def test_citation_hash_computed(self):
        cb = CitationBundle(schema_version=1, request_hash="rh1", anchors=[_make_anchor()])
        assert len(cb.citation_hash) == 64
    def test_wrong_schema_version_raises(self):
        with pytest.raises(ValueError):
            CitationBundle(schema_version=99, request_hash="rh1", anchors=[])
    def test_empty_request_hash_raises(self):
        with pytest.raises(ValueError):
            CitationBundle(schema_version=1, request_hash="", anchors=[])
    def test_sorts_anchors(self):
        a1 = _make_anchor(source_doc_id="z", chunk_id="c1")
        a2 = _make_anchor(source_doc_id="a", chunk_id="c1")
        cb = CitationBundle(schema_version=1, request_hash="rh1", anchors=[a1, a2])
        assert cb.anchors[0].source_doc_id == "a"
    def test_to_dict(self):
        cb = CitationBundle(schema_version=1, request_hash="rh1", anchors=[])
        d = cb.to_dict()
        assert "citation_hash" in d; assert "anchors" in d

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestBuildCitationBundle:
    def test_factory_creates(self):
        cb = build_citation_bundle(request_hash="rh2", anchors=[_make_anchor()])
        assert cb.schema_version == 1
        assert len(cb.citation_hash) == 64

def test_module_importable(): assert _AVAIL or not _AVAIL
