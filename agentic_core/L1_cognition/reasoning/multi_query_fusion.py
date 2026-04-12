"""
Multi-Query Fusion Engine for L1 Cognition
Executes parallel searches across relevant ChromaDB collections.
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from .query_router import QueryRouter, RoutingDecision
from .semantic_retriever import RetrievalQuery, RetrievalResult, SemanticRetriever

logger = logging.getLogger(__name__)


@dataclass
class FusionQuery:
    """Enhanced query for fusion execution."""

    original_query: str
    routing_decision: RoutingDecision
    query_variations: list[str]
    max_results_per_collection: int
    fusion_strategy: str


@dataclass
class FusionResult:
    """Result from multi-query fusion."""

    original_query: str
    collection_results: dict[str, list[RetrievalResult]]
    fusion_strategy: str
    total_results: int
    execution_time_ms: float
    query_variations_used: list[str]


class MultiQueryFusion:
    """
    Multi-query fusion engine for parallel ChromaDB searches.

    Executes parallel searches across relevant collections and merges results
    using various fusion strategies.
    """

    def __init__(self, semantic_retriever: SemanticRetriever):
        """
        Initialize multi-query fusion engine.

        Args:
            semantic_retriever: Semantic retriever instance
        """
        if semantic_retriever is None:
            raise ValueError("semantic_retriever cannot be None")

        self.retriever = semantic_retriever
        self.router = QueryRouter()
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Fusion strategies
        self.fusion_strategies = [
            "reciprocal_rank_fusion",
            "score_fusion",
            "collection_priority_fusion",
            "hybrid_fusion",
        ]

        logger.info("Multi-query fusion engine initialized")

    async def execute_fusion_search(
        self,
        query: str,
        fusion_strategy: str = "reciprocal_rank_fusion",
        max_results_per_collection: int = 20,
        generate_variations: bool = True,
    ) -> FusionResult:
        """
        Execute multi-query fusion search.

        Args:
            query: Original query string
            fusion_strategy: Fusion strategy to use
            max_results_per_collection: Max results per collection
            generate_variations: Whether to generate query variations

        Returns:
            FusionResult with merged results
        """
        start_time = time.time()

        # Route query to collections
        available_collections = self.retriever.get_collection_stats().keys()
        routing_decision = self.router.route_query(query, list(available_collections))

        # Generate query variations
        query_variations = []
        if generate_variations:
            query_variations = self._generate_query_variations(query)

        # Create fusion query
        fusion_query = FusionQuery(
            original_query=query,
            routing_decision=routing_decision,
            query_variations=query_variations,
            max_results_per_collection=max_results_per_collection,
            fusion_strategy=fusion_strategy,
        )

        # Execute parallel searches
        collection_results = await self._execute_parallel_searches(fusion_query)

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        # Create fusion result
        result = FusionResult(
            original_query=query,
            collection_results=collection_results,
            fusion_strategy=fusion_strategy,
            total_results=sum(len(results) for results in collection_results.values()),
            execution_time_ms=execution_time_ms,
            query_variations_used=query_variations,
        )

        logger.info(f"Fusion search completed: {result.total_results} results in {execution_time_ms:.2f}ms")

        return result

    async def _execute_parallel_searches(self, fusion_query: FusionQuery) -> dict[str, list[RetrievalResult]]:
        """Execute parallel searches across collections."""
        collection_results = {}

        # Combine primary and secondary collections
        all_collections = (
            fusion_query.routing_decision.primary_collections
            + fusion_query.routing_decision.secondary_collections
        )

        # Create search tasks
        tasks = []
        for collection in all_collections:
            # Original query
            task = self._search_collection(collection, fusion_query.original_query, fusion_query)
            tasks.append(task)

            # Query variations (limit to avoid too many queries)
            for variation in fusion_query.query_variations[:2]:  # Max 2 variations
                task = self._search_collection(collection, variation, fusion_query)
                tasks.append(task)

        # Execute tasks concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Search task failed: {result}")
                    continue

                collection, search_results = result
                if collection not in collection_results:
                    collection_results[collection] = []

                # Add results (avoid duplicates)
                existing_ids = {r.metadata.get("file_path", "") for r in collection_results[collection]}
                for search_result in search_results:
                    result_id = search_result.metadata.get("file_path", "")
                    if result_id not in existing_ids:
                        collection_results[collection].append(search_result)
                        existing_ids.add(result_id)

        return collection_results

    async def _search_collection(
        self,
        collection: str,
        query_text: str,
        fusion_query: FusionQuery,
    ) -> tuple[str, list[RetrievalResult]]:
        """Search a single collection."""
        try:
            # Create retrieval query
            retrieval_query = RetrievalQuery(
                text=query_text,
                collections=[collection],
                max_results=fusion_query.max_results_per_collection,
            )

            # Execute search
            results = await self.retriever.retrieve(retrieval_query)

            return collection, results

        except Exception as e:
            logger.error(f"Failed to search collection {collection}: {e}")
            return collection, []

    def _generate_query_variations(self, query: str) -> list[str]:
        """Generate variations of the original query."""
        variations = []

        # Simple variation strategies
        query_lower = query.lower()

        # Add synonyms and related terms
        synonyms = {
            "function": ["method", "procedure", "routine"],
            "class": ["type", "object", "structure"],
            "component": ["module", "part", "element"],
            "failure": ["error", "bug", "issue", "problem"],
            "performance": ["speed", "efficiency", "optimization"],
            "dependency": ["reliance", "requirement", "coupling"],
        }

        # Generate synonym variations
        for word, synonym_list in synonyms.items():
            if word in query_lower:
                for synonym in synonym_list:
                    variation = query_lower.replace(word, synonym)
                    if variation != query_lower:
                        variations.append(variation)

        # Generate expanded variations
        if "what does" in query_lower:
            variations.append(query_lower.replace("what does", "explain"))
            variations.append(query_lower.replace("what does", "describe"))

        if "how does" in query_lower:
            variations.append(query_lower.replace("how does", "explain"))
            variations.append(query_lower.replace("how does", "describe"))

        # Generate component-specific variations
        if "uwg" in query_lower or "universal write gateway" in query_lower:
            variations.append(query_lower + " write operation")
            variations.append(query_lower + " execution")

        if "adg" in query_lower:
            variations.append(query_lower + " dependency graph")
            variations.append(query_lower + " static analysis")

        # Limit variations and remove duplicates
        unique_variations = list(set(variations[:5]))  # Max 5 variations

        return unique_variations

    def apply_fusion_strategy(
        self,
        collection_results: dict[str, list[RetrievalResult]],
        fusion_strategy: str,
        max_final_results: int = 50,
    ) -> list[RetrievalResult]:
        """
        Apply fusion strategy to merge results from multiple collections.

        Args:
            collection_results: Results per collection
            fusion_strategy: Fusion strategy to apply
            max_final_results: Maximum final results

        Returns:
            Merged and ranked results
        """
        if not collection_results:
            return []

        if fusion_strategy == "reciprocal_rank_fusion":
            return self._reciprocal_rank_fusion(collection_results, max_final_results)
        elif fusion_strategy == "score_fusion":
            return self._score_fusion(collection_results, max_final_results)
        elif fusion_strategy == "collection_priority_fusion":
            return self._collection_priority_fusion(collection_results, max_final_results)
        elif fusion_strategy == "hybrid_fusion":
            return self._hybrid_fusion(collection_results, max_final_results)
        else:
            # Default to reciprocal rank fusion
            return self._reciprocal_rank_fusion(collection_results, max_final_results)

    def _reciprocal_rank_fusion(
        self,
        collection_results: dict[str, list[RetrievalResult]],
        max_results: int,
        k: int = 60,
    ) -> list[RetrievalResult]:
        """Apply Reciprocal Rank Fusion (RRF)."""
        # Collect all unique results
        all_results = {}

        for collection, results in collection_results.items():
            for rank, result in enumerate(results, 1):
                # Create unique key
                key = f"{result.collection}:{result.metadata.get('file_path', '')}"

                if key not in all_results:
                    all_results[key] = {
                        "result": result,
                        "rrf_score": 0.0,
                        "collections": set(),
                        "ranks": [],
                    }

                # Add RRF score: 1 / (k + rank)
                rrf_score = 1.0 / (k + rank)
                all_results[key]["rrf_score"] += rrf_score
                all_results[key]["collections"].add(collection)
                all_results[key]["ranks"].append(rank)

        # Sort by RRF score
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x["rrf_score"],
            reverse=True,
        )

        # Create final results
        final_results = []
        for item in sorted_results[:max_results]:
            result = item["result"]
            result.score = item["rrf_score"]  # Update score with RRF score
            final_results.append(result)

        return final_results

    def _score_fusion(
        self,
        collection_results: dict[str, list[RetrievalResult]],
        max_results: int,
    ) -> list[RetrievalResult]:
        """Apply score-based fusion."""
        all_results = []

        for collection, results in collection_results.items():
            # Apply collection weight
            collection_weight = 1.0
            if collection in ["repo_symbols", "repo_adg_graph"]:
                collection_weight = 1.2  # Boost structural collections
            elif collection in ["repo_runtime_evidence", "repo_incidents_rca"]:
                collection_weight = 1.1  # Boost execution collections

            for result in results:
                result.score *= collection_weight
                all_results.append(result)

        # Sort by score and deduplicate
        all_results.sort(key=lambda x: x.score, reverse=True)

        # Remove duplicates
        seen = set()
        final_results = []
        for result in all_results:
            key = f"{result.collection}:{result.metadata.get('file_path', '')}"
            if key not in seen:
                seen.add(key)
                final_results.append(result)
                if len(final_results) >= max_results:
                    break

        return final_results

    def _collection_priority_fusion(
        self,
        collection_results: dict[str, list[RetrievalResult]],
        max_results: int,
    ) -> list[RetrievalResult]:
        """Apply collection priority fusion."""
        # Define collection priorities
        priority_order = [
            "repo_symbols",
            "repo_adg_graph",  # Highest priority
            "repo_code_chunks",
            "repo_runtime_evidence",  # Medium priority
            "repo_arch_docs",
            "repo_tests_guardrails",  # Lower priority
            "repo_git_history",
            "repo_incidents_rca",  # Lowest priority
        ]

        final_results = []
        seen = set()

        # Add results by priority
        for collection in priority_order:
            if collection in collection_results:
                for result in collection_results[collection]:
                    key = f"{result.collection}:{result.metadata.get('file_path', '')}"
                    if key not in seen:
                        seen.add(key)
                        final_results.append(result)
                        if len(final_results) >= max_results:
                            return final_results

        return final_results

    def _hybrid_fusion(
        self,
        collection_results: dict[str, list[RetrievalResult]],
        max_results: int,
    ) -> list[RetrievalResult]:
        """Apply hybrid fusion (combination of strategies)."""
        # First apply collection priority for top candidates
        priority_results = self._collection_priority_fusion(collection_results, max_results // 2)

        # Then apply score fusion for remaining
        remaining_collections = {
            col: results
            for col, results in collection_results.items()
            if len([r for r in results if r not in priority_results]) > 0
        }

        if remaining_collections:
            score_results = self._score_fusion(remaining_collections, max_results - len(priority_results))
            priority_results.extend(score_results)

        return priority_results[:max_results]

    def get_fusion_stats(self) -> dict[str, Any]:
        """Get fusion engine statistics."""
        return {
            "fusion_strategies": self.fusion_strategies,
            "max_workers": 10,
            "router_stats": self.router.get_routing_stats(),
        }


# Example usage and testing
async def main():
    """Test the multi-query fusion engine."""
    from ..retrievers.semantic_retriever import SemanticRetriever

    retriever = SemanticRetriever()
    fusion_engine = MultiQueryFusion(retriever)

    # Test queries
    test_queries = [
        "What does the UniversalWriteGateway do?",
        "Show me the blast radius for ADG scanner changes",
        "Find failures related to memory leaks in L1 cognition",
    ]

    print("Multi-Query Fusion Test:")
    for query in test_queries:
        print(f"\nQuery: {query}")

        # Test different fusion strategies
        for strategy in ["reciprocal_rank_fusion", "score_fusion", "collection_priority_fusion"]:
            try:
                result = await fusion_engine.execute_fusion_search(
                    query=query,
                    fusion_strategy=strategy,
                    max_results_per_collection=10,
                )

                print(f"  {strategy}: {result.total_results} results in {result.execution_time_ms:.2f}ms")

            except Exception as e:
                print(f"  {strategy}: Error - {e}")


if __name__ == "__main__":
    asyncio.run(main())
