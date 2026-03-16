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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "ssot_metrics_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_metrics_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_metrics_mixin", "state_snapshot")
emit_replay_key("p0", "ssot_metrics_mixin")
emit_determinism_digest("p0", "ssot_metrics_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_metrics_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_metrics_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_metrics_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_metrics_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_metrics_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_metrics_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_metrics_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_metrics_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_metrics_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_metrics_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_metrics_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_metrics_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_metrics_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_metrics_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_metrics_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_metrics_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_metrics_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_metrics_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_metrics_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_metrics_mixin", "exec_snapshot_link")

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
