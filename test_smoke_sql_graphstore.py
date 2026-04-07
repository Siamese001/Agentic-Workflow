"""Comprehensive Smoke Test Suite for SQLiteGraphStore.

Smoke tests validate the entire graph store stack:
- Database connectivity and schema validation
- Core operations (CRUD, search, traversal)
- Graph algorithms (path finding, centrality, communities)
- Performance benchmarks
- Error handling and edge cases
- Integration with ADG data
"""

from pathlib import Path
import time
import sqlite3
from typing import Any

from agentic_core.L4_state.utils.memory.graph_store_factory import (
    create_sqlite_graph_store,
    create_sqlite_graph_store_or_none,
    get_default_adg_db_path,
)
from agentic_core.L4_state.types.graph_store_types import (
    GraphEntity,
    GraphRelationship,
    GraphPath,
    GraphSubgraph,
    GraphCommunity,
)


class SmokeTestResults:
    """Track smoke test results."""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def record_pass(self, test_name: str, duration: float):
        """Record a passing test."""
        self.passed.append((test_name, duration))
        print(f"  ✓ {test_name} ({duration:.3f}s)")
    
    def record_fail(self, test_name: str, error: str):
        """Record a failing test."""
        self.failed.append((test_name, error))
        print(f"  ✗ {test_name}: {error}")
    
    def record_warning(self, test_name: str, message: str):
        """Record a warning."""
        self.warnings.append((test_name, message))
        print(f"  ⚠ {test_name}: {message}")
    
    def summary(self):
        """Print summary."""
        total = len(self.passed) + len(self.failed)
        print(f"\n{'='*80}")
        print(f"Smoke Test Summary: {len(self.passed)}/{total} passed, {len(self.failed)} failed, {len(self.warnings)} warnings")
        print(f"{'='*80}")
        
        if self.failed:
            print("\nFailed Tests:")
            for test_name, error in self.failed:
                print(f"  ✗ {test_name}: {error}")
        
        if self.warnings:
            print("\nWarnings:")
            for test_name, message in self.warnings:
                print(f"  ⚠ {test_name}: {message}")
        
        return len(self.failed) == 0


def test_database_connectivity(results: SmokeTestResults, db_path: Path):
    """Test 1: Database connectivity and schema validation."""
    print("\n[1] Database Connectivity and Schema Validation")
    
    start = time.time()
    try:
        # Test SQLite connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Validate required tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        required_tables = {'nodes', 'edges', 'meta', 'violations'}
        missing_tables = required_tables - tables
        
        if missing_tables:
            results.record_fail(
                "Database Schema",
                f"Missing tables: {missing_tables}"
            )
            return
        
        # Validate node schema
        cursor.execute("PRAGMA table_info(nodes)")
        node_columns = {row[1] for row in cursor.fetchall()}
        required_node_columns = {'id', 'adg_name', 'entity_type', 'layer', 'resolved_path'}
        missing_node_columns = required_node_columns - node_columns
        
        if missing_node_columns:
            results.record_warning(
                "Node Schema",
                f"Missing columns: {missing_node_columns}"
            )
        
        # Validate edge schema
        cursor.execute("PRAGMA table_info(edges)")
        edge_columns = {row[1] for row in cursor.fetchall()}
        required_edge_columns = {'src_id', 'dst_id', 'relation_type', 'edge_kind'}
        missing_edge_columns = required_edge_columns - edge_columns
        
        if missing_edge_columns:
            results.record_warning(
                "Edge Schema",
                f"Missing columns: {missing_edge_columns}"
            )
        
        # Get graph statistics
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]
        
        conn.close()
        
        duration = time.time() - start
        results.record_pass(
            f"Database Connectivity ({node_count} nodes, {edge_count} edges)",
            duration
        )
        
    except Exception as e:
        results.record_fail("Database Connectivity", str(e))


