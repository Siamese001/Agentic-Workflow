#!/usr/bin/env python3
"""
Retrieval System Demonstration Script

This script demonstrates the capabilities of the four-layer retrieval system
through practical examples and performance benchmarks.
"""

import sys
import time
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L4_state.reasoning.retrieval_layers import RetrievalOrchestrator


def print_banner():
    """Print demonstration banner."""
    print("=" * 80)
    print(" " * 20 + "RETRIEVAL SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()


def demonstrate_layer_performance():
    """Demonstrate performance of each layer."""
    print("🚀 LAYER PERFORMANCE DEMONSTRATION")
    print("-" * 40)

    orchestrator = RetrievalOrchestrator()

    # Test queries for different scenarios
    test_queries = [
        ("Exact Match (L1)", "How does ADG work?"),
        ("Semantic Similar (L2)", "What is the architecture dependency graph?"),
        ("Complex RAG (L3)", "Find information about L4 state management"),
        ("Action Query (L4)", "Search for architecture documentation")
    ]

    for scenario, query in test_queries:
        print(f"\n📋 {scenario}")
        print(f"Query: {query}")

        start_time = time.time()
        results = orchestrator.retrieve(query, n_results=3)
        end_time = time.time()

        print(f"Response Time: {(end_time - start_time) * 1000:.2f}ms")
        print(f"Layers Used: {', '.join(results['layers_used'])}")
        print(f"Results Found: {len(results['results'])}")

        if results['results']:
            for i, result in enumerate(results['results'][:2]):
                print(f"  Result {i+1} ({result['layer']}): {result['content'][:80]}...")

    print()


def demonstrate_cache_behavior():
    """Demonstrate caching behavior."""
    print("💾 CACHE BEHAVIOR DEMONSTRATION")
    print("-" * 40)

    orchestrator = RetrievalOrchestrator()

    # First query - should miss cache
    query = "What is the ADG architecture?"
    print(f"First query (expected cache miss): {query}")

    start_time = time.time()
    results1 = orchestrator.retrieve(query)
    first_time = time.time() - start_time

    print(f"First query time: {first_time * 1000:.2f}ms")
    print(f"Layers used: {results1['layers_used']}")

    # Second query - should hit cache
    print(f"\nSecond query (expected cache hit): {query}")

    start_time = time.time()
    results2 = orchestrator.retrieve(query)
    second_time = time.time() - start_time

    print(f"Second query time: {second_time * 1000:.2f}ms")
    print(f"Layers used: {results2['layers_used']}")

    if first_time > second_time:
        speedup = first_time / second_time
        print(f"🎯 Cache speedup: {speedup:.2f}x faster")

    print()


def demonstrate_semantic_search():
    """Demonstrate semantic search capabilities."""
    print("🔍 SEMANTIC SEARCH DEMONSTRATION")
    print("-" * 40)

    orchestrator = RetrievalOrchestrator()

    # Test semantic variations
    semantic_queries = [
        ("Original", "How does the architecture dependency graph work?"),
        ("Paraphrase 1", "Explain the ADG system architecture"),
        ("Paraphrase 2", "Describe the dependency graph architecture"),
        ("Different terms", "What are the architectural dependencies in ADG?")
    ]

    for variation, query in semantic_queries:
        print(f"\n📝 {variation}")
        print(f"Query: {query}")

        results = orchestrator.retrieve(query, n_results=2)

        if results['results']:
            for i, result in enumerate(results['results']):
                print(f"  Result {i+1}: {result['content'][:60]}...")

    print()


def demonstrate_trace_retrieval():
    """Demonstrate healing trace retrieval."""
    print("🔧 HEALING TRACE RETRIEVAL DEMONSTRATION")
    print("-" * 40)

    orchestrator = RetrievalOrchestrator()

    # Query for similar traces
    trace_queries = [
        "Similar to trace_000042",
        "Find execution traces with errors",
        "Healing patterns for validation failures",
        "Performance optimization traces"
    ]

    for query in trace_queries:
        print(f"\n🔍 Trace Query: {query}")

        results = orchestrator.retrieve(query, n_results=3)

        trace_results = [r for r in results['results'] if r['layer'] == 'L3_Traces']

        if trace_results:
            for i, result in enumerate(trace_results[:2]):
                metadata = result['metadata']
                print(f"  Trace {i+1}: ID={metadata.get('trace_id', 'unknown')}, "
                      f"Line={metadata.get('line_number', 'unknown')}")
        else:
            print("  No trace results found")

    print()


def demonstrate_action_validation():
    """Demonstrate L4 action validation."""
    print("✅ ACTION VALIDATION DEMONSTRATION")
    print("-" * 40)

    from agentic_core.L4_state.reasoning.retrieval_layers import L4AgenticActions

    actions = L4AgenticActions()

    # Test action validation
    test_actions = [
        ("Valid", "search_docs", {"query": "ADG architecture"}),
        ("Invalid - Missing Param", "search_docs", {}),
        ("Unknown", "unknown_action", {"param": "value"}),
        ("Valid", "find_similar_traces", {"trace_id": "trace_000042"})
    ]

    for test_type, action_name, params in test_actions:
        print(f"\n🧪 {test_type}")
        print(f"Action: {action_name}")
        print(f"Parameters: {params}")

        is_valid = actions.validate_action(action_name, params)
        print(f"Valid: {'✅ Yes' if is_valid else '❌ No'}")

    # Show available actions
    print(f"\n📋 Available Actions: {', '.join(actions.list_available_actions())}")
    print()


def demonstrate_performance_benchmark():
    """Demonstrate performance benchmarks."""
    print("⚡ PERFORMANCE BENCHMARK")
    print("-" * 40)

    orchestrator = RetrievalOrchestrator()

    # Benchmark queries
    benchmark_queries = [
        "How does ADG work?",
        "What is L4 state?",
        "Find similar traces",
        "Search architecture docs",
        "Explain the caching system",
        "Healing patterns",
        "Performance optimization",
        "Validation rules"
    ]

    print(f"Running {len(benchmark_queries)} queries...")

    times = []
    layer_usage = {}

    for i, query in enumerate(benchmark_queries, 1):
        start_time = time.time()
        results = orchestrator.retrieve(query)
        end_time = time.time()

        query_time = end_time - start_time
        times.append(query_time)

        layers = ','.join(results['layers_used'])
        layer_usage[layers] = layer_usage.get(layers, 0) + 1

        print(f"Query {i}: {query_time * 1000:.2f}ms ({layers})")

    # Statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print("\n📊 Performance Statistics:")
    print(f"  Average: {avg_time * 1000:.2f}ms")
    print(f"  Min: {min_time * 1000:.2f}ms")
    print(f"  Max: {max_time * 1000:.2f}ms")
    print(f"  Total: {sum(times) * 1000:.2f}ms")

    print("\n📈 Layer Usage Distribution:")
    for layers, count in layer_usage.items():
        percentage = (count / len(benchmark_queries)) * 100
        print(f"  {layers}: {count} queries ({percentage:.1f}%)")

    print()


def demonstrate_system_stats():
    """Demonstrate system statistics."""
    print("📊 SYSTEM STATISTICS")
    print("-" * 40)

    orchestrator = RetrievalOrchestrator()
    stats = orchestrator.get_all_stats()

    for layer, layer_stats in stats.items():
        print(f"\n{layer.upper()}:")
        for key, value in layer_stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")

    print()


def main():
    """Run the complete demonstration."""
    print_banner()

    print("Welcome to the Retrieval System Demonstration!")
    print("This showcase will demonstrate the four-layer retrieval architecture.")
    print("Each layer provides different capabilities and performance characteristics.")
    print()

    demonstrations = [
        demonstrate_layer_performance,
        demonstrate_cache_behavior,
        demonstrate_semantic_search,
        demonstrate_trace_retrieval,
        demonstrate_action_validation,
        demonstrate_performance_benchmark,
        demonstrate_system_stats
    ]

    for demo in demonstrations:
        try:
            demo()
            input("Press Enter to continue to next demonstration...")
            print("\n" + "=" * 80 + "\n")
        except KeyboardInterrupt:
            print("\n\nDemonstration interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ Error in demonstration: {e}")
            print("Continuing to next demonstration...")
            continue

    print("🎉 Demonstration Complete!")
    print("\nKey Takeaways:")
    print("• L1 Cache provides <1ms exact match responses")
    print("• L2 Cache enables semantic similarity matching")
    print("• L3 RAG searches across 100K+ documents and traces")
    print("• L4 Actions validate and route tool operations")
    print("• The system learns and improves with each interaction")
    print("\nThank you for exploring the Retrieval System!")


if __name__ == "__main__":
    main()
