# === CONSOLIDATED FILE ===
# TIMESTAMP: 2025-11-17T16:29:33.150852Z
# TARGET: rag_stack.py
# SOURCE FILES:
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_execution.py | SHA256: 3c9bf8e25f814d82cb4a0874c25318fe74b6fb3f3a7b3bde818340af5a38975c
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_orchestration.py | SHA256: 2a9773e1f4bbae8c1140b4f5122b0a990a13f1c5bf41e2a3fa58cbea3e27ca19
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_planning.py | SHA256: 1d634517b61b37d159bb24e257ed9bfe0cbc482b9a173f1b599b1caed3f36192
# MERGE RULE: 10_8 overrides 10_7; namespace collisions suffixed with __srcN


# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_execution.py (sha256=3c9bf8e25f814d82cb4a0874c25318fe74b6fb3f3a7b3bde818340af5a38975c) ====
"""Pure action implementation of the v10.8 RAG execution stack."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from agent_tools_v10_7 import BM25SearchTool, ChromaDBSearchTool, HyDETool
from core_v10_7 import BaseAgent, PydanticSchemaError, RAGPlan, _format_prompt_with_defaults
from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack


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
        self._adapter = StateAdapterStack(context, debug_mode)

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
        memory_patch = self._adapter.patch_memory(
            agent_notes=self._append_agent_note(state, metadata),
            vector_store_ids=self._collect_vector_ids(state, candidate_batches),
        )
        patch.update(memory_patch.model_dump(exclude_none=True))
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

    def _append_agent_note(
        self, state: Dict[str, Any], metadata: Dict[str, Any]
    ) -> List[str]:
        existing = state.get("memory", {}).get("episodic", {}).get("agent_notes") or []
        note = (
            f"RAG retrieved {metadata.get('candidate_count', 0)} candidates; "
            f"top source: {metadata.get('top_candidate', {}).get('source', 'n/a')}"
        )
        return [*existing, note]

    def _collect_vector_ids(
        self, state: Dict[str, Any], batches: Sequence[Sequence[Dict[str, Any]]]
    ) -> List[str]:
        existing_ids = state.get("memory", {}).get("semantic", {}).get(
            "vector_store_ids", []
        ) or []
        collected: List[str] = list(existing_ids)
        seen = set(existing_ids)
        for batch in batches:
            for record in batch:
                for key in ("id", "doc_id", "document_id"):
                    value = record.get(key)
                    if value is None:
                        continue
                    str_value = str(value)
                    if str_value in seen:
                        continue
                    seen.add(str_value)
                    collected.append(str_value)
        return collected

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
        strategy = state.get("strategy", {}).get("strategy_plan", {})
        strategy_payload = (
            strategy.model_dump() if hasattr(strategy, "model_dump") else strategy
        )
        final_prompt = state.get("prompts", {}).get("final_prompt")
        if final_prompt:
            prompt = final_prompt
        else:
            prompt_template = self.prompt_manager.get_template("rerank_results")
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
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_execution.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_orchestration.py (sha256=2a9773e1f4bbae8c1140b4f5122b0a990a13f1c5bf41e2a3fa58cbea3e27ca19) ====
"""Layer-3 orchestration for the v10.8 RAG workflow."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import BaseAgent

from .rag_execution import RAGExecutionStack
from .rag_planning import RAGPlanningStack