def test_factory_functions(results: SmokeTestResults, db_path: Path):
    """Test 2: Factory functions."""
    print("\n[2] Factory Functions")
    
    # Test get_default_adg_db_path
    start = time.time()
    try:
        default_path = get_default_adg_db_path()
        if default_path is None:
            results.record_warning(
                "get_default_adg_db_path",
                "Returns None (expected if no symlink exists)"
            )
        else:
            results.record_pass("get_default_adg_db_path", time.time() - start)
    except Exception as e:
        results.record_fail("get_default_adg_db_path", str(e))
    
    # Test create_sqlite_graph_store
    start = time.time()
    try:
        store = create_sqlite_graph_store(db_path)
        store.close()
        results.record_pass("create_sqlite_graph_store", time.time() - start)
    except Exception as e:
        results.record_fail("create_sqlite_graph_store", str(e))
    
    # Test create_sqlite_graph_store_or_none
    start = time.time()
    try:
        store = create_sqlite_graph_store_or_none(db_path)
        if store is None:
            results.record_fail("create_sqlite_graph_store_or_none", "Returned None for valid path")
        else:
            store.close()
            results.record_pass("create_sqlite_graph_store_or_none", time.time() - start)
    except Exception as e:
        results.record_fail("create_sqlite_graph_store_or_none", str(e))
    
    # Test create_sqlite_graph_store_or_none with invalid path
    start = time.time()
    try:
        store = create_sqlite_graph_store_or_none("/invalid/path")
        if store is not None:
            results.record_fail(
                "create_sqlite_graph_store_or_none (invalid path)",
                "Should return None for invalid path"
            )
        else:
            results.record_pass(
                "create_sqlite_graph_store_or_none (invalid path)",
                time.time() - start
            )
    except Exception as e:
        results.record_fail("create_sqlite_graph_store_or_none (invalid path)", str(e))


def test_entity_operations(results: SmokeTestResults, store):
    """Test 3: Entity operations."""
    print("\n[3] Entity Operations")
    
    # Test get_entity with valid ID
    start = time.time()
    try:
        entity = store.get_entity("1")
        if entity is None:
            results.record_warning("get_entity(id=1)", "Entity ID 1 not found")
        else:
            assert isinstance(entity, GraphEntity)
            assert entity.id == "1"
            assert entity.name is not None
            assert entity.entity_type is not None
            results.record_pass("get_entity(id=1)", time.time() - start)
    except Exception as e:
        results.record_fail("get_entity(id=1)", str(e))
    
    # Test get_entity with invalid ID
    start = time.time()
    try:
        entity = store.get_entity("999999999")
        if entity is not None:
            results.record_fail("get_entity(invalid)", "Should return None for invalid ID")
        else:
            results.record_pass("get_entity(invalid)", time.time() - start)
    except Exception as e:
        results.record_fail("get_entity(invalid)", str(e))
    
    # Test search_entities
    start = time.time()
    try:
        results_list = store.search_entities("Agent", limit=10)
        assert isinstance(results_list, list)
        for entity in results_list:
            assert isinstance(entity, GraphEntity)
        results.record_pass(f"search_entities('Agent', n={len(results_list)})", time.time() - start)
    except Exception as e:
        results.record_fail("search_entities", str(e))
    
    # Test search_entities with empty query
    start = time.time()
    try:
        results_list = store.search_entities("", limit=5)
        assert isinstance(results_list, list)
        results.record_pass(f"search_entities('', n={len(results_list)})", time.time() - start)
    except Exception as e:
        results.record_fail("search_entities(empty)", str(e))
    
    # Test add_entity (should raise NotImplementedError)
    start = time.time()
    try:
        entity = GraphEntity(
            id="test",
            name="Test",
            entity_type="test"
        )
        store.add_entity(entity)
        results.record_fail("add_entity", "Should raise NotImplementedError (read-only)")
    except NotImplementedError:
        results.record_pass("add_entity (read-only)", time.time() - start)
    except Exception as e:
        results.record_fail("add_entity", f"Wrong exception: {e}")


