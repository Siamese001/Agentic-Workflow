# FILE: v10_9_clean/shared/ranking.py
"""
Shared Ranking Utilities (v10_9)

Implements deterministic BM25-style ranking, dense similarity ranking, and
hybrid ranking (combined BM25 + dense). These are pure functions containing
no external dependencies.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List


def _stable_dense_score(text: str) -> int:
    """Stable pseudo-embedding similarity score."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest, 16) % 100


def _order_and_rank(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    ranked = [{**item} for item in items]
    ranked.sort(
        key=lambda r: (
            -float(r.get(key, 0)),
            r.get("query", ""),
            r.get("evidence", ""),
        )
    )
    for i, entry in enumerate(ranked):
        entry["rank"] = i + 1
    return ranked


def bm25_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank by BM25-like proxy — evidence length."""
    scored = []
    for item in items:
        evidence = str(item.get("evidence", ""))
        score = len(evidence)
        scored.append({**item, "bm25_score": score, "score": score})
    return _order_and_rank(scored, "score")


def dense_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank by stable hash-based dense proxy."""
    scored = []
    for item in items:
        q = str(item.get("query", ""))
        score = _stable_dense_score(q)
        scored.append({**item, "dense_score": score, "score": score})
    return _order_and_rank(scored, "score")


def hybrid_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Hybrid: combine BM25 and dense scores."""
    scored = []
    for item in items:
        evidence = str(item.get("evidence", ""))
        query = str(item.get("query", ""))

        bm_score = len(evidence)
        d_score = _stable_dense_score(query)
        score = (bm_score + d_score) / 2

        scored.append({
            **item,
            "bm25_score": bm_score,
            "dense_score": d_score,
            "hybrid_score": score,
            "score": score,
        })

    return _order_and_rank(scored, "score")
