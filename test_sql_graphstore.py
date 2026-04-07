"""Test SQL Graphstore for Graph RAG and Graph DB Capabilities.

This script demonstrates the SQLiteGraphStore capabilities using the real ADG database.
Tests include:
- Entity retrieval and search
- Relationship queries
- Graph traversal
- Path finding
- Subgraph extraction
- Centrality metrics
- Community detection
"""

import time
from pathlib import Path

from agentic_core.L4_state.utils.memory.graph_store_factory import create_sqlite_graph_store


def time_operation(operation_name: str, func, *args, **kwargs):
    """Time an operation and print the result."""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    print(f"✓ {operation_name}: {elapsed:.3f}s")
    return result


def test_entity_operations(store):
    """Test entity retrieval and search."""
    print("\n=== Testing Entity Operations ===")

    # Test get_entity with a known ID (try ID 1)
    entity = time_operation("get_entity(id=1)", store.get_entity, "1")
    if entity:
        print(f"  Found entity: {entity.name} (type: {entity.entity_type})")
        print(f"  Layer: {entity.metadata.get('layer', 'N/A')}")
        print(f"  File: {entity.metadata.get('file_path', 'N/A')}")
    else:
        print("  Entity ID 1 not found")

    # Test search_entities
    results = time_operation("search_entities('Graph')", store.search_entities, "Graph", limit=5)
    print(f"  Found {len(results)} results for 'Graph'")
    for i, e in enumerate(results[:3]):
        print(f"    {i+1}. {e.name} ({e.entity_type})")

    # Test search for common terms
    for term in ["Agent", "Engine", "Store"]:
        results = store.search_entities(term, limit=3)
        print(f"  Search '{term}': {len(results)} results")


def test_relationship_operations(store):
    """Test relationship queries."""
    print("\n=== Testing Relationship Operations ===")

    # Get a sample entity ID
    entity = store.get_entity("1")
    if entity:
        entity_id = entity.id
    else:
        # Find first entity
        results = store.search_entities("", limit=1)
        if results:
            entity_id = results[0].id
        else:
            print("  No entities found")
            return

    print(f"  Using entity ID: {entity_id}")

    # Test outgoing relationships
    outgoing = time_operation(
        f"get_relationships(id={entity_id}, direction='outgoing')",
        store.get_relationships,
        entity_id,
        direction="outgoing",
    )
    print(f"  Outgoing relationships: {len(outgoing)}")
    if outgoing:
        print(f"    Sample: {outgoing[0].relation_type} -> {outgoing[0].target_id}")

    # Test incoming relationships
    incoming = time_operation(
        f"get_relationships(id={entity_id}, direction='incoming')",
        store.get_relationships,
        entity_id,
        direction="incoming",
    )
    print(f"  Incoming relationships: {len(incoming)}")

    # Test both directions
    both = time_operation(
        f"get_relationships(id={entity_id}, direction='both')",
        store.get_relationships,
        entity_id,
        direction="both",
    )
    print(f"  Total relationships: {len(both)}")

    # Show unique relation types
    relation_types = set(r.relation_type for r in both)
    print(f"  Unique relation types: {sorted(relation_types)[:10]}")


def test_traversal_operations(store):
    """Test graph traversal."""
    print("\n=== Testing Traversal Operations ===")

    # Get a starting entity
    results = store.search_entities("Graph", limit=1)
    if not results:
        results = store.search_entities("", limit=1)

    if not results:
        print("  No entities found for traversal")
        return

    start_id = results[0].id
    print(f"  Starting from entity: {results[0].name} (ID: {start_id})")

    # Test 1-hop traversal
    paths = time_operation(
        f"traverse(id={start_id}, max_depth=1)",
        store.traverse,
        start_id,
        max_depth=1,
    )
    print(f"  1-hop paths found: {len(paths)}")

    # Test 2-hop traversal
    paths = time_operation(
        f"traverse(id={start_id}, max_depth=2)",
        store.traverse,
        start_id,
        max_depth=2,
    )
    print(f"  2-hop paths found: {len(paths)}")

    # Test filtered traversal
    paths_filtered = time_operation(
        f"traverse(id={start_id}, max_depth=2, relation_types=['imports'])",
        store.traverse,
        start_id,
        max_depth=2,
        relation_types=["imports"],
    )
    print(f"  2-hop paths (imports only): {len(paths_filtered)}")

    # Test get_neighbors
    neighbors = time_operation(
        f"get_neighbors(id={start_id}, max_hops=1)",
        store.get_neighbors,
        start_id,
        max_hops=1,
    )
    print(f"  1-hop neighbors: {len(neighbors)}")

    neighbors_2hop = time_operation(
        f"get_neighbors(id={start_id}, max_hops=2)",
        store.get_neighbors,
        start_id,
        max_hops=2,
    )
    print(f"  2-hop neighbors: {len(neighbors_2hop)}")


