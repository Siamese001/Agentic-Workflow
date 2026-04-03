"""Latency Analyzer.

Latency attribution and percentile tracking.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections import defaultdict
import statistics

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class LatencyReport:
    """Latency analysis report."""
    stage_name: str
    p50_ms: float
    p95_ms: float
    p99_ms: float
    mean_ms: float
    max_ms: float
    min_ms: float
    sample_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class LatencyAnalyzer:
    """Analyzes latency by pipeline stage.

    The LatencyAnalyzer tracks latency at each pipeline stage and
    provides percentile analysis for bottleneck identification.
    """

    def __init__(self):
        """Initialize the latency analyzer."""
        self._stage_latencies: Dict[str, List[float]] = defaultdict(list)

        log.info("LatencyAnalyzer initialized")

    def record_stage_latency(
        self,
        stage_name: str,
        latency_ms: float,
    ) -> None:
        """Record latency for a pipeline stage.

        Args:
            stage_name: Name of the pipeline stage
            latency_ms: Latency in milliseconds
        """
        self._stage_latencies[stage_name].append(latency_ms)

        # Keep only last 1000 measurements per stage
        if len(self._stage_latencies[stage_name]) > 1000:
            self._stage_latencies[stage_name] = self._stage_latencies[stage_name][-1000:]

    def generate_report(self, stage_name: str) -> Optional[LatencyReport]:
        """Generate latency report for a stage.

        Args:
            stage_name: Stage to analyze

        Returns:
            LatencyReport if data available
        """
        trace_id = f"latency_{stage_name}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "LatencyAnalyzer.generate_report"
        )

        latencies = self._stage_latencies.get(stage_name, [])

        if not latencies:
            return None

        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        p50 = self._percentile(sorted_latencies, 50)
        p95 = self._percentile(sorted_latencies, 95)
        p99 = self._percentile(sorted_latencies, 99)

        return LatencyReport(
            stage_name=stage_name,
            p50_ms=p50,
            p95_ms=p95,
            p99_ms=p99,
            mean_ms=statistics.mean(latencies),
            max_ms=max(latencies),
            min_ms=min(latencies),
            sample_count=n,
        )

    def generate_all_reports(self) -> Dict[str, LatencyReport]:
        """Generate reports for all stages.

        Returns:
            Dictionary mapping stage names to reports
        """
        reports = {}
        for stage_name in self._stage_latencies.keys():
            report = self.generate_report(stage_name)
            if report:
                reports[stage_name] = report
        return reports

    def get_bottlenecks(self, threshold_ms: float = 100.0) -> List[str]:
        """Identify bottleneck stages.

        Args:
            threshold_ms: P95 threshold for bottleneck detection

        Returns:
            List of bottleneck stage names
        """
        bottlenecks = []

        for stage_name in self._stage_latencies.keys():
            report = self.generate_report(stage_name)
            if report and report.p95_ms > threshold_ms:
                bottlenecks.append(stage_name)

        return bottlenecks

    def _percentile(self, sorted_data: List[float], p: float) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0

        k = (len(sorted_data) - 1) * (p / 100)
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f

        if f == c:
            return sorted_data[f]

        return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)


# Global instance
_global_analyzer: Optional[LatencyAnalyzer] = None


def get_latency_analyzer() -> LatencyAnalyzer:
    """Get or create the global latency analyzer."""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = LatencyAnalyzer()
    return _global_analyzer
