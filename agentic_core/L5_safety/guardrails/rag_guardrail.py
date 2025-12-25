#!/usr/bin/env python3
"""
RAGGuardrail - L5 RAG Content Filtering and Reranking
"""

import asyncio
import math
from typing import List, Dict, Any, Optional

import torch

class RAGGuardrail:
    def __init__(self):
        self.bge_reranker = None
        self.reranker_available = False

        try:
            from FlagEmbedding import FlagReranker
            # Detect hardware: CUDA > MPS (Mac) > CPU
            device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
            # v2-m3 is the 2025 SOTA for multilingual + 1024 context
            model_name = "BAAI/bge-reranker-v2-m3" 
            self.bge_reranker = FlagReranker(model_name, use_fp16=(device != "cpu"))
            self.reranker_available = True
            print(f"   [OK] BGE Reranker armed on {device}: {model_name}")
        except ImportError:
            print(f"   [!] FlagEmbedding not installed — falling back to RRF only")

    async def rerank_documents(
        self,
        documents: List[Any],
        query: str,
        top_k: int = 10
    ) -> List[Any]:
        """
        L5 reranking using BGE-v2-m3 for sovereign precision
        """
        if not self.reranker_available or not documents:
            return documents

        try:
            # BGE-v2-m3 Reranking with Sovereign Confidence Filtering
            pairs = [[query, doc.text] for doc in documents]
            
            def _compute():
                return self.bge_reranker.compute_score(pairs, batch_size=32)
            
            raw_logits = await asyncio.to_thread(_compute)
            
            if isinstance(raw_logits, (float, int)):
                raw_logits = [raw_logits]

            confident_docs = []
            min_confidence = 0.75  # Sovereign Default
            
            for doc, logit in zip(documents, raw_logits):
                # Apply Sigmoid: 1 / (1 + exp(-x))
                confidence = 1 / (1 + math.exp(-logit))
                
                if confidence >= min_confidence:
                    doc.score = float(confidence)
                    confident_docs.append(doc)

            # Resort by calibrated confidence
            confident_docs.sort(key=lambda x: x.score, reverse=True)
            
            dropped = len(documents) - len(confident_docs)
            if dropped > 0:
                print(f"   [FILTER] Dropped {dropped} low-confidence docs (<{min_confidence})")
            
            if not confident_docs:
                print(f"   [!] SOVEREIGN ALERT: Zero documents passed confidence threshold.")
                
            return confident_docs[:top_k]
        except Exception as e:
            print(f"   [!] BGE reranking failed: {e}")
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
