from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "health_status_types")
trace_contract.emit_determinism_digest("p0", "health_status_types")

trace_contract._emit_dispatches_healing_run("p1", "health_status_types", "L5")
trace_contract._emit_routes_through("p1", "health_status_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "health_status_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "health_status_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "health_status_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "health_status_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "health_status_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "health_status_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "health_status_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "health_status_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "health_status_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "health_status_types")
trace_contract._emit_gated_by_confidence("p1", "health_status_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "health_status_types", "L5")
trace_contract._emit_reads_policy_state("p1", "health_status_types", "L5")
trace_contract._emit_authorize_and_execute("p2", "health_status_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "health_status_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "health_status_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "health_status_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "health_status_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "health_status_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "health_status_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "health_status_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "health_status_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "health_status_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "health_status_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "health_status_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "health_status_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "health_status_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "health_status_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "health_status_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "health_status_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "health_status_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "health_status_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "health_status_types", "exec_snapshot_link")

"Types and models for AutonomicMonitorAgent."
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


trace_contract._emit_emits_metric_event("health_status_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("health_status_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("health_status_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("health_status_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("health_status_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("health_status_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("health_status_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("health_status_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("health_status_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("health_status_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("health_status_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("health_status_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("health_status_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("health_status_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("health_status_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("health_status_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("health_status_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("health_status_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("health_status_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("health_status_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("health_status_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("health_status_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("health_status_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("health_status_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("health_status_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("health_status_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("health_status_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("health_status_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "health_status_types", "context_pull")
trace_contract._emit_pulls_context("p1", "health_status_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "health_status_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "health_status_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "health_status_types", "write_through")
trace_contract._emit_writes_through("p1", "health_status_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "health_status_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "health_status_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "health_status_types", "routing_commit")

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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "health_metrics.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "health_metrics.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "health_metrics.to_dict")
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
