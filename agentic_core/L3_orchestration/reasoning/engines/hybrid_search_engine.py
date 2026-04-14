"""Hybrid Search Unification - Pipeline C Layer 3 (4a+4b)

Implements spec-compliant hybrid search combining:
- 4a: Vector/Semantic Search (ChromaDB)
- 4b: Lexical/BM25 Search (BM25Store)
- 4c: Parent-Child Expansion (L4E)
- 4d: Score-Based Adaptive Rerank

Provides unified 🔵 intent vs 🟠 fact matching across both search modalities.
"""

from __future__ import annotations

import glob
import logging
import re as _re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tqdm import tqdm

try:
    from agentic_core.embeddings.bge_runtime import BGEInstallError as _BGEInstallError
except ImportError:
    _BGEInstallError = RuntimeError  # type: ignore[assignment,misc]

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)
from agentic_core.L4_state.utils.memory.bm25_store import SparseIndex, get_sparse_index
from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
    EvidenceBundle,
    EvidenceShaper,
)

Logger = logging.getLogger(__name__)


def _resolve_adg_path() -> str:
    """Resolve the latest ADG SQLite snapshot dynamically."""
    candidates = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
    return candidates[-1] if candidates else "artifacts/adg/adg_indexed_latest.sqlite"


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
        bm25_index: SparseIndex | None = None,
        vector_weight: float = 0.7,
        lexical_weight: float = 0.3,
        top_k: int = 10,
        adg_db_path: str | None = None,
    ):
        """Initialize hybrid search engine.

        Args:
            chroma_client: ChromaDB client for vector search
            bm25_index: SparseIndex (persistent FTS5 sidecar) for lexical search
            vector_weight: Base weight for vector scores (0.7); overridden by signal detection
            lexical_weight: Base weight for lexical scores (0.3); overridden by signal detection
            top_k: Number of results to return
            adg_db_path: Path to ADG SQLite database for structural queries
        """
        self.chroma_client = chroma_client
        self.bm25_index = bm25_index  # SparseIndex | None
        self.vector_weight = vector_weight
        self.lexical_weight = lexical_weight
        self.top_k = top_k

        self._search_count = 0
        self._avg_fusion_time_ms = 0.0

        # ADG SQLite connection for structural queries
        self.adg_db_path = adg_db_path or _resolve_adg_path()
        self._adg_conn: sqlite3.Connection | None = None

    def search(
        self,
        query: str,
        query_embedding: list[float] | None = None,
        collection_name: str = "code_chunks",
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

        # Phase B2: dynamic weight selection based on query signal
        vw, lw = _compute_weights(query, self.vector_weight, self.lexical_weight)

        # 4a: Vector Search (Semantic)
        vector_results = self._vector_search(query, query_embedding, collection_name, filter_dict)

        # 4b: Lexical Search — persistent FTS5 sidecar for this collection
        lexical_results = self._lexical_search(query, collection_name)

        # Fuse results (4d: Score-Based Fusion) with dynamic weights
        fused_results = self._fuse_results(vector_results, lexical_results, vw, lw)

        # Apply governance filters
        if governance_filter:
            fused_results = self._apply_governance_filters(fused_results, governance_filter)

        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self._avg_fusion_time_ms = (self._avg_fusion_time_ms * self._search_count + elapsed_ms) / (
            self._search_count + 1
        )
        self._search_count += 1

        Logger.info(f"Hybrid search complete: {len(fused_results)} results in {elapsed_ms:.1f}ms")

        return fused_results[: self.top_k]

    def shape_search(
        self,
        query: str,
        query_embedding: list[float] | None = None,
        collection_name: str = "code_chunks",
        filter_dict: dict[str, Any] | None = None,
        governance_filter: dict[str, Any] | None = None,
    ) -> EvidenceBundle:
        """Hybrid search + C0 evidence shaping in one call.

        Returns an EvidenceBundle instead of a raw list.  Backward compatibility:
        callers that need list[HybridSearchResult] can read .ranked_chunks.

        Adds on top of search():
          - digest-based deduplication
          - exact-match winner preservation
          - sibling expansion (chunk_index ± 1) where metadata supports it
          - contradiction detection and flagging
          - citation anchor generation
          - heuristic rerank by signal-weighted composite score
        """
        raw = self.search(
            query,
            query_embedding=query_embedding,
            collection_name=collection_name,
            filter_dict=filter_dict,
            governance_filter=governance_filter,
        )
        shaper = EvidenceShaper()
        return shaper.shape(query, raw, collection_name, self.chroma_client)

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
                tqdm(
                    zip(
                        chroma_results["ids"][0],
                        chroma_results["documents"][0],
                        chroma_results["metadatas"][0],
                        chroma_results["distances"][0],
                    ),
                    desc="vector-results",
                    leave=False,
                    disable=True,
                ),
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

    def _lexical_search(
        self, query: str, collection_name: str = "code_chunks"
    ) -> dict[str, HybridSearchResult]:
        """Execute lexical FTS5 search against the persistent sidecar (4b).

        Resolves the correct SparseIndex for *collection_name* — either from
        self.bm25_index (if explicitly provided) or via get_sparse_index().
        Falls back silently for collections without a sidecar.

        Args:
            query: Query text
            collection_name: Canonical collection name (selects sidecar DB)

        Returns:
            Dict mapping chunk_id to HybridSearchResult with lexical_score set
        """
        results: dict[str, HybridSearchResult] = {}

        # Resolve the sparse index: explicit arg wins, else look up sidecar by collection
        sparse: SparseIndex | None = self.bm25_index or get_sparse_index(collection_name)

        if sparse is None or not sparse.is_available:
            Logger.debug("No sparse sidecar for collection '%s' — sparse leg skipped", collection_name)
            return results

        try:
            fts_results = sparse.search(query, top_k=self.top_k * 2)

            for item in tqdm(fts_results, desc="Processing", unit="item"):
                doc_id = item.get("id", "")
                if not doc_id:
                    continue
                # SparseIndex already normalises score to (0, 1] via 1/(1+rank)
                score = float(item.get("score", 0.0))
                results[doc_id] = HybridSearchResult(
                    chunk_id=doc_id,
                    content=item.get("content", ""),
                    lexical_score=score,
                    metadata=item.get("metadata", {}),
                    source="lexical",
                )

            Logger.debug("Lexical search [%s]: %d results", collection_name, len(results))

        except (sqlite3.OperationalError, ValueError) as e:
            Logger.error("Lexical search failed for '%s': %s", collection_name, e)

        return results

    def _fuse_results(
        self,
        vector_results: dict[str, HybridSearchResult],
        lexical_results: dict[str, HybridSearchResult],
        vector_weight: float | None = None,
        lexical_weight: float | None = None,
    ) -> list[HybridSearchResult]:
        """Fuse vector and lexical results (4d: Score-Based Fusion).

        Uses weighted linear combination with dynamically chosen weights:
        combined_score = vector_weight * vector_score + lexical_weight * lexical_score

        Args:
            vector_results: Results from vector search
            lexical_results: Results from lexical search
            vector_weight: Override from signal detection (falls back to self.vector_weight)
            lexical_weight: Override from signal detection (falls back to self.lexical_weight)

        Returns:
            Sorted list of fused results
        """
        vw = vector_weight if vector_weight is not None else self.vector_weight
        lw = lexical_weight if lexical_weight is not None else self.lexical_weight

        fused: dict[str, HybridSearchResult] = {}

        # Add vector results
        for doc_id, result in vector_results.items():
            fused[doc_id] = result

        # Merge lexical results
        for doc_id, result in lexical_results.items():
            if doc_id in fused:
                existing = fused[doc_id]
                existing.lexical_score = result.lexical_score
                existing.source = "both"
            else:
                fused[doc_id] = result

        # Calculate combined scores using resolved weights
        for result in fused.values():
            result.combined_score = vw * result.vector_score + lw * result.lexical_score

        # Sort by combined score
        return sorted(fused.values(), key=lambda r: r.combined_score, reverse=True)

    def _generate_query_embedding(self, query: str) -> list[float] | None:
        """Generate embedding for query (🔵 intent_vec) using BAAI/bge-m3 (1024-dim).

        Delegates to the shared process-level singleton in bge_runtime.
        RuntimeError(BGE_DIM_MISMATCH) propagates — never swallowed silently.

        Args:
            query: Query text

        Returns:
            Query embedding vector (1024-dim, L2-normalised), or None on install failure
        """
        try:
            from agentic_core.embeddings.bge_runtime import bge_embed_query

            return bge_embed_query(query)
        except (_BGEInstallError, ImportError) as e:
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
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                Logger.error(f"Failed to connect to ADG database: {e}")
                raise  # Re-raise to surface connection errors
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
        self,
        results: list[HybridSearchResult],
        filters: dict[str, Any],
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

        for result in tqdm(results, desc="filter-results", leave=False, disable=True):
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

    def get_chunks_by_adg_node(
        self, adg_node_id: int, collection_name: str = "repo_code_chunks"
    ) -> list[HybridSearchResult]:
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
                        ),
                    )

            Logger.info(f"Found {len(chunks)} chunks for ADG node {adg_node_id}")
            return chunks

        except Exception as e:
            Logger.error(f"Failed to get chunks by ADG node: {e}")
            return []

    def get_related_chunks(
        self, chunk_id: str, relation_type: str = "calls", limit: int = 10
    ) -> list[HybridSearchResult]:
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
                chunks = self.get_chunks_by_adg_node(
                    node["src_id"] if relation_type in ["calls", "imports"] else node["dst_id"]
                )
                related_chunks.extend(chunks)

            return related_chunks[:limit]

        except Exception as e:
            Logger.error(f"Failed to get related chunks: {e}")
            return []

    def expand_results_with_adg(
        self,
        results: list[HybridSearchResult],
        relation_types: list[str] = ["calls"],
        limit_per_relation: int = 3,
    ) -> list[HybridSearchResult]:
        """Expand search results with ADG-related chunks.

        Args:
            results: Original search results
            relation_types: ADG relation types to traverse
            limit_per_relation: Max chunks per relation type

        Returns:
            Expanded results with ADG-related chunks
        """
        expanded_results = list(results)  # Start with original results
        seen_ids = {r.chunk_id for r in results}

        for result in results:
            for relation_type in relation_types:
                related = self.get_related_chunks(result.chunk_id, relation_type, limit_per_relation)
                for chunk in related:
                    if chunk.chunk_id not in seen_ids:
                        # Mark as expanded result
                        chunk.metadata["expanded_via"] = f"adg_{relation_type}"
                        chunk.metadata["expanded_from"] = result.chunk_id
                        expanded_results.append(chunk)
                        seen_ids.add(chunk.chunk_id)

        if len(expanded_results) > len(results):
            Logger.info(f"ADG expansion: {len(results)} -> {len(expanded_results)} results")

        return expanded_results

    def expand_results_with_parent_child(
        self,
        results: list[HybridSearchResult],
        max_depth: int = 1,
    ) -> list[HybridSearchResult]:
        """Expand search results using parent-child relationships from metadata.

        Args:
            results: Original search results
            max_depth: Maximum expansion depth (1 = direct parent/child only)

        Returns:
            Expanded results with parent/child chunks
        """
        if self.chroma_client is None:
            Logger.warning("ChromaDB client not available for parent-child expansion")
            return results

        expanded_results = list(results)
        seen_ids = {r.chunk_id for r in results}

        try:
            collection = self.chroma_client.get_collection("repo_code_chunks")

            for result in tqdm(results, desc="expand-parents", leave=False, disable=True):
                parent_id = result.metadata.get("parent_id")
                chunk_id = result.chunk_id

                # Expand to parent
                if parent_id and parent_id not in seen_ids:
                    parent_results = collection.get(ids=[parent_id])
                    if parent_results["ids"]:
                        parent_chunk = HybridSearchResult(
                            chunk_id=parent_id,
                            content=parent_results["documents"][0],
                            metadata=parent_results["metadatas"][0],
                            source="parent_expansion",
                        )
                        parent_chunk.metadata["expanded_via"] = "parent_child"
                        parent_chunk.metadata["expanded_from"] = chunk_id
                        expanded_results.append(parent_chunk)
                        seen_ids.add(parent_id)

                # Expand to children (find chunks with this as parent)
                if max_depth > 0:
                    # Query for chunks where parent_id matches this chunk_id
                    child_results = collection.query(
                        query_texts=[""],
                        n_results=50,
                        where={"parent_id": chunk_id},
                    )

                    if child_results["ids"] and child_results["ids"][0]:
                        for i, child_id in enumerate(
                            tqdm(child_results["ids"][0], desc="expand-children", leave=False, disable=True)
                        ):
                            if child_id not in seen_ids:
                                child_chunk = HybridSearchResult(
                                    chunk_id=child_id,
                                    content=child_results["documents"][0][i],
                                    metadata=child_results["metadatas"][0][i],
                                    source="child_expansion",
                                )
                                child_chunk.metadata["expanded_via"] = "parent_child"
                                child_chunk.metadata["expanded_from"] = chunk_id
                                expanded_results.append(child_chunk)
                                seen_ids.add(child_id)

            if len(expanded_results) > len(results):
                Logger.info(f"Parent-child expansion: {len(results)} -> {len(expanded_results)} results")

            return expanded_results

        except Exception as e:
            Logger.error(f"Parent-child expansion failed: {e}")
            return results

    def enforce_context_budget(
        self,
        results: list[HybridSearchResult],
        max_tokens: int = 4000,
        avg_tokens_per_chunk: int = 100,
    ) -> list[HybridSearchResult]:
        """Enforce context budget by limiting number of chunks.

        Args:
            results: Search results to filter
            max_tokens: Maximum token budget
            avg_tokens_per_chunk: Average tokens per chunk (default 100)

        Returns:
            Filtered results within token budget
        """
        if avg_tokens_per_chunk <= 0:
            raise ValueError(f"avg_tokens_per_chunk must be positive, got {avg_tokens_per_chunk}")

        max_chunks = max_tokens // avg_tokens_per_chunk

        if len(results) <= max_chunks:
            return results

        # Sort by combined score (higher is better)
        sorted_results = sorted(results, key=lambda r: r.combined_score, reverse=True)

        # Keep top-k results
        filtered = sorted_results[:max_chunks]

        Logger.info(
            f"Context budget enforcement: {len(results)} -> {len(filtered)} chunks "
            f"(budget: {max_tokens} tokens, max_chunks: {max_chunks})",
        )

        return filtered


