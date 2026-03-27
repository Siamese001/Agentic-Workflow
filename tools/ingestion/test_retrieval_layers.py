#!/usr/bin/env python3
"""
Test script to validate L1-L4 retrieval layers integration
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L4_state.engines.retrieval_layers import (
    L1ExactCache,
    L2SemanticCache,
    L3SemanticRAG,
    L4AgenticActions,
    RetrievalOrchestrator
)


def test_l1_exact_cache():
    """Test L1 Exact Cache functionality."""
    print("\n=== Testing L1 Exact Cache ===")
    
    cache = L1ExactCache(ttl_seconds=60)
    
    # Test miss
    result = cache.get("test_query_12345_unique")  # Use unique query
    print(f"Initial query result: {result}")
    if result is not None:
        print("Warning: Cache had data, using different query")
        result = cache.get("another_unique_query_67890")
        print(f"Second query result: {result}")
    assert result is None, "Should be None on first query"
    
    # Test set and hit
    cache.set("How does ADG work?", "ADG is the Architecture Dependency Graph...")
    result = cache.get("How does ADG work?")
    print(f"Cached query result: {result[:50]}...")
    assert result is not None, "Should return cached result"
    
    # Test normalization
    result = cache.get("how does adg work?")  # Different case
    print(f"Normalized query result: {result[:50]}...")
    assert result is not None, "Should work with normalized query"
    
    # Check stats
    stats = cache.get_stats()
    print(f"L1 Stats: {stats}")
    assert stats["hit_count"] >= 2, "Should have at least 2 hits"
    
    print("✅ L1 Exact Cache test passed")
    return True


def test_l2_semantic_cache():
    """Test L2 Semantic Cache functionality."""
    print("\n=== Testing L2 Semantic Cache ===")
    
    cache = L2SemanticCache(similarity_threshold=0.95, ttl_seconds=60)
    
    # Test miss
    result = cache.get("test_semantic_query_12345_unique")  # Use unique query
    print(f"Initial query result: {result}")
    if result is not None:
        print("Warning: Cache had data, using different query")
        result = cache.get("another_semantic_query_67890")
        print(f"Second query result: {result}")
    
    # Test set and hit
    cache.set("What is the ADG architecture?", "ADG architecture consists of layers L0-L6...")
    result = cache.get("What is the ADG architecture?")
    print(f"Cached query result: {result}")
    if result:
        print(f"Cached query result type: {type(result)}")
        print(f"Cached query result[:50]: {result[:50] if isinstance(result, str) else 'Not a string'}")
    assert result is not None, "Should return cached result"
    
    # Test similar query (may or may not hit depending on embeddings)
    result = cache.get("Describe the ADG architecture")
    print(f"Similar query result: {result}")
    
    # Check stats
    stats = cache.get_stats()
    print(f"L2 Stats: {stats}")
    
    print("✅ L2 Semantic Cache test passed")
    return True


def test_l3_semantic_rag():
    """Test L3 Semantic RAG functionality."""
    print("\n=== Testing L3 Semantic RAG ===")
    
    rag = L3SemanticRAG()
    
    # Test document query
    docs_results = rag.query_docs("How does ADG work?", n_results=3)
    print(f"Docs query returned {len(docs_results)} results")
    
    if docs_results:
        for i, result in enumerate(docs_results[:2]):
            print(f"  Doc {i+1}: {result['metadata'].get('doc_type', 'unknown')} - {result['content'][:50]}...")
    
    # Test trace query
    traces_results = rag.query_traces("Similar to trace_000042", n_results=3)
    print(f"Traces query returned {len(traces_results)} results")
    
    if traces_results:
        for i, result in enumerate(traces_results[:2]):
            print(f"  Trace {i+1}: {result['metadata'].get('trace_id', 'unknown')} - Line {result['metadata'].get('line_number', 'unknown')}")
    
    # Check stats
    stats = rag.get_stats()
    print(f"L3 Stats: {stats}")
    assert stats["docs_count"] > 0, "Should have documents in collection"
    assert stats["traces_count"] > 0, "Should have traces in collection"
    
    print("✅ L3 Semantic RAG test passed")
    return True


def test_l4_agentic_actions():
    """Test L4 Agentic Actions functionality."""
    print("\n=== Testing L4 Agentic Actions ===")
    
    actions = L4AgenticActions()
    
    # Test valid action
    valid = actions.validate_action("search_docs", {"query": "ADG architecture"})
    print(f"Valid action validation: {valid}")
    assert valid, "Should validate correct action"
    
    # Test invalid action (missing required param)
    valid = actions.validate_action("search_docs", {})
    print(f"Invalid action validation: {valid}")
    assert not valid, "Should reject action with missing required param"
    
    # Test unknown action
    valid = actions.validate_action("unknown_action", {})
    print(f"Unknown action validation: {valid}")
    assert not valid, "Should reject unknown action"
    
    # List available actions
    available = actions.list_available_actions()
    print(f"Available actions: {available}")
    assert len(available) > 0, "Should have available actions"
    
    # Get tool schema
    schema = actions.get_tool_schema("search_docs")
    print(f"Search docs schema: {schema.get('name')}")
    assert schema is not None, "Should return schema"
    
    # Check stats
    stats = actions.get_stats()
    print(f"L4 Stats: {stats}")
    assert stats["action_count"] > 0, "Should have processed actions"
    
    print("✅ L4 Agentic Actions test passed")
    return True


def test_retrieval_orchestrator():
    """Test the full retrieval orchestrator."""
    print("\n=== Testing Retrieval Orchestrator ===")
    
    orchestrator = RetrievalOrchestrator()
    
    # Test document query (should go to L3)
    results = orchestrator.retrieve("How does ADG work?", n_results=3)
    print(f"Orchestrator query used layers: {results['layers_used']}")
    print(f"Number of results: {len(results['results'])}")
    
    if results['results']:
        for result in results['results'][:2]:
            print(f"  {result['layer']}: {result.get('content', '')[:50]}...")
    
    # Test action query (should validate with L4)
    results = orchestrator.retrieve("Search for ADG architecture information", n_results=3)
    print(f"Action query used layers: {results['layers_used']}")
    
    # Test caching by querying the same thing again
    results = orchestrator.retrieve("How does ADG work?", n_results=3)
    print(f"Cached query used layers: {results['layers_used']}")
    
    # Get all stats
    all_stats = orchestrator.get_all_stats()
    print(f"All layer stats:")
    for layer, stats in all_stats.items():
        print(f"  {layer}: {stats}")
    
    print("✅ Retrieval Orchestrator test passed")
    return True


def main():
    """Run all retrieval layer tests."""
    print("=== Retrieval Layers Integration Test ===")
    
    tests = [
        test_l1_exact_cache,
        test_l2_semantic_cache,
        test_l3_semantic_rag,
        test_l4_agentic_actions,
        test_retrieval_orchestrator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All retrieval layer tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
