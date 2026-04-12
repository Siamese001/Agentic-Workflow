"""Tests for retrieval benchmarking."""

from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchEngine,
)
from agentic_core.L3_orchestration.reasoning.engines.retrieval_benchmark import (
    BenchmarkMetrics,
    BenchmarkQuery,
    RetrievalBenchmark,
    RetrievalQualityMetrics,
)


def test_benchmark_metrics_creation():
    """Test BenchmarkMetrics dataclass."""
    metrics = BenchmarkMetrics(
        query_count=10,
        avg_latency_ms=50.0,
        p95_latency_ms=80.0,
        p99_latency_ms=100.0,
        total_results=100,
        avg_results_per_query=10.0,
    )

    assert metrics.query_count == 10
    assert metrics.avg_latency_ms == 50.0
    assert metrics.p95_latency_ms == 80.0


def test_retrieval_quality_metrics_creation():
    """Test RetrievalQualityMetrics dataclass."""
    metrics = RetrievalQualityMetrics(
        precision_at_k=0.8,
        recall_at_k=0.7,
        mean_reciprocal_rank=0.75,
        ndcg_at_k=0.85,
    )

    assert metrics.precision_at_k == 0.8
    assert metrics.recall_at_k == 0.7
    assert metrics.mean_reciprocal_rank == 0.75


def test_benchmark_query_creation():
    """Test BenchmarkQuery dataclass."""
    query = BenchmarkQuery(
        query="test query",
        expected_chunk_ids=["chunk1", "chunk2"],
        intent="semantic",
    )

    assert query.query == "test query"
    assert len(query.expected_chunk_ids) == 2
    assert query.intent == "semantic"


def test_performance_benchmark():
    """Test performance benchmark execution."""
    engine = HybridSearchEngine()
    benchmark = RetrievalBenchmark(engine)

    # Run with mock queries (will fail without ChromaDB, but tests structure)
    queries = ["test query 1", "test query 2"]

    # This will return metrics with zeros since ChromaDB is not available
    metrics = benchmark.run_performance_benchmark(queries, iterations=1)

    assert metrics.query_count == 2  # 2 queries * 1 iteration
    assert isinstance(metrics.avg_latency_ms, float)


def test_quality_benchmark():
    """Test quality benchmark execution."""
    engine = HybridSearchEngine()
    benchmark = RetrievalBenchmark(engine)

    queries = [
        BenchmarkQuery(
            query="test query",
            expected_chunk_ids=["chunk1", "chunk2"],
        ),
    ]

    # This will return metrics with zeros since ChromaDB is not available
    metrics = benchmark.run_quality_benchmark(queries, k=5)

    assert isinstance(metrics.precision_at_k, float)
    assert isinstance(metrics.recall_at_k, float)
    assert isinstance(metrics.mean_reciprocal_rank, float)


def test_governance_benchmark():
    """Test governance benchmark execution."""
    engine = HybridSearchEngine()
    benchmark = RetrievalBenchmark(engine)

    queries = ["test query 1", "test query 2"]
    governance_filter = {"layers": ["L2"]}

    # This will return statistics (zeros since ChromaDB is not available)
    stats = benchmark.run_governance_benchmark(queries, governance_filter)

    assert "avg_results_without_filter" in stats
    assert "avg_results_with_filter" in stats
    assert "filter_reduction_pct" in stats
    assert isinstance(stats["filter_reduction_pct"], float)


def test_quality_benchmark_empty_queries():
    """Test quality benchmark with empty query list."""
    engine = HybridSearchEngine()
    benchmark = RetrievalBenchmark(engine)

    metrics = benchmark.run_quality_benchmark([], k=5)

    assert metrics.precision_at_k == 0.0
    assert metrics.recall_at_k == 0.0
    assert metrics.mean_reciprocal_rank == 0.0


def test_performance_benchmark_empty_queries():
    """Test performance benchmark with empty query list."""
    engine = HybridSearchEngine()
    benchmark = RetrievalBenchmark(engine)

    metrics = benchmark.run_performance_benchmark([])

    assert metrics.query_count == 0
    assert metrics.avg_latency_ms == 0.0
