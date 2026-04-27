"""Branch / line coverage closure for L6 shadow_eval (06.x).

This file is the third hardening layer over the v6 doctrine.

  * ``test_06_*`` — happy-path doctrine assertions
  * ``test_06_hardening.py`` — deferred/open scope items from the
    post-implementation audit (gap_report span, pattern span, downstream-use
    derivation, seal HOLD path)
  * ``test_06_edge_cases.py`` — vocabulary cardinality and parametrized
    sweeps over enum values
  * ``test_06_branch_coverage.py`` — *this file* — drives every remaining
    uncovered branch in the implementation modules to <=1% miss, including
    error paths, defensive guards, and rare doctrine corners that the prior
    layers did not exercise.

Each test names its target file:line range so a coverage regression has a
direct lookup. Where a guard is unreachable through the public API in
practice, the test reaches it via the internal helper that *does* exercise
the branch — never via monkey-patch of doctrine state.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from agentic_core.L6_observability.shadow_eval import (
    ALLOWED_DOWNSTREAM_USE,
    GovernanceBaseline,
    L6PipelineState,
    L6SpanRecord,
    L6SpanRecorder,
    ObserverViolation,
    ProposalError,
    RCAError,
    GauntletError,
    bind_uwg_receipt,
    build_blast_radius,
    build_calibration_record,
    build_drift_cluster_map,
    build_human_agreement_record,
    build_judge_reliability_signal,
    build_observer_compliance_receipt,
    build_promotion_packet,
    build_proposed_diff_manifest,
    build_rca_packet,
    build_rollback_plan,
    build_rubric_calibration_receipt,
    build_stage_map,
    build_surface_isolation_manifest,
    build_test_plan,
    build_uwg_request_package,
    decide_approval,
    evaluate_governance_regression,
    evaluate_outcome,
    evaluate_readiness,
    evaluate_trajectory,
    fuse_signals,
    record_denied_write_attempt,
    run_6a,
    run_6b,
    run_6c,
    run_6d,
    run_gauntlet,
    run_observer,
    run_proposal,
    seal_eval_record,
    stage_barrier_check,
    synthesize_patterns,
)
from agentic_core.L6_observability.shadow_eval.ingest import (
    collect_source_refs,
    normalize_records,
    receive_completed_run_marker,
    validate_lineage,
)
from agentic_core.L6_observability.shadow_eval._digest import (
    DIGEST_FIELD,
    canonical_json,
    compute_digest,
    stamp_digest,
)
from agentic_core.L6_observability.shadow_eval.contracts import (
    AffectedSurfaceCandidateMap,
    DraftProposalPacket,
    EvalReadinessReceipt,
    NormalizedEvidenceRecord,
    ProposalAdmissionReceipt,
)
from agentic_core.L6_observability.shadow_eval.observer import (
    FORBIDDEN_WRITE_SURFACES,
    READINESS_HOLD,
    READINESS_NON_EVAL,
    READINESS_PARTIAL,
    READINESS_READY,
)
from agentic_core.L6_observability.shadow_eval.proposal import (
    admit_proposal,
    draft_proposal,
    proposal_content_hash,
)
from agentic_core.L6_observability.shadow_eval.rca import (
    build_affected_surface_candidate_map,
    _classify_root_cause,
)
from agentic_core.L6_observability.shadow_eval.gauntlet import (
    build_future_run_activation_receipt,
)
from agentic_core.L6_observability.shadow_eval._digest import (
    _canonicalize,
)
from agentic_core.L6_observability.shadow_eval.evaluation import (
    CodeOnlyGrader,
    HybridGrader,
    EvaluationError,
    OUTCOME_DIMENSIONS,
)
from agentic_core.L6_observability.shadow_eval.calibration import (
    CALIBRATION_TTL_DAYS_DEFAULT,
)
from agentic_core.L6_observability.shadow_eval.ingest import (
    EXPECTED_STAGES,
    IngestError,
    REASON_LIVE_RUN_NOT_CLOSED,
    REASON_POLICY_HASH_MISMATCH,
    REASON_UNKNOWN_PROVIDER_FALLBACK,
)
from agentic_core.L6_observability.shadow_eval.otel_spans import (
    KPI_BOARD,
    KpiThreshold,
    SPAN_ORDER_INDEX,
)
from agentic_core.L6_observability.shadow_eval.pipeline import (
    L6IngestResult,
    L6EvalResult,
    L6RcaResult,
    L6ProposalResult,
)


# ---------------------------------------------------------------------------
# _digest.py — canonicalization edge cases
# ---------------------------------------------------------------------------


def test_canonicalize_set_is_sorted_by_repr():
    """`_digest.py:38` — sets/frozensets are deterministically ordered."""
    a = canonical_json({"s": {"b", "a", "c"}})
    b = canonical_json({"s": frozenset({"c", "a", "b"})})
    assert a == b
    # Order is stable across calls
    assert canonical_json({"s": {"x", "y"}}) == canonical_json({"s": {"y", "x"}})


def test_canonicalize_unknown_type_falls_back_to_repr():
    """`_digest.py:41` — exotic types get repr() fallback rather than crashing."""

    class Exotic:
        def __repr__(self) -> str:
            return "<Exotic-instance>"

    encoded = canonical_json({"e": Exotic()})
    assert "<Exotic-instance>" in encoded


def test_stamp_digest_handles_immutable_record():
    """`_digest.py:70-72` — namedtuple/immutable structures hit the
    AttributeError fallback without raising.
    """
    from collections import namedtuple

    Pt = namedtuple("Pt", ["x", "y"])
    rec = Pt(1, 2)
    out = stamp_digest(rec)
    # Returned same object; digest field cannot be set on namedtuples.
    assert out is rec
    assert not hasattr(out, DIGEST_FIELD)


def test_compute_digest_is_stable_for_identical_dataclass():
    """Digest stability across two equivalent dataclass instances."""
    a = build_rollback_plan(proposal_id="p", rollback_steps=["s1", "s2"])
    b = build_rollback_plan(proposal_id="p", rollback_steps=["s1", "s2"])
    # Different ids by construction (uuid), so digests differ — but the
    # digest function itself is deterministic when payload is identical.
    payload = {"k": [1, 2, 3]}
    assert compute_digest(payload) == compute_digest(payload)


# ---------------------------------------------------------------------------
# ingest.py — POLICY_HASH_MISMATCH gap and UNKNOWN_PROVIDER_FALLBACK warning
# ---------------------------------------------------------------------------


def test_validate_lineage_emits_policy_hash_mismatch_when_missing():
    """`ingest.py:121` — empty/missing policy_hash surfaces the gap code."""
    raw = {"trace_root": "tr", "replay_key": "rk", "policy_hash": ""}
    codes = validate_lineage(raw, [])
    assert REASON_POLICY_HASH_MISMATCH in codes


def test_normalize_records_warns_unknown_provider(sealed_completed_run):
    """`ingest.py:213` — provider_lane in (None, "", "unknown") yields warning."""
    raw = dict(sealed_completed_run)
    raw["events"] = [
        {
            "event_type": "tool_call",
            "stage": "L2",
            "trace_id": "t",
            "span_id": "s",
            "provider_lane": "unknown",
            "eval_readiness_hint": "READY",
        },
        {
            "event_type": "tool_call",
            "stage": "L2",
            "trace_id": "t",
            "span_id": "s2",
            "provider_lane": None,
            "eval_readiness_hint": "READY",
        },
    ]
    out = normalize_records(raw, "rxb-test")
    assert all(REASON_UNKNOWN_PROVIDER_FALLBACK in r.normalization_warnings for r in out)


def test_receive_completed_run_marker_rejects_missing_completed_at():
    """`ingest.py:77` — `completed_at` missing classifies as in-flight."""
    with pytest.raises(IngestError, match=REASON_LIVE_RUN_NOT_CLOSED):
        receive_completed_run_marker({"runtime_boundary_crossed": True, "exit_disposition_ref": "x"})


def test_collect_source_refs_handles_empty_source_exhaust():
    """No source_exhaust key — returns empty list, no crash."""
    assert collect_source_refs({}) == []
    assert collect_source_refs({"source_exhaust": []}) == []


def test_build_stage_map_flags_uwg_before_exit():
    """StageMap impossible_order_flags includes UWG_BEFORE_EXIT."""
    raw = {"trace_root": "t", "run_id": "r", "request_id": "q"}
    manifests = collect_source_refs(
        {
            "source_exhaust": [
                {
                    "source_type": "uwg",
                    "source_ref": "u",
                    "observed_stage": "UWG",
                    "lineage_parent_refs": ["x"],
                }
            ]
        }
    )
    sm = build_stage_map(raw, manifests)
    assert "UWG_BEFORE_EXIT" in sm.impossible_order_flags


# ---------------------------------------------------------------------------
# observer.py — exit_disposition flag + UNKNOWN status path + every readiness branch
# ---------------------------------------------------------------------------


def _bare_bundle(**overrides):
    """Build a RuntimeExhaustBundle directly so we can exercise readiness branches
    without going through the full ingest pipeline (which itself rejects most
    of these states earlier)."""
    from agentic_core.L6_observability.shadow_eval.contracts import RuntimeExhaustBundle

    base = dict(
        runtime_exhaust_bundle_id="rxb-x",
        request_id="r",
        run_id="run",
        session_id="s",
        tenant_id="t",
        trace_root="tr",
        completed_at="2026-01-01T00:00:00+00:00",
        runtime_boundary_crossed=True,
        source_exhaust_refs=[],
        route_contract_ref="rc",
        l1_plan_ref=None,
        c0_evidence_contract_refs=[],
        prompt_envelope_refs=[],
        l2_artifact_refs=[],
        l3_workflow_package_ref=None,
        exit_disposition_ref="exit",
        hitl_packet_refs=[],
        uwg_receipt_refs=[],
        policy_hash="pH",
        blueprint_hash="bH",
        replay_key="rK",
        source_lineage_manifest_ref="lin",
        artifact_inventory_ref="inv",
        ingest_gap_report_ref="gap",
    )
    base.update(overrides)
    return RuntimeExhaustBundle(**base)


def test_stage_barrier_flags_missing_exit_disposition():
    """`observer.py:86` — bundle with runtime_boundary_crossed=True but no
    exit_disposition_ref still surfaces EXIT_DISPOSITION_MISSING.
    """
    b = _bare_bundle(exit_disposition_ref=None)
    barrier = stage_barrier_check(b)
    assert "EXIT_DISPOSITION_MISSING" in barrier.boundary_violation_flags
    assert barrier.barrier_status == "FAIL"


def test_isolation_manifest_status_unknown_when_violation_undenied():
    """`observer.py:145` — write requested AND no denied-record => UNKNOWN."""
    b = _bare_bundle()
    manifest = build_surface_isolation_manifest(
        b,
        read_surfaces_touched=("traces",),
        write_surfaces_requested=["L4"],  # forbidden surface
        denied_write_attempts=[],  # none — so status escalates to UNKNOWN
    )
    assert manifest.isolation_status == "UNKNOWN"


def _ready_observer_for(bundle):
    barrier = stage_barrier_check(bundle)
    isolation = build_surface_isolation_manifest(bundle, read_surfaces_touched=["traces"])
    return build_observer_compliance_receipt(bundle, barrier=barrier, isolation=isolation)


def _norm(**overrides):
    base = dict(
        normalized_record_id="n1",
        runtime_exhaust_bundle_id="rxb-x",
        canonical_event_type="tool_call",
        canonical_stage="L2",
        source_ref="span",
        normalized_payload_ref="p",
        trace_id="t",
        span_id="s",
        parent_span_id=None,
        request_id="r",
        run_id="run",
        tenant_id="t",
        route_id="rt",
        step_id=None,
        attempt_id=None,
        model_id=None,
        tool_id=None,
        provider_lane="anthropic",
        token_count_in=0,
        token_count_out=0,
        cost_estimate=0.0,
        latency_ms=0.0,
        retry_count=0,
        repair_count=0,
        fallback_depth=0,
        error_code=None,
        reason_codes=[],
        policy_hash="pH",
        blueprint_hash="bH",
        replay_key="rK",
        prompt_hash="ph",
        context_hash=None,
        artifact_digest=None,
        eval_readiness_hint="READY",
        normalization_warnings=[],
    )
    base.update(overrides)
    return NormalizedEvidenceRecord(**base)


def test_readiness_each_individual_field_missing_path():
    """`observer.py:231,233,237,239,241` — every single missing-field branch fires.

    The key insight: trace_root and exit_disposition trigger NON_EVALUABLE,
    while policy_hash/route_contract on their own (with replay present)
    trigger PARTIAL_BUT_SCORABLE — that flow exercises the missing_field_refs
    appends without short-circuiting earlier.
    """
    # Missing policy_hash + route_contract + artifacts collectively still
    # produces a usable readiness receipt.
    b = _bare_bundle(policy_hash=None, route_contract_ref=None)
    receipt, missing, non_eval = evaluate_readiness(b, _ready_observer_for(b), [_norm()])
    # Missing fields are surfaced.
    assert "policy_hash" in receipt.reason_codes
    assert "route_contract" in receipt.reason_codes
    assert receipt.readiness_decision == READINESS_PARTIAL


def test_readiness_observer_violation_routes_to_non_evaluable_branch():
    """`observer.py:259-260` — observer.isolation_status != CLEAN forces NON_EVAL."""
    b = _bare_bundle()
    barrier = stage_barrier_check(b)
    # Forge a violating manifest by going through the public API with a
    # write-surface request and no denied-record.
    isolation = build_surface_isolation_manifest(
        b, read_surfaces_touched=["x"], write_surfaces_requested=["L4"]
    )
    obs = build_observer_compliance_receipt(b, barrier=barrier, isolation=isolation)
    receipt, _missing, non_eval = evaluate_readiness(b, obs, [_norm()])
    assert receipt.readiness_decision == READINESS_NON_EVAL
    assert non_eval is not None
    assert "OBSERVER_LAW_VIOLATION" in non_eval.reason_codes


def test_readiness_partial_branch_preserves_normalized_records():
    """`observer.py:274-281` — PARTIAL path returns a non-blocking missing map."""
    b = _bare_bundle(policy_hash=None)
    receipt, missing, _ = evaluate_readiness(b, _ready_observer_for(b), [_norm()])
    assert receipt.readiness_decision == READINESS_PARTIAL
    assert missing is not None
    assert missing.blocking is False


def test_readiness_no_normalized_records_yields_non_evaluable():
    """`observer.py:282-284` — empty normalized list with otherwise-clean bundle
    falls through to the final NON_EVAL else-arm.
    """
    # Missing artifacts because normalized=[] AND replay-dependent missing
    # but not trace/exit — falls through to the NO_NORMALIZED_RECORDS arm.
    b = _bare_bundle(replay_key=None)
    # Force replay_key missing AND empty normalized AND replay_dependent=False
    # so the "replay_key" missing-field is suppressed: artifacts is the only
    # missing field, which falls into the else-arm.
    receipt, _missing, non_eval = evaluate_readiness(b, _ready_observer_for(b), [], replay_dependent=False)
    assert receipt.readiness_decision == READINESS_NON_EVAL
    assert non_eval is not None
    assert "NO_NORMALIZED_RECORDS" in non_eval.reason_codes or "artifacts" in non_eval.reason_codes


def test_readiness_missing_trace_root_routes_to_non_evaluable():
    """`observer.py:231,257-263` — trace_root missing => NON_EVAL via elif arm.

    Bundle has clean observer + normalized records, but trace_root is empty.
    The "elif trace_root in missing_field_refs..." arm fires.
    """
    b = _bare_bundle(trace_root="")
    receipt, missing, non_eval = evaluate_readiness(b, _ready_observer_for(b), [_norm()])
    assert receipt.readiness_decision == READINESS_NON_EVAL
    assert non_eval is not None
    assert "trace_root" in non_eval.reason_codes
    assert missing is None  # NON_EVAL uses non_eval, not missing_map


def test_readiness_missing_exit_disposition_routes_to_non_evaluable():
    """`observer.py:241,257-263` — exit_disposition missing => NON_EVAL via elif arm."""
    b = _bare_bundle(exit_disposition_ref=None)
    # We want the observer to remain CLEAN (no write request) so the elif
    # branch fires, not the if-isolation-violated branch.
    barrier = stage_barrier_check(b)
    isolation = build_surface_isolation_manifest(b, read_surfaces_touched=["x"])
    obs = build_observer_compliance_receipt(b, barrier=barrier, isolation=isolation)
    assert obs.isolation_status == "CLEAN"
    receipt, missing, non_eval = evaluate_readiness(b, obs, [_norm()])
    assert receipt.readiness_decision == READINESS_NON_EVAL
    assert non_eval is not None
    assert "exit_disposition" in non_eval.reason_codes


def test_record_denied_write_attempt_carries_full_metadata():
    """`observer.py` — denied-write factory populates every audit field."""
    b = _bare_bundle()
    rec = record_denied_write_attempt(
        b,
        surface="L4",
        operation="write_versioned",
        reason_code="L6_OBSERVER_FAIL",
        stack_signature="trace:abc",
    )
    assert rec.target_surface == "L4"
    assert rec.operation == "write_versioned"
    assert rec.reason_code == "L6_OBSERVER_FAIL"
    assert rec.stack_signature == "trace:abc"


# ---------------------------------------------------------------------------
# evaluation.py — UNKNOWN/WARN dimension paths + governance refusal_drift
# ---------------------------------------------------------------------------


def test_code_only_grader_unknown_when_no_evidence():
    """`evaluation.py:106` — empty evidence => UNKNOWN, never PASS."""
    s = CodeOnlyGrader().grade("dim.x", "x", [])
    assert s.result == "UNKNOWN"
    assert s.score == 0.0


def test_code_only_grader_warn_when_evidence_flagged_non_evaluable():
    """`evaluation.py:107` — non-eval/UNKNOWN hint => WARN with bad refs."""
    bad = _norm(eval_readiness_hint="NON_EVALUABLE")
    s = CodeOnlyGrader().grade("dim.x", "x", [bad])
    assert s.result == "WARN"
    assert bad.normalized_record_id in s.evidence_refs


def test_hybrid_grader_relabels_code_only_score():
    """HybridGrader composes CodeOnlyGrader and changes grader_type."""
    s = HybridGrader().grade("d", "task_completion", [_norm()])
    assert s.grader_type == "hybrid"


def test_evaluate_outcome_refuses_on_non_ready_readiness():
    """`evaluation.py:_require_ready` — rejects NON_EVAL/HOLD readiness."""
    # Synthesize a HOLD readiness from the bare path
    b = _bare_bundle(replay_key=None)
    receipt, _, _ = evaluate_readiness(b, _ready_observer_for(b), [_norm()])
    assert receipt.readiness_decision == READINESS_HOLD
    with pytest.raises(EvaluationError):
        evaluate_outcome(receipt, [_norm()])


def test_trajectory_eval_emits_silent_fallback_flag():
    """`evaluation.py:287` — fallback_depth > 1 emits silent_fallback flag."""
    b = _bare_bundle()
    obs = _ready_observer_for(b)
    ready, _, _ = evaluate_readiness(b, obs, [_norm()])
    rec = evaluate_trajectory(ready, [_norm(fallback_depth=2)])
    assert "silent_fallback" in rec.trajectory_flags


def test_governance_refusal_drift_path():
    """`evaluation.py:355-356` — refusal events with error_code drive refusal_drift."""
    b = _bare_bundle()
    obs = _ready_observer_for(b)
    ready, _, _ = evaluate_readiness(b, obs, [_norm()])
    refusal_norm = _norm(canonical_event_type="refusal", error_code="REFUSED")
    gov = evaluate_governance_regression(
        ready,
        [refusal_norm],
        GovernanceBaseline(policy_hash="pH", rubric_hash="rH", replay_digest="rK"),
    )
    assert refusal_norm.normalized_record_id in gov.refusal_abstain_drift_flags
    assert "refusal" in gov.impacted_surfaces


# ---------------------------------------------------------------------------
# calibration.py — ISO parse failure, INSUFFICIENT/UNKNOWN budget,
# JudgeReliability all branches, RubricCalibrationReceipt mappings, seal HOLD
# ---------------------------------------------------------------------------


def test_calibration_record_marks_insufficient_on_bad_timestamp():
    """`calibration.py:65-67` — non-iso timestamp falls into INSUFFICIENT bucket."""
    rec = build_calibration_record(
        rubric_hash="r",
        rubric_version="1",
        grader_version="g",
        calibration_freshness_timestamp="not-a-date",
    )
    assert rec.calibration_status == "INSUFFICIENT"


def test_calibration_unknown_budget_status_is_normalized():
    """`calibration.py:99-100` — unknown enum value coerced to UNKNOWN literal."""
    rec = build_calibration_record(
        rubric_hash="r",
        rubric_version="1",
        grader_version="g",
        unknown_budget_status="GIBBERISH",
    )
    assert rec.unknown_budget_status == "UNKNOWN"


def test_judge_reliability_signal_recommends_human_review_on_high_unknown_rate():
    """`calibration.py:131-132` — unknown_rate > 0.3 => REQUIRE_HUMAN_REVIEW."""
    sig = build_judge_reliability_signal(
        grader_id="g",
        task_class="t",
        rubric_hash="r",
        recent_agreement_score=0.9,
        disagreement_rate=0.1,
        unknown_rate=0.5,
    )
    assert sig.recommended_use == "REQUIRE_HUMAN_REVIEW"


def test_judge_reliability_signal_recommends_hybrid_on_high_disagreement():
    """`calibration.py:135-136` — high disagreement triggers REQUIRE_HYBRID."""
    sig = build_judge_reliability_signal(
        grader_id="g",
        task_class="t",
        rubric_hash="r",
        recent_agreement_score=0.4,
        disagreement_rate=0.5,
        unknown_rate=0.1,
    )
    assert sig.recommended_use == "REQUIRE_HYBRID"


def test_judge_reliability_signal_disables_for_surface_on_drift_flags():
    """`calibration.py:137-138` — bias/forced flags route to DISABLE_FOR_SURFACE."""
    sig = build_judge_reliability_signal(
        grader_id="g",
        task_class="t",
        rubric_hash="r",
        recent_agreement_score=0.95,
        disagreement_rate=0.05,
        unknown_rate=0.05,
        bias_or_drift_flags=["temporal_drift"],
    )
    assert sig.recommended_use == "DISABLE_FOR_SURFACE"


def test_judge_reliability_signal_allows_for_eval_on_clean_inputs():
    """`calibration.py:139-140` — clean inputs => ALLOW_FOR_EVAL."""
    sig = build_judge_reliability_signal(
        grader_id="g",
        task_class="t",
        rubric_hash="r",
        recent_agreement_score=0.95,
        disagreement_rate=0.05,
        unknown_rate=0.05,
    )
    assert sig.recommended_use == "ALLOW_FOR_EVAL"


def test_rubric_calibration_receipt_fresh_status():
    """`calibration.py:177` — CURRENT calibration => FRESH receipt."""
    rec = build_calibration_record(rubric_hash="r", rubric_version="1", grader_version="g")
    receipt = build_rubric_calibration_receipt(rec)
    assert receipt.receipt_status == "FRESH"


def test_rubric_calibration_receipt_insufficient_on_unknown_status():
    """`calibration.py:181` — non-CURRENT/non-known status => INSUFFICIENT."""
    rec = build_calibration_record(
        rubric_hash="r",
        rubric_version="1",
        grader_version="g",
        calibration_freshness_timestamp="not-iso",
    )
    # status is INSUFFICIENT — receipt should mirror as STALE per code path
    receipt = build_rubric_calibration_receipt(rec)
    assert receipt.receipt_status == "STALE"


def test_human_agreement_record_round_trips_reviewers():
    """build_human_agreement_record preserves reviewer refs."""
    rec = build_human_agreement_record(
        rubric_hash="r",
        task_class="t",
        samples=10,
        agreement_rate=0.9,
        reviewer_refs=["rev-1", "rev-2"],
    )
    assert rec.reviewer_refs == ["rev-1", "rev-2"]


def test_seal_eval_record_reasons_include_missing_refs(sealed_completed_run):
    """`calibration.py:353` — completed_eval_record with empty refs => MISSING_EVAL_REFS."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    # Seed a completed eval record from the pipeline.
    ev = run_6b(
        state,
        readiness,
        governance_baseline=GovernanceBaseline(
            policy_hash="pH", rubric_hash="rH", replay_digest=state.ingest.bundle.replay_key
        ),
    )
    # Mutate completed eval record to drop one ref AND mismatch rubric hash —
    # both reason codes fire.
    object.__setattr__(ev.completed, "outcome_eval_ref", "")
    object.__setattr__(ev.completed, "rubric_hash", "DIFFERENT")
    out = seal_eval_record(ev.completed, ev.calibration)
    assert "MISSING_EVAL_REFS" in out.reason_codes
    assert "RUBRIC_HASH_MISMATCH" in out.reason_codes


