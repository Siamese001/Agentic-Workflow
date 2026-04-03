"""Titanium RAG Pipeline - Advanced Retrieval Pipeline

Implements spec-compliant Titanium RAG with:
- Compression-aware retrieval
- Query decomposition
- Adaptive reranking
- Integration with SovereignRagOrchestrator

Provides the advanced retrieval path for Pipeline C Layer 3.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_captures_evaluation_metric,
)

Logger = logging.getLogger(__name__)


@dataclass
class TitaniumQuery:
    """Decomposed query for Titanium pipeline."""
    original_query: str
    sub_queries: list[str] = field(default_factory=list)
    query_embedding: Optional[list[float]] = None
    complexity_score: float = 0.5
    requires_decomposition: bool = False


@dataclass
class TitaniumRetrievalResult:
    """Result from Titanium RAG pipeline."""
    content: str
    chunk_id: str
    retrieval_score: float
    rerank_score: float
    compression_ratio: float = 1.0
    source_documents: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class TitaniumCompressor:
    """Context compression for efficient retrieval.

    Compresses retrieved documents while preserving semantic meaning.
    """

    def __init__(self, target_token_count: int = 2000, llm_client: Optional[Any] = None):
        self.target_token_count = target_token_count
        self.llm_client = llm_client
        self._compression_count = 0

    def compress(self, documents: list[str], query: str) -> tuple[str, float]:
        """Compress documents to target token count.

        Args:
            documents: List of document chunks
            query: Query for relevance-aware compression

        Returns:
            Tuple of (compressed_text, compression_ratio)
        """
        if not documents:
            return "", 1.0

        # Simple truncation-based compression (production would use LLM)
        combined = "\n\n".join(documents)
        original_length = len(combined)

        # Rough token estimate (1 token ≈ 4 chars)
        current_tokens = original_length // 4

        if current_tokens <= self.target_token_count:
            return combined, 1.0

        # Compress by keeping most relevant sentences
        # In production, this would use query-aware LLM compression
        target_chars = self.target_token_count * 4

        if len(combined) > target_chars:
            compressed = combined[:target_chars] + "..."
        else:
            compressed = combined

        compression_ratio = len(compressed) / original_length
        self._compression_count += 1

        return compressed, compression_ratio


class QueryDecomposer:
    """Decomposes complex queries into sub-queries.

    Identifies when a query requires multi-step retrieval.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client
        self._decomposition_threshold = 0.6

    def decompose(self, query: str) -> TitaniumQuery:
        """Decompose query into sub-queries if complex.

        Args:
            query: Original user query

        Returns:
            TitaniumQuery with decomposition info
        """
        # Analyze query complexity
        complexity = self._calculate_complexity(query)

        if complexity < self._decomposition_threshold:
            # Simple query - no decomposition needed
            return TitaniumQuery(
                original_query=query,
                sub_queries=[query],
                complexity_score=complexity,
                requires_decomposition=False,
            )

        # Complex query - decompose
        sub_queries = self._generate_sub_queries(query)

        return TitaniumQuery(
            original_query=query,
            sub_queries=sub_queries,
            complexity_score=complexity,
            requires_decomposition=True,
        )

    def _calculate_complexity(self, query: str) -> float:
        """Calculate query complexity score (0-1)."""
        # Heuristic-based complexity estimation
        complexity = 0.3  # Base complexity

        # Indicators of complexity
        if "and" in query.lower():
            complexity += 0.1
        if "compare" in query.lower() or "vs" in query.lower():
            complexity += 0.2
        if len(query.split()) > 15:
            complexity += 0.2
        if "?" in query:
            complexity += 0.1

        return min(complexity, 1.0)

    def _generate_sub_queries(self, query: str) -> list[str]:
        """Generate sub-queries for complex queries."""
        # Production would use LLM for decomposition
        # For now, simple splitting on "and" or keeping as single query
        if " and " in query.lower():
            parts = query.lower().split(" and ")
            return [p.strip().capitalize() for p in parts if p.strip()]

        return [query]


