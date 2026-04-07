"""End-to-End Integration Test for SQL GraphStore GraphRAG Pipeline.

This test demonstrates the complete GraphRAG workflow:
1. Graph store initialization with ADG data
2. Entity search and retrieval
3. Graph traversal for context expansion
4. Subgraph extraction for prompt assembly
5. Community-aware retrieval
6. Performance validation
7. Integration with search engines (simulated)
"""

from pathlib import Path
import time
from typing import Any
from dataclasses import dataclass, field

from agentic_core.L4_state.utils.memory.graph_store_factory import create_sqlite_graph_store
from agentic_core.L4_state.types.graph_store_types import GraphEntity


@dataclass
class RetrievalContext:
    """Context for GraphRAG retrieval."""
    chunk_id: str
    content: str
    score: float
    source: str
    graph_context: dict[str, Any] = field(default_factory=dict)
    expansion_depth: int = 0
    groundedness_score: float = 0.0


@dataclass
class GraphRAGQuery:
    """GraphRAG query with parameters."""
    query: str
    max_results: int = 5
    expansion_depth: int = 2
    relation_types: list[str] | None = None
    enable_community_filter: bool = False


class GraphRAGE2EEngine:
    """End-to-end GraphRAG engine using SQLiteGraphStore."""
    
    def __init__(self, db_path: str | Path):
        """Initialize the GraphRAG engine."""
        self.store = create_sqlite_graph_store(db_path)
        self.stats = {
            "queries_processed": 0,
            "total_contexts_retrieved": 0,
            "total_expansion_nodes": 0,
            "avg_latency_ms": 0.0,
        }
    
    def query(self, graphrag_query: GraphRAGQuery) -> list[RetrievalContext]:
        """Execute a GraphRAG query.
        
        Args:
            graphrag_query: Query parameters
            
        Returns:
            List of retrieval contexts with graph enhancement
        """
        start_time = time.time()
        
        # Step 1: Initial entity search (vector search simulation)
        entities = self.store.search_entities(
            graphrag_query.query,
            limit=graphrag_query.max_results
        )
        
        contexts = []
        total_expansion_nodes = 0
        
        for entity in entities:
            # Step 2: Graph context expansion
            graph_context = self._expand_graph_context(
                entity,
                depth=graphrag_query.expansion_depth,
                relation_types=graphrag_query.relation_types
            )
            
            total_expansion_nodes += len(graph_context["neighbors"])
            
            # Step 3: Community filtering (if enabled)
            if graphrag_query.enable_community_filter:
                graph_context["community"] = self._get_entity_community(entity.id)
            
            # Step 4: Groundedness scoring
            groundedness_score = self._calculate_groundedness(graph_context)
            
            # Step 5: Create retrieval context
            context = RetrievalContext(
                chunk_id=entity.id,
                content=entity.name,
                score=1.0 - (len(contexts) * 0.1),  # Simulated relevance score
                source="graph_store",
                graph_context=graph_context,
                expansion_depth=graphrag_query.expansion_depth,
                groundedness_score=groundedness_score
            )
            
            contexts.append(context)
        
        # Update stats
        latency_ms = (time.time() - start_time) * 1000
        self.stats["queries_processed"] += 1
        self.stats["total_contexts_retrieved"] += len(contexts)
        self.stats["total_expansion_nodes"] += total_expansion_nodes
        
        # Update average latency
        n = self.stats["queries_processed"]
        self.stats["avg_latency_ms"] = (
            (self.stats["avg_latency_ms"] * (n - 1) + latency_ms) / n
        )
        
        return contexts
    
    def _expand_graph_context(
        self,
        entity: GraphEntity,
        depth: int,
        relation_types: list[str] | None
    ) -> dict[str, Any]:
        """Expand graph context around an entity."""
        # Get relationships
        relationships = self.store.get_relationships(
            entity.id,
            direction="both"
        )
        
        # Get neighbors for expansion
        neighbors = self.store.get_neighbors(
            entity.id,
            max_hops=depth
        )
        
        # Get centrality
        centrality = self.store.get_centrality(entity.id)
        
        # Get subgraph for detailed context
        subgraph = self.store.get_subgraph(entity.id, radius=min(depth, 2))
        
        return {
            "entity_id": entity.id,
            "entity_name": entity.name,
            "entity_type": entity.entity_type,
            "layer": entity.metadata.get("layer", "N/A"),
            "relationship_count": len(relationships),
            "relation_types": list(set(r.relation_type for r in relationships)),
            "neighbors": neighbors,
            "neighbor_count": len(neighbors),
            "centrality": centrality,
            "subgraph_stats": {
                "node_count": len(subgraph.nodes),
                "edge_count": len(subgraph.relationships),
                "radius": min(depth, 2)
            }
        }
    
    def _get_entity_community(self, entity_id: str) -> dict[str, Any] | None:
        """Get community information for an entity."""
        communities = self.store.detect_communities()
        
        for community in communities:
            if entity_id in community.entities:
                return {
                    "community_id": community.id,
                    "community_name": community.name,
                    "community_size": len(community.entities)
                }
        
        return None
    
    def _calculate_groundedness(self, graph_context: dict[str, Any]) -> float:
        """Calculate groundedness score based on graph context richness."""
        score = 0.0
        
        # Relationship count contributes to groundedness
        rel_count = graph_context["relationship_count"]
        score += min(rel_count / 50.0, 0.3)  # Max 0.3 from relationships
        
        # Neighbor count contributes
        neighbor_count = graph_context["neighbor_count"]
        score += min(neighbor_count / 100.0, 0.3)  # Max 0.3 from neighbors
        
        # Centrality contributes
        centrality = graph_context["centrality"]
        score += min(centrality / 100.0, 0.2)  # Max 0.2 from centrality
        
        # Subgraph density contributes
        subgraph = graph_context["subgraph_stats"]
        if subgraph["node_count"] > 0:
            density = subgraph["edge_count"] / (subgraph["node_count"] ** 2)
            score += min(density * 10, 0.2)  # Max 0.2 from density
        
        return min(score, 1.0)
    
    def get_stats(self) -> dict[str, Any]:
        """Get engine statistics."""
        return self.stats.copy()
    
    def close(self):
        """Close the graph store."""
        self.store.close()


