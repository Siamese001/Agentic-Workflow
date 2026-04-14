"""Rollout & Rollback Contracts — Wave 7.0.12 (Schema Lock Only).

Defines schema-locked, frozen artifacts for safe rollout planning:
  - MetaLearningRolloutPlanArtifact  (versioned rollout config)
  - MetaLearningRollbackArtifact     (rollback record)

NO runtime behavior changes.  NO mutation logic.  NO automatic application.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from agentic_core.interfaces.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "rollout_types", "execution_auth")
_emit_validates_capability("p2", "rollout_types", "capability_check")
_emit_routes_to_capability("p2", "rollout_types", "capability_route")
_emit_writes_via_uwg("p2", "rollout_types", "uwg_write")
_emit_blocks_direct_write("p2", "rollout_types", "direct_write_block")
_emit_records_tool_invocation("p2", "rollout_types", "tool_invocation")
_emit_captures_execution_output("p2", "rollout_types", "exec_output")
_emit_dispatches_agent("p3", "rollout_types", "agent_dispatch")
_emit_coordinates_agents("p3", "rollout_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "rollout_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "rollout_types", "healing_outcome")
_emit_escalates_failure("p3", "rollout_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "rollout_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rollout_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "rollout_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "rollout_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rollout_types", "eval_metric")
_emit_stores_embedding("p4", "rollout_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "rollout_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rollout_types", "exec_snapshot_link")
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
from system_learning.enforcement.determinism import (
    deterministic_json,
    stable_sha256_json,
)
from system_learning.types.meta_learning_types import (
    MetaLearningChangePackageArtifact,
    _canonical_payload_json,
)

_emit_emits_metric_event("rollout_types", "p4obs", "metric_1")
_emit_emits_metric_event("rollout_types", "p4obs", "metric_2")
_emit_emits_metric_event("rollout_types", "p4obs", "metric_3")
_emit_emits_metric_event("rollout_types", "p4obs", "metric_4")
_emit_emits_metric_event("rollout_types", "p4obs", "metric_5")
_emit_emits_metric_event("rollout_types", "p4obs", "metric_6")
_emit_records_incident_event("rollout_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("rollout_types", "p4obs", "anomaly")
_emit_writes_observability_log("rollout_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("rollout_types", "p4obs", "mon_state")
_emit_triggers_alert("rollout_types", "p4obs", "alert")
_emit_links_incident_trace("rollout_types", "p4obs", "trace_link")
_emit_captures_pattern("rollout_types", "p3lm", "pattern")
_emit_records_learning_event("rollout_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rollout_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("rollout_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rollout_types", "p3lm", "routing")
_emit_improves_agent_policy("rollout_types", "p3lm", "policy")
_emit_stores_learning_state("rollout_types", "p3lm", "state")
_emit_records_execution_trace("rollout_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rollout_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rollout_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rollout_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rollout_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rollout_types", "env_read", "p2_env_1")
_emit_reads_environ("rollout_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("rollout_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rollout_types", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "rollout_types")
_emit_applies_guardrail("p0", "rollout_types", "p0_governance")
_emit_snapshots_state("p0", "rollout_types", "state_snapshot")
_emit_pulls_context("p1", "rollout_types", "context_pull")
_emit_pulls_context("p1", "rollout_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "rollout_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rollout_types", "uwg_term_secondary")
_emit_writes_through("p1", "rollout_types", "write_through")
_emit_writes_through("p1", "rollout_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "rollout_types", "safety_validation")
_emit_invokes_eval("p1", "rollout_types", "eval_call")
_emit_proposal_commits_routing("p1", "rollout_types", "routing_commit")
_emit_escalates_to_human("p1", "rollout_types", "human_escalation")
_emit_routes_through("p1", "rollout_types", "route_through")
_emit_checks_agent_registry("p1", "rollout_types", "agent_registry")
_emit_validates_agent_capability("p1", "rollout_types", "capability")
_emit_dispatches_execution_plan("p1", "rollout_types", "exec_plan")
_emit_agent_executes_agent("p1", "rollout_types", "sub_agent")
_emit_routes_to_agent("p1", "rollout_types", "target_agent")
_emit_verifies_policy("p1", "rollout_types", "policy_check")
_emit_observes_runtime_state("p1", "rollout_types", "runtime_state")
_emit_verifies_boundary("p1", "rollout_types", "boundary_check")
_emit_transcripts_response("p1", "rollout_types", "transcript")
_emit_hard_fails_untranscripted("p1", "rollout_types")
_emit_gated_by_confidence("p1", "rollout_types", "confidence_gate")
emit_replay_key("p0", "rollout_types")
emit_determinism_digest("p0", "rollout_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# =============================================================================
# §Wave7.0.12 — MetaLearningRolloutPlanArtifact
# =============================================================================

ROLLOUT_STRATEGIES = frozenset({"CANARY", "ALL_AT_ONCE"})
ROLLBACK_REASONS = frozenset(
    {
        "INVARIANT_VIOLATION",
        "METRIC_REGRESSION",
        "TIMEOUT",
        "MANUAL",
    },
)


@dataclass(frozen=True)
class MetaLearningRolloutPlanArtifact:
    """Frozen, schema-locked rollout plan.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - rollout_strategy must be CANARY or ALL_AT_ONCE.
    - canary_percent required iff CANARY (1-50 range); forbidden for ALL_AT_ONCE.
    - invariants must be non-empty list.
    - max_duration_minutes must be >= 1.
    - rollback_on_invariant_fail defaults True; always stored.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_ROLLOUT_PLAN"]
    change_package_trace_id: str
    rollout_strategy: str
    canary_percent: int | None
    max_duration_minutes: int
    invariants: tuple[str, ...]
    rollback_on_invariant_fail: bool
    semantic_clock: SemanticClockSnapshot
    policy_config_hash: str | None
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningRolloutPlanArtifact")
        if self.artifact_type != "META_LEARNING_ROLLOUT_PLAN":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_ROLLOUT_PLAN', got {self.artifact_type!r}",
            )
        if self.rollout_strategy not in ROLLOUT_STRATEGIES:
            raise ValueError(f"INVALID_ROLLOUT_STRATEGY: {self.rollout_strategy!r}")
        if self.rollout_strategy == "CANARY":
            if self.canary_percent is None:
                raise ValueError("CANARY_PERCENT_REQUIRED_FOR_CANARY")
            if not (1 <= self.canary_percent <= 50):
                raise ValueError(
                    f"CANARY_PERCENT_OUT_OF_RANGE: {self.canary_percent} not in [1,50]",
                )
        elif self.canary_percent is not None:
            raise ValueError("CANARY_PERCENT_FORBIDDEN_FOR_ALL_AT_ONCE")
        if not self.invariants:
            raise ValueError("INVARIANTS_EMPTY")
        if self.max_duration_minutes < 1:
            raise ValueError("MAX_DURATION_MINUTES_LESS_THAN_ONE")

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "artifact_type": self.artifact_type,
            "canary_percent": self.canary_percent,
            "change_package_trace_id": self.change_package_trace_id,
            "invariants": list(self.invariants),
            "max_duration_minutes": self.max_duration_minutes,
            "policy_config_hash": self.policy_config_hash,
            "rollback_on_invariant_fail": self.rollback_on_invariant_fail,
            "rollout_strategy": self.rollout_strategy,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


