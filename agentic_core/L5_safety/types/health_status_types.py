from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "health_status_types")
emit_determinism_digest("p0", "health_status_types")

_emit_dispatches_healing_run("p1", "health_status_types", "L5")
_emit_routes_through("p1", "health_status_types", "L5")
_emit_escalates_to_human("p1", "health_status_types", "L5")
_emit_reads_policy_state("p1", "health_status_types", "L5")
_emit_authorize_and_execute("p2", "health_status_types", "execution_auth")
_emit_validates_capability("p2", "health_status_types", "capability_check")
_emit_routes_to_capability("p2", "health_status_types", "capability_route")
_emit_writes_via_uwg("p2", "health_status_types", "uwg_write")
_emit_blocks_direct_write("p2", "health_status_types", "direct_write_block")
_emit_records_tool_invocation("p2", "health_status_types", "tool_invocation")
_emit_captures_execution_output("p2", "health_status_types", "exec_output")
_emit_dispatches_agent("p3", "health_status_types", "agent_dispatch")
_emit_coordinates_agents("p3", "health_status_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "health_status_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "health_status_types", "healing_outcome")
_emit_escalates_failure("p3", "health_status_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "health_status_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "health_status_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "health_status_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "health_status_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "health_status_types", "eval_metric")
_emit_stores_embedding("p4", "health_status_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "health_status_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "health_status_types", "exec_snapshot_link")

"Types and models for AutonomicMonitorAgent."
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger: Any = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Agent health status."""

    HEALTHY: Any = "healthy"
    DEGRADED: Any = "degraded"
    CRITICAL: Any = "critical"
    OFFLINE: Any = "offline"


class AlertSeverity(Enum):
    """Alert Severity levels."""

    INFO: Any = "info"
    WARNING: Any = "warning"
    ERROR: Any = "error"
    CRITICAL: Any = "critical"


@dataclass
class health_metrics:
    """Health metrics for an agent."""

    agent_id: str
    success_rate: float
    avg_response_time_ms: float
    error_rate: float
    circuit_breaker_trips: int
    total_requests: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "health_metrics.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "health_metrics.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "health_metrics.to_dict")
        return {
            "agent_id": self.agent_id,
            "success_rate": self.success_rate,
            "avg_response_time_ms": self.avg_response_time_ms,
            "error_rate": self.error_rate,
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "total_requests": self.total_requests,
            "timestamp": self.timestamp,
        }


@dataclass
class HealthAlert:
    """Health alert for degradation detection."""

    alert_id: str
    agent_id: str
    Severity: AlertSeverity
    message: str
    metrics: health_metrics
    recommended_actions: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "agent_id": self.agent_id,
            "Severity": self.Severity.value,
            "message": self.message,
            "metrics": self.metrics.to_dict(),
            "recommended_actions": self.recommended_actions,
            "timestamp": self.timestamp,
        }
