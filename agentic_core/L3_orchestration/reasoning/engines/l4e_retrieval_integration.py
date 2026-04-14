"""L4E Retrieval Integration for Pipeline C - PRODUCTION.

Implements spec-compliant retrieval from Agentic Retrieval Models v9:
- Phase 2: Inference Routing & Graph Hydration (Pipeline C)
- Layer 3: Agentic RAG with Parent-Child Expansion (Step 4c)
- Integrates L4E ParentChildIndex with L3 retrieval layers
- REAL ADG edge hydration via SQLite queries

Provides:
- ADG edge hydration during retrieval (REAL - queries SQLite)
- pulls_context edge resolution
- Parent-child expansion with confidence decay
- Graph-based context assembly
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.reasoning.engines.adg_integration import (
    ADGQueryClient,
    get_global_adg_client,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_evaluation_metric,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_learning_event,
    _emit_stores_embedding,
)
from tqdm import tqdm

# ParentChildExpander, ExpansionContext, L4ERetrievalIntegrator, ChunkManifestRegistry, EnrichedChunkManifest
# imported lazily to avoid L3->L4 violation

Logger = logging.getLogger(__name__)


@dataclass
class ADGEdgeHydration:
    """Hydrated ADG edges for a retrieved chunk.

    Represents the resolved reads_from, writes_to, and pulls_context
    edges from the ADG graph that are relevant to a retrieved chunk.
    """

    chunk_id: str
    reads_from: list[dict[str, Any]] = field(default_factory=list)
    writes_to: list[dict[str, Any]] = field(default_factory=list)
    pulls_context: list[dict[str, Any]] = field(default_factory=list)
    adg_node_ids: list[str] = field(default_factory=list)
    edge_confidence: float = 1.0


@dataclass
class GraphRetrievalContext:
    """Retrieval context enriched with ADG graph edges.

    Combines vector search results with graph-hydrated metadata
    for completeness-aware retrieval.
    """

    chunk_id: str
    content: str
    score: float
    source: str  # 'vector', 'lexical', 'l4e_expansion'

    # L4D manifest data
    manifest: EnrichedChunkManifest | None = None

    # ADG edge hydration
    adg_hydration: ADGEdgeHydration | None = None

    # Parent-child expansion metadata
    expansion_depth: int = 0
    expansion_relationship: str = "seed"  # 'seed', 'parent', 'child', 'sibling'
    expansion_confidence: float = 1.0

    # Groundedness scoring
    groundedness_score: float = 0.0
    supporting_edges: list[str] = field(default_factory=list)

    def to_prompt_context(self) -> dict[str, Any]:
        """Convert to prompt-friendly context format."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "title": self.manifest.title if self.manifest else "",
            "key_concepts": self.manifest.key_concepts if self.manifest else [],
            "adg_edges": self.adg_hydration.reads_from if self.adg_hydration else [],
            "expansion": {
                "depth": self.expansion_depth,
                "relationship": self.expansion_relationship,
                "confidence": self.expansion_confidence,
            }
            if self.expansion_depth > 0
            else None,
        }


