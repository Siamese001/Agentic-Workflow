"""
Resource prediction types for L2 execution learning.
Deterministic, frozen dataclasses with canonical serialization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_snapshots_state,  # noqa: E402
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

emit_replay_key("p0", "resource_prediction_types")
emit_determinism_digest("p0", "resource_prediction_types")

_emit_dispatches_healing_run("p1", "resource_prediction_types", "L2")
_emit_routes_through("p1", "resource_prediction_types", "L2")
_emit_checks_agent_registry("p1", "resource_prediction_types", "agent_registry")
_emit_validates_agent_capability("p1", "resource_prediction_types", "capability")
_emit_dispatches_execution_plan("p1", "resource_prediction_types", "exec_plan")
_emit_agent_executes_agent("p1", "resource_prediction_types", "sub_agent")
_emit_routes_to_agent("p1", "resource_prediction_types", "target_agent")
_emit_verifies_policy("p1", "resource_prediction_types", "policy_check")
_emit_observes_runtime_state("p1", "resource_prediction_types", "runtime_state")
_emit_verifies_boundary("p1", "resource_prediction_types", "boundary_check")
_emit_transcripts_response("p1", "resource_prediction_types", "transcript")
_emit_hard_fails_untranscripted("p1", "resource_prediction_types")
_emit_gated_by_confidence("p1", "resource_prediction_types", "confidence_gate")
_emit_escalates_to_human("p1", "resource_prediction_types", "L2")
_emit_reads_policy_state("p1", "resource_prediction_types", "L2")

_emit_applies_guardrail("p0", "resource_prediction_types", "p0_governance")
_emit_snapshots_state("p0", "resource_prediction_types", "state_snapshot")
_emit_authorize_and_execute("p2", "resource_prediction_types", "execution_auth")
_emit_validates_capability("p2", "resource_prediction_types", "capability_check")
_emit_routes_to_capability("p2", "resource_prediction_types", "capability_route")
_emit_writes_via_uwg("p2", "resource_prediction_types", "uwg_write")
_emit_blocks_direct_write("p2", "resource_prediction_types", "direct_write_block")
_emit_records_tool_invocation("p2", "resource_prediction_types", "tool_invocation")
_emit_captures_execution_output("p2", "resource_prediction_types", "exec_output")
_emit_dispatches_agent("p3", "resource_prediction_types", "agent_dispatch")
_emit_coordinates_agents("p3", "resource_prediction_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "resource_prediction_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "resource_prediction_types", "healing_outcome")
_emit_escalates_failure("p3", "resource_prediction_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "resource_prediction_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "resource_prediction_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "resource_prediction_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "resource_prediction_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "resource_prediction_types", "eval_metric")
_emit_stores_embedding("p4", "resource_prediction_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "resource_prediction_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "resource_prediction_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_1")
_emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_2")
_emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_3")
_emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_4")
_emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_5")
_emit_emits_metric_event("resource_prediction_types", "p4obs", "metric_6")
_emit_records_incident_event("resource_prediction_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("resource_prediction_types", "p4obs", "anomaly")
_emit_writes_observability_log("resource_prediction_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("resource_prediction_types", "p4obs", "mon_state")
_emit_triggers_alert("resource_prediction_types", "p4obs", "alert")
_emit_links_incident_trace("resource_prediction_types", "p4obs", "trace_link")
_emit_captures_pattern("resource_prediction_types", "p3lm", "pattern")
_emit_records_learning_event("resource_prediction_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("resource_prediction_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("resource_prediction_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("resource_prediction_types", "p3lm", "routing")
_emit_improves_agent_policy("resource_prediction_types", "p3lm", "policy")
_emit_stores_learning_state("resource_prediction_types", "p3lm", "state")
_emit_records_execution_trace("resource_prediction_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("resource_prediction_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("resource_prediction_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("resource_prediction_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("resource_prediction_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("resource_prediction_types", "env_read", "p2_env_1")
_emit_reads_environ("resource_prediction_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("resource_prediction_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("resource_prediction_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "resource_prediction_types", "context_pull")
_emit_pulls_context("p1", "resource_prediction_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "resource_prediction_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "resource_prediction_types", "uwg_term_2")
_emit_writes_through("p1", "resource_prediction_types", "write_through")
_emit_writes_through("p1", "resource_prediction_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "resource_prediction_types", "safety_validation")
_emit_invokes_eval("p1", "resource_prediction_types", "eval_call")
_emit_proposal_commits_routing("p1", "resource_prediction_types", "routing_commit")


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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "FailureSignature.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FailureSignature.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ResourceEnvelope.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ResourceEnvelope.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ResourcePrediction.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ResourcePrediction.canonical_bytes".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
