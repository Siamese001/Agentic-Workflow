"""L2 RAG execution stack."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from rag_planning import RAGPlan


class RAGExecutionStack:
    """Hybrid retrieval stub that returns deterministic patches."""

    def _load_plan(self, state: Dict[str, Any]) -> RAGPlan:
        plan_data = state.get("rag", {}).get("plan") or {}
        if isinstance(plan_data, RAGPlan):
            return plan_data
        if isinstance(plan_data, dict):
            return RAGPlan(**plan_data)
        return RAGPlan()

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._load_plan(state)
        queries = plan.retrieval_queries or ["experience impact"]

        candidates: List[Dict[str, Any]] = []
        for idx, query in enumerate(queries):
            candidates.append({"query": query, "source": "chroma", "score": 1.0 - idx * 0.05})
            candidates.append({"query": query, "source": "bm25", "score": 0.9 - idx * 0.05})

        ranked = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
        top_k = ranked[:5]

        metadata = {
            "goal": plan.goal,
            "context_inputs": plan.context_inputs,
            "risk_checks": plan.risk_checks,
            "candidate_count": len(candidates),
            "top_candidate": top_k[0] if top_k else None,
        }

        return {
            "resume": {"experience_bullets": top_k},
            "rag": {"plan": plan.model_dump(), "metadata": metadata},
        }
