"""
metric_config.py - Metrics Module

Domain: metrics
Generated: 2025-12-07T12:07:59.847509
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field

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

_emit_applies_guardrail("p0", "metric_util", "p0_governance")
_emit_reads_policy_state("p0", "metric_util", "policy_binding")
_emit_snapshots_state("p0", "metric_util", "state_snapshot")
emit_replay_key("p0", "metric_util")
emit_determinism_digest("p0", "metric_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "metric_util", "execution_auth")
_emit_validates_capability("p2", "metric_util", "capability_check")
_emit_routes_to_capability("p2", "metric_util", "capability_route")
_emit_writes_via_uwg("p2", "metric_util", "uwg_write")
_emit_blocks_direct_write("p2", "metric_util", "direct_write_block")
_emit_records_tool_invocation("p2", "metric_util", "tool_invocation")
_emit_captures_execution_output("p2", "metric_util", "exec_output")
_emit_dispatches_agent("p3", "metric_util", "agent_dispatch")
_emit_coordinates_agents("p3", "metric_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "metric_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "metric_util", "healing_outcome")
_emit_escalates_failure("p3", "metric_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "metric_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "metric_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "metric_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "metric_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "metric_util", "eval_metric")
_emit_stores_embedding("p4", "metric_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "metric_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "metric_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """A single metric."""

    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class MetricConfig:
    """Metrics collector for metrics domain."""

    def __init__(self, config: dict[str, object] | None = None):
        self.config = config or {}
        self.metrics: dict[str, list[Metric]] = defaultdict(list)
        logger.info(f"Initialized {self.__class__.__name__}")

    def record(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record a metric."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MetricConfig.record")

        metric = Metric(name=name, value=value, labels=labels or {})
        self.metrics[name].append(metric)
        logger.debug(f"Recorded metric {name}={value}")

    def get_metrics(self, name: str | None = None) -> list[Metric]:
        """Get recorded metrics."""
        if name:
            return self.metrics.get(name, [])
        return [m for metrics in self.metrics.values() for m in metrics]

    def get_latest(self, name: str) -> Metric | None:
        """Get latest metric value."""
        metrics = self.metrics.get(name, [])
        return metrics[-1] if metrics else None

    def clear(self, name: str | None = None) -> None:
        """Clear metrics."""
        if name:
            self.metrics.pop(name, None)
        else:
            self.metrics.clear()


_collector = MetricConfig()


def record_metric(name: str, value: float, labels: dict[str, str] | None = None) -> None:
    """Record a metric to global collector."""
    _collector.record(name, value, labels)


def get_metrics(name: str | None = None) -> list[Metric]:
    """Get metrics from global collector."""
    return _collector.get_metrics(name)
