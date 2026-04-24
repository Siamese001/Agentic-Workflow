"""Qwen plain-text citation adapter.

Anthropic's Messages API emits structured ``<document-citation>`` records
that ``anthropic_citation_adapter`` parses into internal ``Citation`` records.
Qwen (local vLLM) does NOT emit structured citations — the generated text
is plain. For retrieval flows that prompt Qwen with a numbered document
block (e.g. ``[1] ...chunk text...``) and ask it to cite sources by index,
this adapter scans the plain-text answer for bracketed references and
builds internal ``Citation`` records by mapping each reference to the
corresponding ``VerifiedChunk``.

Supported reference shapes
--------------------------
* ``[1]`` — bare integer in square brackets
* ``[doc 1]`` / ``[doc:1]``
* ``[chunk 1]`` / ``[chunk:1]``
* ``[source 1]`` / ``[source:1]``
* ``[1, 2]`` — comma-separated multi-reference
* ``[1][2]`` — adjacent references

Case-insensitive on the ``doc`` / ``chunk`` / ``source`` keyword.

Design invariants
-----------------
* Pure functions. No I/O, no gateway calls.
* Never raises on malformed input — unresolvable references are skipped
  with a debug log. Produces as many citations as can be mapped cleanly.
* Duplicate references to the same chunk are de-duplicated (one Citation
  per unique chunk, preserving first-occurrence order).
* ``content_snippet`` is the first 200 chars of the chunk content, matching
  the Anthropic adapter convention.

Plan ref: ``.windsurf/plans/qwen-adoption-waves-a7f3c2.md`` Wave G (F2).
"""

from __future__ import annotations

import logging
import re
from typing import Iterable

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    Citation,
    VerifiedChunk,
)

_log = logging.getLogger(__name__)

# Max chars copied into Citation.content_snippet (matches anthropic adapter).
_CONTENT_SNIPPET_MAX = 200

# Index patterns in priority order. Each captures one or more integer
# indices inside a single bracketed group. The body allows digits,
# whitespace, commas, and an optional keyword prefix.
_BRACKET_RE = re.compile(
    r"\[\s*(?:(?:doc|chunk|source)\s*[:\s]?\s*)?"  # optional keyword prefix
    r"(\d+(?:\s*,\s*\d+)*)"  # one or more comma-separated integers
    r"\s*\]",
    re.IGNORECASE,
)


def _iter_reference_indices(text: str) -> Iterable[int]:
    """Yield every integer reference found in ``text``, in textual order.

    Duplicates ARE yielded; caller is responsible for deduplication.
    """
    if not text:
        return
    for match in _BRACKET_RE.finditer(text):
        group = match.group(1)
        for part in group.split(","):
            part = part.strip()
            if part.isdigit():
                yield int(part)


def extract_indices(text: str) -> list[int]:
    """Return the ordered, de-duplicated list of cited indices in ``text``.

    Preserves first-occurrence order so downstream consumers can decide
    whether to emit citations in the order Qwen produced them.
    """
    seen: set[int] = set()
    out: list[int] = []
    for idx in _iter_reference_indices(text):
        if idx in seen:
            continue
        seen.add(idx)
        out.append(idx)
    return out


def build_citations_from_qwen_text(
    answer_text: str,
    *,
    chunk_by_index: dict[int, VerifiedChunk],
    default_source: str = "qwen_local",
) -> list[Citation]:
    """Build internal ``Citation`` records from Qwen's plain-text answer.

    Parameters
    ----------
    answer_text:
        The Qwen-generated answer string that may contain bracketed refs.
    chunk_by_index:
        Mapping from 1-based document index to the source ``VerifiedChunk``.
        This is the same map the ``anthropic_citation_adapter`` uses; the
        prompt-renderer is expected to have enumerated documents as
        ``[1] ... [2] ...`` or ``<document index="1">`` and pass through the
        corresponding map. Keys of 0 or negative values are ignored.
    default_source:
        Source label stamped on Citation.source when the chunk itself does
        not carry a source_id.

    Returns
    -------
    list[Citation]
        Ordered, deduplicated citations. Indices with no matching chunk
        are skipped (debug-logged).
    """
    if not answer_text:
        return []

    citations: list[Citation] = []
    anchor_counter = 1
    for idx in extract_indices(answer_text):
        if idx <= 0:
            _log.debug("qwen_citation_adapter: skipping non-positive index %d", idx)
            continue
        chunk = chunk_by_index.get(idx)
        if chunk is None:
            _log.debug(
                "qwen_citation_adapter: no chunk for index %d (map has %d entries)",
                idx,
                len(chunk_by_index),
            )
            continue

        snippet = (chunk.content or "")[:_CONTENT_SNIPPET_MAX]
        anchor = chunk.citation_anchor or f"[{anchor_counter}]"
        citation = Citation(
            doc_id=chunk.chunk_id,
            content_snippet=snippet,
            source=chunk.source_id or default_source,
            confidence=float(chunk.support_score or 0.0),
            citation_anchor=anchor,
            page_number=chunk.provenance.get("page_number")
            if isinstance(chunk.provenance, dict)
            else None,
            section=chunk.provenance.get("section")
            if isinstance(chunk.provenance, dict)
            else None,
        )
        citations.append(citation)
        anchor_counter += 1

    return citations


def citation_coverage_ratio(
    citations: list[Citation],
    must_use_chunks: list[VerifiedChunk],
) -> float:
    """Fraction of must-use chunks that appear in ``citations`` (0.0..1.0).

    Mirrors the contract of ``anthropic_citation_adapter.citation_coverage_ratio``
    so downstream completeness-enforcement code is provider-agnostic.
    """
    if not must_use_chunks:
        return 1.0
    must_ids = {c.chunk_id for c in must_use_chunks}
    cited_ids = {c.doc_id for c in citations}
    covered = must_ids & cited_ids
    return len(covered) / len(must_ids)


__all__ = [
    "build_citations_from_qwen_text",
    "citation_coverage_ratio",
    "extract_indices",
]
