"""Tests for the async future-run evaluation slice.

Covers:
  1. ShadowEvalPacket construction from SealedL2Artifact + CurrentRunEvaluationResult
  2. ShadowPacketGrader multi-dimensional grading
  3. RcaAggregator clustering of repeated failures
  4. PromotionPacket creation as PENDING only
  5. Isolation invariants — no live mutation, no UWG call

Architectural invariant under test:
  ShadowEvalPacket.run_scope == 'FUTURE_RUN'
  CurrentRunEvaluationResult.run_scope == 'CURRENT_RUN'
  PromotionPacket.approval_state == ApprovalState.PENDING (from packetize_pending)
"""

from __future__ import annotations

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
    ShadowEvalPacket,
    build_shadow_eval_packet,
)
from agentic_core.L6_observability.utils.evaluation.promotion_packet import (
    ApprovalState,
    PromotionPacket,
    PromotionPacketizer,
)
from agentic_core.L6_observability.utils.evaluation.promotion_stager import (
    PromotionStager,
)
from agentic_core.L6_observability.utils.evaluation.rca_aggregator import (
    RcaAggregator,
    RcaCluster,
)
from agentic_core.L6_observability.utils.evaluation.shadow_eval_grader import (
    ShadowGradeBundle,
    ShadowPacketGrader,
    bridge_to_shadow_eval_result,
)
from agentic_core.L6_observability.utils.evaluation.shadow_eval_pipeline import (
    L6ShadowEvalPipeline,
)

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

_GOOD_EXEC_TRACE = {
    "trace_id": "t-001",
    "actor": "test-agent",
    "policy_hash": "ph-good",
    "replay_key": "rk-001",
}


def _good_artifact(**overrides) -> SealedL2Artifact:
    defaults = dict(
        artifact_id="art-001",
        trace_id="trace-001",
        exec_trace=dict(_GOOD_EXEC_TRACE),
        validation_counters=ValidationCounters(
            policy_checks_passed=5,
            schema_checks_passed=3,
        ),
        terminal_classification=TerminalClassification.SUCCESS,
        replay_metadata=ReplayMetadata(replay_completeness=1.0, isolation_verified=True),
    )
    defaults.update(overrides)
    return SealedL2Artifact(**defaults)


def _good_eval_result(artifact: SealedL2Artifact, **overrides) -> CurrentRunEvaluationResult:
    defaults = dict(
        eval_id="eval-001",
        artifact_id=artifact.artifact_id,
        trace_id=artifact.trace_id,
        rubric_scores=RubricScores(
            rules_compliance_score=1.0,
            policy_adherence_score=1.0,
            schema_completion_score=1.0,
        ),
        quality_checks=QualityChecks(
            answer_fit=True,
            groundedness_score=0.8,
            support_coverage=0.7,
            relevance_score=0.9,
            abstain_correct=True,
            escalation_correct=True,
        ),
        integrity_checks=IntegrityChecks(
            safety_clear=True,
            policy_pass=True,
            mutation_authorized=True,
            env_integrity=True,
            replay_env_complete=True,
        ),
        confidence_score=0.85,
        disposition=ExitDisposition.ALLOW_RESPONSE,
        disposition_reason="All checks passed",
        policy_hash="ph-good",
    )
    defaults.update(overrides)
    return CurrentRunEvaluationResult(**defaults)


def _make_cluster(
    *,
    failure_mode: str = "ABSTAIN_MISSED",
    failure_count: int = 4,
    severity: str = "medium",
    lane_id: str = "test-lane",
) -> RcaCluster:
    return RcaCluster(
        cluster_id=f"rca-test-{failure_mode.lower()}",
        cluster_key=f"{lane_id}|{failure_mode}",
        lane_id=lane_id,
        failure_mode=failure_mode,
        failure_count=failure_count,
        sample_packet_ids=[f"p{i}" for i in range(min(failure_count, 5))],
        collections_affected=["col-a"],
        avg_support_coverage=0.25,
        avg_citation_completeness=0.45,
        avg_exact_match_drift=-0.05,
        severity=severity,
        rca_summary="Test cluster",
        first_seen_at=1000.0,
        last_seen_at=2000.0,
    )


