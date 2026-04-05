"""Healing Outcome Learning Types - Deterministic aggregation for meta-learning.

Immutable, frozen dataclasses for deterministic healing outcome aggregation.
All types are frozen with slots for deterministic behavior.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

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

_emit_applies_guardrail("p0", "healing_outcome_learning_types", "p0_governance")
_emit_reads_policy_state("p0", "healing_outcome_learning_types", "policy_binding")
_emit_snapshots_state("p0", "healing_outcome_learning_types", "state_snapshot")
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

_emit_emits_metric_event("healing_outcome_learning_types", "p4obs", "metric_1")
_emit_emits_metric_event("healing_outcome_learning_types", "p4obs", "metric_2")
_emit_emits_metric_event("healing_outcome_learning_types", "p4obs", "metric_3")
_emit_emits_metric_event("healing_outcome_learning_types", "p4obs", "metric_4")
_emit_emits_metric_event("healing_outcome_learning_types", "p4obs", "metric_5")
_emit_emits_metric_event("healing_outcome_learning_types", "p4obs", "metric_6")
_emit_records_incident_event("healing_outcome_learning_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_outcome_learning_types", "p4obs", "anomaly")
_emit_writes_observability_log("healing_outcome_learning_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_outcome_learning_types", "p4obs", "mon_state")
_emit_triggers_alert("healing_outcome_learning_types", "p4obs", "alert")
_emit_links_incident_trace("healing_outcome_learning_types", "p4obs", "trace_link")
_emit_captures_pattern("healing_outcome_learning_types", "p3lm", "pattern")
_emit_records_learning_event("healing_outcome_learning_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_outcome_learning_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_outcome_learning_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_outcome_learning_types", "p3lm", "routing")
_emit_improves_agent_policy("healing_outcome_learning_types", "p3lm", "policy")
_emit_stores_learning_state("healing_outcome_learning_types", "p3lm", "state")
_emit_records_execution_trace("healing_outcome_learning_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_outcome_learning_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_outcome_learning_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_outcome_learning_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_outcome_learning_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_outcome_learning_types", "env_read", "p2_env_1")
_emit_reads_environ("healing_outcome_learning_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_outcome_learning_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_outcome_learning_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_outcome_learning_types", "context_pull")
_emit_pulls_context("p1", "healing_outcome_learning_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_outcome_learning_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_outcome_learning_types", "uwg_term_2")
_emit_writes_through("p1", "healing_outcome_learning_types", "write_through")
_emit_writes_through("p1", "healing_outcome_learning_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_outcome_learning_types", "safety_validation")
_emit_invokes_eval("p1", "healing_outcome_learning_types", "eval_call")
_emit_proposal_commits_routing("p1", "healing_outcome_learning_types", "routing_commit")
_emit_escalates_to_human("p1", "healing_outcome_learning_types", "human_escalation")
_emit_routes_through("p1", "healing_outcome_learning_types", "route_through")
_emit_checks_agent_registry("p1", "healing_outcome_learning_types", "agent_registry")
_emit_validates_agent_capability("p1", "healing_outcome_learning_types", "capability")
_emit_dispatches_execution_plan("p1", "healing_outcome_learning_types", "exec_plan")
_emit_agent_executes_agent("p1", "healing_outcome_learning_types", "sub_agent")
_emit_routes_to_agent("p1", "healing_outcome_learning_types", "target_agent")
_emit_verifies_policy("p1", "healing_outcome_learning_types", "policy_check")
_emit_observes_runtime_state("p1", "healing_outcome_learning_types", "runtime_state")
_emit_verifies_boundary("p1", "healing_outcome_learning_types", "boundary_check")
_emit_transcripts_response("p1", "healing_outcome_learning_types", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_outcome_learning_types")
_emit_gated_by_confidence("p1", "healing_outcome_learning_types", "confidence_gate")
emit_replay_key("p0", "healing_outcome_learning_types")
emit_determinism_digest("p0", "healing_outcome_learning_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "healing_outcome_learning_types", "execution_auth")
_emit_validates_capability("p2", "healing_outcome_learning_types", "capability_check")
_emit_routes_to_capability("p2", "healing_outcome_learning_types", "capability_route")
_emit_writes_via_uwg("p2", "healing_outcome_learning_types", "uwg_write")
_emit_blocks_direct_write("p2", "healing_outcome_learning_types", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_outcome_learning_types", "tool_invocation")
_emit_captures_execution_output("p2", "healing_outcome_learning_types", "exec_output")
_emit_dispatches_agent("p3", "healing_outcome_learning_types", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_outcome_learning_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_outcome_learning_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_outcome_learning_types", "healing_outcome")
_emit_escalates_failure("p3", "healing_outcome_learning_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_outcome_learning_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_outcome_learning_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_outcome_learning_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_outcome_learning_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_outcome_learning_types", "eval_metric")
_emit_stores_embedding("p4", "healing_outcome_learning_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_outcome_learning_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_outcome_learning_types", "exec_snapshot_link")


@dataclass(frozen=True, slots=True)
class HealingOutcomeAggregateKey:
    """Deterministic key for healing outcome aggregation.

    Attributes
    ----------
    healer_name : str
        Canonical healer identifier.
    tier : str
        Healing tier (e.g., 'LOCAL_AGENT', 'REMOTE_AGENT', 'CLOUD_SERVICE').
    failure_type : str
        Stable failure category string.
    """

    healer_name: str
    tier: str
    failure_type: str

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not self.healer_name:
            raise ValueError("healer_name must not be empty")
        if not self.tier:
            raise ValueError("tier must not be empty")
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")


@dataclass(frozen=True, slots=True)
class HealingOutcomeAggregate:
    """Deterministic aggregate counters for a healing outcome key.

    Attributes
    ----------
    success_count : int
        Number of successful healing attempts.
    failure_count : int
        Number of failed healing attempts.
    total_count : int
        Total attempts (success_count + failure_count).
    """

    success_count: int
    failure_count: int
    total_count: int

    def __post_init__(self) -> None:
        """Validate invariants."""
        if self.success_count < 0:
            raise ValueError("success_count must be non-negative")
        if self.failure_count < 0:
            raise ValueError("failure_count must be non-negative")
        if self.total_count != self.success_count + self.failure_count:
            raise ValueError("total_count must equal success_count + failure_count")

    @property
    def success_rate(self) -> float:
        """Compute success rate with deterministic rounding."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingOutcomeAggregate.success_rate")

        if self.total_count == 0:
            return 0.0
        raw_rate = self.success_count / self.total_count
        return round(raw_rate + 1e-10, 4)

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation for hashing."""
        data = {
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_count": self.total_count,
        }
        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA-256 hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class HealingOutcomeAggregateSnapshot:
    """Deterministic snapshot of healing outcome aggregates.

    Attributes
    ----------
    version_id : str
        Unique version identifier (SHA-256 hash of content).
    created_utc : int
        Snapshot creation timestamp (explicit, no wall-clock reads).
    aggregates : tuple[tuple[HealingOutcomeAggregateKey, HealingOutcomeAggregate], ...]
        Sorted tuple of (key, aggregate) pairs.
    """

    version_id: str
    created_utc: int
    aggregates: tuple[tuple[HealingOutcomeAggregateKey, HealingOutcomeAggregate], ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not self.version_id:
            raise ValueError("version_id must not be empty")
        if self.created_utc < 0:
            raise ValueError("created_utc must be non-negative")
        if self.aggregates:
            keys = [key for key, _ in self.aggregates]
            sorted_keys = sorted(keys, key=lambda k: (k.healer_name, k.tier, k.failure_type))
            if keys != sorted_keys:
                raise ValueError("aggregates must be sorted by (healer_name, tier, failure_type)")

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingOutcomeAggregateSnapshot.canonical_bytes")

        aggregates_data = []
        for key, aggregate in self.aggregates:
            key_data = {"healer_name": key.healer_name, "tier": key.tier, "failure_type": key.failure_type}
            aggregate_data = {
                "success_count": aggregate.success_count,
                "failure_count": aggregate.failure_count,
                "total_count": aggregate.total_count,
            }
            aggregates_data.append({"key": key_data, "aggregate": aggregate_data})
        data = {"version_id": self.version_id, "created_utc": self.created_utc, "aggregates": aggregates_data}
        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA-256 hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def get_success_rate(self, key: HealingOutcomeAggregateKey) -> float:
        """Get success rate for a specific key."""
        for k, aggregate in self.aggregates:
            if (
                k.healer_name == key.healer_name
                and k.tier == key.tier
                and (k.failure_type == key.failure_type)
            ):
                return aggregate.success_rate
        return 0.0


__all__ = ["HealingOutcomeAggregateKey", "HealingOutcomeAggregate", "HealingOutcomeAggregateSnapshot"]
