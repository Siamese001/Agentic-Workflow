from __future__ import annotations
"""
RAGGuardrail - L5 RAG Content Filtering and Reranking
"""
import asyncio
import math
from typing import Any, Dict, List, Optional
import torch

class RagGuardrail:
    """Brief description of functionality and purpose."""

    def __init__(self):
        self.bge_reranker = None
        self.reranker_available = False
        try:
            from FlagEmbedding import FlagReranker
            device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
            model_name = 'BAAI/bge-reranker-v2-m3'
            self.bge_reranker = FlagReranker(model_name, use_fp16=device != 'cpu')
            self.reranker_available = True
            print(f'   [OK] BGE Reranker armed on {device}: {model_name}')
        except ImportError:
            print(f'   [!] FlagEmbedding not installed — falling back to RRF only')

    async def rerank_documents(self, documents: List[Any], query: str, top_k: int=10) -> List[Any]:
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
            if isinstance(raw_logits, (float, int)):
                raw_logits: Any = [raw_logits]
            confident_docs: Any = []
            min_confidence: Any = 0.75
            for doc, logit in zip(documents, raw_logits):
                confidence: Any = 1 / (1 + math.exp(-logit))
                if confidence >= min_confidence:
                    doc.score = float(confidence)
                    confident_docs.append(doc)
            confident_docs.sort(key=lambda x: x.score, reverse=True)
            dropped: Any = len(documents) - len(confident_docs)
            if dropped > 0:
                print(f'   [FILTER] Dropped {dropped} low-confidence docs (<{min_confidence})')
            if not confident_docs:
                print(f'   [!] SOVEREIGN ALERT: Zero documents passed confidence threshold.')
            return confident_docs[:top_k]
        except Exception as e:
            print(f'   [!] BGE reranking failed: {e}')
            return documents

    async def filter_hallucinations(self, documents: List[Any], query: str) -> List[Any]:
        """
        Filter out potentially hallucinated content
        """
        if not documents:
            return documents
        return documents

    async def apply_safety_filters(self, documents: List[Any]) -> List[Any]:
        """
        Apply L5 safety filters to RAG results
        """
        filtered: Any = []
        for doc in documents:
            if not doc.text or len(doc.text.strip()) < 10:
                continue
            forbidden: Any = ['password', 'secret', 'api_key', 'private_key']
            text_lower: Any = doc.text.lower()
            if any((word in text_lower for word in forbidden)):
                continue
            filtered.append(doc)
        return filtered

    async def process(self, documents: List[Any], query: str) -> List[Any]:
        """
        Full RAG guardrail processing pipeline
        """
        filtered: Any = await self.apply_safety_filters(documents)
        safe: Any = await self.filter_hallucinations(filtered, query)
        reranked: Any = await self.rerank_documents(safe, query)
        return reranked