class RAGOrchestratorStack(BaseAgent):
    """Coordinates RAG planning and execution without adding new heuristics."""

    def __init____src2(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self._adapter = StateAdapterStack(context, debug_mode)
        self._planning = RAGPlanningStack(context, debug_mode)
        self._execution = RAGExecutionStack(context, debug_mode)
        self.safety_policy = getattr(context, "safety_policy", None)
        self.policy_stack = getattr(context, "policy_stack", None)
        self.constitutional_engine = getattr(context, "constitutional_engine", None)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        current_state = state

        plan_patch = await self._planning.run_async(current_state, workflow_id)
        plan_payload = self._ensure_plan_metadata(plan_patch)
        current_state = self._adapter.apply_patch(current_state, plan_patch)
        self._append_a2a_message(
            current_state,
            message_type="PLAN_CREATED",
            payload={
                "workflow_id": workflow_id,
                "goal": plan_payload.get("goal", ""),
            },
        )
        self.log_feedback(
            workflow_id,
            "rag_plan",
            "signal",
            {"goal": plan_payload.get("goal"), "use_hyde": plan_payload.get("use_hyde", True)},
        )

        self._append_a2a_message(
            current_state,
            message_type="EXECUTION_STARTED",
            payload={"workflow_id": workflow_id, "query_count": len(plan_payload.get("retrieval_queries", []))},
        )
        self.log_feedback(
            workflow_id,
            "rag_execution",
            "signal",
            {"phase": "start", "queries": len(plan_payload.get("retrieval_queries", []))},
        )

        execution_patch = await self._execution.run_async(current_state, workflow_id)
        current_state = self._adapter.apply_patch(current_state, execution_patch)
        current_state = await self._maybe_retry_rag(
            current_state, workflow_id, plan_payload
        )

        bullets = current_state.get("resume", {}).get("experience_bullets", [])
        self._append_a2a_message(
            current_state,
            message_type="EXECUTION_COMPLETED",
            payload={
                "workflow_id": workflow_id,
                "bullet_count": len(bullets),
            },
        )
        self.log_feedback(
            workflow_id,
            "rag_execution",
            "success",
            {"phase": "complete", "bullets": len(bullets)},
        )

        await self._record_arbitration(current_state, workflow_id)
        safety_report = current_state.get("safety_report") or {}
        policy_decision = current_state.get("policy_decision") or {}
        constitutional_review = current_state.get("constitutional_review") or {}
        if not hasattr(safety_report, "dict"):
            safety_report = type("_Wrapper", (), {"dict": lambda self: dict(safety_report or {})})()
        if not hasattr(policy_decision, "dict"):
            policy_decision = type("_Wrapper", (), {"dict": lambda self: dict(policy_decision or {})})()
        if not hasattr(constitutional_review, "dict"):
            constitutional_review = type(
                "_Wrapper", (), {"dict": lambda self: dict(constitutional_review or {})}
            )()
        current_state["safety_report"] = safety_report.dict()
        current_state["policy_decision"] = policy_decision.dict()
        current_state["constitutional_review"] = constitutional_review.dict()
        return current_state

    def _append_a2a_message(
        self, state: Dict[str, Any], *, message_type: str, payload: Dict[str, Any]
    ) -> None:
        channel = state.setdefault("a2a", {})
        messages = channel.setdefault("messages", [])
        messages.append(
            {
                "sender": self.__class__.__name__,
                "recipient": "ALL",
                "message_type": message_type,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def _ensure_plan_metadata(self, plan_patch: Dict[str, Any]) -> Dict[str, Any]:
        plan_payload = (plan_patch.get("rag", {}) or {}).get("plan", {})
        if isinstance(plan_payload, dict) and "use_hyde" not in plan_payload:
            plan_payload["use_hyde"] = True
        return plan_payload

    async def _maybe_retry_rag(
        self,
        state: Dict[str, Any],
        workflow_id: str,
        plan_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        scm = getattr(self, "self_correction_manager", None)
        bullets = state.get("resume", {}).get("experience_bullets", [])
        should_retry = plan_payload.get("use_hyde", True) and not bullets
        if not (should_retry and scm and scm.can_retry(workflow_id, "rag")):
            return state

        report = scm.start_retry(
            workflow_id,
            "rag",
            issue="hyde_zero_results",
            action="rerun_without_hyde",
            metadata={"query_count": len(plan_payload.get("retrieval_queries", []))},
        )
        plan_payload["use_hyde"] = False
        self._append_a2a_message(
            state,
            message_type="RETRY_TRIGGERED",
            payload={"workflow_id": workflow_id, "reason": "hyde_zero_results"},
        )
        self.log_feedback(
            workflow_id,
            "rag_retry",
            "retry",
            {"reason": "hyde_zero_results"},
        )

        retry_patch = await self._execution.run_async(state, workflow_id)
        state = self._adapter.apply_patch(state, retry_patch)
        bullets_after = state.get("resume", {}).get("experience_bullets", [])
        resolved = bool(bullets_after)
        scm.finalize_retry(report, resolved, {"bullet_count": len(bullets_after)})
        self.log_feedback(
            workflow_id,
            "rag_retry",
            "success" if resolved else "failure",
            {"resolved": resolved, "bullet_count": len(bullets_after)},
        )
        return state

    async def _record_arbitration(self, state: Dict[str, Any], workflow_id: str) -> None:
        engine = getattr(self.context, "arbitration_engine", None)
        if engine is None:
            return
        report = await engine.run_check("prompt_rag_join", state)
        bucket = state.setdefault("arbitration", {})
        bucket["prompt_rag_join"] = report.model_dump()
        self.log_feedback(
            workflow_id,
            "rag_arbitration",
            "signal",
            {
                "decision": report.decision,
                "confidence": report.confidence,
            },
        )
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_orchestration.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_planning.py (sha256=1d634517b61b37d159bb24e257ed9bfe0cbc482b9a173f1b599b1caed3f36192) ====
"""Deterministic Level-1 planner for RAG orchestration."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core_v10_7 import BaseAgent, RAGPlan

from .planning_utils import describe_experience, extract_job_profile, extract_resume_profile


class RAGPlanningStack(BaseAgent):
    """Produces a lightweight retrieval plan without calling any tools."""

    def __init____src3(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._build_plan(state)
        return {"rag": {"plan": plan.model_dump()}}

    def _build_plan(self, state: Dict[str, Any]) -> RAGPlan:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        experiences = resume_profile["experiences"]
        requirements = job_profile["requirements"]
        workflow_goal = self._goal_statement(job_profile)
        context_inputs = self._context_inputs(job_profile, resume_profile)
        retrieval_queries = self._queries(job_profile, experiences, requirements)
        prioritization = self._prioritization(requirements, experiences)
        risk_checks = self._risk_checks(requirements)
        return RAGPlan(
            goal=workflow_goal,
            context_inputs=context_inputs,
            retrieval_queries=retrieval_queries,
            prioritization=prioritization,
            risk_checks=risk_checks,
        )

    def _goal_statement(self, job_profile: Dict[str, Any]) -> str:
        title = job_profile["title"]
        company = job_profile["company"]
        if title and company:
            return f"Surface evidence that proves readiness for {title} at {company}"
        if title:
            return f"Surface evidence tailored to the {title} mandate"
        return "Surface evidence aligned to the target role"

    def _context_inputs(
        self, job_profile: Dict[str, Any], resume_profile: Dict[str, Any]
    ) -> List[str]:
        inputs: List[str] = []
        if job_profile["summary"]:
            inputs.append("job.description")
        if job_profile["requirements"]:
            inputs.append("job.requirements")
        if resume_profile["summary"]:
            inputs.append("resume.summary")
        if resume_profile["experiences"]:
            inputs.append("resume.professional_experience")
        metadata = self.context.prompt_manager.goal_state if self.context else {}
        if metadata:
            inputs.append("prompt.goal_state")
        return inputs

    def _queries(
        self,
        job_profile: Dict[str, Any],
        experiences: List[Dict[str, Any]],
        requirements: List[str],
    ) -> List[str]:
        queries: List[str] = []
        base_role = job_profile["title"] or "target role"
        company = job_profile["company"]
        keyword_suffix = (
            " ".join(requirements[:2]) if requirements else "impact metrics"
        )
        queries.append(f"{base_role} {company} {keyword_suffix}".strip())
        if experiences:
            queries.append(
                f"{describe_experience(experiences[0])} supporting evidence for {base_role}"
            )
        if len(experiences) > 1:
            queries.append(
                f"Leadership examples from {describe_experience(experiences[1])}"
            )
        return [query for query in queries if query]

    def _prioritization(
        self,
        requirements: List[str],
        experiences: List[Dict[str, Any]],
    ) -> List[str]:
        prioritization: List[str] = []
        if requirements:
            prioritization.append(
                f"Match JD keywords first: {', '.join(requirements[:3])}"
            )
        if experiences:
            prioritization.append("Favor most recent quantified roles")
        prioritization.append("Deduplicate overlapping bullets before ranking")
        return prioritization

    def _risk_checks(self, requirements: List[str]) -> List[str]:
        checks = [
            "Verify every plan output references an original resume source",
            "Ensure at least one leadership and one technical example",
        ]
        if requirements:
            checks.append("Confirm each top JD requirement is backed by evidence")
        return checks
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/rag_planning.py ====
