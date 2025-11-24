"""Retrieval - Meta Layer

This module provides the main retrieval entrypoint.

Layer: Meta
Responsibilities:
- Orchestrate retrieval (BM25/dense/hybrid)
- HYDE query support
- RRF fusion
- QA-council evidence weighting
- Failure isolation
- Telemetry

Non-responsibilities:
- LLM calls (L2 generates HYDE query)
- Planning
- State mutation
"""

# FILE: retrieval.py

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