# ---------------------------------------------------------------------------
# 1. ShadowEvalPacket construction
# ---------------------------------------------------------------------------


class TestBuildShadowEvalPacket:
    def test_build_success_all_fields_populated(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)

        packet = build_shadow_eval_packet(artifact, result)

        assert isinstance(packet, ShadowEvalPacket)
        assert packet.run_id == result.eval_id
        assert packet.exit_disposition == ExitDisposition.ALLOW_RESPONSE.value
        assert packet.exit_trace_id == result.trace_id
        assert packet.exit_reason == result.disposition_reason

    def test_telemetry_carries_outcome_signals(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)

        packet = build_shadow_eval_packet(artifact, result)

        assert packet.telemetry["groundedness_score"] == 0.8
        assert packet.telemetry["support_coverage"] == 0.7
        assert packet.telemetry["relevance_score"] == 0.9
        assert packet.telemetry["abstain_correct"] is True
        assert packet.telemetry["escalation_correct"] is True

    def test_telemetry_carries_rubric_and_integrity_signals(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)

        packet = build_shadow_eval_packet(artifact, result)

        assert packet.telemetry["rules_compliance_score"] == 1.0
        assert packet.telemetry["policy_adherence_score"] == 1.0
        assert packet.telemetry["replay_env_complete"] is True
        assert packet.telemetry["terminal_classification"] == "SUCCESS"

    def test_exec_traces_serialized_from_artifact(self):
        artifact = _good_artifact(exec_trace={"actor": "agent-x", "policy_hash": "ph-abc"})
        result = _good_eval_result(artifact)

        packet = build_shadow_eval_packet(artifact, result)

        assert len(packet.exec_traces) == 1
        assert packet.exec_traces[0]["actor"] == "agent-x"
        assert packet.exec_traces[0]["policy_hash"] == "ph-abc"

    def test_exec_traces_empty_when_no_exec_trace(self):
        artifact = _good_artifact(exec_trace={})
        result = _good_eval_result(artifact)

        packet = build_shadow_eval_packet(artifact, result)

        assert packet.exec_traces == ()

    def test_lineage_ids_include_both_trace_ids_when_different(self):
        artifact = _good_artifact(trace_id="art-trace-999")
        result = _good_eval_result(artifact, trace_id="eval-trace-888")

        packet = build_shadow_eval_packet(artifact, result)

        assert "eval-trace-888" in packet.lineage_ids
        assert "art-trace-999" in packet.lineage_ids

    def test_lineage_ids_deduplicated_when_same(self):
        artifact = _good_artifact(trace_id="shared-trace")
        result = _good_eval_result(artifact, trace_id="shared-trace")

        packet = build_shadow_eval_packet(artifact, result)

        assert packet.lineage_ids.count("shared-trace") == 1

    def test_baseline_ids_populated_from_hashes(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact, policy_hash="ph-xyz", compliance_hash="ch-xyz")

        packet = build_shadow_eval_packet(artifact, result)

        assert "ph-xyz" in packet.baseline_ids
        assert "ch-xyz" in packet.baseline_ids

    def test_hitl_packet_merged_into_telemetry(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)
        hitl = {"hitl_id": "hitl-001", "reason": "jurisdiction_review"}

        packet = build_shadow_eval_packet(artifact, result, hitl_packet=hitl)

        assert packet.telemetry["hitl_packet"]["hitl_id"] == "hitl-001"

    def test_extra_telemetry_merged(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)

        packet = build_shadow_eval_packet(
            artifact, result, extra_telemetry={"retry_count": 7, "budget_remaining": 0.0}
        )

        assert packet.telemetry["retry_count"] == 7
        assert packet.telemetry["budget_remaining"] == 0.0