# ---------------------------------------------------------------------------
# Phase B2 — dynamic weight selection
# ---------------------------------------------------------------------------

# Patterns that indicate an exact-match / lexical-dominant query
_QUOTED_PHRASE_RE = _re.compile(r'"[^"]+"|\u2018[^\u2019]+\u2019')
_SNAKE_CASE_RE = _re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+){1,}\b")
_CAMEL_CASE_RE = _re.compile(r"\b[A-Z][a-zA-Z0-9]+[A-Z][a-zA-Z0-9]*\b|\b[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]*\b")
_DOTTED_PATH_RE = _re.compile(r"\b(?:[a-zA-Z_][a-zA-Z0-9_]*\.){2,}[a-zA-Z_][a-zA-Z0-9_]*\b")
_HASH_ID_RE = _re.compile(r"\b[0-9a-f]{7,40}\b|\b[A-Z][A-Z0-9_]{3,}\b")
_SECTION_RE = _re.compile(r"\b(?:§|section|enum|phase|ADR|L[0-9])[\s\-]?[0-9A-Z]", _re.IGNORECASE)


def _detect_query_signal(query: str) -> str:
    """Return 'exact', 'semantic', or 'mixed' based on observable query features.

    Exact-match signals (sparse should dominate):
    - Quoted phrases
    - snake_case / CamelCase identifiers
    - Dotted import paths (a.b.c)
    - Hashes / UPPER_CONST slugs
    - Section numbers / enum names / ADR references

    Semantic signals (dense should dominate):
    - Long natural-language sentences (>8 words, no exact signals)
    """
    signals = 0
    if _QUOTED_PHRASE_RE.search(query):
        signals += 2
    if _SNAKE_CASE_RE.search(query):
        signals += 2
    if _CAMEL_CASE_RE.search(query):
        signals += 2  # CamelCase identifiers are unambiguous exact-match signals
    if _DOTTED_PATH_RE.search(query):
        signals += 2
    if _HASH_ID_RE.search(query):
        signals += 1
    if _SECTION_RE.search(query):
        signals += 1

    word_count = len(query.split())
    is_long_prose = word_count > 8 and signals == 0

    if signals >= 2:
        return "exact"
    if is_long_prose:
        return "semantic"
    return "mixed"


