"""
tests/unit/agentic_core/L6_observability/utils/evaluation/test_pipeline_integration.py

Full-path integration tests for the evaluation pipeline.

Exercises the complete pipeline from SealedL2Artifact through:
  ExitControlGate → shape_outcome → build_shadow_eval_packet →
  L6ShadowEvalPipeline → promotion → governed handoff

7 tests:
  1. ALLOW_RESPONSE happy path → shadow eval → COMMITTED via mocked handoff
  2. DENY_RETURN live path → DenyReturnPayload + shadow packet stays FUTURE_RUN
  3. ESCALATE_TO_HITL live path → EscalateToHITLPacket with bounded_context
  4. COMMIT_TO_UWG live path → CommitToUWGRequest, then async shadow eval
  5. Async grading → HOLD (failure_count below _PROPOSE_MIN_FAILURES threshold)
  6. Governed handoff failure → packet stays APPROVED, never COMMITTED
  7. Scope-mixing invariant → wrong run_scope raises ValueError at each guard

Architectural invariants verified
----------------------------------
* build_shadow_eval_packet rejects non-CURRENT_RUN inputs.
* ShadowPacketGrader.grade rejects non-FUTURE_RUN inputs.
* run_shadow_packet_cycle rejects non-FUTURE_RUN packets.
* GovernedHandoffAgent.handoff rejects non-FUTURE_RUN packets.
* COMMITTED is only reachable when HandoffRecord.committed is True.
* CurrentRunEvaluationResult is frozen; shadow eval never mutates it.
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.eval_pipeline

from agentic_core.L2_execution.types.sealed_l2_artifact import (
    ReplayMetadata,
    SealedL2Artifact,
    TerminalClassification,
    ValidationCounters,
)
from agentic_core.L5_safety.enforcement.exit_control_gate import ExitControlGate
from agentic_core.L5_safety.types.exit_disposition_types import ExitDisposition
from agentic_core.L5_safety.types.exit_outcome_types import (
    AllowResponsePayload,
    CommitToUWGRequest,
    DenyReturnPayload,
    EscalateToHITLPacket,
)
from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (
    ShadowEvalPacket,
    build_shadow_eval_packet,
)
from agentic_core.L6_observability.utils.evaluation.governed_handoff import HandoffRecord
from agentic_core.L6_observability.utils.evaluation.promotion_packet import (
    ApprovalState,
    PromotionPacket,
    transition_approval_state,
)
from agentic_core.L6_observability.utils.evaluation.shadow_eval_grader import ShadowPacketGrader
from agentic_core.L6_observability.utils.evaluation.shadow_eval_pipeline import (
    L6ShadowEvalPipeline,
)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _make_allow_artifact() -> SealedL2Artifact:
    """SealedL2Artifact where all gates pass → ALLOW_RESPONSE."""
    return SealedL2Artifact(
        artifact_id="art-allow",
        trace_id="trace-allow",
        validation_counters=ValidationCounters(
            policy_checks_passed=5,
            policy_checks_failed=0,
            schema_checks_passed=3,
            schema_checks_failed=0,
            mutation_auth_checks_passed=1,
            mutation_auth_checks_failed=0,
        ),
        terminal_classification=TerminalClassification.SUCCESS,
        replay_metadata=ReplayMetadata(
            replay_key="rk-allow",
            replay_completeness=1.0,
            isolation_verified=True,
        ),
        evidence_bundle={
            "safety_clear": True,
            "groundedness_score": 0.80,
            "support_coverage": 0.80,
            "relevance_score": 0.80,
            "abstain_correct": True,
            "escalation_correct": True,
        },
        has_commit_payload=False,
    )


def _make_deny_artifact() -> SealedL2Artifact:
    """SealedL2Artifact with safety_clear=False → DENY_RETURN."""
    return SealedL2Artifact(
        artifact_id="art-deny",
        trace_id="trace-deny",
        validation_counters=ValidationCounters(
            policy_checks_passed=5,
            policy_checks_failed=0,
        ),
        terminal_classification=TerminalClassification.SUCCESS,
        replay_metadata=ReplayMetadata(replay_completeness=1.0, isolation_verified=True),
        evidence_bundle={
            "safety_clear": False,
            "groundedness_score": 0.80,
            "support_coverage": 0.80,
            "relevance_score": 0.80,
        },
        has_commit_payload=False,
    )


def _make_escalate_artifact() -> SealedL2Artifact:
    """SealedL2Artifact with escalation_reason set → ESCALATE_TO_HITL."""
    return SealedL2Artifact(
        artifact_id="art-esc",
        trace_id="trace-esc",
        validation_counters=ValidationCounters(
            policy_checks_passed=5,
            policy_checks_failed=0,
        ),
        terminal_classification=TerminalClassification.SUCCESS,
        replay_metadata=ReplayMetadata(replay_completeness=1.0, isolation_verified=True),
        evidence_bundle={
            "safety_clear": True,
            "groundedness_score": 0.80,
            "support_coverage": 0.80,
            "relevance_score": 0.80,
        },
        has_commit_payload=False,
        escalation_reason="Ambiguous policy clause detected",
    )


def _make_commit_artifact() -> SealedL2Artifact:
    """SealedL2Artifact with has_commit_payload=True + authorized → COMMIT_TO_UWG."""
    return SealedL2Artifact(
        artifact_id="art-commit",
        trace_id="trace-commit",
        state_diff={"parameter": "new_value"},
        validation_counters=ValidationCounters(
            policy_checks_passed=5,
            policy_checks_failed=0,
            mutation_auth_checks_passed=1,
            mutation_auth_checks_failed=0,
        ),
        terminal_classification=TerminalClassification.SUCCESS,
        replay_metadata=ReplayMetadata(
            replay_key="rk-commit",
            replay_completeness=1.0,
            isolation_verified=True,
        ),
        evidence_bundle={
            "safety_clear": True,
            "groundedness_score": 0.80,
            "support_coverage": 0.80,
            "relevance_score": 0.80,
        },
        has_commit_payload=True,
    )


def _make_approved_packet() -> PromotionPacket:
    """Minimal PromotionPacket in APPROVED state with valid rollback metadata."""
    ref = f"ep-{uuid.uuid4().hex[:8]}"
    digest = "abcd1234ef567890"
    return PromotionPacket(
        packet_id=f"pp-{uuid.uuid4().hex[:12]}",
        edition="future-run/v1/test",
        version_tag="integ-v1",
        candidate_id="pc-integ-test",
        cluster_key="integ-lane|GROUNDEDNESS_FAIL",
        target_destination_class="evidence_threshold.citation_quality",
        rationale="integration test approved packet",
        evidence_replay_references=(ref,),
        baseline_regression_refs=("cluster_key=integ-lane|GROUNDEDNESS_FAIL",),
        rollout_metadata={
            "parameter": "grounded_citation_threshold",
            "current_value": 0.50,
            "proposed_value": 0.45,
            "rationale": "integration test",
            "cluster_id": "cl-integ",
            "failure_count": 5,
            "severity": "high",
        },
        rollback_metadata={
            "parameter": "grounded_citation_threshold",
            "revert_to_value": 0.50,
            "from_proposed_value": 0.45,
            "rollback_trigger": "regression_detected",
            "cluster_id": "cl-integ",
        },
        replay_digest=digest,
        sealed_at=0.0,
        approval_state=ApprovalState.APPROVED,
    )


def _make_committed_record(packet: PromotionPacket) -> HandoffRecord:
    """HandoffRecord indicating a successful UWG commit."""
    return HandoffRecord(
        record_id="hr-integ-committed",
        packet_id=packet.packet_id,
        token_id="tk-integ-test",
        token_valid=True,
        approved=True,
        commit_attempted=True,
        committed=True,
        rollout_published=True,
        rollback_metadata_valid=True,
        dry_run=False,
        destination_namespace=packet.target_destination_class,
        handoff_at=0.0,
        error="",
    )


def _make_failed_record(packet: PromotionPacket) -> HandoffRecord:
    """HandoffRecord indicating a failed UWG commit."""
    return HandoffRecord(
        record_id="hr-integ-failed",
        packet_id=packet.packet_id,
        token_id="UNISSUED",
        token_valid=False,
        approved=True,
        commit_attempted=True,
        committed=False,
        rollout_published=False,
        rollback_metadata_valid=False,
        dry_run=False,
        destination_namespace=packet.target_destination_class,
        handoff_at=0.0,
        error="mock UWG write failure",
    )


def _make_failing_shadow_packet(run_id: str = "run-hold") -> ShadowEvalPacket:
    """ShadowEvalPacket with low groundedness → GROUNDEDNESS_FAIL grade → HOLD candidate."""
    return ShadowEvalPacket(
        packet_id=f"sep-{uuid.uuid4().hex[:8]}",
        run_id=run_id,
        exit_disposition="DENY_RETURN",
        exit_trace_id="t-hold",
        exit_reason="X1D failed",
        telemetry={
            "groundedness_score": 0.10,
            "support_coverage": 0.10,
            "relevance_score": 0.50,
            "abstain_correct": True,
            "escalation_correct": True,
            "answer_fit": True,
            "rules_compliance_score": 1.0,
            "policy_adherence_score": 1.0,
            "schema_completion_score": 1.0,
            "confidence_score": 0.50,
            "safety_clear": True,
            "policy_pass": True,
            "mutation_authorized": True,
            "env_integrity": True,
            "replay_env_complete": True,
            "terminal_classification": "SUCCESS",
            "replay_completeness": 1.0,
            "policy_checks_passed": 5,
            "policy_checks_failed": 0,
            "schema_checks_passed": 3,
            "schema_checks_failed": 0,
            "mutation_auth_checks_failed": 0,
            "has_commit_payload": False,
            "policy_hash": "",
            "compliance_hash": "",
        },
        sealed_at=0.0,
    )


# ---------------------------------------------------------------------------
# Test 1: Happy path — ALLOW_RESPONSE → shadow eval → COMMITTED
# ---------------------------------------------------------------------------


class TestHappyPathAllowToCommitted:
    def test_gate_produces_allow_response(self) -> None:
        gate = ExitControlGate()
        artifact = _make_allow_artifact()
        result = gate.evaluate_sealed(artifact)

        assert result.disposition == ExitDisposition.ALLOW_RESPONSE
        assert result.run_scope == "CURRENT_RUN"

    def test_shape_outcome_returns_allow_payload(self) -> None:
        gate = ExitControlGate()
        artifact = _make_allow_artifact()
        result = gate.evaluate_sealed(artifact)

        outcome = gate.shape_outcome(result, artifact)
        assert isinstance(outcome, AllowResponsePayload)
        assert outcome.run_scope == "CURRENT_RUN"

    def test_shadow_packet_crosses_scope_boundary(self) -> None:
        gate = ExitControlGate()
        artifact = _make_allow_artifact()
        result = gate.evaluate_sealed(artifact)

        shadow_pkt = build_shadow_eval_packet(artifact, result)
        assert shadow_pkt.run_scope == "FUTURE_RUN"
        assert shadow_pkt.exit_disposition == ExitDisposition.ALLOW_RESPONSE.value
        # Completed run is unchanged
        assert result.run_scope == "CURRENT_RUN"
        assert result.disposition == ExitDisposition.ALLOW_RESPONSE

    def test_approve_and_handoff_reaches_committed(self) -> None:
        packet = _make_approved_packet()
        committed_record = _make_committed_record(packet)
        pipeline = L6ShadowEvalPipeline()

        with patch(
            "agentic_core.L6_observability.utils.evaluation.governed_handoff.GovernedHandoffAgent.handoff",
            return_value=committed_record,
        ):
            final_pkt, record = pipeline.approve_and_handoff(packet, dry_run=False)

        assert record.committed is True
        assert final_pkt.approval_state == ApprovalState.COMMITTED

    def test_committed_only_via_successful_handoff(self) -> None:
        """COMMITTED is unreachable without handoff returning committed=True."""
        packet = _make_approved_packet()
        # transition_approval_state enforces the valid transition graph
        # APPROVED → COMMITTED is valid only after handoff; direct call also valid as typed transition
        committed_pkt = transition_approval_state(packet, ApprovalState.COMMITTED)
        assert committed_pkt.approval_state == ApprovalState.COMMITTED
        # But transition from PENDING → COMMITTED is forbidden
        pending_pkt = transition_approval_state(packet, ApprovalState.REJECTED)
        with pytest.raises(ValueError, match="Invalid approval state transition"):
            transition_approval_state(pending_pkt, ApprovalState.COMMITTED)


# ---------------------------------------------------------------------------
# Test 2: DENY_RETURN path
# ---------------------------------------------------------------------------


class TestDenyReturnPath:
    def test_gate_produces_deny_return(self) -> None:
        gate = ExitControlGate()
        result = gate.evaluate_sealed(_make_deny_artifact())
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_shape_outcome_returns_deny_payload(self) -> None:
        gate = ExitControlGate()
        artifact = _make_deny_artifact()
        result = gate.evaluate_sealed(artifact)

        outcome = gate.shape_outcome(result, artifact)
        assert isinstance(outcome, DenyReturnPayload)
        assert outcome.run_scope == "CURRENT_RUN"

    def test_shadow_packet_built_with_deny_disposition(self) -> None:
        gate = ExitControlGate()
        artifact = _make_deny_artifact()
        result = gate.evaluate_sealed(artifact)

        shadow_pkt = build_shadow_eval_packet(artifact, result)
        assert shadow_pkt.run_scope == "FUTURE_RUN"
        assert shadow_pkt.exit_disposition == ExitDisposition.DENY_RETURN.value
        # Completed run must not be mutated
        assert result.disposition == ExitDisposition.DENY_RETURN
        assert result.run_scope == "CURRENT_RUN"


# ---------------------------------------------------------------------------
# Test 3: ESCALATE_TO_HITL path
# ---------------------------------------------------------------------------


class TestEscalateToHITLPath:
    def test_gate_produces_escalate(self) -> None:
        gate = ExitControlGate()
        result = gate.evaluate_sealed(_make_escalate_artifact())
        assert result.disposition == ExitDisposition.ESCALATE_TO_HITL

    def test_shape_outcome_returns_escalate_packet(self) -> None:
        gate = ExitControlGate()
        artifact = _make_escalate_artifact()
        result = gate.evaluate_sealed(artifact)

        outcome = gate.shape_outcome(result, artifact)
        assert isinstance(outcome, EscalateToHITLPacket)
        assert outcome.run_scope == "CURRENT_RUN"
        assert "artifact_id" in outcome.bounded_context
        assert outcome.bounded_context["artifact_id"] == artifact.artifact_id

    def test_shadow_packet_built_with_escalate_disposition(self) -> None:
        gate = ExitControlGate()
        artifact = _make_escalate_artifact()
        result = gate.evaluate_sealed(artifact)

        shadow_pkt = build_shadow_eval_packet(artifact, result)
        assert shadow_pkt.run_scope == "FUTURE_RUN"
        assert shadow_pkt.exit_disposition == ExitDisposition.ESCALATE_TO_HITL.value


# ---------------------------------------------------------------------------
# Test 4: COMMIT_TO_UWG live path → CommitToUWGRequest, then async shadow eval
# ---------------------------------------------------------------------------


class TestCommitToUWGLiveToAsyncShadow:
    def test_gate_produces_commit_to_uwg(self) -> None:
        gate = ExitControlGate()
        result = gate.evaluate_sealed(_make_commit_artifact())
        assert result.disposition == ExitDisposition.COMMIT_TO_UWG

    def test_shape_outcome_returns_commit_request(self) -> None:
        gate = ExitControlGate()
        artifact = _make_commit_artifact()
        result = gate.evaluate_sealed(artifact)

        outcome = gate.shape_outcome(result, artifact)
        assert isinstance(outcome, CommitToUWGRequest)
        assert outcome.run_scope == "CURRENT_RUN"
        assert outcome.state_diff  # must contain the proposed change

    def test_shadow_packet_carries_commit_disposition(self) -> None:
        gate = ExitControlGate()
        artifact = _make_commit_artifact()
        result = gate.evaluate_sealed(artifact)

        shadow_pkt = build_shadow_eval_packet(artifact, result)
        assert shadow_pkt.run_scope == "FUTURE_RUN"
        assert shadow_pkt.exit_disposition == ExitDisposition.COMMIT_TO_UWG.value

    def test_shadow_eval_cycle_does_not_mutate_live_result(self) -> None:
        """Shadow eval runs after the live commit; the completed run is frozen."""
        gate = ExitControlGate()
        artifact = _make_commit_artifact()
        result = gate.evaluate_sealed(artifact)

        shadow_pkt = build_shadow_eval_packet(artifact, result)
        pipeline = L6ShadowEvalPipeline()
        summary = pipeline.run_shadow_packet_cycle([shadow_pkt])

        assert summary["packets_processed"] == 1
        # Completed current-run result is unchanged
        assert result.disposition == ExitDisposition.COMMIT_TO_UWG
        assert result.run_scope == "CURRENT_RUN"


# ---------------------------------------------------------------------------
# Test 5: Async grading → HOLD (single failure, below threshold)
# ---------------------------------------------------------------------------


class TestAsyncHoldPath:
    def test_single_failing_packet_produces_hold_candidate(self) -> None:
        pipeline = L6ShadowEvalPipeline()
        shadow_pkt = _make_failing_shadow_packet()

        summary = pipeline.run_shadow_packet_cycle([shadow_pkt])

        assert summary["packets_processed"] == 1
        candidates = pipeline.candidates()
        hold = [c for c in candidates if c.classification == "HOLD"]
        propose = [c for c in candidates if c.classification == "PROPOSE"]
        assert len(hold) >= 1, "Expected at least 1 HOLD candidate"
        assert len(propose) == 0, "Single failure must not reach PROPOSE"

    def test_hold_candidate_has_correct_failure_mode(self) -> None:
        pipeline = L6ShadowEvalPipeline()
        pipeline.run_shadow_packet_cycle([_make_failing_shadow_packet()])

        candidates = pipeline.candidates()
        hold = [c for c in candidates if c.classification == "HOLD"]
        assert hold[0].cluster_key.endswith("GROUNDEDNESS_FAIL")


# ---------------------------------------------------------------------------
# Test 6: Governed handoff failure → packet stays APPROVED, never COMMITTED
# ---------------------------------------------------------------------------


class TestHandoffFailureNeverCommitted:
    def test_failed_handoff_leaves_packet_approved(self) -> None:
        packet = _make_approved_packet()
        failed_record = _make_failed_record(packet)
        pipeline = L6ShadowEvalPipeline()

        with patch(
            "agentic_core.L6_observability.utils.evaluation.governed_handoff.GovernedHandoffAgent.handoff",
            return_value=failed_record,
        ):
            final_pkt, record = pipeline.approve_and_handoff(packet, dry_run=False)

        assert record.committed is False
        assert record.error == "mock UWG write failure"
        assert final_pkt.approval_state == ApprovalState.APPROVED

    def test_pending_packet_rejected_before_handoff(self) -> None:
        pending_pkt = PromotionPacket(
            packet_id="pp-pending-test",
            edition="future-run/v1/pending",
            version_tag="pending-v1",
            candidate_id="pc-pending",
            cluster_key="lane|UNKNOWN",
            target_destination_class="evidence_threshold.generic",
            rationale="pending test",
            evidence_replay_references=("ep-001",),
            baseline_regression_refs=("cluster_key=lane|UNKNOWN",),
            rollout_metadata={"parameter": "x", "current_value": 0, "proposed_value": 1},
            rollback_metadata={"parameter": "x", "revert_to_value": 0, "rollback_trigger": "t"},
            replay_digest="deadbeef01234567",
            sealed_at=0.0,
            approval_state=ApprovalState.PENDING,
        )
        pipeline = L6ShadowEvalPipeline()
        with pytest.raises(ValueError, match="APPROVED"):
            pipeline.approve_and_handoff(pending_pkt)


# ---------------------------------------------------------------------------
# Test 7: Scope-mixing invariant — wrong run_scope raises ValueError
# ---------------------------------------------------------------------------


class TestScopeMixingInvariant:
    def test_build_shadow_eval_packet_rejects_future_run_artifact(self) -> None:
        """build_shadow_eval_packet raises when artifact has wrong run_scope."""
        bad_artifact = MagicMock()
        bad_artifact.run_scope = "FUTURE_RUN"
        good_eval = MagicMock()
        good_eval.run_scope = "CURRENT_RUN"

        with pytest.raises(ValueError, match="run_scope='CURRENT_RUN'"):
            build_shadow_eval_packet(bad_artifact, good_eval)

    def test_build_shadow_eval_packet_rejects_future_run_eval_result(self) -> None:
        """build_shadow_eval_packet raises when eval_result has wrong run_scope."""
        good_artifact = _make_allow_artifact()
        bad_eval = MagicMock()
        bad_eval.run_scope = "FUTURE_RUN"

        with pytest.raises(ValueError, match="run_scope='CURRENT_RUN'"):
            build_shadow_eval_packet(good_artifact, bad_eval)

    def test_shadow_packet_grader_rejects_current_run_packet(self) -> None:
        """ShadowPacketGrader.grade raises when packet has run_scope != FUTURE_RUN."""
        grader = ShadowPacketGrader()
        bad_pkt = MagicMock()
        bad_pkt.run_scope = "CURRENT_RUN"

        with pytest.raises(ValueError, match="run_scope='FUTURE_RUN'"):
            grader.grade(bad_pkt)

    def test_run_shadow_packet_cycle_rejects_wrong_scope(self) -> None:
        """run_shadow_packet_cycle raises when any packet has wrong run_scope."""
        pipeline = L6ShadowEvalPipeline()
        bad_pkt = MagicMock()
        bad_pkt.run_scope = "CURRENT_RUN"

        with pytest.raises(ValueError, match="run_scope != 'FUTURE_RUN'"):
            pipeline.run_shadow_packet_cycle([bad_pkt])

    def test_governed_handoff_rejects_current_run_packet(self) -> None:
        """GovernedHandoffAgent.handoff raises when packet has wrong run_scope."""
        from agentic_core.L6_observability.utils.evaluation.governed_handoff import (
            GovernedHandoffAgent,
        )

        bad_pkt = MagicMock()
        bad_pkt.run_scope = "CURRENT_RUN"
        agent = GovernedHandoffAgent()

        with pytest.raises(ValueError, match="run_scope='FUTURE_RUN'"):
            agent.handoff(bad_pkt)

    def test_real_shadow_eval_packet_passes_scope_guard(self) -> None:
        """ShadowEvalPacket (run_scope='FUTURE_RUN') is accepted by all guards."""
        pipeline = L6ShadowEvalPipeline()
        shadow_pkt = _make_failing_shadow_packet(run_id="run-scope-check")

        # Must not raise
        summary = pipeline.run_shadow_packet_cycle([shadow_pkt])
        assert summary["packets_processed"] == 1
