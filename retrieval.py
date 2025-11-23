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

from typing import Optional

from core.models.models import RetrievalConfig, CouncilVote, RAGResult

from meta.retrieval.retrieval import orchestrate_retrieval


def run_rag_retrieval(
    *,
    query: str,
    ctx,
    retrieval_cfg: RetrievalConfig,
    hyde_query: Optional[str] = None,
    council_vote: Optional[CouncilVote] = None,
) -> RAGResult:
    """Primary production retrieval entrypoint (thin wrapper).

    All retrieval logic (BM25/dense/Chroma, RRF fusion, council weighting,
    telemetry) is implemented inside the META orchestrator in
    meta.retrieval.retrieval.orchestrate_retrieval.
    """

    return orchestrate_retrieval(
        query=query,
        ctx=ctx,
        cfg=retrieval_cfg,
        hyde_query=hyde_query,
        council_vote=council_vote,
    )
