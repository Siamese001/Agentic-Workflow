#!/usr/bin/env python3
"""
Test script to validate L1-L4 retrieval layers integration
"""

import sys
import time
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L4_state.reasoning.retrieval_layers import (
    L1ExactCache,
    L2SemanticCache,
    L3SemanticRAG,
    L4AgenticActions,
    RetrievalOrchestrator,
)


def test_l1_exact_cache():
    """Test L1 Exact Cache functionality."""
    print("\n=== Testing L1 Exact Cache ===")

    cache = L1ExactCache(ttl_seconds=60)

    # Test miss
    unique_query = f"test_query_{hash(time.time())}"  # Ensure uniqueness
    result = cache.get(unique_query)
    print(f"Initial query result: {result}")
    assert result is None, f"Should be None on first query for: {unique_query}"

    # Test set and hit
    test_query = "How does ADG work?"
    test_response = "ADG is the Architecture Dependency Graph..."
    cache.set(test_query, test_response)
    result = cache.get(test_query)
    print(f"Cached query result: {result[:50] if result else 'None'}...")
    assert result == test_response, f"Should return exact cached response: {test_response}"

    # Test normalization
    normalized_query = "how does adg work?"  # Different case
    result = cache.get(normalized_query)
    print(f"Normalized query result: {result[:50] if result else 'None'}...")
    assert result == test_response, "Should work with normalized query"

    # Test different query miss
    different_query = "completely different query"
    result = cache.get(different_query)
    assert result is None, "Should return None for different query"

    # Check stats
    stats = cache.get_stats()
    print(f"L1 Stats: {stats}")
    assert stats["hit_count"] >= 2, f"Should have at least 2 hits, got {stats['hit_count']}"
    assert stats["miss_count"] >= 2, f"Should have at least 2 misses, got {stats['miss_count']}"

    print("✅ L1 Exact Cache test passed")
    return True


def test_l2_semantic_cache():
    """Test L2 Semantic Cache functionality."""
    print("\n=== Testing L2 Semantic Cache ===")

    cache = L2SemanticCache(similarity_threshold=0.95, ttl_seconds=60)

    # Test miss with unique query
    unique_query = f"semantic_test_{hash(time.time())}"
    result = cache.get(unique_query)
    print(f"Initial query result: {result}")
    assert result is None, f"Should be None on first query for: {unique_query}"

    # Test set and exact hit
    test_query = "What is the ADG architecture?"
    test_response = "ADG architecture consists of layers L0-L6..."
    cache.set(test_query, test_response)
    result = cache.get(test_query)
    print(f"Cached query result: {result}")
    assert result == test_response, f"Should return exact cached response: {test_response}"

    # Test semantic similarity (same query should hit)
    result = cache.get(test_query)
    print(f"Similar query result: {result}")
    assert result == test_response, "Same query should hit semantic cache"

    # Test different query miss
    different_query = "completely unrelated topic"
    result = cache.get(different_query)
    assert result is None, "Should return None for different query"

    # Check stats
    stats = cache.get_stats()
    print(f"L2 Stats: {stats}")
    assert stats["hit_count"] >= 1, f"Should have at least 1 hit, got {stats['hit_count']}"
    assert stats["miss_count"] >= 2, f"Should have at least 2 misses, got {stats['miss_count']}"
    assert stats["similarity_threshold"] == 0.95, "Should maintain similarity threshold"

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
    print("All layer stats:")
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

    print("\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ All retrieval layer tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
