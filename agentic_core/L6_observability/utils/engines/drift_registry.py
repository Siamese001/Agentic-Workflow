"""DriftRegistry — unified timeline for all drift signal sources.

Aggregates entries from RetrievalDriftMonitor, EmbeddingDriftMonitor,
ShadowDriftAnalyzer, and DriftDetector into a single queryable, append-only
L4 timeline.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402
    record_execution_trace,
)

record_execution_trace("drift_registry", "drift_registry_trace")


_emit_records_execution_trace("p0", "evidence", "drift_registry")
_logger = logging.getLogger(__name__)
_TIMELINE_PATH = Path("agentic_core/L4_state/stores/drift_timeline.jsonl")
DriftSource = Literal["retrieval", "embedding", "shadow", "c0_context"]
DriftSeverity = Literal["info", "warning", "critical"]


@dataclass(frozen=True)
class DriftRegistryEntry:
    """Immutable record of a single drift measurement."""

    source: DriftSource
    timestamp_iso: str
    metric_name: str
    current_value: float
    threshold_value: float
    drift_flag: bool
    severity: DriftSeverity
    deterministic_digest: str

    @classmethod
    def create(
        cls,
        source: DriftSource,
        timestamp_iso: str,
        metric_name: str,
        current_value: float,
        threshold_value: float,
        drift_flag: bool,
        severity: DriftSeverity,
    ) -> DriftRegistryEntry:
        canonical = json.dumps(
            {
                "source": source,
                "timestamp_iso": timestamp_iso,
                "metric_name": metric_name,
                "current_value": round(current_value, 8),
                "threshold_value": round(threshold_value, 8),
                "drift_flag": drift_flag,
                "severity": severity,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(
            source=source,
            timestamp_iso=timestamp_iso,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            drift_flag=drift_flag,
            severity=severity,
            deterministic_digest=digest,
        )

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "timestamp_iso": self.timestamp_iso,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "drift_flag": self.drift_flag,
            "severity": self.severity,
            "deterministic_digest": self.deterministic_digest,
        }


class DriftRegistry:
    """Unified in-memory + append-only file timeline for all drift signals.

    Thread-safety: not thread-safe; designed for single-process use.
    """

    def __init__(self, timeline_path: Path | None = None) -> None:
        self._timeline_path = timeline_path or _TIMELINE_PATH
        self._entries: list[DriftRegistryEntry] = []
        self._lock = threading.RLock()

    def record(self, entry: DriftRegistryEntry) -> None:
        """Append a drift entry to the in-memory list and persist to JSONL."""
        with self._lock:
            self._entries.append(entry)
            self._persist(entry)
        if entry.severity == "critical":
            _logger.warning(
                "DriftRegistry: critical drift detected",
                extra={
                    "source": entry.source,
                    "metric": entry.metric_name,
                    "value": entry.current_value,
                    "threshold": entry.threshold_value,
                },
            )

    def query(
        self,
        since_iso: str | None = None,
        source_filter: DriftSource | None = None,
    ) -> list[DriftRegistryEntry]:
        """Return entries matching the given filters, oldest first."""
        with self._lock:
            results = list(self._entries)
        if since_iso is not None:
            results = [e for e in results if e.timestamp_iso >= since_iso]
        if source_filter is not None:
            results = [e for e in results if e.source == source_filter]
        return results

    def all_entries(self) -> list[DriftRegistryEntry]:
        """Return all recorded entries, oldest first."""
        with self._lock:
            return list(self._entries)

    def _persist(self, entry: DriftRegistryEntry) -> None:
        try:
            self._timeline_path.parent.mkdir(parents=True, exist_ok=True)
            with self._timeline_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry.to_dict(), separators=(",", ":")) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
        except (OSError, TypeError, ValueError):
            _logger.warning("DriftRegistry: failed to persist entry", exc_info=True)


_registry: DriftRegistry | None = None


def get_drift_registry() -> DriftRegistry:
    """Return the module-level singleton DriftRegistry."""
    global _registry
    if _registry is None:
        _registry = DriftRegistry()
    return _registry


__all__ = ["DriftRegistryEntry", "DriftRegistry", "DriftSource", "DriftSeverity", "get_drift_registry"]