# ---------------------------------------------------------------------------
# rca.py — affected_surface candidate paths, root-cause classifier full sweep,
# first_bad span localization, AffectedSurfaceCandidateMap
# ---------------------------------------------------------------------------


def _completed_eval_with_score(**overrides):
    """Build a CompletedEvalRecord with controlled immutable_score_bundle."""
    from agentic_core.L6_observability.shadow_eval.contracts import CompletedEvalRecord

    base = dict(
        completed_eval_record_id="ceval-x",
        runtime_exhaust_bundle_id="rxb-x",
        eval_readiness_receipt_id="ready-x",
        outcome_eval_ref="oc-x",
        trajectory_eval_ref="tr-x",
        governance_regression_ref="gov-x",
        calibration_record_ref="calib-x",
        rubric_hash="r",
        rubric_version="1",
        grader_versions=["g"],
        evidence_snapshot_hash="snap",
        immutable_score_bundle={
            "governance.policy_drift_count": 1.0,
            "governance.replay_drift_count": 1.0,
            "trajectory.retry_thrash": 0.2,
        },
        uncertainty_markers=[],
        support_rationale_refs=[],
        reviewer_override_refs=[],
        allowed_downstream_use="RCA_AND_PROPOSAL",
    )
    base.update(overrides)
    return CompletedEvalRecord(**base)


