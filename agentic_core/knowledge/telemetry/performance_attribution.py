"""Performance Attribution.

Latency attribution and success rate tracking by query type.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a query type."""
    query_count: int = 0
    total_latency_ms: float = 0.0
    success_count: int = 0
    cache_hit_count: int = 0
    cache_miss_count: int = 0

    @property
    def avg_latency_ms(self) -> float:
        if self.query_count == 0:
            return 0.0
        return self.total_latency_ms / self.query_count

    @property
    def success_rate(self) -> float:
        if self.query_count == 0:
            return 0.0
        return self.success_count / self.query_count

    @property
    def cache_hit_rate(self) -> float:
        total_cache = self.cache_hit_count + self.cache_miss_count
        if total_cache == 0:
            return 0.0
        return self.cache_hit_count / total_cache


@dataclass
class PerformanceReport:
    """Performance report."""
    timestamp: float = field(default_factory=time.time)
    overall_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    by_intent: dict[str, PerformanceMetrics] = field(default_factory=dict)
    by_domain: dict[str, PerformanceMetrics] = field(default_factory=dict)
    by_complexity: dict[str, PerformanceMetrics] = field(default_factory=dict)


class PerformanceAttribution:
    """Tracks performance by query attributes.

    The PerformanceAttribution provides latency attribution and
    success rate tracking categorized by query type.
    """

    def __init__(self):
        """Initialize the performance attribution."""
        self._metrics: dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self._by_intent: dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self._by_domain: dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self._by_complexity: dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)

        log.info("PerformanceAttribution initialized")

    def record_query(
        self,
        query_id: str,
        tags: Any,
        latency_ms: float,
        success: bool,
        cache_hit: bool = False,
    ) -> None:
        """Record a query's performance.

        Args:
            query_id: Query identifier
            tags: QueryTags from tagger
            latency_ms: Query latency in milliseconds
            success: Whether query succeeded
            cache_hit: Whether cache was hit
        """
        trace_id = f"perf_{query_id}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "PerformanceAttribution.record_query"
        )

        intent = getattr(tags, 'intent', 'unknown')
        domain = getattr(tags, 'domain', 'general')
        complexity = getattr(tags, 'complexity', 'medium')

        # Update intent metrics
        self._by_intent[intent].query_count += 1
        self._by_intent[intent].total_latency_ms += latency_ms
        if success:
            self._by_intent[intent].success_count += 1
        if cache_hit:
            self._by_intent[intent].cache_hit_count += 1
        else:
            self._by_intent[intent].cache_miss_count += 1

        # Update domain metrics
        self._by_domain[domain].query_count += 1
        self._by_domain[domain].total_latency_ms += latency_ms
        if success:
            self._by_domain[domain].success_count += 1

        # Update complexity metrics
        self._by_complexity[complexity].query_count += 1
        self._by_complexity[complexity].total_latency_ms += latency_ms
        if success:
            self._by_complexity[complexity].success_count += 1

        log.debug(f"Recorded performance: intent={intent}, latency={latency_ms:.1f}ms")

    def generate_report(self) -> PerformanceReport:
        """Generate performance report.

        Returns:
            PerformanceReport with aggregated metrics
        """
        # Calculate overall metrics
        overall = PerformanceMetrics()
        for metrics in self._by_intent.values():
            overall.query_count += metrics.query_count
            overall.total_latency_ms += metrics.total_latency_ms
            overall.success_count += metrics.success_count
            overall.cache_hit_count += metrics.cache_hit_count
            overall.cache_miss_count += metrics.cache_miss_count

        return PerformanceReport(
            overall_metrics=overall,
            by_intent=dict(self._by_intent),
            by_domain=dict(self._by_domain),
            by_complexity=dict(self._by_complexity),
        )

    def get_slowest_intents(self, n: int = 3) -> list[tuple]:
        """Get slowest intents.

        Args:
            n: Number to return

        Returns:
            List of (intent, avg_latency) tuples
        """
        sorted_intents = sorted(
            self._by_intent.items(),
            key=lambda x: x[1].avg_latency_ms,
            reverse=True
        )
        return [(intent, m.avg_latency_ms) for intent, m in sorted_intents[:n]]

    def get_lowest_success_domains(self, n: int = 3) -> list[tuple]:
        """Get domains with lowest success rates.

        Args:
            n: Number to return

        Returns:
            List of (domain, success_rate) tuples
        """
        sorted_domains = sorted(
            self._by_domain.items(),
            key=lambda x: x[1].success_rate
        )
        return [(domain, m.success_rate) for domain, m in sorted_domains[:n]]


# Global instance
_global_attribution: PerformanceAttribution | None = None


def get_performance_attribution() -> PerformanceAttribution:
    """Get or create the global performance attribution."""
    global _global_attribution
    if _global_attribution is None:
        _global_attribution = PerformanceAttribution()
    return _global_attribution
