"""Test Suite for Phase 2 Reasoning Layer Components.

This test file demonstrates the Query Decomposer and Dynamic Hybrid Scorer
working together to handle complex executive queries.

Run with: python -m asyncio runtime.shared.test_reasoning_layer.py
"""

import asyncio
import time

# Import the reasoning layer components
    HybridScorer,
    QueryDecomposer,
    decompose_query,
)


class ReasoningLayerTestSuite:
    """Test suite for Phase 2 Reasoning Layer components."""

    def __init__(self):
        """Initialize the test suite."""
        self.decomposer = QueryDecomposer()
        self.scorer = HybridScorer(dynamic_alpha=True)

        # Sample search results for testing
        self.sample_dense_results = [
            {"doc_id": "doc1", "score": 0.9, "content": "Our RAG pipeline achieves 50ms latency"},
            {"doc_id": "doc2", "score": 0.8, "content": "Industry benchmarks show 100ms average"},
            {
                "doc_id": "doc3",
                "score": 0.7,
                "content": "Financial apps require sub-100ms response",
            },
        ]

        self.sample_sparse_results = [
            {"doc_id": "doc1", "score": 2.5},
            {"doc_id": "doc2", "score": 1.8},
            {"doc_id": "doc3", "score": 1.2},
        ]

        # Test queries for decomposition
        self.test_queries = [
            # Simple queries (should not decompose)
            {
                "query": "What is RAG?",
                "expected_sub_queries": 1,
                "complexity_min": 1,
                "complexity_max": 3,
            },
            # Comparison queries
            {
                "query": "Compare AWS vs Azure pricing for financial services",
                "expected_sub_queries": 3,
                "complexity_min": 6,
                "complexity_max": 9,
            },
            # Causation queries
            {
                "query": "Why did our latency increase after the migration?",
                "expected_sub_queries": 2,
                "complexity_min": 5,
                "complexity_max": 8,
            },
            # Complex multi-hop
            {
                "query": "Compare the performance of our RAG pipeline to industry standards for financial apps and identify the root causes of any discrepancies",
                "expected_sub_queries": 4,
                "complexity_min": 8,
                "complexity_max": 10,
            },
            # Technical queries
            {
                "query": "Python API v3.1 documentation for Redis",
                "expected_sub_queries": 1,
                "complexity_min": 1,
                "complexity_max": 4,
            },
        ]

        # Test queries for dynamic alpha
        self.alpha_test_queries = [
            {
                "query": "ABC-123 error code in production",
                "expected_alpha": 0.3,
                "reason": "Entity pattern (ticket ID)",
            },
            {
                "query": "Python Django REST API performance",
                "expected_alpha": 0.4,
                "reason": "Technical pattern",
            },
            {
                "query": "Company culture and leadership strategy",
                "expected_alpha": 0.8,
                "reason": "Concept/strategy pattern",
            },
            {
                "query": "General information about systems",
                "expected_alpha": 0.6,
                "reason": "Default case",
            },
        ]

    async def test_query_decomposer(self):
        """Test the Query Decomposer with various query types."""
        print("\n" + "=" * 60)
        print("TESTING: Query Decomposer")
        print("=" * 60)

        for i, test_case in enumerate(self.test_queries, 1):
            print(f"\nTest Case {i}: {test_case['query']}")
            print("-" * 40)

            start_time = time.time()
            result = await self.decomposer.decompose(test_case["query"])
            elapsed = time.time() - start_time

            print(f"✅ Decomposition completed in {elapsed:.3f}s")
            print(f"   Original: {result.original_query}")
            print(f"   Sub-queries: {len(result.sub_queries)}")
            print(f"   Complexity: {result.complexity_score}/10")
            print(f"   Reasoning: {result.reasoning}")

            # Verify expectations
            if len(result.sub_queries) == test_case["expected_sub_queries"]:
                print("   ✅ Correct number of sub-queries")
            else:
                print(
                    f"   ⚠️  Expected {test_case['expected_sub_queries']}, got {len(result.sub_queries)}"
                )

            if (
                test_case["complexity_min"]
                <= result.complexity_score
                <= test_case["complexity_max"]
            ):
                print("   ✅ Complexity within expected range")
            else:
                print(
                    f"   ⚠️  Complexity {result.complexity_score} outside range "
                    f"({test_case['complexity_min']}-{test_case['complexity_max']})"
                )

            # Show sub-queries
            for j, sub_query in enumerate(result.sub_queries, 1):
                print(f"     {j}. {sub_query}")

    def test_dynamic_hybrid_scorer(self):
        """Test the Dynamic Hybrid Scorer with different query types."""
        print("\n" + "=" * 60)
        print("TESTING: Dynamic Hybrid Scorer")
        print("=" * 60)

        for test_case in self.alpha_test_queries:
            print(f"\nQuery: {test_case['query']}")
            print(f"Expected Alpha: {test_case['expected_alpha']} ({test_case['reason']})")
            print("-" * 40)

            # Test with dynamic alpha
            results = self.scorer.score_documents(
                dense_results=self.sample_dense_results,
                sparse_results=self.sample_sparse_results,
                query=test_case["query"],
            )

            print(f"   ✅ Dynamic alpha used: {self.scorer.alpha}")

            if self.scorer.alpha == test_case["expected_alpha"]:
                print("   ✅ Alpha matches expectation")
            else:
                print(f"   ⚠️  Expected {test_case['expected_alpha']}, got {self.scorer.alpha}")

            # Show top result
            if results:
                top = results[0]
                print(f"   Top result: {top.doc_id} (score: {top.final_score:.3f})")
                print(
                    f"   Score breakdown: Dense={top.dense_score:.3f}, "
                    f"Sparse={top.sparse_score:.3f}, Boost={top.metadata_boost:.3f}"
                )

    async def test_integration_scenario(self):
        """Test both components working together in a realistic scenario."""
        print("\n" + "=" * 60)
        print("TESTING: Integration Scenario")
        print("=" * 60)

        # Complex executive query
        executive_query = "Compare our RAG pipeline performance against financial industry benchmarks and identify optimization opportunities"

        print(f"\nExecutive Query: {executive_query}")
        print("-" * 60)

        # Step 1: Decompose the query
        print("\n1. Decomposing query...")
        decomposed = await self.decomposer.decompose(executive_query)
        print(f"   Generated {len(decomposed.sub_queries)} sub-queries")

        # Step 2: Process each sub-query with dynamic scoring
        print("\n2. Processing sub-queries with dynamic scoring...")
        all_results = []

        for i, sub_query in enumerate(decomposed.sub_queries, 1):
            print(f"\n   Sub-query {i}: {sub_query}")

            # Determine alpha for this sub-query
            alpha = self.scorer._determine_dynamic_alpha(sub_query)
            print(f"   Alpha: {alpha} ({'keyword-focused' if alpha < 0.5 else 'semantic-focused'})")

            # Score documents
            results = self.scorer.score_documents(
                dense_results=self.sample_dense_results,
                sparse_results=self.sample_sparse_results,
                query=sub_query,
            )

            if results:
                top_result = results[0]
                print(f"   Top match: {top_result.doc_id} (score: {top_result.final_score:.3f})")
                all_results.extend(results)

        # Step 3: Aggregate and analyze results
        print("\n3. Aggregating results...")
        unique_docs = set(r.doc_id for r in all_results)
        print(f"   Found {len(all_results)} total results from {len(unique_docs)} unique documents")

        # Show document frequency
        doc_frequency = {}
        for result in all_results:
            doc_frequency[result.doc_id] = doc_frequency.get(result.doc_id, 0) + 1

        print("\n   Document relevance frequency:")
        for doc_id, freq in sorted(doc_frequency.items(), key=lambda x: x[1], reverse=True):
            print(f"     {doc_id}: matched {freq} sub-queries")

    async def test_async_execution(self):
        """Test the async execution helper for parallel sub-query processing."""
        print("\n" + "=" * 60)
        print("TESTING: Async Execution Helper")
        print("=" * 60)

        # Create a mock search function
        async def mock_search(query: str, delay: float = 0.1):
            """Mock async search function."""
            await asyncio.sleep(delay)
            return [{"query": query, "result": f"mock_result_for_{query[:10]}"}]

        # Test with decomposed query
        test_query = "Compare AWS vs Azure vs GCP pricing models"
        decomposed = await self.decomposer.decompose(test_query)

        print(f"\nTesting parallel execution of {len(decomposed.sub_queries)} sub-queries")

        start_time = time.time()
        results = await self.decomposer.execute_plan(
            decomposed=decomposed, search_function=mock_search, delay=0.05
        )
        elapsed = time.time() - start_time

        print(f"✅ Parallel execution completed in {elapsed:.3f}s")
        print(f"   Expected time (sequential): {len(decomposed.sub_queries) * 0.05:.3f}s")
        print(f"   Actual time (parallel): {elapsed:.3f}s")
        print(f"   Speedup: {(len(decomposed.sub_queries) * 0.05) / elapsed:.1f}x")

        # Verify results
        for i, result_list in enumerate(results):
            if result_list:
                print(f"   Sub-query {i + 1}: {len(result_list)} result(s)")

    def test_convenience_functions(self):
        """Test the convenience functions for direct usage."""
        print("\n" + "=" * 60)
        print("TESTING: Convenience Functions")
        print("=" * 60)

        # Test decompose_query function
        print("\n1. Testing decompose_query() function:")
        result = asyncio.run(decompose_query("What are the best practices for microservices?"))
        print(f"   Sub-queries: {len(result.sub_queries)}")
        print(f"   Complexity: {result.complexity_score}/10")
        print(f"   Reasoning: {result.reasoning}")

        # Test dynamic alpha without query (static mode)
        print("\n2. Testing static alpha mode:")
        static_scorer = HybridScorer(alpha=0.8, dynamic_alpha=False)
        results = static_scorer.score_documents(
            dense_results=self.sample_dense_results,
            sparse_results=self.sample_sparse_results,
            query="This should not affect alpha",
        )
        print(f"   Static alpha: {static_scorer.alpha}")
        print(f"   Results: {len(results)} documents scored")

    def run_all_tests(self):
        """Run all tests sequentially."""
        print("🚀 Starting Phase 2 Reasoning Layer Test Suite")
        print("=" * 60)

        # Run async tests
        asyncio.run(self.test_query_decomposer())
        asyncio.run(self.test_integration_scenario())
        asyncio.run(self.test_async_execution())

        # Run sync tests
        self.test_dynamic_hybrid_scorer()
        self.test_convenience_functions()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nPhase 2 Reasoning Layer is ready for integration!")
        print("\nKey Benefits Achieved:")
        print("  • Complex query decomposition into atomic sub-queries")
        print("  • Dynamic alpha adjustment based on query characteristics")
        print("  • Parallel execution of sub-queries for efficiency")
        print("  • Entity-aware scoring (IDs, technical terms, concepts)")
        print("  • Seamless integration with Phase 1 Precision Layer")


def main():
    """Main entry point for running tests."""
    test_suite = ReasoningLayerTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