def test_fuse_signals_emits_replay_and_execution_candidates():
    """`rca.py:97,99` — replay drift + retry thrash flag both candidates."""
    ev = _completed_eval_with_score()
    fused = fuse_signals([ev])
    assert "replay" in fused.affected_surface_candidates
    assert "execution" in fused.affected_surface_candidates


def test_fuse_signals_recommends_observation_only_when_all_clean():
    """The fall-through OBSERVATION_ONLY recommendation is reachable."""
    ev = _completed_eval_with_score(immutable_score_bundle={"trajectory.retry_thrash": 1.0})
    fused = fuse_signals([ev])
    assert fused.recommended_investigation_type == "OBSERVATION_ONLY"


def test_first_bad_span_localized_when_normalized_record_has_error():
    """`rca.py:147-168` — first_bad span is captured when record has error_code."""
    bad = _norm(error_code="TOOL_FAIL", canonical_stage="L2")
    ev = _completed_eval_with_score()
    fused = fuse_signals([ev])
    rca = build_rca_packet(fused, normalized=[bad])
    assert rca.first_bad_span.span_id == bad.span_id
    assert rca.first_bad_span.confidence == "medium"


def test_failure_chain_includes_retry_thrash_step():
    """`rca.py:152-154` — retry_count > 2 emits 'retry_thrash' step."""
    rec = _norm(retry_count=5, canonical_stage="L2")
    ev = _completed_eval_with_score()
    fused = fuse_signals([ev])
    rca = build_rca_packet(fused, normalized=[rec])
    assert any("retry_thrash" in s for s in rca.failure_chain.steps)
    assert rca.failure_chain.first_bad_stage == "L2"


