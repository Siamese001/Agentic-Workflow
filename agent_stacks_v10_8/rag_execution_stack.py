"""Layer-pure Action/RAG stack wrapper for v10.8."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple

from core_v10_7 import BaseAgent, PydanticSchemaError, _format_prompt_with_defaults
from agent_tools_v10_7 import HyDETool, ChromaDBSearchTool, BM25SearchTool


class RAGExecutionStack(BaseAgent):
    """Layer-2 execution stack that performs deterministic hybrid retrieval."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self.context = context
        self.hyde_tool = HyDETool(context, debug_mode)
        self.bm25_tool = BM25SearchTool(context, debug_mode)
        self.chroma_tool = ChromaDBSearchTool(context, debug_mode)
        self.chroma_client = context.chromadb_client
        self.collection_name = context.config.chromadb_config.default_collection_name
        self.embedding_function = context.embedding_function

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute deterministic hybrid retrieval and return a patch."""

        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        query = self._build_query(state)
        resume_experience = self._extract_experience(state)

        await self._ingest_resume_to_chroma_async(resume_experience, workflow_id)

        search_query, hyde_meta = await self._generate_hypothetical_query(
            query, workflow_id
        )
        corpus_text, corpus_metadata = self._build_bm25_corpus(resume_experience)

        chroma_results = await self._run_chroma_search(search_query, workflow_id)
        bm25_results = await self._run_bm25_search(
            search_query, corpus_text, corpus_metadata, workflow_id
        )

        merged_candidates = self._merge_and_dedupe([chroma_results, bm25_results])
        if not merged_candidates:
            merged_candidates = resume_experience[: self.config.agent_stacks.reranking_top_k]

        ranked, rerank_meta = await self._rerank_candidates(
            query, merged_candidates, state
        )

        return {"resume": {"experience_bullets": ranked}}

    def _build_query(self, state: Dict[str, Any]) -> str:
        job = state.get("job", {})
        job_title = job.get("job_title") or job.get("title") or ""
        company = job.get("company") or job.get("employer") or ""
        if job_title and company:
            return f"{job_title} at {company}"
        return job_title or company or state.get("metadata", {}).get("workflow_id", "")

    def _extract_experience(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        resume = state.get("resume", {})
        master_resume = resume.get("master_resume") or {}
        experience = master_resume.get("professional_experience")
        if isinstance(experience, list):
            return experience
        return []

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
        for exp_index, exp in enumerate(resume_experience):
            bullets = exp.get("bullet_pool") or []
            exp_payload = json.dumps(exp, sort_keys=True)
            for bullet_index, bullet in enumerate(bullets):
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

        if not documents:
            return

        try:
            await asyncio.to_thread(
                collection.add,
                documents=documents,
                metadatas=metadatas,
                ids=ids,
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
            corpus_text.append(document)
            corpus_metadata.append(exp)
        return corpus_text, corpus_metadata

    async def _generate_hypothetical_query(
        self, base_query: str, workflow_id: str
    ) -> Tuple[str, Dict[str, Any]]:
        try:
            hyde_result = await self.hyde_tool.run_async({"query": base_query}, workflow_id)
        except Exception:
            hyde_result = {"status": "error", "hypothetical_document": base_query}

        document = hyde_result.get("hypothetical_document") or base_query
        status = hyde_result.get("status", "error")
        return document, {"status": status, "document": document}

    async def _run_chroma_search(
        self, query: str, workflow_id: str
    ) -> List[Dict[str, Any]]:
        try:
            result = await self.chroma_tool.run_async({"query": query}, workflow_id)
        except Exception:
            return []
        return result.get("search_results") or []

    async def _run_bm25_search(
        self,
        query: str,
        corpus_text: Sequence[str],
        corpus_metadata: Sequence[Dict[str, Any]],
        workflow_id: str,
    ) -> List[Dict[str, Any]]:
        if not corpus_text:
            return []
        tool_input = {
            "query": query,
            "corpus_text": list(corpus_text),
            "corpus_metadata": list(corpus_metadata),
        }
        try:
            result = await self.bm25_tool.run_async(tool_input, workflow_id)
        except Exception:
            return []
        return result.get("search_results") or []

    def _merge_and_dedupe(
        self, result_lists: Sequence[Sequence[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        merged: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for result_list in result_lists:
            for item in result_list:
                key = json.dumps(item, sort_keys=True, default=str)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(item)
        return merged

    async def _rerank_candidates(
        self,
        query: str,
        candidates: Sequence[Dict[str, Any]],
        state: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        rerank_client = self.get_model_client("reranker_model")
        prompt_template = self.prompt_manager.get_template("rerank_results")
        strategy = state.get("strategy", {}).get("strategy_plan", {})
        if hasattr(strategy, "model_dump"):
            strategy_payload = strategy.model_dump()
        else:
            strategy_payload = strategy

        formatted_candidates = json.dumps(candidates, default=str)
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {
                "query": query,
                "strategy": json.dumps(strategy_payload, default=str),
                "candidates": formatted_candidates,
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
            ranked = content.get("ranked")
            if isinstance(ranked, list) and ranked:
                ordered = ranked[: self.config.agent_stacks.reranking_top_k]
            else:
                ordered = list(candidates[: self.config.agent_stacks.reranking_top_k])
        except Exception:
            ordered = list(candidates[: self.config.agent_stacks.reranking_top_k])

        scores = [float(len(ordered) - idx) for idx, _ in enumerate(ordered)]
        return ordered, {"scores": scores}

    def _build_rag_metadata(
        self,
        query: str,
        search_query: str,
        hyde_meta: Dict[str, Any],
        bm25_results: Sequence[Dict[str, Any]],
        chroma_results: Sequence[Dict[str, Any]],
        ranked: Sequence[Dict[str, Any]],
        rerank_meta: Dict[str, Any],
    ) -> Dict[str, Any]:
        top_entry = ranked[0] if ranked else {}
        document = self._summarize_experience(top_entry)
        source_uri = top_entry.get("source_uri") or self._build_source_uri(top_entry)
        scores = rerank_meta.get("scores") or []
        top_score = scores[0] if scores else 0.0

        return {
            "query": query,
            "search_query": search_query,
            "hyde_status": hyde_meta.get("status"),
            "document": document,
            "top_document": document,
            "score": top_score,
            "scores": scores,
            "source_uri": source_uri,
            "raw_results": {
                "bm25": bm25_results,
                "chroma": chroma_results,
            },
        }

    def _summarize_experience(self, experience: Dict[str, Any]) -> str:
        if not experience:
            return ""
        bullets = experience.get("bullet_pool") or []
        header_parts = [experience.get("title"), experience.get("company")]
        header = " - ".join([part for part in header_parts if part])
        excerpt = bullets[0] if bullets else ""
        return " ".join(part for part in [header, excerpt] if part)

    def _build_source_uri(self, experience: Dict[str, Any]) -> str:
        company = experience.get("company", "unknown").lower().replace(" ", "-")
        title = experience.get("title", "role").lower().replace(" ", "-")
        return f"resume://experience/{company}/{title}"
