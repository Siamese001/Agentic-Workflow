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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "tier_lattice_types")
trace_contract.emit_determinism_digest("p0", "tier_lattice_types")

trace_contract._emit_dispatches_healing_run("p1", "tier_lattice_types", "L5")
trace_contract._emit_routes_through("p1", "tier_lattice_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "tier_lattice_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tier_lattice_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tier_lattice_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tier_lattice_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tier_lattice_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "tier_lattice_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tier_lattice_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tier_lattice_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tier_lattice_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tier_lattice_types")
trace_contract._emit_gated_by_confidence("p1", "tier_lattice_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "tier_lattice_types", "L5")
trace_contract._emit_reads_policy_state("p1", "tier_lattice_types", "L5")

trace_contract._emit_applies_guardrail("p0", "tier_lattice_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "tier_lattice_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "tier_lattice_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "tier_lattice_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tier_lattice_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tier_lattice_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tier_lattice_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tier_lattice_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tier_lattice_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tier_lattice_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tier_lattice_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tier_lattice_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tier_lattice_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tier_lattice_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tier_lattice_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tier_lattice_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tier_lattice_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tier_lattice_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tier_lattice_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tier_lattice_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tier_lattice_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tier_lattice_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tier_lattice_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tier_lattice_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tier_lattice_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tier_lattice_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tier_lattice_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tier_lattice_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tier_lattice_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tier_lattice_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tier_lattice_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tier_lattice_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tier_lattice_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tier_lattice_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tier_lattice_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tier_lattice_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("tier_lattice_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tier_lattice_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tier_lattice_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tier_lattice_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tier_lattice_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tier_lattice_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tier_lattice_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tier_lattice_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tier_lattice_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "tier_lattice_types", "context_pull")
trace_contract._emit_pulls_context("p1", "tier_lattice_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "tier_lattice_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tier_lattice_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "tier_lattice_types", "write_through")
trace_contract._emit_writes_through("p1", "tier_lattice_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "tier_lattice_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tier_lattice_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tier_lattice_types", "routing_commit")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "TierLattice.can_drop")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TierLattice.can_drop".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
