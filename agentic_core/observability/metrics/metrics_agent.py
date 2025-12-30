"""
MetricsAgent: Sovereign Observability Metrics Collector

Centralized metric collection for compliance and system health.
Supports:
- Counters (monotonically increasing)
- Gauges (settable values)
- Labeled counters (e.g., violations by type)
- Basic metadata storage

Designed for integration with:
- ComplianceOrchestrator (increment violations)
- ReportingAgent (read current state)

Placed in observability/metrics per SSOT semantic registry:
  "Metric collection, counters, gauges, and prometheus exports"

Depth: agentic_core/observability/metrics/metrics_agent.py
      → root/L1/L2/file.py → exactly 4 parts → Canon Key 3/12 compliant

In-memory only (no persistence) — suitable for runtime missions.
Future: extend with Prometheus exposition or file export.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class metrics_agent:
    """
    Autonomous metrics collection agent.
    Thread-safe, in-memory metric store.
    Sovereign-compliant: no external dependencies.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize metric store.
        project_root optional — for future context-aware metrics.
        """
        self.project_root = project_root.resolve() if project_root else None
        self._lock = Lock()

        # Storage
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._labeled_counters: Dict[str, Dict[str, int]] = {}  # name → labels → count
        self._metadata: Dict[str, Any] = {}

        # Initialize compliance metrics
        self._initialize_compliance_metrics()

    def _initialize_compliance_metrics(self) -> None:
        """Pre-define known compliance metrics with zero values."""
        with self._lock:
            # Total violations across all scans
            self._counters["compliance.total_violations"] = 0

            # Labeled: violation types
            self._labeled_counters["compliance.violations_by_type"] = {
                "location": 0,
                "hierarchy": 0,
                "naming": 0,
                "import": 0,
                "gravity": 0,
                "other": 0,
            }

            # Compliance rate gauge (0-100)
            self._gauges["compliance.compliance_rate"] = 100.0

            # Metadata
            self._metadata["compliance.last_scan"] = None
            self._metadata["compliance.scan_count"] = 0

    # === Counter Operations ===

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter."""
        if value < 0:
            raise ValueError("Counter increment must be non-negative")
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def get_counter(self, name: str) -> int:
        """Get current counter value."""
        with self._lock:
            return self._counters.get(name, 0)

    # === Labeled Counter Operations ===

    def increment_labeled(self, name: str, label: str, value: int = 1) -> None:
        """Increment a labeled counter."""
        if value < 0:
            raise ValueError("Increment must be non-negative")
        with self._lock:
            labels = self._labeled_counters.setdefault(name, {})
            labels[label] = labels.get(label, 0) + value

    def get_labeled_counter(self, name: str) -> Dict[str, int]:
        """Get all labels and values for a labeled counter."""
        with self._lock:
            return self._labeled_counters.get(name, {}).copy()

    # === Gauge Operations ===

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge value."""
        with self._lock:
            self._gauges[name] = float(value)

    def get_gauge(self, name: str) -> float:
        """Get current gauge value."""
        with self._lock:
            return self._gauges.get(name, 0.0)

    # === Metadata ===

    def set_metadata(self, key: str, value: Any) -> None:
        """Store arbitrary metadata."""
        with self._lock:
            self._metadata[key] = value

    def get_metadata(self, key: str) -> Any:
        """Retrieve metadata."""
        with self._lock:
            return self._metadata.get(key)

    # === Compliance-Specific Helpers ===

    def record_compliance_scan(self, violations: list) -> None:
        """
        Record results of a compliance scan.
        Called by ComplianceOrchestrator.
        """
        total = len(violations)
        timestamp = datetime.now().isoformat()

        with self._lock:
            # Reset per-type counts
            type_counts = {
                "location": 0,
                "hierarchy": 0,
                "naming": 0,
                "import": 0,
                "gravity": 0,
                "other": 0,
            }

            for _, msg in violations:
                msg_lower = msg.lower()
                if "location" in msg_lower or "void" in msg_lower:
                    type_counts["location"] += 1
                elif "hierarchy" in msg_lower or "span" in msg_lower or "depth" in msg_lower:
                    type_counts["hierarchy"] += 1
                elif "naming" in msg_lower or "signal" in msg_lower:
                    type_counts["naming"] += 1
                elif "import" in msg_lower or "gravity" in msg_lower:
                    if "gravity" in msg_lower:
                        type_counts["gravity"] += 1
                    else:
                        type_counts["import"] += 1
                else:
                    type_counts["other"] += 1

            # Update counters
            self._counters["compliance.total_violations"] = total
            self._labeled_counters["compliance.violations_by_type"] = type_counts

            # Update gauge (assume total files scanned elsewhere or approximate)
            compliance_rate = 0.0 if total > 0 else 100.0
            self._gauges["compliance.compliance_rate"] = compliance_rate

            # Metadata
            self._metadata["compliance.last_scan"] = timestamp
            self._metadata["compliance.scan_count"] = self._metadata.get("compliance.scan_count", 0) + 1

        logger.info(f"[MetricsAgent] Recorded compliance scan: {total} violations")

    def get_all_metrics(self) -> Dict[str, Any]:
        """Export full metric snapshot (for debugging or export)."""
        with self._lock:
            return {
                "counters": self._counters.copy(),
                "gauges": self._gauges.copy(),
                "labeled_counters": {k: v.copy() for k, v in self._labeled_counters.items()},
                "metadata": self._metadata.copy(),
            }


# Uppercase alias for backward compatibility
MetricsAgent = metrics_agent
