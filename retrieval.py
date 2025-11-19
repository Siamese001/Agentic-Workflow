# FILE: retrieval.py
"""
Retrieval Utilities (v10_9, Fully Refactored)
PURE META-LAYER RAG INFRASTRUCTURE

This module provides deterministic, enterprise-grade retrieval
post-processing utilities for the v10_9 agentic workflow.

It is strictly META-layer and must not perform:

    • L1 cognition (no planning)
    • L2 execution (no tool/LLM calls)
    • L3 orchestration (no DAG logic)
    • L4 state mutation (no StateAdapter usage)
    • L5 safety/policy decisions
    • Provider/SDK/DB/Vector Store calls

All behavior is deterministic and side-effect-free.

Restored 10_8 functionality:
    • Resume-aware ranking boosts
    • JD-aware scoring hints
    • Deduplication rules
    • Fusion across multiple retrieval streams
    • Evidence normalization
    • Configurable ranking strategy
    • Canonical RetrievalItem & RetrievalResult models
    • Metadata-rich RAG item schema
    • Multi-source fusion utilities
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from runtime_utils import Retrieval as _Retrieval
from runtime_utils import Ranking as _Ranking
from runtime_utils import RAGUtils as _RAGUtils


# ============================================================================
# 1. RETRIEVAL CONFIGURATION
# ============================================================================


@dataclass
class RetrievalConfig:
    """
    Configuration for retrieval post-processing.

    Fields:
        ranking_strategy:
            "bm25" | "dense" | "hybrid".
        max_items:
            Maximum number of items to retain after fusion.
        metadata:
            Optional additional hints (e.g., source identifiers).
        resume_alignment_boost:
            If True, apply resume-based boosting (10_8 parity).
        jd_alignment_boost:
            If True, apply JD-based boosting (10_8 parity).
    """

    ranking_strategy: str = "hybrid"
    max_items: int = 50
    metadata: Dict[str, Any] = field(default_factory=dict)
    resume_alignment_boost: bool = True
    jd_alignment_boost: bool = True


@dataclass
class RetrievalItem:
    """
    Canonical retrieval item.

    Fields:
        query:
            The query string used to retrieve this item.
        evidence:
            The text snippet or document content.
        rank:
            Integer rank (1 = best).
        metadata:
            Arbitrary metadata (scores, ids, etc.).
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
        items:
            list[RetrievalItem]
        config:
            RetrievalConfig used for post-processing.
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
                "resume_alignment_boost": self.config.resume_alignment_boost,
                "jd_alignment_boost": self.config.jd_alignment_boost,
            },
        }


# ============================================================================
# 2. INTERNAL HELPERS
# ============================================================================


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
    s = (strategy or "hybrid").lower().strip()
    if s == "bm25":
        return _Ranking.bm25_rank(items)
    if s == "dense":
        return _Ranking.dense_rank(items)
    # fallback to hybrid
    return _Ranking.hybrid_rank(items)


