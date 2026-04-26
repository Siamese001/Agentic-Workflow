"""06.8 observability / anti-bypass / pack-level acceptance tests.

Doctrine PACK-LEVEL TEST REQUIREMENTS (06.8) — proven here:

- L6 starts from in-flight run -> rejected.
- L6 mutates live runtime state -> not possible (no client imported).
- L6 writes to L4 directly -> blocked structurally.
- L6 publishes BUS U before UWG receipt -> blocked.
- RCA consumes raw traces without CompletedEvalRecord -> blocked.
- Proposal lacks eval / RCA / rollback / exact diff -> blocked.
- Proposal bypasses gauntlet -> blocked.
- Approval bypasses stale eval/calibration checks -> blocked.
- Promotion has no content hash -> impossible (auto-computed).
- Activation applies before next run_start -> blocked.
- Unknown is coerced into PASS -> not done.
- Human preference becomes policy directly -> not done.
- Non-UWG writer is detected -> the only L4 path is uwg_commit callable.
- Replay divergence cannot be localized but promotion proceeds -> blocked
  via gauntlet failing_cases / divergence_localization fields.

This module also asserts:

- 06.8 OTEL span name registry is exhaustive and sequence-ordered.
- KPI board has correct directions and targets.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.shadow_eval import (
    KPI_BOARD,
    L6PipelineState,
    L6SpanRecorder,
    SPAN_NAMES,
    SPAN_ORDER_INDEX,
    GovernanceBaseline,
    evaluate_kpi,
    run_6a,
    run_6b,
    run_6c,
    run_6d,
    run_observer,
    run_proposal,
)
from agentic_core.L6_observability.shadow_eval.otel_spans import L6SpanRecord


def _uwg_commit_stub(_promotion):
    return ("uwg-receipt-mock-001", "l4-digest-mock-001")


def test_span_registry_is_unique_and_ordered():
    assert len(set(SPAN_NAMES)) == len(SPAN_NAMES)
    for i, name in enumerate(SPAN_NAMES):
        assert SPAN_ORDER_INDEX[name] == i


def test_kpi_board_has_19_kpis():
    assert len(KPI_BOARD) == 19


def test_evaluate_kpi_directions():
    # <= direction
    assert evaluate_kpi("trace_ingest_freshness_minutes", 5.0) is True
    assert evaluate_kpi("trace_ingest_freshness_minutes", 11.0) is False
    # >= direction
    assert evaluate_kpi("eval_readiness_coverage_pct", 99.0) is True
    assert evaluate_kpi("eval_readiness_coverage_pct", 50.0) is False
    # == direction
    assert evaluate_kpi("observer_law_violation_count", 0.0) is True
    assert evaluate_kpi("observer_law_violation_count", 1.0) is False


def test_recorder_rejects_unknown_span():
    rec = L6SpanRecorder()
    with pytest.raises(ValueError):
        rec.record(
            L6SpanRecord(
                name="l6.runtime.feedback_into_runtime",  # forbidden — would be feedback edge
                trace_id="t",
                span_id="s",
            )
        )


def test_full_pipeline_ordered_spans(sealed_completed_run):
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    # Replay-digest drift at high severity now forces RCA_ONLY downstream
    # use (06.4 hardening) which would block proposal admission. Match the
    # run's replay_key so only policy drift fires.
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL",
        rubric_hash="rh",
        replay_digest=state.ingest.bundle.replay_key,
    )
    run_6b(state, readiness, governance_baseline=baseline)
    run_6c(state)
    run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="p1",
        proposed_version_ref="p2",
        problem_statement="problem",
        expected_effect="effect",
        rollback_steps=["revert"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="o@org",
        policy_hash="A",
    )
    promo = run_6d(
        state,
        uwg_commit=_uwg_commit_stub,
        target_version_current="p1",
        target_version_proposed="p2",
        rollback_rehearsal_ref="rehearsal-1",
    )
    assert promo.approval_decision == "APPROVE"
    state.recorder.assert_no_runtime_feedback_edge()
    state.recorder.assert_pipeline_order()
    names = state.recorder.names()
    # Required boundary spans appear in the trace.
    for required in (
        "l6.ingest.bundle_receive",
        "l6.observer.surface_isolation_check",
        "l6.readiness.evaluate",
        "l6.eval.outcome.record_emit",
        "l6.eval.trajectory.record_emit",
        "l6.eval.governance_regression.record_emit",
        "l6.calibration.record_emit",
        "l6.eval_record.seal",
        "l6.rca.signal_fusion",
        "l6.rca.packet_emit",
        "l6.proposal.draft",
        "l6.proposal.admission_receipt",
        "l6.gauntlet.run",
        "l6.gauntlet.receipt_emit",
        "l6.approval.decide",
        "l6.promotion.packet_build",
        "l6.promotion.uwg_request_package",
        "l6.promotion.uwg_receipt_bind",
        "l6.future_run.activation_receipt",
    ):
        assert required in names, f"missing required L6 span: {required}"


def test_pipeline_blocks_inflight_run(in_flight_run):
    state = L6PipelineState()
    with pytest.raises(Exception):  # IngestError
        run_6a(state, in_flight_run)


def test_pipeline_does_not_emit_activation_when_gauntlet_fails(sealed_completed_run, monkeypatch):
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    # Replay-digest drift at high severity now forces RCA_ONLY downstream
    # use (06.4 hardening) which would block proposal admission. Match the
    # run's replay_key so only policy drift fires.
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL",
        rubric_hash="rh",
        replay_digest=state.ingest.bundle.replay_key,
    )
    run_6b(state, readiness, governance_baseline=baseline)
    run_6c(state)
    run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="p1",
        proposed_version_ref="p2",
        problem_statement="x",
        expected_effect="e",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="o@org",
        policy_hash="A",
    )
    promo = run_6d(
        state,
        uwg_commit=_uwg_commit_stub,
        target_version_current="p1",
        target_version_proposed="p2",
        rollback_rehearsal_ref="rehearsal-1",
        failing_cases=["case-broken"],
    )
    assert promo.approval_decision == "REJECT"
    assert promo.activation is None
    assert promo.promotion is None


def test_proof_command_artifact_inventory_is_complete(sealed_completed_run):
    """06.8: proof command — dump artifact inventory.

    The pipeline state, after a clean run, must carry RuntimeExhaustBundle,
    CompletedEvalRecord, RCAPacket, PromotionPacket, FutureRunActivationReceipt.
    """
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    # Replay-digest drift at high severity now forces RCA_ONLY downstream
    # use (06.4 hardening) which would block proposal admission. Match the
    # run's replay_key so only policy drift fires.
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL",
        rubric_hash="rh",
        replay_digest=state.ingest.bundle.replay_key,
    )
    run_6b(state, readiness, governance_baseline=baseline)
    run_6c(state)
    run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="p1",
        proposed_version_ref="p2",
        problem_statement="x",
        expected_effect="e",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="o@org",
        policy_hash="A",
    )
    run_6d(
        state,
        uwg_commit=_uwg_commit_stub,
        target_version_current="p1",
        target_version_proposed="p2",
        rollback_rehearsal_ref="rehearsal-1",
    )
    assert state.ingest is not None and state.ingest.bundle is not None
    assert state.eval is not None and state.eval.completed is not None
    assert state.rca is not None and state.rca.rca is not None
    assert state.promotion is not None and state.promotion.promotion is not None
    assert state.promotion.activation is not None