class ADGEdgeHydrator:
    """Hydrates retrieval results with REAL ADG graph edges from SQLite.

    Queries the ADG graph to resolve reads_from, writes_to, and
    pulls_context edges for retrieved chunks.
    """

    def __init__(self, adg_client: ADGQueryClient | None = None):
        """Initialize ADG edge hydrator.

        Args:
            adg_client: ADG client for querying the graph. If None, uses global.
        """
        self.adg_client = adg_client or get_global_adg_client()
        self._hydration_count = 0
        self._avg_hydration_time_ms = 0.0

    def hydrate(
        self,
        chunk_id: str,
        source_file: str | None = None,
    ) -> ADGEdgeHydration:
        """Hydrate a chunk with REAL ADG edges.

        Args:
            chunk_id: Chunk identifier
            source_file: Optional source file for edge lookup

        Returns:
            ADGEdgeHydration with resolved edges from SQLite ADG
        """
        _trace_id = f"hydrate_{chunk_id}"
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "ADGEdgeHydrator.hydrate",
        )

        hydration = ADGEdgeHydration(chunk_id=chunk_id)

        if source_file:
            # Resolve REAL ADG edges from SQLite
            hydration.reads_from = self._resolve_reads_from(source_file)
            hydration.writes_to = self._resolve_writes_to(source_file)
            hydration.pulls_context = self._resolve_pulls_context(source_file)

            # Collect ADG node IDs
            nodes = self.adg_client.get_nodes_for_file(source_file)
            hydration.adg_node_ids = [n.node_id for n in nodes]

            for ctx in hydration.pulls_context:
                _emit_stores_embedding(_trace_id, chunk_id, ctx.get("source", ""))

        self._hydration_count += 1

        return hydration

    def hydrate_batch(
        self,
        chunk_ids: list[str],
        source_files: dict[str, str] | None = None,
    ) -> dict[str, ADGEdgeHydration]:
        """Hydrate multiple chunks with ADG edges.

        Args:
            chunk_ids: List of chunk identifiers
            source_files: Optional mapping of chunk_id -> source_file

        Returns:
            Mapping of chunk_id -> ADGEdgeHydration
        """
        results = {}
        for chunk_id in chunk_ids:
            source = source_files.get(chunk_id) if source_files else None
            results[chunk_id] = self.hydrate(chunk_id, source)
        return results

    def _resolve_reads_from(self, source_file: str) -> list[dict[str, Any]]:
        """Resolve reads_from edges for a source file from REAL ADG."""
        nodes = self.adg_client.get_nodes_for_file(source_file)
        reads_from = []

        for node in tqdm(nodes, desc="Processing", unit="item"):
            edges = self.adg_client.get_edges_for_node(
                node.node_id,
                relation_type="reads_from",
                direction="out",
            )
            for edge in edges:
                reads_from.append(
                    {
                        "symbol": edge.symbol,
                        "source_node": node.symbol_name,
                        "target_node_id": edge.dst_id,
                        "relation": edge.relation_type,
                        "line_no": edge.line_no,
                    }
                )

        return reads_from

    def _resolve_writes_to(self, source_file: str) -> list[dict[str, Any]]:
        """Resolve writes_to edges for a source file from REAL ADG."""
        nodes = self.adg_client.get_nodes_for_file(source_file)
        writes_to = []

        for node in tqdm(nodes, desc="Processing", unit="item"):
            edges = self.adg_client.get_edges_for_node(
                node.node_id,
                relation_type="writes_to",
                direction="out",
            )
            for edge in edges:
                writes_to.append(
                    {
                        "symbol": edge.symbol,
                        "source_node": node.symbol_name,
                        "target_node_id": edge.dst_id,
                        "relation": edge.relation_type,
                        "line_no": edge.line_no,
                    }
                )

        return writes_to

    def _resolve_pulls_context(self, source_file: str) -> list[dict[str, Any]]:
        """Resolve pulls_context edges for a source file from REAL ADG."""
        nodes = self.adg_client.get_nodes_for_file(source_file)
        pulls_context = []

        for node in nodes:
            # pulls_context is based on nodes in the file
            pulls_context.append(
                {
                    "source": node.symbol_name,
                    "node_id": node.node_id,
                    "entity_type": node.entity_type,
                    "layer": node.layer,
                }
            )

        return pulls_context