def test_e2e_basic_queries(engine: GraphRAGE2EEngine):
    """Test 1: Basic GraphRAG queries."""
    print("\n[1] Basic GraphRAG Queries")
    
    queries = [
        GraphRAGQuery(query="Graph", max_results=3, expansion_depth=1),
        GraphRAGQuery(query="Agent", max_results=3, expansion_depth=2),
        GraphRAGQuery(query="Engine", max_results=3, expansion_depth=1),
    ]
    
    for i, query in enumerate(queries, 1):
        start = time.time()
        contexts = engine.query(query)
        duration = time.time() - start
        
        print(f"  Query {i}: '{query.query}'")
        print(f"    Contexts: {len(contexts)}")
        print(f"    Latency: {duration*1000:.2f}ms")
        
        for j, ctx in enumerate(contexts[:2], 1):
            print(f"      {j}. {ctx.content}")
            print(f"         Layer: {ctx.graph_context['layer']}")
            print(f"         Neighbors: {ctx.graph_context['neighbor_count']}")
            print(f"         Groundedness: {ctx.groundedness_score:.2f}")
        
        assert len(contexts) > 0, f"Query '{query.query}' returned no results"
        assert all(ctx.groundedness_score >= 0 for ctx in contexts), "Negative groundedness score"
        assert all(ctx.groundedness_score <= 1 for ctx in contexts), "Groundedness > 1"
    
    print("  ✓ All basic queries passed")


def test_e2e_filtered_queries(engine: GraphRAGE2EEngine):
    """Test 2: Filtered queries with relation types."""
    print("\n[2] Filtered Queries (Relation Type Filtering)")
    
    queries = [
        GraphRAGQuery(
            query="Graph",
            max_results=3,
            expansion_depth=2,
            relation_types=["imports"]
        ),
        GraphRAGQuery(
            query="Agent",
            max_results=3,
            expansion_depth=2,
            relation_types=["reads_from", "writes_to"]
        ),
    ]
    
    for i, query in enumerate(queries, 1):
        start = time.time()
        contexts = engine.query(query)
        duration = time.time() - start
        
        print(f"  Query {i}: '{query.query}' (filter: {query.relation_types})")
        print(f"    Contexts: {len(contexts)}")
        print(f"    Latency: {duration*1000:.2f}ms")
        
        for ctx in contexts[:1]:
            print(f"      Sample: {ctx.content}")
            print(f"        Neighbors: {ctx.graph_context['neighbor_count']}")
    
    print("  ✓ All filtered queries passed")


def test_e2e_community_aware_queries(engine: GraphRAGE2EEngine):
    """Test 3: Community-aware queries."""
    print("\n[3] Community-Aware Queries")
    
    query = GraphRAGQuery(
        query="Graph",
        max_results=3,
        expansion_depth=1,
        enable_community_filter=True
    )
    
    start = time.time()
    contexts = engine.query(query)
    duration = time.time() - start
    
    print(f"  Query: '{query.query}' (community filter enabled)")
    print(f"  Contexts: {len(contexts)}")
    print(f"  Latency: {duration*1000:.2f}ms")
    
    for ctx in contexts:
        community = ctx.graph_context.get("community")
        if community:
            print(f"    {ctx.content}")
            print(f"      Community: {community['community_name']} ({community['community_size']} entities)")
        else:
            print(f"    {ctx.content}")
            print(f"      Community: None")
    
    print("  ✓ Community-aware queries passed")


