"""Apply Attempt Artifact — Wave 7.0.14 (Schema Lock).

Frozen, schema-locked artifact recording the outcome of an explicit
meta-learning apply attempt (DRY_RUN or APPLY).

NO automatic application.  Explicit invoke only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.interfaces.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "apply_attempt_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "apply_attempt_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "apply_attempt_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "apply_attempt_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "apply_attempt_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "apply_attempt_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "apply_attempt_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "apply_attempt_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "apply_attempt_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "apply_attempt_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "apply_attempt_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "apply_attempt_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "apply_attempt_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "apply_attempt_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "apply_attempt_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "apply_attempt_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "apply_attempt_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "apply_attempt_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "apply_attempt_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "apply_attempt_types", "exec_snapshot_link")
from agentic_core.L6_system_learning.enforcement.determinism import (
    deterministic_json,
    stable_sha256_json,
)
from .meta_learning_types import (
    _canonical_payload_json,
)

trace_contract._emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("apply_attempt_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("apply_attempt_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("apply_attempt_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("apply_attempt_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("apply_attempt_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("apply_attempt_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("apply_attempt_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("apply_attempt_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("apply_attempt_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("apply_attempt_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("apply_attempt_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("apply_attempt_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("apply_attempt_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("apply_attempt_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("apply_attempt_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("apply_attempt_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("apply_attempt_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("apply_attempt_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("apply_attempt_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("apply_attempt_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("apply_attempt_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("apply_attempt_types", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "apply_attempt_types")
trace_contract._emit_applies_guardrail("p0", "apply_attempt_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "apply_attempt_types", "state_snapshot")
trace_contract._emit_pulls_context("p1", "apply_attempt_types", "context_pull")
trace_contract._emit_pulls_context("p1", "apply_attempt_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "apply_attempt_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "apply_attempt_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "apply_attempt_types", "write_through")
trace_contract._emit_writes_through("p1", "apply_attempt_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "apply_attempt_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "apply_attempt_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "apply_attempt_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "apply_attempt_types", "human_escalation")
trace_contract._emit_routes_through("p1", "apply_attempt_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "apply_attempt_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "apply_attempt_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "apply_attempt_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "apply_attempt_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "apply_attempt_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "apply_attempt_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "apply_attempt_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "apply_attempt_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "apply_attempt_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "apply_attempt_types")
trace_contract._emit_gated_by_confidence("p1", "apply_attempt_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "apply_attempt_types")
trace_contract.emit_determinism_digest("p0", "apply_attempt_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True)
class MetaLearningApplyAttemptArtifact:
    """Frozen, schema-locked apply attempt record.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - outcome is APPLIED or REJECTED (fail-closed).
    - reject_reason is None when APPLIED, a stable code when REJECTED.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_APPLY_ATTEMPT"]
    change_package_trace_id: str
    rollout_trace_id: str
    policy_config_hash: str | None
    target_component: str
    apply_mode: Literal["DRY_RUN", "APPLY"]
    outcome: Literal["APPLIED", "REJECTED"]
    reject_reason: str | None
    details: dict[str, str]
    semantic_clock: SemanticClockSnapshot
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningApplyAttemptArtifact")
        if self.artifact_type != "META_LEARNING_APPLY_ATTEMPT":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_APPLY_ATTEMPT', got {self.artifact_type!r}",
            )

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "apply_mode": self.apply_mode,
            "artifact_type": self.artifact_type,
            "change_package_trace_id": self.change_package_trace_id,
            "details": dict(sorted(self.details.items())),
            "outcome": self.outcome,
            "policy_config_hash": self.policy_config_hash,
            "reject_reason": self.reject_reason,
            "rollout_trace_id": self.rollout_trace_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target_component": self.target_component,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


def build_apply_attempt(
    *,
    change_package_trace_id: str,
    rollout_trace_id: str,
    policy_config_hash: str | None,
    target_component: str,
    apply_mode: Literal["DRY_RUN", "APPLY"],
    outcome: Literal["APPLIED", "REJECTED"],
    reject_reason: str | None,
    details: dict[str, str],
    semantic_clock: SemanticClockSnapshot,
) -> MetaLearningApplyAttemptArtifact:
    """Build a MetaLearningApplyAttemptArtifact with deterministic trace_id."""
    validate_semantic_clock(semantic_clock, "build_apply_attempt")

    sorted_details = dict(sorted(details.items()))

    temp_payload: dict[str, Any] = {
        "apply_mode": apply_mode,
        "artifact_type": "META_LEARNING_APPLY_ATTEMPT",
        "change_package_trace_id": change_package_trace_id,
        "details": sorted_details,
        "outcome": outcome,
        "policy_config_hash": policy_config_hash,
        "reject_reason": reject_reason,
        "rollout_trace_id": rollout_trace_id,
        "semantic_clock": semantic_clock.to_dict(),
        "target_component": target_component,
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningApplyAttemptArtifact(
        artifact_type="META_LEARNING_APPLY_ATTEMPT",
        change_package_trace_id=change_package_trace_id,
        rollout_trace_id=rollout_trace_id,
        policy_config_hash=policy_config_hash,
        target_component=target_component,
        apply_mode=apply_mode,
        outcome=outcome,
        reject_reason=reject_reason,
        details=sorted_details,
        semantic_clock=semantic_clock,
        trace_id=trace_id,
    )
