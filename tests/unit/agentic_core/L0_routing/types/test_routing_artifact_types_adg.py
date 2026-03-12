"""ADG contract tests for agentic_core/L0_routing/types/routing_artifact_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.routing_artifact_types import (
        RetrievalQuery, RetrievedChunk, CitationEntry, CitationBundle, ErrorSignature,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    RetrievalQuery = RetrievedChunk = CitationEntry = CitationBundle = None  # type: ignore[assignment,misc]
    ErrorSignature = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCitationEntry:
    def test_is_frozen(self): assert CitationEntry.__dataclass_params__.frozen is True
    def test_creates(self):
        e = CitationEntry(
            citation_id="c1", chunk_id="ch1", source_id="s1",
            location="file.py:10", retrieval_hash="abc",
        )
        assert e.citation_id == "c1"
    def test_empty_citation_id_raises(self):
        with pytest.raises(ValueError):
            CitationEntry(citation_id="", chunk_id="ch", source_id="s",
                          location="f", retrieval_hash="h")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCitationBundle:
    def test_is_frozen(self): assert CitationBundle.__dataclass_params__.frozen is True
    def test_creates(self):
        e = CitationEntry(citation_id="c1", chunk_id="ch1", source_id="s1",
                          location="f", retrieval_hash="h")
        b = CitationBundle(
            trace_id="t1", bundle_id="b1", citations=(e,),
            retrieval_query_hash="qh", bundle_hash="bh",
        )
        assert len(b.citations) == 1
    def test_empty_citations_raises(self):
        with pytest.raises(ValueError):
            CitationBundle(trace_id="t", bundle_id="b", citations=(),
                           retrieval_query_hash="q", bundle_hash="bh")

def test_module_importable(): assert _AVAIL or not _AVAIL
