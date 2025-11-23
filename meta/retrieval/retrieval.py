from __future__ import annotations

from typing import List, Optional

from models import Evidence, RetrievalConfig, CouncilVote, RAGResult, RetrievalAttemptEvent, RetrievalSuccessEvent, RetrievalFailureEvent
from observability import start_span, end_span, emit_retrieval_attempt, emit_retrieval_success, emit_retrieval_failure

from meta.retrieval.hybrid_ranker import fuse_and_rank
from meta.retrieval.retrievers.bm25 import bm25_search as _bm25_search
from meta.retrieval.retrievers.dense import dense_search as _dense_search
from meta.retrieval.vector_store_chroma import chroma_hybrid_search as _chroma_hybrid_search


def run_bm25_retrieval(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
    corpus = []  # Placeholder corpus; real wiring is handled by existing retrievers.
    scored = _bm25_search(query=query, corpus=corpus, cfg=None)  # type: ignore[arg-type]
    return [
        Evidence(text=str(item.get("text", "")), score=float(item.get("score", 0.0)), source="bm25", metadata={})
        for item in scored[:max_hits]
    ]


def run_dense_retrieval(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
    return _dense_search(query=query, max_hits=max_hits)


def run_hyde_expansion(base_query: str, hyde_query: Optional[str]) -> str:
    return hyde_query if hyde_query else base_query


def normalize_documents(evidence: List[Evidence]) -> List[Evidence]:
    return evidence


def orchestrate_retrieval(
    *,
    query: str,
    ctx,
    cfg: RetrievalConfig,
    hyde_query: Optional[str] = None,
    council_vote: Optional[CouncilVote] = None,
) -> RAGResult:
    workflow_id = ctx.workflow_id
    max_hits = cfg.max_hits

    effective_query = run_hyde_expansion(query, hyde_query)
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

    bm25_hits: List[Evidence] = []
    try:
        bm25_hits = run_bm25_retrieval(effective_query, cfg, max_hits)
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

    dense_hits: List[Evidence] = []
    try:
        dense_hits = run_dense_retrieval(effective_query, cfg, max_hits)
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

    # Optional Chroma retrieval via META adapter
    if getattr(cfg, "chroma", None) and cfg.chroma.enabled:
        try:
            chroma_hits = _chroma_hybrid_search(effective_query, cfg, max_hits)
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
        except Exception as e:  # pragma: no cover - defensive
            emit_retrieval_failure(
                RetrievalFailureEvent(
                    name="retrieval_failure",
                    method="chroma",
                    reason=str(e),
                    workflow_id=workflow_id,
                )
            )

    rag_result = fuse_and_rank(
        lex_results=bm25_hits,
        dense_results=dense_hits,
        cfg=cfg,
        council_vote=council_vote,
        used_hyde=hyde_query is not None,
    )

    end_span(span)
    return RAGResult(evidence=list(rag_result.evidence or []), used_hyde=rag_result.used_hyde)
