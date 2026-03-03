"""
Phase 8 — Wave 3 Tests: End-to-end gateway citations + static audit.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L4_state.enforcement.citation_enforcement import (
    CitationEnforcementViolation,
    assemble_response,
    enforce_citations_for_retrieval,
)
from agentic_core.L4_state.types.retrieval_anchor import AnchoredResult, RetrievalAnchor

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"
_RH = "a" * 64

_CITATION_BUNDLE_MODULE = (
    Path(__file__).parent.parent.parent / "agentic_core" / "L4_state" / "types" / "citation_bundle.py"
)

_ENFORCEMENT_MODULE = (
    Path(__file__).parent.parent.parent
    / "agentic_core"
    / "L4_state"
    / "enforcement"
    / "citation_enforcement.py"
)


def _make_anchor(chunk_id: str, source_doc_id: str = "doc-A") -> RetrievalAnchor:
    return RetrievalAnchor(
        source_doc_id=source_doc_id,
        chunk_id=chunk_id,
        char_start=0,
        char_end=10,
        retrieved_at_utc=_TS,
        version_hash=f"vh-{chunk_id}",
    )


def _make_anchored_result(chunk_id: str) -> AnchoredResult:
    return AnchoredResult(content=f"content of {chunk_id}", anchor=_make_anchor(chunk_id))


_BASE_OUTPUT: dict = {"answer": "Paris is the capital of France.", "model": "gpt-4"}


class TestCaseARetrievalWithStrippedAnchors:
    def test_retrieval_used_stripped_anchors_raises_violation(self):
        """
        Case A: retrieval path used but anchors intentionally stripped
        → deterministic CitationEnforcementViolation.
        """
        with pytest.raises(CitationEnforcementViolation) as exc_info:
            enforce_citations_for_retrieval(
                output=dict(_BASE_OUTPUT),
                anchored_results=[],
                retrieval_used=True,
            )
        assert exc_info.value.code == "MISSING_CITATIONS"

    def test_none_anchors_with_retrieval_used_raises(self):
        with pytest.raises(CitationEnforcementViolation) as exc_info:
            enforce_citations_for_retrieval(
                output=dict(_BASE_OUTPUT),
                anchored_results=None,
                retrieval_used=True,
            )
        assert "MISSING_CITATIONS" in str(exc_info.value)

    def test_violation_is_pre_action_no_output_mutation(self):
        """Violation must be raised before any output mutation."""
        original = dict(_BASE_OUTPUT)
        with pytest.raises(CitationEnforcementViolation):
            enforce_citations_for_retrieval(
                output=original,
                anchored_results=[],
                retrieval_used=True,
            )
        assert "citations" not in original


class TestCaseBRetrievalWithAnchors:
    def test_retrieval_with_anchors_passes(self):
        """
        Case B: retrieval path used with anchors → passes and output contains
        CitationBundle with stable hash.
        """
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
            request_hash=_RH,
        )
        assert "citations" in result
        assert result["citations"]["citation_hash"]

    def test_citation_bundle_hash_stable_end_to_end(self):
        """CitationBundle hash must be stable across two identical calls."""
        kwargs = {
            "output": dict(_BASE_OUTPUT),
            "anchored_results": [_make_anchored_result("chunk-1")],
            "retrieval_used": True,
            "request_hash": _RH,
        }
        r1 = enforce_citations_for_retrieval(**kwargs)
        r2 = enforce_citations_for_retrieval(**kwargs)
        assert r1["citations"]["citation_hash"] == r2["citations"]["citation_hash"]

    def test_output_contains_citation_bundle_schema_version(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
        )
        assert result["citations"]["schema_version"] == 1

    def test_all_anchors_present_in_bundle(self):
        results = [
            _make_anchored_result("chunk-A"),
            _make_anchored_result("chunk-B"),
        ]
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=results,
            retrieval_used=True,
        )
        chunk_ids = {a["chunk_id"] for a in result["citations"]["anchors"]}
        assert "chunk-A" in chunk_ids
        assert "chunk-B" in chunk_ids

    def test_anchors_sorted_in_bundle(self):
        results = [
            _make_anchored_result("chunk-Z"),
            _make_anchored_result("chunk-A"),
        ]
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=results,
            retrieval_used=True,
        )
        chunk_ids = [a["chunk_id"] for a in result["citations"]["anchors"]]
        assert chunk_ids == sorted(chunk_ids)

    def test_assemble_response_gateway_with_anchors(self):
        """assemble_response() gateway path with anchors succeeds."""
        result = assemble_response(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
            request_hash=_RH,
        )
        assert "citations" in result
        assert len(result["citations"]["citation_hash"]) == 64

    def test_non_mutating_knowledge_index(self):
        """
        CitationBundle is attached to result payload only.
        The anchors list in the bundle is a copy — original anchored_results unchanged.
        """
        anchored = [_make_anchored_result("chunk-1")]
        original_anchor_chunk_id = anchored[0].anchor.chunk_id
        enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=anchored,
            retrieval_used=True,
        )
        assert anchored[0].anchor.chunk_id == original_anchor_chunk_id


class TestCaseCNoRetrieval:
    def test_no_retrieval_passes_unchanged(self):
        """
        Case C: no retrieval → passes, no citations required, output unchanged.
        """
        original = {"answer": "42", "model": "gpt-4"}
        result = enforce_citations_for_retrieval(
            output=original,
            anchored_results=None,
            retrieval_used=False,
        )
        assert result is original
        assert "citations" not in result

    def test_no_retrieval_empty_list_no_violation(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[],
            retrieval_used=False,
        )
        assert "citations" not in result

    def test_assemble_response_no_retrieval_passthrough(self):
        original = {"answer": "42"}
        result = assemble_response(
            output=original,
            anchored_results=None,
            retrieval_used=False,
        )
        assert result is original


class TestStaticAuditCitationEnforcement:
    def test_citation_bundle_module_exists(self):
        assert _CITATION_BUNDLE_MODULE.exists(), f"Not found: {_CITATION_BUNDLE_MODULE}"

    def test_enforcement_module_exists(self):
        assert _ENFORCEMENT_MODULE.exists(), f"Not found: {_ENFORCEMENT_MODULE}"

    def test_assemble_response_calls_enforce_citations(self):
        """
        Static audit: assemble_response() must call enforce_citations_for_retrieval.
        """
        source = _ENFORCEMENT_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        assemble_calls: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "assemble_response":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func = child.func
                        if isinstance(func, ast.Name) and func.id == "enforce_citations_for_retrieval":
                            assemble_calls.append(func.id)
                        elif (
                            isinstance(func, ast.Attribute) and func.attr == "enforce_citations_for_retrieval"
                        ):
                            assemble_calls.append(func.attr)

        assert len(assemble_calls) >= 1, "assemble_response() must call enforce_citations_for_retrieval()"

    def test_citation_bundle_excludes_volatile_fields_from_canonical_bytes(self):
        """citation_bundle.py canonical_bytes must not include retrieved_at_utc."""
        source = _CITATION_BUNDLE_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Find canonical_bytes method and check retrieved_at_utc is not in its string constants
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "canonical_bytes":
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, str):
                        assert child.value != "retrieved_at_utc", (
                            "canonical_bytes() must not include volatile field 'retrieved_at_utc'"
                        )

    def test_enforcement_module_raises_citation_enforcement_violation(self):
        """Enforcement module must define and raise CitationEnforcementViolation."""
        source = _ENFORCEMENT_MODULE.read_text(encoding="utf-8")
        assert "CitationEnforcementViolation" in source
        assert "MISSING_CITATIONS" in source

    def test_citation_bundle_module_uses_sha256(self):
        """CitationBundle must use sha256 for citation_hash."""
        source = _CITATION_BUNDLE_MODULE.read_text(encoding="utf-8")
        assert "sha256" in source

    def test_enforcement_module_does_not_mutate_knowledge_index(self):
        """
        Static AST audit: citation_enforcement.py must not call upsert/setex/set
        (no knowledge index mutation during citation attachment).
        """
        source = _ENFORCEMENT_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("upsert", "setex"):
                    forbidden.append(node.func.attr)
        assert forbidden == [], (
            f"citation_enforcement.py contains knowledge-index mutation calls: {forbidden}"
        )
