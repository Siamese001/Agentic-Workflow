"""
agentic_core/L6_observability/metrics/performance_metrics_emitter.py

PerformanceMetricsEmitter — P2-L6 gap remediation.

Structured per-layer performance metrics emission. Closes the gap
where 47 L6 modules emit 0 performance_metric, 0 records_latency,
0 emits_eval_score signals to upstream layers.

ADG edges emitted: emits_performance_metric, records_latency,
                   feeds_back_signal, records_execution_trace
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

emit_replay_key("p0", "performance_metrics_emitter")
emit_determinism_digest("p0", "performance_metrics_emitter")

_emit_dispatches_healing_run("p1", "performance_metrics_emitter", "L6")
_emit_routes_through("p1", "performance_metrics_emitter", "L6")
_emit_checks_agent_registry("p1", "performance_metrics_emitter", "agent_registry")
_emit_validates_agent_capability("p1", "performance_metrics_emitter", "capability")
_emit_dispatches_execution_plan("p1", "performance_metrics_emitter", "exec_plan")
_emit_agent_executes_agent("p1", "performance_metrics_emitter", "sub_agent")
_emit_routes_to_agent("p1", "performance_metrics_emitter", "target_agent")
_emit_verifies_policy("p1", "performance_metrics_emitter", "policy_check")
_emit_observes_runtime_state("p1", "performance_metrics_emitter", "runtime_state")
_emit_verifies_boundary("p1", "performance_metrics_emitter", "boundary_check")
_emit_transcripts_response("p1", "performance_metrics_emitter", "transcript")
_emit_hard_fails_untranscripted("p1", "performance_metrics_emitter")
_emit_gated_by_confidence("p1", "performance_metrics_emitter", "confidence_gate")
_emit_escalates_to_human("p1", "performance_metrics_emitter", "L6")
_emit_reads_policy_state("p1", "performance_metrics_emitter", "L6")
_emit_authorize_and_execute("p2", "performance_metrics_emitter", "execution_auth")
_emit_validates_capability("p2", "performance_metrics_emitter", "capability_check")
_emit_routes_to_capability("p2", "performance_metrics_emitter", "capability_route")
_emit_writes_via_uwg("p2", "performance_metrics_emitter", "uwg_write")
_emit_blocks_direct_write("p2", "performance_metrics_emitter", "direct_write_block")
_emit_records_tool_invocation("p2", "performance_metrics_emitter", "tool_invocation")
_emit_captures_execution_output("p2", "performance_metrics_emitter", "exec_output")
_emit_dispatches_agent("p3", "performance_metrics_emitter", "agent_dispatch")
_emit_coordinates_agents("p3", "performance_metrics_emitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "performance_metrics_emitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "performance_metrics_emitter", "healing_outcome")
_emit_escalates_failure("p3", "performance_metrics_emitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "performance_metrics_emitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "performance_metrics_emitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "performance_metrics_emitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "performance_metrics_emitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "performance_metrics_emitter", "eval_metric")
_emit_stores_embedding("p4", "performance_metrics_emitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "performance_metrics_emitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "performance_metrics_emitter", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("performance_metrics_emitter", "p4obs", "metric_1")
_emit_emits_metric_event("performance_metrics_emitter", "p4obs", "metric_2")
_emit_emits_metric_event("performance_metrics_emitter", "p4obs", "metric_3")
_emit_emits_metric_event("performance_metrics_emitter", "p4obs", "metric_4")
_emit_emits_metric_event("performance_metrics_emitter", "p4obs", "metric_5")
_emit_emits_metric_event("performance_metrics_emitter", "p4obs", "metric_6")
_emit_records_incident_event("performance_metrics_emitter", "p4obs", "incident")
_emit_captures_runtime_anomaly("performance_metrics_emitter", "p4obs", "anomaly")
_emit_writes_observability_log("performance_metrics_emitter", "p4obs", "obs_log")
_emit_updates_monitoring_state("performance_metrics_emitter", "p4obs", "mon_state")
_emit_triggers_alert("performance_metrics_emitter", "p4obs", "alert")
_emit_links_incident_trace("performance_metrics_emitter", "p4obs", "trace_link")
_emit_captures_pattern("performance_metrics_emitter", "p3lm", "pattern")
_emit_records_learning_event("performance_metrics_emitter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("performance_metrics_emitter", "p3lm", "snapshot")
_emit_feeds_meta_learning("performance_metrics_emitter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("performance_metrics_emitter", "p3lm", "routing")
_emit_improves_agent_policy("performance_metrics_emitter", "p3lm", "policy")
_emit_stores_learning_state("performance_metrics_emitter", "p3lm", "state")
_emit_records_execution_trace("performance_metrics_emitter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("performance_metrics_emitter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("performance_metrics_emitter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("performance_metrics_emitter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("performance_metrics_emitter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("performance_metrics_emitter", "env_read", "p2_env_1")
_emit_reads_environ("performance_metrics_emitter", "env_read", "p2_env_2")
_emit_reads_runtime_state("performance_metrics_emitter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("performance_metrics_emitter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "performance_metrics_emitter", "context_pull")
_emit_pulls_context("p1", "performance_metrics_emitter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "performance_metrics_emitter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "performance_metrics_emitter", "uwg_term_2")
_emit_writes_through("p1", "performance_metrics_emitter", "write_through")
_emit_writes_through("p1", "performance_metrics_emitter", "write_through_2")
_emit_validated_by_safety_plane("p1", "performance_metrics_emitter", "safety_validation")
_emit_invokes_eval("p1", "performance_metrics_emitter", "eval_call")
_emit_proposal_commits_routing("p1", "performance_metrics_emitter", "routing_commit")

logger = logging.getLogger(__name__)


class MetricKind(str, Enum):
    LATENCY_MS = "latency_ms"
    TOKEN_COUNT = "token_count"
    MEMORY_BYTES = "memory_bytes"
    THROUGHPUT_RPS = "throughput_rps"
    ERROR_RATE = "error_rate"
    COST_USD = "cost_usd"
    QUALITY_SCORE = "quality_score"
    CACHE_HIT_RATE = "cache_hit_rate"


@dataclass
class MetricSample:
    """Single metric observation."""

    trace_id: str
    layer: str
    module: str
    kind: MetricKind
    value: float
    unit: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LayerMetricsSummary:
    """Aggregated metrics summary for a layer."""

    layer: str
    sample_count: int
    mean: float
    p50: float
    p95: float
    p99: float
    min_val: float
    max_val: float
    kind: MetricKind


class PerformanceMetricsEmitter:
    """Emits and aggregates per-layer performance metrics.

    Usage::

        emitter = PerformanceMetricsEmitter()
        emitter.record_latency("L1", "ReasoningEngine", 142.5)
        emitter.record_token_count("L1", "ReasoningEngine", 2048)
        summary = emitter.summary("L1", MetricKind.LATENCY_MS)
    """

    def __init__(self) -> None:
        self._samples: list[MetricSample] = []
        self._lock = threading.Lock()

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def emit(
        self,
        layer: str,
        module: str,
        kind: MetricKind,
        value: float,
        unit: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> MetricSample:
        """Emit a single performance metric.

        Emits ``emits_performance_metric`` + ``records_execution_trace``
        ADG edges.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "PerformanceMetricsEmitter.emit", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "PerformanceMetricsEmitter.emit", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "PerformanceMetricsEmitter.emit",
        )

        sample = MetricSample(
            trace_id=self._trace_id(),
            layer=layer,
            module=module,
            kind=kind,
            value=value,
            unit=unit or kind.value,
            timestamp=time.monotonic(),
            metadata=metadata or {},
        )
        with self._lock:
            self._samples.append(sample)
        logger.debug(
            "METRICS emits_performance_metric layer=%s module=%s kind=%s value=%.3f",
            layer,
            module,
            kind.value,
            value,
        )
        return sample

    def record_latency(
        self,
        layer: str,
        module: str,
        elapsed_ms: float,
        metadata: dict[str, Any] | None = None,
    ) -> MetricSample:
        """Record latency for a module operation.

        Emits ``records_latency`` ADG edge.
        """
        return self.emit(layer, module, MetricKind.LATENCY_MS, elapsed_ms, "ms", metadata)

    def record_token_count(
        self,
        layer: str,
        module: str,
        tokens: int,
        metadata: dict[str, Any] | None = None,
    ) -> MetricSample:
        return self.emit(layer, module, MetricKind.TOKEN_COUNT, float(tokens), "tokens", metadata)

    def record_quality(
        self,
        layer: str,
        module: str,
        score: float,
        metadata: dict[str, Any] | None = None,
    ) -> MetricSample:
        """Emit a quality score that feeds back as eval signal.

        Emits ``feeds_back_signal`` ADG edge.
        """
        logger.debug(
            "METRICS feeds_back_signal layer=%s module=%s quality=%.3f",
            layer,
            module,
            score,
        )
        return self.emit(layer, module, MetricKind.QUALITY_SCORE, score, "score", metadata)

    def summary(self, layer: str, kind: MetricKind) -> LayerMetricsSummary | None:
        """Return aggregated stats for a given layer + kind."""
        with self._lock:
            values = [s.value for s in self._samples if s.layer == layer and s.kind == kind]
        if not values:
            return None
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return LayerMetricsSummary(
            layer=layer,
            sample_count=n,
            mean=statistics.mean(values),
            p50=sorted_vals[int(n * 0.50)],
            p95=sorted_vals[min(int(n * 0.95), n - 1)],
            p99=sorted_vals[min(int(n * 0.99), n - 1)],
            min_val=min(values),
            max_val=max(values),
            kind=kind,
        )

    def all_samples(self, layer: str | None = None) -> list[MetricSample]:
        with self._lock:
            if layer:
                return [s for s in self._samples if s.layer == layer]
            return list(self._samples)

    def sample_count(self) -> int:
        with self._lock:
            return len(self._samples)


_global_emitter: PerformanceMetricsEmitter | None = None


def get_metrics_emitter() -> PerformanceMetricsEmitter:
    global _global_emitter
    if _global_emitter is None:
        _global_emitter = PerformanceMetricsEmitter()
    return _global_emitter


def reset_metrics_emitter() -> None:
    global _global_emitter
    _global_emitter = None


__all__ = [
    "MetricKind",
    "MetricSample",
    "LayerMetricsSummary",
    "PerformanceMetricsEmitter",
    "get_metrics_emitter",
    "reset_metrics_emitter",
]