def test_relationship_operations(results: SmokeTestResults, store):
    """Test 4: Relationship operations."""
    print("\n[4] Relationship Operations")
    
    # Get a valid entity ID
    entity = store.get_entity("1")
    if entity is None:
        results.record_fail("Relationship Operations", "No valid entity found")
        return
    
    entity_id = entity.id
    
    # Test get_relationships (outgoing)
    start = time.time()
    try:
        rels = store.get_relationships(entity_id, direction="outgoing")
        assert isinstance(rels, list)
        for rel in rels:
            assert isinstance(rel, GraphRelationship)
        results.record_pass(f"get_relationships(outgoing, n={len(rels)})", time.time() - start)
    except Exception as e:
        results.record_fail("get_relationships(outgoing)", str(e))
    
    # Test get_relationships (incoming)
    start = time.time()
    try:
        rels = store.get_relationships(entity_id, direction="incoming")
        assert isinstance(rels, list)
        results.record_pass(f"get_relationships(incoming, n={len(rels)})", time.time() - start)
    except Exception as e:
        results.record_fail("get_relationships(incoming)", str(e))
    
    # Test get_relationships (both)
    start = time.time()
    try:
        rels = store.get_relationships(entity_id, direction="both")
        assert isinstance(rels, list)
        results.record_pass(f"get_relationships(both, n={len(rels)})", time.time() - start)
    except Exception as e:
        results.record_fail("get_relationships(both)", str(e))


def test_traversal_operations(results: SmokeTestResults, store):
    """Test 5: Traversal operations."""
    print("\n[5] Traversal Operations")
    
    # Get a valid entity ID
    results_list = store.search_entities("Graph", limit=1)
    if not results_list:
        results_list = store.search_entities("", limit=1)
    
    if not results_list:
        results.record_fail("Traversal Operations", "No entities found")
        return
    
    start_id = results_list[0].id
    
    # Test traverse (depth 1)
    start = time.time()
    try:
        paths = store.traverse(start_id, max_depth=1)
        assert isinstance(paths, list)
        for path in paths:
            assert isinstance(path, GraphPath)
        results.record_pass(f"traverse(depth=1, paths={len(paths)})", time.time() - start)
    except Exception as e:
        results.record_fail("traverse(depth=1)", str(e))
    
    # Test traverse (depth 2)
    start = time.time()
    try:
        paths = store.traverse(start_id, max_depth=2)
        assert isinstance(paths, list)
        results.record_pass(f"traverse(depth=2, paths={len(paths)})", time.time() - start)
    except Exception as e:
        results.record_fail("traverse(depth=2)", str(e))
    
    # Test traverse with relation type filter
    start = time.time()
    try:
        paths = store.traverse(start_id, max_depth=2, relation_types=["imports"])
        assert isinstance(paths, list)
        results.record_pass(f"traverse(filtered, paths={len(paths)})", time.time() - start)
    except Exception as e:
        results.record_fail("traverse(filtered)", str(e))
    
    # Test get_neighbors (1-hop)
    start = time.time()
    try:
        neighbors = store.get_neighbors(start_id, max_hops=1)
        assert isinstance(neighbors, list)
        for neighbor in neighbors:
            assert isinstance(neighbor, GraphEntity)
        results.record_pass(f"get_neighbors(1-hop, n={len(neighbors)})", time.time() - start)
    except Exception as e:
        results.record_fail("get_neighbors(1-hop)", str(e))
    
    # Test get_neighbors (2-hop)
    start = time.time()
    try:
        neighbors = store.get_neighbors(start_id, max_hops=2)
        assert isinstance(neighbors, list)
        results.record_pass(f"get_neighbors(2-hop, n={len(neighbors)})", time.time() - start)
    except Exception as e:
        results.record_fail("get_neighbors(2-hop)", str(e))


