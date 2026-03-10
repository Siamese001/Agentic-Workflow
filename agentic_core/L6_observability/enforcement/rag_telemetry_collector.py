from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
RAG Telemetry Collector - L6 observability
Tracks RAG performance metrics for dashboard visualization
"""
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RagMetrics:
    """RAG performance metrics."""

    total_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    avg_documents_returned: float = 0.0
    avg_faithfulness_score: float = 0.0
    rerank_count: int = 0
    hallucination_warnings: int = 0
    dimension_mismatches: int = 0
    batch_upsert_failures: int = 0
    latency_warnings: int = 0  # >500ms

    # Per-namespace metrics
    namespace_stats: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(dict))

    # Latency histogram
    latency_buckets: dict[str, int] = field(
        default_factory=lambda: {
            "0-50ms": 0,
            "50-100ms": 0,
            "100-200ms": 0,
            "200-500ms": 0,
            "500ms+": 0,
        },
    )


class RagTelemetryCollector:
    """
    Collects RAG telemetry for L6 observability dashboard.
    Singleton pattern for global access.
    """

    _instance: RagTelemetryCollector | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.metrics = RagMetrics()
        self._latency_samples: list[float] = []
        self._faithfulness_samples: list[float] = []
        self._doc_count_samples: list[int] = []
        self._initialized = True

    def record_query(
        self,
        latency_ms: float,
        cached: bool,
        reranked: bool,
        doc_count: int,
        faithfulness_score: float = 0.0,
        namespace: str = "sovereign-core",
    ) -> None:
        """Record a RAG query execution."""
        self.metrics.total_queries += 1

        # cache tracking
        if cached:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1

        # Reranking tracking
        if reranked:
            self.metrics.rerank_count += 1

        # Latency tracking
        self._latency_samples.append(latency_ms)
        if latency_ms > 500:
            self.metrics.latency_warnings += 1

        # Latency histogram
        if latency_ms < 50:
            self.metrics.latency_buckets["0-50ms"] += 1
        elif latency_ms < 100:
            self.metrics.latency_buckets["50-100ms"] += 1
        elif latency_ms < 200:
            self.metrics.latency_buckets["100-200ms"] += 1
        elif latency_ms < 500:
            self.metrics.latency_buckets["200-500ms"] += 1
        else:
            self.metrics.latency_buckets["500ms+"] += 1

        # Document count tracking
        self._doc_count_samples.append(doc_count)

        # Faithfulness tracking
        if faithfulness_score > 0:
            self._faithfulness_samples.append(faithfulness_score)

        # Namespace tracking
        if namespace not in self.metrics.namespace_stats:
            self.metrics.namespace_stats[namespace] = {"queries": 0, "cache_hits": 0}
        self.metrics.namespace_stats[namespace]["queries"] += 1
        if cached:
            self.metrics.namespace_stats[namespace]["cache_hits"] += 1

        # Update aggregates
        self._update_aggregates()

    def _update_aggregates(self) -> None:
        """Update aggregate metrics from samples."""
        if self._latency_samples:
            self.metrics.avg_latency_ms = sum(self._latency_samples) / len(self._latency_samples)
            sorted_latencies = sorted(self._latency_samples)
            p95_idx = int(len(sorted_latencies) * 0.95)
            p99_idx = int(len(sorted_latencies) * 0.99)
            self.metrics.p95_latency_ms = sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else 0
            self.metrics.p99_latency_ms = sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else 0

        if self._doc_count_samples:
            self.metrics.avg_documents_returned = sum(self._doc_count_samples) / len(self._doc_count_samples)

        if self._faithfulness_samples:
            self.metrics.avg_faithfulness_score = sum(self._faithfulness_samples) / len(
                self._faithfulness_samples,
            )

    def record_hallucination_warning(self) -> None:
        """Record a hallucination warning from L5 guardrail."""
        self.metrics.hallucination_warnings += 1

    def record_dimension_mismatch(self) -> None:
        """Record a dimension mismatch from Pinecone store."""
        self.metrics.dimension_mismatches += 1

    def get_metrics(self) -> RagMetrics:
        """Get current RAG metrics snapshot."""
        return self.metrics
