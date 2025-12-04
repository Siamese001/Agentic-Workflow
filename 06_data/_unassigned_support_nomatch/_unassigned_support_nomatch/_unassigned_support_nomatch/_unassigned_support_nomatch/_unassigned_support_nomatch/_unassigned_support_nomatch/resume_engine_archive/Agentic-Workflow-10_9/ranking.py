# FILE: ranking.py
"""
Ranking Utilities (v10_9) — PURE META-LAYER MODULE

This module provides deterministic ranking functions for use by:

    • L2 RAGExecutor
    • retrieval.py
    • routing/meta layers
    • simulation harness
    • observability

It must remain strictly *META* and never call:
    • L1 planners
    • L2 executors directly
    • L3 orchestration
    • L4 StateAdapter
    • L5 Safety/Policy engines
    • Provider/LLM/DB/Network code

All ranking here is deterministic and side-effect-free.

The actual ranking algorithms are delegated to runtime_utils.Ranking.
This file wraps those behaviors and exposes a stable API.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_utils import Ranking as _Ranking


# ============================================================================
# 1. ALGORITHM WRAPPERS
# ============================================================================

def bm25(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deterministic BM25-like ranking.

    Delegates scoring to runtime_utils.Ranking.bm25_rank.
    """
    return _Ranking.bm25_rank(items)


def dense(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deterministic dense-score ranking (SHA-based pseudo-embedding).
    """
    return _Ranking.dense_rank(items)


def hybrid(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Combined ranking (BM25 + dense).
    """
    return _Ranking.hybrid_rank(items)


# ============================================================================
# 2. STRATEGY ROUTING
# ============================================================================

def apply_strategy(
    items: List[Dict[str, Any]],
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    Apply a ranking strategy:

        "bm25"
        "dense"
        "hybrid"
        anything else → hybrid

    After ranking, all candidates receive a deterministic "rank" field.

    This function never mutates the caller’s list.
    """
    s = (strategy or "hybrid").lower().strip()

    if s == "bm25":
        ranked = bm25(items)
    elif s == "dense":
        ranked = dense(items)
    else:
        ranked = hybrid(items)

    # Assign integer rank (1-based)
    out: List[Dict[str, Any]] = []
    for idx, item in enumerate(ranked):
        new_item = dict(item)
        new_item["rank"] = idx + 1
        out.append(new_item)

    return out


# ============================================================================
# 3. FUSION HELPERS
# ============================================================================

def fuse_ranked_groups(groups: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Fuse multiple pre-ranked lists into a single deterministic list.

    Algorithm:
        1. Flatten
        2. Deduplicate by (query, evidence)
        3. Sort by minimal rank across groups
        4. Secondary sort by alphabetical evidence
        5. Re-assign ranks

    All behavior purely deterministic.
    """
    flattened: List[Dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for group in groups or []:
        for item in group or []:
            key = (str(item.get("query", "")), str(item.get("evidence", "")))
            if key not in seen:
                seen.add(key)
                flattened.append(dict(item))

    flattened.sort(
        key=lambda x: (
            int(x.get("rank", 9_999_999)),
            str(x.get("evidence", "")).lower(),
        )
    )

    # Reassign clean ranks
    for idx, item in enumerate(flattened):
        item["rank"] = idx + 1

    return flattened


# ============================================================================
# 4. HIGH-LEVEL API
# ============================================================================

def rank_documents(
    items: List[Dict[str, Any]],
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    Top-level ranking helper used by RAGExecutor:

        items:
            list[{ query, evidence, ... }]

        strategy:
            "bm25" | "dense" | "hybrid"

    Returns ranked+sorted list with final deterministic ordering.
    """
    if not items:
        return []

    ranked = apply_strategy(items, strategy=strategy)

    # Final stability sort
    ranked.sort(
        key=lambda x: (
            int(x.get("rank", 9_999_999)),
            x.get("evidence", ""),
        )
    )
    return ranked
