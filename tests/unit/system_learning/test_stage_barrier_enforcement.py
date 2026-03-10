"""Addendum 5.1: Stage Barrier Enforcer tests."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation
from system_learning.engines.stage_barrier_enforcer import MetaLearningStage, StageBarrierEnforcer


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
