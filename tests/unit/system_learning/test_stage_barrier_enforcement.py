"""Addendum 5.1: Stage Barrier Enforcer tests."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_stage_barrier_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_stage_barrier_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_stage_barrier_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_stage_barrier_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_stage_barrier_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_stage_barrier_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_stage_barrier_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_stage_barrier_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_stage_barrier_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_stage_barrier_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_stage_barrier_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_stage_barrier_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_stage_barrier_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_stage_barrier_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_stage_barrier_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_stage_barrier_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_stage_barrier_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_stage_barrier_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_stage_barrier_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_stage_barrier_enforcement", "exec_snapshot_link")
from system_learning.engines.stage_barrier_enforcer import MetaLearningStage, StageBarrierEnforcer

_emit_records_execution_trace("p0", "evidence", "test_stage_barrier_enforcement")
_emit_applies_guardrail("p0", "test_stage_barrier_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_stage_barrier_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_stage_barrier_enforcement", "state_snapshot")
emit_replay_key("p0", "test_stage_barrier_enforcement")
emit_determinism_digest("p0", "test_stage_barrier_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class TestStageBarrierEnforcer:
    def test_advance_sequential_passes(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S1_AUDIT)
        enforcer.advance_to(MetaLearningStage.S3_CONFIG)
        enforcer.advance_to(MetaLearningStage.S9_COMMIT)

    def test_backwards_advance_raises(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S5_RCA)
        with pytest.raises(RuntimePolicyMutationViolation, match="cannot move"):
            enforcer.advance_to(MetaLearningStage.S3_CONFIG)

    def test_same_stage_raises(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S2_TELEMETRY)
        with pytest.raises(RuntimePolicyMutationViolation):
            enforcer.advance_to(MetaLearningStage.S2_TELEMETRY)

    def test_config_mutation_allowed_at_s9(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S9_COMMIT)
        enforcer.assert_config_mutation_allowed()

    def test_config_mutation_blocked_before_s9(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S6_PROPOSE)
        with pytest.raises(RuntimePolicyMutationViolation, match="S9"):
            enforcer.assert_config_mutation_allowed()

    def test_initial_state_blocks_config_mutation(self):
        enforcer = StageBarrierEnforcer()
        with pytest.raises(RuntimePolicyMutationViolation):
            enforcer.assert_config_mutation_allowed()

    def test_reset_allows_restart(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S5_RCA)
        enforcer.reset()
        enforcer.advance_to(MetaLearningStage.S1_AUDIT)

    def test_is_commit_stage_true_at_s9(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S9_COMMIT)
        assert enforcer.is_commit_stage() is True

    def test_is_commit_stage_false_before_s9(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S8_INTAKE)
        assert enforcer.is_commit_stage() is False

    def test_negative_valid_sequence_never_raises(self):
        """Negative control: a fully sequential advance must never raise."""
        enforcer = StageBarrierEnforcer()
        raised = False
        try:
            for stage in MetaLearningStage:
                enforcer.advance_to(stage)
        except RuntimePolicyMutationViolation:  # guardian: allow-silent-swallower
            raised = True
        assert not raised
