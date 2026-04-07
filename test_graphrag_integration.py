"""GraphRAG Integration Test using SQLiteGraphStore.

Demonstrates graph-aware retrieval capabilities:
- Entity search with graph context
- Multi-hop context expansion
- Relationship-based filtering
- Graph-enhanced query results
"""

from pathlib import Path
from typing import Any

from agentic_core.L4_state.utils.memory.graph_store_factory import create_sqlite_graph_store
from agentic_core.L4_state.types.graph_store_types import GraphEntity


class GraphRAGRetriever:
    """Graph-aware retriever using SQLiteGraphStore."""
    
    def __init__(self, db_path: str | Path | None = None):
        """Initialize the retriever with graph store."""
        self.store = create_sqlite_graph_store(db_path)
    
    def search_with_context(
        self,
        query: str,
        max_hops: int = 2,
        limit: int = 5
    ) -> list[dict[str, Any]]:
        """Search entities and expand with graph context.
        
        Args:
            query: Search query for entities
            max_hops: Maximum hops for context expansion
            limit: Number of initial results to return
            
        Returns:
            List of entities with graph context
        """
        # Initial entity search
        entities = self.store.search_entities(query, limit=limit)
        
        results = []
        for entity in entities:
            # Get relationships
            relationships = self.store.get_relationships(
                entity.id,
                direction="both"
            )
            
            # Get neighbors for context expansion
            neighbors = self.store.get_neighbors(entity.id, max_hops=max_hops)
            
            # Get centrality (importance score)
            centrality = self.store.get_centrality(entity.id)
            
            results.append({
                "entity": {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type,
                    "layer": entity.metadata.get("layer", "N/A"),
                    "file_path": entity.metadata.get("file_path", "N/A"),
                },
                "graph_context": {
                    "relationship_count": len(relationships),
                    "relation_types": list(set(r.relation_type for r in relationships)),
                    "neighbor_count": len(neighbors),
                    "centrality": centrality,
                },
                "sample_relationships": [
                    {
                        "type": r.relation_type,
                        "target": r.target_id if r.source_id == entity.id else r.source_id,
                        "direction": "outgoing" if r.source_id == entity.id else "incoming",
                    }
                    for r in relationships[:5]
                ]
            })
        
        return results
    
    def get_subgraph_context(
        self,
        entity_id: str,
        radius: int = 2
    ) -> dict[str, Any]:
        """Get subgraph context around an entity.
        
        Args:
            entity_id: The center entity ID
            radius: Radius in hops
            
        Returns:
            Subgraph context with nodes and edges
        """
        entity = self.store.get_entity(entity_id)
        if not entity:
            return {"error": "Entity not found"}
        
        subgraph = self.store.get_subgraph(entity_id, radius=radius)
        
        return {
            "center_entity": {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type,
                "layer": entity.metadata.get("layer", "N/A"),
            },
            "subgraph_stats": {
                "node_count": len(subgraph.nodes),
                "edge_count": len(subgraph.relationships),
                "radius": radius,
            },
            "nodes_by_layer": self._group_nodes_by_layer(subgraph.nodes),
            "edges_by_type": self._group_edges_by_type(subgraph.relationships),
        }
    
    def find_related_entities(
        self,
        entity_id: str,
        relation_types: list[str] | None = None,
        max_depth: int = 2
    ) -> list[dict[str, Any]]:
        """Find entities related through specific relationship types.
        
        Args:
            entity_id: Starting entity ID
            relation_types: Filter by these relation types (None = all)
            max_depth: Maximum traversal depth
            
        Returns:
            List of related entities with path information
        """
        paths = self.store.traverse(
            entity_id,
            max_depth=max_depth,
            relation_types=relation_types
        )
        
        results = []
        seen_entities = set()
        
        for path in paths:
            for node in path.nodes:
                if node.id not in seen_entities and node.id != entity_id:
                    seen_entities.add(node.id)
                    results.append({
                        "id": node.id,
                        "name": node.name,
                        "type": node.entity_type,
                        "layer": node.metadata.get("layer", "N/A"),
                        "path_length": len(path.nodes) - 1,
                        "path_cost": path.cost,
                    })
        
        # Sort by path length (shortest paths first)
        results.sort(key=lambda x: x["path_length"])
        
        return results[:20]  # Limit to top 20
    
    def detect_entity_communities(
        self,
        entity_id: str
    ) -> dict[str, Any]:
        """Detect communities and find which community an entity belongs to.
        
        Args:
            entity_id: Entity ID to find community for
            
        Returns:
            Community information
        """
        communities = self.store.detect_communities()
        
        # Find which community the entity belongs to
        entity_community = None
        for community in communities:
            if entity_id in community.entities:
                entity_community = community
                break
        
        if not entity_community:
            return {"error": "Entity not found in any community"}
        
        # Get sample entities from the same community
        sample_entities = []
        for eid in entity_community.entities[:10]:
            entity = self.store.get_entity(eid)
            if entity:
                sample_entities.append({
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type,
                })
        
        return {
            "community_id": entity_community.id,
            "community_name": entity_community.name,
            "community_size": len(entity_community.entities),
            "sample_entities": sample_entities,
        }
    
    def _group_nodes_by_layer(self, nodes: list[GraphEntity]) -> dict[str, int]:
        """Group nodes by layer."""
        layers = {}
        for node in nodes:
            layer = node.metadata.get("layer", "Unknown")
            layers[layer] = layers.get(layer, 0) + 1
        return dict(sorted(layers.items(), key=lambda x: x[1], reverse=True))
    
    def _group_edges_by_type(self, relationships: list[Any]) -> dict[str, int]:
        """Group edges by relation type."""
        types = {}
        for rel in relationships:
            rel_type = rel.relation_type
            types[rel_type] = types.get(rel_type, 0) + 1
        return dict(sorted(types.items(), key=lambda x: x[1], reverse=True))
    
    def close(self):
        """Close the graph store connection."""
        self.store.close()


