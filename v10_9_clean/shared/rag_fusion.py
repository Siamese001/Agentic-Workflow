# FILE: v10_9_clean/shared/rag_fusion.py
"""
RAG Fusion Utilities (v10_9)

Implements deterministic multi-query fusion behavior consistent with
10_7/10_8 retrieval stacks. This centralizes merging logic:

    • merging evidence from multiple queries
    • rank-aware consolidation
    • deduplication across sources
    • weighted hybrid fusion
    • final deterministic ordering

This module contains ONLY pure functions.
"""

from __future__ import annotations
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Deduplication strategy
# ---------------------------------------------------------------------------

def _dedupe_key(item: Dict[str, Any]) -> tuple:
    """
    A deterministic identity key for deduplication.

    Uses:
        (normalized_query, normalized_evidence)
    """
    q = str(item.get("query", "")).strip().lower()
    e = str(item.get("evidence", "")).strip().lower()
    return (q, e)


# ---------------------------------------------------------------------------
# Hybrid-weighted fusion
# ---------------------------------------------------------------------------

def _compute_weighted_score(item: Dict[str, Any]) -> float:
    """
    Compute a deterministic hybrid score for fusion.

    Uses available fields:
        - rank (inverse)
        - metadata.evidence_length
        - metadata.snippet length
    """
    base_rank = int(item.get("rank", 0))
    evidence = item.get("metadata", {}).get("evidence_length", 0)
    snippet_len = len(item.get("metadata", {}).get("snippet", ""))

    # Lower rank = better; invert rank for weight
    rank_component = max(1, 100 - base_rank)

    # Evidence richness factor
    richness = evidence + snippet_len

    return float(rank_component + 0.1 * richness)


# ---------------------------------------------------------------------------
# Fusion entrypoint
# ---------------------------------------------------------------------------

def fuse_multi_query_results(sources: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merge multiple ranked lists into a single fused list.

    Behavior:
        1. Flatten all sources
        2. Deduplicate across sources
        3. Compute weighted hybrid score per item
        4. Sort by weighted score (descending), with deterministic tie-breaking
        5. Reassign final sequential rank (1..N)

    Returns:
        List of canonical retrieval items with updated ranks.
    """

    merged: List[Dict[str, Any]] = []

    # --- flatten ---
    for src in sources:
        for item in src:
            merged.append(dict(item))

    # --- dedupe ---
    deduped_map: Dict[tuple, Dict[str, Any]] = {}
    for item in merged:
        key = _dedupe_key(item)
        if key not in deduped_map:
            deduped_map[key] = item

    deduped_items = list(deduped_map.values())

    # --- compute weighted score ---
    for it in deduped_items:
        it["_fusion_score"] = _compute_weighted_score(it)

    # --- sort deterministically ---
    deduped_items.sort(
        key=lambda r: (
            -r.get("_fusion_score", 0.0),
            r.get("query", ""),
            r.get("metadata", {}).get("evidence_length", 0),
        )
    )

    # --- reassign final deterministic ranks ---
    for idx, entry in enumerate(deduped_items):
        entry["rank"] = idx + 1
        if "_fusion_score" in entry:
            del entry["_fusion_score"]

    return deduped_items
