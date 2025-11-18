# FILE: v10_9_clean/l2/rag_execution.py
"""
L2 — RAG Execution (v10_9)

Executes retrieval queries using:
    • shared.retrieval (normalization, fusion, dedupe)
    • shared.ranking (bm25, dense, hybrid)
    • model backends via l2 clients
    • optional vector store / cache integrations (plugged in via infra)

No planning logic here — pure execution.

This file is a 10_9 evolution of the 10_7/10_8 rag_execution stack.
"""

from __future__ import annotations

from typing import Any, Dict, List

from shared.models import ExecutionResult
from shared.models import PlanObject
from shared.exceptions import ToolExecutionError

from shared.retrieval import (
    normalize_documents,
    dedupe_results,
    rerank_results,
    fuse_results,
    truncate_by_budget,
    apply_ranker,
)
from shared.models import BudgetConfig

from shared.ranking import bm25_rank, dense_rank, hybrid_rank   # optional external ranking
from l2.clients import build_client


# ---------------------------------------------------------------------------
# Core executor
# ---------------------------------------------------------------------------

async def execute_rag(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    """
    Execute a retrieval step:
        • fan out queries
        • collect preliminary results (stubbed backend for now)
        • normalize, dedupe
        • apply ranking
        • fuse multi-query sources
        • truncate based on budget
    """

    try:
        fragment = plan.retrieval or {}
        queries: List[str] = fragment.get("queries") or []
        filters: Dict[str, Any] = fragment.get("filters") or {}
        ranking_cfg: Dict[str, Any] = fragment.get("ranking") or {}

        # Build an L2 client (future: use correct model for retrieval)
        client = build_client(plan.handoff.get("model") or "gpt-4.1")

        # Temporary placeholder: real vector store retrieval will be plugged here
        raw_results: List[Dict[str, Any]] = []
        for q in queries:
            # For now return deterministic stub evidence
            raw_results.append(
                {
                    "query": q,
                    "evidence": f"stub evidence for query: {q}",
                    "rank": 0,
                }
            )

        # Pipeline:
        docs = normalize_documents(raw_results)
        docs = dedupe_results(docs)

        strategy = ranking_cfg.get("strategy", "hybrid")

        if strategy == "bm25":
            docs = bm25_rank(docs)
        elif strategy == "dense":
            docs = dense_rank(docs)
        elif strategy == "hybrid":
            docs = hybrid_rank(docs)
        else:
            docs = apply_ranker(docs, strategy=strategy)

        docs = rerank_results(docs, strategy)
        fused = fuse_results([docs])

        # Truncate via budget
        bg = BudgetConfig()
        truncated = truncate_by_budget(fused, bg)

        payload = {
            "queries": queries,
            "filters": filters,
            "ranking": ranking_cfg,
            "documents": truncated,
        }

        return ExecutionResult(
            status=ExecutionResult.__fields__["status"].type_.SUCCESS,
            payload=payload,
            model=client.model,
            usage={},
        )

    except Exception as exc:
        raise ToolExecutionError(f"RAG execution failed: {exc}") from exc