# Weight table by signal type
#   exact  → sparse-dominant  (sparse 0.65, dense 0.35)
#   mixed  → balanced         (sparse 0.45, dense 0.55)
#   semantic → dense-dominant (sparse 0.15, dense 0.85)
_WEIGHT_TABLE: dict[str, tuple[float, float]] = {
    "exact": (0.35, 0.65),  # (vector_weight, lexical_weight)
    "mixed": (0.55, 0.45),
    "semantic": (0.85, 0.15),
}


def _compute_weights(
    query: str,
    base_vector: float,
    base_lexical: float,
) -> tuple[float, float]:
    """Return (vector_weight, lexical_weight) for this query.

    Uses dynamic signal detection; falls back to caller-supplied base weights
    when the engine has no sparse index (graceful degradation).
    """
    signal = _detect_query_signal(query)
    vw, lw = _WEIGHT_TABLE.get(signal, (base_vector, base_lexical))
    Logger.debug("Query signal=%s → vw=%.2f lw=%.2f  query=%r", signal, vw, lw, query[:60])
    return vw, lw


# ---------------------------------------------------------------------------
# Global factories
# ---------------------------------------------------------------------------

# Global instance per-collection (keyed so different collections get distinct engines)
_engine_cache: dict[str, HybridSearchEngine] = {}

