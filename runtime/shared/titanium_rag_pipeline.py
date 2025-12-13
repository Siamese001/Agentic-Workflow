"""Titanium RAG Pipeline - State-of-the-Art Retrieval with Precision, Reasoning, and SOTA.

This module orchestrates the complete Titanium RAG system with three layers:
- Phase 1: Precision Layer (Contextual Compression)
- Phase 2: Reasoning Layer (Query Decomposition & Dynamic Scoring)
- Phase 3: SOTA Layer (Semantic Cache & Cross-Encoder Reranking)

Enhanced with adversarial defense as the outermost security layer.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass

from .precision_layer import (
    ContextualCompressor,
    SignalQualityPipeline,
    CompressionResult,
    create_compressor,
    create_signal_pipeline,
)
from .reasoning_layer import (
    QueryDecomposer,
    DecomposedQuery,
    HybridScorer,
    ScoringResult,
    create_query_decomposer,
    create_hybrid_scorer,
)
from .sota_layer import (
    ContrastiveSemanticCache,
    LateInteractionReranker,
    CacheEntry,
    RerankResult,
    create_cache,
    create_reranker,
)
from .input_guardrail import (
    InputGuardrail,
    GuardAction,
    GuardResult,
    get_input_guardrail,
)

logger = logging.getLogger(__name__)


class TitaniumRAGPipeline:
    """Titanium-grade RAG pipeline combining all three layers.
    
    Phase 1 (Precision): Filters noise and avoids unnecessary searches
    Phase 2 (Reasoning): Handles complex queries with intelligent decomposition
    Phase 3 (SOTA): Provides Google-quality ranking and Redis-speed caching
    """
    
    def __init__(
        self,
        # Phase 1 components
        gate: Optional[AdaptiveRetrievalGate] = None,
        compressor: Optional[ContextualCompressor] = None,
        
        # Phase 2 components
        decomposer: Optional[QueryDecomposer] = None,
        scorer: Optional[HybridScorer] = None,
        
        # Phase 3 components
        reranker: Optional[LateInteractionReranker] = None,
        cache: Optional[ContrastiveSemanticCache] = None,
        
        # Security layer
        input_guardrail: Optional[InputGuardrail] = None,
        
        # Configuration
        enable_compression: bool = True,
        enable_decomposition: bool = True,
        enable_reranking: bool = True,
        enable_caching: bool = True,
        enable_security: bool = True,
        max_retrieved_docs: int = 50,
        top_k_final: int = 5
    ):
        """Initialize the Titanium RAG Pipeline.
        
        Args:
            gate: Adaptive retrieval gate (Phase 1)
            compressor: Contextual compressor (Phase 1)
            decomposer: Query decomposer (Phase 2)
            scorer: Dynamic hybrid scorer (Phase 2)
            reranker: Late interaction reranker (Phase 3)
            cache: Contrastive semantic cache (Phase 3)
            input_guardrail: Security layer for input validation
            enable_compression: Whether to enable compression
            enable_decomposition: Whether to enable query decomposition
            enable_reranking: Whether to enable reranking
            enable_caching: Whether to enable caching
            enable_security: Whether to enable security scanning
            max_retrieved_docs: Maximum documents to retrieve initially
            top_k_final: Number of top documents to return
        """
        # Initialize components if not provided
        self.gate = gate or AdaptiveRetrievalGate()
        self.compressor = compressor or ContextualCompressor()
        self.decomposer = decomposer or QueryDecomposer()
        self.scorer = scorer or HybridScorer(dynamic_alpha=True)
        self.reranker = reranker or LateInteractionReranker()
        self.cache = cache or ContrastiveSemanticCache()
        
        # Initialize security layer
        self.input_guardrail = input_guardrail or (get_input_guardrail() if enable_security else None)
        self.enable_security = enable_security and self.input_guardrail is not None
        
        # Configuration
        self.enable_compression = enable_compression
        self.enable_decomposition = enable_decomposition
        self.enable_reranking = enable_reranking
        self.enable_caching = enable_caching
        self.max_retrieved_docs = max_retrieved_docs
        self.top_k_final = top_k_final
        
        # Statistics
        self.stats = {
            "total_queries": 0,
            "gate_blocks": 0,
            "cache_hits": 0,
            "decompositions": 0,
            "compressions": 0,
            "rerankings": 0,
            "security_blocks": 0,
            "security_warnings": 0,
            "pii_redactions": 0
        }
        
        logger.info(f"Initialized TitaniumRAGPipeline with all 3 phases + "
                   f"Security Layer: {self.enable_security}")
    
    async def query(
        self,
        query: str,
        retrieval_function: callable,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a complete RAG pipeline query.
        
        Args:
            query: User query
            retrieval_function: Async function to retrieve documents
            **kwargs: Additional arguments for retrieval function
            
        Returns:
            Dictionary with results and metadata
        """
        start_time = time.time()
        self.stats["total_queries"] += 1
        
        logger.info(f"Processing query: {query[:50]}...")
        
        # Security Layer: Input validation (Phase 0 - Outermost)
        # ----------------------------------------------------
        if self.enable_security and self.input_guardrail:
            guard_result = self.input_guardrail.scan(query, user_id=kwargs.get('user_id'))
            
            # Handle security actions
            if guard_result.action == GuardAction.BLOCK:
                self.stats["security_blocks"] += 1
                logger.warning(f"Query blocked by security: {guard_result.reason}")
                return {
                    "query": query,
                    "response": "I cannot process that request due to safety protocols.",
                    "documents": [],
                    "metadata": {
                        "security_action": "BLOCKED",
                        "security_reason": guard_result.reason,
                        "security_confidence": guard_result.confidence,
                        "processing_time": time.time() - start_time
                    }
                }
            elif guard_result.action == GuardAction.WARN:
                self.stats["security_warnings"] += 1
                logger.warning(f"Security warning for query: {guard_result.reason}")
                # Continue but mark as suspicious
            elif guard_result.action == GuardAction.REDACT:
                self.stats["pii_redactions"] += 1
                logger.info(f"PII redacted from query")
                query = guard_result.sanitized_input or query
        
        # Phase 1: Precision Layer
        # ----------------------
        
        # 1. Check if retrieval is needed
        gate_decision = self.gate.should_retrieve(query)
        if not gate_decision.should_retrieve:
            self.stats["gate_blocks"] += 1
            logger.info(f"Query blocked by gate: {gate_decision.reason}")
            return {
                "query": query,
                "response": None,
                "documents": [],
                "metadata": {
                    "gate_decision": gate_decision.dict(),
                    "cached": False,
                    "decomposed": False,
                    "compressed": False,
                    "reranked": False,
                    "processing_time": time.time() - start_time
                }
            }
        
        # 2. Check semantic cache
        cached_response = None
        if self.enable_caching:
            cached_response = self.cache.get(query)
            if cached_response:
                self.stats["cache_hits"] += 1
                logger.info("Cache hit, returning cached response")
                return {
                    "query": query,
                    "response": cached_response,
                    "documents": [],
                    "metadata": {
                        "gate_decision": gate_decision.dict(),
                        "cached": True,
                        "decomposed": False,
                        "compressed": False,
                        "reranked": False,
                        "processing_time": time.time() - start_time
                    }
                }
        
        # Phase 2: Reasoning Layer
        # -----------------------
        
        # 3. Decompose query if needed
        queries_to_process = [query]
        decomposed_result = None
        
        if self.enable_decomposition:
            decomposed_result = await self.decomposer.decompose(query)
            if len(decomposed_result.sub_queries) > 1:
                queries_to_process = decomposed_result.sub_queries
                self.stats["decompositions"] += 1
                logger.info(f"Decomposed into {len(queries_to_process)} sub-queries")
        
        # 4. Retrieve documents for each query
        all_retrieved = []
        for sub_query in queries_to_process:
            # Retrieve dense and sparse results
            dense_results, sparse_results = await retrieval_function(
                sub_query,
                max_docs=self.max_retrieved_docs,
                **kwargs
            )
            
            # Score with dynamic alpha
            scored = self.scorer.score_documents(
                dense_results=dense_results,
                sparse_results=sparse_results,
                query=sub_query
            )
            
            all_retrieved.extend(scored)
        
        # Remove duplicates and sort by score
        seen_docs = set()
        unique_docs = []
        for doc in all_retrieved:
            if doc.doc_id not in seen_docs:
                seen_docs.add(doc.doc_id)
                unique_docs.append(doc)
        
        unique_docs.sort(key=lambda x: x.final_score, reverse=True)
        retrieved_docs = unique_docs[:self.max_retrieved_docs]
        
        logger.info(f"Retrieved {len(retrieved_docs)} unique documents")
        
        # Phase 3: SOTA Layer
        # -------------------
        
        # 5. Rerank documents
        if self.enable_reranking and len(retrieved_docs) > self.top_k_final:
            # Extract document texts from metadata
            doc_texts = []
            for doc in retrieved_docs:
                # Try multiple fields for document text
                if hasattr(doc, 'metadata') and 'text' in doc.metadata:
                    doc_texts.append(doc.metadata['text'])
                elif hasattr(doc, 'text'):
                    doc_texts.append(doc.text)
                elif hasattr(doc, 'content'):
                    doc_texts.append(doc.content)
                else:
                    # Fallback: use doc_id as placeholder
                    doc_texts.append(f"Document {doc.doc_id}")
            
            # Rerank
            reranked_texts = self.reranker.rerank(
                query=query,
                documents=doc_texts,
                top_k=self.top_k_final
            )
            
            # Map back to documents by text matching
            text_to_doc = {}
            for doc in retrieved_docs:
                doc_text = None
                if hasattr(doc, 'metadata') and 'text' in doc.metadata:
                    doc_text = doc.metadata['text']
                elif hasattr(doc, 'text'):
                    doc_text = doc.text
                elif hasattr(doc, 'content'):
                    doc_text = doc.content
                
                if doc_text and doc_text not in text_to_doc:
                    text_to_doc[doc_text] = doc
            
            # Reconstruct final documents list
            final_docs = []
            for text in reranked_texts:
                if text in text_to_doc:
                    final_docs.append(text_to_doc[text])
            
            # If we couldn't map all documents, fill with remaining ones
            if len(final_docs) < self.top_k_final:
                for doc in retrieved_docs:
                    if doc not in final_docs:
                        final_docs.append(doc)
                        if len(final_docs) >= self.top_k_final:
                            break
            
            self.stats["rerankings"] += 1
            logger.info(f"Reranked to {len(final_docs)} documents")
        else:
            final_docs = retrieved_docs[:self.top_k_final]
        
        # 6. Compress context if needed
        compressed_context = None
        if self.enable_compression and final_docs:
            doc_texts = [doc.metadata.get("text", "") for doc in final_docs]
            compression_result = self.compressor.compress(
                chunks=doc_texts,
                query=query
            )
            compressed_context = compression_result.compressed_text
            self.stats["compressions"] += 1
            logger.info(f"Compressed context: {compression_result.compression_ratio:.2f} ratio")
        
        # Generate response (mock - would use LLM in real implementation)
        response = self._generate_response(query, final_docs, compressed_context)
        
        # 7. Cache the result
        if self.enable_caching and response:
            self.cache.put(query, response)
            logger.info("Cached the response")
        
        # Return results
        processing_time = time.time() - start_time
        logger.info(f"Query processed in {processing_time:.3f}s")
        
        return {
            "query": query,
            "response": response,
            "documents": final_docs,
            "compressed_context": compressed_context,
            "metadata": {
                "gate_decision": gate_decision.dict(),
                "cached": False,
                "decomposed": decomposed_result.dict() if decomposed_result else None,
                "compressed": bool(compressed_context),
                "reranked": self.enable_reranking and len(retrieved_docs) > self.top_k_final,
                "processing_time": processing_time,
                "stats": self.get_stats()
            }
        }
    
    def _generate_response(
        self,
        query: str,
        documents: List[Any],
        compressed_context: Optional[str] = None
    ) -> str:
        """Generate response from retrieved documents.
        
        In a real implementation, this would call an LLM.
        Here we provide a mock response for testing.
        """
        if not documents:
            return "I couldn't find relevant information to answer your question."
        
        # Mock response based on available documents
        response = f"Based on {len(documents)} relevant documents"
        
        if compressed_context:
            response += f" (compressed to {len(compressed_context)} characters)"
        
        response += f", here's the answer to: {query}"
        
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        total = self.stats["total_queries"]
        stats = self.stats.copy()
        
        # Calculate rates
        if total > 0:
            stats["gate_block_rate"] = self.stats["gate_blocks"] / total
            stats["cache_hit_rate"] = self.stats["cache_hits"] / total
            stats["decomposition_rate"] = self.stats["decompositions"] / total
            stats["compression_rate"] = self.stats["compressions"] / total
            stats["reranking_rate"] = self.stats["rerankings"] / total
        else:
            stats.update({
                "gate_block_rate": 0.0,
                "cache_hit_rate": 0.0,
                "decomposition_rate": 0.0,
                "compression_rate": 0.0,
                "reranking_rate": 0.0
            })
        
        return stats
    
    def get_component_info(self) -> Dict[str, Any]:
        """Get information about all components.
        
        Returns:
            Dictionary with component status and capabilities
        """
        return {
            "phase_1_precision": {
                "gate_available": True,
                "compressor_available": True,
                "compression_enabled": self.enable_compression
            },
            "phase_2_reasoning": {
                "decomposer_available": True,
                "scorer_available": True,
                "decomposition_enabled": self.enable_decomposition,
                "dynamic_alpha_enabled": self.scorer.dynamic_alpha
            },
            "phase_3_sota": {
                "reranker_available": self.reranker.is_available,
                "cache_available": self.cache.is_available,
                "reranking_enabled": self.enable_reranking,
                "caching_enabled": self.enable_caching
            }
        }


# Convenience function for quick setup
def create_titanium_pipeline(
    enable_all: bool = True,
    **kwargs
) -> TitaniumRAGPipeline:
    """Create a Titanium RAG Pipeline with default configuration.
    
    Args:
        enable_all: Whether to enable all features
        **kwargs: Additional configuration options
        
    Returns:
        Configured TitaniumRAGPipeline instance
    """
    if enable_all:
        return TitaniumRAGPipeline(
            enable_compression=True,
            enable_decomposition=True,
            enable_reranking=True,
            enable_caching=True,
            **kwargs
        )
    else:
        return TitaniumRAGPipeline(**kwargs)
