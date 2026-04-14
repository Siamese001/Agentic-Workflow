"""Addendum P0: Architectural invariant tests."""

from __future__ import annotations

import pytest

_human_review_queue = pytest.importorskip(
    "agentic_core.L5_safety.audit.human_review_queue",
    reason="Requires architectural invariant dependencies from the monorepo checkout.",
)
HumanReviewQueue = _human_review_queue.HumanReviewQueue
PendingVerdict = _human_review_queue.PendingVerdict

_boundary_validator = pytest.importorskip(
    "agentic_core.L2_execution.enforcement.boundary_validator",
    reason="Requires boundary validator from the monorepo checkout.",
)
compute_boundary_diff = _boundary_validator.compute_boundary_diff
verify_mutation_replay_integrity = _boundary_validator.verify_mutation_replay_integrity

_two_phase = pytest.importorskip(
    "agentic_core.L4_state.utils.commit.two_phase_coordinator",
    reason="Requires two-phase coordinator from the monorepo checkout.",
)
TwoPhaseCoordinator = _two_phase.TwoPhaseCoordinator

_ledger = pytest.importorskip(
    "agentic_core.L4_state.utils.ledger.integrity_validator",
    reason="Requires ledger integrity validator from the monorepo checkout.",
)
append_with_hash = _ledger.append_with_hash
validate_ledger_chain = _ledger.validate_ledger_chain

_patch_validator = pytest.importorskip(
    "agentic_core.L5_safety.enforcement.hitl.patch_validator",
    reason="Requires patch validator from the monorepo checkout.",
)
validate_patch = _patch_validator.validate_patch

_hardening_errors = pytest.importorskip(
    "agentic_core.L5_safety.types.hardening_errors",
    reason="Requires hardening error types from the monorepo checkout.",
)
HumanPatchValidationError = _hardening_errors.HumanPatchValidationError
MutationCommitFailure = _hardening_errors.MutationCommitFailure
RuntimePolicyMutationViolation = _hardening_errors.RuntimePolicyMutationViolation

_stage_barrier = pytest.importorskip(
    "system_learning.engines.stage_barrier_enforcer",
    reason="Requires system_learning stage barrier enforcer from the monorepo checkout.",
)
MetaLearningStage = _stage_barrier.MetaLearningStage
StageBarrierEnforcer = _stage_barrier.StageBarrierEnforcer


class TestBoundaryValidator:
    def test_matching_diffs_pass(self):
        pre = {"file_a": "v1", "file_b": "v2"}
        post = {"file_a": "v1_updated", "file_b": "v2"}
        uwg_diff = compute_boundary_diff(pre, post)
        verify_mutation_replay_integrity(pre, post, uwg_diff)

    def test_mismatched_diffs_raise(self):
        from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation

        pre = {"file_a": "v1"}
        post = {"file_a": "v1_updated"}
        fake_uwg_diff = {"file_a": {"pre": "v1", "post": "DIFFERENT"}}
        with pytest.raises(MutationReplayIntegrityViolation, match="hash mismatch"):
            verify_mutation_replay_integrity(pre, post, fake_uwg_diff)


class TestLedgerIntegrityValidator:
    def test_valid_chain_passes(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "foo.py"})
        append_with_hash(entries, {"op": "delete", "file": "bar.py"})
        validate_ledger_chain(entries)

    def test_tampered_hash_raises(self):
        from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation

        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "foo.py"})
        entries[0]["_hash"] = "tampered0000000000000000000000000000000000000000000000000000000000"
        with pytest.raises(LedgerIntegrityViolation, match="hash mismatch"):
            validate_ledger_chain(entries)

    def test_missing_hash_raises(self):
        from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation

        entries = [{"op": "write", "file": "foo.py"}]
        with pytest.raises(LedgerIntegrityViolation, match="missing '_hash'"):
            validate_ledger_chain(entries)


