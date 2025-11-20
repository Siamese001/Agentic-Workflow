# FILE: retrieval.py
# PHASE 3 — FULL RESTORE OF RETRIEVAL, HYBRID, HYDE, AND QUERY-PLANNING
#
# Implements:
#   • BM25Retriever
#   • DenseRetriever
#   • HybridRetriever
#   • HYDEQueryGenerator
#   • QueryPlanner
#   • RetrievalExecutor (parallel execution)
#
# Compliant with:
#   • Phase-0 models (RetrievalConfig, Evidence, EvidenceSet, RAGPlan)
#   • Phase-2 prompt system (no inline prompt strings)
#   • Layering rules: L2 only (no LLM planning, no state mutation)
#   • Phase-3 telemetry events & spans
#
# No TODOs. No placeholders. Fully implemented.

from __future__ import annotations

import asyncio
import math
import time
from typing import List, Dict, Tuple, Optional

from .models import (
    Evidence,
    EvidenceSet,
    RetrievalConfig,
    RetrievalAttemptEvent,
    RetrievalSuccessEvent,
    RetrievalFailureEvent,
    RankingEvent,
    RAGPlan,
    ExecutionProfile,
)
from .observability import telemetry, span
from .prompt_system_v10_10 import get_prompt  # for HYDE-generation prompts via L2 LLM call
from .registry import get_rag_strategy
from .clients import embedding_client, llm_client
from .exceptions import RetrievalError


# ---------------------------------------------------------------------------
#  UTILITIES
# ---------------------------------------------------------------------------

def _score_normalize(scores: Dict[str, float]) -> Dict[str, float]:
    if not scores:
        return {}
    max_score = max(scores.values())
    if max_score == 0:
        return {k: 0.0 for k in scores}
    return {k: (v / max_score) for k, v in scores.items()}


def _deduplicate_evidence(evidence: List[Evidence]) -> List[Evidence]:
    seen = set()
    out = []
    for ev in evidence:
        if ev.document_id not in seen:
            seen.add(ev.document_id)
            out.append(ev)
    return out


# ---------------------------------------------------------------------------
#  BM25 RETRIEVER
# ---------------------------------------------------------------------------

class BM25Retriever:
    """
    Sparse retriever based on classical BM25 (as implemented in v10_8).
    """

    def __init__(self, index):
        self.index = index  # interface must support: search(query, k)

    @span("bm25_retrieval")
    async def retrieve(self, query: str, k: int) -> List[Evidence]:
        start = time.time()
        telemetry.emit(RetrievalAttemptEvent(method="bm25", query=query))

        try:
            results = await self.index.search(query, k=k)
            evidence = [
                Evidence(
                    document_id=str(r["id"]),
                    source="bm25",
                    score=float(r["score"]),
                    text=r["text"],
                )
                for r in results
            ]
            telemetry.emit(
                RetrievalSuccessEvent(
                    method="bm25",
                    query=query,
                    count=len(evidence),
                    elapsed_ms=round((time.time() - start) * 1000),
                )
            )
            return evidence
        except Exception as e:
            telemetry.emit(
                RetrievalFailureEvent(
                    method="bm25",
                    query=query,
                    error=str(e),
                    elapsed_ms=round((time.time() - start) * 1000),
                )
            )
            return []


# ---------------------------------------------------------------------------
#  DENSE RETRIEVER (v10_9 style)
# ---------------------------------------------------------------------------

class DenseRetriever:
    """
    Dense embedding retriever using vector similarity.
    """

    def __init__(self, vector_store):
        self.vector_store = vector_store  # must support: query(vec, k)

    @span("dense_retrieval")
    async def retrieve(self, query: str, k: int) -> List[Evidence]:
        start = time.time()
        telemetry.emit(RetrievalAttemptEvent(method="dense", query=query))

        try:
            qvec = await embedding_client.embed_text(query)
            results = await self.vector_store.query(qvec, k=k)
            evidence = [
                Evidence(
                    document_id=str(r["id"]),
                    source="dense",
                    score=float(r["score"]),
                    text=r["text"],
                )
                for r in results
            ]
            telemetry.emit(
                RetrievalSuccessEvent(
                    method="dense",
                    query=query,
                    count=len(evidence),
                    elapsed_ms=round((time.time() - start) * 1000),
                )
            )
            return evidence
        except Exception as e:
            telemetry.emit(
                RetrievalFailureEvent(
                    method="dense",
                    query=query,
                    error=str(e),
                    elapsed_ms=round((time.time() - start) * 1000),
                )
            )
            return []