def test_path_finding(results: SmokeTestResults, store):
    """Test 6: Path finding."""
    print("\n[6] Path Finding")
    
    # Get two entity IDs
    results_list = store.search_entities("", limit=2)
    if len(results_list) < 2:
        results.record_fail("Path Finding", "Not enough entities")
        return
    
    src_id = results_list[0].id
    dst_id = results_list[1].id
    
    # Test find_shortest_path
    start = time.time()
    try:
        path = store.find_shortest_path(src_id, dst_id)
        if path is not None:
            assert isinstance(path, GraphPath)
            results.record_pass(f"find_shortest_path (found, cost={path.cost})", time.time() - start)
        else:
            results.record_pass("find_shortest_path (not found)", time.time() - start)
    except Exception as e:
        results.record_fail("find_shortest_path", str(e))
    
    # Test find_shortest_path (same node)
    start = time.time()
    try:
        path = store.find_shortest_path(src_id, src_id)
        if path is not None:
            assert path.cost == 0.0
            results.record_pass("find_shortest_path (same node)", time.time() - start)
        else:
            results.record_fail("find_shortest_path (same node)", "Should return path with cost 0")
    except Exception as e:
        results.record_fail("find_shortest_path (same node)", str(e))


def test_subgraph_operations(results: SmokeTestResults, store):
    """Test 7: Subgraph operations."""
    print("\n[7] Subgraph Operations")
    
    # Get a valid entity ID
    results_list = store.search_entities("Graph", limit=1)
    if not results_list:
        results_list = store.search_entities("", limit=1)
    
    if not results_list:
        results.record_fail("Subgraph Operations", "No entities found")
        return
    
    center_id = results_list[0].id
    
    # Test get_subgraph (radius 1)
    start = time.time()
    try:
        subgraph = store.get_subgraph(center_id, radius=1)
        assert isinstance(subgraph, GraphSubgraph)
        assert isinstance(subgraph.nodes, list)
        assert isinstance(subgraph.relationships, list)
        results.record_pass(
            f"get_subgraph(radius=1, {len(subgraph.nodes)} nodes, {len(subgraph.relationships)} edges)",
            time.time() - start
        )
    except Exception as e:
        results.record_fail("get_subgraph(radius=1)", str(e))
    
    # Test get_subgraph (radius 2)
    start = time.time()
    try:
        subgraph = store.get_subgraph(center_id, radius=2)
        assert isinstance(subgraph, GraphSubgraph)
        results.record_pass(
            f"get_subgraph(radius=2, {len(subgraph.nodes)} nodes, {len(subgraph.relationships)} edges)",
            time.time() - start
        )
    except Exception as e:
        results.record_fail("get_subgraph(radius=2)", str(e))


def test_centrality_operations(results: SmokeTestResults, store):
    """Test 8: Centrality operations."""
    print("\n[8] Centrality Operations")
    
    # Get a valid entity ID
    results_list = store.search_entities("Graph", limit=1)
    if not results_list:
        results_list = store.search_entities("", limit=1)
    
    if not results_list:
        results.record_fail("Centrality Operations", "No entities found")
        return
    
    entity_id = results_list[0].id
    
    # Test get_centrality
    start = time.time()
    try:
        centrality = store.get_centrality(entity_id)
        assert isinstance(centrality, float)
        assert centrality >= 0.0
        results.record_pass(f"get_centrality (score={centrality})", time.time() - start)
    except Exception as e:
        results.record_fail("get_centrality", str(e))


def test_community_operations(results: SmokeTestResults, store):
    """Test 9: Community operations."""
    print("\n[9] Community Operations")
    
    # Test detect_communities
    start = time.time()
    try:
        communities = store.detect_communities()
        assert isinstance(communities, list)
        for community in communities:
            assert isinstance(community, GraphCommunity)
        results.record_pass(f"detect_communities (n={len(communities)})", time.time() - start)
    except Exception as e:
        results.record_fail("detect_communities", str(e))
    
    # Test get_community (if any communities found)
    if communities:
        start = time.time()
        try:
            community = store.get_community(communities[0].id)
            if community is not None:
                assert isinstance(community, GraphCommunity)
                results.record_pass("get_community", time.time() - start)
            else:
                results.record_fail("get_community", "Should not return None for valid ID")
        except Exception as e:
            results.record_fail("get_community", str(e))