class TestTwoPhaseCoordinator:
    def test_both_acks_succeed(self):
        coordinator = TwoPhaseCoordinator()
        r_calls = []
        l_calls = []
        r, l = coordinator.execute_commit(
            resource_write=lambda: r_calls.append(1) or "ok",
            ledger_write=lambda: l_calls.append(1) or "ok",
        )
        assert r == "ok"
        assert l == "ok"
        assert len(r_calls) == 1
        assert len(l_calls) == 1

    def test_resource_failure_aborts(self):
        coordinator = TwoPhaseCoordinator()
        with pytest.raises(MutationCommitFailure, match="Phase 1"):
            coordinator.execute_commit(
                resource_write=lambda: (_ for _ in ()).throw(RuntimeError("disk full")),
                ledger_write=lambda: "ok",
            )

    def test_ledger_failure_aborts(self):
        coordinator = TwoPhaseCoordinator()
        with pytest.raises(MutationCommitFailure, match="Phase 2"):
            coordinator.execute_commit(
                resource_write=lambda: "ok",
                ledger_write=lambda: (_ for _ in ()).throw(RuntimeError("ledger locked")),
            )


# DEAD CODE: TestC0Guard class removed - c0_guard.py was deleted
# class TestC0Guard:
#     def test_safe_payload_passes(self):
#         guard_c0_payload({"query": "hello", "context": "software"})
#
#     def test_authority_field_raises(self):
#         with pytest.raises(C0AuthorityLeakError, match="auth_token"):
#             guard_c0_payload({"query": "hello", "auth_token": "bearer 123"})
#
#     def test_immutability_passes_when_equal(self):
#         payload = {"key": "value"}
#         verify_c0_immutability(payload, {"key": "value"})
#
#     def test_immutability_raises_on_mutation(self):
#         with pytest.raises(C0MutationViolation, match="mutated"):
#             verify_c0_immutability({"key": "original"}, {"key": "modified"})


class TestStageBarrierEnforcer:
    def test_sequential_advance_passes(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S1_AUDIT)
        enforcer.advance_to(MetaLearningStage.S9_COMMIT)
        enforcer.assert_config_mutation_allowed()

    def test_backwards_advance_raises(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S5_RCA)
        with pytest.raises(RuntimePolicyMutationViolation, match="cannot move"):
            enforcer.advance_to(MetaLearningStage.S3_CONFIG)

    def test_config_mutation_before_s9_raises(self):
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S6_PROPOSE)
        with pytest.raises(RuntimePolicyMutationViolation, match="S9"):
            enforcer.assert_config_mutation_allowed()


class TestPatchValidator:
    def test_valid_patch_passes(self):
        patch = {
            "original_plan_hash": "abc123",
            "structured_patch_schema": {"type": "MODIFY_DIFF", "file": "foo.py"},
            "reviewer_signature": "reviewer@example.com",
        }
        result = validate_patch(patch)
        assert result.reviewer_signature == "reviewer@example.com"
        assert result.patch_hash

    def test_missing_field_raises(self):
        with pytest.raises(HumanPatchValidationError, match="reviewer_signature"):
            validate_patch({"original_plan_hash": "abc", "structured_patch_schema": {}})


class TestHumanReviewQueue:
    def test_enqueue_and_approve(self):
        q = HumanReviewQueue()
        verdict = PendingVerdict(
            verdict_id="v001",
            component="JudgeEvaluator",
            trace_id="t001",
            confidence=0.4,
            verdict="PASS",
            input_hash="abc",
        )
        q.enqueue(verdict)
        assert q.is_blocked("v001")
        assert q.pending_count() == 1
        q.approve("v001", "looks good")
        assert q.is_approved("v001")
        assert q.pending_count() == 0

    def test_reject(self):
        q = HumanReviewQueue()
        q.enqueue(PendingVerdict("v002", "Comp", "t002", 0.3, "FAIL", "xyz"))
        q.reject("v002", "bad verdict")
        assert not q.is_approved("v002")
        assert not q.is_blocked("v002")
