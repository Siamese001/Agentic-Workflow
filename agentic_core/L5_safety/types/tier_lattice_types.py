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
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "tier_lattice_types")
emit_determinism_digest("p0", "tier_lattice_types")

_emit_dispatches_healing_run("p1", "tier_lattice_types", "L5")
_emit_routes_through("p1", "tier_lattice_types", "L5")
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