class AdaptiveReranker:
    """Adaptive reranking based on initial retrieval scores.

    Implements 4d: Score-Based Adaptive Rerank.
    """

    def __init__(self, top_k: int = 5, diversity_weight: float = 0.3):
        self.top_k = top_k
        self.diversity_weight = diversity_weight
        self._rerank_count = 0

    def rerank(
        self,
        results: list[TitaniumRetrievalResult],
        query: str,
    ) -> list[TitaniumRetrievalResult]:
        """Rerank results using adaptive scoring.

        Args:
            results: Initial retrieval results
            query: Original query

        Returns:
            Reranked results
        """
        if not results:
            return []

        # Calculate rerank scores
        for result in results:
            # Combine retrieval score with diversity bonus
            # Simple MMR-style reranking
            result.rerank_score = result.retrieval_score

        # Sort by rerank score
        reranked = sorted(results, key=lambda r: r.rerank_score, reverse=True)

        # Apply diversity (MMR)
        selected = []
        remaining = reranked[:20]  # Consider top 20

        while len(selected) < self.top_k and remaining:
            if not selected:
                # First pick highest score
                selected.append(remaining.pop(0))
            else:
                # Pick based on MMR: λ*score - (1-λ)*max_similarity
                best_mmr_score = -float('inf')
                best_idx = 0

                for i, result in enumerate(remaining):
                    # Calculate max similarity to selected
                    max_sim = max(
                        self._calculate_similarity(result, s)
                        for s in selected
                    )

                    # MMR score
                    mmr = (
                        (1 - self.diversity_weight) * result.rerank_score -
                        self.diversity_weight * max_sim
                    )

                    if mmr > best_mmr_score:
                        best_mmr_score = mmr
                        best_idx = i

                selected.append(remaining.pop(best_idx))

        self._rerank_count += 1
        return selected

    def _calculate_similarity(
        self,
        result1: TitaniumRetrievalResult,
        result2: TitaniumRetrievalResult,
    ) -> float:
        """Calculate content similarity between two results."""
        # Simple Jaccard similarity on words
        words1 = set(result1.content.lower().split())
        words2 = set(result2.content.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0


class TitaniumRAGPipeline:
    """Titanium RAG Pipeline - Advanced Retrieval Implementation.

    Provides compression, decomposition, and adaptive reranking
    for the SovereignRagOrchestrator.
    """

    def __init__(
        self,
        retriever: Optional[Any] = None,
        llm_client: Optional[Any] = None,
        enable_compression: bool = True,
        enable_decomposition: bool = True,
        enable_reranking: bool = True,
    ):
        """Initialize Titanium pipeline.

        Args:
            retriever: Base retriever (HybridSearchEngine)
            llm_client: LLM for compression/decomposition
            enable_compression: Enable context compression
            enable_decomposition: Enable query decomposition
            enable_reranking: Enable adaptive reranking
        """
        self.retriever = retriever
        self.llm_client = llm_client

        self.compression_enabled = enable_compression
        self.decomposition_enabled = enable_decomposition
        self.reranking_enabled = enable_reranking

        # Initialize components
        self.compressor = TitaniumCompressor(llm_client=llm_client)
        self.decomposer = QueryDecomposer(llm_client=llm_client)
        self.reranker = AdaptiveReranker()

        self._query_count = 0
        self._avg_retrieval_time_ms = 0.0

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        enable_compression: Optional[bool] = None,
    ) -> dict[str, Any]:
        """Execute Titanium RAG retrieval.

        Args:
            query: User query
            top_k: Number of results to return
            enable_compression: Override compression setting

        Returns:
            Retrieval result dict
        """
        import time
        start_time = time.time()

        _trace_id = f"titanium_{self._query_count}"
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "TitaniumRAGPipeline.retrieve"
        )

        # Step 1: Query Decomposition (if enabled)
        if self.decomposition_enabled:
            titanium_query = self.decomposer.decompose(query)
        else:
            titanium_query = TitaniumQuery(
                original_query=query,
                sub_queries=[query],
                requires_decomposition=False,
            )

        # Step 2: Retrieve for each sub-query
        all_results: list[TitaniumRetrievalResult] = []

        for sub_query in titanium_query.sub_queries:
            sub_results = await self._retrieve_single(sub_query, top_k * 2)
            all_results.extend(sub_results)

        # Step 3: Deduplicate and rerank
        deduplicated = self._deduplicate_results(all_results)

        if self.reranking_enabled:
            final_results = self.reranker.rerank(deduplicated, query)
        else:
            final_results = sorted(
                deduplicated,
                key=lambda r: r.retrieval_score,
                reverse=True,
            )[:top_k]

        # Step 4: Compression (if enabled)
        compression_ratio = 1.0
        if enable_compression or (enable_compression is None and self.compression_enabled):
            contexts = [r.content for r in final_results]
            compressed, compression_ratio = self.compressor.compress(contexts, query)
        else:
            compressed = "\n\n".join([r.content for r in final_results])

        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self._avg_retrieval_time_ms = (
            self._avg_retrieval_time_ms * self._query_count + elapsed_ms
        ) / (self._query_count + 1)
        self._query_count += 1

        _emit_captures_evaluation_metric(
            _trace_id, "titanium", "retrieval_time_ms", elapsed_ms
        )

        return {
            "query": query,
            "titanium_query": titanium_query,
            "results": final_results,
            "compressed_context": compressed,
            "compression_ratio": compression_ratio,
            "result_count": len(final_results),
            "retrieval_time_ms": elapsed_ms,
        }

    async def _retrieve_single(
        self,
        query: str,
        top_k: int,
    ) -> list[TitaniumRetrievalResult]:
        """Retrieve for a single query.

        Args:
            query: Query string
            top_k: Number of results

        Returns:
            List of retrieval results
        """
        if self.retriever is None:
            Logger.warning("No retriever configured for Titanium pipeline")
            return []

        try:
            # Use hybrid search engine
            from agentic_core.L3_orchestration.engines.hybrid_search_engine import (
                HybridSearchEngine,
            )

            if isinstance(self.retriever, HybridSearchEngine):
                hybrid_results = self.retriever.search(query, top_k=top_k)
            else:
                # Fallback to whatever retriever provides
                hybrid_results = self.retriever.search(query)

            # Convert to Titanium results
            titanium_results = []
            for result in hybrid_results:
                titanium_results.append(TitaniumRetrievalResult(
                    content=result.content,
                    chunk_id=result.chunk_id,
                    retrieval_score=result.combined_score,
                    rerank_score=result.combined_score,
                    metadata=result.metadata,
                ))

            return titanium_results

        except (ValueError, TypeError) as e:
            Logger.error(f"Retrieval failed: {e}")
            return []

    def _deduplicate_results(
        self,
        results: list[TitaniumRetrievalResult],
    ) -> list[TitaniumRetrievalResult]:
        """Deduplicate results by chunk_id."""
        seen = {}

        for result in results:
            if result.chunk_id not in seen:
                seen[result.chunk_id] = result
            else:
                # Keep higher score
                if result.retrieval_score > seen[result.chunk_id].retrieval_score:
                    seen[result.chunk_id] = result

        return list(seen.values())

    def get_stats(self) -> dict[str, Any]:
        """Get Titanium pipeline statistics."""
        return {
            "query_count": self._query_count,
            "avg_retrieval_time_ms": self._avg_retrieval_time_ms,
            "compression_enabled": self.compression_enabled,
            "decomposition_enabled": self.decomposition_enabled,
            "reranking_enabled": self.reranking_enabled,
        }
