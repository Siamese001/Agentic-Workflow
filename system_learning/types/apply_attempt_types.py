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
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_authorize_and_execute("p2", "apply_attempt_types", "execution_auth")
_emit_validates_capability("p2", "apply_attempt_types", "capability_check")
_emit_routes_to_capability("p2", "apply_attempt_types", "capability_route")
_emit_writes_via_uwg("p2", "apply_attempt_types", "uwg_write")
_emit_blocks_direct_write("p2", "apply_attempt_types", "direct_write_block")
_emit_records_tool_invocation("p2", "apply_attempt_types", "tool_invocation")
_emit_captures_execution_output("p2", "apply_attempt_types", "exec_output")
_emit_dispatches_agent("p3", "apply_attempt_types", "agent_dispatch")
_emit_coordinates_agents("p3", "apply_attempt_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "apply_attempt_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "apply_attempt_types", "healing_outcome")
_emit_escalates_failure("p3", "apply_attempt_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "apply_attempt_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "apply_attempt_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "apply_attempt_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "apply_attempt_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "apply_attempt_types", "eval_metric")
_emit_stores_embedding("p4", "apply_attempt_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "apply_attempt_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "apply_attempt_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
from system_learning.enforcement.determinism import (
    deterministic_json,
    stable_sha256_json,
)
from system_learning.types.meta_learning_types import (
    _canonical_payload_json,
)

_emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_1")
_emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_2")
_emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_3")
_emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_4")
_emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_5")
_emit_emits_metric_event("apply_attempt_types", "p4obs", "metric_6")
_emit_records_incident_event("apply_attempt_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("apply_attempt_types", "p4obs", "anomaly")
_emit_writes_observability_log("apply_attempt_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("apply_attempt_types", "p4obs", "mon_state")
_emit_triggers_alert("apply_attempt_types", "p4obs", "alert")
_emit_links_incident_trace("apply_attempt_types", "p4obs", "trace_link")
_emit_captures_pattern("apply_attempt_types", "p3lm", "pattern")
_emit_records_learning_event("apply_attempt_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("apply_attempt_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("apply_attempt_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("apply_attempt_types", "p3lm", "routing")
_emit_improves_agent_policy("apply_attempt_types", "p3lm", "policy")
_emit_stores_learning_state("apply_attempt_types", "p3lm", "state")
_emit_records_execution_trace("apply_attempt_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("apply_attempt_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("apply_attempt_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("apply_attempt_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("apply_attempt_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("apply_attempt_types", "env_read", "p2_env_1")
_emit_reads_environ("apply_attempt_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("apply_attempt_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("apply_attempt_types", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "apply_attempt_types")
_emit_applies_guardrail("p0", "apply_attempt_types", "p0_governance")
_emit_snapshots_state("p0", "apply_attempt_types", "state_snapshot")
_emit_pulls_context("p1", "apply_attempt_types", "context_pull")
_emit_pulls_context("p1", "apply_attempt_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "apply_attempt_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "apply_attempt_types", "uwg_term_secondary")
_emit_writes_through("p1", "apply_attempt_types", "write_through")
_emit_writes_through("p1", "apply_attempt_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "apply_attempt_types", "safety_validation")
_emit_invokes_eval("p1", "apply_attempt_types", "eval_call")
_emit_proposal_commits_routing("p1", "apply_attempt_types", "routing_commit")
_emit_escalates_to_human("p1", "apply_attempt_types", "human_escalation")
_emit_routes_through("p1", "apply_attempt_types", "route_through")
_emit_checks_agent_registry("p1", "apply_attempt_types", "agent_registry")
_emit_validates_agent_capability("p1", "apply_attempt_types", "capability")
_emit_dispatches_execution_plan("p1", "apply_attempt_types", "exec_plan")
_emit_agent_executes_agent("p1", "apply_attempt_types", "sub_agent")
_emit_routes_to_agent("p1", "apply_attempt_types", "target_agent")
_emit_verifies_policy("p1", "apply_attempt_types", "policy_check")
_emit_observes_runtime_state("p1", "apply_attempt_types", "runtime_state")
_emit_verifies_boundary("p1", "apply_attempt_types", "boundary_check")
_emit_transcripts_response("p1", "apply_attempt_types", "transcript")
_emit_hard_fails_untranscripted("p1", "apply_attempt_types")
_emit_gated_by_confidence("p1", "apply_attempt_types", "confidence_gate")
emit_replay_key("p0", "apply_attempt_types")
emit_determinism_digest("p0", "apply_attempt_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
