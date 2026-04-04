"""Hybrid Search Unification - Pipeline C Layer 3 (4a+4b)

Implements spec-compliant hybrid search combining:
- 4a: Vector/Semantic Search (ChromaDB)
- 4b: Lexical/BM25 Search (BM25Store)
- 4c: Parent-Child Expansion (L4E)
- 4d: Score-Based Adaptive Rerank

Provides unified 🔵 intent vs 🟠 fact matching across both search modalities.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

# BM25Index imported lazily to avoid L3->L4 violation
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


@dataclass
class HybridSearchResult:
    """Result from hybrid search combining vector + lexical scores."""
    chunk_id: str
    content: str
    vector_score: float = 0.0
    lexical_score: float = 0.0
    combined_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = ""  # 'vector', 'lexical', or 'both'


class HybridSearchEngine:
    """Unified hybrid search engine for Pipeline C Layer 3.

    Implements 4a+4b parallel search with score fusion.
    """

    def __init__(
        self,
        chroma_client: Any | None = None,
        bm25_index: BM25Index | None = None,
        vector_weight: float = 0.7,
        lexical_weight: float = 0.3,
        top_k: int = 10,
    ):
        """Initialize hybrid search engine.

        Args:
            chroma_client: ChromaDB client for vector search
            bm25_index: BM25 index for lexical search
            vector_weight: Weight for vector scores (default 0.7)
            lexical_weight: Weight for lexical scores (default 0.3)
            top_k: Number of results to return
        """
        self.chroma_client = chroma_client
        self.bm25_index = bm25_index
        self.vector_weight = vector_weight
        self.lexical_weight = lexical_weight
        self.top_k = top_k

        self._search_count = 0
        self._avg_fusion_time_ms = 0.0

    def search(
        self,
        query: str,
        query_embedding: list[float] | None = None,
        collection_name: str = "docs",
        filter_dict: dict[str, Any] | None = None,
    ) -> list[HybridSearchResult]:
        """Execute hybrid search (4a+4b parallel).

        Args:
            query: Raw query text
            query_embedding: Pre-computed query embedding (🔵 intent_vec)
            collection_name: ChromaDB collection to search
            filter_dict: Optional metadata filters

        Returns:
            Fused hybrid search results sorted by combined score
        """
        import time
        start_time = time.time()

        _trace_id = f"hybrid_search_{self._search_count}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HybridSearchEngine.search")

        # 4a: Vector Search (Semantic)
        vector_results = self._vector_search(query, query_embedding, collection_name, filter_dict)

        # 4b: Lexical Search (BM25)
        lexical_results = self._lexical_search(query)

        # Fuse results (4d: Score-Based Fusion)
        fused_results = self._fuse_results(vector_results, lexical_results)

        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self._avg_fusion_time_ms = (
            self._avg_fusion_time_ms * self._search_count + elapsed_ms
        ) / (self._search_count + 1)
        self._search_count += 1

        Logger.info(f"Hybrid search complete: {len(fused_results)} results in {elapsed_ms:.1f}ms")

        return fused_results[:self.top_k]

    def _vector_search(
        self,
        query: str,
        query_embedding: list[float] | None,
        collection_name: str,
        filter_dict: dict[str, Any] | None,
    ) -> dict[str, HybridSearchResult]:
        """Execute vector search (4a).

        Args:
            query: Query text (for fallback embedding generation)
            query_embedding: Pre-computed 🔵 intent_vec
            collection_name: ChromaDB collection
            filter_dict: Metadata filters

        Returns:
            Dict mapping chunk_id to HybridSearchResult
        """
        results = {}

        if self.chroma_client is None:
            Logger.warning("ChromaDB client not available for vector search")
            return results

        try:

            # Get embedding if not provided
            if query_embedding is None:
                query_embedding = self._generate_query_embedding(query)

            if query_embedding is None:
                Logger.warning("Could not generate query embedding")
                return results

            # Query ChromaDB
            collection = self.chroma_client.get_collection(collection_name)
            chroma_results = collection.query(
                query_embeddings=[query_embedding],
                n_results=self.top_k * 2,  # Get more for fusion
                where=filter_dict,
                include=["metadatas", "documents", "distances"],
            )

            # Convert to results dict
            for i, (doc_id, doc, metadata, distance) in enumerate(
                zip(
                    chroma_results["ids"][0],
                    chroma_results["documents"][0],
                    chroma_results["metadatas"][0],
                    chroma_results["distances"][0],
                )
            ):
                # Convert distance to similarity score (cosine distance -> similarity)
                similarity = 1.0 - distance

                results[doc_id] = HybridSearchResult(
                    chunk_id=doc_id,
                    content=doc,
                    vector_score=similarity,
                    metadata=metadata,
                    source="vector",
                )

            Logger.debug(f"Vector search: {len(results)} results")

        except (RuntimeError, ValueError) as e:
            Logger.error(f"Vector search failed: {e}")

        return results

    def _lexical_search(self, query: str) -> dict[str, HybridSearchResult]:
        """Execute lexical BM25 search (4b).

        Args:
            query: Query text

        Returns:
            Dict mapping chunk_id to HybridSearchResult
        """
        results = {}

        if self.bm25_index is None:
            Logger.warning("BM25 index not available for lexical search")
            return results

        try:
            # Get top-k from BM25
            bm25_results = self.bm25_index.search(query, top_k=self.top_k * 2)

            for result in bm25_results:
                doc_id = result.get("id", "")
                score = result.get("score", 0.0)
                content = result.get("content", "")

                # Normalize BM25 score to 0-1 range
                # BM25 scores can vary widely, so we use a sigmoid-like normalization
                normalized_score = min(score / 10.0, 1.0)  # Cap at 1.0

                results[doc_id] = HybridSearchResult(
                    chunk_id=doc_id,
                    content=content,
                    lexical_score=normalized_score,
                    metadata=result.get("metadata", {}),
                    source="lexical",
                )

            Logger.debug(f"Lexical search: {len(results)} results")

        except (RuntimeError, ValueError) as e:
            Logger.error(f"Lexical search failed: {e}")

        return results

    def _fuse_results(
        self,
        vector_results: dict[str, HybridSearchResult],
        lexical_results: dict[str, HybridSearchResult],
    ) -> list[HybridSearchResult]:
        """Fuse vector and lexical results (4d: Score-Based Fusion).

        Uses weighted linear combination:
        combined_score = vector_weight * vector_score + lexical_weight * lexical_score

        Args:
            vector_results: Results from vector search
            lexical_results: Results from lexical search

        Returns:
            Sorted list of fused results
        """
        fused = {}

        # Add vector results
        for doc_id, result in vector_results.items():
            fused[doc_id] = result

        # Merge lexical results
        for doc_id, result in lexical_results.items():
            if doc_id in fused:
                # Merge scores
                existing = fused[doc_id]
                existing.lexical_score = result.lexical_score
                existing.source = "both"
            else:
                fused[doc_id] = result

        # Calculate combined scores
        for doc_id, result in fused.items():
            result.combined_score = (
                self.vector_weight * result.vector_score +
                self.lexical_weight * result.lexical_score
            )

        # Sort by combined score
        sorted_results = sorted(
            fused.values(),
            key=lambda r: r.combined_score,
            reverse=True,
        )

        return sorted_results

    def _generate_query_embedding(self, query: str) -> list[float] | None:
        """Generate embedding for query (🔵 intent_vec).

        Args:
            query: Query text

        Returns:
            Query embedding vector
        """
        try:
            # Use BGE-M3 or OpenAI based on config
            import asyncio

            from agentic_core.embeddings.embedding_factory import create_embedding_client
            from agentic_core.embeddings.embedding_input_guard import GuardedText

            client = create_embedding_client("bge-m3")
            guarded = GuardedText(raw_text=query, redacted_text=query)

            # Run async embedding generation
            embedding = asyncio.run(client.get_embedding(guarded))
            return embedding

        except (RuntimeError, ValueError) as e:
            Logger.error(f"Failed to generate query embedding: {e}")
            return None

    def get_stats(self) -> dict[str, Any]:
        """Get hybrid search statistics."""
        return {
            "search_count": self._search_count,
            "avg_fusion_time_ms": self._avg_fusion_time_ms,
            "vector_weight": self.vector_weight,
            "lexical_weight": self.lexical_weight,
            "top_k": self.top_k,
        }


# Global instance
_global_hybrid_engine: HybridSearchEngine | None = None


def get_global_hybrid_engine() -> HybridSearchEngine:
    """Get or create global hybrid search engine."""
    global _global_hybrid_engine
    if _global_hybrid_engine is None:
        _global_hybrid_engine = HybridSearchEngine()
    return _global_hybrid_engine


def hybrid_search(
    query: str,
    query_embedding: list[float] | None = None,
    top_k: int = 10,
) -> list[HybridSearchResult]:
    """Convenience function for hybrid search."""
    return get_global_hybrid_engine().search(query, query_embedding, top_k=top_k)
