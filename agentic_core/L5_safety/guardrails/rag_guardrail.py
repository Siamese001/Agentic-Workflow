#!/usr/bin/env python3
"""
RAGGuardrail - L5 RAG Content Filtering and Reranking
"""

import asyncio
import torch
from typing import List, Dict, Any, Optional

class RAGGuardrail:
    def __init__(self):
        self.colbert_reranker = None
        self.reranker_available = False

        try:
            from ragatouille import RAGPretrainedModel
            # Detect best available hardware
            device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
            self.colbert_reranker = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
            # Note: RAGatouille handles device internally, but we log it for sovereignty
            self.reranker_available = True
            print(f"   [OK] ColBERTv2 reranker armed on {device} — sovereign precision online")
        except ImportError:
            print(f"   [!] ragatouille not installed — falling back to RRF only")

    async def rerank_documents(
        self,
        documents: List[Any],
        query: str,
        top_k: int = 10
    ) -> List[Any]:
        """
        Sovereign reranking using ColBERTv2 for maximum precision
        """
        if not self.reranker_available or not documents:
            return documents

        try:
            # Extract texts for ColBERT
            doc_texts = [doc.text for doc in documents]
            
            # Offload heavy ColBERT scoring to a thread pool
            def _colbert_run():
                return self.colbert_reranker.rerank(
                    query=query, 
                    documents=doc_texts, 
                    k=len(doc_texts)
                )
            
            rerank_results = await asyncio.to_thread(_colbert_run)
            
            # Map back to RetrievalResult objects
            reranked_docs = []
            for result in rerank_results:
                # RAGatouille returns document_index which matches our input order
                idx = result["result_index"] if "result_index" in result else result["document_index"]
                original_doc = documents[idx]
                original_doc.score = float(result["score"])
                reranked_docs.append(original_doc)
            
            print(f"   [RERANK] ColBERTv2 applied → top-{top_k} sovereign refined")
            return reranked_docs[:top_k]
        except Exception as e:
            print(f"   [!] ColBERT reranking failed: {e}")
            return documents

    async def filter_hallucinations(self, documents: List[Any], query: str) -> List[Any]:
        """
        Filter out potentially hallucinated content
        """
        if not documents:
            return documents

        # Placeholder for hallucination detection
        # Could integrate with factual verification systems
        return documents

    async def apply_safety_filters(self, documents: List[Any]) -> List[Any]:
        """
        Apply L5 safety filters to RAG results
        """
        filtered = []
        
        for doc in documents:
            # Basic safety checks
            if not doc.text or len(doc.text.strip()) < 10:
                continue
                
            # Check for forbidden patterns
            forbidden = ["password", "secret", "api_key", "private_key"]
            text_lower = doc.text.lower()
            
            if any(word in text_lower for word in forbidden):
                continue
                
            filtered.append(doc)
        
        return filtered

    async def process(self, documents: List[Any], query: str) -> List[Any]:
        """
        Full RAG guardrail processing pipeline
        """
        # Step 1: Safety filtering
        filtered = await self.apply_safety_filters(documents)
        
        # Step 2: Hallucination filtering
        safe = await self.filter_hallucinations(filtered, query)
        
        # Step 3: Rerank for relevance
        reranked = await self.rerank_documents(safe, query)
        
        return reranked