# ---------------------------------------------------------------------------
# 2. Scope / isolation invariants
# ---------------------------------------------------------------------------


class TestScopeInvariants:
    def test_shadow_eval_packet_run_scope_is_future_run(self):
        assert ShadowEvalPacket.run_scope == "FUTURE_RUN"

    def test_sealed_l2_artifact_run_scope_is_current_run(self):
        assert SealedL2Artifact.run_scope == "CURRENT_RUN"

    def test_current_run_eval_result_run_scope_is_current_run(self):
        assert CurrentRunEvaluationResult.run_scope == "CURRENT_RUN"

    def test_promotion_packet_run_scope_is_future_run(self):
        assert PromotionPacket.run_scope == "FUTURE_RUN"

    def test_current_run_result_is_frozen_immutable(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)

        with pytest.raises((AttributeError, TypeError)):
            result.disposition = ExitDisposition.DENY_RETURN  # type: ignore[misc]

    def test_current_run_result_unchanged_after_async_slice(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)
        original_disposition = result.disposition
        original_confidence = result.confidence_score

        packet = build_shadow_eval_packet(artifact, result)
        ShadowPacketGrader().grade(packet)

        assert result.disposition is original_disposition
        assert result.confidence_score == original_confidence


# ---------------------------------------------------------------------------
# 3. ShadowPacketGrader — multi-dimensional grading
# ---------------------------------------------------------------------------


