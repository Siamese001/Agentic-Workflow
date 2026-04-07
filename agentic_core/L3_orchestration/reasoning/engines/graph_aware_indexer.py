"""Graph-Aware Indexing Engine for Pipeline B.

Implements spec-compliant graph ingestion from Agentic Retrieval Models v9:
- Phase 1: Graph Ingestion & Indexing (Pipeline B)
- Binds doc_id, source, and crucially: ADG edges (reads_from, writes_to)
- ParentChildIndex (L4E) registry population

Provides integration between:
- ADG static graph edges (REAL - now queries SQLite)
- ChunkManifestRegistry (L4D)
- ParentChildIndexRegistry (L4E)
- Vector DB (ChromaDB) for embeddings
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.reasoning.engines.adg_integration import (
    ADGQueryClient,
    get_global_adg_client,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_pulls_context,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_learning_event,
    _emit_stores_embedding,
    _emit_writes_through,
)

# ChunkManifestRegistry, EnrichedChunkManifest, SemanticEnricher imported lazily to avoid L3->L4 violation

Logger = logging.getLogger(__name__)


@dataclass
class ADGEdgeBinding:
    """ADG edge binding for a chunk.

    Represents the reads_from and writes_to edges from ADG
    that are bound to a document chunk during ingestion.
    """
    chunk_id: str
    source_file: str
    reads_from: list[str] = field(default_factory=list)  # Source entities
    writes_to: list[str] = field(default_factory=list)  # Target entities
    pulls_context: list[str] = field(default_factory=list)  # Context sources

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "reads_from": self.reads_from,
            "writes_to": self.writes_to,
            "pulls_context": self.pulls_context,
        }


@dataclass
class GraphEnrichmentContext:
    """Context for graph-aware enrichment during ingestion."""
    doc_id: str
    source_path: str
    adg_edges: ADGEdgeBinding
    parent_section_id: str | None = None
    sibling_ids: list[str] = field(default_factory=list)
    heading_path: list[str] = field(default_factory=list)


class GraphAwareIndexer:
    """Graph-aware indexing engine for Pipeline B.

    Implements:
    - ADG edge extraction and binding
    - ChunkManifest (L4D) population
    - ParentChildIndex (L4E) registry population
    - Vector DB integration for fact_vec storage
    """

    def __init__(
        self,
        l4d_registry: L4DChunkManifestRegistry | None = None,
        l4e_registry: ParentChildIndexRegistry | None = None,
        chunk_manifest_registry: ChunkManifestRegistry | None = None,
        vector_db_client: Any | None = None,
    ):
        """Initialize graph-aware indexer.

        Args:
            l4d_registry: L4D ChunkManifestRegistry
            l4e_registry: L4E ParentChildIndexRegistry
            chunk_manifest_registry: In-memory ChunkManifestRegistry
            vector_db_client: ChromaDB or similar vector DB client
        """
        self.l4d_registry = l4d_registry or L4DChunkManifestRegistry()
        self.l4e_registry = l4e_registry or ParentChildIndexRegistry()
        self.chunk_manifest_registry = chunk_manifest_registry or ChunkManifestRegistry()
        self.vector_db_client = vector_db_client

        self._indexed_count = 0
        self._edge_bindings: dict[str, ADGEdgeBinding] = {}

    def index_document(
        self,
        doc_id: str,
        source_path: str,
        chunks: list[dict[str, Any]],
        adg_edges: ADGEdgeBinding | None = None,
        embeddings: list[list[float]] | None = None,
    ) -> dict[str, Any]:
        """Index a document with graph-aware metadata.

        Args:
            doc_id: Document identifier (must be non-empty)
            source_path: Source file path (must be non-empty)
            chunks: List of chunk dicts with content, metadata
            adg_edges: ADG edge bindings for this document
            embeddings: Pre-computed embeddings for chunks

        Returns:
            Indexing result with manifest IDs and edge bindings

        Raises:
            ValueError: If doc_id or source_path is empty
        """
        # Input validation
        if not doc_id or not isinstance(doc_id, str):
            raise ValueError(f"Invalid doc_id: {doc_id!r}")
        if not source_path or not isinstance(source_path, str):
            raise ValueError(f"Invalid source_path: {source_path!r}")
        if not isinstance(chunks, list):
            raise ValueError(f"chunks must be a list, got {type(chunks)}")

        # Handle empty chunks gracefully
        if not chunks:
            Logger.warning(f"No chunks to index for doc_id={doc_id}")
            return {
                "doc_id": doc_id,
                "chunks_indexed": 0,
                "manifests_created": [],
                "parent_child_links": [],
                "adg_edges_bound": (adg_edges or ADGEdgeBinding(chunk_id=f"{doc_id}_doc", source_file=source_path)).to_dict(),
            }

        # Validate embeddings length matches chunks
        if embeddings and len(embeddings) != len(chunks):
            Logger.warning(
                f"Embeddings length ({len(embeddings)}) doesn't match chunks ({len(chunks)}). "
                "Ignoring embeddings.",
            )
            embeddings = None

        _trace_id = f"graph_index_{doc_id}"
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "GraphAwareIndexer.index_document",
        )

        results = {
            "doc_id": doc_id,
            "chunks_indexed": 0,
            "manifests_created": [],
            "parent_child_links": [],
            "adg_edges_bound": [],
        }

        # Create or use ADG edge binding
        edges = adg_edges or ADGEdgeBinding(
            chunk_id=f"{doc_id}_doc",
            source_file=source_path,
        )
        self._edge_bindings[doc_id] = edges

        parent_chunk_id: str | None = None

        for idx, chunk_data in enumerate(chunks):
            chunk_id = chunk_data.get("chunk_id") or f"{doc_id}_chunk_{idx}"
            content = chunk_data.get("content", "")
            metadata = chunk_data.get("metadata", {})

            # Create enriched manifest (L4D)
            manifest = self._create_enriched_manifest(
                chunk_id=chunk_id,
                doc_id=doc_id,
                source_path=source_path,
                content=content,
                chunk_index=idx,
                metadata=metadata,
                adg_edges=edges,
                parent_chunk_id=parent_chunk_id,
                embedding=embeddings[idx] if embeddings and idx < len(embeddings) else None,
            )

            # Store in L4D registry
            if self.l4d_registry.store_manifest(manifest):
                results["manifests_created"].append(chunk_id)
                _emit_stores_embedding(_trace_id, chunk_id, manifest.fact_vec_hash or "")

            # Create parent-child link (L4E)
            if parent_chunk_id:
                link = ParentChildLink(
                    child_chunk_id=chunk_id,
                    parent_chunk_id=parent_chunk_id,
                    expansion_policy="default",
                    neighbor_window_ids=tuple(),  # Populated below
                )
                self.l4e_registry.write(link)
                results["parent_child_links"].append((parent_chunk_id, chunk_id))
                _emit_pulls_context(_trace_id, chunk_id, parent_chunk_id)

            # Emit ADG edge signals
            for reads_from in edges.reads_from:
                _emit_reads_through(_trace_id, chunk_id, reads_from)
            for writes_to in edges.writes_to:
                _emit_writes_through(_trace_id, chunk_id, writes_to)

            # Store in vector DB if available
            if self.vector_db_client and manifest.fact_vec:
                self._store_in_vector_db(manifest)

            parent_chunk_id = chunk_id
            results["chunks_indexed"] += 1
            self._indexed_count += 1

        # Update neighbor windows in L4E
        self._update_neighbor_windows(doc_id, results["parent_child_links"])

        results["adg_edges_bound"] = edges.to_dict()

        _emit_records_learning_event(
            _trace_id, "document_indexed", f"chunks:{results['chunks_indexed']}",
        )

        Logger.info(f"Indexed document {doc_id}: {results['chunks_indexed']} chunks")
        return results

    def _create_enriched_manifest(
        self,
        chunk_id: str,
        doc_id: str,
        source_path: str,
        content: str,
        chunk_index: int,
        metadata: dict[str, Any],
        adg_edges: ADGEdgeBinding,
        parent_chunk_id: str | None = None,
        embedding: list[float] | None = None,
    ) -> EnrichedChunkManifest:
        """Create an enriched chunk manifest from raw content."""
        # Generate embedding hash if embedding provided
        fact_vec_hash = ""
        if embedding:
            fact_vec_hash = hashlib.sha256(
                json.dumps(embedding, sort_keys=True).encode(),
            ).hexdigest()[:16]

        # Lazy import to avoid L3->L4 violation
        from agentic_core.knowledge.enrichment.semantic_enricher import SemanticEnricher

        # Try semantic enrichment; fall back to metadata on failure (fail-open)
        enrichment_source = "metadata_fallback"
        title = metadata.get("title", "")
        summary = metadata.get("summary", "")
        key_concepts = metadata.get("key_concepts", [])
        agentic_patterns = metadata.get("agentic_patterns", [])
        execution_insight = metadata.get("execution_insight", "")
        query_expansion_terms = metadata.get("query_expansion_terms", [])

        try:
            enricher = SemanticEnricher()
            knowledge_obj = enricher.enrich_chunk(
                chunk_id=chunk_id,
                raw_text=content,
                chunk_type="general",
                source_metadata=metadata,
            )
            # Validate enrichment produced non-empty fields
            if knowledge_obj.title and knowledge_obj.key_concepts:
                # Populate from enriched knowledge object
                title = knowledge_obj.title
                summary = knowledge_obj.summary
                key_concepts = knowledge_obj.key_concepts
                agentic_patterns = knowledge_obj.agentic_patterns
                execution_insight = knowledge_obj.execution_insight
                query_expansion_terms = knowledge_obj.query_expansion_terms
                enrichment_source = "semantic_enricher"
                Logger.debug(f"Enriched chunk {chunk_id} via SemanticEnricher")
            else:
                Logger.warning(f"Semantic enrichment produced empty fields for chunk {chunk_id}; using metadata fallback")
        except Exception as e:
            Logger.warning(f"Semantic enrichment failed for chunk {chunk_id}: {e}; using metadata fallback")

        # Extract enrichment fields from metadata or enrichment
        enriched_content = {
            "raw": content,
            "adg_edges": adg_edges.to_dict(),
            "extracted_entities": metadata.get("entities", []),
            "extracted_relationships": metadata.get("relationships", []),
            "enrichment_source": enrichment_source,
        }

        return EnrichedChunkManifest(
            chunk_id=chunk_id,
            raw_content=content,
            enriched_content=enriched_content,
            title=title,
            summary=summary,
            key_concepts=key_concepts,
            agentic_patterns=agentic_patterns,
            execution_insight=execution_insight,
            query_expansion_terms=query_expansion_terms,
            source_file=source_path,
            doc_id=doc_id,
            chunk_index=chunk_index,
            security_labels=metadata.get("security_labels", []),
            adg_edges=[adg_edges.to_dict()],
            fact_vec=embedding,
            fact_vec_hash=fact_vec_hash,
            embedding_model=metadata.get("embedding_model", "bge-m3"),
            healer_used=metadata.get("healer_used", ""),
            success_status=True,
            trace_id=f"graph_index_{doc_id}",
            replay_key=metadata.get("replay_key", ""),
            parent_chunk_id=parent_chunk_id,
        )

    def _store_in_vector_db(self, manifest: EnrichedChunkManifest) -> bool:
        """Store chunk embedding in vector DB."""
        if not self.vector_db_client or not manifest.fact_vec:
            return False

        try:
            # Assuming ChromaDB client with add method
            collection = self.vector_db_client.get_or_create_collection(name="graphrag")
            collection.add(
                ids=[manifest.chunk_id],
                embeddings=[manifest.fact_vec],
                documents=[manifest.raw_content],
                metadatas=[{
                    "doc_id": manifest.doc_id,
                    "source_file": manifest.source_file,
                    "chunk_index": manifest.chunk_index,
                    "title": manifest.title,
                    "key_concepts": json.dumps(manifest.key_concepts),
                    "adg_edges": json.dumps(manifest.adg_edges),
                }],
            )
            return True
        except (ValueError, TypeError) as e:
            Logger.error(f"Failed to store in vector DB: {e}")
            return False

    def _update_neighbor_windows(self, doc_id: str, links: list[tuple[str, str]]) -> None:
        """Update neighbor window IDs for sibling context."""
        # Build sibling groups by parent
        parent_to_children: dict[str, list[str]] = {}
        for parent_id, child_id in links:
            if parent_id not in parent_to_children:
                parent_to_children[parent_id] = []
            parent_to_children[parent_id].append(child_id)

        # Update links with neighbor windows
        for parent_id, children in parent_to_children.items():
            for child_id in children:
                link = self.l4e_registry.get_link(child_id)
                if link:
                    # Get siblings (all children of same parent except self)
                    siblings = [c for c in children if c != child_id]
                    # Create new link with updated neighbor window
                    updated_link = ParentChildLink(
                        child_chunk_id=link.child_chunk_id,
                        parent_chunk_id=link.parent_chunk_id,
                        expansion_policy=link.expansion_policy,
                        neighbor_window_ids=tuple(siblings[:5]),  # Max 5 siblings
                    )
                    # Re-write updated link
                    self.l4e_registry.write(updated_link)

    def get_adg_edges(self, doc_id: str) -> ADGEdgeBinding | None:
        """Get ADG edge binding for a document."""
        return self._edge_bindings.get(doc_id)

    def get_stats(self) -> dict[str, Any]:
        """Get indexer statistics."""
        return {
            "total_indexed": self._indexed_count,
            "edge_bindings": len(self._edge_bindings),
            "l4d_manifests": self.l4d_registry.get_stats(),
            "l4e_links": self.l4e_registry.count(),
        }


class ADGEdgeExtractor:
    """Extracts ADG edges for document chunks using REAL SQLite queries.

    Queries the ADG graph to find reads_from and writes_to edges
    that are relevant to a given source file.
    """

    def __init__(self, adg_client: ADGQueryClient | None = None):
        """Initialize ADG edge extractor.

        Args:
            adg_client: ADG client for querying the graph. If None, uses global.
        """
        self.adg_client = adg_client or get_global_adg_client()

    def extract_edges(self, source_file: str) -> ADGEdgeBinding:
        """Extract ADG edges for a source file.

        Args:
            source_file: Source file path to find edges for

        Returns:
            ADGEdgeBinding with reads_from and writes_to edges from REAL ADG
        """
        chunk_id = f"adg_{hashlib.sha256(source_file.encode()).hexdigest()[:16]}"

        # Query REAL ADG for nodes and edges
        nodes = self.adg_client.get_nodes_for_file(source_file)

        reads_from = []
        writes_to = []
        pulls_context = []

        for node in nodes:
            # Get outgoing edges (what this file/module depends on)
            edges = self.adg_client.get_edges_for_node(node.node_id, direction="out")

            for edge in edges:
                if edge.relation_type in ("reads_from", "imports", "calls", "invokes"):
                    reads_from.append(edge.symbol or edge.dst_id)
                elif edge.relation_type in ("writes_to", "exports", "defines"):
                    writes_to.append(edge.symbol or edge.dst_id)

            # Node symbol is a context source
            if node.symbol_name:
                pulls_context.append(node.symbol_name)

        # Get incoming edges (what depends on this file/module)
        for node in nodes:
            edges = self.adg_client.get_edges_for_node(node.node_id, direction="in")
            for edge in edges:
                if edge.relation_type in ("calls", "imports", "reads_from"):
                    # This shows what depends on this file
                    writes_to.append(f"dep:{edge.src_id}")

        return ADGEdgeBinding(
            chunk_id=chunk_id,
            source_file=source_file,
            reads_from=list(set(reads_from))[:50],  # Limit to top 50
            writes_to=list(set(writes_to))[:20],
            pulls_context=list(set(pulls_context))[:10],
        )

    def extract_edges_for_chunk(
        self,
        chunk_id: str,
        content: str,
        entities: list[str],
    ) -> ADGEdgeBinding:
        """Extract ADG edges for a specific chunk.

        Uses entity mentions in content to find relevant ADG edges.

        Args:
            chunk_id: Chunk identifier
            content: Chunk content
            entities: Named entities extracted from content

        Returns:
            ADGEdgeBinding specific to this chunk
        """
        # For chunks, we use entities to look up in ADG
        reads_from = []
        writes_to = []
        pulls_context = []

        for entity in entities[:10]:  # Check top 10 entities
            node = self.adg_client.get_node_by_symbol(entity)
            if node:
                pulls_context.append(entity)
                # Get edges for this entity
                edges = self.adg_client.get_edges_for_node(node.node_id)
                for edge in edges:
                    if edge.relation_type == "reads_from":
                        reads_from.append(edge.symbol)
                    elif edge.relation_type == "writes_to":
                        writes_to.append(edge.symbol)

        return ADGEdgeBinding(
            chunk_id=chunk_id,
            source_file="",
            reads_from=list(set(reads_from))[:10],
            writes_to=list(set(writes_to))[:5],
            pulls_context=list(set(pulls_context))[:5],
        )


# Global instances
_global_indexer: GraphAwareIndexer | None = None
_global_extractor: ADGEdgeExtractor | None = None


def get_global_indexer() -> GraphAwareIndexer:
    """Get or create global graph-aware indexer."""
    global _global_indexer
    if _global_indexer is None:
        _global_indexer = GraphAwareIndexer()
    return _global_indexer


def get_global_extractor() -> ADGEdgeExtractor:
    """Get or create global ADG edge extractor."""
    global _global_extractor
    if _global_extractor is None:
        _global_extractor = ADGEdgeExtractor()
    return _global_extractor


def index_document(
    doc_id: str,
    source_path: str,
    chunks: list[dict[str, Any]],
    adg_edges: ADGEdgeBinding | None = None,
    embeddings: list[list[float]] | None = None,
) -> dict[str, Any]:
    """Convenience function to index a document."""
    return get_global_indexer().index_document(
        doc_id=doc_id,
        source_path=source_path,
        chunks=chunks,
        adg_edges=adg_edges,
        embeddings=embeddings,
    )


__all__ = [
    "GraphAwareIndexer",
    "ADGEdgeExtractor",
    "ADGEdgeBinding",
    "GraphEnrichmentContext",
    "get_global_indexer",
    "get_global_extractor",
    "index_document",
]