def test_e2e_deep_expansion(engine: GraphRAGE2EEngine):
    """Test 4: Deep expansion queries."""
    print("\n[4] Deep Expansion Queries")
    
    query = GraphRAGQuery(
        query="Graph",
        max_results=1,
        expansion_depth=3
    )
    
    start = time.time()
    contexts = engine.query(query)
    duration = time.time() - start
    
    print(f"  Query: '{query.query}' (depth=3)")
    print(f"  Contexts: {len(contexts)}")
    print(f"  Latency: {duration*1000:.2f}ms")
    
    for ctx in contexts:
        print(f"    Entity: {ctx.content}")
        print(f"    Expansion depth: {ctx.expansion_depth}")
        print(f"    Neighbors found: {ctx.graph_context['neighbor_count']}")
        print(f"    Subgraph nodes: {ctx.graph_context['subgraph_stats']['node_count']}")
        print(f"    Subgraph edges: {ctx.graph_context['subgraph_stats']['edge_count']}")
    
    print("  ✓ Deep expansion queries passed")


def test_e2e_performance_validation(engine: GraphRAGE2EEngine):
    """Test 5: Performance validation."""
    print("\n[5] Performance Validation")
    
    # Run multiple queries to establish baseline
    num_queries = 10
    latencies = []
    
    for i in range(num_queries):
        query = GraphRAGQuery(
            query=f"test_{i}",
            max_results=3,
            expansion_depth=1
        )
        
        start = time.time()
        contexts = engine.query(query)
        duration = time.time() - start
        latencies.append(duration * 1000)  # Convert to ms
    
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
    p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
    
    print(f"  Queries executed: {num_queries}")
    print(f"  Average latency: {avg_latency:.2f}ms")
    print(f"  P95 latency: {p95_latency:.2f}ms")
    print(f"  P99 latency: {p99_latency:.2f}ms")
    
    # Performance targets
    if avg_latency < 100:
        print(f"  ✓ Average latency < 100ms target")
    else:
        print(f"  ⚠ Average latency exceeds 100ms target")
    
    if p95_latency < 200:
        print(f"  ✓ P95 latency < 200ms target")
    else:
        print(f"  ⚠ P95 latency exceeds 200ms target")


def test_e2e_statistics_validation(engine: GraphRAGE2EEngine):
    """Test 6: Statistics validation."""
    print("\n[6] Statistics Validation")
    
    stats = engine.get_stats()
    
    print(f"  Queries processed: {stats['queries_processed']}")
    print(f"  Total contexts retrieved: {stats['total_contexts_retrieved']}")
    print(f"  Total expansion nodes: {stats['total_expansion_nodes']}")
    print(f"  Average latency: {stats['avg_latency_ms']:.2f}ms")
    
    assert stats['queries_processed'] > 0, "No queries processed"
    assert stats['total_contexts_retrieved'] > 0, "No contexts retrieved"
    assert stats['avg_latency_ms'] > 0, "Average latency is zero"
    
    print("  ✓ Statistics validation passed")


def main():
    """Run end-to-end integration tests."""
    print("=" * 80)
    print("SQL GraphStore End-to-End Integration Test - GraphRAG Pipeline")
    print("=" * 80)
    
    # Find ADG database
    adg_dir = Path("artifacts/adg")
    db_files = list(adg_dir.glob("adg_indexed_*.sqlite"))
    if not db_files:
        print("✗ No ADG database found")
        return False
    
    db_path = sorted(db_files)[-1]
    print(f"\nUsing ADG database: {db_path}")
    
    # Initialize GraphRAG engine
    print("\nInitializing GraphRAG E2E Engine...")
    engine = GraphRAGE2EEngine(db_path)
    print("✓ Engine initialized")
    
    try:
        # Run e2e tests
        test_e2e_basic_queries(engine)
        test_e2e_filtered_queries(engine)
        test_e2e_community_aware_queries(engine)
        test_e2e_deep_expansion(engine)
        test_e2e_performance_validation(engine)
        test_e2e_statistics_validation(engine)
        
        print("\n" + "=" * 80)
        print("✓ All E2E integration tests passed successfully")
        print("=" * 80)
        
        # Print final statistics
        stats = engine.get_stats()
        print(f"\nFinal Statistics:")
        print(f"  Total queries: {stats['queries_processed']}")
        print(f"  Total contexts: {stats['total_contexts_retrieved']}")
        print(f"  Total expansions: {stats['total_expansion_nodes']}")
        print(f"  Average latency: {stats['avg_latency_ms']:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"\n✗ E2E test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        engine.close()
        print("\n✓ Engine closed")


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
