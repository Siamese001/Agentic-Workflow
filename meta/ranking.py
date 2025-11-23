from __future__ import annotations

from typing import Any, Dict, Iterable, List

from models import Evidence


def bm25_score(item: Dict[str, Any]) -> float:
    """BM25-style deterministic score used by META ranking helpers.

    Mirrors the simple scoring behavior used in the core ranking module
    (lowercasing, term counting, and a length-normalized bonus) but is
    defined here so L2/L3 do not rely on private helpers.
    """

    text = str(item.get("text") or item.get("evidence") or "").lower()
    if not text:
        return 0.0

    tokens = text.split()
    length = len(tokens)
    bonus = 0.0

    important = {"llm", "resume", "experience", "impact", "owner", "lead"}
    for t in tokens:
        if t in important:
            bonus += 0.75

    base = bonus / (1.0 + (length / 50.0))
    return float(base)


def dense_score(item: Dict[str, Any]) -> float:
    """Dense-style pseudo-embedding score (hash-based, deterministic)."""

    text = str(item.get("text") or item.get("evidence") or "").lower()
    if not text:
        return 0.0

    h = hash(text)
    return float((h % 10_000_000) / 10_000_000.0)


def normalize_scores(evidence: Iterable[Evidence]) -> List[Evidence]:
    """Normalize evidence scores to [0, 1] across the provided items."""

    items = list(evidence)
    if not items:
        return []

    scores = [e.score for e in items]
    max_score = max(scores)
    min_score = min(scores)

    if max_score == min_score:
        return [e.model_copy(update={"score": 1.0}) for e in items]

    span = max_score - min_score
    out: List[Evidence] = []
    for e in items:
        norm = (e.score - min_score) / span
        out.append(e.model_copy(update={"score": float(norm)}))
    return out


def merge_scores(evidence: Iterable[Evidence]) -> List[Evidence]:
    """Deduplicate evidence items by (source, text) while preserving order."""

    items: List[Evidence] = []
    seen: set[tuple[str, str]] = set()
    for ev in evidence:
        key = (str(ev.source or ""), ev.text)
        if key in seen:
            continue
        seen.add(key)
        items.append(ev)
    return items
