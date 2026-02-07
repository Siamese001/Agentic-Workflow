from __future__ import annotations

"""
RAGGuardrail - L5 RAG Content Filtering and Reranking
"""
import asyncio
import math
import re
from typing import Any

# Lazy import torch to avoid import-time side effects
torch = None


def _get_torch():
    """Lazy load torch to avoid import-time overhead."""
    global torch
    if torch is None:
        import torch as _torch

        torch = _torch
    return torch


class RagGuardrail:
    """Brief description of functionality and purpose."""

    def __init__(self):
        self.bge_reranker = None
        self.reranker_available = False
        try:
            from FlagEmbedding import FlagReranker

            _torch = _get_torch()
            device = (
                "cuda"
                if _torch.cuda.is_available()
                else "mps"
                if _torch.backends.mps.is_available()
                else "cpu"
            )
            model_name = "BAAI/bge-reranker-v2-m3"
            self.bge_reranker = FlagReranker(model_name, use_fp16=device != "cpu")
            self.reranker_available = True
            print(f"   [OK] BGE Reranker armed on {device}: {model_name}")
        except ImportError:
            print("   [!] FlagEmbedding not installed — falling back to RRF only")

    async def rerank_documents(self, documents: list[Any], query: str, top_k: int = 10) -> list[Any]:
        """
        L5 reranking using BGE-v2-m3 for sovereign precision
        """
        if not self.reranker_available or not documents:
            return documents
        try:
            pairs: Any = [[query, doc.text] for doc in documents]

            def _compute():
                return self.bge_reranker.compute_score(pairs, batch_size=32)

            raw_logits: Any = await asyncio.to_thread(_compute)
            if isinstance(raw_logits, float | int):
                raw_logits: Any = [raw_logits]
            confident_docs: Any = []
            min_confidence: Any = 0.75
            for doc, logit in zip(documents, raw_logits, strict=False):
                confidence: Any = 1 / (1 + math.exp(-logit))
                if confidence >= min_confidence:
                    doc.score = float(confidence)
                    confident_docs.append(doc)
            confident_docs.sort(key=lambda x: x.score, reverse=True)
            dropped: Any = len(documents) - len(confident_docs)
            if dropped > 0:
                print(f"   [FILTER] Dropped {dropped} low-confidence docs (<{min_confidence})")
            if not confident_docs:
                print("   [!] SOVEREIGN ALERT: Zero documents passed confidence threshold.")
            return confident_docs[:top_k]
        except Exception as e:
            print(f"   [!] BGE reranking failed: {e}")
            return documents

    async def filter_hallucinations(self, documents: list[Any], query: str) -> list[Any]:
        """
        Heuristic: Checks if key entities in the query/response are supported by documents.
        """
        if not documents:
            return documents

        combined_context = " ".join([d.text.lower() for d in documents])

        # Extract capitalized words (heuristic for entities) from query
        # In a real scenario, we would check the *Response*, but here we check if
        # the documents retrieved actually support the Query's entities.
        query_entities = set(re.findall(r"\b[A-Z][a-z]+\b", query))

        if not query_entities:
            return documents

        supported_entities = 0
        for entity in query_entities:
            if entity.lower() in combined_context:
                supported_entities += 1

        # If the retrieved docs don't contain at least 50% of the query's entities, warn.
        ratio = supported_entities / len(query_entities)
        if ratio < 0.5:
            print(f"   [WARN] Retrieval Validity Low: Only {ratio:.1%} of query entities found in context.")

        return documents

    async def apply_safety_filters(self, documents: list[Any]) -> list[Any]:
        """
        Apply L5 safety filters to RAG results
        """
        filtered: Any = []
        for doc in documents:
            if not doc.text or len(doc.text.strip()) < 10:
                continue
            forbidden: Any = ["password", "secret", "api_key", "private_key"]
            text_lower: Any = doc.text.lower()
            if any(word in text_lower for word in forbidden):
                continue
            filtered.append(doc)
        return filtered

    async def process(self, documents: list[Any], query: str) -> list[Any]:
        """
        Full RAG guardrail processing pipeline
        """
        filtered: Any = await self.apply_safety_filters(documents)
        safe: Any = await self.filter_hallucinations(filtered, query)
        reranked: Any = await self.rerank_documents(safe, query)
        return reranked
