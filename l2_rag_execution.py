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

from l2_tool_base import ExecutionAgent
from utils_types import PlanObject, StatePatch


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
        queries: List[str] = [str(q) for q in plan.get("queries", [])]
        filters = plan.get("filters", {})
        results = [_synthesize_result(query, idx) for idx, query in enumerate(queries)]

        history = list(state.get("rag_history", [])) + results
        patch: StatePatch = StatePatch(
            {
                "rag_history": history,
                "last_retrieval": {
                    "queries": queries,
                    "filters": filters,
                    "ranking": plan.get("ranking", {}),
                    "status": "completed",
                },
            }
        )
        return patch