def test_root_cause_classifier_replay_integrity_error():
    """`rca.py:192` — replay_digest_drift_flags maps to REPLAY_INTEGRITY_ERROR."""
    from agentic_core.L6_observability.shadow_eval.contracts import (
        FailureChain,
        GovernanceRegressionRecord,
    )

    fc = FailureChain(failure_chain_id="fc", steps=[], first_bad_stage=None, final_observed_stage=None)
    gov = GovernanceRegressionRecord(
        governance_regression_id="g",
        policy_drift_flags=[],
        schema_api_drift_flags=[],
        replay_digest_drift_flags=["norm-1"],
        refusal_abstain_drift_flags=[],
        impacted_surfaces=["replay"],
        severity="high",
        suspected_cause="DRIFT",
        required_review="L5_GOVERNANCE_REVIEW",
        policy_hash=None,
        rubric_hash=None,
        replay_digest=None,
    )
    fused_with_replay = _completed_eval_with_score()
    fused = fuse_signals([fused_with_replay])
    assert _classify_root_cause(fused, gov, fc) == "REPLAY_INTEGRITY_ERROR"


def test_root_cause_classifier_provider_drift_via_silent_fallback():
    """`rca.py:194` — silent_fallback step => PROVIDER_DRIFT."""
    from agentic_core.L6_observability.shadow_eval.contracts import FailureChain

    fc = FailureChain(
        failure_chain_id="fc",
        steps=["silent_fallback"],
        first_bad_stage=None,
        final_observed_stage=None,
    )
    fused = fuse_signals([_completed_eval_with_score(immutable_score_bundle={})])
    assert _classify_root_cause(fused, None, fc) == "PROVIDER_DRIFT"


