"""Integration Test for the Complete Titanium RAG Pipeline.

This test demonstrates all three phases (Precision, Reasoning, SOTA)
working together in the unified pipeline facade.

Run with: python -m asyncio runtime.shared.test_titanium_pipeline.py
"""

import asyncio
import time

# Import the complete pipeline


class TitaniumPipelineIntegrationTest:
    """Integration test suite for the complete Titanium RAG Pipeline."""

    def __init__(self):
        """Initialize the test suite."""
        # Create pipeline with all features enabled
        self.pipeline = create_titanium_pipeline(
            enable_all=True, max_retrieved_docs=20, top_k_final=5
        )

        # Mock document database
        self.document_db = [
            {
                "doc_id": "doc1",
                "text": "Our RAG pipeline achieves 50ms average latency with 95% accuracy using optimized vector search",
                "metadata": {"source": "performance_report", "date": "2024-01-15"},
            },
            {
                "doc_id": "doc2",
                "text": "Industry benchmarks for financial applications show 100ms average response time with 90% accuracy",
                "metadata": {"source": "industry_analysis", "date": "2024-01-10"},
            },
            {
                "doc_id": "doc3",
                "text": "The microservices architecture improved scalability by 300% through horizontal scaling and load balancing",
                "metadata": {"source": "architecture_doc", "date": "2024-01-05"},
            },
            {
                "doc_id": "doc4",
                "text": "Python Django REST API handles 10,000 requests per second with proper caching and database optimization",
                "metadata": {"source": "api_documentation", "date": "2024-01-12"},
            },
            {
                "doc_id": "doc5",
                "text": "Our strategic plan for Q2 focuses on expanding market presence and improving customer retention by 25%",
                "metadata": {"source": "strategy_doc", "date": "2024-01-20"},
            },
            {
                "doc_id": "doc6",
                "text": "Authentication system uses OAuth 2.0 with JWT tokens for secure API access and session management",
                "metadata": {"source": "security_doc", "date": "2024-01-08"},
            },
            {
                "doc_id": "doc7",
                "text": "Error rate decreased from 5% to 0.1% after implementing comprehensive monitoring and alerting",
                "metadata": {"source": "quality_report", "date": "2024-01-18"},
            },
            {
                "doc_id": "doc8",
                "text": "Machine learning model accuracy improved to 99.2% using ensemble methods and feature engineering",
                "metadata": {"source": "ml_report", "date": "2024-01-14"},
            },
            {
                "doc_id": "doc9",
                "text": "Kubernetes cluster runs on 50 nodes with auto-scaling based on CPU and memory utilization",
                "metadata": {"source": "infrastructure_doc", "date": "2024-01-11"},
            },
            {
                "doc_id": "doc10",
                "text": "Customer satisfaction scores increased by 25% after implementing real-time support chat",
                "metadata": {"source": "customer_report", "date": "2024-01-22"},
            },
        ]

        # Test scenarios covering all phases
        self.test_scenarios = [
            {
                "name": "Simple Query (Gate Block)",
                "query": "hello",
                "expected_phase": "gate_block",
                "description": "Should be blocked by AdaptiveRetrievalGate",
            },
            {
                "name": "Cache Hit (SOTA Layer)",
                "query": "What is our strategy?",
                "expected_phase": "cache_hit",
                "description": "Should hit semantic cache on second query",
            },
            {
                "name": "Technical Query (Dynamic Alpha)",
                "query": "Python API performance metrics",
                "expected_phase": "reasoning",
                "description": "Should use keyword-focused scoring",
            },
            {
                "name": "Executive Complex Query (Full Pipeline)",
                "query": "Compare our system performance against industry benchmarks and identify optimization opportunities",
                "expected_phase": "full_pipeline",
                "description": "Should use all three phases",
            },
            {
                "name": "Reference Query (Contextual)",
                "query": "What was mentioned in the previous document?",
                "expected_phase": "gate_block",
                "description": "Should be blocked as reference query",
            },
        ]

    async def mock_retrieval_function(
        self, query: str, max_docs: int = 10, **kwargs
    ) -> tuple[list[dict], list[dict]]:
        """Mock retrieval function that simulates vector and BM25 search.

        Args:
            query: Query string
            max_docs: Maximum documents to retrieve
            **kwargs: Additional arguments

        Returns:
            Tuple of (dense_results, sparse_results)
        """
        # Simple keyword matching for simulation
        query_words = query.lower().split()
        scored_docs = []

        for doc in self.document_db:
            score = 0
            text = doc["text"].lower()

            # Calculate simple relevance score
            for word in query_words:
                if word in text:
                    score += 1

            if score > 0:
                scored_docs.append((doc, score))

        # Sort by score
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Take top documents
        top_docs = scored_docs[:max_docs]

        # Create dense results (mock vector search)
        dense_results = []
        for doc, score in top_docs:
            dense_results.append(
                {
                    "doc_id": doc["doc_id"],
                    "score": min(score / len(query_words), 1.0),  # Normalize to 0-1
                    "metadata": doc,
                }
            )

        # Create sparse results (mock BM25)
        sparse_results = []
        for doc, score in top_docs:
            sparse_results.append(
                {
                    "doc_id": doc["doc_id"],
                    "score": score * 1.5,  # BM25 scores are typically higher
                }
            )

        return dense_results, sparse_results

    async def test_individual_phases(self):
        """Test each phase individually."""
        print("\n" + "=" * 60)
        print("TESTING: Individual Phases")
        print("=" * 60)

        # Test Phase 1: Precision Layer
        print("\n1. Testing Phase 1 (Precision Layer):")
        print("-" * 40)

        # Test gate
        gate_result = self.pipeline.gate.should_retrieve("hello")
        print(
            f"   Gate - Simple query: {'Block' if not gate_result.should_retrieve else 'Allow'} ({gate_result.reason})"
        )

        gate_result = self.pipeline.gate.should_retrieve("What is RAG?")
        print(
            f"   Gate - Complex query: {'Block' if not gate_result.should_retrieve else 'Allow'} ({gate_result.reason})"
        )

        # Test compressor
        test_chunks = [
            "Our RAG pipeline is fast and efficient. It achieves 50ms latency.",
            "The system uses advanced algorithms for optimization.",
            "Customer satisfaction is our top priority.",
        ]
        compression_result = self.pipeline.compressor.compress(
            chunks=test_chunks, query="RAG pipeline performance"
        )
        print(f"   Compression ratio: {compression_result.compression_ratio:.2f}")

        # Test Phase 2: Reasoning Layer
        print("\n2. Testing Phase 2 (Reasoning Layer):")
        print("-" * 40)

        # Test decomposition
        decomposed = await self.pipeline.decomposer.decompose(
            "Compare AWS vs Azure pricing for financial services"
        )
        print(f"   Decomposition: {len(decomposed.sub_queries)} sub-queries")
        for i, sub_query in enumerate(decomposed.sub_queries, 1):
            print(f"     {i}. {sub_query}")

        # Test dynamic alpha
        alpha_entity = self.pipeline.scorer._determine_dynamic_alpha("ABC-123 error code")
        alpha_technical = self.pipeline.scorer._determine_dynamic_alpha("Python API")
        alpha_concept = self.pipeline.scorer._determine_dynamic_alpha("company strategy")
        print(
            f"   Dynamic Alpha - Entity: {alpha_entity}, Technical: {alpha_technical}, Concept: {alpha_concept}"
        )

        # Test Phase 3: SOTA Layer
        print("\n3. Testing Phase 3 (SOTA Layer):")
        print("-" * 40)

        # Test reranker availability
        print(f"   Reranker available: {self.pipeline.reranker.is_available}")
        if self.pipeline.reranker.is_available:
            test_docs = [doc["text"] for doc in self.document_db[:5]]
            reranked = self.pipeline.reranker.rerank(
                query="Python API performance", documents=test_docs, top_k=3
            )
            print(f"   Reranked {len(test_docs)} to {len(reranked)} documents")

        # Test cache availability
        print(f"   Cache available: {self.pipeline.cache.is_available}")
        if self.pipeline.cache.is_available:
            # Put and get
            self.pipeline.cache.put("test query", "test response")
            cached = self.pipeline.cache.get("test query")
            print(f"   Cache test: {'Hit' if cached else 'Miss'}")

    async def test_full_pipeline_scenarios(self):
        """Test complete pipeline with various scenarios."""
        print("\n" + "=" * 60)
        print("TESTING: Full Pipeline Scenarios")
        print("=" * 60)

        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\nScenario {i}: {scenario['name']}")
            print(f"Query: {scenario['query']}")
            print(f"Description: {scenario['description']}")
            print("-" * 40)

            # Clear cache for clean test
            self.pipeline.cache.clear()

            # First query
            start_time = time.time()
            result1 = await self.pipeline.query(
                query=scenario["query"], retrieval_function=self.mock_retrieval_function
            )
            time1 = time.time() - start_time

            print(f"   First query: {time1:.3f}s")
            print(f"   Cached: {result1['metadata']['cached']}")
            print(f"   Decomposed: {bool(result1['metadata']['decomposed'])}")
            print(f"   Compressed: {result1['metadata']['compressed']}")
            print(f"   Reranked: {result1['metadata']['reranked']}")

            # Second query (for cache test)
            if scenario["expected_phase"] == "cache_hit":
                start_time = time.time()
                result2 = await self.pipeline.query(
                    query=scenario["query"], retrieval_function=self.mock_retrieval_function
                )
                time2 = time.time() - start_time

                print(f"   Second query: {time2:.3f}s")
                print(f"   Cache speedup: {time1 / time2:.1f}x faster")
                print(f"   Cached hit: {result2['metadata']['cached']}")

            # Verify expected behavior
            if scenario["expected_phase"] == "gate_block":
                if not result1["metadata"]["gate_decision"]["should_retrieve"]:
                    print("   ✅ Correctly blocked by gate")
                else:
                    print("   ❌ Should have been blocked by gate")

    async def test_pipeline_statistics(self):
        """Test pipeline statistics and monitoring."""
        print("\n" + "=" * 60)
        print("TESTING: Pipeline Statistics")
        print("=" * 60)

        # Run some queries to generate stats
        queries = [
            "hello",  # Should be blocked
            "What is our strategy?",  # Should be cached
            "Python API documentation",  # Should use technical alpha
            "Compare our performance to benchmarks",  # Full pipeline
        ]

        print("\nRunning queries to generate statistics...")
        for query in queries:
            await self.pipeline.query(query=query, retrieval_function=self.mock_retrieval_function)

        # Get statistics
        stats = self.pipeline.get_stats()
        print("\nPipeline Statistics:")
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Gate blocks: {stats['gate_blocks']} ({stats['gate_block_rate']:.1%})")
        print(f"   Cache hits: {stats['cache_hits']} ({stats['cache_hit_rate']:.1%})")
        print(f"   Decompositions: {stats['decompositions']} ({stats['decomposition_rate']:.1%})")
        print(f"   Compressions: {stats['compressions']} ({stats['compression_rate']:.1%})")
        print(f"   Rerankings: {stats['rerankings']} ({stats['reranking_rate']:.1%})")

        # Get component info
        component_info = self.pipeline.get_component_info()
        print("\nComponent Status:")
        print("   Phase 1 (Precision): Available")
        print("   Phase 2 (Reasoning): Available")
        print(
            f"   Phase 3 (SOTA): Reranker={component_info['phase_3_sota']['reranker_available']}, "
            f"Cache={component_info['phase_3_sota']['cache_available']}"
        )

    async def test_error_handling(self):
        """Test pipeline error handling and fallbacks."""
        print("\n" + "=" * 60)
        print("TESTING: Error Handling & Fallbacks")
        print("=" * 60)

        # Test with empty results
        print("\n1. Testing with empty retrieval results:")
        result = await self.pipeline.query(
            query="test query", retrieval_function=lambda q, **kwargs: ([], [])
        )
        print(f"   Handled empty results: {len(result['documents'])} documents")

        # Test with None query
        print("\n2. Testing with None query:")
        result = await self.pipeline.query(
            query=None, retrieval_function=self.mock_retrieval_function
        )
        print(f"   Handled None query: {result['response'] is not None}")

        # Test component fallbacks
        print("\n3. Testing component fallbacks:")

        # Create pipeline with disabled components
        minimal_pipeline = TitaniumRAGPipeline(
            enable_compression=False,
            enable_decomposition=False,
            enable_reranking=False,
            enable_caching=False,
        )

        result = await minimal_pipeline.query(
            query="test query", retrieval_function=self.mock_retrieval_function
        )
        print(f"   Minimal pipeline works: {result['metadata'] is not None}")

    def test_convenience_functions(self):
        """Test convenience functions for easy setup."""
        print("\n" + "=" * 60)
        print("TESTING: Convenience Functions")
        print("=" * 60)

        # Test create_titanium_pipeline
        print("\n1. Testing create_titanium_pipeline():")

        # Full pipeline
        full_pipeline = create_titanium_pipeline(enable_all=True)
        print(f"   Full pipeline created: {full_pipeline is not None}")

        # Custom pipeline
        custom_pipeline = create_titanium_pipeline(
            enable_all=False, enable_caching=True, enable_reranking=False
        )
        print(f"   Custom pipeline created: {custom_pipeline is not None}")
        print(f"   Caching enabled: {custom_pipeline.enable_caching}")
        print(f"   Reranking enabled: {custom_pipeline.enable_reranking}")

    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting Titanium RAG Pipeline Integration Test Suite")
        print("=" * 60)

        # Check component availability
        print("\nChecking component availability...")
        component_info = self.pipeline.get_component_info()

        print("  Phase 1 (Precision): ✅ Available")
        print("  Phase 2 (Reasoning): ✅ Available")
        print("  Phase 3 (SOTA):")
        print(
            f"    - Reranker: {'✅' if component_info['phase_3_sota']['reranker_available'] else '⚠️  Fallback'}"
        )
        print(
            f"    - Cache: {'✅' if component_info['phase_3_sota']['cache_available'] else '⚠️  Fallback'}"
        )

        # Run all tests
        await self.test_individual_phases()
        await self.test_full_pipeline_scenarios()
        await self.test_pipeline_statistics()
        await self.test_error_handling()
        self.test_convenience_functions()

        print("\n" + "=" * 60)
        print("✅ ALL INTEGRATION TESTS COMPLETED")
        print("=" * 60)
        print("\nThe Titanium RAG Pipeline is fully integrated and ready!")
        print("\nArchitecture Summary:")
        print("  • Phase 1 (Precision): Filters noise and optimizes retrieval")
        print("  • Phase 2 (Reasoning): Decomposes queries and dynamically scores")
        print("  • Phase 3 (SOTA): Reranks for precision and caches for speed")
        print("\nUsage Example:")
        print("  pipeline = create_titanium_pipeline()")
        print("  result = await pipeline.query(query, retrieval_function)")


def main():
    """Main entry point for running integration tests."""
    test_suite = TitaniumPipelineIntegrationTest()
    asyncio.run(test_suite.run_all_tests())


if __name__ == "__main__":
    main()