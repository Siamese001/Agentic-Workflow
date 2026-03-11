"""
Phase 8 — Wave 2 Tests: enforce_citations_for_retrieval() + response assembly seam.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.enforcement.citation_enforcement import (
    CitationEnforcementViolation,
    assemble_response,
    enforce_citations_for_retrieval,
)
from agentic_core.L4_state.types.retrieval_anchor_types import AnchoredResult, RetrievalAnchor

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"
_RH = "a" * 64


def _make_anchor(chunk_id: str = "chunk-1", source_doc_id: str = "doc-A") -> RetrievalAnchor:
    return RetrievalAnchor(
        source_doc_id=source_doc_id,
        chunk_id=chunk_id,
        char_start=0,
        char_end=10,
        retrieved_at_utc=_TS,
        version_hash=f"vh-{chunk_id}",
    )


def _make_anchored_result(chunk_id: str = "chunk-1") -> AnchoredResult:
    return AnchoredResult(content=f"content of {chunk_id}", anchor=_make_anchor(chunk_id))


_BASE_OUTPUT: dict = {"answer": "The capital is Paris.", "model": "gpt-4"}


class TestMissingCitationsRejected:
    def test_missing_citations_rejected(self):
        """
        Core Wave 2 guarantee: retrieval_used=True with empty anchored_results
        raises CitationEnforcementViolation.
        """
        with pytest.raises(CitationEnforcementViolation) as exc_info:
            enforce_citations_for_retrieval(
                output=dict(_BASE_OUTPUT),
                anchored_results=[],
                retrieval_used=True,
            )
        assert exc_info.value.code == "MISSING_CITATIONS"

    def test_none_anchored_results_rejected(self):
        with pytest.raises(CitationEnforcementViolation) as exc_info:
            enforce_citations_for_retrieval(
                output=dict(_BASE_OUTPUT),
                anchored_results=None,
                retrieval_used=True,
            )
        assert "MISSING_CITATIONS" in str(exc_info.value)

    def test_violation_detail_non_empty(self):
        try:
            enforce_citations_for_retrieval(
                output=dict(_BASE_OUTPUT),
                anchored_results=[],
                retrieval_used=True,
            )
            pytest.fail("Expected CitationEnforcementViolation")
        except CitationEnforcementViolation as exc:  # guardian: allow-silent-swallower
            assert exc.detail != ""

    def test_violation_code_constant(self):
        assert CitationEnforcementViolation.code == "MISSING_CITATIONS"

    def test_violation_is_exception(self):
        exc = CitationEnforcementViolation("test")
        assert isinstance(exc, Exception)

    def test_violation_detail_stored(self):
        exc = CitationEnforcementViolation("my detail")
        assert exc.detail == "my detail"


class TestAnchoredOutputIncludesCitationBundle:
    def test_anchored_output_includes_citation_bundle(self):
        """
        Core Wave 2 guarantee: retrieval_used=True with non-empty anchored_results
        returns output with "citations" key containing CitationBundle.
        """
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
        )
        assert "citations" in result
        citations = result["citations"]
        assert "citation_hash" in citations
        assert "anchors" in citations
        assert len(citations["anchors"]) == 1

    def test_citations_block_contains_schema_version(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert result["citations"]["schema_version"] == 1

    def test_citations_hash_is_64_chars(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert len(result["citations"]["citation_hash"]) == 64

    def test_citations_hash_stable_for_same_inputs(self):
        r1 = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
            request_hash=_RH,
        )
        r2 = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
            request_hash=_RH,
        )
        assert r1["citations"]["citation_hash"] == r2["citations"]["citation_hash"]

    def test_multiple_anchors_all_included(self):
        results = [
            _make_anchored_result("chunk-A"),
            _make_anchored_result("chunk-B"),
            _make_anchored_result("chunk-C"),
        ]
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=results,
            retrieval_used=True,
        )
        assert len(result["citations"]["anchors"]) == 3

    def test_original_output_fields_preserved(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert result["answer"] == _BASE_OUTPUT["answer"]
        assert result["model"] == _BASE_OUTPUT["model"]

    def test_output_dict_not_mutated_in_place(self):
        """enforce_citations_for_retrieval must return a new dict, not mutate input."""
        original = dict(_BASE_OUTPUT)
        enforce_citations_for_retrieval(
            output=original,
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert "citations" not in original

    def test_explicit_request_hash_used_in_bundle(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
            request_hash=_RH,
        )
        assert result["citations"]["request_hash"] == _RH


class TestNoRetrievalPreservesLegacyOutput:
    def test_no_retrieval_preserves_legacy_output(self):
        """
        Core Wave 2 guarantee: retrieval_used=False returns output unchanged.
        """
        original = dict(_BASE_OUTPUT)
        result = enforce_citations_for_retrieval(
            output=original,
            anchored_results=None,
            retrieval_used=False,
        )
        assert result == original
        assert "citations" not in result

    def test_no_retrieval_empty_anchors_no_violation(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[],
            retrieval_used=False,
        )
        assert "citations" not in result

    def test_no_retrieval_returns_same_object_reference(self):
        original = dict(_BASE_OUTPUT)
        result = enforce_citations_for_retrieval(
            output=original,
            anchored_results=None,
            retrieval_used=False,
        )
        assert result is original


class TestAssembleResponseSeam:
    def test_assemble_response_calls_enforce_citations(self):
        """assemble_response() is the canonical seam and must enforce citations."""
        with pytest.raises(CitationEnforcementViolation):
            assemble_response(
                output=dict(_BASE_OUTPUT),
                anchored_results=[],
                retrieval_used=True,
            )

    def test_assemble_response_with_anchors_succeeds(self):
        result = assemble_response(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert "citations" in result

    def test_assemble_response_no_retrieval_passthrough(self):
        original = dict(_BASE_OUTPUT)
        result = assemble_response(
            output=original,
            anchored_results=None,
            retrieval_used=False,
        )
        assert result is original
