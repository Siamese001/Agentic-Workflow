"""Unit tests for qwen_citation_adapter (Wave G / F2 of qwen-adoption-waves-a7f3c2)."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    Citation,
    VerifiedChunk,
)
from agentic_core.knowledge.retrieval.qwen_citation_adapter import (
    build_citations_from_qwen_text,
    citation_coverage_ratio,
    extract_indices,
)


def _chunk(idx: int, content: str = "body", source: str = "kb") -> VerifiedChunk:
    return VerifiedChunk(
        chunk_id=f"c-{idx}",
        content=content,
        source_id=source,
        citation_anchor=f"[{idx}]",
        support_score=0.9,
        is_must_use=True,
        provenance={"page_number": idx * 10, "section": f"s-{idx}"},
    )


# ---- extract_indices ------------------------------------------------------


def test_extract_indices_empty_text() -> None:
    assert extract_indices("") == []


def test_extract_indices_bare_integer() -> None:
    assert extract_indices("see [1] and [2] and [3]") == [1, 2, 3]


def test_extract_indices_dedupes_in_order() -> None:
    assert extract_indices("see [2] then [1] then [2] then [3] then [1]") == [2, 1, 3]


def test_extract_indices_doc_prefix() -> None:
    assert extract_indices("as shown in [doc 4] and [doc:5]") == [4, 5]


def test_extract_indices_chunk_prefix() -> None:
    assert extract_indices("[chunk 7] says this and [CHUNK:8] agrees") == [7, 8]


def test_extract_indices_source_prefix() -> None:
    assert extract_indices("[source 9]") == [9]


def test_extract_indices_comma_separated() -> None:
    assert extract_indices("cited in [1, 2, 3]") == [1, 2, 3]


def test_extract_indices_adjacent_brackets() -> None:
    assert extract_indices("strong support [1][2][3]") == [1, 2, 3]


def test_extract_indices_ignores_non_integer_tokens() -> None:
    assert extract_indices("this [note] is ignored but [1] is kept") == [1]


# ---- build_citations_from_qwen_text --------------------------------------


def test_build_citations_empty_text_returns_empty_list() -> None:
    assert build_citations_from_qwen_text("", chunk_by_index={1: _chunk(1)}) == []


def test_build_citations_maps_indices_to_chunks() -> None:
    chunks = {1: _chunk(1, content="alpha fact"), 2: _chunk(2, content="beta fact")}
    answer = "The answer is alpha [1]. Also beta [2]."
    cites = build_citations_from_qwen_text(answer, chunk_by_index=chunks)

    assert len(cites) == 2
    assert cites[0].doc_id == "c-1"
    assert cites[0].content_snippet == "alpha fact"
    assert cites[0].source == "kb"
    assert cites[0].confidence == pytest.approx(0.9)
    assert cites[0].citation_anchor == "[1]"
    assert cites[0].page_number == 10
    assert cites[0].section == "s-1"
    assert cites[1].doc_id == "c-2"


def test_build_citations_skips_unknown_indices() -> None:
    chunks = {1: _chunk(1)}
    answer = "mix [1] and [99] in one sentence"
    cites = build_citations_from_qwen_text(answer, chunk_by_index=chunks)
    assert [c.doc_id for c in cites] == ["c-1"]


def test_build_citations_dedupes_on_repeated_index() -> None:
    chunks = {1: _chunk(1)}
    answer = "[1] and also [1] and again [1]"
    cites = build_citations_from_qwen_text(answer, chunk_by_index=chunks)
    assert len(cites) == 1


def test_build_citations_snippet_truncated_to_200_chars() -> None:
    chunks = {1: _chunk(1, content="X" * 500)}
    cites = build_citations_from_qwen_text("cite [1]", chunk_by_index=chunks)
    assert len(cites[0].content_snippet) == 200
    assert cites[0].content_snippet == "X" * 200


def test_build_citations_respects_chunk_citation_anchor() -> None:
    chunk = VerifiedChunk(
        chunk_id="c-custom",
        content="content",
        source_id="kb",
        citation_anchor="[custom-anchor]",
        support_score=0.5,
    )
    cites = build_citations_from_qwen_text("see [1]", chunk_by_index={1: chunk})
    assert cites[0].citation_anchor == "[custom-anchor]"


def test_build_citations_ignores_non_positive_index() -> None:
    chunks = {1: _chunk(1)}
    # Pattern only matches [digits], so "0" in brackets is valid as integer=0.
    # That index should be skipped, not passed to chunk lookup.
    cites = build_citations_from_qwen_text("ref [0] and [1]", chunk_by_index=chunks)
    assert len(cites) == 1
    assert cites[0].doc_id == "c-1"


# ---- citation_coverage_ratio ---------------------------------------------


def test_coverage_ratio_empty_must_use_returns_one() -> None:
    assert citation_coverage_ratio([], []) == 1.0


def test_coverage_ratio_full_coverage() -> None:
    must = [_chunk(1), _chunk(2)]
    cites = [
        Citation(doc_id="c-1", content_snippet="", source="", confidence=1.0),
        Citation(doc_id="c-2", content_snippet="", source="", confidence=1.0),
    ]
    assert citation_coverage_ratio(cites, must) == 1.0


def test_coverage_ratio_partial_coverage() -> None:
    must = [_chunk(1), _chunk(2), _chunk(3), _chunk(4)]
    cites = [
        Citation(doc_id="c-1", content_snippet="", source="", confidence=1.0),
        Citation(doc_id="c-3", content_snippet="", source="", confidence=1.0),
    ]
    assert citation_coverage_ratio(cites, must) == pytest.approx(0.5)


def test_coverage_ratio_zero_coverage() -> None:
    must = [_chunk(1)]
    cites = [Citation(doc_id="c-unrelated", content_snippet="", source="", confidence=1.0)]
    assert citation_coverage_ratio(cites, must) == 0.0
