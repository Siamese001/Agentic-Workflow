# FILE: ranking.py
"""
Ranking Utilities (v10_9) — ENTERPRISE MODULE

This module provides pure deterministic ranking algorithms for use by
L2 retrieval executors (e.g., RAGExecutor) and by upstream infra modules
(retrieval.py, routing.py).

It is infrastructure-only, sitting BELOW L2 executors and ABOVE the
runtime_utils primitives.

Responsibilities:
    • Provide BM25-like scoring (length-based).
    • Provide dense score ranking (hash-based).
    • Provide hybrid ranking (BM25 + dense).
    • Provide fallback semantics.
    • Provide consistent deterministic ordering.
    • No external dependencies, no randomness.

Non-responsibilities:
    • NO L1 planning.
    • NO L2 execution logic.
    • NO orchestration.
    • NO L4 state mutation.
    • NO safety decisions.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_utils import Ranking as _Ranking


# =============================================================================
# 1. ALGORITHM WRAPPERS
# =============================================================================

def bm25(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply deterministic BM25-like ranking. This delegates to the
    canonical BM25 implementation in runtime_utils.Ranking.
    """
    return _Ranking.bm25_rank(items)


def dense(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply deterministic dense-score ranking (hash-based).
    """
    return _Ranking.dense_rank(items)


def hybrid(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply the hybrid ranker (BM25 + dense).
    """
    return _Ranking.hybrid_rank(items)


# =============================================================================
# 2. ROUTING LAYER
# =============================================================================

def apply_strategy(
    items: List[Dict[str, Any]],
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    Apply the requested ranking strategy.

    Inputs:
        • items: list of dicts containing "evidence" and optional metadata.
        • strategy:
            "bm25"   – BM25-like ranking
            "dense"  – Dense score ranking
            "hybrid" – Combined ranking
            else     – fallback to hybrid

    Output:
        • Ranked list of dicts, each with a deterministic "rank" value.
    """
    s = (strategy or "hybrid").lower().strip()
    if s == "bm25":
        ranked = bm25(items)
    elif s == "dense":
        ranked = dense(items)
    else:
        ranked = hybrid(items)

    # Ensure clean integer rank assignment
    for idx, item in enumerate(ranked):
        item["rank"] = idx + 1

    return ranked


# =============================================================================
# 3. FUSION HELPERS
# =============================================================================

def fuse_ranked_groups(groups: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Fuse multiple pre-ranked lists into a single ranked list.

    Inputs:
        • groups: list of ranked lists (already sorted by rank)

    Behavior:
        • Flatten the groups.
        • Deduplicate by (query, evidence).
        • Produce final sorted result by minimal rank across groups.
        • Secondary sort by alphabetical evidence text.

    Output:
        • Final fused ranked list with clean integer rank values.
    """
    flattened: List[Dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for group in groups:
        for item in group:
            key = (str(item.get("query", "")), str(item.get("evidence", "")))
            if key not in seen:
                seen.add(key)
                flattened.append(dict(item))

    # Sort by rank first, evidence second
    flattened.sort(key=lambda x: (int(x.get("rank", 9999999)), str(x.get("evidence", "")).lower()))

    # Reassign clean ranks
    for idx, item in enumerate(flattened):
        item["rank"] = idx + 1

    return flattened


# =============================================================================
# 4. NARROW API FOR RAG EXECUTORS
# =============================================================================

def rank_documents(
    items: List[Dict[str, Any]],
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    High-level wrapper used by RAGExecutor.

    - Applies the chosen strategy.
    - Returns a sorted list with clean rank values.
    """
    if not items:
        return []

    ranked = apply_strategy(items, strategy=strategy)

    # Final deterministic sort for stability
    ranked.sort(key=lambda x: (int(x.get("rank", 999999)), x.get("evidence", "")))

    return ranked