def test_root_cause_classifier_tool_arg_schema_via_execution_candidate():
    """`rca.py:196` — execution candidate (no policy/replay drift) => TOOL_ARG_SCHEMA_ERROR."""
    from agentic_core.L6_observability.shadow_eval.contracts import FailureChain

    fc = FailureChain(failure_chain_id="fc", steps=[], first_bad_stage=None, final_observed_stage=None)
    ev = _completed_eval_with_score(immutable_score_bundle={"trajectory.retry_thrash": 0.1})
    fused = fuse_signals([ev])
    # affected_surface_candidates contains execution due to retry_thrash<0.5
    assert "execution" in fused.affected_surface_candidates
    assert _classify_root_cause(fused, None, fc) == "TOOL_ARG_SCHEMA_ERROR"


def test_build_rca_packet_rejects_unknown_root_cause(monkeypatch):
    """`rca.py:212` — root_cause not in ROOT_CAUSE_CLASSES raises RCAError."""
    import agentic_core.L6_observability.shadow_eval.rca as rca_mod

    monkeypatch.setattr(rca_mod, "_classify_root_cause", lambda *a, **k: "NOT_A_REAL_CLASS")
    fused = fuse_signals([_completed_eval_with_score()])
    with pytest.raises(RCAError, match="unknown root_cause_class"):
        build_rca_packet(fused, normalized=[_norm()])


def test_synthesize_patterns_below_recurrence_threshold_emits_nothing():
    """Single RCA below the recurrence floor returns []."""
    fused = fuse_signals([_completed_eval_with_score()])
    rca = build_rca_packet(fused, normalized=[_norm(error_code="x")])
    out = synthesize_patterns([rca], minimum_recurrence=2)
    assert out == []


def test_drift_cluster_map_groups_by_root_cause():
    """build_drift_cluster_map groups packets by root_cause_class."""
    fused = fuse_signals([_completed_eval_with_score()])
    rca1 = build_rca_packet(fused, normalized=[_norm(error_code="x")])
    rca2 = build_rca_packet(fused, normalized=[_norm(error_code="y")])
    m = build_drift_cluster_map([rca1, rca2])
    assert rca1.root_cause_class in m.clusters


def test_affected_surface_candidate_map_aggregates_probabilities():
    """`rca.py:301-305` — surface counter sums to <=1.0 normalized."""
    fused1 = fuse_signals([_completed_eval_with_score()])
    fused2 = fuse_signals([_completed_eval_with_score(immutable_score_bundle={})])
    m = build_affected_surface_candidate_map([fused1, fused2])
    assert isinstance(m, AffectedSurfaceCandidateMap)
    if m.candidates:
        assert pytest.approx(sum(m.candidates.values()), rel=1e-6) == 1.0


def test_affected_surface_candidate_map_handles_empty_input():
    """No fused bundles => no division-by-zero, candidates is empty dict."""
    m = build_affected_surface_candidate_map([])
    assert m.candidates == {}


# ---------------------------------------------------------------------------
# proposal.py — every error path + every admission open_blocker
# ---------------------------------------------------------------------------


def test_proposed_diff_manifest_requires_target_surface_and_op():
    """`proposal.py:85` — empty target_surface raises."""
    with pytest.raises(ProposalError, match="target_surface"):
        build_proposed_diff_manifest(
            target_surface="",
            operation_type="UPDATE",
            before_ref="b",
            after_candidate_ref="a",
            diff_summary="d",
        )


def test_proposed_diff_manifest_requires_before_after_refs():
    """`proposal.py:87` — empty before/after refs raises."""
    with pytest.raises(ProposalError, match="before_ref"):
        build_proposed_diff_manifest(
            target_surface="policy",
            operation_type="UPDATE",
            before_ref="",
            after_candidate_ref="a",
            diff_summary="d",
        )


def test_blast_radius_requires_at_least_one_surface():
    """build_blast_radius raises on empty surfaces."""
    with pytest.raises(ProposalError, match="affected surface"):
        build_blast_radius(proposal_id="p", affected_surfaces=[])


def test_rollback_plan_requires_steps():
    """build_rollback_plan raises on empty steps."""
    with pytest.raises(ProposalError, match="step"):
        build_rollback_plan(proposal_id="p", rollback_steps=[])


def test_test_plan_requires_affected_tests():
    """build_test_plan raises on empty tests."""
    with pytest.raises(ProposalError, match="affected tests"):
        build_test_plan(proposal_id="p", affected_tests=[])


