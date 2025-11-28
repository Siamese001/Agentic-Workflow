# FILE: retrieval.py
"""
Retrieval Utilities (v10_9) — PURE META-LAYER RAG INFRA (META-AWARE, REFINED)

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
    • Adapt behavior based on meta_profile biases (routing/planning/QA/safety)
      without violating L1–L5 boundaries.

Non-responsibilities (Agentic Guardrails):
    • NO L1 cognition (no planning).
    • NO L2 tool/LLM execution.
    • NO L3 orchestration.
    • NO L4 state management (no StateAdapter usage).
    • NO L5 safety decisions.
    • NO provider/DB/SDK calls.

META-awareness (from meta_profile):
    • routing_bias.prefer_fast             → fewer items, lighter ranking.
    • routing_bias.prefer_robust_retrieval → hybrid ranking, more items.
    • planning_bias.conservative           → increase coverage (more items).
    • qa_bias.recent_failures              → increase coverage (more items).
    • safety_bias.heightened_caution       → filter out obviously risky items.

All behavior here is deterministic and side-effect-free.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from runtime.runtime_utils_v10_9 import Retrieval as _Retrieval
from runtime.runtime_utils_v10_9 import Ranking as _Ranking
from runtime.runtime_utils_v10_9 import RAGUtils as _RAGUtils

from meta_profile import (
    get_routing_bias,
    get_planning_bias,
    get_qa_bias,
    get_safety_bias,
)


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


def _apply_meta_biases_to_config(cfg: RetrievalConfig) -> RetrievalConfig:
    """
    Return a new RetrievalConfig adjusted by meta_profile biases.

    Meta influences:

        • routing_bias.prefer_fast:
            - reduce max_items (e.g., by half)
        • routing_bias.prefer_robust_retrieval:
            - enforce hybrid ranking, slightly more items
        • planning_bias.conservative:
            - increase max_items (more coverage)
        • qa_bias.recent_failures:
            - increase max_items (more evidence)
        • safety_bias.heightened_caution:
            - add flag in metadata for optional downstream filtering

    All behavior is deterministic and side-effect-free; original cfg is
    not mutated.
    """
    routing = get_routing_bias()
    planning = get_planning_bias()
    qa = get_qa_bias()
    safety = get_safety_bias()

    new_cfg = RetrievalConfig(
        ranking_strategy=cfg.ranking_strategy,
        max_items=cfg.max_items,
        metadata=dict(cfg.metadata),
    )

    # Routing biases
    if routing.get("prefer_fast"):
        # Aggressively reduce the number of items to consider downstream.
        new_cfg.max_items = max(10, cfg.max_items // 2)
        new_cfg.metadata["meta_prefer_fast"] = True

    if routing.get("prefer_robust_retrieval"):
        new_cfg.ranking_strategy = "hybrid"
        new_cfg.max_items = max(cfg.max_items, 60)
        new_cfg.metadata["meta_prefer_robust_retrieval"] = True

    # Planning / QA biases: increase coverage
    if planning.get("conservative") or qa.get("recent_failures"):
        new_cfg.max_items = max(new_cfg.max_items, cfg.max_items + 20)
        new_cfg.metadata["meta_conservative_or_qa_failures"] = True

    # Safety bias: mark runs as high-safety for downstream filters
    if safety.get("heightened_caution"):
        new_cfg.metadata["meta_high_safety"] = True

    return new_cfg


def _filter_for_safety(items: List[Dict[str, Any]], safety_bias: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply very light deterministic filtering for obviously risky items.

    For now, this is deliberately simple and hard-coded. It is meant to
    support heightened_caution flows by removing items that contain
    highly suspicious markers in 'evidence'.
    """
    if not safety_bias.get("heightened_caution"):
        return items

    filtered: List[Dict[str, Any]] = []
    risky_markers = ["password", "ssn", "social security number"]
    for it in items:
        ev = str(it.get("evidence", "")).lower()
        if any(m in ev for m in risky_markers):
            continue
        filtered.append(it)
    return filtered


# =============================================================================
# 3. PUBLIC API — SINGLE-SOURCE NORMALIZATION
# =============================================================================


def normalize_raw_results(
    raw_results: List[Dict[str, Any]],
    *,
    config: Optional[RetrievalConfig] = None,
) -> RetrievalResult:
    """
    Normalize raw retrieval results into a canonical RetrievalResult.

    Steps:
        0. Apply meta_profile biases to RetrievalConfig.
        1. Normalize raw dicts into {query, evidence, rank}.
        2. Deduplicate identical (query, evidence) pairs.
        3. Apply ranking strategy (bm25/dense/hybrid).
        4. Rerank & fuse results (single-source).
        5. Limit items to config.max_items.
        6. Optionally filter for basic safety when heightened_caution.
        7. Normalize to RAG-style items with metadata.
        8. Return RetrievalResult with RetrievalItem objects.

    This function does NOT call any external services; it operates on
    already-fetched raw results (e.g., from a DB, vector store, or LLM).
    """
    base_cfg = config or RetrievalConfig()
    cfg = _apply_meta_biases_to_config(base_cfg)

    # 1. Normalize query/evidence/rank structure
    norm = _Retrieval.normalize_documents(raw_results)

    # 2. Deduplicate
    norm = _Retrieval.dedupe_results(norm)

    # 3. Ranking strategy
    ranked = _apply_ranking_strategy(norm, cfg.ranking_strategy)

    # 4. Rerank and fuse (single source)
    reranked = _Retrieval.rerank_results(ranked, cfg.ranking_strategy)
    fused = _Retrieval.fuse_results([reranked])

    # 5. Limit items
    fused = _limit_items(fused, cfg.max_items)

    # 6. Optional safety filtering
    safety_bias = get_safety_bias()
    fused = _filter_for_safety(fused, safety_bias)

    # 7. Normalize to RAG-style items with metadata
    rag_items = _RAGUtils.normalize_rag_results(fused)

    # 8. Convert to RetrievalItem objects
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
        0. Apply meta_profile biases to RetrievalConfig.
        1. Flatten all sources into one list.
        2. Normalize and dedupe results.
        3. Apply ranking strategy (bm25/dense/hybrid).
        4. Limit items to config.max_items.
        5. Optional meta-aware safety filtering.
        6. Normalize to canonical RetrievalResult.
    """
    base_cfg = config or RetrievalConfig()
    cfg = _apply_meta_biases_to_config(base_cfg)

    merged: List[Dict[str, Any]] = []
    for source_list in sources or []:
        for item in source_list or []:
            merged.append(dict(item))

    # Reuse normalize_raw_results for the merged list — but it will apply
    # meta-aware config logic and ranking again internally.
    # NOTE: pass cfg so that we preserve effective meta-aware configuration.
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
