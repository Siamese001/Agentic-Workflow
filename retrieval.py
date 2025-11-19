# FILE: retrieval.py
"""
Retrieval Utilities (v10_9) — PURE META-LAYER RAG INFRA

This module provides higher-level retrieval utilities for the v10_9
agentic architecture. It is a *pure infrastructure* layer, sitting
below L2 executors and above low-level primitives in runtime_utils.

Responsibilities:
    • Normalize raw retrieval hits into canonical structures.
    • Apply ranking strategies (bm25, dense, hybrid) over retrieval results.
    • Fuse multiple retrieval sources into a single ranked list.
    • Enforce simple item limits (max_items).
    • Provide small, typed helpers that L2 executors (e.g., RAGExecutor)
      and external RAG clients can use.

Non-responsibilities (Agentic Guardrails):
    • NO L1 cognition (no planning).
    • NO L2 tool/LLM execution.
    • NO L3 orchestration.
    • NO L4 state management (no StateAdapter usage).
    • NO L5 safety decisions.
    • NO provider/DB/SDK calls.

This module is deterministic and side-effect-free.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from runtime_utils import Retrieval as _Retrieval
from runtime_utils import Ranking as _Ranking
from runtime_utils import RAGUtils as _RAGUtils


# =============================================================================
# 1. DATA CLASSES
# =============================================================================


@dataclass
class RetrievalConfig:
    """
    Configuration for retrieval post-processing.

    Fields:
        • ranking_strategy: "bm25" | "dense" | "hybrid".
        • max_items: maximum number of items to retain after fusion.
        • metadata: optional additional hints (e.g., source identifiers).
    """

    ranking_strategy: str = "hybrid"
    max_items: int = 50
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalItem:
    """
    Canonical retrieval item.

    Fields:
        • query: the query string used to retrieve this item.
        • evidence: the text snippet or document content.
        • rank: integer rank (1 = best).
        • metadata: arbitrary metadata (scores, ids, etc.).
    """

    query: str
    evidence: str
    rank: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """
    Aggregated retrieval result for a set of queries.

    Fields:
        • items: list of RetrievalItem objects.
        • config: RetrievalConfig used for post-processing.
    """

    items: List[RetrievalItem] = field(default_factory=list)
    config: RetrievalConfig = field(default_factory=RetrievalConfig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                {
                    "query": it.query,
                    "evidence": it.evidence,
                    "rank": it.rank,
                    "metadata": dict(it.metadata),
                }
                for it in self.items
            ],
            "config": {
                "ranking_strategy": self.config.ranking_strategy,
                "max_items": self.config.max_items,
                "metadata": dict(self.config.metadata),
            },
        }


# =============================================================================
# 2. INTERNAL HELPERS
# =============================================================================


def _apply_ranking_strategy(
    items: List[Dict[str, Any]],
    strategy: str,
) -> List[Dict[str, Any]]:
    """
    Apply the requested ranking strategy to a list of retrieval dicts.

    Strategy:
        • "bm25"   → length-based BM25-like ranking.
        • "dense"  → hash-based dense score ranking.
        • "hybrid" → combined BM25 + dense ranking.
        • default  → hybrid.
    """
    s = (strategy or "hybrid").lower()
    if s == "bm25":
        return _Ranking.bm25_rank(items)
    if s == "dense":
        return _Ranking.dense_rank(items)
    # fallback to hybrid
    return _Ranking.hybrid_rank(items)


def _limit_items(items: List[Dict[str, Any]], max_items: int) -> List[Dict[str, Any]]:
    """
    Limit the list of items to max_items, preserving order.
    """
    if max_items <= 0:
        return items
    if len(items) <= max_items:
        return items
    return items[:max_items]


# =============================================================================
# 3. PUBLIC API — SINGLE-SOURCE NORMALIZATION
# =============================================================================


def normalize_raw_results(
    raw_results: List[Dict[str, Any]],
    *,
    config: Optional{RetrievalConfig} = None,
) -> RetrievalResult:
    """
    Normalize raw retrieval results into a canonical RetrievalResult.

    Steps:
        1. Normalize raw dicts into {query, evidence, rank}.
        2. Deduplicate identical (query, evidence) pairs.
        3. Apply ranking strategy (bm25/dense/hybrid).
        4. Rerank & fuse results (single-source).
        5. Limit items to config.max_items.
        6. Normalize to RAG-style items with metadata.
        7. Return RetrievalResult with specialized RetrievalItem objects.

    This function does NOT call any external services; it operates on
    already-fetched raw results (e.g., from a DB, vector store, or LLM).
    """
    cfg = config or RetrievalConfig()

    # 1. Normalize query/evidence/rank structure
    norm = _Retrieval.normalize_documents(raw_results)

    # 2. Deduplicate
    norm = _Retrieval.dedupe_results(norm)

    # 3. Ranking strategy
    ranked = _apply_ranking_strategy(norm, cfg.ranking_strategy)

    # 4. Rerank and fuse (single source for now)
    reranked = _Retrieval.rerank_results(ranked, cfg.ranking_strategy)
    fused = _Retrieval.fuse_results([reranked])

    # 5. Limit items
    fused = _limit_items(fused, cfg.max_items)

    # 6. Normalize to RAG-style items with metadata
    rag_items = _RAGUtils.normalize_rag_results(fused)

    # 7. Convert to RetrievalItem objects
    items: List[RetrievalItem] = []
    for d in rag_items:
        items.append(
            RetrievalItem(
                query=str(d.get("query", "")),
                evidence=str(d.get("evidence", "")),
                rank=int(d.get("rank", 0) or 0),
                metadata=dict(d.get("metadata", {})),
            )
        )

    return RetrievalResult(items=items, config=cfg)


# =============================================================================
# 4. PUBLIC API — MULTI-SOURCE FUSION
# =============================================================================


def fuse_multiple_sources(
    sources: List[List[Dict[str, Any]]],
    *,
    config: Optional[RetrievalConfig] = None,
) -> RetrievalResult:
    """
    Fuse retrieval results from multiple sources into a single ranked list.

    Inputs:
        • sources:
            A list of lists, where each inner list is a set of raw retrieval
            dicts from a given source (e.g., vector DB, keyword DB, LLM-HYDE).

        • config:
            Optional RetrievalConfig controlling ranking and max_items.

    Behavior:
        1. Flatten all sources.
        2. Normalize and dedupe results.
        3. Apply ranking strategy (bm25/dense/hybrid).
        4. Limit items.
        5. Normalize to canonical RetrievalResult.

    This is designed to be a higher-level wrapper compared to
    normalize_raw_results() when you already have multiple raw sources.
    """
    cfg = config or RetrievalConfig()

    # Flatten sources
    merged: List[Dict[str, Any]] = []
    for source_list in sources or []:
        for item in source_list or []:
            merged.append(dict(item))

    return normalize_raw_results(merged, config=cfg)


# =============================================================================
# 5. UTILITY — SIMPLE DICT LIST VIEW
# =============================================================================


def to_simple_dict_list(result: RetrievalResult) -> List[Dict[str, Any]]:
    """
    Convenience helper: return a plain list[dict] for use in JSON or
    logging. Each item is:

        {
            "query": str,
            "evidence": str,
            "rank": int,
            "metadata": {...}
        }
    """
    return [
        {
            "query": it.query,
            "evidence": it.evidence,
            "rank": it.rank,
            "metadata": dict(it.metadata),
        }
        for it in result.items
    ]