def main():
    """Run GraphRAG integration tests."""
    print("=" * 80)
    print("GraphRAG Integration Test - SQLiteGraphStore")
    print("=" * 80)
    
    # Find ADG database
    adg_dir = Path("artifacts/adg")
    db_files = list(adg_dir.glob("adg_indexed_*.sqlite"))
    if not db_files:
        print("✗ No ADG database found")
        return
    
    db_path = sorted(db_files)[-1]
    print(f"\nUsing ADG database: {db_path}")
    
    retriever = GraphRAGRetriever(db_path)
    
    try:
        # Test 1: Search with context
        print("\n" + "=" * 80)
        print("Test 1: Search with Graph Context")
        print("=" * 80)
        
        results = retriever.search_with_context("Graph", max_hops=1, limit=3)
        for i, result in enumerate(results, 1):
            entity = result["entity"]
            ctx = result["graph_context"]
            print(f"\n{i}. {entity['name']}")
            print(f"   Type: {entity['type']}, Layer: {entity['layer']}")
            print(f"   Relationships: {ctx['relationship_count']}")
            print(f"   Relation Types: {', '.join(ctx['relation_types'][:5])}")
            print(f"   Neighbors (1-hop): {ctx['neighbor_count']}")
            print(f"   Centrality: {ctx['centrality']}")
        
        # Test 2: Subgraph context
        print("\n" + "=" * 80)
        print("Test 2: Subgraph Context Extraction")
        print("=" * 80)
        
        if results:
            entity_id = results[0]["entity"]["id"]
            subgraph = retriever.get_subgraph_context(entity_id, radius=1)
            
            print(f"\nCenter: {subgraph['center_entity']['name']}")
            print(f"Subgraph: {subgraph['subgraph_stats']['node_count']} nodes, "
                  f"{subgraph['subgraph_stats']['edge_count']} edges")
            print(f"\nNodes by layer:")
            for layer, count in list(subgraph['nodes_by_layer'].items())[:5]:
                print(f"  {layer}: {count}")
            print(f"\nEdges by type:")
            for edge_type, count in list(subgraph['edges_by_type'].items())[:5]:
                print(f"  {edge_type}: {count}")
        
        # Test 3: Find related entities
        print("\n" + "=" * 80)
        print("Test 3: Find Related Entities (imports only)")
        print("=" * 80)
        
        if results:
            entity_id = results[0]["entity"]["id"]
            related = retriever.find_related_entities(
                entity_id,
                relation_types=["imports"],
                max_depth=2
            )
            
            print(f"\nFound {len(related)} related entities via imports:")
            for i, rel in enumerate(related[:5], 1):
                print(f"  {i}. {rel['name']} (path length: {rel['path_length']})")
        
        # Test 4: Community detection
        print("\n" + "=" * 80)
        print("Test 4: Entity Community Detection")
        print("=" * 80)
        
        if results:
            entity_id = results[0]["entity"]["id"]
            community = retriever.detect_entity_communities(entity_id)
            
            if "error" not in community:
                print(f"\nCommunity: {community['community_name']}")
                print(f"Size: {community['community_size']} entities")
                print(f"\nSample entities in community:")
                for i, entity in enumerate(community['sample_entities'][:5], 1):
                    print(f"  {i}. {entity['name']} ({entity['type']})")
            else:
                print(f"\n{community['error']}")
        
        print("\n" + "=" * 80)
        print("✓ All GraphRAG integration tests completed successfully")
        print("=" * 80)
        
    finally:
        retriever.close()
        print("\n✓ Graph store connection closed")


if __name__ == "__main__":
    main()
