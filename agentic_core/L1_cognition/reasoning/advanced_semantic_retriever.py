"""
Advanced Semantic Retriever for L1 Cognition
Integrates Wave 4 components: Query Routing, Multi-Query Fusion, and Reranking.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

from .multi_query_fusion import FusionResult, MultiQueryFusion
from .query_router import QueryRouter, QueryType
from .reranking_engine import RerankingEngine, RerankingResult
from .semantic_retriever import RetrievalResult, SemanticRetriever

logger = logging.getLogger(__name__)


@dataclass
class AdvancedRetrievalRequest:
    """Advanced retrieval request with all options."""

    query: str
    fusion_strategy: str = "reciprocal_rank_fusion"
    max_results_per_collection: int = 20
    max_final_results: int = 50
    enable_reranking: bool = True
    generate_query_variations: bool = True
    include_reasoning: bool = True


@dataclass
class AdvancedRetrievalResponse:
    """Advanced retrieval response with comprehensive results."""

    original_query: str
    query_type: QueryType
    routing_decision: dict[str, Any]
    fusion_result: FusionResult
    reranking_result: RerankingResult | None
    final_results: list[RetrievalResult]
    execution_time_ms: float
    component_breakdown: dict[str, Any]


class AdvancedSemanticRetriever:
    """
    Advanced semantic retriever integrating Wave 4 components.

    Combines intelligent query routing, multi-query fusion, and ML-based reranking
    to provide the most relevant search results across all ChromaDB collections.
    """

    def __init__(self, reranking_model_path: str | None = None):
        """
        Initialize advanced semantic retriever.

        Args:
            reranking_model_path: Path to LightGBM reranking model
        """
        # Initialize base components
        self.base_retriever = SemanticRetriever()
        self.query_router = QueryRouter()
        self.fusion_engine = MultiQueryFusion(self.base_retriever)
        self.reranking_engine = RerankingEngine(reranking_model_path)

        logger.info("Advanced semantic retriever initialized with Wave 4 components")

    async def retrieve(self, request: AdvancedRetrievalRequest) -> AdvancedRetrievalResponse:
        """
        Execute advanced retrieval with all Wave 4 components.

        Args:
            request: Advanced retrieval request

        Returns:
            Advanced retrieval response with comprehensive results
        """
        # Input validation
        if request is None:
            raise ValueError("request cannot be None")
        if not request.query or not request.query.strip():
            raise ValueError("request.query cannot be empty")
        if request.fusion_strategy not in self.fusion_engine.fusion_strategies:
            raise ValueError(f"Invalid fusion strategy: {request.fusion_strategy}")
        if request.max_results_per_collection <= 0:
            raise ValueError("max_results_per_collection must be positive")
        if request.max_final_results <= 0:
            raise ValueError("max_final_results must be positive")

        start_time = time.time()

        logger.info(f"Starting advanced retrieval: {request.query}")

        # Step 1: Query Routing
        available_collections = list(self.base_retriever.get_collection_stats().keys())
        routing_decision = self.query_router.route_query(request.query, available_collections)

        routing_info = {
            "query_type": routing_decision.query_type.value,
            "primary_collections": routing_decision.primary_collections,
            "secondary_collections": routing_decision.secondary_collections,
            "confidence": routing_decision.confidence,
            "reasoning": routing_decision.reasoning,
        }

        logger.info(f"Query routed to {len(routing_decision.primary_collections)} primary collections")

        # Step 2: Multi-Query Fusion
        fusion_result = await self.fusion_engine.execute_fusion_search(
            query=request.query,
            fusion_strategy=request.fusion_strategy,
            max_results_per_collection=request.max_results_per_collection,
            generate_variations=request.generate_query_variations,
        )

        logger.info(
            f"Fusion search: {fusion_result.total_results} results in {fusion_result.execution_time_ms:.2f}ms"
        )

        # Step 3: Reranking (if enabled)
        reranking_result = None
        final_results = []

        if request.enable_reranking and fusion_result.total_results > 0:
            reranking_result = self.reranking_engine.rerank_results(
                fusion_result=fusion_result,
                query=request.query,
                max_results=request.max_final_results,
            )
            final_results = reranking_result.reranked_results

            logger.info(
                f"Reranking completed: {len(final_results)} results in {reranking_result.execution_time_ms:.2f}ms"
            )
        else:
            # Apply fusion strategy without reranking
            all_results = []
            for collection_results in fusion_result.collection_results.values():
                all_results.extend(collection_results)

            final_results = self.fusion_engine.apply_fusion_strategy(
                collection_results=fusion_result.collection_results,
                fusion_strategy=request.fusion_strategy,
                max_final_results=request.max_final_results,
            )

            logger.info(f"Fusion strategy applied: {len(final_results)} final results")

        # Calculate total execution time
        total_time_ms = (time.time() - start_time) * 1000

        # Generate component breakdown
        component_breakdown = self._generate_component_breakdown(
            fusion_result,
            reranking_result,
            total_time_ms,
        )

        # Create response
        response = AdvancedRetrievalResponse(
            original_query=request.query,
            query_type=routing_decision.query_type,
            routing_decision=routing_info,
            fusion_result=fusion_result,
            reranking_result=reranking_result,
            final_results=final_results,
            execution_time_ms=total_time_ms,
            component_breakdown=component_breakdown,
        )

        logger.info(
            f"Advanced retrieval completed: {len(final_results)} final results in {total_time_ms:.2f}ms"
        )

        return response

    async def simple_retrieve(self, query: str, max_results: int = 20) -> list[RetrievalResult]:
        """
        Simple retrieval interface with default settings.

        Args:
            query: Query string
            max_results: Maximum number of results

        Returns:
            List of retrieval results
        """
        request = AdvancedRetrievalRequest(
            query=query,
            max_final_results=max_results,
            enable_reranking=True,
        )

        response = await self.retrieve(request)
        return response.final_results

    def _generate_component_breakdown(
        self,
        fusion_result: FusionResult,
        reranking_result: RerankingResult | None,
        total_time_ms: float,
    ) -> dict[str, Any]:
        """Generate breakdown of component performance."""
        breakdown = {
            "total_time_ms": total_time_ms,
            "fusion_time_ms": fusion_result.execution_time_ms,
            "collections_searched": len(fusion_result.collection_results),
            "total_fusion_results": fusion_result.total_results,
            "fusion_strategy": fusion_result.fusion_strategy,
            "query_variations_used": len(fusion_result.query_variations_used),
        }

        # Add reranking breakdown if available
        if reranking_result:
            breakdown.update(
                {
                    "reranking_enabled": True,
                    "reranking_time_ms": reranking_result.execution_time_ms,
                    "reranking_model": reranking_result.model_info,
                    "original_results": len(reranking_result.original_results),
                    "reranked_results": len(reranking_result.reranked_results),
                    "features_used": reranking_result.features_used,
                }
            )
        else:
            breakdown.update(
                {
                    "reranking_enabled": False,
                    "reranking_reason": "Disabled or no results to rerank",
                }
            )

        # Add collection-specific breakdown
        collection_stats = {}
        for collection, results in fusion_result.collection_results.items():
            collection_stats[collection] = {
                "result_count": len(results),
                "avg_score": np.mean([getattr(r, "score", 0.5) for r in results]) if results else 0.0,
                "top_score": max([getattr(r, "score", 0.5) for r in results]) if results else 0.0,
            }

        breakdown["collection_stats"] = collection_stats

        return breakdown

    def get_retrieval_stats(self) -> dict[str, Any]:
        """Get comprehensive retrieval statistics."""
        return {
            "base_retriever": {
                "collections": list(self.base_retriever.get_collection_stats().keys()),
                "total_documents": sum(
                    stats["document_count"] for stats in self.base_retriever.get_collection_stats().values()
                ),
            },
            "query_router": self.query_router.get_routing_stats(),
            "fusion_engine": self.fusion_engine.get_fusion_stats(),
            "reranking_engine": self.reranking_engine.get_reranking_stats(),
        }

    async def benchmark_retrieval(
        self,
        queries: list[str],
        strategies: list[str] = None,
    ) -> dict[str, Any]:
        """
        Benchmark different retrieval strategies.

        Args:
            queries: List of test queries
            strategies: List of fusion strategies to test

        Returns:
            Benchmark results
        """
        if strategies is None:
            strategies = ["reciprocal_rank_fusion", "score_fusion", "collection_priority_fusion"]

        benchmark_results = {}

        for strategy in strategies:
            strategy_results = []

            for query in queries:
                try:
                    request = AdvancedRetrievalRequest(
                        query=query,
                        fusion_strategy=strategy,
                        enable_reranking=False,  # Disable for fair comparison
                    )

                    response = await self.retrieve(request)

                    strategy_results.append(
                        {
                            "query": query,
                            "total_results": len(response.final_results),
                            "execution_time_ms": response.execution_time_ms,
                            "collections_searched": len(response.fusion_result.collection_results),
                        }
                    )

                except Exception as e:
                    logger.error(f"Benchmark query failed: {query} - {e}")
                    strategy_results.append(
                        {
                            "query": query,
                            "error": str(e),
                        }
                    )

            # Calculate strategy statistics
            successful_results = [r for r in strategy_results if "error" not in r]

            if successful_results:
                avg_time = np.mean([r["execution_time_ms"] for r in successful_results])
                avg_results = np.mean([r["total_results"] for r in successful_results])

                benchmark_results[strategy] = {
                    "avg_execution_time_ms": avg_time,
                    "avg_results_count": avg_results,
                    "success_rate": len(successful_results) / len(strategy_results),
                    "detailed_results": strategy_results,
                }
            else:
                benchmark_results[strategy] = {
                    "avg_execution_time_ms": 0,
                    "avg_results_count": 0,
                    "success_rate": 0,
                    "detailed_results": strategy_results,
                }

        return benchmark_results


# Example usage and testing
async def main():
    """Test the advanced semantic retriever."""
    retriever = AdvancedSemanticRetriever()

    # Test queries
    test_queries = [
        "What does the UniversalWriteGateway do?",
        "Show me the blast radius for ADG scanner changes",
        "Find failures related to memory leaks in L1 cognition",
        "How does the routing between L0 and L2 work?",
        "What were the recent commits affecting safety layer?",
    ]

    print("Advanced Semantic Retriever Test:")
    print("=" * 60)

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)

        try:
            request = AdvancedRetrievalRequest(
                query=query,
                fusion_strategy="reciprocal_rank_fusion",
                enable_reranking=True,
                max_final_results=10,
            )

            response = await retriever.retrieve(request)

            print(f"Query Type: {response.query_type.value}")
            print(f"Primary Collections: {response.routing_decision['primary_collections']}")
            print(f"Final Results: {len(response.final_results)}")
            print(f"Total Time: {response.execution_time_ms:.2f}ms")

            if response.reranking_result:
                print(f"Reranking: {response.reranking_result.model_info['model_type']}")

            # Show top results
            for j, result in enumerate(response.final_results[:3], 1):
                print(f"  {j}. [{result.collection}] {result.content[:60]}...")
                if hasattr(result, "score"):
                    print(f"     Score: {result.score:.3f}")

        except Exception as e:
            print(f"Error: {e}")

    # Show retrieval stats
    print("\n" + "=" * 60)
    print("Retrieval Statistics:")
    stats = retriever.get_retrieval_stats()
    print(f"Total Collections: {len(stats['base_retriever']['collections'])}")
    print(f"Total Documents: {stats['base_retriever']['total_documents']}")
    print(f"Query Types: {len(stats['query_router']['query_types'])}")
    print(f"Fusion Strategies: {len(stats['fusion_engine']['fusion_strategies'])}")
    print(f"Reranking Model: {stats['reranking_engine']['model_loaded']}")


if __name__ == "__main__":
    import numpy as np

    asyncio.run(main())