class GraphRetrievalEngine:
    """Graph-aware retrieval engine for Pipeline C.

    Implements:
    - Vector search retrieval (L3)
    - Parent-child expansion via L4E (Step 4c)
    - ADG edge hydration
    - Groundedness scoring
    - Prompt context generation
    """

    def __init__(
        self,
        vector_db_client: Any | None = None,
        l4e_expander: ParentChildExpander | None = None,
        adg_hydrator: ADGEdgeHydrator | None = None,
        l4d_registry: ChunkManifestRegistry | None = None,
    ):
        """Initialize graph retrieval engine.

        Args:
            vector_db_client: ChromaDB or similar vector DB client
            l4e_expander: Parent-child expander from L4E
            adg_hydrator: ADG edge hydrator
            l4d_registry: L4D chunk manifest registry
        """
        self.vector_db_client = vector_db_client
        self.l4e_expander = l4e_expander or ParentChildExpander()
        self.adg_hydrator = adg_hydrator or ADGEdgeHydrator()
        self.l4d_registry = l4d_registry

        self._retrieval_count = 0
        self._avg_expansion_factor = 1.0

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        expansion_depth: int = 3,
        hydrate_adg: bool = True,
    ) -> list[GraphRetrievalContext]:
        """Retrieve with graph-aware expansion and hydration.

        Args:
            query: Search query (must be non-empty)
            n_results: Number of initial vector results
            expansion_depth: Parent-child expansion depth (1-5, clamped)
            hydrate_adg: Whether to hydrate with ADG edges

        Returns:
            List of graph-retrieval contexts (may be empty on failure)
        """
        # Input validation
        if not query or not isinstance(query, str):
            Logger.error(f"Invalid query: {query!r}")
            return []

        # Clamp expansion depth to valid range
        expansion_depth = max(0, min(expansion_depth, 5))

        _trace_id = f"retrieve_{self._retrieval_count}"
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "GraphRetrievalEngine.retrieve",
        )
        _emit_reads_through(_trace_id, "vector", query[:50])

        try:
            # Step 1: Vector search (4a)
            initial_results = self._vector_search(query, n_results)

            if not initial_results:
                Logger.warning(f"No initial results for query: {query[:50]}...")
                return []

            # Step 2: Parent-child expansion (4c)
            expanded_results = self._expand_with_l4e(initial_results, expansion_depth)

            # Step 3: ADG edge hydration
            contexts = []
            for result in expanded_results:
                try:
                    context = self._create_retrieval_context(result, hydrate_adg)
                    contexts.append(context)
                except (RuntimeError, ValueError) as e:
                    Logger.error(f"Failed to create context for {result.get('chunk_id')}: {e}")
                    # Continue with other results (fail-open for individual contexts)
                    continue

            # Step 4: Groundedness scoring
            contexts = self._score_groundedness(contexts)

            # Update stats
            expansion_factor = len(contexts) / max(len(initial_results), 1)
            self._avg_expansion_factor = (
                self._avg_expansion_factor * self._retrieval_count + expansion_factor
            ) / (self._retrieval_count + 1)
            self._retrieval_count += 1

            _emit_records_learning_event(_trace_id, "prompt_context_generated", f"chunks:{len(contexts)}")

            return contexts

        except (RuntimeError, ValueError) as e:
            Logger.error(f"Retrieval failed for query '{query[:50]}...': {e}")
            # Fail-closed: return empty list rather than partial results
            return []

    def _vector_search(
        self,
        query: str,
        n_results: int,
    ) -> list[dict[str, Any]]:
        """Perform vector search."""
        if not self.vector_db_client:
            return []

        try:
            collection = self.vector_db_client.get_collection(name="graphrag")
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
            )

            formatted = []
            for i, (doc_id, document, metadata) in tqdm(
                enumerate(
                    zip(
                        results["ids"][0],
                        results["documents"][0],
                        results["metadatas"][0],
                    )
                ),
                desc="Processing",
                unit="item",
            ):
                formatted.append(
                    {
                        "chunk_id": doc_id,
                        "content": document,
                        "metadata": metadata,
                        "score": 1.0 - (i * 0.1),  # Descending score
                        "source": "vector",
                    }
                )

            return formatted

        except (RuntimeError, ValueError) as e:
            Logger.error(f"Vector search failed: {e}")
            return []

    def _expand_with_l4e(
        self,
        initial_results: list[dict[str, Any]],
        depth: int,
    ) -> list[dict[str, Any]]:
        """Expand results using L4E ParentChildIndex."""
        self.l4e_expander.max_depth = depth

        all_results = list(initial_results)
        seen_ids = {r["chunk_id"] for r in initial_results}

        for seed in tqdm(initial_results, desc="Processing", unit="item"):
            chunk_id = seed["chunk_id"]
            content = seed["content"]

            # Expand via L4E
            expanded = self.l4e_expander.expand(
                seed_chunk_id=chunk_id,
                seed_content=content,
            )

            for ctx in tqdm(expanded, desc="Processing", unit="item"):
                if ctx.chunk_id in seen_ids:
                    continue

                seen_ids.add(ctx.chunk_id)
                all_results.append(
                    {
                        "chunk_id": ctx.chunk_id,
                        "content": ctx.content,
                        "metadata": ctx.metadata,
                        "score": ctx.confidence * 0.5,
                        "source": "l4e_expansion",
                        "expansion_depth": ctx.depth,
                        "expansion_relationship": ctx.relationship,
                        "expansion_confidence": ctx.confidence,
                    }
                )

        return all_results

    def _create_retrieval_context(
        self,
        result: dict[str, Any],
        hydrate_adg: bool,
    ) -> GraphRetrievalContext:
        """Create graph retrieval context from result."""
        chunk_id = result["chunk_id"]
        metadata = result.get("metadata", {})

        # Get L4D manifest if available
        manifest = None
        if self.l4d_registry:
            manifest = self.l4d_registry.get_manifest(chunk_id)

        # Hydrate ADG edges
        adg_hydration = None
        if hydrate_adg:
            source_file = metadata.get("source_file", "")
            adg_hydration = self.adg_hydrator.hydrate(chunk_id, source_file)

        return GraphRetrievalContext(
            chunk_id=chunk_id,
            content=result["content"],
            score=result["score"],
            source=result["source"],
            manifest=manifest,
            adg_hydration=adg_hydration,
            expansion_depth=result.get("expansion_depth", 0),
            expansion_relationship=result.get("expansion_relationship", "seed"),
            expansion_confidence=result.get("expansion_confidence", 1.0),
        )

    def _score_groundedness(
        self,
        contexts: list[GraphRetrievalContext],
    ) -> list[GraphRetrievalContext]:
        """Score groundedness of retrieval contexts."""
        for ctx in tqdm(contexts, desc="Processing", unit="item"):
            score = 0.0

            # Factor 1: Source reliability
            if ctx.source == "vector":
                score += 0.4
            elif ctx.source == "l4e_expansion":
                score += 0.3 * ctx.expansion_confidence

            # Factor 2: ADG edge support
            if ctx.adg_hydration:
                edge_count = (
                    len(ctx.adg_hydration.reads_from)
                    + len(ctx.adg_hydration.writes_to)
                    + len(ctx.adg_hydration.pulls_context)
                )
                score += min(0.3, edge_count * 0.05)

            # Factor 3: Manifest enrichment
            if ctx.manifest:
                if ctx.manifest.key_concepts:
                    score += 0.15
                if ctx.manifest.agentic_patterns:
                    score += 0.15

            ctx.groundedness_score = min(1.0, score)
            _emit_captures_evaluation_metric(f"ctx_{ctx.chunk_id}", "groundedness", ctx.groundedness_score)

        # Sort by groundedness score
        contexts.sort(key=lambda c: c.groundedness_score, reverse=True)
        return contexts

    def assemble_prompt_context(
        self,
        contexts: list[GraphRetrievalContext],
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        """Assemble retrieval contexts into prompt context.

        Args:
            contexts: List of graph retrieval contexts
            max_tokens: Maximum tokens for context

        Returns:
            Prompt context with formatted chunks and metadata
        """
        _trace_id = f"assemble_{self._retrieval_count}"
        _emit_records_learning_event(_trace_id, "context_assembled", f"input:{len(contexts)}")

        # Filter by groundedness score
        filtered = [c for c in contexts if c.groundedness_score >= 0.5]
        if not filtered:
            filtered = contexts[:3]  # Fallback to top 3

        # Format chunks for prompt
        formatted_chunks = []
        total_tokens = 0

        for ctx in tqdm(filtered, desc="Processing", unit="item"):
            chunk_tokens = len(ctx.content.split())  # Approximate
            if total_tokens + chunk_tokens > max_tokens:
                break

            formatted_chunks.append(
                {
                    "chunk_id": ctx.chunk_id,
                    "content": ctx.content,
                    "title": ctx.manifest.title if ctx.manifest else "",
                    "key_concepts": ctx.manifest.key_concepts if ctx.manifest else [],
                    "groundedness": ctx.groundedness_score,
                    "source": ctx.source,
                }
            )
            total_tokens += chunk_tokens

        return {
            "chunks": formatted_chunks,
            "total_chunks": len(formatted_chunks),
            "total_tokens": total_tokens,
            "expansion_used": any(c.expansion_depth > 0 for c in filtered),
            "adg_hydrated": any(c.adg_hydration is not None for c in filtered),
        }

    def get_stats(self) -> dict[str, Any]:
        """Get retrieval engine statistics."""
        return {
            "retrieval_count": self._retrieval_count,
            "avg_expansion_factor": self._avg_expansion_factor,
            "l4e_expander": self.l4e_expander.get_stats(),
        }


class RetrievalWithGraphIntegration:
    """High-level integration wrapper for graph-aware retrieval.

    Combines all Pipeline C components:
    - GraphRetrievalEngine for vector + L4E expansion
    - ADGEdgeHydrator for edge hydration
    - L4ERetrievalIntegrator for parent-child expansion
    """

    def __init__(
        self,
        retrieval_engine: GraphRetrievalEngine | None = None,
    ):
        """Initialize retrieval with graph integration.

        Args:
            retrieval_engine: Graph retrieval engine
        """
        self.engine = retrieval_engine or GraphRetrievalEngine()

    def search(
        self,
        query: str,
        n_results: int = 5,
        expansion_depth: int = 3,
    ) -> dict[str, Any]:
        """Search with full graph integration.

        Args:
            query: Search query
            n_results: Number of results
            expansion_depth: Parent-child expansion depth

        Returns:
            Search results with graph context
        """
        # Retrieve with graph awareness
        contexts = self.engine.retrieve(
            query=query,
            n_results=n_results,
            expansion_depth=expansion_depth,
            hydrate_adg=True,
        )

        # Assemble prompt context
        prompt_context = self.engine.assemble_prompt_context(contexts)

        return {
            "query": query,
            "contexts": [ctx.to_prompt_context() for ctx in contexts],
            "prompt_context": prompt_context,
            "stats": {
                "total_contexts": len(contexts),
                "vector_results": sum(1 for c in contexts if c.source == "vector"),
                "expanded_results": sum(1 for c in contexts if c.expansion_depth > 0),
                "avg_groundedness": sum(c.groundedness_score for c in contexts) / max(len(contexts), 1),
            },
        }


# Global instances
_global_engine: GraphRetrievalEngine | None = None
_global_integration: RetrievalWithGraphIntegration | None = None


def get_global_engine() -> GraphRetrievalEngine:
    """Get or create global graph retrieval engine."""
    global _global_engine
    if _global_engine is None:
        _global_engine = GraphRetrievalEngine()
    return _global_engine


def get_global_integration() -> RetrievalWithGraphIntegration:
    """Get or create global retrieval integration."""
    global _global_integration
    if _global_integration is None:
        _global_integration = RetrievalWithGraphIntegration(
            retrieval_engine=get_global_engine(),
        )
    return _global_integration


def search(
    query: str,
    n_results: int = 5,
    expansion_depth: int = 3,
) -> dict[str, Any]:
    """Convenience function for graph-aware search."""
    return get_global_integration().search(
        query=query,
        n_results=n_results,
        expansion_depth=expansion_depth,
    )


__all__ = [
    "ADGEdgeHydration",
    "ADGEdgeHydrator",
    "GraphRetrievalContext",
    "GraphRetrievalEngine",
    "RetrievalWithGraphIntegration",
    "RetrievalContextComposer",
    "get_global_engine",
    "get_global_integration",
    "search",
]


class RetrievalContextComposer:
    """Composes retrieval context from multiple sources for L4E integration.

    Combines vector search results, ADG edge hydration, and parent-child
    expansion into a unified context for prompt assembly.
    """

    def __init__(self, retrieval_engine: GraphRetrievalEngine | None = None):
        """Initialize context composer.

        Args:
            retrieval_engine: Graph retrieval engine instance
        """
        self.engine = retrieval_engine or get_global_engine()

    def compose(
        self,
        query: str,
        n_results: int = 5,
        expansion_depth: int = 3,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        """Compose retrieval context from query.

        Args:
            query: Search query
            n_results: Number of vector results
            expansion_depth: Parent-child expansion depth
            max_tokens: Maximum tokens for context

        Returns:
            Composed context with chunks, metadata, and stats
        """
        # Retrieve with graph awareness
        contexts = self.engine.retrieve(
            query=query,
            n_results=n_results,
            expansion_depth=expansion_depth,
            hydrate_adg=True,
        )

        # Assemble prompt context
        prompt_context = self.engine.assemble_prompt_context(contexts, max_tokens)

        return {
            "query": query,
            "contexts": [ctx.to_prompt_context() for ctx in contexts],
            "prompt_context": prompt_context,
            "stats": {
                "total_contexts": len(contexts),
                "vector_results": sum(1 for c in contexts if c.source == "vector"),
                "expanded_results": sum(1 for c in contexts if c.expansion_depth > 0),
                "avg_groundedness": sum(c.groundedness_score for c in contexts) / max(len(contexts), 1),
            },
        }

    def get_stats(self) -> dict[str, Any]:
        """Get composer statistics."""
        return self.engine.get_stats()
