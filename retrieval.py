# FILE: retrieval.py
"""
Retrieval Engine (v10_10 • Phase 3 — FINAL)
===========================================

This module is strictly META-layer logic (L2-free, L3-free):

    • BM25 retrieval
    • Dense retrieval
    • Hybrid retrieval orchestration
    • HYDE query integration (from L2)
    • Weighted RRF fusion
    • QA-council evidence weighting
    • Telemetry event emission

Design principles:
    - No LLM calls here (HYDE query is generated in L2).
    - Deterministic behavior unless HYDE is supplied.
    - Pure ranking/scoring; no state mutation.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    Evidence,
    RetrievalConfig,
    RetrievalAttemptEvent,
    RetrievalResultEvent,
    RankingEvent,
    CouncilVote,
)
from .observability import emit_telemetry_event


# ======================================================================
# INTERNAL HELPERS
# ======================================================================


def _emit_attempt(ctx, method: str, query: str):
    emit_telemetry_event(
        RetrievalAttemptEvent(
            name="retrieval.attempt",
            method=method,
            query=query,
            workflow_id=ctx.workflow_id,
        )
    )


def _emit_result(ctx, method: str, hit_count: int, max_hits: int):
    emit_telemetry_event(
        RetrievalResultEvent(
            name="retrieval.result",
            method=method,
            hit_count=hit_count,
            max_hits=max_hits,
            workflow_id=ctx.workflow_id,
        )
    )


# ======================================================================
# FAKE BM25 + DENSE RETRIEVERS (stub implementations preserved)
# ======================================================================


def _bm25_search(query: str, k1: float, b: float, max_hits: int) -> List[Evidence]:
    """
    Deterministic BM25 stub.
    In production, replace this with a real index lookup.
    """
    return [
        Evidence(
            id=f"bm25_{i}",
            text=f"BM25 evidence {i} for: {query}",
            score=1.0 / (i + 1.0),
            source="bm25",
            metadata={"rank": i},
        )
        for i in range(max_hits)
    ]


def _dense_search(query: str, max_hits: int) -> List[Evidence]:
    """
    Deterministic dense retrieval stub.
    """
    return [
        Evidence(
            id=f"dense_{i}",
            text=f"Dense evidence {i} for: {query}",
            score=1.0 / (i + 2.0),
            source="dense",
            metadata={"rank": i},
        )
        for i in range(max_hits)
    ]


# ======================================================================
# RRF HELPERS
# ======================================================================


def _trim_weights(weights: Optional[List[float]], groups: int) -> List[float]:
    if not weights:
        return [1.0] * groups
    if len(weights) == groups:
        return weights
    if len(weights) > groups:
        return weights[:groups]
    # Extend short list
    return weights + [weights[-1]] * (groups - len(weights))


def _rrf_fuse(groups: List[List[Evidence]], weights: List[float]) -> List[Evidence]:
    """
    Weighted RRF implementation (Phase-3 requirement).
    """
    score_map: Dict[str, float] = {}
    evidence_map: Dict[str, Evidence] = {}

    for g_idx, group in enumerate(groups):
        w = weights[g_idx]
        for rank, ev in enumerate(group):
            score = w * (1.0 / (60.0 + rank))
            score_map[ev.id] = score_map.get(ev.id, 0.0) + score
            if ev.id not in evidence_map:
                evidence_map[ev.id] = ev

    # Sort by fused score
    items = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    fused = [evidence_map[eid] for eid, _ in items]
    return fused


# ======================================================================
# QA-COUNCIL EVIDENCE WEIGHTING
# ======================================================================


def _apply_qa_council_weights(
    fused: List[Evidence], council: Optional[CouncilVote]
) -> List[Evidence]:
    """
    Apply council-based adjustments to scores:
        • Boost evidence if related to council-selected findings.
        • Slightly demote evidence tied to losing branches.

    Gaps resolved: G10, G29, G31.
    """
    if council is None or council.selected_id is None:
        return fused

    selected = council.selected_id
    boost = 1.15
    demote = 0.90

    adjusted: List[Evidence] = []
    for ev in fused:
        ev2 = ev.copy()
        if selected in ev.text:
            ev2.score *= boost
        else:
            ev2.score *= demote
        adjusted.append(ev2)

    return adjusted


# ======================================================================
# MAIN RETRIEVAL ENTRYPOINT
# ======================================================================


def run_rag_retrieval(
    *,
    query: str,
    ctx: Any,
    retrieval_cfg: RetrievalConfig,
    hyde_query: Optional[str] = None,
) -> List[Evidence]:
    """
    Runs BM25, Dense, and optional HYDE-enhanced retrieval,
    then fuses via weighted RRF and applies QA council weighting.

    Gaps resolved:
        • G13: weighted RRF
        • G37: HYDE integration
        • G10/G29/G31: QA council evidence adjustments
    """
    max_hits = retrieval_cfg.max_hits

    # HYDE query overrides normal query text
    effective_query = hyde_query if hyde_query else query

    # Emit telemetry for the retrieval attempt
    method = "hyde_query" if hyde_query else "query"
    _emit_attempt(ctx, method, effective_query)

    # BM25
    bm25_hits = _bm25_search(
        effective_query,
        retrieval_cfg.bm25_k1,
        retrieval_cfg.bm25_b,
        max_hits,
    )
    _emit_result(ctx, "bm25", len(bm25_hits), max_hits)

    # Dense
    dense_hits = _dense_search(effective_query, max_hits)
    _emit_result(ctx, "dense", len(dense_hits), max_hits)

    groups: List[List[Evidence]] = [bm25_hits, dense_hits]

    # Weighted RRF fusion
    weights = _trim_weights(retrieval_cfg.rrf_weights, len(groups))
    fused = _rrf_fuse(groups, weights)

    emit_telemetry_event(
        RankingEvent(
            name="ranking.rrf_fused",
            stage="rrf",
            input_count=sum(len(g) for g in groups),
            output_count=len(fused),
            details={"weights": weights},
            workflow_id=ctx.workflow_id,
        )
    )

    # Council-aware adjustments (if present)
    council: Optional[CouncilVote] = ctx.slots.get("qa_council_vote") if hasattr(ctx, "slots") else None
    if council:
        adj = _apply_qa_council_weights(fused, council)
        emit_telemetry_event(
            RankingEvent(
                name="ranking.council_adjusted",
                stage="council",
                input_count=len(fused),
                output_count=len(adj),
                details={"selected_id": council.selected_id},
                workflow_id=ctx.workflow_id,
            )
        )
        fused = adj

    return fused
