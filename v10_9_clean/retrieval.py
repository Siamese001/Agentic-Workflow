# FILE: v10_9_clean/shared/retrieval.py
"""
Shared Retrieval Utilities (v10_9)

Provides deterministic normalization, fusion, dedupe, reranking, and budget-aware
truncation of retrieval results. This file contains pure functions only.
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, List

from shared.models import BudgetConfig


def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normed: List[Dict[str, Any]] = []
    for r in results:
        normed.append({
            "query": r.get("query", ""),
            "evidence": r.get("evidence", ""),
            "rank": r.get("rank", 0),
        })
    return normed


def dedupe_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for r in results:
        key = (r.get("query", ""), r.get("evidence", ""))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def rerank_results(results: List[Dict[str, Any]], strategy: str = "relevance_then_recency") -> List[Dict[str, Any]]:
    # Deterministic ascending-rank rerank
    return sorted(results, key=lambda r: r.get("rank", 0))


def fuse_results(source_lists: Iterable[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for src in source_lists:
        for item in src:
            merged.append(dict(item))
    return sorted(merged, key=lambda r: (r.get("query", ""), r.get("rank", 0)))


def truncate_by_budget(results: List[Dict[str, Any]], config: BudgetConfig) -> List[Dict[str, Any]]:
    limit = config.max_rag_items
    if len(results) <= limit:
        return results
    return results[-limit:]


def apply_ranker(results: List[Dict[str, Any]], strategy: str | None = None) -> List[Dict[str, Any]]:
    """
    Deterministic fallback ranker.
    Other rankers (bm25, dense, hybrid) live in shared/ranking.py.
    """
    if not results:
        return []
    return sorted(results, key=lambda r: (r.get("rank", 0), r.get("query", "")))
