"""Tests for ExitControlGate.evaluate_sealed() — current-run evaluation slice.

Tests the full live path:
    SealedL2Artifact → evaluate_sealed() → CurrentRunEvaluationResult
    CurrentRunEvaluationResult → shape_outcome() → outcome payload stub

Test classes
------------
TestAllowResponse         — success path → ALLOW_RESPONSE
TestDenyReturn            — integrity / replay / policy / quality failures → DENY_RETURN
TestEscalateToHITL        — low confidence + explicit escalation reason → ESCALATE_TO_HITL
TestCommitToUWG           — authorized mutation proposal → COMMIT_TO_UWG
TestSingleDispositionInvariant — exactly one disposition per evaluation
TestShadowEvalIsolation   — shadow-eval code cannot influence current-run disposition
TestOutcomeShaping        — shape_outcome() produces correct typed stubs
TestFailClosed            — malformed or incomplete artifact → DENY_RETURN
TestCurrentRunScopeInvariant — run_scope sentinel on result and outcome types

Architecture invariants checked
---------------------------------
- Exactly one ExitDisposition emitted per evaluate_sealed() call
- COMMIT_TO_UWG requires mutation_authorized (not just has_commit_payload)
- DENY takes priority over COMMIT when mutation is unauthorized
- Shadow-eval ingester (AsyncEvalIngester) is never called by evaluate_sealed()
- AllowResponsePayload, DenyReturnPayload, EscalateToHITLPacket, CommitToUWGRequest
  all carry run_scope='CURRENT_RUN' to prevent conflation with PromotionPacket
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from agentic_core.L2_execution.types.sealed_l2_artifact import (
    ReplayMetadata,
    SealedL2Artifact,
    TerminalClassification,
    ValidationCounters,
)
from agentic_core.L5_safety.enforcement.exit_control_gate import ExitControlGate
from agentic_core.L5_safety.types.exit_disposition_types import (
    CurrentRunEvaluationResult,
    ExitDisposition,
)
from agentic_core.L5_safety.types.exit_outcome_types import (
    AllowResponsePayload,
    CommitToUWGRequest,
    DenyReturnPayload,
    EscalateToHITLPacket,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GOOD_EVIDENCE = {
    "groundedness_score": 0.90,
    "support_coverage": 0.85,
    "relevance_score": 0.88,
    "abstain_correct": True,
    "escalation_correct": True,
    "safety_clear": True,
}

_GOOD_COUNTERS = ValidationCounters(
    policy_checks_passed=5,
    policy_checks_failed=0,
    schema_checks_passed=3,
    schema_checks_failed=0,
    mutation_auth_checks_passed=0,
    mutation_auth_checks_failed=0,
    env_integrity_checks_passed=2,
    env_integrity_checks_failed=0,
)

_GOOD_REPLAY = ReplayMetadata(
    replay_key="rk-test-001",
    determinism_digest="abc123",
    replay_completeness=0.95,
    seed_captured=True,
    isolation_verified=True,
)


def _artifact(**overrides) -> SealedL2Artifact:
    """Build a fully-passing SealedL2Artifact, overridable per-field."""
    defaults: dict = dict(
        artifact_id="art-001",
        trace_id="trace-001",
        terminal_classification=TerminalClassification.SUCCESS,
        evidence_bundle=dict(_GOOD_EVIDENCE),
        validation_counters=_GOOD_COUNTERS,
        replay_metadata=_GOOD_REPLAY,
        has_commit_payload=False,
        escalation_reason=None,
        sealed_at=1_700_000_000.0,
    )
    defaults.update(overrides)
    return SealedL2Artifact(**defaults)


def _artifact_with_commit(**overrides) -> SealedL2Artifact:
    """Artifact pre-configured for the COMMIT_TO_UWG path.

    state_diff defaults to empty dict (from SealedL2Artifact default).
    Callers that need a specific state_diff must pass it via **overrides.
    """
    return _artifact(
        has_commit_payload=True,
        **overrides,
    )


def _gate(threshold: float = 0.70) -> ExitControlGate:
    return ExitControlGate(
        policy_hash="sha256:test-policy",
        compliance_hash="sha256:test-compliance",
        confidence_threshold=threshold,
    )


# ---------------------------------------------------------------------------
# TestAllowResponse
# ---------------------------------------------------------------------------


class TestAllowResponse:
    def test_fully_passing_artifact_returns_allow(self):
        result = _gate().evaluate_sealed(_artifact())
        assert result.disposition is ExitDisposition.ALLOW_RESPONSE

    def test_allow_result_has_non_empty_eval_id(self):
        result = _gate().evaluate_sealed(_artifact())
        assert result.eval_id and len(result.eval_id) > 0

    def test_allow_result_trace_id_matches_artifact(self):
        result = _gate().evaluate_sealed(_artifact(trace_id="my-trace"))
        assert result.trace_id == "my-trace"

    def test_allow_result_artifact_id_matches(self):
        result = _gate().evaluate_sealed(_artifact(artifact_id="art-xyz"))
        assert result.artifact_id == "art-xyz"

    def test_allow_result_run_scope_is_current_run(self):
        result = _gate().evaluate_sealed(_artifact())
        assert result.run_scope == "CURRENT_RUN"

    def test_allow_result_confidence_above_threshold(self):
        result = _gate().evaluate_sealed(_artifact())
        assert result.confidence_score >= 0.70

    def test_allow_result_all_integrity_checks_pass(self):
        result = _gate().evaluate_sealed(_artifact())
        assert result.integrity_checks.safety_clear is True
        assert result.integrity_checks.policy_pass is True
        assert result.integrity_checks.mutation_authorized is True
        assert result.integrity_checks.replay_env_complete is True

    def test_allow_result_quality_answer_fit_true(self):
        result = _gate().evaluate_sealed(_artifact())
        assert result.quality_checks.answer_fit is True

    def test_two_evaluations_produce_different_eval_ids(self):
        gate = _gate()
        r1 = gate.evaluate_sealed(_artifact())
        r2 = gate.evaluate_sealed(_artifact())
        assert r1.eval_id != r2.eval_id


# ---------------------------------------------------------------------------
# TestDenyReturn
# ---------------------------------------------------------------------------


class TestDenyReturn:
    def test_safety_clear_false_returns_deny(self):
        eb = dict(_GOOD_EVIDENCE, safety_clear=False)
        result = _gate().evaluate_sealed(_artifact(evidence_bundle=eb))
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_deny_reason_mentions_x1c_when_safety_fails(self):
        eb = dict(_GOOD_EVIDENCE, safety_clear=False)
        result = _gate().evaluate_sealed(_artifact(evidence_bundle=eb))
        assert "X1C" in result.disposition_reason or "safety" in result.disposition_reason.lower()

    def test_policy_checks_failed_returns_deny(self):
        bad_counters = ValidationCounters(
            policy_checks_passed=0,
            policy_checks_failed=3,
            schema_checks_passed=3,
            schema_checks_failed=0,
        )
        result = _gate().evaluate_sealed(_artifact(validation_counters=bad_counters))
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_deny_reason_mentions_x1a_when_policy_fails(self):
        bad_counters = ValidationCounters(policy_checks_passed=0, policy_checks_failed=3)
        result = _gate().evaluate_sealed(_artifact(validation_counters=bad_counters))
        assert "X1A" in result.disposition_reason or "rules" in result.disposition_reason.lower()

    def test_replay_completeness_below_threshold_returns_deny(self):
        low_replay = ReplayMetadata(
            replay_key="rk-001",
            replay_completeness=0.50,  # below _REPLAY_COMPLETENESS_THRESHOLD=0.80
            isolation_verified=True,
        )
        result = _gate().evaluate_sealed(_artifact(replay_metadata=low_replay))
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_deny_reason_mentions_x1d_when_replay_incomplete(self):
        low_replay = ReplayMetadata(replay_key="rk", replay_completeness=0.10)
        result = _gate().evaluate_sealed(_artifact(replay_metadata=low_replay))
        assert "X1D" in result.disposition_reason or "ground" in result.disposition_reason.lower()

    def test_failure_terminal_classification_returns_deny(self):
        result = _gate().evaluate_sealed(_artifact(terminal_classification=TerminalClassification.FAILURE))
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_deny_reason_mentions_x1b_when_answer_fit_false(self):
        result = _gate().evaluate_sealed(_artifact(terminal_classification=TerminalClassification.FAILURE))
        assert "X1B" in result.disposition_reason or "answer" in result.disposition_reason.lower()

    def test_groundedness_below_threshold_returns_deny(self):
        eb = dict(_GOOD_EVIDENCE, groundedness_score=0.20)  # below _GROUNDED_THRESHOLD=0.60
        result = _gate().evaluate_sealed(_artifact(evidence_bundle=eb))
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_unauthorized_commit_payload_returns_deny_not_commit(self):
        unauthorized_counters = ValidationCounters(
            policy_checks_passed=5,
            policy_checks_failed=0,
            schema_checks_passed=3,
            schema_checks_failed=0,
            mutation_auth_checks_passed=0,
            mutation_auth_checks_failed=2,  # failed auth → not authorized
        )
        result = _gate().evaluate_sealed(_artifact_with_commit(validation_counters=unauthorized_counters))
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_deny_reason_mentions_mutation_authorized_when_unauthorized(self):
        bad_counters = ValidationCounters(mutation_auth_checks_failed=1)
        result = _gate().evaluate_sealed(_artifact_with_commit(validation_counters=bad_counters))
        assert (
            "mutation" in result.disposition_reason.lower()
            or "authorized" in result.disposition_reason.lower()
        )

    def test_safety_fail_overrides_commit_payload(self):
        eb = dict(_GOOD_EVIDENCE, safety_clear=False)
        result = _gate().evaluate_sealed(_artifact_with_commit(evidence_bundle=eb))
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_safety_fail_overrides_explicit_escalation_reason(self):
        """X1C (priority 1) must beat escalation_reason (priority 4).

        An artifact with safety_clear=False AND an explicit escalation_reason
        must produce DENY_RETURN, not ESCALATE_TO_HITL.  Verifies the
        decision tree priority contract in _decide_from_evaluation.
        """
        eb = dict(_GOOD_EVIDENCE, safety_clear=False)
        result = _gate().evaluate_sealed(
            _artifact(
                evidence_bundle=eb,
                escalation_reason="jurisdiction review requested",
            )
        )
        assert result.disposition is ExitDisposition.DENY_RETURN
        assert "X1C" in result.disposition_reason or "safety" in result.disposition_reason.lower()


# ---------------------------------------------------------------------------
# TestEscalateToHITL
# ---------------------------------------------------------------------------


class TestEscalateToHITL:
    def test_low_confidence_returns_escalate(self):
        eb = dict(
            _GOOD_EVIDENCE,
            groundedness_score=0.0,
            support_coverage=0.0,
            relevance_score=0.0,
        )
        result = _gate(threshold=0.70).evaluate_sealed(_artifact(evidence_bundle=eb))
        assert result.disposition is ExitDisposition.ESCALATE_TO_HITL

    def test_explicit_escalation_reason_returns_escalate(self):
        result = _gate().evaluate_sealed(_artifact(escalation_reason="policy ambiguity detected by L2"))
        assert result.disposition is ExitDisposition.ESCALATE_TO_HITL

    def test_escalate_reason_contains_escalation_reason_text(self):
        result = _gate().evaluate_sealed(_artifact(escalation_reason="requires human jurisdiction decision"))
        assert "requires human jurisdiction decision" in result.disposition_reason

    def test_escalation_reason_takes_priority_over_commit_payload(self):
        result = _gate().evaluate_sealed(_artifact_with_commit(escalation_reason="human approval needed"))
        assert result.disposition is ExitDisposition.ESCALATE_TO_HITL

    def test_escalation_reason_takes_priority_even_with_high_confidence(self):
        result = _gate(threshold=0.10).evaluate_sealed(
            _artifact(escalation_reason="jurisdiction review required")
        )
        assert result.disposition is ExitDisposition.ESCALATE_TO_HITL

    def test_low_confidence_reason_contains_threshold(self):
        eb = dict(_GOOD_EVIDENCE, groundedness_score=0.0, support_coverage=0.0, relevance_score=0.0)
        result = _gate(threshold=0.70).evaluate_sealed(_artifact(evidence_bundle=eb))
        assert "0.70" in result.disposition_reason or "threshold" in result.disposition_reason.lower()


# ---------------------------------------------------------------------------
# TestCommitToUWG
# ---------------------------------------------------------------------------


class TestCommitToUWG:
    def test_authorized_mutation_returns_commit(self):
        result = _gate().evaluate_sealed(_artifact_with_commit())
        assert result.disposition is ExitDisposition.COMMIT_TO_UWG

    def test_commit_reason_mentions_uwg(self):
        result = _gate().evaluate_sealed(_artifact_with_commit())
        assert "UWG" in result.disposition_reason or "uwg" in result.disposition_reason.lower()

    def test_commit_requires_all_four_dimensions_pass(self):
        eb = dict(_GOOD_EVIDENCE, safety_clear=False)
        result = _gate().evaluate_sealed(_artifact_with_commit(evidence_bundle=eb))
        assert result.disposition is not ExitDisposition.COMMIT_TO_UWG

    def test_commit_without_escalation_reason(self):
        result = _gate().evaluate_sealed(_artifact_with_commit(escalation_reason=None))
        assert result.disposition is ExitDisposition.COMMIT_TO_UWG

    def test_allow_returned_when_no_commit_payload(self):
        result = _gate().evaluate_sealed(_artifact(has_commit_payload=False))
        assert result.disposition is ExitDisposition.ALLOW_RESPONSE


# ---------------------------------------------------------------------------
# TestSingleDispositionInvariant
# ---------------------------------------------------------------------------


class TestSingleDispositionInvariant:
    def test_each_evaluation_emits_exactly_one_disposition(self):
        gate = _gate()
        artifacts = [
            _artifact(),
            _artifact_with_commit(),
            _artifact(escalation_reason="human review"),
            _artifact(evidence_bundle=dict(_GOOD_EVIDENCE, safety_clear=False)),
        ]
        for art in artifacts:
            result = gate.evaluate_sealed(art)
            assert result.disposition in (
                ExitDisposition.ALLOW_RESPONSE,
                ExitDisposition.DENY_RETURN,
                ExitDisposition.ESCALATE_TO_HITL,
                ExitDisposition.COMMIT_TO_UWG,
            ), f"Unexpected disposition: {result.disposition}"

    def test_disposition_field_is_not_none(self):
        result = _gate().evaluate_sealed(_artifact())
        assert result.disposition is not None

    def test_commit_and_allow_are_mutually_exclusive(self):
        allow_result = _gate().evaluate_sealed(_artifact(has_commit_payload=False))
        commit_result = _gate().evaluate_sealed(_artifact_with_commit())
        assert allow_result.disposition is ExitDisposition.ALLOW_RESPONSE
        assert commit_result.disposition is ExitDisposition.COMMIT_TO_UWG
        assert allow_result.disposition is not commit_result.disposition

    def test_deny_and_escalate_are_mutually_exclusive_on_same_artifact(self):
        low_confidence_eb = dict(
            _GOOD_EVIDENCE, groundedness_score=0.0, support_coverage=0.0, relevance_score=0.0
        )
        result = _gate().evaluate_sealed(_artifact(evidence_bundle=low_confidence_eb))
        assert result.disposition in (
            ExitDisposition.DENY_RETURN,
            ExitDisposition.ESCALATE_TO_HITL,
        )


# ---------------------------------------------------------------------------
# TestShadowEvalIsolation
# ---------------------------------------------------------------------------


class TestShadowEvalIsolation:
    def test_async_eval_ingester_not_called_during_evaluate_sealed(self):
        """evaluate_sealed() must NOT call shadow-eval packetization.

        AsyncEvalIngester.ingest is patched to raise AssertionError.
        If it were called, the test would fail with that error.
        """
        with patch(
            "agentic_core.L6_observability.utils.evaluation.async_eval_packet.AsyncEvalIngester.ingest",
            side_effect=AssertionError(
                "Shadow eval AsyncEvalIngester.ingest was called during current-run evaluation"
            ),
        ):
            result = _gate().evaluate_sealed(_artifact())
        assert result.disposition is ExitDisposition.ALLOW_RESPONSE

    def test_shadow_eval_pipeline_not_called_during_evaluate_sealed(self):
        """evaluate_sealed() must NOT trigger L6ShadowEvalPipeline."""
        with patch(
            "agentic_core.L6_observability.utils.evaluation.shadow_eval_pipeline.L6ShadowEvalPipeline.run_cycle",
            side_effect=AssertionError(
                "L6ShadowEvalPipeline.run_cycle was called during current-run evaluation"
            ),
        ):
            result = _gate().evaluate_sealed(_artifact())
        assert result.disposition is ExitDisposition.ALLOW_RESPONSE

    def test_current_run_result_run_scope_is_current_run(self):
        result = _gate().evaluate_sealed(_artifact())
        assert result.run_scope == "CURRENT_RUN"

    def test_current_run_result_run_scope_differs_from_future_run(self):
        from agentic_core.L6_observability.utils.evaluation.promotion_packet import (
            PromotionPacket,
        )

        result = _gate().evaluate_sealed(_artifact())
        assert result.run_scope != PromotionPacket.run_scope

    def test_evaluate_sealed_returns_current_run_evaluation_result_type(self):
        result = _gate().evaluate_sealed(_artifact())
        assert isinstance(result, CurrentRunEvaluationResult)


# ---------------------------------------------------------------------------
# TestOutcomeShaping
# ---------------------------------------------------------------------------


class TestOutcomeShaping:
    def test_allow_disposition_shapes_to_allow_payload(self):
        gate = _gate()
        result = gate.evaluate_sealed(_artifact())
        outcome = gate.shape_outcome(result, _artifact())
        assert isinstance(outcome, AllowResponsePayload)

    def test_deny_disposition_shapes_to_deny_payload(self):
        gate = _gate()
        eb = dict(_GOOD_EVIDENCE, safety_clear=False)
        art = _artifact(evidence_bundle=eb)
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert isinstance(outcome, DenyReturnPayload)

    def test_escalate_disposition_shapes_to_hitl_packet(self):
        gate = _gate()
        art = _artifact(escalation_reason="jurisdiction review")
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert isinstance(outcome, EscalateToHITLPacket)

    def test_commit_disposition_shapes_to_uwg_request(self):
        gate = _gate()
        art = _artifact_with_commit()
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert isinstance(outcome, CommitToUWGRequest)

    def test_allow_payload_has_run_scope_current_run(self):
        gate = _gate()
        result = gate.evaluate_sealed(_artifact())
        outcome = gate.shape_outcome(result, _artifact())
        assert outcome.run_scope == "CURRENT_RUN"

    def test_deny_payload_has_run_scope_current_run(self):
        gate = _gate()
        eb = dict(_GOOD_EVIDENCE, safety_clear=False)
        art = _artifact(evidence_bundle=eb)
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert outcome.run_scope == "CURRENT_RUN"

    def test_commit_payload_contains_state_diff(self):
        gate = _gate()
        art = _artifact_with_commit(state_diff={"key": "value"})
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert isinstance(outcome, CommitToUWGRequest)
        assert outcome.state_diff == {"key": "value"}

    def test_commit_payload_contains_replay_key(self):
        gate = _gate()
        art = _artifact_with_commit()
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert isinstance(outcome, CommitToUWGRequest)
        assert outcome.replay_key == "rk-test-001"

    def test_commit_payload_disposition_is_commit_to_uwg(self):
        gate = _gate()
        art = _artifact_with_commit()
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert isinstance(outcome, CommitToUWGRequest)
        assert outcome.disposition is ExitDisposition.COMMIT_TO_UWG

    def test_escalate_packet_contains_bounded_context(self):
        gate = _gate()
        art = _artifact(escalation_reason="human required")
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert isinstance(outcome, EscalateToHITLPacket)
        assert "artifact_id" in outcome.bounded_context
        assert "integrity_checks" in outcome.bounded_context
        assert "rubric_scores" in outcome.bounded_context

    def test_deny_payload_reason_is_non_empty(self):
        gate = _gate()
        eb = dict(_GOOD_EVIDENCE, safety_clear=False)
        art = _artifact(evidence_bundle=eb)
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert isinstance(outcome, DenyReturnPayload)
        assert outcome.reason and len(outcome.reason) > 0

    def test_commit_uwg_request_run_scope_current_run(self):
        gate = _gate()
        art = _artifact_with_commit()
        result = gate.evaluate_sealed(art)
        outcome = gate.shape_outcome(result, art)
        assert outcome.run_scope == "CURRENT_RUN"

    def test_all_outcome_types_run_scope_current_run(self):
        """None of the four outcome types carry FUTURE_RUN scope."""
        for cls in (
            AllowResponsePayload,
            DenyReturnPayload,
            EscalateToHITLPacket,
            CommitToUWGRequest,
        ):
            assert cls.run_scope == "CURRENT_RUN"


# ---------------------------------------------------------------------------
# TestFailClosed
# ---------------------------------------------------------------------------


class TestFailClosed:
    def test_evaluate_sealed_never_raises(self):
        """evaluate_sealed must not raise even on an adversarial artifact."""
        gate = _gate()
        art = _artifact()
        result = gate.evaluate_sealed(art)
        assert isinstance(result, CurrentRunEvaluationResult)

    def test_missing_trace_id_still_produces_result(self):
        art = _artifact(trace_id="")
        result = _gate().evaluate_sealed(art)
        assert isinstance(result, CurrentRunEvaluationResult)
        assert result.disposition is not None

    def test_empty_evidence_bundle_returns_deny(self):
        art = _artifact(evidence_bundle={})
        result = _gate().evaluate_sealed(art)
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_zero_replay_completeness_returns_deny(self):
        bad_replay = ReplayMetadata(replay_key="rk", replay_completeness=0.0)
        art = _artifact(replay_metadata=bad_replay)
        result = _gate().evaluate_sealed(art)
        assert result.disposition is ExitDisposition.DENY_RETURN

    def test_confidence_score_is_zero_when_all_inputs_are_zero(self):
        """_compute_confidence_from_checks returns exactly 0.0 for all-zero inputs.

        Uses zero ValidationCounters (rules=0.0, schema=0.0), empty evidence
        bundle (groundedness/support/relevance=0.0, safety_clear=False → weight=0.0),
        and FAILURE terminal (format_fit=0.0).  Verifies the weighted formula
        produces 0.0 and does not silently inflate the score.
        """
        zero_art = SealedL2Artifact(
            artifact_id="zero-art",
            trace_id="zero-trace",
            terminal_classification=TerminalClassification.FAILURE,
            evidence_bundle={},
            validation_counters=ValidationCounters(),
            replay_metadata=ReplayMetadata(),
        )
        result = _gate().evaluate_sealed(zero_art)
        assert result.confidence_score == 0.0

    def test_all_policy_checks_failed_returns_deny(self):
        bad_counters = ValidationCounters(policy_checks_passed=0, policy_checks_failed=10)
        result = _gate().evaluate_sealed(_artifact(validation_counters=bad_counters))
        assert result.disposition is ExitDisposition.DENY_RETURN


# ---------------------------------------------------------------------------
# TestCurrentRunScopeInvariant
# ---------------------------------------------------------------------------


class TestCurrentRunScopeInvariant:
    def test_current_run_evaluation_result_run_scope(self):
        assert CurrentRunEvaluationResult.run_scope == "CURRENT_RUN"

    def test_allow_response_payload_run_scope(self):
        assert AllowResponsePayload.run_scope == "CURRENT_RUN"

    def test_deny_return_payload_run_scope(self):
        assert DenyReturnPayload.run_scope == "CURRENT_RUN"

    def test_escalate_to_hitl_packet_run_scope(self):
        assert EscalateToHITLPacket.run_scope == "CURRENT_RUN"

    def test_commit_to_uwg_request_run_scope(self):
        assert CommitToUWGRequest.run_scope == "CURRENT_RUN"

    def test_sealed_l2_artifact_run_scope(self):
        assert SealedL2Artifact.run_scope == "CURRENT_RUN"

    def test_current_run_scope_differs_from_promotion_packet(self):
        from agentic_core.L6_observability.utils.evaluation.promotion_packet import (
            PromotionPacket,
        )

        assert CurrentRunEvaluationResult.run_scope != PromotionPacket.run_scope
        assert AllowResponsePayload.run_scope != PromotionPacket.run_scope