# Canonical BGE store — same path used by ingest_code_chunks.py and SemanticRetriever
_CANONICAL_CHROMA_PATH = str(Path(__file__).resolve().parents[4] / "data" / "cache" / "chromadb")


def get_global_hybrid_engine(collection_name: str = "code_chunks") -> HybridSearchEngine:
    """Get or create a hybrid search engine for *collection_name*.

    Sparse leg is wired automatically via get_sparse_index() when a sidecar exists.
    Sparse leg is silently absent for collections without a built sidecar.
    """
    if collection_name not in _engine_cache:
        try:
            import chromadb as _chromadb

            _chroma_client = _chromadb.PersistentClient(path=_CANONICAL_CHROMA_PATH)
        except (
            Exception
        ):  # guardian: allow-broad-exception -- best-effort client init, falls back to vector-disabled mode
            _chroma_client = None

        sparse = get_sparse_index(collection_name)  # None for unsupported collections
        _engine_cache[collection_name] = HybridSearchEngine(
            chroma_client=_chroma_client,
            bm25_index=sparse,
        )
        Logger.info(
            "HybridSearchEngine created: collection=%s sparse=%s",
            collection_name,
            "yes" if (sparse and sparse.is_available) else "no",
        )
    return _engine_cache[collection_name]


def hybrid_search(
    query: str,
    query_embedding: list[float] | None = None,
    collection_name: str = "code_chunks",
) -> list[HybridSearchResult]:
    """Convenience function for hybrid search against the collection-aware cached engine."""
    return get_global_hybrid_engine(collection_name).search(query, query_embedding, collection_name)


def shaped_hybrid_search(
    query: str,
    query_embedding: list[float] | None = None,
    collection_name: str = "code_chunks",
) -> EvidenceBundle:
    """Hybrid search + C0 evidence shaping. Returns EvidenceBundle.

    The primary entry point for callers that want citation anchors, provenance,
    contradiction flags, and heuristic rerank on top of the dense+sparse fusion.
    """
    return get_global_hybrid_engine(collection_name).shape_search(query, query_embedding, collection_name)


def get_hybrid_search_engine(
    collection_name: str = "code_chunks",
    vector_weight: float = 0.7,
    lexical_weight: float = 0.3,
    top_k: int = 10,
) -> HybridSearchEngine:
    """Return a HybridSearchEngine wired to the canonical Chroma store and sparse sidecar."""
    import chromadb as _chromadb

    client = _chromadb.PersistentClient(path=_CANONICAL_CHROMA_PATH)
    sparse = get_sparse_index(collection_name)  # None for unsupported collections
    return HybridSearchEngine(
        chroma_client=client,
        bm25_index=sparse,
        vector_weight=vector_weight,
        lexical_weight=lexical_weight,
        top_k=top_k,
    )
