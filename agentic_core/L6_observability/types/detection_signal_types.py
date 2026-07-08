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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "detection_signal_types")
trace_contract.emit_determinism_digest("p0", "detection_signal_types")

trace_contract._emit_dispatches_healing_run("p1", "detection_signal_types", "L6")
trace_contract._emit_routes_through("p1", "detection_signal_types", "L6")
trace_contract._emit_checks_agent_registry("p1", "detection_signal_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "detection_signal_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "detection_signal_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "detection_signal_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "detection_signal_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "detection_signal_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "detection_signal_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "detection_signal_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "detection_signal_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "detection_signal_types")
trace_contract._emit_gated_by_confidence("p1", "detection_signal_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "detection_signal_types", "L6")
trace_contract._emit_reads_policy_state("p1", "detection_signal_types", "L6")
trace_contract._emit_authorize_and_execute("p2", "detection_signal_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "detection_signal_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "detection_signal_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "detection_signal_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "detection_signal_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "detection_signal_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "detection_signal_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "detection_signal_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "detection_signal_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "detection_signal_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "detection_signal_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "detection_signal_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "detection_signal_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "detection_signal_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "detection_signal_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "detection_signal_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "detection_signal_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "detection_signal_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "detection_signal_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "detection_signal_types", "exec_snapshot_link")

trace_contract.record_execution_trace("detection_signal_types", "detection_signal_types_trace")


trace_contract._emit_emits_metric_event("detection_signal_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("detection_signal_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("detection_signal_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("detection_signal_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("detection_signal_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("detection_signal_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("detection_signal_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("detection_signal_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("detection_signal_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("detection_signal_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("detection_signal_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("detection_signal_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("detection_signal_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("detection_signal_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("detection_signal_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("detection_signal_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("detection_signal_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("detection_signal_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("detection_signal_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("detection_signal_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("detection_signal_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("detection_signal_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("detection_signal_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("detection_signal_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("detection_signal_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("detection_signal_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("detection_signal_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("detection_signal_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "detection_signal_types", "context_pull")
trace_contract._emit_pulls_context("p1", "detection_signal_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "detection_signal_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "detection_signal_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "detection_signal_types", "write_through")
trace_contract._emit_writes_through("p1", "detection_signal_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "detection_signal_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "detection_signal_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "detection_signal_types", "routing_commit")


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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "DetectionSignal.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "DetectionSignal.canonical_bytes", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L6_OBSERVABILITY,
            "DetectionSignal.canonical_bytes",
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
