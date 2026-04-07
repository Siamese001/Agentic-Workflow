#!/usr/bin/env python3
"""
Test Wave 4: Advanced Retrieval & Reranking
Tests the complete Wave 4 implementation with query routing, fusion, and reranking.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent / "agentic_core"))

from L1_cognition.engines.advanced_semantic_retriever import (
    AdvancedRetrievalRequest,
    AdvancedSemanticRetriever,
)
from L1_cognition.engines.multi_query_fusion import MultiQueryFusion
from L1_cognition.engines.query_router import QueryRouter
from L1_cognition.engines.reranking_engine import RerankingEngine


async def test_query_routing():
    """Test query routing functionality."""
    print("=== Query Routing Test ===\n")

    router = QueryRouter()

    test_queries = [
        ("What does the UniversalWriteGateway do?", "CODE_KNOWLEDGE"),
        ("Show me the blast radius for ADG changes", "BLAST_RADIUS"),
        ("Find failures related to memory leaks", "FAILURE_ANALYSIS"),
        ("What were the recent commits?", "HISTORICAL_ANALYSIS"),
        ("How does execution work?", "EXECUTION_INTELLIGENCE"),
        ("What is the system architecture?", "STRUCTURAL_ANALYSIS"),
    ]

    available_collections = [
        "repo_code_chunks", "repo_symbols", "repo_arch_docs",
        "repo_adg_graph", "repo_tests_guardrails",
        "repo_runtime_evidence", "repo_git_history", "repo_incidents_rca",
    ]

    routing_success = 0

    for query, expected_type in test_queries:
        decision = router.route_query(query, available_collections)

        print(f"Query: {query}")
        print(f"Expected: {expected_type}, Got: {decision.query_type.value}")
        print(f"Primary: {decision.primary_collections}")
        print(f"Confidence: {decision.confidence:.2f}")
        print(f"Reasoning: {decision.reasoning}")
        print("-" * 50)

        if decision.query_type.value.lower() == expected_type.lower():
            routing_success += 1

    print(f"\nQuery Routing Results: {routing_success}/{len(test_queries)} correct")
    return routing_success == len(test_queries)


async def test_multi_query_fusion():
    """Test multi-query fusion functionality."""
    print("\n=== Multi-Query Fusion Test ===\n")

    try:
        from L1_cognition.engines.semantic_retriever import SemanticRetriever

        base_retriever = SemanticRetriever()
        fusion_engine = MultiQueryFusion(base_retriever)

        test_queries = [
            "UniversalWriteGateway implementation",
            "ADG dependency analysis",
            "L1 cognition components",
        ]

        fusion_success = 0

        for query in test_queries:
            print(f"Testing fusion for: {query}")

            try:
                result = await fusion_engine.execute_fusion_search(
                    query=query,
                    fusion_strategy="reciprocal_rank_fusion",
                    max_results_per_collection=5,
                    generate_variations=True,
                )

                print(f"  Collections searched: {len(result.collection_results)}")
                print(f"  Total results: {result.total_results}")
                print(f"  Execution time: {result.execution_time_ms:.2f}ms")
                print(f"  Query variations: {len(result.query_variations_used)}")

                if result.total_results > 0:
                    fusion_success += 1
                    print("  ✅ Fusion successful")
                else:
                    print("  ⚠️  No results found")

            except Exception as e:
                print(f"  ❌ Fusion failed: {e}")

            print("-" * 50)

        print(f"\nMulti-Query Fusion Results: {fusion_success}/{len(test_queries)} successful")
        return fusion_success > 0

    except Exception as e:
        print(f"Multi-query fusion test failed: {e}")
        return False


async def test_reranking_engine():
    """Test reranking engine functionality."""
    print("\n=== Reranking Engine Test ===\n")

    reranker = RerankingEngine()

    # Create dummy fusion result for testing
    from L1_cognition.engines.multi_query_fusion import FusionResult
    from L1_cognition.engines.semantic_retriever import RetrievalResult

    dummy_results = [
        RetrievalResult(
            content="UniversalWriteGateway write operations implementation",
            metadata={"artifact_type": "code", "layer": "L2", "file_path": "uwg.py"},
            score=0.8,
            collection="repo_code_chunks",
        ),
        RetrievalResult(
            content="ADG static scanner dependency graph analysis",
            metadata={"artifact_type": "sym", "layer": "L4", "file_path": "scanner.py"},
            score=0.7,
            collection="repo_symbols",
        ),
        RetrievalResult(
            content="L1 cognition semantic retrieval components",
            metadata={"artifact_type": "code", "layer": "L1", "file_path": "retriever.py"},
            score=0.6,
            collection="repo_code_chunks",
        ),
    ]

    dummy_fusion = FusionResult(
        original_query="What does UWG do?",
        collection_results={"repo_code_chunks": dummy_results[::2], "repo_symbols": [dummy_results[1]]},
        fusion_strategy="score_fusion",
        total_results=3,
        execution_time_ms=50.0,
        query_variations_used=["explain UWG", "describe UniversalWriteGateway"],
    )

    try:
        rerank_result = reranker.rerank_results(
            fusion_result=dummy_fusion,
            query="What does UWG do?",
            max_results=10,
        )

        print(f"Original results: {len(rerank_result.original_results)}")
        print(f"Reranked results: {len(rerank_result.reranked_results)}")
        print(f"Execution time: {rerank_result.execution_time_ms:.2f}ms")
        print(f"Model type: {rerank_result.model_info['model_type']}")
        print(f"Features used: {len(rerank_result.features_used)}")

        print("\nReranked results:")
        for i, (result, score) in enumerate(zip(rerank_result.reranked_results, rerank_result.reranking_scores), 1):
            print(f"  {i}. Score: {score:.3f} - {result.content[:50]}...")

        print("\n✅ Reranking engine test successful")
        return True

    except Exception as e:
        print(f"❌ Reranking engine test failed: {e}")
        return False


async def test_advanced_retrieval():
    """Test complete advanced retrieval pipeline."""
    print("\n=== Advanced Retrieval Pipeline Test ===\n")

    try:
        retriever = AdvancedSemanticRetriever()

        test_queries = [
            "What does the UniversalWriteGateway do?",
            "Show me the blast radius for ADG scanner changes",
            "Find failures related to memory leaks in L1 cognition",
        ]

        retrieval_success = 0

        for query in test_queries:
            print(f"Testing advanced retrieval: {query}")

            try:
                request = AdvancedRetrievalRequest(
                    query=query,
                    fusion_strategy="reciprocal_rank_fusion",
                    enable_reranking=True,
                    max_final_results=5,
                )

                response = await retriever.retrieve(request)

                print(f"  Query type: {response.query_type.value}")
                print(f"  Primary collections: {response.routing_decision['primary_collections']}")
                print(f"  Final results: {len(response.final_results)}")
                print(f"  Total time: {response.execution_time_ms:.2f}ms")

                if response.reranking_result:
                    print(f"  Reranking: {response.reranking_result.model_info['model_type']}")
                    print(f"  Reranking time: {response.reranking_result.execution_time_ms:.2f}ms")

                # Show top results
                print("  Top results:")
                for i, result in enumerate(response.final_results[:2], 1):
                    print(f"    {i}. [{result.collection}] {result.content[:40]}...")
                    if hasattr(result, 'score'):
                        print(f"       Score: {result.score:.3f}")

                if len(response.final_results) > 0:
                    retrieval_success += 1
                    print("  ✅ Advanced retrieval successful")
                else:
                    print("  ⚠️  No results found")

            except Exception as e:
                print(f"  ❌ Advanced retrieval failed: {e}")

            print("-" * 60)

        print(f"\nAdvanced Retrieval Results: {retrieval_success}/{len(test_queries)} successful")
        return retrieval_success > 0

    except Exception as e:
        print(f"Advanced retrieval test failed: {e}")
        return False


async def test_fusion_strategies():
    """Test different fusion strategies."""
    print("\n=== Fusion Strategies Comparison Test ===\n")

    try:
        retriever = AdvancedSemanticRetriever()

        query = "UniversalWriteGateway implementation and usage"
        strategies = ["reciprocal_rank_fusion", "score_fusion", "collection_priority_fusion"]

        strategy_results = {}

        for strategy in strategies:
            try:
                request = AdvancedRetrievalRequest(
                    query=query,
                    fusion_strategy=strategy,
                    enable_reranking=False,  # Disable for fair comparison
                    max_final_results=10,
                )

                response = await retriever.retrieve(request)

                strategy_results[strategy] = {
                    "results_count": len(response.final_results),
                    "execution_time": response.execution_time_ms,
                    "collections_searched": len(response.fusion_result.collection_results),
                }

                print(f"{strategy}:")
                print(f"  Results: {len(response.final_results)}")
                print(f"  Time: {response.execution_time_ms:.2f}ms")
                print(f"  Collections: {len(response.fusion_result.collection_results)}")

            except Exception as e:
                print(f"{strategy}: Failed - {e}")
                strategy_results[strategy] = {"error": str(e)}

            print("-" * 40)

        # Compare results
        successful_strategies = {k: v for k, v in strategy_results.items() if 'error' not in v}

        if successful_strategies:
            print("\nStrategy Comparison Summary:")
            for strategy, results in successful_strategies.items():
                print(f"  {strategy}: {results['results_count']} results, {results['execution_time']:.2f}ms")

            print("\n✅ Fusion strategies comparison successful")
            return True
        else:
            print("\n⚠️  No fusion strategies succeeded")
            return False

    except Exception as e:
        print(f"Fusion strategies test failed: {e}")
        return False


async def test_performance():
    """Test performance of the advanced retrieval system."""
    print("\n=== Performance Test ===\n")

    try:
        retriever = AdvancedSemanticRetriever()

        # Performance test queries
        perf_queries = [
            "UWG write operations",
            "ADG graph analysis",
            "L1 cognition retrieval",
            "L5 safety validation",
            "L0 routing dispatch",
        ]

        start_time = time.time()
        total_results = 0
        successful_queries = 0

        for query in perf_queries:
            try:
                request = AdvancedRetrievalRequest(
                    query=query,
                    fusion_strategy="reciprocal_rank_fusion",
                    enable_reranking=True,
                    max_final_results=5,
                )

                response = await retriever.retrieve(request)
                total_results += len(response.final_results)
                successful_queries += 1

                print(f"  {query}: {len(response.final_results)} results in {response.execution_time_ms:.2f}ms")

            except Exception as e:
                print(f"  {query}: Failed - {e}")

        total_time = time.time() - start_time

        print("\nPerformance Summary:")
        print(f"  Total queries: {len(perf_queries)}")
        print(f"  Successful: {successful_queries}")
        print(f"  Total results: {total_results}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Avg time per query: {(total_time / len(perf_queries) * 1000):.2f}ms")
        print(f"  Results per second: {total_results / total_time:.1f}")

        success_rate = successful_queries / len(perf_queries)
        print(f"  Success rate: {success_rate:.1%}")

        return success_rate >= 0.8  # 80% success rate threshold

    except Exception as e:
        print(f"Performance test failed: {e}")
        return False


async def main():
    """Main test execution for Wave 4."""
    print("Wave 4: Advanced Retrieval & Reranking Test Suite")
    print("=" * 60)

    # Run all tests
    test_results = {}

    test_results["query_routing"] = await test_query_routing()
    test_results["multi_query_fusion"] = await test_multi_query_fusion()
    test_results["reranking_engine"] = await test_reranking_engine()
    test_results["advanced_retrieval"] = await test_advanced_retrieval()
    test_results["fusion_strategies"] = await test_fusion_strategies()
    test_results["performance"] = await test_performance()

    # Summary
    print("\n" + "=" * 60)
    print("Wave 4 Test Results Summary:")
    print("=" * 60)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed_tests += 1

    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All Wave 4 tests passed!")
        print("\nWave 4 Success: Advanced Retrieval & Reranking fully functional!")
    elif passed_tests >= total_tests * 0.8:
        print("✅ Wave 4 mostly successful (80%+ tests passed)")
    else:
        print("⚠️  Wave 4 needs attention (less than 80% tests passed)")

    # Show system stats
    print("\n" + "=" * 60)
    print("System Statistics:")
    try:
        retriever = AdvancedSemanticRetriever()
        stats = retriever.get_retrieval_stats()

        print(f"  Collections: {len(stats['base_retriever']['collections'])}")
        print(f"  Total Documents: {stats['base_retriever']['total_documents']:,}")
        print(f"  Query Types: {len(stats['query_router']['query_types'])}")
        print(f"  Fusion Strategies: {len(stats['fusion_engine']['fusion_strategies'])}")
        print(f"  Reranking Model: {'Loaded' if stats['reranking_engine']['model_loaded'] else 'Rule-based'}")

    except Exception as e:
        print(f"  Could not retrieve stats: {e}")


if __name__ == "__main__":
    asyncio.run(main())
