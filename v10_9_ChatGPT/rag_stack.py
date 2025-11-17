"""RAG planning and execution."""
from __future__ import annotations

from typing import Dict, List

from .clients import AsyncEmbeddingClient
from .models import Message, RAGPlan
from .services import ServiceBundle
from .telemetry import log_event


class RAGStack:
    def __init__(self, services: ServiceBundle, embedding_client: AsyncEmbeddingClient) -> None:
        self.services = services
        self.embedding_client = embedding_client

    def plan(self, query: str) -> Dict[str, RAGPlan]:
        plan = RAGPlan(query=query, sources=["bm25", "chroma", "hyde"])
        log_event("rag_plan", {"query": query})
        return {"rag_plan": plan}

    async def execute(self, plan: RAGPlan) -> Dict[str, List[Message]]:
        await self.embedding_client.embed(plan.query)
        results = [Message(role="system", content=f"retrieved for {plan.query}")]
        log_event("rag_execute", {"sources": plan.sources})
        return {"messages": results}
