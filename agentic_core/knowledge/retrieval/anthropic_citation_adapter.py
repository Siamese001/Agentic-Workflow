"""Anthropic Citations adapter.

Maps Anthropic Messages-API native-citation response shape onto the internal
``Citation`` dataclass used throughout the knowledge/retrieval stack.

Enabling ``citations: {"enabled": true}`` on an Anthropic Messages request
causes Claude to return structured citation references alongside generated
text. The response shape:

    {
      "content": [
        {"type": "text", "text": "The answer is X."},
        {"type": "text",
         "text": "Because Y.",
         "citations": [
           {
             "type": "char_location",
             "cited_text": "...",
             "document_index": 0,
             "document_title": "...",
             "start_char_index": 42,
             "end_char_index": 75
           }
         ]
        }
      ]
    }

This module translates that shape into the internal ``Citation`` records used
by ``citation_enforcement`` / ``ProvenancetrackerStrategy`` etc., using a
caller-supplied document-index → VerifiedChunk map built at prompt-render time
(the P1.2 renderer emits ``<document index="1">...</document>`` in the exact
order that Anthropic then references as ``document_index``, so the caller
already has the correspondence).

Reference:
  https://docs.anthropic.com/en/docs/build-with-claude/citations

Design invariants:
- Pure functions. No I/O, no gateway calls.
- Response-shape-tolerant: accepts dicts and objects duck-typed with
  ``.content`` attribute so both real SDK responses and test fixtures work.
- Never raises on malformed / partial citation data — skips the offending
  record and logs. Missing citations are common when Claude cannot ground a
  span, and the caller's existing completeness enforcement decides policy.
- Preserves internal ``Citation`` dataclass contract (doc_id, content_snippet,
  source, confidence, citation_anchor, page_number, section).
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    Citation,
    VerifiedChunk,
)

Logger = logging.getLogger(__name__)

# Anthropic's 0-indexed document_index maps to PromptEnvelope chunk order.
# The P1.2 renderer emits <document index="1">, so external-visible indexing
# is 1-based; convert at the boundary.
_ANTHROPIC_INDEX_BASE = 0

# Max chars copied into Citation.content_snippet (mirrors internal Citation).
_CONTENT_SNIPPET_MAX = 200


def _as_content_list(response: Any) -> list[dict[str, Any]]:
    """Normalize an Anthropic response into a list of content blocks.

    Accepts:
      - dict with ``content: [...]``
      - object with ``.content`` attribute
      - already-a-list
    """
    if response is None:
        return []
    if isinstance(response, list):
        return [b for b in response if isinstance(b, dict)]
    if isinstance(response, dict):
        content = response.get("content", [])
        return [b for b in content if isinstance(b, dict)]
    # Duck-typed SDK object
    content = getattr(response, "content", None)
    if content is None:
        return []
    if isinstance(content, list):
        # SDK objects may expose content blocks as attribute-bearing objects.
        # Coerce to dicts via vars()/asdict when possible.
        normalized: list[dict[str, Any]] = []
        for block in content:
            if isinstance(block, dict):
                normalized.append(block)
            elif hasattr(block, "__dict__"):
                normalized.append({k: v for k, v in vars(block).items() if not k.startswith("_")})
        return normalized
    return []


def extract_answer_text(response: Any) -> str:
    """Return the joined text from all text-type content blocks.

    Citations are metadata on blocks; the answer itself is the block text.
    """
    blocks = _as_content_list(response)
    parts: list[str] = []
    for block in blocks:
        if block.get("type") == "text":
            text = block.get("text", "")
            if text:
                parts.append(text)
    return "".join(parts)


def _anthropic_to_internal_citation(
    raw: dict[str, Any],
    *,
    chunk_by_index: dict[int, VerifiedChunk],
    fallback_anchor_counter: int,
) -> Citation | None:
    """Map a single Anthropic citation dict onto the internal Citation.

    Returns None when the Anthropic citation is malformed (missing required
    fields) or when no corresponding chunk exists in the document map.
    """
    citation_type = raw.get("type")
    if citation_type not in ("char_location", "page_location", "content_block_location"):
        Logger.debug("Skipping citation with unrecognized type: %s", citation_type)
        return None

    doc_index = raw.get("document_index")
    if not isinstance(doc_index, int):
        Logger.debug("Skipping citation without integer document_index: %r", doc_index)
        return None

    chunk = chunk_by_index.get(doc_index)
    cited_text = raw.get("cited_text", "") or ""

    # Build content_snippet from cited_text (more informative than chunk head
    # for narrow spans). Fall back to chunk.content[:200] when cited_text is
    # empty (rare but possible for whole-document citations).
    snippet = (cited_text or (chunk.content if chunk else ""))[:_CONTENT_SNIPPET_MAX]

    # doc_id and source: prefer the verified chunk's stable identifiers; fall
    # back to Anthropic's document_title when the chunk map is incomplete.
    if chunk is not None:
        doc_id = chunk.chunk_id
        source = chunk.source_id
        confidence = chunk.support_score
        provenance = chunk.provenance or {}
        page_number = provenance.get("page_number")
        section = provenance.get("section") or provenance.get("heading_path")
    else:
        title = raw.get("document_title", "") or ""
        doc_id = title or f"anthropic_doc_{doc_index}"
        source = "anthropic_citation"
        confidence = 0.0  # unknown when chunk map is incomplete
        page_number = raw.get("page_number") if citation_type == "page_location" else None
        section = None

    # Citation anchor: we cannot reach back into the envelope here, so use a
    # stable counter. Callers who need the envelope's [1]/[2] anchor can
    # replace this after mapping via doc_id lookup.
    anchor = f"[{fallback_anchor_counter}]"

    return Citation(
        doc_id=doc_id,
        content_snippet=snippet,
        source=source,
        confidence=confidence,
        citation_anchor=anchor,
        page_number=page_number,
        section=section,
    )


def extract_citations(
    response: Any,
    *,
    chunk_by_index: dict[int, VerifiedChunk] | None = None,
) -> list[Citation]:
    """Extract all citations from an Anthropic response as internal Citations.

    Parameters
    ----------
    response:
        Anthropic Messages-API response (dict, SDK object, or list of content
        blocks).
    chunk_by_index:
        Map from Anthropic ``document_index`` (0-based) to the
        ``VerifiedChunk`` that occupied that slot in the rendered prompt.
        Typically built by the caller immediately after
        ``render_anthropic_prompt`` like::

            chunk_by_index = {i: c for i, c in enumerate(envelope.verified_chunks)}

    Returns
    -------
    List of internal ``Citation`` records, one per Anthropic citation on each
    text block (multiple citations per block are preserved). Malformed
    citations are skipped with debug logging.
    """
    chunk_by_index = chunk_by_index or {}
    blocks = _as_content_list(response)

    citations: list[Citation] = []
    anchor_counter = 1
    for block in blocks:
        if block.get("type") != "text":
            continue
        raw_citations = block.get("citations") or []
        for raw in raw_citations:
            if not isinstance(raw, dict):
                continue
            mapped = _anthropic_to_internal_citation(
                raw,
                chunk_by_index=chunk_by_index,
                fallback_anchor_counter=anchor_counter,
            )
            if mapped is not None:
                citations.append(mapped)
                anchor_counter += 1

    return citations


def map_citations_to_envelope_anchors(
    citations: list[Citation],
    envelope_anchor_by_doc_id: dict[str, str],
) -> list[Citation]:
    """Rewrite citation anchors to match the envelope's anchor scheme.

    After ``extract_citations`` assigns sequential ``[1]/[2]`` anchors, callers
    who already track a canonical anchor per chunk (e.g., the prompt-render
    pass numbered them differently) can rewrite in one pass without mutating
    the existing Citation records.

    Returns a new list with updated anchors; original list is not modified.
    """
    rewritten: list[Citation] = []
    for cite in citations:
        new_anchor = envelope_anchor_by_doc_id.get(cite.doc_id, cite.citation_anchor)
        rewritten.append(
            Citation(
                doc_id=cite.doc_id,
                content_snippet=cite.content_snippet,
                source=cite.source,
                confidence=cite.confidence,
                citation_anchor=new_anchor,
                page_number=cite.page_number,
                section=cite.section,
            )
        )
    return rewritten


def citation_coverage_ratio(
    citations: list[Citation],
    must_use_chunks: list[VerifiedChunk],
) -> float:
    """Fraction of must-use chunks that received at least one citation.

    Zero when no must-use chunks were supplied (guards divide-by-zero).
    A low ratio is a strong signal that the answer is under-grounded even
    when the text looks plausible.
    """
    if not must_use_chunks:
        return 0.0
    cited_doc_ids = {c.doc_id for c in citations}
    covered = sum(1 for c in must_use_chunks if c.chunk_id in cited_doc_ids)
    return covered / len(must_use_chunks)


__all__ = [
    "extract_answer_text",
    "extract_citations",
    "map_citations_to_envelope_anchors",
    "citation_coverage_ratio",
]