def build_meta_learning_rollout_plan(
    change_pkg: MetaLearningChangePackageArtifact,
    *,
    strategy: str,
    canary_percent: int | None = None,
    invariants: list[str],
    max_duration_minutes: int,
    rollback_on_invariant_fail: bool = True,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None = None,
) -> MetaLearningRolloutPlanArtifact:
    """Build a MetaLearningRolloutPlanArtifact with deterministic trace_id.

    Parameters
    ----------
    change_pkg : MetaLearningChangePackageArtifact
        The change package this rollout plan covers.
    strategy : str
        CANARY or ALL_AT_ONCE.
    canary_percent : int | None
        Required for CANARY (1-50), forbidden for ALL_AT_ONCE.
    invariants : list[str]
        Non-empty list of invariant checks to enforce during rollout.
    max_duration_minutes : int
        Maximum rollout duration (>= 1).
    rollback_on_invariant_fail : bool
        Whether to auto-rollback on invariant failure (default True).
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Optional hash of the governing policy config.

    Returns
    -------
    MetaLearningRolloutPlanArtifact
    """
    validate_semantic_clock(semantic_clock, "build_meta_learning_rollout_plan")
    if strategy not in ROLLOUT_STRATEGIES:
        raise ValueError(f"INVALID_ROLLOUT_STRATEGY: {strategy!r}")
    if not invariants:
        raise ValueError("INVARIANTS_EMPTY")

    inv_tuple = tuple(sorted(invariants))

    temp_payload = {
        "artifact_type": "META_LEARNING_ROLLOUT_PLAN",
        "canary_percent": canary_percent,
        "change_package_trace_id": change_pkg.trace_id,
        "invariants": list(inv_tuple),
        "max_duration_minutes": max_duration_minutes,
        "policy_config_hash": policy_config_hash,
        "rollback_on_invariant_fail": rollback_on_invariant_fail,
        "rollout_strategy": strategy,
        "semantic_clock": semantic_clock.to_dict(),
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningRolloutPlanArtifact(
        artifact_type="META_LEARNING_ROLLOUT_PLAN",
        change_package_trace_id=change_pkg.trace_id,
        rollout_strategy=strategy,
        canary_percent=canary_percent,
        max_duration_minutes=max_duration_minutes,
        invariants=inv_tuple,
        rollback_on_invariant_fail=rollback_on_invariant_fail,
        semantic_clock=semantic_clock,
        policy_config_hash=policy_config_hash,
        trace_id=trace_id,
    )


# =============================================================================
# §Wave7.0.12 — MetaLearningRollbackArtifact
# =============================================================================


@dataclass(frozen=True)
class MetaLearningRollbackArtifact:
    """Frozen, schema-locked rollback record.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - rollback_reason must be a valid ROLLBACK_REASONS value.
    - rollout_trace_id links back to the rollout plan.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_ROLLBACK"]
    rollout_trace_id: str
    rollback_reason: str
    semantic_clock: SemanticClockSnapshot
    policy_config_hash: str | None
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningRollbackArtifact")
        if self.artifact_type != "META_LEARNING_ROLLBACK":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_ROLLBACK', got {self.artifact_type!r}",
            )
        if self.rollback_reason not in ROLLBACK_REASONS:
            raise ValueError(f"INVALID_ROLLBACK_REASON: {self.rollback_reason!r}")

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "artifact_type": self.artifact_type,
            "policy_config_hash": self.policy_config_hash,
            "rollback_reason": self.rollback_reason,
            "rollout_trace_id": self.rollout_trace_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


def build_meta_learning_rollback(
    rollout: MetaLearningRolloutPlanArtifact,
    *,
    rollback_reason: str,
    semantic_clock: SemanticClockSnapshot,
) -> MetaLearningRollbackArtifact:
    """Build a MetaLearningRollbackArtifact with deterministic trace_id.

    Parameters
    ----------
    rollout : MetaLearningRolloutPlanArtifact
        The rollout plan being rolled back.
    rollback_reason : str
        Must be one of ROLLBACK_REASONS.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.

    Returns
    -------
    MetaLearningRollbackArtifact
    """
    validate_semantic_clock(semantic_clock, "build_meta_learning_rollback")
    if rollback_reason not in ROLLBACK_REASONS:
        raise ValueError(f"INVALID_ROLLBACK_REASON: {rollback_reason!r}")

    temp_payload = {
        "artifact_type": "META_LEARNING_ROLLBACK",
        "policy_config_hash": rollout.policy_config_hash,
        "rollback_reason": rollback_reason,
        "rollout_trace_id": rollout.trace_id,
        "semantic_clock": semantic_clock.to_dict(),
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningRollbackArtifact(
        artifact_type="META_LEARNING_ROLLBACK",
        rollout_trace_id=rollout.trace_id,
        rollback_reason=rollback_reason,
        semantic_clock=semantic_clock,
        policy_config_hash=rollout.policy_config_hash,
        trace_id=trace_id,
    )
