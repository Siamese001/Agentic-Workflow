# FILE: retrieval.py
"""
Retrieval & Query Planning (v10_10 · Phase 3 — FINAL)
=====================================================

Implements:
    • BM25 retrieval
    • Dense retrieval
    • Hybrid mode (BM25 + Dense)
    • HYDE query support (real hook; L2 supplies HYDE query)
    • Retriever-level failure isolation
    • Weighted RRF fusion (Phase-3 requirement)
    • QA-council evidence weighting (Phase-3 requirement)
    • Full telemetry spans / failure events

Layer: META (no LLM calls; L2 generates HYDE query)
"""

from __future__ import annotations
from typing import List, Optional

from models import (
    Evidence,
    RetrievalConfig,
    CouncilVote,
    RetrievalAttemptEvent,
    RetrievalSuccessEvent,
    RetrievalFailureEvent,
)
from observability import (
    start_span,
    end_span,
    emit_telemetry_event,
    emit_retrieval_attempt,
    emit_retrieval_success,
    emit_retrieval_failure,
)

import ranking as _ranking


# ======================================================================
# INTERNAL RETRIEVERS — REAL IMPLEMENTATIONS
# ======================================================================

def _run_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
    """
    Real BM25 retriever — already implemented in your codebase.
    Deterministic, uses integrated scoring functions.
    """
    from retrievers.bm25 import bm25_search
    return bm25_search(
        query=query,
        k1=cfg.bm25_k1,
        b=cfg.bm25_b,
        max_hits=max_hits,
    )


def _run_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
    """
    Real dense retriever — uses your actual vector index.
    Deterministic due to seeded search paths.
    """
    from retrievers.dense import dense_search
    return dense_search(query=query, max_hits=max_hits)


# ======================================================================
# QA-COUNCIL EVIDENCE WEIGHTING
# ======================================================================

def _apply_council_weights(
    fused: List[Evidence],
    council: Optional[CouncilVote],
) -> List[Evidence]:
    """
    Apply post-fusion weighting according to QA-council decision.

    Selected-ID receives a ~12% boost.
    Others receive slight demotion.
    """
    if council is None or not council.selected_id:
        return fused

    sel = council.selected_id
    BOOST = 1.12
    DEMOTE = 0.94

    adjusted = []
    for ev in fused:
        e = ev.copy()
        if sel in ev.text:
            e.score *= BOOST
        else:
            e.score *= DEMOTE
        adjusted.append(e)

    return adjusted


# ======================================================================
# MAIN ENTRYPOINT — HYBRID RETRIEVAL + WEIGHTED RRF
# ======================================================================

def run_rag_retrieval(
    *,
    query: str,
    ctx,
    retrieval_cfg: RetrievalConfig,
    hyde_query: Optional[str] = None,
    council_vote: Optional[CouncilVote] = None,
) -> List[Evidence]:
    """
    Primary production retrieval entrypoint.

    Steps:
        1. Select effective query (HYDE if provided)
        2. Emit attempt telemetry
        3. Run BM25 (isolated)
        4. Run Dense (isolated)
        5. Fuse via weighted RRF
        6. Apply QA-council evidence weighting
        7. Emit success/failure events per retriever

    Deterministic unless HYDE is enabled (HYDE generated in L2).
    """

    workflow_id = ctx.workflow_id
    max_hits = retrieval_cfg.max_hits

    # -----------------------------------------------------
    # Choose query (if HYDE passed from L2)
    # -----------------------------------------------------
    effective_query = hyde_query if hyde_query else query
    emit_retrieval_attempt(effective_query, workflow_id)

    span = start_span(
        "retrieval.run",
        workflow_id=workflow_id,
        attrs={
            "query.is_hyde": hyde_query is not None,
            "retrieval.strategy": retrieval_cfg.strategy,
            "max_hits": max_hits,
        },
    )

    groups = []

    # -----------------------------------------------------
    # BM25 — isolated error domain
    # -----------------------------------------------------
    try:
        bm25_hits = _run_bm25(effective_query, retrieval_cfg, max_hits)
        groups.append(bm25_hits)
        emit_retrieval_success("bm25", len(bm25_hits), workflow_id)
    except Exception as e:
        emit_retrieval_failure("bm25", str(e), workflow_id)

    # -----------------------------------------------------
    # Dense — isolated error domain
    # -----------------------------------------------------
    try:
        dense_hits = _run_dense(effective_query, retrieval_cfg, max_hits)
        groups.append(dense_hits)
        emit_retrieval_success("dense", len(dense_hits), workflow_id)
    except Exception as e:
        emit_retrieval_failure("dense", str(e), workflow_id)

    # -----------------------------------------------------
    # Weighted RRF fusion
    # -----------------------------------------------------
    fused = _ranking.fuse_ranked_groups_rrf(
        groups=groups,
        rrf_weights=retrieval_cfg.rrf_weights,
        workflow_id=workflow_id,
    )

    # -----------------------------------------------------
    # Council-aware post weighting
    # -----------------------------------------------------
    fused = _apply_council_weights(fused, council_vote)

    end_span(span)
    return fused
