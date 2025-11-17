"""Retrieval module consolidating RAG configuration and transformers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from shared.models import BudgetConfig  # UPDATED: used to be utils_types.BudgetConfig
from .ranking import bm25_rank, dense_rank, hybrid_rank


@dataclass
class RetrievalConfig:
    queries: List[str]
    filters: Dict[str, Any]
    ranking: Dict[str, Any]
    metadata: Dict[str, Any] | None = None

    def to_plan_fragment(self) -> Dict[str, Any]:
        return {
            "queries": self.queries,
            "filters": self.filters,
            "ranking": self.ranking,
            "metadata": self.metadata or {},
        }


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


def fuse_results(list_of_sources: Iterable[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for source in list_of_sources:
        for item in source:
            merged.append(dict(item))

    return sorted(merged, key=lambda r: (r.get("query", ""), r.get("rank", 0)))