def _apply_resume_alignment_boost(
    items: List[Dict[str, Any]],
    resume_profile: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Resume-aware evidence boost (10_8 parity):

        • Evidence mentioning key resume attributes gets small boosts.
    """
    if not resume_profile:
        return items

    summary = (resume_profile.get("summary") or "").lower()
    experiences = resume_profile.get("experiences") or []

    keywords: List[str] = []
    if summary:
        keywords.extend(summary.split())
    for exp in experiences[:3]:
        title = (exp.get("title") or "").lower()
        company = (exp.get("company") or "").lower()
        if title:
            keywords.append(title)
        if company:
            keywords.append(company)

    if not keywords:
        return items

    boosted: List[Dict[str, Any]] = []
    for it in items:
        score = float(it.get("score", it.get("rank", 0)))
        ev = str(it.get("evidence", "")).lower()
        matches = sum(1 for k in keywords if k and k in ev)
        if matches:
            score += 0.2 * matches
        boosted.append({**it, "score": score})

    boosted.sort(key=lambda x: -x["score"])
    return boosted


def _apply_jd_alignment_boost(
    items: List[Dict[str, Any]],
    job_profile: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    JD-aware evidence boost (10_8 parity):

        • Evidence matching top JD requirements gets small boosts.
    """
    if not job_profile:
        return items

    reqs = job_profile.get("requirements") or []
    reqs = [str(r).lower() for r in reqs[:3] if r]

    if not reqs:
        return items

    boosted: List[Dict[str, Any]] = []
    for it in items:
        score = float(it.get("score", it.get("rank", 0)))
        ev = str(it.get("evidence", "")).lower()
        matches = sum(1 for req in reqs if req in ev)
        if matches:
            score += 0.3 * matches
        boosted.append({**it, "score": score})

    boosted.sort(key=lambda x: -x["score"])
    return boosted


def _limit_items(items: List[Dict[str, Any]], max_items: int) -> List[Dict[str, Any]]:
    """
    Limit the list of items to max_items, preserving order.
    """
    if max_items <= 0:
        return items
    if len(items) <= max_items:
        return items
    return items[:max_items]


# ============================================================================
# 3. PUBLIC API — SINGLE-SOURCE NORMALIZATION
# ============================================================================


def normalize_raw_results(
    raw_results: List[Dict[str, Any]],
    *,
    config: Optional[RetrievalConfig] = None,
    job_profile: Optional[Dict[str, Any]] = None,
    resume_profile: Optional[Dict[str, Any]] = None,
) -> RetrievalResult:
    """
    Normalize raw retrieval results into a canonical RetrievalResult.

    Steps:
        1. Normalize raw dicts into {query, evidence, rank}.
        2. Deduplicate identical (query, evidence) pairs.
        3. Apply ranking strategy (bm25/dense/hybrid).
        4. Optional resume alignment boosts.
        5. Optional JD alignment boosts.
        6. Rerank & fuse (single-source).
        7. Limit items to config.max_items.
        8. Normalize to RAG-style items with metadata.
        9. Convert to RetrievalItem objects.

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

    # 4. Resume alignment boost (optional)
    if cfg.resume_alignment_boost:
        ranked = _apply_resume_alignment_boost(ranked, resume_profile)

    # 5. JD alignment boost (optional)
    if cfg.jd_alignment_boost:
        ranked = _apply_jd_alignment_boost(ranked, job_profile)

    # 6. Rerank and fuse (single source for now)
    reranked = _Retrieval.rerank_results(ranked, cfg.ranking_strategy)
    fused = _Retrieval.fuse_results([reranked])

    # 7. Limit items
    fused = _limit_items(fused, cfg.max_items)

    # 8. Normalize to RAG-style items with metadata
    rag_items = _RAGUtils.normalize_rag_results(fused)

    # 9. Convert to RetrievalItem objects
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


# ============================================================================
# 4. PUBLIC API — MULTI-SOURCE FUSION
# ============================================================================


def fuse_multiple_sources(
    sources: List[List[Dict[str, Any]]],
    *,
    config: Optional[RetrievalConfig] = None,
    job_profile: Optional[Dict[str, Any]] = None,
    resume_profile: Optional[Dict[str, Any]] = None,
) -> RetrievalResult:
    """
    Fuse retrieval results from multiple sources into a single ranked list.

    Inputs:
        sources:
            A list of lists, where each inner list is a set of raw retrieval
            dicts from a given source (e.g., vector DB, keyword DB, LLM-HYDE).

        config:
            Optional RetrievalConfig controlling ranking and max_items.

    Behavior:
        1. Flatten all sources.
        2. Normalize and dedupe results.
        3. Apply ranking strategy + optional resume/JD boosts.
        4. Limit items.
        5. Normalize to canonical RetrievalResult.
    """
    cfg = config or RetrievalConfig()

    merged: List[Dict[str, Any]] = []
    for source_list in sources or []:
        for item in source_list or []:
            merged.append(dict(item))

    return normalize_raw_results(
        merged,
        config=cfg,
        job_profile=job_profile,
        resume_profile=resume_profile,
    )


# ============================================================================
# 5. UTILITY — SIMPLE DICT LIST VIEW
# ============================================================================


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
