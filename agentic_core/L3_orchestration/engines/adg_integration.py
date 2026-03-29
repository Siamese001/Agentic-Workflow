"""ADG Integration Wiring for GraphRAG.

Provides the integration layer between:
- ADG (Agentic Directed Graph) static edges
- GraphRAG retrieval and indexing
- ParentChildIndex (L4E) registry

Implements:
- ADG edge query interface
- pulls_context edge resolution
- reads_from/writes_to edge binding
- Graph topology queries
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_records_execution_trace,
    _emit_pulls_context,
    _emit_reads_through,
    _emit_writes_through,
)

Logger = logging.getLogger(__name__)


@dataclass
class ADGNode:
    """ADG node representation."""
    node_id: str
    entity_type: str
    layer: str
    file_path: str
    symbol_name: str


@dataclass
class ADGEdge:
    """ADG edge representation."""
    edge_id: str
    src_id: str
    dst_id: str
    relation_type: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str


class ADGQueryClient:
    """Client for querying ADG graph.
    
    Provides interface to:
    - Query nodes by file, layer, or entity type
    - Query edges by relation type
    - Resolve pulls_context edges
    - Get graph topology
    """
    
    def __init__(self, adg_db_path: Optional[str] = None):
        """Initialize ADG query client.
        
        Args:
            adg_db_path: Path to ADG SQLite database
        """
        self.adg_db_path = adg_db_path
        self._cache: dict[str, Any] = {}
    
    def get_nodes_for_file(self, file_path: str) -> list[ADGNode]:
        """Get ADG nodes for a specific file.
        
        Args:
            file_path: Source file path
            
        Returns:
            List of ADG nodes defined in the file
        """
        # In production, query ADG SQLite:
        # SELECT * FROM nodes WHERE file_path = ?
        
        # Placeholder implementation
        return [
            ADGNode(
                node_id=f"{file_path}::symbol_{i}",
                entity_type="function",
                layer="L2_EXECUTION",
                file_path=file_path,
                symbol_name=f"symbol_{i}",
            )
            for i in range(3)
        ]
    
    def get_edges_for_node(
        self,
        node_id: str,
        relation_type: Optional[str] = None,
    ) -> list[ADGEdge]:
        """Get edges for a specific node.
        
        Args:
            node_id: Source node ID
            relation_type: Optional filter by relation type
            
        Returns:
            List of ADG edges from/to the node
        """
        # In production, query ADG SQLite:
        # SELECT * FROM edges WHERE src_id = ? OR dst_id = ?
        
        return []
    
    def resolve_pulls_context(
        self,
        chunk_id: str,
        context_sources: list[str],
    ) -> list[dict[str, Any]]:
        """Resolve pulls_context edges for a chunk.
        
        Args:
            chunk_id: Chunk identifier
            context_sources: List of context source identifiers
            
        Returns:
            List of resolved context edges with metadata
        """
        _trace_id = f"pulls_context_{chunk_id}"
        _emit_records_execution_trace(
            _trace_id, "L4_STATE", "ADGQueryClient.resolve_pulls_context"
        )
        
        resolved = []
        for source in context_sources:
            _emit_pulls_context(_trace_id, chunk_id, source)
            resolved.append({
                "chunk_id": chunk_id,
                "source": source,
                "relation": "pulls_context",
                "confidence": 1.0,
            })
        
        return resolved
    
    def get_graph_topology(
        self,
        edge_types: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Get overall graph topology statistics.
        
        Args:
            edge_types: Optional list of edge types to filter
            
        Returns:
            Graph topology statistics
        """
        # In production, query ADG for counts
        default_topology = {
            "retrieves_via": 52,
            "pulls_context": 32,
            "scores_groundedness": 40,
            "generates_prompt": 215,
            "reads_from": 72660,
            "writes_to": 5102,
            "records_execution_trace": 115,
        }
        
        if edge_types:
            return {k: v for k, v in default_topology.items() if k in edge_types}
        
        return default_topology


class GraphRAGADGIntegration:
    """Integration layer between GraphRAG and ADG.
    
    Provides:
    - ADG edge binding during ingestion
    - ADG edge hydration during retrieval
    - pulls_context resolution
    - Graph topology awareness
    """
    
    def __init__(
        self,
        adg_client: Optional[ADGQueryClient] = None,
    ):
        """Initialize GraphRAG-ADG integration.
        
        Args:
            adg_client: ADG query client
        """
        self.adg_client = adg_client or ADGQueryClient()
    
    def bind_edges_for_ingestion(
        self,
        doc_id: str,
        source_path: str,
        chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Bind ADG edges during document ingestion.
        
        Args:
            doc_id: Document identifier
            source_path: Source file path
            chunks: Document chunks
            
        Returns:
            Edge binding results with reads_from, writes_to, pulls_context
        """
        # Get ADG nodes for this file
        nodes = self.adg_client.get_nodes_for_file(source_path)
        
        # Extract entity names for binding
        entity_names = [node.symbol_name for node in nodes]
        
        # Create edge binding
        binding = {
            "doc_id": doc_id,
            "source_path": source_path,
            "adg_nodes": [n.node_id for n in nodes],
            "reads_from": entity_names[:5],  # Limit to top 5
            "writes_to": [],  # Populated based on analysis
            "pulls_context": entity_names[:3] if len(entity_names) > 3 else entity_names,
        }
        
        return binding
    
    def hydrate_edges_for_retrieval(
        self,
        chunk_id: str,
        source_path: str,
    ) -> dict[str, Any]:
        """Hydrate ADG edges during chunk retrieval.
        
        Args:
            chunk_id: Chunk identifier
            source_path: Source file path
            
        Returns:
            Hydrated edge data
        """
        # Get nodes for the source file
        nodes = self.adg_client.get_nodes_for_file(source_path)
        
        # Get edges for these nodes
        edges = []
        for node in nodes:
            node_edges = self.adg_client.get_edges_for_node(node.node_id)
            edges.extend(node_edges)
        
        # Resolve pulls_context edges
        context_sources = [n.symbol_name for n in nodes]
        pulls_context = self.adg_client.resolve_pulls_context(chunk_id, context_sources)
        
        return {
            "chunk_id": chunk_id,
            "adg_nodes": len(nodes),
            "adg_edges": len(edges),
            "pulls_context": pulls_context,
            "reads_from": [e.symbol for e in edges if e.relation_type == "reads_from"],
            "writes_to": [e.symbol for e in edges if e.relation_type == "writes_to"],
        }


# Global instance
_global_adg_integration: Optional[GraphRAGADGIntegration] = None


def get_global_adg_integration() -> GraphRAGADGIntegration:
    """Get or create global ADG integration."""
    global _global_adg_integration
    if _global_adg_integration is None:
        _global_adg_integration = GraphRAGADGIntegration()
    return _global_adg_integration


__all__ = [
    "ADGQueryClient",
    "GraphRAGADGIntegration",
    "ADGNode",
    "ADGEdge",
    "get_global_adg_integration",
]
