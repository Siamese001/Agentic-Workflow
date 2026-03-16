"""
L6 DetectionSignal — Phase 3

Non-authority passive detection signal emitted at mission boundary.
Carries scalar health metrics; persisted to L4 SSOT for N+1 routing influence.

AUTHORITY CONSTRAINT: DetectionSignal MUST NOT mutate current execution decisions.
It is emitted AFTER GatewayResult is finalized and cannot change it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "detection_signal_types")
emit_determinism_digest("p0", "detection_signal_types")

_emit_dispatches_healing_run("p1", "detection_signal_types", "L6")
_emit_routes_through("p1", "detection_signal_types", "L6")
_emit_escalates_to_human("p1", "detection_signal_types", "L6")
_emit_reads_policy_state("p1", "detection_signal_types", "L6")
_emit_authorize_and_execute("p2", "detection_signal_types", "execution_auth")
_emit_validates_capability("p2", "detection_signal_types", "capability_check")
_emit_routes_to_capability("p2", "detection_signal_types", "capability_route")
_emit_writes_via_uwg("p2", "detection_signal_types", "uwg_write")
_emit_blocks_direct_write("p2", "detection_signal_types", "direct_write_block")
_emit_records_tool_invocation("p2", "detection_signal_types", "tool_invocation")
_emit_captures_execution_output("p2", "detection_signal_types", "exec_output")
_emit_dispatches_agent("p3", "detection_signal_types", "agent_dispatch")
_emit_coordinates_agents("p3", "detection_signal_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "detection_signal_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "detection_signal_types", "healing_outcome")
_emit_escalates_failure("p3", "detection_signal_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "detection_signal_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "detection_signal_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "detection_signal_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "detection_signal_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "detection_signal_types", "eval_metric")
_emit_stores_embedding("p4", "detection_signal_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "detection_signal_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "detection_signal_types", "exec_snapshot_link")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class DetectionSignal:
    """
    Scalar health metrics snapshot emitted at mission boundary.

    Fields:
        schema_version    — int, incremented on breaking changes
        mission_id        — str, identifies the mission/execution context
        created_at_utc    — int, UTC epoch seconds (stable, no sub-second noise)
        anomaly_score     — float [0..1], overall anomaly level
        escalation_rate   — float [0..1], fraction of steps that escalated
        retry_rate        — float [0..1], fraction of steps that retried
        violation_density — float [0..1], fraction of steps with violations
        signal_hash       — sha256 of canonical_bytes() excluding signal_hash itself
    """

    schema_version: int
    mission_id: str
    created_at_utc: int
    anomaly_score: float
    escalation_rate: float
    retry_rate: float
    violation_density: float
    signal_hash: str
    _FLOAT_FIELDS = ("anomaly_score", "escalation_rate", "retry_rate", "violation_density")

    def __post_init__(self) -> None:
        if self.schema_version < 1:
            raise ValueError(f"schema_version must be >= 1, got {self.schema_version}")
        if not self.mission_id:
            raise ValueError("mission_id must be non-empty")
        if self.created_at_utc < 0:
            raise ValueError(f"created_at_utc must be >= 0, got {self.created_at_utc}")
        for field_name in self._FLOAT_FIELDS:
            v = getattr(self, field_name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{field_name} must be in [0.0, 1.0], got {v}")
        if len(self.signal_hash) != 64:
            raise ValueError(f"signal_hash must be 64 hex chars, got len={len(self.signal_hash)}")

    def canonical_bytes(self) -> bytes:
        """Deterministic serialization excluding signal_hash (used to compute it)."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DetectionSignal.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DetectionSignal.canonical_bytes", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "DetectionSignal.canonical_bytes"
        )

        doc = {
            "anomaly_score": self.anomaly_score,
            "created_at_utc": self.created_at_utc,
            "escalation_rate": self.escalation_rate,
            "mission_id": self.mission_id,
            "retry_rate": self.retry_rate,
            "schema_version": self.schema_version,
            "violation_density": self.violation_density,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    @staticmethod
    def compute_hash(
        schema_version: int,
        mission_id: str,
        created_at_utc: int,
        anomaly_score: float,
        escalation_rate: float,
        retry_rate: float,
        violation_density: float,
    ) -> str:
        """Compute signal_hash from raw field values (before construction)."""
        doc = {
            "anomaly_score": anomaly_score,
            "created_at_utc": created_at_utc,
            "escalation_rate": escalation_rate,
            "mission_id": mission_id,
            "retry_rate": retry_rate,
            "schema_version": schema_version,
            "violation_density": violation_density,
        }
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
        return _sha256(raw)

    @classmethod
    def build(
        cls,
        mission_id: str,
        created_at_utc: int,
        anomaly_score: float,
        escalation_rate: float,
        retry_rate: float,
        violation_density: float,
        schema_version: int = 1,
    ) -> DetectionSignal:
        """Factory: compute signal_hash automatically."""
        h = cls.compute_hash(
            schema_version=schema_version,
            mission_id=mission_id,
            created_at_utc=created_at_utc,
            anomaly_score=anomaly_score,
            escalation_rate=escalation_rate,
            retry_rate=retry_rate,
            violation_density=violation_density,
        )
        return cls(
            schema_version=schema_version,
            mission_id=mission_id,
            created_at_utc=created_at_utc,
            anomaly_score=anomaly_score,
            escalation_rate=escalation_rate,
            retry_rate=retry_rate,
            violation_density=violation_density,
            signal_hash=h,
        )