class TestShadowPacketGrader:
    def test_all_good_packet_grades_as_pass(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)
        packet = build_shadow_eval_packet(artifact, result)

        bundle = ShadowPacketGrader().grade(packet)

        assert bundle.overall_grade == "PASS"
        assert bundle.severity_tags == ()
        assert bundle.normalized_score > 0.5

    def test_outcome_good_trajectory_bad_grades_as_warn(self):
        artifact = _good_artifact()
        result = _good_eval_result(
            artifact,
            integrity_checks=IntegrityChecks(
                safety_clear=True,
                policy_pass=True,
                mutation_authorized=True,
                env_integrity=True,
                replay_env_complete=False,
            ),
        )
        packet = build_shadow_eval_packet(artifact, result, extra_telemetry={"retry_count": 5})

        bundle = ShadowPacketGrader().grade(packet)

        assert bundle.outcome_grades.task_completion == 1.0
        assert bundle.outcome_grades.groundedness_score == 0.8
        assert bundle.trajectory_grades.trajectory_integrity is False
        assert bundle.trajectory_grades.retry_thrash_ok is False
        assert "RETRY_THRASH" in bundle.severity_tags
        assert "TRAJECTORY_BROKEN" in bundle.severity_tags
        assert bundle.overall_grade == "WARN"

    def test_escalation_missed_grades_as_fail(self):
        artifact = _good_artifact()
        result = _good_eval_result(
            artifact,
            quality_checks=QualityChecks(
                answer_fit=True,
                groundedness_score=0.8,
                support_coverage=0.7,
                relevance_score=0.9,
                abstain_correct=True,
                escalation_correct=False,
            ),
        )
        packet = build_shadow_eval_packet(artifact, result)

        bundle = ShadowPacketGrader().grade(packet)

        assert bundle.outcome_grades.escalation_correct is False
        assert "ESCALATION_MISSED" in bundle.severity_tags
        assert bundle.overall_grade == "FAIL"

    def test_policy_violation_grades_as_fail(self):
        artifact = _good_artifact()
        result = _good_eval_result(
            artifact,
            rubric_scores=RubricScores(
                rules_compliance_score=0.2,  # below 0.5 threshold
                policy_adherence_score=1.0,
                schema_completion_score=1.0,
            ),
        )
        packet = build_shadow_eval_packet(artifact, result)

        bundle = ShadowPacketGrader().grade(packet)

        assert bundle.trajectory_grades.policy_compliance == 0.2
        assert "POLICY_VIOLATION" in bundle.severity_tags
        assert bundle.overall_grade == "FAIL"

    def test_gate_regression_grades_as_fail(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact, disposition=ExitDisposition.ALLOW_RESPONSE)
        packet = build_shadow_eval_packet(artifact, result)

        baseline = {"expected_disposition": "DENY_RETURN"}
        bundle = ShadowPacketGrader().grade(packet, baseline=baseline)

        assert bundle.governance.gate_regression is True
        assert "GATE_REGRESSION" in bundle.severity_tags
        assert bundle.overall_grade == "FAIL"

    def test_schema_drift_grades_as_warn(self):
        artifact = _good_artifact(
            validation_counters=ValidationCounters(schema_checks_failed=1, schema_checks_passed=2)
        )
        result = _good_eval_result(artifact)
        packet = build_shadow_eval_packet(artifact, result)

        bundle = ShadowPacketGrader().grade(packet)

        assert bundle.governance.schema_drift is True
        assert "SCHEMA_DRIFT" in bundle.severity_tags
        assert bundle.overall_grade == "WARN"

    def test_api_drift_detected_via_policy_hash_change(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact, policy_hash="ph-current")
        packet = build_shadow_eval_packet(artifact, result)

        baseline = {"policy_hash": "ph-old"}
        bundle = ShadowPacketGrader().grade(packet, baseline=baseline)

        assert bundle.governance.api_drift is True
        assert "API_DRIFT" in bundle.severity_tags

    def test_rubric_drift_detected_when_adherence_shifts(self):
        artifact = _good_artifact()
        result = _good_eval_result(
            artifact,
            rubric_scores=RubricScores(
                rules_compliance_score=1.0,
                policy_adherence_score=0.6,  # current
                schema_completion_score=1.0,
            ),
        )
        packet = build_shadow_eval_packet(artifact, result)

        baseline = {"policy_adherence_baseline": 1.0}  # delta = 0.4 > 0.15
        bundle = ShadowPacketGrader().grade(packet, baseline=baseline)

        assert bundle.governance.rubric_drift is True
        assert "RUBRIC_DRIFT" in bundle.severity_tags

    def test_task_incomplete_on_failure_terminal(self):
        artifact = _good_artifact(terminal_classification=TerminalClassification.FAILURE)
        result = _good_eval_result(artifact, disposition=ExitDisposition.DENY_RETURN)
        packet = build_shadow_eval_packet(artifact, result)

        bundle = ShadowPacketGrader().grade(packet)

        assert bundle.outcome_grades.task_completion == 0.0
        assert "TASK_INCOMPLETE" in bundle.severity_tags

    def test_normalized_score_is_clamped_to_unit_interval(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)
        packet = build_shadow_eval_packet(artifact, result)

        bundle = ShadowPacketGrader().grade(packet)

        assert 0.0 <= bundle.normalized_score <= 1.0

    def test_grade_reasons_are_populated_for_failures(self):
        artifact = _good_artifact()
        result = _good_eval_result(
            artifact,
            quality_checks=QualityChecks(
                answer_fit=True,
                groundedness_score=0.1,  # below 0.30 threshold
                support_coverage=0.1,
                relevance_score=0.5,
                abstain_correct=True,
                escalation_correct=True,
            ),
        )
        packet = build_shadow_eval_packet(artifact, result)

        bundle = ShadowPacketGrader().grade(packet)

        assert any("GROUNDEDNESS_FAIL" in r for r in bundle.grade_reasons)


# ---------------------------------------------------------------------------
# 4. Bridge: ShadowGradeBundle → ShadowEvalResult
# ---------------------------------------------------------------------------


