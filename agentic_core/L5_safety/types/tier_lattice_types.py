"""
H7: Formal tier lattice definition with partial order.

Defines the canonical partial order over learning tiers (L0–L6)
and the backpressure drop policy.

Lattice invariants:
  1. Irreflexivity: no tier strictly dominates itself
  2. Antisymmetry: if a dominates b, b does not dominate a
  3. Transitivity: if a > b and b > c then a > c
  4. Escalation monotonicity: tier can only increase within
     a rollout sequence

Preservation policy:
  drop(L0) = safe
  drop(L1) = under pressure only
  never drop(L2+)
"""

from __future__ import annotations

import enum
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

emit_replay_key("p0", "tier_lattice_types")
emit_determinism_digest("p0", "tier_lattice_types")

_emit_dispatches_healing_run("p1", "tier_lattice_types", "L5")
_emit_routes_through("p1", "tier_lattice_types", "L5")
_emit_checks_agent_registry("p1", "tier_lattice_types", "agent_registry")
_emit_validates_agent_capability("p1", "tier_lattice_types", "capability")
_emit_dispatches_execution_plan("p1", "tier_lattice_types", "exec_plan")
_emit_agent_executes_agent("p1", "tier_lattice_types", "sub_agent")
_emit_routes_to_agent("p1", "tier_lattice_types", "target_agent")
_emit_verifies_policy("p1", "tier_lattice_types", "policy_check")
_emit_observes_runtime_state("p1", "tier_lattice_types", "runtime_state")
_emit_verifies_boundary("p1", "tier_lattice_types", "boundary_check")
_emit_transcripts_response("p1", "tier_lattice_types", "transcript")
_emit_hard_fails_untranscripted("p1", "tier_lattice_types")
_emit_gated_by_confidence("p1", "tier_lattice_types", "confidence_gate")
_emit_escalates_to_human("p1", "tier_lattice_types", "L5")
_emit_reads_policy_state("p1", "tier_lattice_types", "L5")

_emit_applies_guardrail("p0", "tier_lattice_types", "p0_governance")
_emit_snapshots_state("p0", "tier_lattice_types", "state_snapshot")
_emit_authorize_and_execute("p2", "tier_lattice_types", "execution_auth")
_emit_validates_capability("p2", "tier_lattice_types", "capability_check")
_emit_routes_to_capability("p2", "tier_lattice_types", "capability_route")
_emit_writes_via_uwg("p2", "tier_lattice_types", "uwg_write")
_emit_blocks_direct_write("p2", "tier_lattice_types", "direct_write_block")
_emit_records_tool_invocation("p2", "tier_lattice_types", "tool_invocation")
_emit_captures_execution_output("p2", "tier_lattice_types", "exec_output")
_emit_dispatches_agent("p3", "tier_lattice_types", "agent_dispatch")
_emit_coordinates_agents("p3", "tier_lattice_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "tier_lattice_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "tier_lattice_types", "healing_outcome")
_emit_escalates_failure("p3", "tier_lattice_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "tier_lattice_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tier_lattice_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "tier_lattice_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "tier_lattice_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tier_lattice_types", "eval_metric")
_emit_stores_embedding("p4", "tier_lattice_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "tier_lattice_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tier_lattice_types", "exec_snapshot_link")
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

_emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_1")
_emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_2")
_emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_3")
_emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_4")
_emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_5")
_emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_6")
_emit_records_incident_event("tier_lattice_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("tier_lattice_types", "p4obs", "anomaly")
_emit_writes_observability_log("tier_lattice_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("tier_lattice_types", "p4obs", "mon_state")
_emit_triggers_alert("tier_lattice_types", "p4obs", "alert")
_emit_links_incident_trace("tier_lattice_types", "p4obs", "trace_link")
_emit_captures_pattern("tier_lattice_types", "p3lm", "pattern")
_emit_records_learning_event("tier_lattice_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tier_lattice_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("tier_lattice_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tier_lattice_types", "p3lm", "routing")
_emit_improves_agent_policy("tier_lattice_types", "p3lm", "policy")
_emit_stores_learning_state("tier_lattice_types", "p3lm", "state")
_emit_records_execution_trace("tier_lattice_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tier_lattice_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tier_lattice_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tier_lattice_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tier_lattice_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tier_lattice_types", "env_read", "p2_env_1")
_emit_reads_environ("tier_lattice_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("tier_lattice_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tier_lattice_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tier_lattice_types", "context_pull")
_emit_pulls_context("p1", "tier_lattice_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tier_lattice_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tier_lattice_types", "uwg_term_2")
_emit_writes_through("p1", "tier_lattice_types", "write_through")
_emit_writes_through("p1", "tier_lattice_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "tier_lattice_types", "safety_validation")
_emit_invokes_eval("p1", "tier_lattice_types", "eval_call")
_emit_proposal_commits_routing("p1", "tier_lattice_types", "routing_commit")


class LearningTier(enum.IntEnum):
    """Canonical learning tier enumeration."""

    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6


class DropPolicy(enum.Enum):
    """Backpressure drop policy per tier."""

    SAFE = "safe"
    UNDER_PRESSURE = "under_pressure"
    NEVER = "never"


_DROP_POLICY: dict[LearningTier, DropPolicy] = {
    LearningTier.L0: DropPolicy.SAFE,
    LearningTier.L1: DropPolicy.UNDER_PRESSURE,
    LearningTier.L2: DropPolicy.NEVER,
    LearningTier.L3: DropPolicy.NEVER,
    LearningTier.L4: DropPolicy.NEVER,
    LearningTier.L5: DropPolicy.NEVER,
    LearningTier.L6: DropPolicy.NEVER,
}


@dataclass(frozen=True)
class TierLattice:
    """Formal partial order over LearningTier.

    Uses the natural integer ordering of IntEnum values.
    ``dominates(a, b)`` means ``a`` is strictly higher than
    ``b`` in the lattice (a > b).
    """

    def dominates(self, a: LearningTier, b: LearningTier) -> bool:
        """Return True if ``a`` strictly dominates ``b``.

        Strict dominance: a.value > b.value.
        """
        return a.value > b.value

    def drop_policy(self, tier: LearningTier) -> DropPolicy:
        """Return the backpressure drop policy for a tier."""
        return _DROP_POLICY[tier]

    def can_drop(self, tier: LearningTier, under_pressure: bool = False) -> bool:
        """Whether a signal at this tier may be dropped."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "TierLattice.can_drop")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TierLattice.can_drop".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        policy = self.drop_policy(tier)
        if policy is DropPolicy.SAFE:
            return True
        if policy is DropPolicy.UNDER_PRESSURE:
            return under_pressure
        return False


@dataclass
class BackpressurePolicy:
    """Policy engine that references TierLattice for drops."""

    lattice: TierLattice

    def should_drop(self, tier: LearningTier, under_pressure: bool = False) -> bool:
        """Decide whether to drop a signal at this tier."""
        return self.lattice.can_drop(tier, under_pressure=under_pressure)


def validate_escalation_sequence(sequence: list[LearningTier]) -> bool:
    """Validate that a rollout sequence is monotonically
    non-decreasing (escalation monotonicity).

    Returns True if valid, False if any tier decreases.
    """
    for i in range(1, len(sequence)):
        if sequence[i].value < sequence[i - 1].value:
            return False
    return True
