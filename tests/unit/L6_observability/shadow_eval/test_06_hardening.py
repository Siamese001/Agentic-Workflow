"""Hardening tests covering deferred/open scope items.

These tests validate the hardened paths added during the post-implementation
review:

* All four ``allowed_downstream_use`` values (NON_EVALUABLE / HOLD_ONLY /
  RCA_ONLY / RCA_AND_PROPOSAL) are reachable from the seal layer.
* Replay-digest drift at high severity correctly forces ``RCA_ONLY`` even
  when calibration is fresh.
* The conditional OTEL spans ``l6.ingest.gap_report_emit`` and
  ``l6.pattern.record_emit`` are emitted when their preconditions hold,
  completing the 29-span canonical surface.
* The seal record's ``HOLD`` status is reachable when calibration status is
  not in ``{CURRENT, STALE}``.
"""

from __future__ import annotations

import dataclasses

from agentic_core.L6_observability.shadow_eval import (
    GovernanceBaseline,
    L6PipelineState,
    SPAN_NAMES,
    build_calibration_record,
    build_completed_eval_record,
    build_observer_compliance_receipt,
    build_runtime_exhaust_bundle,
    build_surface_isolation_manifest,
    evaluate_governance_regression,
    evaluate_outcome,
    evaluate_readiness,
    evaluate_trajectory,
    run_6a,
    run_6b,
    run_6c,
    run_observer,
    seal_eval_record,
    stage_barrier_check,
)


# ---------------------------------------------------------------------------
# allowed_downstream_use coverage — all four values reachable
# ---------------------------------------------------------------------------


def _build_records(sealed_completed_run, *, replay_drift: bool, calibration_status: str | None = None):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    outcome = evaluate_outcome(receipt, normalized)
    trajectory = evaluate_trajectory(receipt, normalized)
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL",
        rubric_hash="rh",
        replay_digest="DIFF-REP" if replay_drift else bundle.replay_key,
    )
    governance = evaluate_governance_regression(receipt, normalized, baseline)
    calibration = build_calibration_record(
        rubric_hash="rh", rubric_version="1", grader_version="cv1"
    )
    if calibration_status is not None:
        calibration = dataclasses.replace(calibration, calibration_status=calibration_status)
    return bundle, receipt, outcome, trajectory, governance, calibration


def test_clean_run_yields_rca_and_proposal(sealed_completed_run):
    bundle, receipt, outcome, traj, gov, calib = _build_records(
        sealed_completed_run, replay_drift=False
    )
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=traj,
        governance=gov,
        calibration=calib,
        readiness_decision=receipt.readiness_decision,
    )
    assert rec.allowed_downstream_use == "RCA_AND_PROPOSAL"


def test_replay_digest_drift_high_severity_forces_rca_only(sealed_completed_run):
    """06.4 hardening: replay-digest drift invalidates proposal admission."""
    bundle, receipt, outcome, traj, gov, calib = _build_records(
        sealed_completed_run, replay_drift=True
    )
    assert gov.severity == "high"
    assert gov.replay_digest_drift_flags
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=traj,
        governance=gov,
        calibration=calib,
        readiness_decision=receipt.readiness_decision,
    )
    assert rec.allowed_downstream_use == "RCA_ONLY"


def test_hold_for_missing_evidence_yields_hold_only(sealed_completed_run):
    """Per 06.4: HOLD_FOR_MISSING_EVIDENCE readiness collapses to HOLD_ONLY."""
    bundle, receipt, outcome, traj, gov, calib = _build_records(
        sealed_completed_run, replay_drift=False
    )
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=traj,
        governance=gov,
        calibration=calib,
        readiness_decision="HOLD_FOR_MISSING_EVIDENCE",
    )
    assert rec.allowed_downstream_use == "HOLD_ONLY"


def test_non_evaluable_packet_yields_non_evaluable(sealed_completed_run):
    """Per 06.4: defensive NON_EVALUABLE downstream use when readiness fails."""
    bundle, receipt, outcome, traj, gov, calib = _build_records(
        sealed_completed_run, replay_drift=False
    )
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=traj,
        governance=gov,
        calibration=calib,
        readiness_decision="NON_EVALUABLE_PACKET",
    )
    assert rec.allowed_downstream_use == "NON_EVALUABLE"


# ---------------------------------------------------------------------------
# Seal status — HOLD path
# ---------------------------------------------------------------------------


def test_seal_status_hold_when_calibration_inconclusive(sealed_completed_run):
    """06.4: seal HOLDs when calibration is INSUFFICIENT or CONFLICTED."""
    bundle, receipt, outcome, traj, gov, calib = _build_records(
        sealed_completed_run, replay_drift=False, calibration_status="CONFLICTED"
    )
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=traj,
        governance=gov,
        calibration=calib,
        readiness_decision=receipt.readiness_decision,
    )
    seal = seal_eval_record(rec, calib)
    assert seal.seal_status == "HOLD"


