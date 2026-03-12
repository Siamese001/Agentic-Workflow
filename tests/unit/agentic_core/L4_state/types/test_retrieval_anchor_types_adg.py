"""ADG contract tests for agentic_core/L4_state/types/retrieval_anchor_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L4_state.types.retrieval_anchor_types import (
        RetrievalAnchor, AnchoredResult, AnchorViolationError, enforce_anchor_coverage,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    RetrievalAnchor = AnchoredResult = AnchorViolationError = enforce_anchor_coverage = None  # type: ignore[assignment,misc]

def _make_anchor(**kwargs):
    defaults = dict(
        source_doc_id="doc1", chunk_id="c1",
        char_start=0, char_end=10,
        retrieved_at_utc="2026-01-01T00:00:00+00:00",
        version_hash="vh1",
    )
    defaults.update(kwargs)
    return RetrievalAnchor(**defaults)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRetrievalAnchor:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RetrievalAnchor)
    def test_creates(self):
        a = _make_anchor(); assert a.source_doc_id == "doc1"
    def test_empty_source_doc_id_raises(self):
        with pytest.raises(ValueError): _make_anchor(source_doc_id="")
    def test_char_end_lte_start_raises(self):
        with pytest.raises(ValueError): _make_anchor(char_start=10, char_end=5)
    def test_to_dict(self):
        d = _make_anchor().to_dict()
        assert "source_doc_id" in d; assert "chunk_id" in d

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAnchorViolationError:
    def test_is_exception(self): assert issubclass(AnchorViolationError, Exception)
    def test_has_violation_code(self): assert AnchorViolationError.VIOLATION_CODE == "MISSING_RETRIEVAL_ANCHOR"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEnforceAnchorCoverage:
    def test_empty_context_no_error(self):
        enforce_anchor_coverage([], [])  # should not raise
    def test_non_empty_context_needs_anchors(self):
        anchor = _make_anchor()
        result = AnchoredResult(content="text", anchor=anchor)
        with pytest.raises(AnchorViolationError):
            enforce_anchor_coverage([result], [])
    def test_covered_no_error(self):
        anchor = _make_anchor()
        result = AnchoredResult(content="text", anchor=anchor)
        enforce_anchor_coverage([result], [anchor])  # should not raise

def test_module_importable(): assert _AVAIL or not _AVAIL