class TestBridgeToShadowEvalResult:
    def test_bridge_preserves_packet_and_run_id(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)
        packet = build_shadow_eval_packet(artifact, result)
        bundle = ShadowPacketGrader().grade(packet)

        shadow_result = bridge_to_shadow_eval_result(bundle)

        assert shadow_result.packet_id == bundle.packet_id
        assert shadow_result.run_id == bundle.run_id

    def test_bridge_maps_overall_grade(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)
        packet = build_shadow_eval_packet(artifact, result)
        bundle = ShadowPacketGrader().grade(packet)

        shadow_result = bridge_to_shadow_eval_result(bundle)

        assert shadow_result.overall_grade == bundle.overall_grade

    def test_bridge_maps_lane_regression_tag_from_first_severity(self):
        artifact = _good_artifact()
        result = _good_eval_result(
            artifact,
            quality_checks=QualityChecks(
                answer_fit=True,
                groundedness_score=0.8,
                support_coverage=0.7,
                relevance_score=0.9,
                abstain_correct=True,
                escalation_correct=False,
            ),
        )
        packet = build_shadow_eval_packet(artifact, result)
        bundle = ShadowPacketGrader().grade(packet)

        shadow_result = bridge_to_shadow_eval_result(bundle)

        assert shadow_result.lane_regression_tag == bundle.severity_tags[0]

    def test_bridge_result_ingested_by_rca_aggregator(self):
        artifact = _good_artifact()
        result = _good_eval_result(
            artifact,
            quality_checks=QualityChecks(
                answer_fit=True,
                groundedness_score=0.8,
                support_coverage=0.7,
                relevance_score=0.9,
                abstain_correct=True,
                escalation_correct=False,
            ),
        )
        packet = build_shadow_eval_packet(artifact, result)
        bundle = ShadowPacketGrader().grade(packet)
        shadow_result = bridge_to_shadow_eval_result(bundle)

        aggregator = RcaAggregator()
        aggregator.ingest(shadow_result)

        assert aggregator.result_count() == 1


# ---------------------------------------------------------------------------
# 5. Aggregation and pattern detection
# ---------------------------------------------------------------------------


class TestAggregationAndPatternDetection:
    def _make_failing_packet(
        self, run_id: str, *, failure_mode: str = "ESCALATION_MISSED"
    ) -> ShadowEvalPacket:
        artifact = _good_artifact(
            artifact_id=f"art-{run_id}",
            trace_id=f"trace-{run_id}",
            exec_trace={"actor": "cluster-agent", "policy_hash": "ph1"},
        )
        if failure_mode == "ESCALATION_MISSED":
            qc = QualityChecks(
                answer_fit=True,
                groundedness_score=0.8,
                support_coverage=0.7,
                relevance_score=0.9,
                abstain_correct=True,
                escalation_correct=False,
            )
        else:
            qc = QualityChecks(
                answer_fit=True,
                groundedness_score=0.8,
                support_coverage=0.7,
                relevance_score=0.9,
                abstain_correct=False,
                escalation_correct=True,
            )
        result = _good_eval_result(
            artifact,
            eval_id=run_id,
            artifact_id=f"art-{run_id}",
            trace_id=f"trace-{run_id}",
            quality_checks=qc,
        )
        return build_shadow_eval_packet(artifact, result)

    def test_repeated_failures_cluster_into_propose_candidate(self):
        packets = [self._make_failing_packet(f"run-{i}") for i in range(5)]

        pipeline = L6ShadowEvalPipeline()
        summary = pipeline.run_shadow_packet_cycle(packets)

        assert summary["packets_processed"] == 5
        assert summary["fail_count"] == 5
        assert len(summary["clusters"]) >= 1
        propose_candidates = [c for c in pipeline.candidates() if c.classification == "PROPOSE"]
        assert len(propose_candidates) >= 1

    def test_single_failure_does_not_create_propose_candidate(self):
        packets = [self._make_failing_packet("run-solo", failure_mode="ABSTAIN_MISSED")]

        pipeline = L6ShadowEvalPipeline()
        pipeline.run_shadow_packet_cycle(packets)

        propose_candidates = [c for c in pipeline.candidates() if c.classification == "PROPOSE"]
        assert len(propose_candidates) == 0

    def test_two_failures_create_hold_not_propose(self):
        packets = [self._make_failing_packet(f"run-{i}", failure_mode="ABSTAIN_MISSED") for i in range(2)]

        pipeline = L6ShadowEvalPipeline()
        pipeline.run_shadow_packet_cycle(packets)

        candidates = pipeline.candidates()
        assert len(candidates) >= 1
        assert all(c.classification == "HOLD" for c in candidates)

    def test_mixed_passes_and_fails_only_clusters_fails(self):
        good_artifact = _good_artifact()
        good_result = _good_eval_result(good_artifact)
        good_packet = build_shadow_eval_packet(good_artifact, good_result)

        fail_packets = [self._make_failing_packet(f"fail-{i}") for i in range(5)]

        pipeline = L6ShadowEvalPipeline()
        summary = pipeline.run_shadow_packet_cycle([good_packet] + fail_packets)

        assert summary["pass_count"] == 1
        assert summary["fail_count"] == 5
        assert len(summary["clusters"]) >= 1

    def test_empty_packets_returns_zero_summary(self):
        pipeline = L6ShadowEvalPipeline()
        summary = pipeline.run_shadow_packet_cycle([])

        assert summary["packets_processed"] == 0
        assert summary["results_graded"] == 0
        assert summary["clusters"] == []
        assert summary["shadow_grade_bundles"] == []

    def test_shadow_grade_bundles_returned_in_summary(self):
        artifact = _good_artifact()
        result = _good_eval_result(artifact)
        packet = build_shadow_eval_packet(artifact, result)

        pipeline = L6ShadowEvalPipeline()
        summary = pipeline.run_shadow_packet_cycle([packet])

        assert len(summary["shadow_grade_bundles"]) == 1
        assert isinstance(summary["shadow_grade_bundles"][0], ShadowGradeBundle)


