"""
cache Metrics Collector - Singleton for tracking Redis/Pinecone performance

Tracks:
- Hit/miss rates per operation type
- Latency statistics
- Operation counts

Integrates with dashboard for visibility.
"""

import threading
import time
from collections import defaultdict
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class CacheMetrics:
    """
    Thread-safe singleton for cache metrics collection.

    Usage:
        metrics = CacheMetrics()
        metrics.record("redis_get", hit=True, latency_ms=1.5)
        stats = metrics.get_stats()
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._stats_lock = threading.Lock()
        self.stats: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"hits": 0, "misses": 0, "latency_sum": 0.0, "ops": 0, "errors": 0}
        )
        self._start_time = time.time()

    def record(self, operation: str, hit: bool, latency_ms: float) -> None:
        """Record a cache operation."""
        with self._stats_lock:
            if hit:
                self.stats[operation]["hits"] += 1
            else:
                self.stats[operation]["misses"] += 1
            self.stats[operation]["latency_sum"] += latency_ms
            self.stats[operation]["ops"] += 1

    def record_error(self, operation: str) -> None:
        """Record a cache error."""
        with self._stats_lock:
            self.stats[operation]["errors"] += 1

    def get_stats(self) -> dict[str, dict[str, Any]]:
        """Get aggregated statistics for all operations."""
        with self._stats_lock:
            result = {}
            for op, data in self.stats.items():
                total = data["ops"]
                result[op] = {
                    "hit_rate": round(data["hits"] / total, 4) if total else 0.0,
                    "miss_rate": round(data["misses"] / total, 4) if total else 0.0,
                    "avg_latency_ms": round(data["latency_sum"] / total, 2) if total else 0.0,
                    "total_operations": total,
                    "total_errors": data["errors"],
                    "hits": data["hits"],
                    "misses": data["misses"],
                }
            return result

    def get_summary(self) -> dict[str, Any]:
        """Get high-level summary for dashboard."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CacheMetrics.get_summary")

        stats = self.get_stats()
        total_hits = sum(s["hits"] for s in stats.values())
        total_misses = sum(s["misses"] for s in stats.values())
        total_ops = total_hits + total_misses
        total_errors = sum(s["total_errors"] for s in stats.values())
        return {
            "overall_hit_rate": round(total_hits / total_ops, 4) if total_ops else 0.0,
            "total_operations": total_ops,
            "total_errors": total_errors,
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "operations_by_type": stats,
        }

    def reset(self) -> None:
        """Reset all statistics (for testing)."""
        with self._stats_lock:
            self.stats.clear()
            self._start_time = time.time()


_metrics = CacheMetrics()


def get_cache_metrics() -> CacheMetrics:
    """Get the global cache metrics instance."""
    return _metrics
