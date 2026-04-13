"""
tests/unit/agentic_core/L6_observability/utils/evaluation/test_promotion_approval_slice.py

End-to-end tests for the final future-run promotion slice:

  sealed L2 artifact
    → current-run evaluation (ExitControlGate / CurrentRunEvaluationResult)
    → build_shadow_eval_packet()
    → ShadowPacketGrader / RcaAggregator / PromotionStager
    → packetize_pending() → PENDING PromotionPacket
    → transition_approval_state() → APPROVED / REJECTED
    → approve_and_handoff() → HandoffRecord + optional COMMITTED

Architectural invariants verified
----------------------------------
* COMMITTED state only reachable after HandoffRecord.committed is True.
* No direct L6 write to L4 — GovernedHandoffAgent is the only commit seam.
* No completed-run mutation — CurrentRunEvaluationResult is frozen/unchanged.
* Invalid state transitions raise ValueError deterministically.
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
from agentic_core.L5_safety.types.exit_disposition_types import (
    CurrentRunEvaluationResult,
    ExitDisposition,
    IntegrityChecks,
    QualityChecks,
    RubricScores,
)
from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (
    build_shadow_eval_packet,
)
from agentic_core.L6_observability.utils.evaluation.promotion_packet import (
    ApprovalState,
    PromotionPacket,
    PromotionPacketizer,
    transition_approval_state,
)
from agentic_core.L6_observability.utils.evaluation.promotion_stager import (
    PromotionStager,
)
from agentic_core.L6_observability.utils.evaluation.rca_aggregator import (
    RcaCluster,
)
from agentic_core.L6_observability.utils.evaluation.shadow_eval_pipeline import (
    L6ShadowEvalPipeline,
)

# ── Test helpers ─────────────────────────────────────────────────────────────


def _make_artifact(
    *,
    artifact_id: str = "art-test",
    trace_id: str = "trace-test",
    actor: str = "test-agent",
    policy_hash: str = "ph-abc123",
) -> SealedL2Artifact:
    return SealedL2Artifact(
        artifact_id=artifact_id,
        trace_id=trace_id,
        exec_trace={"actor": actor, "policy_hash": policy_hash},
        validation_counters=ValidationCounters(
            policy_checks_passed=5,
            schema_checks_passed=3,
        ),
        terminal_classification=TerminalClassification.SUCCESS,
        replay_metadata=ReplayMetadata(replay_completeness=1.0, isolation_verified=True),
    )


def _make_eval_result(
    artifact: SealedL2Artifact,
    *,
    eval_id: str = "eval-test",
    disposition: ExitDisposition = ExitDisposition.ALLOW_RESPONSE,
    escalation_correct: bool = True,
    abstain_correct: bool = True,
    groundedness_score: float = 0.85,
    support_coverage: float = 0.75,
) -> CurrentRunEvaluationResult:
    return CurrentRunEvaluationResult(
        eval_id=eval_id,
        artifact_id=artifact.artifact_id,
        trace_id=artifact.trace_id,
        disposition=disposition,
        confidence_score=0.90,
        rubric_scores=RubricScores(
            rules_compliance_score=1.0,
            policy_adherence_score=1.0,
            schema_completion_score=1.0,
        ),
        quality_checks=QualityChecks(
            answer_fit=True,
            groundedness_score=groundedness_score,
            support_coverage=support_coverage,
            relevance_score=0.9,
            abstain_correct=abstain_correct,
            escalation_correct=escalation_correct,
        ),
        integrity_checks=IntegrityChecks(
            safety_clear=True,
            policy_pass=True,
            mutation_authorized=True,
            env_integrity=True,
            replay_env_complete=True,
        ),
        disposition_reason="Test eval",
        policy_hash="ph-abc123",
    )


def _make_pending_packet(*, failure_count: int = 4, failure_mode: str = "ABSTAIN_MISSED") -> PromotionPacket:
    """Build a PENDING PromotionPacket via the real stager path."""
    cluster = RcaCluster(
        cluster_id=f"rca-{uuid.uuid4().hex[:8]}",
        cluster_key=f"test-lane|{failure_mode}",
        lane_id="test-lane",
        failure_mode=failure_mode,
        failure_count=failure_count,
        sample_packet_ids=[f"p{i}" for i in range(min(failure_count, 5))],
        collections_affected=["col-a"],
        avg_support_coverage=0.25,
        avg_citation_completeness=0.40,
        avg_exact_match_drift=0.05,
        severity="medium" if failure_count < 5 else "high",
        rca_summary="Test RCA summary",
        first_seen_at=1000.0,
        last_seen_at=1002.0,
    )
    candidate = PromotionStager().stage(cluster)
    return PromotionPacketizer().packetize_pending(candidate, cluster)


# ── TestApprovalStateTransitions ─────────────────────────────────────────────


class TestApprovalStateTransitions:
    """Unit tests for transition_approval_state()."""

    def test_pending_to_approved(self):
        packet = _make_pending_packet()
        assert packet.approval_state == ApprovalState.PENDING

        approved = transition_approval_state(packet, ApprovalState.APPROVED)

        assert approved.approval_state == ApprovalState.APPROVED
        assert approved.packet_id == packet.packet_id
        assert approved.cluster_key == packet.cluster_key
        assert approved.rollback_metadata == packet.rollback_metadata

    def test_pending_to_rejected(self):
        packet = _make_pending_packet()

        rejected = transition_approval_state(packet, ApprovalState.REJECTED)

        assert rejected.approval_state == ApprovalState.REJECTED
        assert rejected.packet_id == packet.packet_id

    def test_approved_to_committed(self):
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)

        committed = transition_approval_state(approved, ApprovalState.COMMITTED)

        assert committed.approval_state == ApprovalState.COMMITTED
        assert committed.packet_id == packet.packet_id

    def test_approved_to_rejected(self):
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)

        rejected = transition_approval_state(approved, ApprovalState.REJECTED)

        assert rejected.approval_state == ApprovalState.REJECTED

    def test_transition_preserves_all_fields(self):
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)

        assert approved.edition == packet.edition
        assert approved.version_tag == packet.version_tag
        assert approved.candidate_id == packet.candidate_id
        assert approved.target_destination_class == packet.target_destination_class
        assert approved.rationale == packet.rationale
        assert approved.evidence_replay_references == packet.evidence_replay_references
        assert approved.baseline_regression_refs == packet.baseline_regression_refs
        assert approved.rollout_metadata == packet.rollout_metadata
        assert approved.rollback_metadata == packet.rollback_metadata
        assert approved.replay_digest == packet.replay_digest
        assert approved.sealed_at == packet.sealed_at

    def test_invalid_pending_to_committed(self):
        packet = _make_pending_packet()

        with pytest.raises(ValueError, match="PENDING.*COMMITTED"):
            transition_approval_state(packet, ApprovalState.COMMITTED)

    def test_invalid_committed_to_pending(self):
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)
        committed = transition_approval_state(approved, ApprovalState.COMMITTED)

        with pytest.raises(ValueError, match="COMMITTED.*PENDING"):
            transition_approval_state(committed, ApprovalState.PENDING)

    def test_invalid_rejected_to_approved(self):
        packet = _make_pending_packet()
        rejected = transition_approval_state(packet, ApprovalState.REJECTED)

        with pytest.raises(ValueError, match="REJECTED.*APPROVED"):
            transition_approval_state(rejected, ApprovalState.APPROVED)

    def test_invalid_committed_to_approved(self):
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)
        committed = transition_approval_state(approved, ApprovalState.COMMITTED)

        with pytest.raises(ValueError):
            transition_approval_state(committed, ApprovalState.APPROVED)

    def test_transition_returns_new_instance(self):
        """transition_approval_state must return a new object, not mutate in place."""
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)

        assert approved is not packet
        assert packet.approval_state == ApprovalState.PENDING


# ── TestApproveAndHandoff ─────────────────────────────────────────────────────


class TestApproveAndHandoff:
    """Tests for L6ShadowEvalPipeline.approve_and_handoff()."""

    def test_dry_run_issues_token_no_commit(self):
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)

        pipeline = L6ShadowEvalPipeline()
        final_packet, record = pipeline.approve_and_handoff(approved, dry_run=True)

        assert record.dry_run is True
        assert record.committed is False
        assert record.token_id != "UNISSUED"
        assert record.token_valid is True
        assert record.packet_id == packet.packet_id
        assert final_packet.approval_state == ApprovalState.APPROVED

    def test_committed_state_reachable_only_via_successful_handoff(self):
        """COMMITTED is set only when HandoffRecord.committed is True."""
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)
        pipeline = L6ShadowEvalPipeline()

        mock_record = MagicMock()
        mock_record.committed = True
        mock_record.dry_run = False
        mock_record.token_id = "tok-abc"
        mock_record.token_valid = True
        mock_record.packet_id = packet.packet_id

        with patch(
            "agentic_core.L6_observability.utils.evaluation.governed_handoff.GovernedHandoffAgent.handoff",
            return_value=mock_record,
        ):
            final_packet, record = pipeline.approve_and_handoff(approved, dry_run=False)

        assert record.committed is True
        assert final_packet.approval_state == ApprovalState.COMMITTED

    def test_handoff_failure_keeps_approved_state(self):
        """If handoff does not commit, packet stays APPROVED."""
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)
        pipeline = L6ShadowEvalPipeline()

        mock_record = MagicMock()
        mock_record.committed = False
        mock_record.error = "PromotionAuthority unavailable"

        with patch(
            "agentic_core.L6_observability.utils.evaluation.governed_handoff.GovernedHandoffAgent.handoff",
            return_value=mock_record,
        ):
            final_packet, record = pipeline.approve_and_handoff(approved, dry_run=False)

        assert record.committed is False
        assert final_packet.approval_state == ApprovalState.APPROVED

    def test_approve_and_handoff_rejects_pending_packet(self):
        """Passing a PENDING packet raises ValueError — must be APPROVED first."""
        packet = _make_pending_packet()
        pipeline = L6ShadowEvalPipeline()

        with pytest.raises(ValueError, match="approval_state=APPROVED"):
            pipeline.approve_and_handoff(packet, dry_run=True)

    def test_approve_and_handoff_rejects_rejected_packet(self):
        packet = _make_pending_packet()
        rejected = transition_approval_state(packet, ApprovalState.REJECTED)
        pipeline = L6ShadowEvalPipeline()

        with pytest.raises(ValueError, match="approval_state=APPROVED"):
            pipeline.approve_and_handoff(rejected, dry_run=True)

    def test_dry_run_rollout_published_on_bus_t(self):
        """Dry-run handoff publishes a PROMOTION_ROLLOUT signal on BUS T."""
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)
        pipeline = L6ShadowEvalPipeline()

        _, record = pipeline.approve_and_handoff(approved, dry_run=True)

        assert record.rollout_published is True

    def test_handoff_preserves_packet_lineage(self):
        """HandoffRecord links back to the original packet_id and destination."""
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)
        pipeline = L6ShadowEvalPipeline()

        _, record = pipeline.approve_and_handoff(approved, dry_run=True)

        assert record.packet_id == packet.packet_id
        assert record.destination_namespace == packet.target_destination_class


# ── TestNoDirectL4Write ───────────────────────────────────────────────────────


class TestNoDirectL4Write:
    """Prove no direct L4 write occurs outside the governed handoff seam."""

    def test_transition_approval_state_has_no_side_effects(self):
        """transition_approval_state is pure; it only returns a new packet."""
        packet = _make_pending_packet()

        with patch(
            "agentic_core.L4_state.enforcement.promotion_authority.get_promotion_authority",
            side_effect=AssertionError("L4 must not be touched by state transition"),
        ):
            approved = transition_approval_state(packet, ApprovalState.APPROVED)

        assert approved.approval_state == ApprovalState.APPROVED

    def test_packetize_pending_does_not_touch_l4(self):
        """packetize_pending() must not call PromotionAuthority."""
        cluster = RcaCluster(
            cluster_id="rca-nol4",
            cluster_key="test-lane|ABSTAIN_MISSED",
            lane_id="test-lane",
            failure_mode="ABSTAIN_MISSED",
            failure_count=4,
            sample_packet_ids=["p0", "p1"],
            collections_affected=["col-a"],
            avg_support_coverage=0.25,
            avg_citation_completeness=0.40,
            avg_exact_match_drift=0.02,
            severity="medium",
            rca_summary="test",
            first_seen_at=1000.0,
            last_seen_at=1002.0,
        )
        candidate = PromotionStager().stage(cluster)

        with patch(
            "agentic_core.L4_state.enforcement.promotion_authority.get_promotion_authority",
            side_effect=AssertionError("L4 must not be touched by packetize_pending"),
        ):
            packet = PromotionPacketizer().packetize_pending(candidate, cluster)

        assert packet.approval_state == ApprovalState.PENDING

    def test_approve_and_handoff_dry_run_does_not_commit_l4(self):
        """dry_run=True must not call PromotionAuthority.update_pointer_via_gateway."""
        packet = _make_pending_packet()
        approved = transition_approval_state(packet, ApprovalState.APPROVED)
        pipeline = L6ShadowEvalPipeline()

        with patch(
            "agentic_core.L4_state.enforcement.promotion_authority.get_promotion_authority",
            side_effect=AssertionError("L4 must not be touched in dry-run mode"),
        ):
            final_packet, record = pipeline.approve_and_handoff(approved, dry_run=True)

        assert record.dry_run is True
        assert record.committed is False
        assert final_packet.approval_state == ApprovalState.APPROVED


# ── TestNoCurrentRunMutation ──────────────────────────────────────────────────


class TestNoCurrentRunMutation:
    """Prove current-run results are not mutated anywhere in the async slice."""

    def test_build_shadow_eval_packet_does_not_mutate_eval_result(self):
        artifact = _make_artifact()
        result = _make_eval_result(artifact)
        original_disposition = result.disposition
        original_confidence = result.confidence_score

        packet = build_shadow_eval_packet(artifact, result)

        assert result.disposition == original_disposition
        assert result.confidence_score == original_confidence
        assert packet.run_scope == "FUTURE_RUN"

    def test_shadow_packet_cycle_does_not_mutate_eval_result(self):
        artifact = _make_artifact()
        result = _make_eval_result(
            artifact,
            escalation_correct=False,
            support_coverage=0.15,
        )
        original_disposition = result.disposition

        shadow_packet = build_shadow_eval_packet(artifact, result)
        pipeline = L6ShadowEvalPipeline()
        pipeline.run_shadow_packet_cycle([shadow_packet])

        assert result.disposition == original_disposition

    def test_current_run_result_is_frozen(self):
        artifact = _make_artifact()
        result = _make_eval_result(artifact)

        with pytest.raises((AttributeError, TypeError)):
            result.disposition = ExitDisposition.DENY_RETURN  # type: ignore[misc]

    def test_full_async_slice_does_not_mutate_artifact(self):
        artifact = _make_artifact(trace_id="trace-frozen")
        original_trace_id = artifact.trace_id
        result = _make_eval_result(artifact)

        shadow_packet = build_shadow_eval_packet(artifact, result)
        pipeline = L6ShadowEvalPipeline()
        pipeline.run_shadow_packet_cycle([shadow_packet])

        assert artifact.trace_id == original_trace_id


# ── TestEndToEnd ──────────────────────────────────────────────────────────────


class TestEndToEnd:
    """Full pipeline: sealed artifact → COMMITTED (mocked UWG) or PENDING."""

    def _run_full_cycle_to_pending(
        self,
        *,
        packet_count: int = 5,
        failure_mode: str = "ESCALATION_MISSED",
    ) -> tuple[L6ShadowEvalPipeline, list[PromotionPacket]]:
        """Push enough failing packets to get PROPOSE-class candidates, then packetize."""
        artifacts = [
            _make_artifact(artifact_id=f"art-{i}", trace_id=f"trace-{i}") for i in range(packet_count)
        ]
        results = [
            _make_eval_result(
                artifacts[i],
                eval_id=f"eval-{i}",
                escalation_correct=(failure_mode != "ESCALATION_MISSED"),
                abstain_correct=(failure_mode != "ABSTAIN_MISSED"),
                support_coverage=0.15,
            )
            for i in range(packet_count)
        ]
        shadow_packets = [build_shadow_eval_packet(artifacts[i], results[i]) for i in range(packet_count)]

        pipeline = L6ShadowEvalPipeline()
        pipeline.run_shadow_packet_cycle(shadow_packets)

        clusters = pipeline.clusters()
        packetizer = PromotionPacketizer()
        candidates = pipeline.candidates()
        pending_packets = []
        for cluster in clusters:
            for cand in candidates:
                if cand.cluster_key == cluster.cluster_key:
                    pending_packets.append(packetizer.packetize_pending(cand, cluster))
        return pipeline, pending_packets

    def test_e2e_sealed_artifact_to_pending_packet(self):
        artifact = _make_artifact()
        result = _make_eval_result(artifact, escalation_correct=False, support_coverage=0.10)
        shadow = build_shadow_eval_packet(artifact, result)

        pipeline = L6ShadowEvalPipeline()
        pipeline.run_shadow_packet_cycle([shadow])

        assert len(pipeline.all_graded()) == 1

    def test_e2e_five_failures_produce_propose_candidate(self):
        pipeline, pending_packets = self._run_full_cycle_to_pending(packet_count=5)

        propose = [c for c in pipeline.candidates() if c.classification == "PROPOSE"]
        assert len(propose) >= 1
        assert len(pending_packets) >= 1
        for pkt in pending_packets:
            assert pkt.approval_state == ApprovalState.PENDING

    def test_e2e_approved_packet_through_dry_run_handoff(self):
        pipeline, pending_packets = self._run_full_cycle_to_pending(packet_count=5)
        assert pending_packets, "Need at least one pending packet"

        pkt = pending_packets[0]
        approved = transition_approval_state(pkt, ApprovalState.APPROVED)

        final_packet, record = pipeline.approve_and_handoff(approved, dry_run=True)

        assert record.dry_run is True
        assert record.committed is False
        assert record.token_id != "UNISSUED"
        assert record.packet_id == pkt.packet_id
        assert final_packet.approval_state == ApprovalState.APPROVED

    def test_e2e_approved_packet_committed_after_successful_handoff(self):
        pipeline, pending_packets = self._run_full_cycle_to_pending(packet_count=5)
        assert pending_packets

        pkt = pending_packets[0]
        approved = transition_approval_state(pkt, ApprovalState.APPROVED)

        mock_record = MagicMock()
        mock_record.committed = True
        mock_record.dry_run = False
        mock_record.token_id = "tok-e2e"
        mock_record.token_valid = True
        mock_record.packet_id = pkt.packet_id

        with patch(
            "agentic_core.L6_observability.utils.evaluation.governed_handoff.GovernedHandoffAgent.handoff",
            return_value=mock_record,
        ):
            final_packet, record = pipeline.approve_and_handoff(approved, dry_run=False)

        assert record.committed is True
        assert final_packet.approval_state == ApprovalState.COMMITTED

    def test_e2e_rejected_path_never_reaches_handoff(self):
        pipeline, pending_packets = self._run_full_cycle_to_pending(packet_count=5)
        assert pending_packets

        pkt = pending_packets[0]
        rejected = transition_approval_state(pkt, ApprovalState.REJECTED)

        with patch(
            "agentic_core.L6_observability.utils.evaluation.governed_handoff.GovernedHandoffAgent.handoff",
            side_effect=AssertionError("handoff must not be called for rejected packets"),
        ):
            with pytest.raises(ValueError, match="approval_state=APPROVED"):
                pipeline.approve_and_handoff(rejected, dry_run=True)

    def test_e2e_committed_unreachable_from_pending_directly(self):
        """PENDING → COMMITTED direct skip is rejected by the state machine."""
        pkt = _make_pending_packet()
        assert pkt.approval_state == ApprovalState.PENDING

        with pytest.raises(ValueError, match="PENDING.*COMMITTED"):
            transition_approval_state(pkt, ApprovalState.COMMITTED)

    def test_e2e_pipeline_does_not_set_committed_when_handoff_not_committed(self):
        """approve_and_handoff keeps APPROVED when HandoffRecord.committed is False."""
        pipeline, pending_packets = self._run_full_cycle_to_pending(packet_count=5)
        assert pending_packets

        pkt = pending_packets[0]
        approved = transition_approval_state(pkt, ApprovalState.APPROVED)

        mock_record = MagicMock()
        mock_record.committed = False
        mock_record.error = "PromotionAuthority refused"

        with patch(
            "agentic_core.L6_observability.utils.evaluation.governed_handoff.GovernedHandoffAgent.handoff",
            return_value=mock_record,
        ):
            final_packet, record = pipeline.approve_and_handoff(approved, dry_run=False)

        assert record.committed is False
        assert final_packet.approval_state == ApprovalState.APPROVED


# ── TestHandoffApprovalStateGate ─────────────────────────────────────────────


class TestHandoffApprovalStateGate:
    """Directly exercise the approval_state gate inside GovernedHandoffAgent.handoff().

    approve_and_handoff() raises ValueError before calling handoff() for non-APPROVED
    packets, so the gate at the handoff() boundary was previously unreachable in tests.
    These tests call handoff() directly.
    """

    def test_handoff_blocks_pending_packet_with_approved_flag(self):
        """handoff(approved=True) returns blocked HandoffRecord when approval_state=PENDING."""
        from agentic_core.L6_observability.utils.evaluation.governed_handoff import (
            GovernedHandoffAgent,
            HandoffRecord,
        )

        pkt = _make_pending_packet()
        assert pkt.approval_state == ApprovalState.PENDING
        assert pkt.run_scope == "FUTURE_RUN"

        agent = GovernedHandoffAgent()
        record = agent.handoff(pkt, dry_run=False, approved=True)

        assert isinstance(record, HandoffRecord)
        assert record.committed is False
        assert record.commit_attempted is False
        assert "approval_state" in (record.error or "").lower()

    def test_handoff_blocks_rejected_packet_with_approved_flag(self):
        """handoff(approved=True) returns blocked HandoffRecord when approval_state=REJECTED."""
        from agentic_core.L6_observability.utils.evaluation.governed_handoff import (
            GovernedHandoffAgent,
            HandoffRecord,
        )

        pkt = _make_pending_packet()
        rejected = transition_approval_state(pkt, ApprovalState.REJECTED)

        agent = GovernedHandoffAgent()
        record = agent.handoff(rejected, dry_run=False, approved=True)

        assert isinstance(record, HandoffRecord)
        assert record.committed is False
        assert "approval_state" in (record.error or "").lower()

    def test_handoff_allows_approved_packet_with_approved_flag(self):
        """handoff(approved=True) proceeds past approval_state gate when state=APPROVED."""
        from agentic_core.L6_observability.utils.evaluation.governed_handoff import (
            GovernedHandoffAgent,
            HandoffRecord,
        )

        pkt = _make_pending_packet()
        approved_pkt = transition_approval_state(pkt, ApprovalState.APPROVED)

        agent = GovernedHandoffAgent()
        record = agent.handoff(approved_pkt, dry_run=True, approved=True)

        assert isinstance(record, HandoffRecord)
        assert record.dry_run is True
        assert "approval_state" not in (record.error or "").lower()