def test_performance_benchmarks(results: SmokeTestResults, store):
    """Test 10: Performance benchmarks."""
    print("\n[10] Performance Benchmarks")
    
    # Benchmark: Single entity lookup
    entity = store.get_entity("1")
    if entity:
        start = time.time()
        for _ in range(100):
            store.get_entity("1")
        duration = time.time() - start
        avg_time = duration / 100
        results.record_pass(f"Entity lookup (100x, avg={avg_time*1000:.2f}ms)", duration)
        
        if avg_time > 0.01:  # 10ms threshold
            results.record_warning("Entity lookup performance", f"Avg {avg_time*1000:.2f}ms exceeds 10ms threshold")
    
    # Benchmark: Relationship query
    rels = store.get_relationships(entity.id, direction="both")
    if rels:
        start = time.time()
        for _ in range(100):
            store.get_relationships(entity.id, direction="both")
        duration = time.time() - start
        avg_time = duration / 100
        results.record_pass(f"Relationship query (100x, avg={avg_time*1000:.2f}ms)", duration)
        
        if avg_time > 0.01:  # 10ms threshold
            results.record_warning("Relationship query performance", f"Avg {avg_time*1000:.2f}ms exceeds 10ms threshold")


def test_error_handling(results: SmokeTestResults):
    """Test 11: Error handling."""
    print("\n[11] Error Handling")
    
    # Test invalid database path
    start = time.time()
    try:
        store = create_sqlite_graph_store("/nonexistent/path/to/db.sqlite")
        results.record_fail("Invalid database path", "Should raise FileNotFoundError")
    except FileNotFoundError:
        results.record_pass("Invalid database path (FileNotFoundError)", time.time() - start)
    except Exception as e:
        results.record_fail("Invalid database path", f"Wrong exception: {e}")
    
    # Test directory as database path
    start = time.time()
    try:
        store = create_sqlite_graph_store("/")
        results.record_fail("Directory as database path", "Should raise FileNotFoundError")
    except FileNotFoundError:
        results.record_pass("Directory as database path (FileNotFoundError)", time.time() - start)
    except Exception as e:
        results.record_fail("Directory as database path", f"Wrong exception: {e}")


def test_context_manager(results: SmokeTestResults, db_path: Path):
    """Test 12: Context manager."""
    print("\n[12] Context Manager")
    
    start = time.time()
    try:
        with create_sqlite_graph_store(db_path) as store:
            entity = store.get_entity("1")
            assert entity is not None
        results.record_pass("Context manager (__enter__/__exit__)", time.time() - start)
    except Exception as e:
        results.record_fail("Context manager", str(e))


def main():
    """Run all smoke tests."""
    print("=" * 80)
    print("SQLiteGraphStore Comprehensive Smoke Test Suite")
    print("=" * 80)
    
    # Find ADG database
    adg_dir = Path("artifacts/adg")
    db_files = list(adg_dir.glob("adg_indexed_*.sqlite"))
    if not db_files:
        print("✗ No ADG database found in artifacts/adg/")
        return False
    
    db_path = sorted(db_files)[-1]
    print(f"\nUsing ADG database: {db_path}")
    
    # Initialize results tracker
    results = SmokeTestResults()
    
    # Run smoke tests
    test_database_connectivity(results, db_path)
    test_factory_functions(results, db_path)
    
    # Create store for remaining tests
    try:
        store = create_sqlite_graph_store(db_path)
    except Exception as e:
        print(f"✗ Failed to create graph store: {e}")
        return False
    
    try:
        test_entity_operations(results, store)
        test_relationship_operations(results, store)
        test_traversal_operations(results, store)
        test_path_finding(results, store)
        test_subgraph_operations(results, store)
        test_centrality_operations(results, store)
        test_community_operations(results, store)
        test_performance_benchmarks(results, store)
        
        store.close()
        
        test_error_handling(results)
        test_context_manager(results, db_path)
        
    finally:
        # Ensure store is closed
        try:
            store.close()
        except:
            pass
    
    # Print summary
    success = results.summary()
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
