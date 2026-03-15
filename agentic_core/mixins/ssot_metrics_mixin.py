"""
SSOT Metrics Mixin — Policy-Hash-Scoped Observability Metrics.

Provides metrics collection that:
  - Prefixes all bucket keys with active_policy_hash
  - Uses deterministic time provider under replay mode
  - Never alters control flow (L6 observer only)

Layer: L6 Observer
Authority: Read-only metrics emission. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_logger = logging.getLogger("SSOTMetrics")


class SSOTMetricsMixin:
    """Policy-hash-scoped metrics collection.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    All metric keys are prefixed with the policy hash to ensure isolation.
    Under replay mode, uses deterministic time (already patched by ReplayGuard).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_metrics: dict[str, list[dict[str, Any]]] = {}

    def record_metric(self, name: str, value: float, tags: dict[str, str] | None = None) -> dict[str, Any]:
        """Record a metric with policy-hash-scoped key.

        Parameters
        ----------
        name : str
            Metric name (e.g. "heal_duration_ms", "violations_found").
        value : float
            Metric value.
        tags : dict | None
            Optional tags for the metric.

        Returns
        -------
        dict
            The recorded metric entry.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTMetricsMixin.record_metric")

        policy_hash = getattr(self, "active_policy_hash", "unknown")
        scoped_key = f"{policy_hash}:{name}"
        entry = {
            "name": name,
            "scoped_key": scoped_key,
            "value": value,
            "timestamp": time.time(),
            "policy_hash": policy_hash,
            "tags": tags or {},
            "replay_mode": getattr(self, "is_replay_mode", False),
        }
        if scoped_key not in self._ssot_metrics:
            self._ssot_metrics[scoped_key] = []
        self._ssot_metrics[scoped_key].append(entry)
        _logger.debug("[SSOTMetrics] %s = %s", scoped_key, value)
        return entry

    def get_metrics(self, name: str | None = None) -> list[dict[str, Any]]:
        """Retrieve recorded metrics, optionally filtered by name.

        Parameters
        ----------
        name : str | None
            If provided, filter to metrics matching this name.

        Returns
        -------
        list[dict]
            Matching metric entries.
        """
        if name is None:
            return [e for entries in self._ssot_metrics.values() for e in entries]
        policy_hash = getattr(self, "active_policy_hash", "unknown")
        scoped_key = f"{policy_hash}:{name}"
        return list(self._ssot_metrics.get(scoped_key, []))

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self._ssot_metrics.clear()
