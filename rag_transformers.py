from typing import Any, Dict, List

from rankers import bm25_rank, dense_rank, hybrid_rank
from utils_types import BudgetConfig


def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Deterministic shallow normalization
    normed = []
    for r in results:
        normed.append({
            "query": r.get("query", ""),
            "rank": r.get("rank", 0),
            "evidence": r.get("evidence", ""),
        })
    return normed


def dedupe_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for r in results:
        key = (r.get("query", ""), r.get("evidence", ""))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def rerank_results(results: List[Dict[str, Any]], strategy: str = "relevance_then_recency") -> List[Dict[str, Any]]:
    # Deterministic: sort by rank ascending
    return sorted(results, key=lambda r: r.get("rank", 0))


def fuse_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Deterministic grouping by query
    # (Flat output, but stable order)
    return sorted(results, key=lambda r: r.get("query", ""))


def truncate_by_budget(results: List[Dict[str, Any]], config: BudgetConfig) -> List[Dict[str, Any]]:
    # Trim to max_rag_items
    if len(results) <= config.max_rag_items:
        return results
    return results[-config.max_rag_items:]


def apply_ranker(results: List[Dict[str, Any]], strategy: str | None = None) -> List[Dict[str, Any]]:
    if strategy == "bm25":
        return bm25_rank(results)
    if strategy == "dense":
        return dense_rank(results)
    if strategy == "hybrid":
        return hybrid_rank(results)
    return rerank_results(results, strategy or "relevance_then_recency")
