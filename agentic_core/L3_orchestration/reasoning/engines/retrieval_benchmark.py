"""Retrieval benchmarking infrastructure for hybrid search."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchEngine,
    HybridSearchResult,
)

Logger = logging.getLogger(__name__)


@dataclass
class BenchmarkQuery:
    """A benchmark query with expected results."""

    query: str
    expected_chunk_ids: list[str] = field(default_factory=list)
    intent: str = "semantic"  # semantic, structural, or hybrid


@dataclass
class BenchmarkMetrics:
    """Benchmark execution metrics."""

    query_count: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    total_results: int = 0
    avg_results_per_query: float = 0.0


@dataclass
class RetrievalQualityMetrics:
    """Retrieval quality metrics."""

    precision_at_k: float = 0.0  # Precision@k
    recall_at_k: float = 0.0  # Recall@k
    mean_reciprocal_rank: float = 0.0  # MRR
    ndcg_at_k: float = 0.0  # NDCG@k


class RetrievalBenchmark:
    """Benchmark retrieval quality and performance."""

    def __init__(self, engine: HybridSearchEngine):
        """Initialize benchmark.

        Args:
            engine: HybridSearchEngine instance
        """
        self.engine = engine

    def run_performance_benchmark(
        self, queries: list[str], iterations: int = 10
    ) -> BenchmarkMetrics:
        """Run performance benchmark.

        Args:
            queries: List of test queries
            iterations: Number of iterations per query

        Returns:
            BenchmarkMetrics with performance statistics
        """
        if not queries:
            return BenchmarkMetrics()

        latencies = []
        total_results = 0

        for _ in range(iterations):
            for query in queries:
                start_time = time.time()
                results = self.engine.search(query)
                elapsed_ms = (time.time() - start_time) * 1000

                latencies.append(elapsed_ms)
                total_results += len(results)

        # Calculate metrics
        latencies.sort()
        n = len(latencies)

        metrics = BenchmarkMetrics(
            query_count=n,
            avg_latency_ms=sum(latencies) / n,
            p95_latency_ms=latencies[int(n * 0.95)] if n > 0 else 0.0,
            p99_latency_ms=latencies[int(n * 0.99)] if n > 0 else 0.0,
            total_results=total_results,
            avg_results_per_query=total_results / n if n > 0 else 0.0,
        )

        Logger.info(f"Performance benchmark complete: {metrics}")
        return metrics

    def run_quality_benchmark(
        self, queries: list[BenchmarkQuery], k: int = 10
    ) -> RetrievalQualityMetrics:
        """Run retrieval quality benchmark.

        Args:
            queries: List of benchmark queries with expected results
            k: Number of top results to evaluate

        Returns:
            RetrievalQualityMetrics with quality statistics
        """
        if not queries:
            return RetrievalQualityMetrics()

        precisions = []
        recalls = []
        reciprocal_ranks = []
        dcg_scores = []

        for benchmark_query in queries:
            results = self.engine.search(benchmark_query.query)
            retrieved_ids = [r.chunk_id for r in results[:k]]
            expected_ids = set(benchmark_query.expected_chunk_ids)

            # Precision@k
            relevant_retrieved = len(set(retrieved_ids) & expected_ids)
            precision = relevant_retrieved / k if k > 0 else 0.0
            precisions.append(precision)

            # Recall@k
            recall = relevant_retrieved / len(expected_ids) if expected_ids else 0.0
            recalls.append(recall)

            # Mean Reciprocal Rank
            for i, chunk_id in enumerate(retrieved_ids):
                if chunk_id in expected_ids:
                    reciprocal_ranks.append(1.0 / (i + 1))
                    break
            else:
                reciprocal_ranks.append(0.0)

            # DCG@k
            dcg = 0.0
            for i, chunk_id in enumerate(retrieved_ids):
                relevance = 1.0 if chunk_id in expected_ids else 0.0
                dcg += relevance / (i + 1)
            dcg_scores.append(dcg)

        # Calculate metrics
        metrics = RetrievalQualityMetrics(
            precision_at_k=sum(precisions) / len(precisions) if precisions else 0.0,
            recall_at_k=sum(recalls) / len(recalls) if recalls else 0.0,
            mean_reciprocal_rank=sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0,
            ndcg_at_k=sum(dcg_scores) / len(dcg_scores) if dcg_scores else 0.0,
        )

        Logger.info(f"Quality benchmark complete: {metrics}")
        return metrics

    def run_governance_benchmark(
        self, queries: list[str], governance_filter: dict[str, Any]
    ) -> dict[str, Any]:
        """Benchmark governance filter effectiveness.

        Args:
            queries: List of test queries
            governance_filter: Governance filter to apply

        Returns:
            Governance filter statistics
        """
        results_without_filter = []
        results_with_filter = []

        for query in queries:
            # Without filter
            unfiltered = self.engine.search(query)
            results_without_filter.append(len(unfiltered))

            # With filter
            filtered = self.engine.search(query, governance_filter=governance_filter)
            results_with_filter.append(len(filtered))

        return {
            "avg_results_without_filter": sum(results_without_filter) / len(results_without_filter)
            if results_without_filter
            else 0.0,
            "avg_results_with_filter": sum(results_with_filter) / len(results_with_filter)
            if results_with_filter
            else 0.0,
            "filter_reduction_pct": (
                (sum(results_without_filter) - sum(results_with_filter))
                / sum(results_without_filter) * 100
                if results_without_filter and sum(results_without_filter) > 0
                else 0.0
            ),
        }
