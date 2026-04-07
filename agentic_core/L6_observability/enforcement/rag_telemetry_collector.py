from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_telemetry_event,
    _emit_signs_execution_trace,
    record_execution_trace,
)

"""RAG Telemetry Collector - L6 observability with OpenTelemetry integration.

Tracks RAG performance metrics for dashboard visualization.
Phase 3: Now consumes OpenTelemetry spans for comprehensive telemetry.
"""
from collections import defaultdict
from dataclasses import dataclass, field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)

record_execution_trace("rag_telemetry_collector", "rag_telemetry_collector_trace")


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
    latency_warnings: int = 0
    namespace_stats: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(dict))
    latency_buckets: dict[str, int] = field(
        default_factory=lambda: {"0-50ms": 0, "50-100ms": 0, "100-200ms": 0, "200-500ms": 0, "500ms+": 0},
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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RagTelemetryCollector.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RagTelemetryCollector.__init__", "p0_governance")
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "RagTelemetryCollector.record_query",
        )

        self.metrics.total_queries += 1
        if cached:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1
        if reranked:
            self.metrics.rerank_count += 1
        self._latency_samples.append(latency_ms)
        if latency_ms > 500:
            self.metrics.latency_warnings += 1
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
        self._doc_count_samples.append(doc_count)
        if faithfulness_score > 0:
            self._faithfulness_samples.append(faithfulness_score)
        if namespace not in self.metrics.namespace_stats:
            self.metrics.namespace_stats[namespace] = {"queries": 0, "cache_hits": 0}
        self.metrics.namespace_stats[namespace]["queries"] += 1
        if cached:
            self.metrics.namespace_stats[namespace]["cache_hits"] += 1
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

    def consume_otel_spans(self, spans: list[dict[str, Any]]) -> int:
        """Consume OpenTelemetry spans for RAG telemetry analysis.

        Phase 3: Integrates OpenTelemetry spans into L6 RAG telemetry.
        Extracts RAG-relevant metrics from span attributes.

        Parameters
        ----------
        spans : list[dict[str, Any]]
            OpenTelemetry span dictionaries from tracing adapter.

        Returns
        -------
        int
            Number of RAG-relevant spans processed.
        """
        if not spans:
            return 0

        processed = 0
        for span in spans:
            # Check if this is a RAG-related span
            name = span.get("name", "")
            attributes = span.get("attributes", {})

            # Look for RAG operation indicators
            is_rag_span = (
                "rag" in name.lower() or
                "retrieval" in name.lower() or
                "embedding" in name.lower() or
                attributes.get("rag.operation") is not None
            )

            if is_rag_span:
                # Extract RAG metrics from span attributes
                latency_ms = attributes.get("rag.latency_ms", 0)
                doc_count = attributes.get("rag.doc_count", 0)
                cached = attributes.get("rag.cached", False)
                reranked = attributes.get("rag.reranked", False)
                faithfulness = attributes.get("rag.faithfulness_score", 0.0)
                namespace = attributes.get("rag.namespace", "sovereign-core")

                self.record_query(
                    latency_ms=latency_ms,
                    cached=cached,
                    reranked=reranked,
                    doc_count=doc_count,
                    faithfulness_score=faithfulness,
                    namespace=namespace,
                )
                processed += 1

        _emit_records_telemetry_event(
            "rag_telemetry_collector", "L6_OBSERVABILITY", "otel_spans_consumed",
            processed_count=processed,
            total_spans=len(spans),
        )

        return processed
