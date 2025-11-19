# FILE: retrieval.py
"""
Retrieval Utilities (v10_9, Refactored) — PURE META-LAYER RAG INFRASTRUCTURE

This module provides fully deterministic, enterprise-grade retrieval
post-processing utilities for the v10_9 agentic workflow.

It is strictly META-layer and must not perform:

    • L1 cognition (no planning)
    • L2 execution (no tool/LLM calls)
    • L3 orchestration (no DAG logic)
    • L4 mutation (no StateAdapter usage)
    • L5 safety/policy decisions
    • Provider/SDK/DB/Vector Store calls

All behavior is deterministic, side-effect-free, and typed.

This refactored version restores all missing 10_8 functionality:
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
    Configures retrieval+ranking post-processing.

    Attributes:
        ranking_strategy:
            "bm25" | "dense" | "hybrid"
        max_items:
            Maximum number of items after fusion/ranking.
        metadata:
            Optional arbitrary metadata block attached to final result.
        resume_alignment_boost:
            Whether to boost scores from resume-linked evidence.
        jd_alignment_boost:
            Whether to boost evidence covering JD requirements.
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
        query:     query string used
        evidence:  text snippet
        rank:      integer rank (1 = best)
        metadata:  metadata for scoring / ranking / display

    The metadata field is preserved end-to-end and never mutated.
    """

    query: str
    evidence: str
    rank: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """
    Aggregated result of retrieval across queries and sources.

    Fields:
        items:  list[RetrievalItem]
        config: RetrievalConfig used to generate result
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
# 2. INTERNAL HELPERS (PRIVATE)
# ============================================================================

def _apply_resume_alignment_boost(
    items: List[Dict[str, Any]],
    resume_profile: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Lightweight resume-aware evidence boost:

        • Longer experience snippets receive small boosts.
        • Evidence mentioning company/job title receives small boosts.

    Boosts are deterministic and subtle — only used for tie-breaking.
    """
    if not resume_profile:
        return items

    company = (resume_profile.get("company") or "").lower()
    title = (resume_profile.get("title") or "").lower()

    boosted = []
    for it in items:
        score = float(it.get("score", it.get("rank", 0)))

        ev = str(it.get("evidence", "")).lower()
        if company and company in ev:
            score += 0.5
        if title and title in ev:
            score += 0.25

        boosted.append({**it, "score": score})

    boosted.sort(key=lambda x: -x["score"])
    return boosted


def _apply_jd_alignment_boost(
    items: List[Dict[str, Any]],
    job_profile: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    JD-aware retrieval boost:

        • Evidence matching first 3 JD requirements gets small boosts.
    """
    if not job_profile:
        return items

    reqs = job_profile.get("requirements") or []
    reqs = [r.lower() for r in reqs[:3]]

    boosted = []
    for it in items:
        score = float(it.get("score", it.get("rank", 0)))
        ev = str(it.get("evidence", "")).lower()

        for req in reqs:
            if req and req in ev:
                score += 0.4

        boosted.append({**it, "score": score})

    boosted.sort(key=lambda x: -x["score"])
    return boosted


def _limit_items(items: List[Dict[str, Any]], max_items: int) -> List[Dict[str, Any]]:
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
    Normalize a list of raw dict results into a canonical RetrievalResult.

    Steps:
        1. Normalize dicts → {query, evidence, rank}
        2. Deduplicate identical (query, evidence)
        3. Apply ranking strategy (BM25/dense/hybrid)
        4. Optional resume- and JD-alignment boosts
        5. Rerank
