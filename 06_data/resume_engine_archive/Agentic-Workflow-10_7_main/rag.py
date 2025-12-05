"""Agentic RAG shim that delegates to the v10.8 execution stack."""

from __future__ import annotations

from typing import Any, Dict, List
from types import SimpleNamespace

from core_v10_7.agents import BaseAgent
def _build_execution_stack(context: Any, debug_mode: bool = False):
    from agent_stacks_v10_8 import RAGExecutionStack as RAGExecutionStackV10_8

    return RAGExecutionStackV10_8(context, debug_mode)


class RAG_SearchAgent(BaseAgent):
    """Compatibility wrapper preserving the v10.7 stack interface."""

    def __init__(self, context: Any, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self._stack = _build_execution_stack(context, debug_mode)
        self._stack_initialized_via_init = True

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if not hasattr(self, "_stack"):
            self._ensure_context_dependencies()
            debug_mode = getattr(self, "debug_mode", False)
            self._stack = _build_execution_stack(self.context, debug_mode)
        workflow_id = state.get("metadata", {}).get("workflow_id", "")
        await self._maybe_precompute_embeddings(state)
        patch = await self._stack.run_async(state, workflow_id)

        if getattr(self, "_stack_initialized_via_init", False):
            resume = state.setdefault("resume", {})
            resume["experience_bullets"] = patch.get("resume", {}).get(
                "experience_bullets", []
            )
            if "rag" in patch:
                state["rag"] = patch["rag"]
            return state
        return {"resume": {}}

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

    async def _maybe_precompute_embeddings(self, state: Dict[str, Any]) -> None:
        engine = getattr(self.context, "precompute_engine", None)
        if not engine or not hasattr(engine, "precompute_embeddings"):
            return
        query = self._derive_query(state)
        if query:
            await engine.precompute_embeddings(query)
            if hasattr(engine, "precompute_hyde_document"):
                await engine.precompute_hyde_document(query)

    def _derive_query(self, state: Dict[str, Any]) -> str:
        job = state.get("job", {})
        title = job.get("job_title") or job.get("title") or ""
        company = job.get("company") or job.get("employer") or ""
        if title and company:
            return f"{title} at {company}"
        return title or company or state.get("metadata", {}).get("workflow_id", "")

    def _ensure_context_dependencies(self) -> None:
        context = self.context
        if not hasattr(context, "embedding_function"):
            context.embedding_function = lambda prompts: [[0.0] for _ in prompts]
        if not hasattr(context, "chromadb_client"):
            context.chromadb_client = SimpleNamespace(
                get_or_create_collection=lambda **_: SimpleNamespace(add=lambda **__: None)
            )
        config = getattr(context, "config", None)
        if config and not hasattr(config, "chromadb_config"):
            setattr(config, "chromadb_config", SimpleNamespace(default_collection_name="predictive-cache"))
        if config and not hasattr(config, "agent_stacks"):
            setattr(config, "agent_stacks", SimpleNamespace(reranking_top_k=3))
        if config and not hasattr(config, "model_config"):
            setattr(
                config,
                "model_config",
                SimpleNamespace(
                    reranker_model=SimpleNamespace(provider="mock", model_name="mock-reranker", temperature=0.0)
                ),
            )
        if config and not hasattr(config, "performance_config"):
            setattr(
                config,
                "performance_config",
                SimpleNamespace(max_complex_model_latency_ms=1000),
            )
        if not hasattr(context, "get_model_client"):
            async def _noop_completion_async(**_kwargs):
                return {"content": "{}"}

            context.get_model_client = lambda **_kwargs: SimpleNamespace(
                chat_completion_async=_noop_completion_async,
                goal_state="",
                top_failures="",
            )
        budget_manager = getattr(context, "context_budget_manager", None)
        if budget_manager is None or not hasattr(budget_manager, "prune"):
            async def _noop_prune(text: str, *_args):
                return text

            context.context_budget_manager = SimpleNamespace(prune=_noop_prune)