# ---------------------------------------------------------------------------
# 6. PromotionPacket — PENDING only, no UWG commit
# ---------------------------------------------------------------------------


class TestPromotionPacketPendingOnly:
    def test_packetize_pending_produces_pending_state(self):
        cluster = _make_cluster(failure_count=4, severity="medium")
        candidate = PromotionStager().stage(cluster)
        packetizer = PromotionPacketizer()

        packet = packetizer.packetize_pending(candidate, cluster)

        assert packet.approval_state == ApprovalState.PENDING

    def test_packetize_pending_is_not_approved(self):
        cluster = _make_cluster(failure_count=4, severity="medium")
        candidate = PromotionStager().stage(cluster)

        packet = PromotionPacketizer().packetize_pending(candidate, cluster)

        assert packet.approval_state != ApprovalState.APPROVED
        assert packet.approval_state != ApprovalState.COMMITTED

    def test_packetize_pending_run_scope_is_future_run(self):
        cluster = _make_cluster()
        candidate = PromotionStager().stage(cluster)

        packet = PromotionPacketizer().packetize_pending(candidate, cluster)

        assert packet.run_scope == "FUTURE_RUN"

    def test_packetize_pending_edition_contains_pending_marker(self):
        cluster = _make_cluster()
        candidate = PromotionStager().stage(cluster)

        packet = PromotionPacketizer().packetize_pending(candidate, cluster)

        assert "pending" in packet.edition.lower()

    def test_packetize_pending_includes_rollback_metadata(self):
        cluster = _make_cluster(failure_mode="ABSTAIN_MISSED", failure_count=4)
        candidate = PromotionStager().stage(cluster)

        packet = PromotionPacketizer().packetize_pending(candidate, cluster)

        assert "parameter" in packet.rollback_metadata
        assert packet.rollback_metadata["rollback_trigger"] == "manual_approval_required"

    def test_packetize_pending_with_empty_replay_refs(self):
        cluster = _make_cluster(failure_count=0)  # sample_packet_ids is already []
        from agentic_core.L6_observability.utils.evaluation.promotion_stager import PromotionCandidate

        candidate = PromotionCandidate(
            candidate_id="pc-test-empty",
            cluster_id=cluster.cluster_id,
            cluster_key=cluster.cluster_key,
            classification="HOLD",
            baseline_drift_findings=(),
            suggested_changes=(
                {"parameter": "x", "current_value": None, "proposed_value": None, "rationale": ""},
            ),
            rationale="test",
            replay_references=(),
            staged_at=0.0,
        )

        packet = PromotionPacketizer().packetize_pending(candidate, cluster)

        assert packet.approval_state == ApprovalState.PENDING
        assert packet.replay_digest == "0" * 16

    def test_pipeline_candidates_are_not_committed(self):
        def _make_pkt(run_id: str) -> ShadowEvalPacket:
            art = _good_artifact(
                artifact_id=f"art-{run_id}",
                trace_id=f"t-{run_id}",
                exec_trace={"actor": "a1", "policy_hash": "ph1"},
            )
            res = _good_eval_result(
                art,
                eval_id=run_id,
                artifact_id=f"art-{run_id}",
                trace_id=f"t-{run_id}",
                quality_checks=QualityChecks(
                    answer_fit=True,
                    groundedness_score=0.8,
                    support_coverage=0.7,
                    relevance_score=0.9,
                    abstain_correct=True,
                    escalation_correct=False,
                ),
            )
            return build_shadow_eval_packet(art, res)

        packets = [_make_pkt(f"r{i}") for i in range(5)]
        pipeline = L6ShadowEvalPipeline()
        pipeline.run_shadow_packet_cycle(packets)

        for candidate in pipeline.candidates():
            assert candidate.classification in ("PROPOSE", "HOLD")