def test_path_finding(store):
    """Test shortest path finding."""
    print("\n=== Testing Path Finding ===")

    # Get two entities
    results = store.search_entities("Agent", limit=2)
    if len(results) < 2:
        results = store.search_entities("", limit=2)

    if len(results) < 2:
        print("  Not enough entities for path finding")
        return

    src_id = results[0].id
    dst_id = results[1].id

    print(f"  Finding path: {results[0].name} (ID: {src_id}) -> {results[1].name} (ID: {dst_id})")

    path = time_operation(
        f"find_shortest_path({src_id} -> {dst_id})",
        store.find_shortest_path,
        src_id,
        dst_id,
    )

    if path:
        print(f"  Path found with {len(path.nodes)} nodes and {len(path.relationships)} edges")
        print(f"  Cost: {path.cost}")
        if path.nodes:
            print(f"  Path: {' -> '.join(n.name[:20] for n in path.nodes[:5])}")
    else:
        print("  No path found")


def test_subgraph_extraction(store):
    """Test subgraph extraction."""
    print("\n=== Testing Subgraph Extraction ===")

    # Get a center entity
    results = store.search_entities("Graph", limit=1)
    if not results:
        results = store.search_entities("", limit=1)

    if not results:
        print("  No entities found for subgraph extraction")
        return

    center_id = results[0].id
    print(f"  Extracting subgraph around: {results[0].name} (ID: {center_id})")

    # Test radius-1 subgraph
    subgraph = time_operation(
        f"get_subgraph(id={center_id}, radius=1)",
        store.get_subgraph,
        center_id,
        radius=1,
    )
    print(f"  Subgraph (radius=1): {len(subgraph.nodes)} nodes, {len(subgraph.relationships)} edges")

    # Test radius-2 subgraph
    subgraph = time_operation(
        f"get_subgraph(id={center_id}, radius=2)",
        store.get_subgraph,
        center_id,
        radius=2,
    )
    print(f"  Subgraph (radius=2): {len(subgraph.nodes)} nodes, {len(subgraph.relationships)} edges")


def test_centrality_metrics(store):
    """Test centrality metrics."""
    print("\n=== Testing Centrality Metrics ===")

    # Get a sample entity
    results = store.search_entities("Graph", limit=1)
    if not results:
        results = store.search_entities("", limit=1)

    if not results:
        print("  No entities found for centrality test")
        return

    entity_id = results[0].id
    print(f"  Computing centrality for: {results[0].name} (ID: {entity_id})")

    centrality = time_operation(
        f"get_centrality(id={entity_id})",
        store.get_centrality,
        entity_id,
    )
    print(f"  Degree centrality: {centrality}")

    # Test centrality for multiple entities
    results = store.search_entities("", limit=5)
    print("\n  Centrality for top 5 entities:")
    for entity in results:
        centrality = store.get_centrality(entity.id)
        print(f"    {entity.name[:30]:30} : {centrality}")


def test_community_detection(store):
    """Test community detection."""
    print("\n=== Testing Community Detection ===")

    # Test with connected components (fast)
    print("  Running community detection (connected components on imports graph)...")
    communities = time_operation(
        "detect_communities(algorithm='leiden')",
        store.detect_communities,
        algorithm="leiden",
    )

    print(f"  Communities detected: {len(communities)}")

    if communities:
        # Show top 5 communities by size
        sorted_communities = sorted(communities, key=lambda c: len(c.entities), reverse=True)[:5]
        print("\n  Top 5 communities by size:")
        for i, community in enumerate(sorted_communities):
            print(f"    {i+1}. {community.name}: {len(community.entities)} entities")
            if community.entities:
                # Get sample entity names
                sample_ids = community.entities[:3]
                sample_names = []
                for eid in sample_ids:
                    entity = store.get_entity(eid)
                    if entity:
                        sample_names.append(entity.name[:20])
                print(f"       Sample: {', '.join(sample_names)}")

    # Test get_community
    if communities:
        community_id = communities[0].id
        community = time_operation(
            f"get_community(id={community_id})",
            store.get_community,
            community_id,
        )
        if community:
            print(f"\n  Retrieved community: {community.name} with {len(community.entities)} entities")


def main():
    """Main test function."""
    print("=" * 80)
    print("SQL Graphstore for Graph RAG and Graph DB Capabilities Test")
    print("=" * 80)

    # Initialize graph store with ADG database
    print("\nInitializing SQLiteGraphStore with ADG database...")

    # Find the actual ADG database file
    adg_dir = Path("artifacts/adg")
    if adg_dir.exists():
        db_files = list(adg_dir.glob("adg_indexed_*.sqlite"))
        if db_files:
            # Use the most recent database
            db_path = sorted(db_files)[-1]
            print(f"  Found ADG database: {db_path}")
        else:
            print(f"✗ No ADG database found in {adg_dir}")
            return
    else:
        print(f"✗ ADG directory not found: {adg_dir}")
        return

    try:
        store = create_sqlite_graph_store(db_path=db_path)
        print("✓ Graph store initialized successfully")
    except FileNotFoundError as e:
        print(f"✗ Failed to initialize graph store: {e}")
        return

    # Run all tests
    try:
        test_entity_operations(store)
        test_relationship_operations(store)
        test_traversal_operations(store)
        test_path_finding(store)
        test_subgraph_extraction(store)
        test_centrality_metrics(store)
        test_community_detection(store)

        print("\n" + "=" * 80)
        print("✓ All tests completed successfully")
        print("=" * 80)

    finally:
        store.close()
        print("\n✓ Graph store connection closed")


if __name__ == "__main__":
    main()
