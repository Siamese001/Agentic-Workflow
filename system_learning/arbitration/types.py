"""Arbitration types for deterministic multi-agent proposal selection."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_applies_guardrail("p0", "types", "p0_governance")
_emit_reads_policy_state("p0", "types", "policy_binding")
_emit_snapshots_state("p0", "types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("types", "p4obs", "metric_1")
_emit_emits_metric_event("types", "p4obs", "metric_2")
_emit_emits_metric_event("types", "p4obs", "metric_3")
_emit_emits_metric_event("types", "p4obs", "metric_4")
_emit_emits_metric_event("types", "p4obs", "metric_5")
_emit_emits_metric_event("types", "p4obs", "metric_6")
_emit_records_incident_event("types", "p4obs", "incident")
_emit_captures_runtime_anomaly("types", "p4obs", "anomaly")
_emit_writes_observability_log("types", "p4obs", "obs_log")
_emit_updates_monitoring_state("types", "p4obs", "mon_state")
_emit_triggers_alert("types", "p4obs", "alert")
_emit_links_incident_trace("types", "p4obs", "trace_link")
_emit_captures_pattern("types", "p3lm", "pattern")
_emit_records_learning_event("types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("types", "p3lm", "snapshot")
_emit_feeds_meta_learning("types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("types", "p3lm", "routing")
_emit_improves_agent_policy("types", "p3lm", "policy")
_emit_stores_learning_state("types", "p3lm", "state")
_emit_records_execution_trace("types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("types", "env_read", "p2_env_1")
_emit_reads_environ("types", "env_read", "p2_env_2")
_emit_reads_runtime_state("types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "types", "context_pull")
_emit_pulls_context("p1", "types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "types", "uwg_term_2")
_emit_writes_through("p1", "types", "write_through")
_emit_writes_through("p1", "types", "write_through_2")
_emit_validated_by_safety_plane("p1", "types", "safety_validation")
_emit_invokes_eval("p1", "types", "eval_call")
_emit_proposal_commits_routing("p1", "types", "routing_commit")
_emit_escalates_to_human("p1", "types", "human_escalation")
_emit_routes_through("p1", "types", "route_through")
_emit_checks_agent_registry("p1", "types", "agent_registry")
_emit_validates_agent_capability("p1", "types", "capability")
_emit_dispatches_execution_plan("p1", "types", "exec_plan")
_emit_agent_executes_agent("p1", "types", "sub_agent")
_emit_routes_to_agent("p1", "types", "target_agent")
_emit_verifies_policy("p1", "types", "policy_check")
_emit_observes_runtime_state("p1", "types", "runtime_state")
_emit_verifies_boundary("p1", "types", "boundary_check")
_emit_transcripts_response("p1", "types", "transcript")
_emit_hard_fails_untranscripted("p1", "types")
_emit_gated_by_confidence("p1", "types", "confidence_gate")
emit_replay_key("p0", "types")
emit_determinism_digest("p0", "types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "types", "execution_auth")
_emit_validates_capability("p2", "types", "capability_check")
_emit_routes_to_capability("p2", "types", "capability_route")
_emit_writes_via_uwg("p2", "types", "uwg_write")
_emit_blocks_direct_write("p2", "types", "direct_write_block")
_emit_records_tool_invocation("p2", "types", "tool_invocation")
_emit_captures_execution_output("p2", "types", "exec_output")
_emit_dispatches_agent("p3", "types", "agent_dispatch")
_emit_coordinates_agents("p3", "types", "agent_coordination")
_emit_records_workflow_lineage("p3", "types", "workflow_lineage")
_emit_records_healing_outcome("p3", "types", "healing_outcome")
_emit_escalates_failure("p3", "types", "failure_escalation")
_emit_orchestrates_workflow("p3", "types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "types", "healing_dispatch")
_emit_invokes_evaluation("p3", "types", "evaluation_signal")
_emit_records_telemetry_event("p4", "types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "types", "eval_metric")
_emit_stores_embedding("p4", "types", "embedding_store")
_emit_updates_meta_learning_state("p4", "types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "types", "exec_snapshot_link")


@dataclass(frozen=True)
class ArbitrationCandidate:
    """A candidate proposal for arbitration."""

    id: str
    kind: str
    payload: dict[str, Any]
    score: float
    cost: float
    provenance: str
    created_at: int | None = None

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArbitrationCandidate.canonical_bytes")

        data = {
            "id": self.id,
            "kind": self.kind,
            "payload": self.payload,
            "score": self.score,
            "cost": self.cost,
            "provenance": self.provenance,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class ArbitrationPolicy:
    """Policy governing arbitration decisions."""

    weights: dict[str, float]
    caps: dict[str, Any]
    thresholds: dict[str, float]
    allowed_kinds: set[str]

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArbitrationPolicy.canonical_bytes")

        data = {
            "weights": self.weights,
            "caps": self.caps,
            "thresholds": self.thresholds,
            "allowed_kinds": sorted(self.allowed_kinds),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class ArbitrationDecision:
    """Result of arbitration process."""

    winner_ids: tuple[str, ...]
    merged_payload: dict[str, Any] | None
    rationale_codes: tuple[str, ...]
    deterministic_fingerprint: str

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArbitrationDecision.canonical_bytes")

        data = {
            "winner_ids": self.winner_ids,
            "merged_payload": self.merged_payload,
            "rationale_codes": self.rationale_codes,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
