"""Agentic RAG shim that delegates to the v10.8 execution stack."""

from __future__ import annotations

from typing import Any, Dict, List

from core_v10_7.agents import BaseAgent
from agent_stacks_v10_8 import RAGExecutionStack as RAGExecutionStackV10_8


class RAG_SearchAgent(BaseAgent):
    """Compatibility wrapper preserving the v10.7 stack interface."""

    def __init__(self, context: Any, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self._stack = RAGExecutionStackV10_8(context, debug_mode)

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = state.get("metadata", {}).get("workflow_id", "")
        patch = await self._stack.run_async(state, workflow_id)

        resume = state.setdefault("resume", {})
        resume["experience_bullets"] = patch.get("resume", {}).get(
            "experience_bullets", []
        )
        if "rag" in patch:
            state["rag"] = patch["rag"]
        return state

    @staticmethod
    def _record_world_model_rag_run(
        agent: Any, workflow_id: str, query: str, ranked: List[Any]
    ) -> None:
        store = getattr(getattr(agent, "context", None), "world_model_store", None)
        if not store or not getattr(store, "enabled", lambda: False)():
            return
        store.set_json(
            f"rag_last_run:{workflow_id}",
            {"query": query, "num_results": len(ranked or [])},
        )