# ---------------------------------------------------------------------------
# 7. No UWG or durable write path invoked
# ---------------------------------------------------------------------------


class TestNoUWGInAsyncSlice:
    def test_governed_handoff_not_called_in_shadow_packet_cycle(self):
        from unittest.mock import patch

        artifact = _good_artifact()
        result = _good_eval_result(artifact)
        packet = build_shadow_eval_packet(artifact, result)
        pipeline = L6ShadowEvalPipeline()

        with patch(
            "agentic_core.L6_observability.utils.evaluation.governed_handoff.GovernedHandoffAgent.handoff",
            side_effect=AssertionError("UWG handoff must NOT be called in async slice"),
        ) as mock_hh:
            summary = pipeline.run_shadow_packet_cycle([packet])
            mock_hh.assert_not_called()

        assert summary["packets_processed"] == 1

    def test_packetize_pending_does_not_require_gauntlet_approval(self):
        cluster = _make_cluster(failure_count=4, severity="medium")
        candidate = PromotionStager().stage(cluster)
        packetizer = PromotionPacketizer()

        packet = packetizer.packetize_pending(candidate, cluster)

        assert packet.approval_state == ApprovalState.PENDING

    def test_run_shadow_packet_cycle_returns_no_committed_promotions(self):
        def _make_pkt(run_id: str) -> ShadowEvalPacket:
            art = _good_artifact(
                artifact_id=f"art-{run_id}", trace_id=f"t-{run_id}", exec_trace={"actor": "agent-x"}
            )
            res = _good_eval_result(
                art,
                eval_id=run_id,
                artifact_id=f"art-{run_id}",
                trace_id=f"t-{run_id}",
                quality_checks=QualityChecks(
                    answer_fit=True,
                    groundedness_score=0.8,
                    support_coverage=0.7,
                    relevance_score=0.9,
                    abstain_correct=False,
                    escalation_correct=True,
                ),
            )
            return build_shadow_eval_packet(art, res)

        packets = [_make_pkt(f"r{i}") for i in range(5)]
        pipeline = L6ShadowEvalPipeline()
        summary = pipeline.run_shadow_packet_cycle(packets)

        assert "committed_packets" not in summary
        new_candidates = summary["new_candidates"]
        for c in new_candidates:
            assert c.classification in ("PROPOSE", "HOLD")
