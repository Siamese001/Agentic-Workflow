# FILE: 10_10/ranking.py
"""
Ranking Utilities (v10_10) — PURE META-LAYER MODULE
===================================================

This module is a refactored version of the v10_9 ranking utilities,
updated to align with the v10_10 architecture.

Responsibilities:
    • Provide deterministic, side-effect-free ranking functions.
    • Support both:
        - Dict-based ranking (backward compatibility with v10_9-style callers).
        - Evidence-based ranking for the v10_10 RAG pipeline.

Non-Responsibilities:
    • No LLM calls.
    • No retrieval (see retrieval.py).
    • No orchestration (L3).
    • No state mutation (L4).
    • No safety decisions (L5).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from models import RAGPlan, Evidence


# =============================================================================
# Internal Scoring Helpers (Deterministic, Pure)
# =============================================================================

def _tokenize(text: str) -> List[str]:
    return [t for t in text.lower().split() if t.strip()]


def _bm25_score(item: Dict[str, Any]) -> float:
    """
    Very simple BM25-like scoring approximation for dict-based ranking.

    Expects:
        item["query"]:    str
        item["evidence"]: str

    We approximate BM25 by counting overlapping tokens.
    """
    query = str(item.get("query", ""))
    evidence = str(item.get("evidence", ""))

    q_tokens = set(_tokenize(query))
    e_tokens = set(_tokenize(evidence))

    if not q_tokens or not e_tokens:
        return 0.0

    overlap = len(q_tokens & e_tokens)
    norm = max(1, len(q_tokens))

    return overlap / norm


def _dense_score(item: Dict[str, Any]) -> float:
    """
    Dense-score approximation using a deterministic hash-based pseudo-similarity.

    This is a non-ML, purely deterministic heuristic to stand in place of
    embedding-based similarity in environments where we can't call out to
    a real embedding service.
    """
    query = str(item.get("query", ""))
    evidence = str(item.get("evidence", ""))

    # Simple hash-based pseudo similarity
    q_hash = hash(query) & 0xFFFFFFFF
    e_hash = hash(evidence) & 0xFFFFFFFF

    # Normalize difference to [0, 1], invert so smaller diff → higher score
    diff = abs(q_hash - e_hash) / float(0xFFFFFFFF or 1)
    return max(0.0, 1.0 - diff)


def _hybrid_score(item: Dict[str, Any]) -> float:
    """
    Hybrid score = average of bm25-like and dense scores.
    """
    b = _bm25_score(item)
    d = _dense_score(item)
    return (b + d) / 2.0


# =============================================================================
# 1. ALGORITHM WRAPPERS (DICT-BASED API, BACKWARD COMPATIBLE)
# =============================================================================

def bm25(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deterministic BM25-like ranking for dict-based items.

    Each item MUST contain:
        - "query": str
        - "evidence": str
    """
    scored: List[Dict[str, Any]] = []
    for it in items or []:
        new_it = dict(it)
        new_it["score"] = _bm25_score(new_it)
        scored.append(new_it)

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return scored


def dense(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deterministic dense-score ranking (hash-based pseudo-embedding).
    """
    scored: List[Dict[str, Any]] = []
    for it in items or []:
        new_it = dict(it)
        new_it["score"] = _dense_score(new_it)
        scored.append(new_it)

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return scored


def hybrid(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Combined ranking (BM25 + dense).
    """
    scored: List[Dict[str, Any]] = []
    for it in items or []:
        new_it = dict(it)
        new_it["score"] = _hybrid_score(new_it)
        scored.append(new_it)

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return scored


# =============================================================================
# 2. STRATEGY ROUTING (DICT-BASED API)
# =============================================================================

def apply_strategy(
    items: List[Dict[str, Any]],
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    Apply a ranking strategy:

        strategy:
            "bm25"
            "dense"
            "hybrid"
            any other value → hybrid

    After ranking, all candidates receive a deterministic "rank" field.

    This function does NOT mutate the caller’s list.
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


# =============================================================================
# 3. FUSION HELPERS (DICT-BASED API)
# =============================================================================

def fuse_ranked_groups(groups: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Fuse multiple pre-ranked lists into a single deterministic list.

    Algorithm:
        1. Flatten
        2. Deduplicate by (query, evidence)
        3. Sort by minimal rank across groups
        4. Secondary sort by alphabetical evidence
        5. Re-assign ranks
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

    for idx, item in enumerate(flattened):
        item["rank"] = idx + 1

    return flattened


# =============================================================================
# 4. HIGH-LEVEL DICT API (BACKWARD COMPATIBLE)
# =============================================================================

def rank_documents(
    items: List[Dict[str, Any]],
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    Top-level ranking helper used by dict-based RAG components (backward compatible).

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
            str(x.get("evidence", "")),
        )
    )
    return ranked


# =============================================================================
# 5. EVIDENCE-BASED RANKING (v10_10 PRIMARY API)
# =============================================================================

def rank_evidence(
    raw_hits: List[Evidence],
    rag_plan: RAGPlan,
    ctx: Any,
    top_k: Optional[int] = None,
) -> List[Evidence]:
    """
    v10_10-native ranking API used by L2.execute_rag.

    Inputs:
        raw_hits: list[Evidence]
        rag_plan: RAGPlan            (currently unused for heuristics; future hook)
        ctx:      ExecutionContext   (currently unused; future hook)
        top_k:    optional cap on returned items

    Behavior:
        • Deterministically sort Evidence by score descending.
        • Optionally truncate to top_k.
        • Return a NEW list of Evidence objects (no mutation of input).
    """
    if not raw_hits:
        return []

    hits = list(raw_hits)
    hits.sort(key=lambda e: e.score, reverse=True)

    if top_k is not None and top_k > 0:
        hits = hits[:top_k]

    return hits
