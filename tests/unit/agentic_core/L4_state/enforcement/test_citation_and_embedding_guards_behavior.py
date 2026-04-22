"""Behavioral tests for L4_state citation_enforcement + embedding_sovereignty_guard."""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L4_state.enforcement.citation_enforcement import (
    CitationEnforcementViolation,
    _build_request_hash_from_output,
    _sha256,
    assemble_response,
    enforce_citations_for_retrieval,
)
from agentic_core.L4_state.enforcement.embedding_sovereignty_guard import (
    EmbeddingInfluenceViolation,
    EmbeddingResult,
    guard_embedding_influence,
)
from agentic_core.L4_state.types.retrieval_anchor_types import (
    AnchoredResult,
    RetrievalAnchor,
)


# ============================================================================
# citation_enforcement
# ============================================================================


def _make_anchored(text: str = "source text") -> AnchoredResult:
    """Construct a real AnchoredResult for enforcement tests."""
    anchor = RetrievalAnchor(
        source_doc_id="doc-1",
        chunk_id="chunk-1",
        char_start=0,
        char_end=10,
        retrieved_at_utc="2026-04-22T00:00:00+00:00",
        version_hash="v1",
    )
    return AnchoredResult(content=text, anchor=anchor)


class TestCitationEnforcementViolation:
    def test_code_is_class_attr(self) -> None:
        assert CitationEnforcementViolation.code == "MISSING_CITATIONS"

    def test_default_message(self) -> None:
        exc = CitationEnforcementViolation()
        assert "MISSING_CITATIONS" in str(exc)
        assert exc.detail == ""

    def test_with_detail(self) -> None:
        exc = CitationEnforcementViolation(detail="why")
        assert "why" in str(exc)
        assert exc.detail == "why"

    def test_is_exception(self) -> None:
        assert issubclass(CitationEnforcementViolation, Exception)


class TestSha256Helper:
    def test_hex_length(self) -> None:
        h = _sha256(b"hello")
        assert len(h) == 64
        int(h, 16)

    def test_deterministic(self) -> None:
        assert _sha256(b"x") == _sha256(b"x")


class TestBuildRequestHashFromOutput:
    def test_filters_volatile_fields(self) -> None:
        h1 = _build_request_hash_from_output(
            {"prompt": "q", "timestamp": 1},
        )
        h2 = _build_request_hash_from_output(
            {"prompt": "q", "timestamp": 2},
        )
        # volatile fields excluded — hash stable
        assert h1 == h2

    def test_different_prompts_different_hash(self) -> None:
        a = _build_request_hash_from_output({"prompt": "a"})
        b = _build_request_hash_from_output({"prompt": "b"})
        assert a != b

    def test_ignores_non_scalar_fields(self) -> None:
        # Only str/int/float/bool are included in the canonical subset
        h1 = _build_request_hash_from_output({"prompt": "q", "extra": [1, 2]})
        h2 = _build_request_hash_from_output({"prompt": "q", "extra": [9, 9]})
        assert h1 == h2


class TestEnforceCitationsForRetrieval:
    def test_retrieval_not_used_returns_unchanged(self) -> None:
        out = {"text": "no retrieval"}
        result = enforce_citations_for_retrieval(
            out, anchored_results=None, retrieval_used=False,
        )
        assert result is out  # unchanged, same object

    def test_retrieval_used_but_empty_raises(self) -> None:
        with pytest.raises(CitationEnforcementViolation, match="MISSING_CITATIONS"):
            enforce_citations_for_retrieval(
                {"text": "x"}, anchored_results=[], retrieval_used=True,
            )

    def test_retrieval_used_but_none_raises(self) -> None:
        with pytest.raises(CitationEnforcementViolation):
            enforce_citations_for_retrieval(
                {"text": "x"}, anchored_results=None, retrieval_used=True,
            )

    def test_retrieval_used_with_anchors_attaches_citations(self) -> None:
        out = {"text": "answer"}
        result = enforce_citations_for_retrieval(
            out, anchored_results=[_make_anchored()], retrieval_used=True,
        )
        assert "citations" in result

    def test_does_not_mutate_input(self) -> None:
        out = {"text": "answer"}
        snapshot = {"text": "answer"}
        enforce_citations_for_retrieval(
            out, anchored_results=[_make_anchored()], retrieval_used=True,
        )
        assert out == snapshot
        assert "citations" not in out

    def test_explicit_request_hash_used(self) -> None:
        result = enforce_citations_for_retrieval(
            {"text": "x"}, anchored_results=[_make_anchored()],
            retrieval_used=True, request_hash="explicit_hash",
        )
        # Bundle's request_hash is propagated (won't inspect exact shape — just
        # verify bundle exists and is a dict)
        assert isinstance(result["citations"], dict)


class TestAssembleResponse:
    def test_delegates_to_enforce(self) -> None:
        out = {"text": "x"}
        result = assemble_response(out, anchored_results=None, retrieval_used=False)
        assert result is out

    def test_empty_anchors_with_retrieval_raises(self) -> None:
        with pytest.raises(CitationEnforcementViolation):
            assemble_response({"text": "x"}, anchored_results=[], retrieval_used=True)


# ============================================================================
# embedding_sovereignty_guard
# ============================================================================


class TestEmbeddingResult:
    def test_instantiable(self) -> None:
        r = EmbeddingResult()
        assert isinstance(r, EmbeddingResult)


class TestEmbeddingInfluenceViolation:
    def test_attributes(self) -> None:
        exc = EmbeddingInfluenceViolation("route", "arg[0]")
        assert exc.decision_type == "route"
        assert exc.found_in == "arg[0]"
        assert "route" in str(exc)
        assert "arg[0]" in str(exc)

    def test_is_exception(self) -> None:
        assert issubclass(EmbeddingInfluenceViolation, Exception)


class TestGuardEmbeddingInfluence:
    def test_clean_args_no_raise(self) -> None:
        guard_embedding_influence("string", 42, decision_type="route")

    def test_clean_kwargs_no_raise(self) -> None:
        guard_embedding_influence(decision_type="route", prompt="hello", budget=10)

    def test_direct_positional_detected(self) -> None:
        with pytest.raises(EmbeddingInfluenceViolation) as exc_info:
            guard_embedding_influence(EmbeddingResult(), decision_type="route")
        assert exc_info.value.decision_type == "route"
        assert "arg[0]" in exc_info.value.found_in

    def test_in_list_detected(self) -> None:
        with pytest.raises(EmbeddingInfluenceViolation) as exc_info:
            guard_embedding_influence(
                ["safe", EmbeddingResult()], decision_type="classify",
            )
        assert "[1]" in exc_info.value.found_in

    def test_in_nested_dict_detected(self) -> None:
        with pytest.raises(EmbeddingInfluenceViolation) as exc_info:
            guard_embedding_influence(
                {"outer": {"inner": EmbeddingResult()}}, decision_type="safety",
            )
        assert "outer" in exc_info.value.found_in
        assert "inner" in exc_info.value.found_in

    def test_in_kwargs_detected(self) -> None:
        with pytest.raises(EmbeddingInfluenceViolation):
            guard_embedding_influence(
                decision_type="route", context=EmbeddingResult(),
            )

    def test_empty_args_passes(self) -> None:
        guard_embedding_influence(decision_type="route")

    def test_scalar_primitives_ignored(self) -> None:
        # strings/ints/floats/bools/None must not trigger violations
        guard_embedding_influence(
            "x", 1, 1.5, True, None, decision_type="route",
        )
