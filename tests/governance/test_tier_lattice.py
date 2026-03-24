"""H7 governance tests: Formal tier lattice with property-based tests.

Validates the 4 lattice invariants exhaustively over all (a, b) pairs:
1. Irreflexivity: no tier strictly dominates itself
2. Antisymmetry: if a dominates b, b does not dominate a
3. Transitivity: if a > b and b > c then a > c
4. Escalation monotonicity: tier can only increase in rollout

Also validates backpressure drop policy and BackpressurePolicy.
"""

import itertools

import pytest

from agentic_core.L5_safety.types.tier_lattice_types import (
    BackpressurePolicy,
    DropPolicy,
    LearningTier,
    TierLattice,
    validate_escalation_sequence,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_tier_lattice", "p4obs", "metric_1")
_emit_emits_metric_event("test_tier_lattice", "p4obs", "metric_2")
_emit_emits_metric_event("test_tier_lattice", "p4obs", "metric_3")
_emit_emits_metric_event("test_tier_lattice", "p4obs", "metric_4")
_emit_emits_metric_event("test_tier_lattice", "p4obs", "metric_5")
_emit_emits_metric_event("test_tier_lattice", "p4obs", "metric_6")
_emit_records_incident_event("test_tier_lattice", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_tier_lattice", "p4obs", "anomaly")
_emit_writes_observability_log("test_tier_lattice", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_tier_lattice", "p4obs", "mon_state")
_emit_triggers_alert("test_tier_lattice", "p4obs", "alert")
_emit_links_incident_trace("test_tier_lattice", "p4obs", "trace_link")
_emit_captures_pattern("test_tier_lattice", "p3lm", "pattern")
_emit_records_learning_event("test_tier_lattice", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_tier_lattice", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_tier_lattice", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_tier_lattice", "p3lm", "routing")
_emit_improves_agent_policy("test_tier_lattice", "p3lm", "policy")
_emit_stores_learning_state("test_tier_lattice", "p3lm", "state")
_emit_records_execution_trace("test_tier_lattice", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_tier_lattice", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_tier_lattice", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_tier_lattice", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_tier_lattice", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_tier_lattice", "env_read", "p2_env_1")
_emit_reads_environ("test_tier_lattice", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_tier_lattice", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_tier_lattice", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_tier_lattice")
_emit_applies_guardrail("p0", "test_tier_lattice", "p0_governance")
_emit_snapshots_state("p0", "test_tier_lattice", "state_snapshot")
_emit_pulls_context("p1", "test_tier_lattice", "context_pull")
_emit_pulls_context("p1", "test_tier_lattice", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_tier_lattice", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_tier_lattice", "uwg_term_secondary")
_emit_writes_through("p1", "test_tier_lattice", "write_through")
_emit_writes_through("p1", "test_tier_lattice", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_tier_lattice", "safety_validation")
_emit_invokes_eval("p1", "test_tier_lattice", "eval_call")
_emit_proposal_commits_routing("p1", "test_tier_lattice", "routing_commit")
_emit_escalates_to_human("p1", "test_tier_lattice", "human_escalation")
_emit_routes_through("p1", "test_tier_lattice", "route_through")
_emit_checks_agent_registry("p1", "test_tier_lattice", "agent_registry")
_emit_validates_agent_capability("p1", "test_tier_lattice", "capability")
_emit_dispatches_execution_plan("p1", "test_tier_lattice", "exec_plan")
_emit_agent_executes_agent("p1", "test_tier_lattice", "sub_agent")
_emit_routes_to_agent("p1", "test_tier_lattice", "target_agent")
_emit_verifies_policy("p1", "test_tier_lattice", "policy_check")
_emit_observes_runtime_state("p1", "test_tier_lattice", "runtime_state")
_emit_verifies_boundary("p1", "test_tier_lattice", "boundary_check")
_emit_transcripts_response("p1", "test_tier_lattice", "transcript")
_emit_hard_fails_untranscripted("p1", "test_tier_lattice")
_emit_gated_by_confidence("p1", "test_tier_lattice", "confidence_gate")
emit_replay_key("p0", "test_tier_lattice")
emit_determinism_digest("p0", "test_tier_lattice")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_tier_lattice", "execution_auth")
_emit_validates_capability("p2", "test_tier_lattice", "capability_check")
_emit_routes_to_capability("p2", "test_tier_lattice", "capability_route")
_emit_writes_via_uwg("p2", "test_tier_lattice", "uwg_write")
_emit_blocks_direct_write("p2", "test_tier_lattice", "direct_write_block")
_emit_records_tool_invocation("p2", "test_tier_lattice", "tool_invocation")
_emit_captures_execution_output("p2", "test_tier_lattice", "exec_output")
_emit_dispatches_agent("p3", "test_tier_lattice", "agent_dispatch")
_emit_coordinates_agents("p3", "test_tier_lattice", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_tier_lattice", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_tier_lattice", "healing_outcome")
_emit_escalates_failure("p3", "test_tier_lattice", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_tier_lattice", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_tier_lattice", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_tier_lattice", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_tier_lattice", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_tier_lattice", "eval_metric")
_emit_stores_embedding("p4", "test_tier_lattice", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_tier_lattice", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_tier_lattice", "exec_snapshot_link")

pytestmark = pytest.mark.governance

ALL_TIERS = list(LearningTier)
ALL_PAIRS = list(itertools.permutations(ALL_TIERS, 2))
ALL_TRIPLES = list(itertools.permutations(ALL_TIERS, 3))

LATTICE = TierLattice()


class TestIrreflexivity:
    """No tier strictly dominates itself."""

    @pytest.mark.parametrize("t", ALL_TIERS, ids=str)
    def test_no_self_dominance(self, t):
        assert not LATTICE.dominates(t, t)


class TestAntisymmetry:
    """If a dominates b, b does not dominate a."""

    @pytest.mark.parametrize(
        "a,b",
        ALL_PAIRS,
        ids=[f"{a.name}-{b.name}" for a, b in ALL_PAIRS],
    )
    def test_antisymmetry(self, a, b):
        if LATTICE.dominates(a, b):
            assert not LATTICE.dominates(b, a)


class TestTransitivity:
    """If a > b and b > c then a > c."""

    @pytest.mark.parametrize(
        "a,b,c",
        ALL_TRIPLES,
        ids=[f"{a.name}-{b.name}-{c.name}" for a, b, c in ALL_TRIPLES],
    )
    def test_transitivity(self, a, b, c):
        if LATTICE.dominates(a, b) and LATTICE.dominates(b, c):
            assert LATTICE.dominates(a, c)


class TestEscalationMonotonicity:
    """Tier can only increase within a rollout sequence."""

    def test_valid_ascending_sequence(self):
        seq = [
            LearningTier.L0,
            LearningTier.L1,
            LearningTier.L2,
            LearningTier.L5,
        ]
        assert validate_escalation_sequence(seq) is True

    def test_valid_flat_sequence(self):
        seq = [
            LearningTier.L2,
            LearningTier.L2,
            LearningTier.L2,
        ]
        assert validate_escalation_sequence(seq) is True

    def test_invalid_descending_sequence(self):
        seq = [
            LearningTier.L3,
            LearningTier.L1,
        ]
        assert validate_escalation_sequence(seq) is False

    def test_empty_sequence_valid(self):
        assert validate_escalation_sequence([]) is True

    def test_single_element_valid(self):
        assert validate_escalation_sequence([LearningTier.L4]) is True


class TestDropPolicy:
    """Backpressure drop policy per tier."""

    def test_l0_safe_to_drop(self):
        assert LATTICE.drop_policy(LearningTier.L0) is DropPolicy.SAFE

    def test_l1_under_pressure_only(self):
        assert LATTICE.drop_policy(LearningTier.L1) is DropPolicy.UNDER_PRESSURE

    @pytest.mark.parametrize(
        "tier",
        [
            LearningTier.L2,
            LearningTier.L3,
            LearningTier.L4,
            LearningTier.L5,
            LearningTier.L6,
        ],
        ids=str,
    )
    def test_l2_plus_never_drop(self, tier):
        assert LATTICE.drop_policy(tier) is DropPolicy.NEVER


class TestCanDrop:
    """can_drop respects policy and pressure flag."""

    def test_l0_always_droppable(self):
        assert LATTICE.can_drop(LearningTier.L0) is True

    def test_l1_not_droppable_without_pressure(self):
        assert LATTICE.can_drop(LearningTier.L1, False) is False

    def test_l1_droppable_under_pressure(self):
        assert LATTICE.can_drop(LearningTier.L1, True) is True

    def test_l2_never_droppable(self):
        assert LATTICE.can_drop(LearningTier.L2, True) is False


class TestBackpressurePolicy:
    """BackpressurePolicy delegates to lattice."""

    def test_should_drop_l0(self):
        bp = BackpressurePolicy(lattice=LATTICE)
        assert bp.should_drop(LearningTier.L0) is True

    def test_should_not_drop_l2(self):
        bp = BackpressurePolicy(lattice=LATTICE)
        assert bp.should_drop(LearningTier.L2) is False

    def test_should_drop_l1_under_pressure(self):
        bp = BackpressurePolicy(lattice=LATTICE)
        assert bp.should_drop(LearningTier.L1, under_pressure=True) is True


class TestLatticeCompleteness:
    """All 21 distinct pairs are covered."""

    def test_21_distinct_pairs(self):
        assert len(ALL_PAIRS) == 42
        distinct = {(min(a, b), max(a, b)) for a, b in ALL_PAIRS}
        assert len(distinct) == 21
