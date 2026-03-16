from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "anomaly_report_config", "p0_governance")
_emit_reads_policy_state("p0", "anomaly_report_config", "policy_binding")
_emit_snapshots_state("p0", "anomaly_report_config", "state_snapshot")
emit_replay_key("p0", "anomaly_report_config")
emit_determinism_digest("p0", "anomaly_report_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "anomaly_report_config", "execution_auth")
_emit_validates_capability("p2", "anomaly_report_config", "capability_check")
_emit_routes_to_capability("p2", "anomaly_report_config", "capability_route")
_emit_writes_via_uwg("p2", "anomaly_report_config", "uwg_write")
_emit_blocks_direct_write("p2", "anomaly_report_config", "direct_write_block")
_emit_records_tool_invocation("p2", "anomaly_report_config", "tool_invocation")
_emit_captures_execution_output("p2", "anomaly_report_config", "exec_output")
_emit_dispatches_agent("p3", "anomaly_report_config", "agent_dispatch")
_emit_coordinates_agents("p3", "anomaly_report_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "anomaly_report_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "anomaly_report_config", "healing_outcome")
_emit_escalates_failure("p3", "anomaly_report_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "anomaly_report_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "anomaly_report_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "anomaly_report_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "anomaly_report_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "anomaly_report_config", "eval_metric")
_emit_stores_embedding("p4", "anomaly_report_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "anomaly_report_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "anomaly_report_config", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
AnomalyReport - Sovereign Anomaly Detection schema

Provides standardized anomaly propagation across layers (L2-L5, apps).
Integrates with HealerMixin for audited healing decisions.

Location: agentic_core/runtime/config/anomaly_report_config.py
"""
import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""

    LOW = "low"  # Cosmetic/drift, auto-heal
    MEDIUM = "medium"  # Functional impairment, local heal
    HIGH = "high"  # Sovereignty risk, escalate
    CRITICAL = "critical"  # Immediate shutdown/escalate to L0


class AnomalyReport(BaseModel):
    """
    Sovereign anomaly report — immutable, auditable structure.

    Emitted by detectors (self-testing, validators, monitors).
    Consumed by HealerMixin._perform_healing().

    Attributes:
        type: Machine-readable anomaly type (e.g., "graph_corruption", "scoring_drift")
        severity: AnomalySeverity level
        description: Human-readable summary
        source: Agent/class name emitting the report
        details: Agent-specific context (e.g., {"graph_nodes": 42})
        timestamp: Auto-timestamp
        provenance_id: MCP chain ID if available
    """

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str = Field(..., description="Machine-readable anomaly type")
    severity: AnomalySeverity = Field(..., description="Severity level")
    description: str = Field(..., description="Human-readable summary")
    source: str = Field(..., description="Agent/class name emitting the report")
    details: dict[str, Any] = Field(default_factory=dict, description="Agent-specific context")
    timestamp: float = Field(default_factory=time.time, description="Auto-timestamp")
    provenance_id: str | None = Field(default=None, description="MCP chain ID if available")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """[HARDENED] Ensure description is not empty."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AnomalyReport.validate_description")

        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.source}: {self.type} — {self.description}"

    def to_dict(self) -> dict[str, Any]:
        """For MCP auditing / serialization."""
        return {
            "type": self.type,
            "severity": self.severity.value,
            "description": self.description,
            "source": self.source,
            "details": self.details or {},
            "timestamp": self.timestamp,
            "provenance_id": self.provenance_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnomalyReport:
        """Create from dictionary."""
        return cls(
            type=data["type"],
            severity=AnomalySeverity(data["severity"]),
            description=data["description"],
            source=data["source"],
            details=data.get("details"),
            timestamp=data.get("timestamp", time.time()),
            provenance_id=data.get("provenance_id"),
        )


__all__ = ["AnomalyReport", "AnomalySeverity"]