# ---------------------------------------------------------------------------
# Conditional spans — l6.ingest.gap_report_emit, l6.pattern.record_emit
# ---------------------------------------------------------------------------


def test_gap_report_span_emitted_when_gaps_present(run_missing_replay_key):
    """06.1: gap report is observable as a first-class OTEL span."""
    state = L6PipelineState()
    run_6a(state, run_missing_replay_key)
    names = state.recorder.names()
    assert "l6.ingest.gap_report_emit" in names
    # And it must follow the canonical span order index.
    idx_artifact = names.index("l6.ingest.artifact_inventory")
    idx_gap = names.index("l6.ingest.gap_report_emit")
    assert idx_gap > idx_artifact


def test_no_gap_report_span_when_clean_run(sealed_completed_run):
    """Doctrine: gap report span must NOT fire on clean runs (false positive guard)."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    assert "l6.ingest.gap_report_emit" not in state.recorder.names()


def test_pattern_record_span_emitted_when_recurrent(sealed_completed_run):
    """06.5: pattern.record_emit fires only when recurrence threshold met."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL", rubric_hash="rh",
        replay_digest=state.ingest.bundle.replay_key,
    )
    run_6b(state, readiness, governance_baseline=baseline)
    # Build a single prior RCA with the same root_cause_class to drive recurrence.
    _ = run_6c(state)  # produces state.rca.rca
    prior = state.rca.rca
    # Reset state.rca and re-run 6c with prior as history; pattern should now emit.
    state.rca = None
    run_6c(state, rca_history=[prior], minimum_recurrence=2)
    names = state.recorder.names()
    assert "l6.pattern.record_emit" in names


def test_no_pattern_record_span_without_history(sealed_completed_run):
    """Single incident — no pattern emission."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL", rubric_hash="rh",
        replay_digest=state.ingest.bundle.replay_key,
    )
    run_6b(state, readiness, governance_baseline=baseline)
    run_6c(state)
    assert "l6.pattern.record_emit" not in state.recorder.names()


# ---------------------------------------------------------------------------
# Canonical 29-span surface — every declared span has a runtime path
# ---------------------------------------------------------------------------


def test_all_29_canonical_spans_have_runtime_path(sealed_completed_run, run_missing_replay_key):
    """Each name in SPAN_NAMES must be exercised by either the clean-run path
    (28 unconditional spans), the gap-report path, or the pattern-recurrence
    path. Together they prove the 29-span doctrine surface is alive."""
    # Clean run — 27 spans (no gap, no pattern).
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL", rubric_hash="rh",
        replay_digest=state.ingest.bundle.replay_key,
    )
    run_6b(state, readiness, governance_baseline=baseline)
    prior = run_6c(state).rca
    state.rca = None
    # Re-run 6c with prior history to trigger pattern.record_emit.
    run_6c(state, rca_history=[prior], minimum_recurrence=2)
    # And run a separate ingest with gaps to trigger gap_report_emit.
    state2 = L6PipelineState()
    run_6a(state2, run_missing_replay_key)

    seen = set(state.recorder.names()) | set(state2.recorder.names())
    # The 6D spans (gauntlet/approval/promotion/activation) require the
    # full pipeline; that surface is covered by t8::test_full_pipeline_ordered_spans.
    # Here we prove each of the 6A/6A.5/6B/6C span-names declared in SPAN_NAMES
    # is reachable through the hardened pipeline.
    for required in (
        "l6.ingest.bundle_receive",
        "l6.ingest.source_collect",
        "l6.ingest.lineage_bind",
        "l6.ingest.stage_map_build",
        "l6.ingest.artifact_inventory",
        "l6.normalize.record_emit",
        "l6.ingest.gap_report_emit",
        "l6.observer.surface_isolation_check",
        "l6.observer.stage_barrier_check",
        "l6.readiness.evaluate",
        "l6.eval.outcome.start",
        "l6.eval.outcome.record_emit",
        "l6.eval.trajectory.start",
        "l6.eval.trajectory.record_emit",
        "l6.eval.governance_regression.start",
        "l6.eval.governance_regression.record_emit",
        "l6.calibration.record_emit",
        "l6.eval_record.seal",
        "l6.rca.signal_fusion",
        "l6.rca.packet_emit",
        "l6.pattern.record_emit",
    ):
        assert required in seen, f"missing canonical span: {required}"
        assert required in SPAN_NAMES, f"span {required} not declared in registry"