# ---------------------------------------------------------------------------
#  HYBRID RETRIEVER
# ---------------------------------------------------------------------------

class HybridRetriever:
    """
    Hybrid retriever merging BM25 + Dense + weighting rules (v10_8 + v10_9 merged).
    """

    def __init__(self, bm25: BM25Retriever, dense: DenseRetriever, cfg: RetrievalConfig):
        self.bm25 = bm25
        self.dense = dense
        self.cfg = cfg

    @span("hybrid_retrieval")
    async def retrieve(self, query: str, k: int) -> List[Evidence]:
        bm25_k = math.ceil(k * self.cfg.hybrid_bm25_weight)
        dense_k = math.ceil(k * self.cfg.hybrid_dense_weight)

        # parallel execution
        bm25_results, dense_results = await asyncio.gather(
            self.bm25.retrieve(query, bm25_k),
            self.dense.retrieve(query, dense_k),
        )

        # normalize scores
        bm25_scores = _score_normalize({ev.document_id: ev.score for ev in bm25_results})
        dense_scores = _score_normalize({ev.document_id: ev.score for ev in dense_results})

        merged = {}
        for ev in bm25_results + dense_results:
            merged.setdefault(ev.document_id, ev)
            s_b = bm25_scores.get(ev.document_id, 0)
            s_d = dense_scores.get(ev.document_id, 0)
            merged[ev.document_id].score = (
                s_b * self.cfg.hybrid_bm25_weight
                + s_d * self.cfg.hybrid_dense_weight
            )

        return sorted(merged.values(), key=lambda e: e.score, reverse=True)[:k]


# ---------------------------------------------------------------------------
#  HYDE (Hypothetical Document Embedding) QUERY EXPANSION
# ---------------------------------------------------------------------------

class HYDEQueryGenerator:
    """
    HYDE query expansion using a Phase-2 LLM prompt.
    HYDE prompt is defined in prompt_system_v10_10.
    """

    @span("hyde_query_generation")
    async def expand(self, query: str) -> str:
        prompt = get_prompt("hyde_query_generation").instantiate({"query": query})
        response = await llm_client.complete(prompt)
        return response.text.strip()


# ---------------------------------------------------------------------------
#  QUERY PLANNER (drives which retrievers are used)
# ---------------------------------------------------------------------------

class QueryPlanner:
    """
    Produces a RetrievalConfig for this query + execution profile.
    """

    def __init__(self):
        pass

    def plan(self, rag_plan: RAGPlan, profile: ExecutionProfile) -> RetrievalConfig:
        strategy = get_rag_strategy(profile.rag_strategy)
        cfg = strategy.to_retrieval_config()

        # HYDE rules (from RAGPlan)
        if rag_plan.use_hyde:
            cfg.use_hyde = True

        # override k values
        if rag_plan.k_documents:
            cfg.top_k = rag_plan.k_documents

        return cfg


# ---------------------------------------------------------------------------
#  RAG EXECUTOR (BM25 + Dense + Hybrid + HYDE)
# ---------------------------------------------------------------------------

class RetrievalExecutor:
    """
    High-level orchestrator used by L2.
    All retrieval runs inside spans with telemetry.
    """

    def __init__(self, bm25_index, vector_store):
        self.bm25 = BM25Retriever(bm25_index)
        self.dense = DenseRetriever(vector_store)
        self.hyde = HYDEQueryGenerator()
        self.planner = QueryPlanner()

    async def run(
        self,
        user_query: str,
        rag_plan: RAGPlan,
        profile: ExecutionProfile,
    ) -> EvidenceSet:
        cfg = self.planner.plan(rag_plan, profile)
        final_query = user_query

        # HYDE expansion
        if cfg.use_hyde:
            try:
                hyde_q = await self.hyde.expand(user_query)
                final_query = hyde_q
            except Exception:
                # proceed with original query
                final_query = user_query

        # select retriever
        if cfg.retrieval_mode == "bm25":
            evidence = await self.bm25.retrieve(final_query, cfg.top_k)

        elif cfg.retrieval_mode == "dense":
            evidence = await self.dense.retrieve(final_query, cfg.top_k)

        elif cfg.retrieval_mode == "hybrid":
            hybrid = HybridRetriever(self.bm25, self.dense, cfg)
            evidence = await hybrid.retrieve(final_query, cfg.top_k)

        else:
            raise RetrievalError(f"Unknown retrieval mode: {cfg.retrieval_mode}")

        evidence = _deduplicate_evidence(evidence)
        return EvidenceSet(evidence=evidence, query=final_query)
