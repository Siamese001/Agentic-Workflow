"""
Meta retrieval system for résumé evidence gathering.

Coordinates multiple retrieval strategies to find relevant data for comprehensive résumé improvement.
"""

from __future__ import annotations

from typing import List, Optional

from core.models.models import (
    Evidence,
    RetrievalConfig,
    CouncilVote,
    RAGResult,
    RetrievalAttemptEvent,
    RetrievalSuccessEvent,
    RetrievalFailureEvent,
)
from observability import (
    start_span,
    end_span,
    emit_retrieval_attempt,
    emit_retrieval_success,
    emit_retrieval_failure,
)

from meta.retrieval.hybrid_ranker import fuse_and_rank


def _run_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
    """
    Performs keyword-based search for résumé evidence.

    Finds exact matches to ensure comprehensive coverage of relevant résumé content.
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
    Performs semantic search for résumé improvement.
    
    Finds conceptually similar content to ensure comprehensive résumé alignment with job requirements.
    """

    from retrievers.dense import dense_search

    return dense_search(query=query, max_hits=max_hits)


def _run_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
    """
    Executes hybrid vector search for résumé evidence.
    
    Combines multiple search approaches for comprehensive résumé improvement data.
    """

    try:  # pragma: no cover - optional Chroma wiring
        from infrastructure.storage.vector_store_chroma import (
            ChromaConfig as _ChromaConfig,
            init_chroma_client as _init_chroma_client,
            chroma_hybrid_search as _chroma_hybrid_search,
        )
    except Exception:  # pragma: no cover - Chroma is optional
        return []

    if not getattr(cfg, "chroma", None) or not cfg.chroma.enabled:
        return []

    chroma_cfg = cfg.chroma
    if not chroma_cfg.collection_name:
        return []

    client, collection = _init_chroma_client(
        _ChromaConfig(
            collection_name=chroma_cfg.collection_name,
            persist_directory=chroma_cfg.persist_directory,
            require_collection=True,
        )
    )

    raw = _chroma_hybrid_search(
        collection,
        query_texts=[query],
        n_results=max_hits,
    )

    docs = (raw.get("documents") or [[]])[0]
    scores = (raw.get("distances") or [[]])[0]

    evidence: List[Evidence] = []
    for text, score in zip(docs, scores):
        evidence.append(
            Evidence(
                text=str(text),
                score=float(score),
                source="chroma",
                metadata={},
            )
        )

    return evidence[:max_hits]


def orchestrate_retrieval(
    *,
    query: str,
    ctx,
    cfg: RetrievalConfig,
    hyde_query: Optional[str] = None,
    council_vote: Optional[CouncilVote] = None,
) -> RAGResult:
    """
    Coordinates comprehensive retrieval for résumé improvement.
    
    Executes multiple search strategies to gather relevant evidence for résumé enhancement.
    """

    workflow_id = ctx.workflow_id
    max_hits = cfg.max_hits

    # Choose query (if HYDE passed from L2)
    effective_query = hyde_query if hyde_query else query
    emit_retrieval_attempt(
        RetrievalAttemptEvent(
            name="retrieval_attempt",
            method=cfg.strategy,
            query=effective_query,
            workflow_id=workflow_id,
            attributes={
                "is_hyde": hyde_query is not None,
                "max_hits": max_hits,
            },
        )
    )

    span = start_span(
        "retrieval.run",
        {
            "workflow_id": workflow_id,
            "query.is_hyde": hyde_query is not None,
            "retrieval.strategy": cfg.strategy,
            "max_hits": max_hits,
        },
    )

    # BM25 — lexical retriever (isolated error domain)
    bm25_hits: List[Evidence] = []
    try:
        bm25_hits = _run_bm25(effective_query, cfg, max_hits)
        emit_retrieval_success(
            RetrievalSuccessEvent(
                name="retrieval_success",
                method="bm25",
                hit_count=len(bm25_hits),
                max_hits=max_hits,
                workflow_id=workflow_id,
            )
        )
    except Exception as e:  # pragma: no cover - defensive
        emit_retrieval_failure(
            RetrievalFailureEvent(
                name="retrieval_failure",
                method="bm25",
                reason=str(e),
                workflow_id=workflow_id,
            )
        )

    # Dense — semantic retriever (isolated error domain)
    dense_hits: List[Evidence] = []
    try:
        dense_hits = _run_dense(effective_query, cfg, max_hits)
        emit_retrieval_success(
            RetrievalSuccessEvent(
                name="retrieval_success",
                method="dense",
                hit_count=len(dense_hits),
                max_hits=max_hits,
                workflow_id=workflow_id,
            )
        )
    except Exception as e:  # pragma: no cover - defensive
        emit_retrieval_failure(
            RetrievalFailureEvent(
                name="retrieval_failure",
                method="dense",
                reason=str(e),
                workflow_id=workflow_id,
            )
        )

    # Optional Chroma retrieval — currently merged into dense hits
    if getattr(cfg, "chroma", None) and cfg.chroma.enabled:
        try:
            chroma_hits = _run_chroma(effective_query, cfg, max_hits)
            if chroma_hits:
                dense_hits = list(dense_hits or []) + list(chroma_hits)
                emit_retrieval_success(
                    RetrievalSuccessEvent(
                        name="retrieval_success",
                        method="chroma",
                        hit_count=len(chroma_hits),
                        max_hits=max_hits,
                        workflow_id=workflow_id,
                    )
                )
        except Exception as e:  # pragma: no cover - Chroma is optional
            emit_retrieval_failure(
                RetrievalFailureEvent(
                    name="retrieval_failure",
                    method="chroma",
                    reason=str(e),
                    workflow_id=workflow_id,
                )
            )

    # Hybrid fusion + evidence ranking (delegated to META hybrid_ranker)
    rag_result = fuse_and_rank(
        lex_results=bm25_hits,
        dense_results=dense_hits,
        cfg=cfg,
        council_vote=council_vote,
        used_hyde=hyde_query is not None,
    )

    end_span(span)
    return RAGResult(evidence=list(rag_result.evidence or []), used_hyde=rag_result.used_hyde)


def run_rag_retrieval(
    *,
    query: str,
    ctx,
    cfg: RetrievalConfig,
    hyde_query: Optional[str] = None,
    council_vote: Optional[CouncilVote] = None,
) -> RAGResult:
    """
    Provides backward-compatible retrieval for résumé evidence.
    
    Maintains existing interface while delivering comprehensive résumé improvement data.
    """

    return orchestrate_retrieval(
        query=query,
        ctx=ctx,
        cfg=cfg,
        hyde_query=hyde_query,
        council_vote=council_vote,
    )



