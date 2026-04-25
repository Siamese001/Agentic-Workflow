"""Unit tests for anthropic_citation_adapter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from agentic_core.knowledge.retrieval.anthropic_citation_adapter import (
    citation_coverage_ratio,
    extract_answer_text,
    extract_citations,
    map_citations_to_envelope_anchors,
)
from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    Citation,
    VerifiedChunk,
)


def _chunk(
    chunk_id: str = "c1",
    content: str = "chunk body",
    source_id: str = "docs/a.md",
    support: float = 0.85,
    provenance: dict[str, Any] | None = None,
    is_must_use: bool = True,
) -> VerifiedChunk:
    return VerifiedChunk(
        chunk_id=chunk_id,
        content=content,
        source_id=source_id,
        citation_anchor=f"[{chunk_id}]",
        support_score=support,
        is_must_use=is_must_use,
        provenance=provenance or {},
    )


def _response(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"content": blocks}


# ---------------------------------------------------------------------------
# extract_answer_text
# ---------------------------------------------------------------------------


def test_extract_answer_text_joins_all_text_blocks():
    resp = _response(
        [
            {"type": "text", "text": "First part. "},
            {"type": "text", "text": "Second part."},
        ]
    )
    assert extract_answer_text(resp) == "First part. Second part."


def test_extract_answer_text_ignores_non_text_blocks():
    resp = _response(
        [
            {"type": "text", "text": "Answer."},
            {"type": "tool_use", "id": "t1", "name": "foo"},
        ]
    )
    assert extract_answer_text(resp) == "Answer."


def test_extract_answer_text_handles_empty_response():
    assert extract_answer_text(None) == ""
    assert extract_answer_text({}) == ""
    assert extract_answer_text({"content": []}) == ""


def test_extract_answer_text_accepts_bare_list():
    blocks = [{"type": "text", "text": "hi"}]
    assert extract_answer_text(blocks) == "hi"


def test_extract_answer_text_accepts_sdk_like_object():
    @dataclass
    class _FakeBlock:
        type: str
        text: str

    @dataclass
    class _FakeResponse:
        content: list = field(default_factory=list)

    resp = _FakeResponse(content=[_FakeBlock(type="text", text="sdk-shaped")])
    assert extract_answer_text(resp) == "sdk-shaped"


# ---------------------------------------------------------------------------
# extract_citations
# ---------------------------------------------------------------------------


def test_extract_citations_maps_to_internal_shape():
    chunk0 = _chunk(chunk_id="chunk-a", source_id="docs/a.md", support=0.9)
    resp = _response(
        [
            {
                "type": "text",
                "text": "Answer references a.",
                "citations": [
                    {
                        "type": "char_location",
                        "cited_text": "precise span from doc",
                        "document_index": 0,
                        "document_title": "Doc A",
                        "start_char_index": 0,
                        "end_char_index": 21,
                    }
                ],
            }
        ]
    )
    cites = extract_citations(resp, chunk_by_index={0: chunk0})
    assert len(cites) == 1
    c = cites[0]
    assert c.doc_id == "chunk-a"
    assert c.source == "docs/a.md"
    assert c.confidence == 0.9
    assert c.content_snippet == "precise span from doc"
    assert c.citation_anchor == "[1]"


def test_extract_citations_increments_anchor_counter_across_blocks():
    chunk0 = _chunk(chunk_id="c0")
    chunk1 = _chunk(chunk_id="c1")
    resp = _response(
        [
            {
                "type": "text",
                "text": "First.",
                "citations": [{"type": "char_location", "cited_text": "a", "document_index": 0}],
            },
            {
                "type": "text",
                "text": "Second.",
                "citations": [{"type": "char_location", "cited_text": "b", "document_index": 1}],
            },
        ]
    )
    cites = extract_citations(resp, chunk_by_index={0: chunk0, 1: chunk1})
    assert [c.citation_anchor for c in cites] == ["[1]", "[2]"]
    assert [c.doc_id for c in cites] == ["c0", "c1"]


def test_extract_citations_preserves_multiple_citations_per_block():
    chunk0 = _chunk(chunk_id="c0")
    chunk1 = _chunk(chunk_id="c1")
    resp = _response(
        [
            {
                "type": "text",
                "text": "Cites two sources.",
                "citations": [
                    {"type": "char_location", "cited_text": "a", "document_index": 0},
                    {"type": "char_location", "cited_text": "b", "document_index": 1},
                ],
            }
        ]
    )
    cites = extract_citations(resp, chunk_by_index={0: chunk0, 1: chunk1})
    assert len(cites) == 2


def test_extract_citations_skips_malformed_without_raising():
    chunk0 = _chunk(chunk_id="c0")
    resp = _response(
        [
            {
                "type": "text",
                "text": "Mixed cites.",
                "citations": [
                    {"type": "char_location", "cited_text": "ok", "document_index": 0},
                    "not a dict",  # malformed
                    {"type": "unknown_type", "cited_text": "x", "document_index": 0},
                    {"type": "char_location", "cited_text": "y"},  # missing document_index
                ],
            }
        ]
    )
    cites = extract_citations(resp, chunk_by_index={0: chunk0})
    assert len(cites) == 1
    assert cites[0].content_snippet == "ok"


def test_extract_citations_uses_fallback_when_chunk_map_missing_index():
    resp = _response(
        [
            {
                "type": "text",
                "text": "Answer.",
                "citations": [
                    {
                        "type": "char_location",
                        "cited_text": "fallback span",
                        "document_index": 99,
                        "document_title": "Unknown Doc",
                    }
                ],
            }
        ]
    )
    cites = extract_citations(resp, chunk_by_index={})
    assert len(cites) == 1
    c = cites[0]
    assert c.doc_id == "Unknown Doc"
    assert c.source == "anthropic_citation"
    assert c.confidence == 0.0


def test_extract_citations_page_location_captures_page_number():
    chunk0 = _chunk(chunk_id="c0", provenance={"page_number": 5, "section": "Intro"})
    resp = _response(
        [
            {
                "type": "text",
                "text": "PDF answer.",
                "citations": [
                    {
                        "type": "page_location",
                        "cited_text": "found on page",
                        "document_index": 0,
                        "start_page_number": 5,
                        "end_page_number": 5,
                    }
                ],
            }
        ]
    )
    cites = extract_citations(resp, chunk_by_index={0: chunk0})
    assert cites[0].page_number == 5
    assert cites[0].section == "Intro"


def test_extract_citations_heading_path_used_when_section_absent():
    chunk0 = _chunk(
        chunk_id="c0",
        provenance={"heading_path": "Retrieval > BM25"},
    )
    resp = _response(
        [
            {
                "type": "text",
                "text": ".",
                "citations": [{"type": "char_location", "cited_text": "x", "document_index": 0}],
            }
        ]
    )
    cites = extract_citations(resp, chunk_by_index={0: chunk0})
    assert cites[0].section == "Retrieval > BM25"


def test_extract_citations_blocks_without_citations_produce_none():
    resp = _response([{"type": "text", "text": "Plain answer, no grounding."}])
    assert extract_citations(resp) == []


def test_extract_citations_empty_cited_text_falls_back_to_chunk_content():
    chunk0 = _chunk(chunk_id="c0", content="Full chunk content spans many words.")
    resp = _response(
        [
            {
                "type": "text",
                "text": ".",
                "citations": [{"type": "char_location", "cited_text": "", "document_index": 0}],
            }
        ]
    )
    cites = extract_citations(resp, chunk_by_index={0: chunk0})
    assert cites[0].content_snippet == "Full chunk content spans many words."


# ---------------------------------------------------------------------------
# map_citations_to_envelope_anchors
# ---------------------------------------------------------------------------


def test_remap_anchors_rewrites_known_doc_ids():
    cites = [
        Citation(doc_id="c0", content_snippet="x", source="s", confidence=0.9, citation_anchor="[1]"),
        Citation(doc_id="c1", content_snippet="y", source="s", confidence=0.8, citation_anchor="[2]"),
    ]
    anchor_map = {"c0": "[alpha]", "c1": "[beta]"}
    rewritten = map_citations_to_envelope_anchors(cites, anchor_map)
    assert [c.citation_anchor for c in rewritten] == ["[alpha]", "[beta]"]
    # Original list must not mutate
    assert cites[0].citation_anchor == "[1]"


def test_remap_anchors_preserves_unknown_doc_ids():
    cites = [
        Citation(doc_id="unknown", content_snippet="x", source="s", confidence=0.5, citation_anchor="[9]"),
    ]
    rewritten = map_citations_to_envelope_anchors(cites, {"c0": "[alpha]"})
    assert rewritten[0].citation_anchor == "[9]"


# ---------------------------------------------------------------------------
# citation_coverage_ratio
# ---------------------------------------------------------------------------


def test_coverage_ratio_all_must_use_covered():
    must = [_chunk(chunk_id="c0"), _chunk(chunk_id="c1")]
    cites = [
        Citation(doc_id="c0", content_snippet="", source="", confidence=0.0),
        Citation(doc_id="c1", content_snippet="", source="", confidence=0.0),
    ]
    assert citation_coverage_ratio(cites, must) == 1.0


def test_coverage_ratio_partial():
    must = [_chunk(chunk_id="c0"), _chunk(chunk_id="c1"), _chunk(chunk_id="c2")]
    cites = [
        Citation(doc_id="c0", content_snippet="", source="", confidence=0.0),
    ]
    assert citation_coverage_ratio(cites, must) == pytest.approx(1 / 3)


def test_coverage_ratio_zero_when_no_must_use():
    cites = [Citation(doc_id="c0", content_snippet="", source="", confidence=0.0)]
    assert citation_coverage_ratio(cites, []) == 0.0


def test_coverage_ratio_zero_when_no_overlap():
    must = [_chunk(chunk_id="c0")]
    cites = [Citation(doc_id="other", content_snippet="", source="", confidence=0.0)]
    assert citation_coverage_ratio(cites, must) == 0.0


# ---------------------------------------------------------------------------
# End-to-end composition
# ---------------------------------------------------------------------------


def test_end_to_end_answer_plus_citations_from_single_response():
    chunk0 = _chunk(chunk_id="c0", source_id="src0", support=0.9)
    chunk1 = _chunk(chunk_id="c1", source_id="src1", support=0.8)
    resp = _response(
        [
            {"type": "text", "text": "Preamble. "},
            {
                "type": "text",
                "text": "Grounded claim.",
                "citations": [
                    {"type": "char_location", "cited_text": "fact a", "document_index": 0},
                    {"type": "char_location", "cited_text": "fact b", "document_index": 1},
                ],
            },
        ]
    )
    text = extract_answer_text(resp)
    cites = extract_citations(resp, chunk_by_index={0: chunk0, 1: chunk1})

    assert text == "Preamble. Grounded claim."
    assert len(cites) == 2
    assert cites[0].doc_id == "c0"
    assert cites[1].doc_id == "c1"
    assert citation_coverage_ratio(cites, [chunk0, chunk1]) == 1.0
