"""Exemplar retrieval \u2014 W4 RH4.2.

Static keyword-matching selection using Jaccard similarity on tokenized
tags + input_text. W7 will replace this with embedding-based selection.

Deterministic: stable ordering for equal scores (falls back to exemplar_id).
"""

from __future__ import annotations

import re

from agentic_core.L4_state.exemplars.bank import ExemplarBank, ExemplarRecord


_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


def _tokens(text: str) -> frozenset[str]:
    """Extract lowercase word tokens from ``text``."""
    return frozenset(m.group(0).lower() for m in _WORD_RE.finditer(text or ""))


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _score(record: ExemplarRecord, query_tokens: frozenset[str]) -> float:
    tag_tokens = frozenset(t.lower() for t in record.tags)
    input_tokens = _tokens(record.input_text)
    # Weight tags 2x \u2014 they are curated, input_text is incidental.
    tag_score = _jaccard(tag_tokens, query_tokens)
    input_score = _jaccard(input_tokens, query_tokens)
    return 2.0 * tag_score + input_score


def select_top_k(
    *,
    query: str,
    task_class: str,
    bank: ExemplarBank,
    k: int = 3,
) -> tuple[ExemplarRecord, ...]:
    """Return the top-k records from ``bank`` for ``task_class`` matching ``query``.

    Returns an empty tuple if the bank has no records for the class or if
    ``k <= 0``. Results are ordered by descending score; ties broken by
    ascending ``exemplar_id`` for determinism.
    """
    if k <= 0:
        return ()
    candidates = bank.by_class(task_class)
    if not candidates:
        return ()

    query_tokens = _tokens(query)
    scored = [(_score(rec, query_tokens), rec.exemplar_id, rec) for rec in candidates]
    # Sort: primary = -score (desc), secondary = exemplar_id (asc) for determinism.
    scored.sort(key=lambda triple: (-triple[0], triple[1]))
    return tuple(rec for _, _, rec in scored[:k])


__all__ = ["select_top_k"]
