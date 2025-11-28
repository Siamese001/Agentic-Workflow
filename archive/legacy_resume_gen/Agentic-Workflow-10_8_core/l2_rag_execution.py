"""
L2 — RAG Execution Agent

Responsibilities:
    • Execute retrieval, ranking, and evidence extraction operations.
    • Apply RAG intents from L1 reasoning while respecting L5 safety constraints.
    • Emit structured artifacts consumable by L4 state managers.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""
from __future__ import annotations

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from l2_execution import ExecutionAgent
from retrieval import fuse_results
from retrieval import (
    normalize_documents,
    dedupe_results,
    rerank_results,
    fuse_sources,
    truncate_by_budget,
    apply_ranker,
)
from l4_memory import ContextBudget
from utils_types import BudgetConfig, PlanObject, StatePatch


def _synthesize_result(query: str, index: int) -> Dict[str, Any]:
    """Create a deterministic retrieval result for a query."""

    return {
        "query": query,
        "rank": index + 1,
        "evidence": f"Evidence synthesized for '{query}'",
    }


class RAGExecutionAgent(ExecutionAgent):
    """Deterministic retrieval executor that returns state patches only."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        retrieval = plan.get("retrieval", {})
        queries: List[str] = [str(q) for q in retrieval.get("queries", [])]
        filters = retrieval.get("filters", {})
        ranking = retrieval.get("ranking", {})
        metadata = retrieval.get("metadata", {})
        results = [_synthesize_result(query, idx) for idx, query in enumerate(queries)]

        transformed = normalize_documents(results)
        transformed = dedupe_results(transformed)
        transformed = rerank_results(transformed, ranking.get("strategy"))
        transformed = apply_ranker(transformed, metadata.get("ranker_strategy") or ranking.get("strategy"))
        transformed = fuse_results([fuse_sources(transformed)])
        budget_config = BudgetConfig()
        context_budget = ContextBudget(budget_config)

        transformed = truncate_by_budget(transformed, budget_config)
        transformed = context_budget.prune_rag_items_by_tokens(transformed)

        history = list(state.get("rag_history", [])) + transformed
        patch: StatePatch = StatePatch(
            {
                "rag_history": history,
                "last_retrieval": {
                    "queries": queries,
                    "filters": filters,
                    "ranking": ranking,
                    "metadata": metadata,
                    "status": "completed",
                },
            }
        )
        patch["tooling_injection"] = {
            "tool_feedback_enabled": DEFAULT_TOOLING_PROFILE.tool_feedback_enabled,
            "evidence_binding_enabled": DEFAULT_TOOLING_PROFILE.evidence_binding_enabled,
            "cross_tool_reconciliation": DEFAULT_TOOLING_PROFILE.cross_tool_reconciliation,
        }
        patch["retrieval_injection"] = {"hybrid_ranker_enabled": True}
        return patch
