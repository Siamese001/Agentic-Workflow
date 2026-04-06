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
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# BM25Index imported lazily to avoid L3->L4 violation
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
        adg_db_path: str | None = None,
    ):
        """Initialize hybrid search engine.

        Args:
            chroma_client: ChromaDB client for vector search
            bm25_index: BM25 index for lexical search
            vector_weight: Weight for vector scores (default 0.7)
            lexical_weight: Weight for lexical scores (default 0.3)
            top_k: Number of results to return
            adg_db_path: Path to ADG SQLite database for structural queries
        """
        self.chroma_client = chroma_client
        self.bm25_index = bm25_index
        self.vector_weight = vector_weight
        self.lexical_weight = lexical_weight
        self.top_k = top_k

        self._search_count = 0
        self._avg_fusion_time_ms = 0.0

        # ADG SQLite connection for structural queries
        self.adg_db_path = adg_db_path or "artifacts/adg/adg_indexed_04062026_1246.sqlite"
        self._adg_conn: sqlite3.Connection | None = None

    def search(
        self,
        query: str,
        query_embedding: list[float] | None = None,
        collection_name: str = "docs",
        filter_dict: dict[str, Any] | None = None,
        governance_filter: dict[str, Any] | None = None,
    ) -> list[HybridSearchResult]:
        """Execute hybrid search (4a+4b parallel).

        Args:
            query: Raw query text
            query_embedding: Pre-computed query embedding (🔵 intent_vec)
            collection_name: ChromaDB collection to search
            filter_dict: Optional metadata filters
            governance_filter: Optional ADG governance filters
                - exclude_violations: bool - exclude nodes with violations
                - layers: list[str] - only include specific layers
                - entity_types: list[str] - only include specific entity types

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

        # Apply governance filters
        if governance_filter:
            fused_results = self._apply_governance_filters(fused_results, governance_filter)

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

    def _get_adg_connection(self) -> sqlite3.Connection | None:
        """Get ADG SQLite connection (lazy initialization)."""
        if self._adg_conn is None:
            try:
                db_path = Path(self.adg_db_path)
                if db_path.exists():
                    self._adg_conn = sqlite3.connect(str(db_path))
                    self._adg_conn.row_factory = sqlite3.Row
                    Logger.info(f"ADG SQLite connection established: {self.adg_db_path}")
                else:
                    Logger.warning(f"ADG database not found: {self.adg_db_path}")
            except Exception as e:
                Logger.error(f"Failed to connect to ADG database: {e}")
        return self._adg_conn

    def close_adg_connection(self) -> None:
        """Close ADG SQLite connection."""
        if self._adg_conn is not None:
            self._adg_conn.close()
            self._adg_conn = None
            Logger.info("ADG SQLite connection closed")

    def get_callers(self, node_id: int, limit: int = 30) -> list[dict[str, Any]]:
        """Get nodes that call this node via 'calls' edges (fan-in).

        Args:
            node_id: ADG node ID
            limit: Maximum results

        Returns:
            List of caller nodes with metadata
        """
        conn = self._get_adg_connection()
        if not conn:
            return []

        try:
            cur = conn.execute(
                """SELECT src_id, n.adg_name, n.resolved_path, n.entity_type, n.layer
                   FROM edges e
                   JOIN nodes n ON n.id = e.src_id
                   WHERE e.dst_id = ? AND e.relation_type = 'calls'
                   LIMIT ?""",
                (node_id, limit),
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            Logger.error(f"ADG query failed (get_callers): {e}")
            return []

    def get_callees(self, node_id: int, limit: int = 30) -> list[dict[str, Any]]:
        """Get nodes called by this node via 'calls' edges (fan-out).

        Args:
            node_id: ADG node ID
            limit: Maximum results

        Returns:
            List of callee nodes with metadata
        """
        conn = self._get_adg_connection()
        if not conn:
            return []

        try:
            cur = conn.execute(
                """SELECT dst_id, n.adg_name, n.resolved_path, n.entity_type, n.layer
                   FROM edges e
                   JOIN nodes n ON n.id = e.dst_id
                   WHERE e.src_id = ? AND e.relation_type = 'calls'
                   LIMIT ?""",
                (node_id, limit),
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            Logger.error(f"ADG query failed (get_callees): {e}")
            return []

    def get_importers(self, node_id: int, limit: int = 30) -> list[dict[str, Any]]:
        """Get nodes that import this node via 'imports' edges (fan-in).

        Args:
            node_id: ADG node ID
            limit: Maximum results

        Returns:
            List of importer nodes with metadata
        """
        conn = self._get_adg_connection()
        if not conn:
            return []

        try:
            cur = conn.execute(
                """SELECT src_id, n.adg_name, n.resolved_path, n.entity_type, n.layer
                   FROM edges e
                   JOIN nodes n ON n.id = e.src_id
                   WHERE e.dst_id = ? AND e.relation_type = 'imports'
                   LIMIT ?""",
                (node_id, limit),
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            Logger.error(f"ADG query failed (get_importers): {e}")
            return []

    def get_imports(self, node_id: int, limit: int = 30) -> list[dict[str, Any]]:
        """Get nodes imported by this node via 'imports' edges (fan-out).

        Args:
            node_id: ADG node ID
            limit: Maximum results

        Returns:
            List of imported nodes with metadata
        """
        conn = self._get_adg_connection()
        if not conn:
            return []

        try:
            cur = conn.execute(
                """SELECT dst_id, n.adg_name, n.resolved_path, n.entity_type, n.layer
                   FROM edges e
                   JOIN nodes n ON n.id = e.dst_id
                   WHERE e.src_id = ? AND e.relation_type = 'imports'
                   LIMIT ?""",
                (node_id, limit),
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            Logger.error(f"ADG query failed (get_imports): {e}")
            return []

    def get_violations(self, node_id: int) -> list[dict[str, Any]]:
        """Get governance violations for this node.

        Args:
            node_id: ADG node ID

        Returns:
            List of violation edges with metadata
        """
        conn = self._get_adg_connection()
        if not conn:
            return []

        try:
            cur = conn.execute(
                """SELECT e.relation_type, n_dst.adg_name as target_name, n_dst.resolved_path
                   FROM edges e
                   JOIN nodes n_dst ON n_dst.id = e.dst_id
                   WHERE e.src_id = ? AND e.relation_type IN ('violates', 'gravity_violates')""",
                (node_id,),
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            Logger.error(f"ADG query failed (get_violations): {e}")
            return []

    def _apply_governance_filters(
        self, results: list[HybridSearchResult], filters: dict[str, Any]
    ) -> list[HybridSearchResult]:
        """Apply ADG governance filters to search results.

        Args:
            results: Fused hybrid search results
            filters: Governance filter dict
                - exclude_violations: bool - exclude nodes with violations
                - layers: list[str] - only include specific layers
                - entity_types: list[str] - only include specific entity types

        Returns:
            Filtered results
        """
        filtered_results = []

        for result in results:
            metadata = result.metadata
            should_include = True

            # Filter by layer
            if filters.get("layers"):
                result_layer = metadata.get("layer", "Unknown")
                if result_layer not in filters["layers"]:
                    should_include = False

            # Filter by entity type
            if filters.get("entity_types"):
                result_entity = metadata.get("entity_type", "unknown")
                if result_entity not in filters["entity_types"]:
                    should_include = False

            # Exclude nodes with violations
            if filters.get("exclude_violations"):
                adg_node_id = metadata.get("adg_node_id")
                if adg_node_id:
                    violations = self.get_violations(adg_node_id)
                    if violations:
                        should_include = False

            if should_include:
                filtered_results.append(result)

        if len(filtered_results) < len(results):
            Logger.info(f"Governance filters reduced results from {len(results)} to {len(filtered_results)}")

        return filtered_results

    def get_node_by_id(self, node_id: int) -> dict[str, Any] | None:
        """Get ADG node by ID.

        Args:
            node_id: ADG node ID

        Returns:
            Node dict or None
        """
        conn = self._get_adg_connection()
        if not conn:
            return None

        try:
            cur = conn.execute(
                """SELECT id, adg_name, resolved_path, entity_type, layer, territory
                   FROM nodes WHERE id = ?""",
                (node_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
        except Exception as e:
            Logger.error(f"ADG query failed (get_node_by_id): {e}")
            return None

    def get_chunks_by_adg_node(self, adg_node_id: int, collection_name: str = "repo_code_chunks") -> list[HybridSearchResult]:
        """Get ChromaDB chunks for a specific ADG node ID.

        Args:
            adg_node_id: ADG node ID
            collection_name: ChromaDB collection name

        Returns:
            List of HybridSearchResult for matching chunks
        """
        if self.chroma_client is None:
            Logger.warning("ChromaDB client not available")
            return []

        try:
            collection = self.chroma_client.get_collection(collection_name)
            results = collection.query(
                query_texts=[""],  # Empty query, filter only
                n_results=100,
                where={"adg_node_id": adg_node_id},
            )

            chunks = []
            if results["ids"] and results["ids"][0]:
                for i, chunk_id in enumerate(results["ids"][0]):
                    chunks.append(
                        HybridSearchResult(
                            chunk_id=chunk_id,
                            content=results["documents"][0][i],
                            metadata=results["metadatas"][0][i],
                            source="chromadb",
                        )
                    )

            Logger.info(f"Found {len(chunks)} chunks for ADG node {adg_node_id}")
            return chunks

        except Exception as e:
            Logger.error(f"Failed to get chunks by ADG node: {e}")
            return []

    def get_related_chunks(self, chunk_id: str, relation_type: str = "calls", limit: int = 10) -> list[HybridSearchResult]:
        """Get chunks related to a given chunk via ADG structural relationships.

        Args:
            chunk_id: ChromaDB chunk ID
            relation_type: ADG relation type (calls, imports, etc.)
            limit: Maximum results

        Returns:
            List of related HybridSearchResult
        """
        if self.chroma_client is None:
            Logger.warning("ChromaDB client not available")
            return []

        conn = self._get_adg_connection()
        if not conn:
            return []

        try:
            # Get the chunk's metadata to find ADG node ID
            collection = self.chroma_client.get_collection("repo_code_chunks")
            chunk_results = collection.get(ids=[chunk_id])

            if not chunk_results["ids"]:
                Logger.warning(f"Chunk {chunk_id} not found in ChromaDB")
                return []

            metadata = chunk_results["metadatas"][0]
            adg_node_id = metadata.get("adg_node_id")

            if not adg_node_id:
                Logger.warning(f"Chunk {chunk_id} has no ADG node ID")
                return []

            # Query ADG for related nodes
            if relation_type == "calls":
                related_nodes = self.get_callees(adg_node_id, limit)
            elif relation_type == "importers":
                related_nodes = self.get_importers(adg_node_id, limit)
            elif relation_type == "imports":
                related_nodes = self.get_imports(adg_node_id, limit)
            else:
                Logger.warning(f"Unsupported relation type: {relation_type}")
                return []

            # Get chunks for related nodes
            related_chunks = []
            for node in related_nodes:
                chunks = self.get_chunks_by_adg_node(node["src_id"] if relation_type in ["calls", "imports"] else node["dst_id"])
                related_chunks.extend(chunks)

            return related_chunks[:limit]

        except Exception as e:
            Logger.error(f"Failed to get related chunks: {e}")
            return []


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
