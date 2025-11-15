"""Pure action implementation of the v10.8 RAG execution stack."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from agent_tools_v10_7 import BM25SearchTool, ChromaDBSearchTool, HyDETool
from core_v10_7 import BaseAgent, PydanticSchemaError, RAGPlan, _format_prompt_with_defaults


class RAGExecutionStack(BaseAgent):
    """Runs deterministic hybrid retrieval using a pre-computed RAGPlan."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self.hyde_tool = HyDETool(context, debug_mode)
        self.chroma_tool = ChromaDBSearchTool(context, debug_mode)
        self.bm25_tool = BM25SearchTool(context, debug_mode)
        self.chroma_client = context.chromadb_client
        self.embedding_function = context.embedding_function
        self.collection_name = context.config.chromadb_config.default_collection_name
        self.safety_policy = getattr(context, "safety_policy", None)
        self.policy_stack = getattr(context, "policy_stack", None)
        self.constitutional_engine = getattr(context, "constitutional_engine", None)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        plan = self._plan_from_state(state)
        experiences = self._extract_experience(state)
        if not self._tools_ready():
            metadata = {
                "goal": plan.goal,
                "context_inputs": plan.context_inputs,
                "prioritization": plan.prioritization,
                "risk_checks": plan.risk_checks,
                "hyde_runs": [],
                "candidate_count": 0,
                "top_candidate": {},
                "scores": [],
            }
            return {
                "resume": {"experience_bullets": []},
                "rag": {"plan": plan.model_dump(), "metadata": metadata},
            }
        await self._ingest_resume_to_chroma_async(experiences, workflow_id)
        corpus_text, corpus_metadata = self._build_bm25_corpus(experiences)

        hyde_runs: List[Dict[str, Any]] = []
        candidate_batches: List[List[Dict[str, Any]]] = []
        queries = plan.retrieval_queries or [plan.goal]

        for query in queries:
            hyde_output = await self._run_hyde(query, workflow_id)
            hyde_runs.append({"query": query, **hyde_output})
            chroma_results = await self._run_chroma_search(
                hyde_output["search_query"], workflow_id
            )
            bm25_results = await self._run_bm25_search(
                hyde_output["search_query"], corpus_text, corpus_metadata, workflow_id
            )
            candidate_batches.append(
                self._annotate_candidates(query, chroma_results, bm25_results)
            )

        merged_candidates = self._merge_candidates(candidate_batches)
        ranked, rerank_meta = await self._rerank_candidates(plan, merged_candidates, state)
        metadata = self._build_metadata(plan, hyde_runs, merged_candidates, rerank_meta)
        patch = {
            "resume": {"experience_bullets": ranked},
            "rag": {"plan": plan.model_dump(), "metadata": metadata},
        }
        safety_report = state.get("safety_report") or {}
        policy_decision = state.get("policy_decision") or {}
        constitutional_review = state.get("constitutional_review") or {}
        if not hasattr(safety_report, "dict"):
            safety_report = type("_Wrapper", (), {"dict": lambda self: dict(safety_report or {})})()
        if not hasattr(policy_decision, "dict"):
            policy_decision = type("_Wrapper", (), {"dict": lambda self: dict(policy_decision or {})})()
        if not hasattr(constitutional_review, "dict"):
            constitutional_review = type(
                "_Wrapper", (), {"dict": lambda self: dict(constitutional_review or {})}
            )()
        patch["safety_report"] = safety_report.dict()
        patch["policy_decision"] = policy_decision.dict()
        patch["constitutional_review"] = constitutional_review.dict()
        return patch

    async def run_from_state_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compatibility helper that mirrors the previous L3 node behavior."""

        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        return await self.run_async(state, workflow_id)

    def _plan_from_state(self, state: Dict[str, Any]) -> RAGPlan:
        plan_payload = state.get("rag", {}).get("plan")
        if plan_payload is None:
            return self._fallback_plan(state)
        if isinstance(plan_payload, RAGPlan):
            return plan_payload
        return RAGPlan.model_validate(plan_payload)

    def _extract_experience(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        resume = state.get("resume", {})
        master_resume = resume.get("master_resume") or {}
        experience = master_resume.get("professional_experience")
        return list(experience or []) if isinstance(experience, Iterable) else []

    async def _ingest_resume_to_chroma_async(
        self, resume_experience: Sequence[Dict[str, Any]], workflow_id: str
    ) -> None:
        if not resume_experience:
            return
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )
        except Exception:
            return

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []
        embeddings: List[List[float]] = []
        for exp_index, exp in enumerate(resume_experience):
            bullets = exp.get("bullet_pool") or []
            if not bullets:
                bullets = [exp.get("impact_summary", "")]
            exp_payload = json.dumps(exp, sort_keys=True, default=str)
            for bullet_index, bullet in enumerate(bullets):
                if not bullet:
                    continue
                documents.append(bullet)
                metadatas.append(
                    {
                        "workflow_id": workflow_id,
                        "company": exp.get("company", ""),
                        "title": exp.get("title", ""),
                        "experience_object": exp_payload,
                    }
                )
                ids.append(f"{workflow_id}_{exp_index}_{bullet_index}")
                embeddings.append(self.embedding_function([bullet])[0])

        if not documents:
            return

        try:
            await asyncio.to_thread(
                collection.add,
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings,
            )
        except Exception:
            return

    def _build_bm25_corpus(
        self, resume_experience: Sequence[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        corpus_text: List[str] = []
        corpus_metadata: List[Dict[str, Any]] = []
        for exp in resume_experience:
            bullets = " ".join(exp.get("bullet_pool", []))
            document = " ".join(
                part
                for part in [exp.get("title"), exp.get("company"), bullets]
                if part
            )
            if not document:
                continue
            corpus_text.append(document)
            corpus_metadata.append(exp)
        return corpus_text, corpus_metadata

    async def _run_hyde(self, query: str, workflow_id: str) -> Dict[str, Any]:
        tool_input = {"query": query, "job_description": query, "style_guide": ""}
        result = await self.hyde_tool.run_async(tool_input, workflow_id)
        document = result.get("hypothetical_document") or query
        return {
            "status": result.get("status", "unknown"),
            "search_query": document,
        }

    async def _run_chroma_search(
        self, query: str, workflow_id: str
    ) -> List[Dict[str, Any]]:
        try:
            output = await self.chroma_tool.run_async({"query": query}, workflow_id)
        except Exception:
            return []
        return output.get("search_results") or []

    async def _run_bm25_search(
        self,
        query: str,
        corpus_text: Sequence[str],
        corpus_metadata: Sequence[Dict[str, Any]],
        workflow_id: str,
    ) -> List[Dict[str, Any]]:
        if not corpus_text:
            return []
        payload = {
            "query": query,
            "corpus_text": list(corpus_text),
            "corpus_metadata": list(corpus_metadata),
        }
        try:
            output = await self.bm25_tool.run_async(payload, workflow_id)
        except Exception:
            return []
        return output.get("search_results") or []

    def _annotate_candidates(
        self,
        query: str,
        chroma_results: Sequence[Dict[str, Any]],
        bm25_results: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        annotated: List[Dict[str, Any]] = []
        for source, results in ("chroma", chroma_results), ("bm25", bm25_results):
            for entry in results:
                record = json.loads(json.dumps(entry, default=str))
                record.setdefault("query", query)
                record.setdefault("source", source)
                annotated.append(record)
        return annotated

    def _merge_candidates(
        self, batches: Sequence[Sequence[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        merged: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for batch in batches:
            for record in batch:
                key = json.dumps(record, sort_keys=True, default=str)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(record)
        return merged

    async def _rerank_candidates(
        self, plan: RAGPlan, candidates: Sequence[Dict[str, Any]], state: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if not candidates:
            return [], {"scores": []}
        rerank_client = self.get_model_client("reranker_model")
        prompt_template = self.prompt_manager.get_template("rerank_results")
        strategy = state.get("strategy", {}).get("strategy_plan", {})
        strategy_payload = (
            strategy.model_dump() if hasattr(strategy, "model_dump") else strategy
        )
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {
                "query": plan.goal,
                "strategy": json.dumps(strategy_payload, default=str),
                "candidates": json.dumps(candidates, default=str),
            },
            self.budget_manager,
            rerank_client.goal_state,
            rerank_client.top_failures,
        )
        try:
            response = await rerank_client.chat_completion_async(
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.model_config.reranker_model.temperature,
                response_format="json_object",
            )
            content, error = self.validator.validate(response["content"], dict)
            if error:
                raise PydanticSchemaError(error)
            ranked = content.get("ranked") or []
        except Exception:
            ranked = list(candidates)
        top_k = self.config.agent_stacks.reranking_top_k
        ordered = list(ranked[:top_k]) if ranked else list(candidates[:top_k])
        scores = [float(len(ordered) - idx) for idx, _ in enumerate(ordered)]
        return ordered, {"scores": scores}

    def _build_metadata(
        self,
        plan: RAGPlan,
        hyde_runs: Sequence[Dict[str, Any]],
        candidates: Sequence[Dict[str, Any]],
        rerank_meta: Dict[str, Any],
    ) -> Dict[str, Any]:
        top_entry = candidates[0] if candidates else {}
        return {
            "goal": plan.goal,
            "context_inputs": plan.context_inputs,
            "prioritization": plan.prioritization,
            "risk_checks": plan.risk_checks,
            "hyde_runs": list(hyde_runs),
            "candidate_count": len(candidates),
            "top_candidate": top_entry,
            "scores": rerank_meta.get("scores", []),
        }

    def _fallback_plan(self, state: Dict[str, Any]) -> RAGPlan:
        query = self._derive_query(state)
        goal = f"Surface evidence for {query}" if query else "Surface evidence"
        return RAGPlan(
            goal=goal,
            context_inputs=["job.title", "job.company"],
            retrieval_queries=[query] if query else [],
            prioritization=["Use resume recency"],
            risk_checks=["Tie every bullet to resume evidence"],
        )

    def _derive_query(self, state: Dict[str, Any]) -> str:
        job = state.get("job", {})
        job_title = job.get("job_title") or job.get("title") or ""
        company = job.get("company") or job.get("employer") or ""
        if job_title and company:
            return f"{job_title} at {company}"
        return job_title or company or state.get("metadata", {}).get("workflow_id", "")

    def _tools_ready(self) -> bool:
        required = ["cache_manager", "chromadb_client", "embedding_function"]
        return all(hasattr(self.context, attr) for attr in required)