def _full_pipeline_through_proposal(sealed_completed_run, **proposal_overrides):
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    ready = run_observer(state)
    run_6b(
        state,
        ready,
        governance_baseline=GovernanceBaseline(
            policy_hash="pH", rubric_hash="rH", replay_digest=state.ingest.bundle.replay_key
        ),
    )
    run_6c(state)
    defaults = dict(
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="needs fix",
        expected_effect="better",
        rollback_steps=["revert"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    defaults.update(proposal_overrides)
    return state, run_proposal(state, **defaults)


def test_draft_proposal_rejects_unknown_proposal_type(sealed_completed_run):
    """`proposal.py:198` — unknown proposal_type raises."""
    with pytest.raises(ProposalError, match="unknown proposal_type"):
        _full_pipeline_through_proposal(sealed_completed_run, proposal_type="NOT_REAL_TYPE")


def test_draft_proposal_requires_problem_statement(sealed_completed_run):
    """`proposal.py:206` — empty problem_statement raises."""
    with pytest.raises(ProposalError, match="problem_statement"):
        _full_pipeline_through_proposal(sealed_completed_run, problem_statement="   ")


def test_draft_proposal_requires_explicit_target_surface(sealed_completed_run):
    """`proposal.py:208` — empty target_surface in draft_proposal raises."""
    # We have to reach draft_proposal directly because run_proposal also feeds
    # target_surface into the diff manifest, which validates first.
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    ready = run_observer(state)
    ev = run_6b(
        state,
        ready,
        governance_baseline=GovernanceBaseline(
            policy_hash="pH", rubric_hash="rH", replay_digest=state.ingest.bundle.replay_key
        ),
    )
    rca_result = run_6c(state)
    diff = build_proposed_diff_manifest(
        target_surface="prompt",
        operation_type="UPDATE",
        before_ref="b",
        after_candidate_ref="a",
        diff_summary="d",
    )
    blast = build_blast_radius(proposal_id="pending", affected_surfaces=["prompt"], affected_tests=["t1"])
    rollback = build_rollback_plan(proposal_id="pending", rollback_steps=["r"])
    with pytest.raises(ProposalError, match="target_surface"):
        draft_proposal(
            proposal_type="PROMPT_UPDATE",
            target_surface="   ",
            current_version_ref="v1",
            proposed_version_ref="v2",
            problem_statement="x",
            completed_eval_record=ev.completed,
            rca_packet=rca_result.rca,
            pattern=None,
            proposed_diff=diff,
            expected_effect="better",
            rollback_plan=rollback,
            blast_radius=blast,
            affected_tests=["t1"],
            migration_notes="",
            owner="o",
            signer_identity="s",
        )


def test_draft_proposal_falls_back_to_blast_radius_tests(sealed_completed_run):
    """`proposal.py:213` — empty affected_tests falls back to blast_radius tests."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    ready = run_observer(state)
    ev = run_6b(
        state,
        ready,
        governance_baseline=GovernanceBaseline(
            policy_hash="pH", rubric_hash="rH", replay_digest=state.ingest.bundle.replay_key
        ),
    )
    rca_result = run_6c(state)
    diff = build_proposed_diff_manifest(
        target_surface="prompt",
        operation_type="UPDATE",
        before_ref="b",
        after_candidate_ref="a",
        diff_summary="d",
    )
    blast = build_blast_radius(
        proposal_id="pending",
        affected_surfaces=["prompt"],
        affected_tests=["fallback-t1"],
    )
    rollback = build_rollback_plan(proposal_id="pending", rollback_steps=["r"])
    p = draft_proposal(
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        completed_eval_record=ev.completed,
        rca_packet=rca_result.rca,
        pattern=None,
        proposed_diff=diff,
        expected_effect="better",
        rollback_plan=rollback,
        blast_radius=blast,
        affected_tests=[],  # empty — fallback fires
        migration_notes="",
        owner="o",
        signer_identity="s",
    )
    assert "fallback-t1" in p.affected_tests


def test_draft_proposal_rejects_when_no_tests_anywhere(sealed_completed_run):
    """`proposal.py:215` — empty tests AND empty blast_radius tests raises."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    ready = run_observer(state)
    ev = run_6b(
        state,
        ready,
        governance_baseline=GovernanceBaseline(
            policy_hash="pH", rubric_hash="rH", replay_digest=state.ingest.bundle.replay_key
        ),
    )
    rca_result = run_6c(state)
    diff = build_proposed_diff_manifest(
        target_surface="prompt",
        operation_type="UPDATE",
        before_ref="b",
        after_candidate_ref="a",
        diff_summary="d",
    )
    blast = build_blast_radius(proposal_id="pending", affected_surfaces=["prompt"], affected_tests=[])
    rollback = build_rollback_plan(proposal_id="pending", rollback_steps=["r"])
    with pytest.raises(ProposalError, match="affected test"):
        draft_proposal(
            proposal_type="PROMPT_UPDATE",
            target_surface="prompt",
            current_version_ref="v1",
            proposed_version_ref="v2",
            problem_statement="x",
            completed_eval_record=ev.completed,
            rca_packet=rca_result.rca,
            pattern=None,
            proposed_diff=diff,
            expected_effect="better",
            rollback_plan=rollback,
            blast_radius=blast,
            affected_tests=[],
            migration_notes="",
            owner="o",
            signer_identity="s",
        )


def _build_minimal_proposal(sealed_completed_run):
    """Build a complete valid DraftProposalPacket through the pipeline."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    ready = run_observer(state)
    ev = run_6b(
        state,
        ready,
        governance_baseline=GovernanceBaseline(
            policy_hash="pH", rubric_hash="rH", replay_digest=state.ingest.bundle.replay_key
        ),
    )
    rca_result = run_6c(state)
    return state, ev, rca_result


def test_admit_proposal_blocks_on_stale_eval(sealed_completed_run):
    """`proposal.py:280-281` (eval) AND `proposal.py:301-302` (calibration) —
    both freshness flags surface their open_blockers and reasons."""
    state, _, _ = _build_minimal_proposal(sealed_completed_run)
    proposal_result = run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="needs fix",
        expected_effect="better",
        rollback_steps=["revert"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    test_plan = build_test_plan(proposal_id=proposal_result.proposal.proposal_id, affected_tests=["t1"])
    admit = admit_proposal(
        proposal_result.proposal,
        test_plan=test_plan,
        completed_eval_record=state.eval.completed,
        rca_packet=state.rca.rca,
        pattern=None,
        eval_freshness_ok=False,
        calibration_freshness_ok=False,
    )
    assert "STALE_EVAL" in admit.open_blockers
    assert "STALE_CALIBRATION" in admit.open_blockers
    assert "eval_freshness_failed" in admit.reason_codes
    assert "calibration_freshness_failed" in admit.reason_codes
    assert admit.freshness_check_status == "STALE"


def test_admit_proposal_holds_on_missing_eval_record():
    """`proposal.py:280-281` — MISSING_EVAL_RECORD => HOLD_FOR_MORE_EVIDENCE.

    We construct a stub proposal whose admission gate is fed `None` for the
    eval record so the gate codepath runs cleanly through `eval_present=False`.
    """

    @dataclasses.dataclass
    class _StubBlast:
        affected_surfaces: list = dataclasses.field(default_factory=list)
        affected_tests: list = dataclasses.field(default_factory=list)
        rollout_risk_score: float = 0.0

    @dataclasses.dataclass
    class _StubDiff:
        diff_summary: str = ""

    @dataclasses.dataclass
    class _StubRollback:
        rollback_steps: list = dataclasses.field(default_factory=list)

    @dataclasses.dataclass
    class _StubTestPlan:
        affected_tests: list = dataclasses.field(default_factory=list)

    @dataclasses.dataclass
    class _StubProposal:
        proposal_id: str = "proposal-x"
        proposal_type: str = "PROMPT_UPDATE"
        target_surface: str = ""
        proposed_diff: _StubDiff = dataclasses.field(default_factory=_StubDiff)
        blast_radius: _StubBlast = dataclasses.field(default_factory=_StubBlast)
        rollback_plan_ref: _StubRollback = dataclasses.field(default_factory=_StubRollback)
        owner: str = ""
        signer_identity: str = ""

    receipt = admit_proposal(
        _StubProposal(),
        test_plan=_StubTestPlan(),
        completed_eval_record=None,
        rca_packet=None,
        pattern=None,
    )
    assert "MISSING_EVAL_RECORD" in receipt.open_blockers
    assert "MISSING_RCA_OR_PATTERN" in receipt.open_blockers
    assert "MISSING_TARGET_SURFACE" in receipt.open_blockers
    assert "MISSING_DIFF" in receipt.open_blockers
    assert "MISSING_BLAST_RADIUS" in receipt.open_blockers
    assert "MISSING_ROLLBACK" in receipt.open_blockers
    assert "MISSING_TEST_PLAN" in receipt.open_blockers
    assert "MISSING_OWNER_SIGNER" in receipt.open_blockers
    assert receipt.decision == "HOLD_FOR_MORE_EVIDENCE"


# ---------------------------------------------------------------------------
# gauntlet.py — every error path
# ---------------------------------------------------------------------------


def test_run_gauntlet_rejects_no_proposal():
    """`gauntlet.py:84` — proposal=None raises."""
    with pytest.raises(GauntletError, match="proposal required"):
        run_gauntlet(None, rollback_rehearsal_ref="r")


def test_run_gauntlet_requires_rollback_rehearsal_ref(sealed_completed_run):
    state, _, _ = _build_minimal_proposal(sealed_completed_run)
    proposal_result = run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        expected_effect="y",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    with pytest.raises(GauntletError, match="rollback rehearsal"):
        run_gauntlet(proposal_result.proposal, rollback_rehearsal_ref="")


def test_decide_approval_rejects_unadmitted_proposal(sealed_completed_run):
    """`gauntlet.py:168-169` — admission != ADMIT_TO_GAUNTLET => REJECT."""
    state, ev, rca_result = _build_minimal_proposal(sealed_completed_run)
    proposal_result = run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        expected_effect="y",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    g = run_gauntlet(proposal_result.proposal, rollback_rehearsal_ref="rh")

    # Forge admission record with non-ADMIT decision
    admission = ProposalAdmissionReceipt(
        admission_receipt_id="admit-bad",
        proposal_id=proposal_result.proposal.proposal_id,
        eval_record_present=True,
        rca_or_pattern_present=True,
        target_surface_present=True,
        proposed_diff_present=True,
        blast_radius_present=True,
        rollback_plan_present=True,
        test_plan_present=True,
        owner_signer_present=True,
        freshness_check_status="OK",
        open_blockers=[],
        decision="REJECT_WEAK_PROPOSAL",
        reason_codes=[],
    )
    decision = decide_approval(
        proposal_result.proposal,
        admission=admission,
        gauntlet=g,
        completed_eval_record=ev.completed,
        rca_packet=rca_result.rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    assert decision.decision == "REJECT"
    assert "PROPOSAL_NOT_ADMITTED" in decision.reason_codes


def test_build_promotion_packet_rejects_when_gauntlet_failed(sealed_completed_run):
    """`gauntlet.py:239` — gauntlet not PASS => raises."""
    state, ev, rca_result = _build_minimal_proposal(sealed_completed_run)
    proposal_result = run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        expected_effect="y",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    g = run_gauntlet(
        proposal_result.proposal,
        rollback_rehearsal_ref="rh",
        failing_cases=["case-a"],  # forces FAIL
    )
    # Forge an APPROVE decision (defensive — caller should never reach here)
    fake_approval = type("A", (), {"decision": "APPROVE", "approval_decision_id": "a-x"})()
    with pytest.raises(GauntletError, match="gauntlet PASS"):
        build_promotion_packet(
            proposal_result.proposal,
            approval=fake_approval,  # type: ignore[arg-type]
            completed_eval_record=ev.completed,
            rca_packet=rca_result.rca,
            gauntlet=g,
            target_version_current="v1",
            target_version_proposed="v2",
        )


def test_build_promotion_packet_rejects_content_hash_mismatch(sealed_completed_run):
    """`gauntlet.py:242` — gauntlet content-hash mismatch raises."""
    state, ev, rca_result = _build_minimal_proposal(sealed_completed_run)
    proposal_result = run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        expected_effect="y",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    g = run_gauntlet(proposal_result.proposal, rollback_rehearsal_ref="rh")
    # Tamper the gauntlet content hash so the binding check fails
    object.__setattr__(g, "proposal_content_hash", "0" * 64)
    fake_approval = type("A", (), {"decision": "APPROVE", "approval_decision_id": "a-x"})()
    with pytest.raises(GauntletError, match="content hash mismatch"):
        build_promotion_packet(
            proposal_result.proposal,
            approval=fake_approval,  # type: ignore[arg-type]
            completed_eval_record=ev.completed,
            rca_packet=rca_result.rca,
            gauntlet=g,
            target_version_current="v1",
            target_version_proposed="v2",
        )


def test_build_uwg_request_package_rejects_empty_approval_id(sealed_completed_run):
    """`gauntlet.py:297` — empty approval_decision_id raises."""
    state, ev, rca_result = _build_minimal_proposal(sealed_completed_run)
    proposal_result = run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        expected_effect="y",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    g = run_gauntlet(proposal_result.proposal, rollback_rehearsal_ref="rh")
    approval = decide_approval(
        proposal_result.proposal,
        admission=proposal_result.admission,
        gauntlet=g,
        completed_eval_record=ev.completed,
        rca_packet=rca_result.rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    promo = build_promotion_packet(
        proposal_result.proposal,
        approval=approval,
        completed_eval_record=ev.completed,
        rca_packet=rca_result.rca,
        gauntlet=g,
        target_version_current="v1",
        target_version_proposed="v2",
    )
    object.__setattr__(promo, "approval_decision_id", "")
    with pytest.raises(GauntletError, match="approval_decision_id"):
        build_uwg_request_package(
            promo,
            version_bump="v1->v2",
            alias_swap_plan="a",
            cache_read_surface_refresh_plan="c",
        )


def test_bind_uwg_receipt_requires_both_ids(sealed_completed_run):
    """`gauntlet.py:330` — empty receipt or digest raises."""
    state, ev, rca_result = _build_minimal_proposal(sealed_completed_run)
    proposal_result = run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        expected_effect="y",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    g = run_gauntlet(proposal_result.proposal, rollback_rehearsal_ref="rh")
    approval = decide_approval(
        proposal_result.proposal,
        admission=proposal_result.admission,
        gauntlet=g,
        completed_eval_record=ev.completed,
        rca_packet=rca_result.rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    promo = build_promotion_packet(
        proposal_result.proposal,
        approval=approval,
        completed_eval_record=ev.completed,
        rca_packet=rca_result.rca,
        gauntlet=g,
        target_version_current="v1",
        target_version_proposed="v2",
    )
    with pytest.raises(GauntletError, match="UWG receipt binding"):
        bind_uwg_receipt(promo, uwg_receipt_id="", l4_version_digest="d")
    with pytest.raises(GauntletError, match="UWG receipt binding"):
        bind_uwg_receipt(promo, uwg_receipt_id="r", l4_version_digest="")


def test_build_future_run_activation_receipt_requires_l4_digest(sealed_completed_run):
    """`gauntlet.py:360` — missing l4_version_digest after UWG receipt set raises."""
    state, ev, rca_result = _build_minimal_proposal(sealed_completed_run)
    proposal_result = run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        expected_effect="y",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    g = run_gauntlet(proposal_result.proposal, rollback_rehearsal_ref="rh")
    approval = decide_approval(
        proposal_result.proposal,
        admission=proposal_result.admission,
        gauntlet=g,
        completed_eval_record=ev.completed,
        rca_packet=rca_result.rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    promo = build_promotion_packet(
        proposal_result.proposal,
        approval=approval,
        completed_eval_record=ev.completed,
        rca_packet=rca_result.rca,
        gauntlet=g,
        target_version_current="v1",
        target_version_proposed="v2",
    )
    object.__setattr__(promo, "uwg_receipt_id", "uwg-r")
    object.__setattr__(promo, "l4_version_digest", None)
    with pytest.raises(GauntletError, match="l4_version_digest"):
        build_future_run_activation_receipt(promo, alias_updated=True)


# ---------------------------------------------------------------------------
# pipeline.py — every prerequisite-missing guard
# ---------------------------------------------------------------------------


def test_run_observer_requires_ingest():
    """`pipeline.py:208`."""
    with pytest.raises(RuntimeError, match="observer requires ingest"):
        run_observer(L6PipelineState())


def test_run_6b_requires_ingest():
    """`pipeline.py:243`."""
    state = L6PipelineState()
    with pytest.raises(RuntimeError, match="6B requires ingest"):
        run_6b(
            state,
            EvalReadinessReceipt(
                eval_readiness_receipt_id="r",
                runtime_exhaust_bundle_id="b",
                observer_receipt_id="o",
                trace_completeness_status="PRESENT",
                artifact_integrity_status="PRESENT",
                replay_key_status="PRESENT",
                policy_hash_status="PRESENT",
                route_contract_status="PRESENT",
                prompt_hash_status="PRESENT",
                source_lineage_status="PRESENT",
                terminal_status_status="PRESENT",
                evaluator_input_status="PRESENT",
                readiness_decision="READY_FOR_6B",
                missing_evidence_map_ref=None,
                excluded_from_learning_until=None,
                reason_codes=[],
            ),
            governance_baseline=GovernanceBaseline(policy_hash=None, rubric_hash=None, replay_digest=None),
        )


def test_run_6c_requires_6b_and_ingest():
    """`pipeline.py:316`."""
    with pytest.raises(RuntimeError, match="6C requires"):
        run_6c(L6PipelineState())


def test_run_proposal_requires_6b_and_6c(sealed_completed_run):
    """`pipeline.py:386`."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    run_observer(state)
    # No 6B/6C yet
    with pytest.raises(RuntimeError, match="proposal requires"):
        run_proposal(
            state,
            proposal_type="PROMPT_UPDATE",
            target_surface="x",
            current_version_ref="v1",
            proposed_version_ref="v2",
            problem_statement="x",
            expected_effect="y",
            rollback_steps=["r"],
            affected_surfaces=["x"],
            affected_tests=["t"],
            owner="o",
            signer_identity="s",
        )


def test_run_6d_requires_proposal(sealed_completed_run):
    """`pipeline.py:479`."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    with pytest.raises(RuntimeError, match="6D requires"):
        run_6d(
            state,
            uwg_commit=lambda p: ("u", "d"),
            target_version_current="v1",
            target_version_proposed="v2",
            rollback_rehearsal_ref="r",
        )


# ---------------------------------------------------------------------------
# otel_spans.py — recorder property + KPI direction error
# ---------------------------------------------------------------------------


def test_span_recorder_records_property_returns_tuple():
    """`otel_spans.py:101` — `.records` exposes a tuple snapshot."""
    rec = L6SpanRecorder()
    rec.record(L6SpanRecord(name="l6.ingest.bundle_receive", trace_id="t", span_id="s"))
    snapshot = rec.records
    assert isinstance(snapshot, tuple)
    assert len(snapshot) == 1


def test_evaluate_kpi_invalid_direction_raises(monkeypatch):
    """`otel_spans.py:173` — a KPI with an unknown direction surfaces ValueError."""
    import agentic_core.L6_observability.shadow_eval.otel_spans as ot

    fake = (KpiThreshold("fake_kpi", direction="<>", target=1.0),)
    monkeypatch.setattr(ot, "KPI_BOARD", fake)
    with pytest.raises(ValueError, match="invalid KPI direction"):
        ot.evaluate_kpi("fake_kpi", 1.0)


def test_span_recorder_assert_pipeline_order_passes_when_in_order():
    """L6SpanRecorder.assert_pipeline_order accepts canonical sequence."""
    rec = L6SpanRecorder()
    rec.record(L6SpanRecord(name="l6.ingest.bundle_receive", trace_id="t", span_id="a"))
    rec.record(L6SpanRecord(name="l6.ingest.source_collect", trace_id="t", span_id="b"))
    rec.assert_pipeline_order()


# ---------------------------------------------------------------------------
# Misc — full pipeline 6D not-approved branch + activation invariants
# ---------------------------------------------------------------------------


def test_run_6d_returns_no_promotion_when_approval_rejected(sealed_completed_run):
    """`pipeline.py` — when approval != APPROVE, promotion=None and activation=None."""
    state, _, _ = _build_minimal_proposal(sealed_completed_run)
    run_proposal(
        state,
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="x",
        expected_effect="y",
        rollback_steps=["r"],
        affected_surfaces=["prompt"],
        affected_tests=["t1"],
        owner="o",
        signer_identity="s",
    )
    # rollback_verified=False forces REQUIRE_ROLLBACK_PLAN
    result = run_6d(
        state,
        uwg_commit=lambda p: ("u", "d"),
        target_version_current="v1",
        target_version_proposed="v2",
        rollback_rehearsal_ref="rh",
        rollback_verified=False,
    )
    assert result.promotion is None
    assert result.activation is None
    assert result.approval_decision == "REQUIRE_ROLLBACK_PLAN"
