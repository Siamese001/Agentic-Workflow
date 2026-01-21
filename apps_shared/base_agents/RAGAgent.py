"""Agentic RAG conductor stack."""

import asyncio
import json
import uuid
from typing import Any

from agent_tools_v10_7 import BM25SearchTool, ChromaDBSearchTool, HyDETool
from core_v10_7 import (
    A2AMessage,
    BaseAgent,
    PydanticSchemaError,
    _format_prompt_with_defaults,
    track_metrics,
)


class RAG_SearchAgent(BaseAgent):
    """Agentic RAG conductor that orchestrates resume search tooling."""

    def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.tools = {
            "search_resume_database": ChromaDBSearchTool(context, debug_mode),
            "search_resume_bm25": BM25SearchTool(context, debug_mode),
            "generate_hypothetical_documents": HyDETool(context, debug_mode),
        }
        self.tool_schemas = [t.get_schema() for t in self.tools.values()]
        self.chroma_client = self.context.chromadb_client
        self.collection_name = self.config.chromadb_config.default_collection_name
        self.embedding_function = self.context.embedding_function

    async def _ingest_resume_to_chroma_async(
        self,
        resume_experience: list[dict[str, Any]],
        workflow_id: str,
    ) -> None:
        self.log_info(
            f"Ingesting {len(resume_experience)} experience blocks into ChromaDB..."
        )
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )
            documents: list[str] = []
            metadatas: list[dict[str, Any]] = []
            ids: list[str] = []
            for exp in resume_experience:
                for bullet in exp.get("bullet_pool", []):
                    documents.append(bullet)
                    metadatas.append(
                        {
                            "workflow_id": workflow_id,
                            "company": exp.get("company", "N/A"),
                            "title": exp.get("title", "N/A"),
                            "experience_object": json.dumps(exp),
                        }
                    )
                    ids.append(f"{workflow_id}_{uuid.uuid4()}")

            if documents:
                await asyncio.to_thread(
                    collection.add,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                )
        except Exception as exc:  # pragma: no cover - defensive logging
            self.log_error(f"ChromaDB ingestion failed: {exc}")

    def _build_bm25_corpus(
        self, resume_experience: list[dict[str, Any]]
    ) -> tuple[list[str], list[dict[str, Any]]]:
        corpus_text: list[str] = []
        corpus_metadata: list[dict[str, Any]] = []
        for exp in resume_experience:
            doc = (
                f"{exp.get('title')} {exp.get('company')} "
                f"{' '.join(exp.get('bullet_pool', []))}"
            )
            corpus_text.append(doc)
            corpus_metadata.append(exp)
        return corpus_text, corpus_metadata

    def _merge_and_deduplicate(self, all_results: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}
        for result_list in all_results:
            for item in result_list:
                key = f"{item.get('company')}_{item.get('title')}"
                merged.setdefault(key, item)
        return list(merged.values())

    async def rerank_results(
        self, query: str, candidates: list[dict[str, Any]], client: Any
    ) -> list[dict[str, Any]]:
        self.log_info(f"Reranking {len(candidates)} hybrid candidates...")
        prompt_template = self.prompt_manager.get_template("rerank_results")

        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"query": query, "strategy": "N/A", "candidates": json.dumps(candidates)},
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.reranker_model.temperature,
            response_format="json_object",
        )
        try:
            content, error = self.validator.validate(response["content"], dict)
            if error:
                raise PydanticSchemaError(error)
            ranked_list = content.get("ranked")
            if isinstance(ranked_list, list):
                ranked = ranked_list[: self.config.agent_stacks.reranking_top_k]
            else:
                ranked = candidates[: self.config.agent_stacks.reranking_top_k]
        except Exception:
            ranked = candidates[: self.config.agent_stacks.reranking_top_k]
        return ranked

    @track_metrics("run_agentic_rag")
    async def run_async(self, state: dict[str, Any]) -> dict[str, Any]:
        self.log_info("Running Agentic RAG Conductor (v10.7)...")

        workflow_id = state["metadata"]["workflow_id"]
        query = f"{state['job']['job_title']} at {state['job']['company']}"
        resume_experience = state["resume"]["master_resume"].get(
            "professional_experience", []
        )
        a2a_messages = state.get("a2a", {}).get("messages", [])

        await self._ingest_resume_to_chroma_async(resume_experience, workflow_id)
        corpus_text, corpus_metadata = self._build_bm25_corpus(resume_experience)

        client = self.get_model_client("react_conductor_model")
        rerank_client = self.get_model_client("reranker_model")
        max_steps = 5

        react_prompt_template = f"""
        {client.goal_state}
        {client.top_failures}
        -------------------
        MODE: ORCHESTRATION
        TASK: You are an Agentic RAG Conductor. Find relevant resume sections.
        Query: "{query}"
        Tools: {json.dumps(self.tool_schemas)}
        Plan:
        1. Call `search_resume_database` (vector) and `search_resume_bm25` (keyword).
        2. THINK: Analyze merged results.
        3. If results are good (> 3), stop.
        4. If results are poor (< 3), call `generate_hypothetical_documents`.
        5. Loop to step 1 with the new query.
        6. Output final list.
        """

        messages = [{"role": "user", "content": react_prompt_template}]
        current_query = query
        all_tool_results: list[list[dict[str, Any]]] = []

        for step in range(max_steps):
            response = await client.chat_completion_async(
                messages=messages,
                temperature=self.config.agent_stacks.conductor_temperature,
                response_format="json_object",
            )

            step_data, error = self.validator.validate(response["content"], dict)
            if error:
                messages.append({"role": "user", "content": f"Error: Invalid JSON: {error}"})
                continue

            messages.append({"role": "assistant", "content": json.dumps(step_data)})

            if "final_results" in step_data:
                self.log_info(f"RAG agent finished in {step + 1} steps.")
                merged = self._merge_and_deduplicate([step_data["final_results"]])
                ranked = await self.rerank_results(query, merged, rerank_client)
                return {
                    "resume": {"experience_bullets": ranked},
                    "a2a": {"messages": a2a_messages},
                }

            if "tool_call" in step_data:
                tool_name = step_data["tool_call"].get("name")
                tool_input = step_data["tool_call"].get("input", {})
                if tool_name not in self.tools:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})
                    continue
                if tool_name == "search_resume_bm25":
                    tool_input["corpus_text"] = corpus_text
                    tool_input["corpus_metadata"] = corpus_metadata
                if "query" not in tool_input:
                    tool_input["query"] = current_query
                try:
                    tool = self.tools[tool_name]
                    tool_result = await tool.run_async(tool_input, workflow_id)
                    if (
                        tool_name == "generate_hypothetical_documents"
                        and tool_result.get("status") == "success"
                    ):
                        current_query = tool_result["hypothetical_document"]
                    elif tool_name in [
                        "search_resume_database",
                        "search_resume_bm25",
                    ]:
                        all_tool_results.append(tool_result.get("search_results", []))
                    messages.append(
                        {"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"}
                    )
                except Exception as exc:  # pragma: no cover - defensive logging
                    self.log_error(f"RAG Tool {tool_name} failed: {exc}")
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Error: Tool '{tool_name}' failed: {exc}",
                        }
                    )

        self.log_warning("RAG agent reached max steps. Reranking gathered results.")

        a2a_messages.append(
            A2AMessage(
                sender="RAG_SearchAgent",
                recipient="ALL",
                message_type="ERROR",
                payload={"error": "RAG_SearchAgent max steps reached."},
            ).model_dump()
        )

        merged = self._merge_and_deduplicate(all_tool_results)
        ranked = await self.rerank_results(query, merged, rerank_client)
        return {"resume": {"experience_bullets": ranked}, "a2a": {"messages": a2a_messages}}
