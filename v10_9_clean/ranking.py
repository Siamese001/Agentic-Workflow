"""Ranking module consolidating ranking helpers."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List


def _stable_dense_score(query: str) -> int:
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()
    return int(digest, 16) % 100


def _order_and_rank(items: List[Dict[str, Any]], score_key: str) -> List[Dict[str, Any]]:
    ranked = [dict(item) for item in items]
    ranked.sort(
        key=lambda r: (
            -r.get(score_key, 0),
            r.get("query", ""),
            r.get("evidence", ""),
        )
    )
    for idx, entry in enumerate(ranked):
        entry["rank"] = idx + 1
    return ranked


def bm25_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []
    for item in items:
        evidence = str(item.get("evidence", ""))
        score = len(evidence)
        scored.append({**item, "bm25_score": score, "score": score})
    return _order_and_rank(scored, "score")


def dense_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []
    for item in items:
        query = str(item.get("query", ""))
        score = _stable_dense_score(query)
        scored.append({**item, "dense_score": score, "score": score})
    return _order_and_rank(scored, "score")


def hybrid_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []
    for item in items:
        evidence = str(item.get("evidence", ""))
        query = str(item.get("query", ""))
        bm25_score = len(evidence)
        dense_score = _stable_dense_score(query)
        score = (bm25_score + dense_score) / 2
        scored.append(
            {
                **item,
                "bm25_score": bm25_score,
                "dense_score": dense_score,
                "hybrid_score": score,
                "score": score,
            }
        )
    return _order_and_rank(scored, "score")
