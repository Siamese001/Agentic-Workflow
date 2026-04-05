"""Addendum P0: Architectural invariant tests.

Tests for:
- boundary_validator (Addendum 1.2)
- ledger integrity_validator (Addendum 2.2)
- two_phase_coordinator (Addendum 2.3)
- c0_guard (Addendum 3.1, 3.2)
- stage_barrier_enforcer (Addendum 5.1)
- patch_validator (Addendum 6.1)
- human_review_queue (Gate C5)
- ai_check_audit (GAP-C)
"""

from __future__ import annotations

import pytest

# DEAD CODE: c0_guard.py was deleted - context folder removed
# from agentic_core.L0_routing.context.c0_guard import guard_c0_payload, verify_c0_immutability
from agentic_core.L2_execution.enforcement.boundary_validator import (
    compute_boundary_diff,
    verify_mutation_replay_integrity,
)
from agentic_core.L4_state.commit.two_phase_coordinator import TwoPhaseCoordinator
from agentic_core.L4_state.ledger.integrity_validator import append_with_hash, validate_ledger_chain
from agentic_core.L5_safety.audit.human_review_queue import HumanReviewQueue, PendingVerdict
from agentic_core.L5_safety.hitl.patch_validator import validate_patch
from agentic_core.L5_safety.types.hardening_errors import (
    C0AuthorityLeakError,
    C0MutationViolation,
    HumanPatchValidationError,
    MutationCommitFailure,
    RuntimePolicyMutationViolation,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_architectural_invariants")
# REMOVED: _emit_applies_guardrail("p0", "test_architectural_invariants", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_architectural_invariants", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_architectural_invariants", "state_snapshot")
from system_learning.engines.stage_barrier_enforcer import MetaLearningStage, StageBarrierEnforcer

# REMOVED: _emit_emits_metric_event("test_architectural_invariants", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_architectural_invariants", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_architectural_invariants", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_architectural_invariants", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_architectural_invariants", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_architectural_invariants", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_architectural_invariants", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_architectural_invariants", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_architectural_invariants", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_architectural_invariants", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_architectural_invariants", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_architectural_invariants", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_architectural_invariants", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_architectural_invariants", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_architectural_invariants", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_architectural_invariants", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_architectural_invariants", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_architectural_invariants", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_architectural_invariants", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_architectural_invariants", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_architectural_invariants", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_architectural_invariants", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_architectural_invariants", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_architectural_invariants", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_architectural_invariants", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_architectural_invariants", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_architectural_invariants", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_architectural_invariants", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_architectural_invariants", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_architectural_invariants", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_architectural_invariants", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_architectural_invariants", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_architectural_invariants", "write_through")
# REMOVED: _emit_writes_through("p1", "test_architectural_invariants", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_architectural_invariants", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_architectural_invariants", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_architectural_invariants", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_architectural_invariants", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_architectural_invariants", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_architectural_invariants", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_architectural_invariants", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_architectural_invariants", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_architectural_invariants", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_architectural_invariants", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_architectural_invariants", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_architectural_invariants", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_architectural_invariants", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_architectural_invariants", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_architectural_invariants")
# REMOVED: _emit_gated_by_confidence("p1", "test_architectural_invariants", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_architectural_invariants")
# REMOVED: emit_determinism_digest("p0", "test_architectural_invariants")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_architectural_invariants", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_architectural_invariants", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_architectural_invariants", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_architectural_invariants", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_architectural_invariants", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_architectural_invariants", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_architectural_invariants", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_architectural_invariants", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_architectural_invariants", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_architectural_invariants", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_architectural_invariants", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_architectural_invariants", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_architectural_invariants", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_architectural_invariants", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_architectural_invariants", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_architectural_invariants", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_architectural_invariants", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_architectural_invariants", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_architectural_invariants", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_architectural_invariants", "exec_snapshot_link")


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
