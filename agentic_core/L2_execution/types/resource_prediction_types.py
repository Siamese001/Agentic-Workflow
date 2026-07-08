"""
Resource prediction types for L2 execution learning.
Deterministic, frozen dataclasses with canonical serialization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "resource_prediction_types")
trace_contract.emit_determinism_digest("p0", "resource_prediction_types")

trace_contract._emit_dispatches_healing_run("p1", "resource_prediction_types", "L2")
trace_contract._emit_routes_through("p1", "resource_prediction_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "resource_prediction_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "resource_prediction_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "resource_prediction_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "resource_prediction_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "resource_prediction_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "resource_prediction_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "resource_prediction_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "resource_prediction_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "resource_prediction_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "resource_prediction_types")
trace_contract._emit_gated_by_confidence("p1", "resource_prediction_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "resource_prediction_types", "L2")
trace_contract._emit_reads_policy_state("p1", "resource_prediction_types", "L2")

trace_contract._emit_applies_guardrail("p0", "resource_prediction_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "resource_prediction_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "resource_prediction_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "resource_prediction_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "resource_prediction_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "resource_prediction_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "resource_prediction_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "resource_prediction_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "resource_prediction_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "resource_prediction_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "resource_prediction_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "resource_prediction_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "resource_prediction_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "resource_prediction_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "resource_prediction_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "resource_prediction_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "resource_prediction_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "resource_prediction_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "resource_prediction_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "resource_prediction_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "resource_prediction_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "resource_prediction_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("resource_prediction_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("resource_prediction_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("resource_prediction_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("resource_prediction_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("resource_prediction_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("resource_prediction_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("resource_prediction_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("resource_prediction_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("resource_prediction_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("resource_prediction_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("resource_prediction_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("resource_prediction_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("resource_prediction_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("resource_prediction_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("resource_prediction_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("resource_prediction_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("resource_prediction_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("resource_prediction_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("resource_prediction_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("resource_prediction_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("resource_prediction_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("resource_prediction_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "resource_prediction_types", "context_pull")
trace_contract._emit_pulls_context("p1", "resource_prediction_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "resource_prediction_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "resource_prediction_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "resource_prediction_types", "write_through")
trace_contract._emit_writes_through("p1", "resource_prediction_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "resource_prediction_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "resource_prediction_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "resource_prediction_types", "routing_commit")


@dataclass(frozen=True)
class FailureSignature:
    """Deterministic signature of a failure for resource prediction."""

    component: str
    failure_type: str
    fingerprint: str

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "FailureSignature.canonical_bytes",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FailureSignature.canonical_bytes".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "component": self.component,
            "failure_type": self.failure_type,
            "fingerprint": self.fingerprint,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class ResourceEnvelope:
    """Bounded resource envelope for execution."""

    cpu_cores: int
    memory_mb: int
    timeout_s: int

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "ResourceEnvelope.canonical_bytes",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ResourceEnvelope.canonical_bytes".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {"cpu_cores": self.cpu_cores, "memory_mb": self.memory_mb, "timeout_s": self.timeout_s}
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class ResourcePrediction:
    """Deterministic resource prediction for a failure signature."""

    signature: FailureSignature
    envelope: ResourceEnvelope
    confidence: float
    reasons: tuple[str, ...]

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "ResourcePrediction.canonical_bytes",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ResourcePrediction.canonical_bytes".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "signature": self.signature.canonical_bytes().decode("ascii"),
            "envelope": self.envelope.canonical_bytes().decode("ascii"),
            "confidence": round(self.confidence, 6),
            "reasons": tuple(sorted(self.reasons)),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
