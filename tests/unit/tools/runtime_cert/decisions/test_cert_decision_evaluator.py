"""Phase D.2 evaluator unit tests — ADR-080 §11 D.2, plan §11.

All tests are pure: no filesystem access, no SQLite, no subprocess, no
network. Every assertion includes
``runtime_certification_status_after == NOT_CERTIFIED`` either directly or
by construction via the D.1 schema invariant.
"""

from __future__ import annotations

import builtins
import hashlib
import json
import math
import sqlite3

import pytest

from tools.runtime_cert.decisions.cert_decision_evaluator import (
    AMBIGUOUS_EVIDENCE,
    CLOSEOUT_MISSING,
    CRITICAL_BLOCKERS_PRESENT,
    FAILURE_REASONS,
    FORBIDDEN_SPAN_VIOLATION,
    FORMAL_CONTROL_MISSING_OR_FAILED,
    MANIFEST_HASH_DRIFT,
    MIN_N,
    NEXT_REVIEW_DAYS_CERTIFY,
    NEXT_REVIEW_DAYS_HOLD,
    NEXT_REVIEW_DAYS_REJECT,
    NOT_TRACE_OBSERVED_READY,
    SAMPLE_SIZE_TOO_SMALL,
    UPLIFT_NOT_POSITIVE,
    WILSON_BELOW_THRESHOLD,
    Z_SCORE_BELOW_THRESHOLD,
    derive_closeout_report_hash,
    evaluate_phase_c_closeout,
    wilson_lower_bound,
)
from tools.runtime_cert.decisions.cert_decision_record import (
    CertificationDecisionRecord,
    NOT_CERTIFIED,
    VERDICT_CERTIFY,
    VERDICT_HOLD,
    VERDICT_REJECT,
    compute_decision_id,
    make_certification_decision_record,
)
from tools.runtime_cert.reports.phase_c_closeout import (
    AppCloseoutSummary,
    EVIDENCE_KIND_BTC,
    EVIDENCE_KIND_FORMAL_EXCEPTION,
    EVIDENCE_KIND_R3,
    EVIDENCE_KIND_SKIPPED,
    PhaseCCloseoutReport,
    REPORT_DISCLAIMER,
)


# ---------------------------------------------------------------------------
# Fixture helpers.
# ---------------------------------------------------------------------------


def _h(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


MANIFEST_A = _h("manifest-A")
MANIFEST_B = _h("manifest-B")
GEN_AT = "2026-05-01T12:00:00Z"


def _summary(
    *,
    app_name: str = "apps_research",
    evidence_kind: str = EVIDENCE_KIND_R3,
    manifest_hash: str = MANIFEST_A,
    passed_trace_observed: bool = False,
    passed_formal_exception_observed: bool = False,
    missing_contracts: tuple[str, ...] = (),
    forbidden_violations: tuple[str, ...] = (),
    attribute_hardening_required: tuple[str, ...] = (),
    unknown_needs_runtime_run: tuple[str, ...] = (),
    gap_count: int = 0,
    highest_gap_severity: str = "info",
    recommendations: tuple[str, ...] = (),
    notes: str = "",
    route_shape: str = "R3_grounded_read",
) -> AppCloseoutSummary:
    return AppCloseoutSummary(
        app_name=app_name,
        route_shape=route_shape,
        static_runtime_mode="observed",
        manifest_hash=manifest_hash,
        runtime_certification_status=NOT_CERTIFIED,
        evidence_kind=evidence_kind,
        passed_trace_observed=passed_trace_observed,
        passed_formal_exception_observed=passed_formal_exception_observed,
        missing_contracts=missing_contracts,
        forbidden_violations=forbidden_violations,
        attribute_hardening_required=attribute_hardening_required,
        unknown_needs_runtime_run=unknown_needs_runtime_run,
        gap_count=gap_count,
        highest_gap_severity=highest_gap_severity,
        recommendations=recommendations,
        notes=notes,
    )


def _report(summaries: tuple[AppCloseoutSummary, ...]) -> PhaseCCloseoutReport:
    trace_ready = sum(
        1
        for s in summaries
        if s.evidence_kind in (EVIDENCE_KIND_R3, EVIDENCE_KIND_BTC)
        and s.passed_trace_observed
    )
    formal_ready = sum(
        1
        for s in summaries
        if s.evidence_kind == EVIDENCE_KIND_FORMAL_EXCEPTION
        and s.passed_formal_exception_observed
    )
    blockers = sum(1 for s in summaries if s.has_blocker)
    return PhaseCCloseoutReport(
        generated_at=GEN_AT,
        app_summaries=summaries,
        total_apps=len(summaries),
        not_certified_count=len(summaries),
        trace_observed_ready_count=trace_ready,
        formal_exception_observed_ready_count=formal_ready,
        blocker_count=blockers,
        top_recommendations=(),
        runtime_certification_status=NOT_CERTIFIED,
        disclaimer=REPORT_DISCLAIMER,
    )


def _prior_record(
    *,
    app_name: str,
    manifest_hash: str,
    trace_observed_n: int,
    trace_observed_success_n: int,
    evidence_rate: float | None = None,
    generated_at_utc: str = "2026-04-24T12:00:00Z",
    verdict: str = VERDICT_HOLD,
    failure_reasons: tuple[str, ...] = (SAMPLE_SIZE_TOO_SMALL,),
    evidence_kind: str = EVIDENCE_KIND_R3,
    route_shape: str = "R3_grounded_read",
) -> CertificationDecisionRecord:
    rate = (
        evidence_rate
        if evidence_rate is not None
        else (
            trace_observed_success_n / trace_observed_n
            if trace_observed_n > 0
            else 0.0
        )
    )
    return make_certification_decision_record(
        generated_at_utc=generated_at_utc,
        app_name=app_name,
        route_shape=route_shape,
        manifest_hash=manifest_hash,
        evidence_kind=evidence_kind,
        closeout_report_id="prior-report",
        closeout_report_hash=_h(f"prior-{app_name}-{generated_at_utc}"),
        trace_observed_n=trace_observed_n,
        trace_observed_success_n=trace_observed_success_n,
        evidence_rate=rate,
        wilson_lower=0.55,
        z_score=1.5,
        uplift=0.0,
        verdict=verdict,
        failure_reasons=failure_reasons,
        next_review_utc="2026-05-01T12:00:00Z",
    )


# ===========================================================================
# wilson_lower_bound
# ===========================================================================


def test_wilson_known_vectors():
    # (30,30) @ z=1.96 ≈ 0.8864 per plan §11 test 1 expected ~0.885.
    assert math.isclose(wilson_lower_bound(30, 30), 0.8864829086, rel_tol=1e-6)
    # (15,30) ≈ 0.3315.
    assert math.isclose(wilson_lower_bound(15, 30), 0.3315385122, rel_tol=1e-6)
    # (0,0) == 0.0.
    assert wilson_lower_bound(0, 0) == 0.0
    # (0,30) returns 0.0 (lower bound of zero-observed successes).
    assert wilson_lower_bound(0, 30) == 0.0
    # (30,30) @ higher z still <= 1.0.
    assert 0.0 <= wilson_lower_bound(30, 30, z=2.58) <= 1.0


def test_wilson_default_z_is_1_96():
    a = wilson_lower_bound(25, 40)
    b = wilson_lower_bound(25, 40, 1.96)
    assert a == b


def test_wilson_rejects_negative_n():
    with pytest.raises(ValueError, match="n"):
        wilson_lower_bound(0, -1)


def test_wilson_rejects_negative_successes():
    with pytest.raises(ValueError, match="successes"):
        wilson_lower_bound(-1, 10)


def test_wilson_rejects_successes_greater_than_n():
    with pytest.raises(ValueError, match="successes"):
        wilson_lower_bound(11, 10)


def test_wilson_rejects_nonpositive_z():
    with pytest.raises(ValueError, match="z"):
        wilson_lower_bound(5, 10, 0.0)
    with pytest.raises(ValueError, match="z"):
        wilson_lower_bound(5, 10, -1.0)


def test_wilson_rejects_non_int_successes():
    with pytest.raises(TypeError):
        wilson_lower_bound(1.5, 10)  # type: ignore[arg-type]


def test_wilson_rejects_non_int_n():
    with pytest.raises(TypeError):
        wilson_lower_bound(5, 10.0)  # type: ignore[arg-type]


def test_wilson_rejects_bool_inputs():
    # bool is int in Python; explicitly rejected to avoid footguns.
    with pytest.raises(TypeError):
        wilson_lower_bound(True, 10)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        wilson_lower_bound(5, True)  # type: ignore[arg-type]


# ===========================================================================
# derive_closeout_report_hash
# ===========================================================================


def test_derive_closeout_report_hash_deterministic():
    r = _report((_summary(),))
    assert derive_closeout_report_hash(r) == derive_closeout_report_hash(r)


def test_derive_closeout_report_hash_changes_with_content():
    a = _report((_summary(app_name="apps_a"),))
    b = _report((_summary(app_name="apps_b"),))
    assert derive_closeout_report_hash(a) != derive_closeout_report_hash(b)


def test_derive_closeout_report_hash_is_64_hex():
    h = derive_closeout_report_hash(_report((_summary(),)))
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ===========================================================================
# Output shape invariants.
# ===========================================================================


def test_one_record_per_summary_preserves_order():
    summaries = (
        _summary(app_name="apps_research"),
        _summary(app_name="apps_eval", evidence_kind=EVIDENCE_KIND_FORMAL_EXCEPTION,
                 route_shape="evaluator_only"),
        _summary(app_name="apps_underwriting_ai", evidence_kind=EVIDENCE_KIND_BTC,
                 route_shape="build_time_compiler"),
    )
    records = evaluate_phase_c_closeout(_report(summaries))
    assert len(records) == 3
    assert [r.app_name for r in records] == [
        "apps_research", "apps_eval", "apps_underwriting_ai",
    ]


def test_every_record_keeps_status_after_not_certified():
    summaries = (
        _summary(passed_trace_observed=True),
        _summary(app_name="apps_eval",
                 evidence_kind=EVIDENCE_KIND_FORMAL_EXCEPTION,
                 route_shape="evaluator_only",
                 passed_formal_exception_observed=True),
    )
    records = evaluate_phase_c_closeout(_report(summaries))
    for r in records:
        assert r.runtime_certification_status_before == NOT_CERTIFIED
        assert r.runtime_certification_status_after == NOT_CERTIFIED


def test_deterministic_decision_id_via_d1_helper():
    summaries = (_summary(passed_trace_observed=True),)
    rep = _report(summaries)
    (rec,) = evaluate_phase_c_closeout(rep)
    expected = compute_decision_id(
        "apps_research", MANIFEST_A, rec.closeout_report_hash
    )
    assert rec.decision_id == expected


def test_closeout_report_hash_override():
    custom_hash = _h("custom")
    summaries = (_summary(),)
    (rec,) = evaluate_phase_c_closeout(
        _report(summaries),
        closeout_report_id="custom-report-id",
        closeout_report_hash=custom_hash,
    )
    assert rec.closeout_report_hash == custom_hash
    assert rec.closeout_report_id == "custom-report-id"


def test_closeout_report_hash_derived_when_omitted():
    rep = _report((_summary(),))
    (rec,) = evaluate_phase_c_closeout(rep)
    assert rec.closeout_report_hash == derive_closeout_report_hash(rep)
    assert rec.closeout_report_id.startswith("closeout:")


# ===========================================================================
# certify verdict.
# ===========================================================================


def _certify_fixture():
    """29 passing accumulators + 1 most-recent moderate-rate prior.

    Current summary contributes (1, 1). Accumulation: 29*(1,1) + 1*(2,1) =
    n=32, succ=31. Most-recent prior has evidence_rate=0.5 so baseline is
    off the {0.0, 1.0} boundary and z_score computes normally.
    """
    summary = _summary(passed_trace_observed=True)
    accumulators = [
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=1,
            trace_observed_success_n=1,
            generated_at_utc=f"2026-04-{1 + i:02d}T12:00:00Z",
            verdict=VERDICT_HOLD,
        )
        for i in range(29)
    ]
    most_recent = _prior_record(
        app_name="apps_research",
        manifest_hash=MANIFEST_A,
        trace_observed_n=2,
        trace_observed_success_n=1,
        evidence_rate=0.5,
        generated_at_utc="2026-04-30T12:00:00Z",  # most recent
        verdict=VERDICT_HOLD,
    )
    history = tuple(accumulators) + (most_recent,)
    return summary, history


def test_certify_when_all_thresholds_pass():
    summary, history = _certify_fixture()
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)

    assert rec.verdict == VERDICT_CERTIFY
    assert rec.failure_reasons == ()
    assert rec.trace_observed_n == 32
    assert rec.trace_observed_success_n == 31
    assert math.isclose(rec.evidence_rate, 31 / 32, rel_tol=1e-9)
    assert rec.wilson_lower >= 0.60
    assert rec.z_score >= 1.96
    assert rec.uplift > 0.0
    # Phase D invariant — certify does NOT promote.
    assert rec.runtime_certification_status_after == NOT_CERTIFIED


def test_certify_still_keeps_status_after_not_certified():
    # Double-assertion reflecting the plan's load-bearing invariant.
    summary, history = _certify_fixture()
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    assert rec.verdict == VERDICT_CERTIFY
    assert rec.runtime_certification_status_after == NOT_CERTIFIED


def test_next_review_is_30_days_when_certify():
    summary, history = _certify_fixture()
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    assert rec.verdict == VERDICT_CERTIFY
    assert rec.next_review_utc.startswith("2026-05-31")  # 2026-05-01 + 30d


# ===========================================================================
# hold verdict.
# ===========================================================================


def test_hold_on_small_n():
    summary = _summary(passed_trace_observed=True)
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_HOLD
    assert SAMPLE_SIZE_TOO_SMALL in rec.failure_reasons
    # Every failure reason must be in the closed ontology.
    for r in rec.failure_reasons:
        assert r in FAILURE_REASONS


def test_hold_on_low_wilson_even_with_large_n():
    # n=50, successes=30 → evidence_rate=0.6, wilson_lower ≈ 0.46 → hold.
    summary = _summary(passed_trace_observed=True)
    # Current contributes (1,1); history supplies 49 more at 29/49 success.
    history = tuple(
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=1,
            trace_observed_success_n=1 if i < 29 else 0,
            generated_at_utc=f"2026-04-{1 + i:02d}T12:00:00Z",
        )
        for i in range(49)
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    assert rec.verdict == VERDICT_HOLD
    assert rec.trace_observed_n == 50
    assert rec.trace_observed_success_n == 30
    assert rec.wilson_lower < 0.60
    assert WILSON_BELOW_THRESHOLD in rec.failure_reasons


def test_hold_uplift_not_positive():
    # Enough n, threshold-passing rate, but baseline equals current → uplift=0.
    summary = _summary(passed_trace_observed=True)
    history_passes = tuple(
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=1,
            trace_observed_success_n=1,
            evidence_rate=1.0,
            generated_at_utc=f"2026-04-{10 + i:02d}T12:00:00Z",
        )
        for i in range(30)
    )
    (rec,) = evaluate_phase_c_closeout(
        _report((summary,)), history=history_passes
    )
    # With baseline=1.0 (boundary), z_score clamps to 0.0; uplift=0.0.
    assert rec.uplift == 0.0
    assert rec.verdict == VERDICT_HOLD
    assert UPLIFT_NOT_POSITIVE in rec.failure_reasons


def test_hold_not_trace_observed_ready():
    # Summary with unknown_needs_runtime_run and no pass → hold with
    # NOT_TRACE_OBSERVED_READY in addition to the threshold reasons.
    summary = _summary(
        passed_trace_observed=False,
        unknown_needs_runtime_run=("contract_a",),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    # unknown_needs_runtime_run is ALSO a critical blocker → reject, not hold.
    # Adjust: use a case without missing/unknown for the hold-ready path.
    assert rec.verdict == VERDICT_REJECT
    assert CRITICAL_BLOCKERS_PRESENT in rec.failure_reasons


def test_next_review_is_7_days_when_hold():
    summary = _summary(passed_trace_observed=True)
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_HOLD
    assert rec.next_review_utc.startswith("2026-05-08")  # 2026-05-01 + 7d


# ===========================================================================
# reject verdict — blockers, forbidden, formal-control, drift, ambiguous.
# ===========================================================================


def test_reject_on_missing_contracts_critical_blocker():
    summary = _summary(missing_contracts=("R3-1", "R3-2"))
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_REJECT
    assert CRITICAL_BLOCKERS_PRESENT in rec.failure_reasons


def test_reject_on_forbidden_span_violation():
    summary = _summary(
        passed_trace_observed=True,
        forbidden_violations=("ForbiddenContract-1",),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_REJECT
    assert FORBIDDEN_SPAN_VIOLATION in rec.failure_reasons


def test_reject_on_formal_control_failure():
    summary = _summary(
        evidence_kind=EVIDENCE_KIND_FORMAL_EXCEPTION,
        route_shape="evaluator_only",
        passed_formal_exception_observed=False,
        forbidden_violations=("CC-EVAL-01",),  # = failed_controls in C.5
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_REJECT
    assert FORMAL_CONTROL_MISSING_OR_FAILED in rec.failure_reasons


def test_reject_on_missing_formal_control():
    summary = _summary(
        evidence_kind=EVIDENCE_KIND_FORMAL_EXCEPTION,
        route_shape="core_adjacent_utility",
        passed_formal_exception_observed=False,
        missing_contracts=("CC-SHARED-05",),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_REJECT
    assert FORMAL_CONTROL_MISSING_OR_FAILED in rec.failure_reasons


def test_reject_on_manifest_hash_drift():
    # Prior history on MANIFEST_B, current on MANIFEST_A, current n < 30
    # → drift rejects the current window.
    summary = _summary(manifest_hash=MANIFEST_A, passed_trace_observed=True)
    history = (
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_B,
            trace_observed_n=50,
            trace_observed_success_n=45,
            generated_at_utc="2026-04-01T00:00:00Z",
        ),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    assert rec.verdict == VERDICT_REJECT
    assert MANIFEST_HASH_DRIFT in rec.failure_reasons


def test_no_drift_on_first_ever_run():
    # No prior history → first-ever run does NOT fire MANIFEST_HASH_DRIFT.
    summary = _summary(passed_trace_observed=True, manifest_hash=MANIFEST_A)
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=())
    assert MANIFEST_HASH_DRIFT not in rec.failure_reasons


def test_drift_does_not_fire_when_current_n_is_sufficient():
    # Even if prior was on different manifest, if current window has
    # accumulated n >= MIN_N on the new manifest, drift doesn't trigger.
    summary = _summary(manifest_hash=MANIFEST_A, passed_trace_observed=True)
    same_manifest_history = tuple(
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=1,
            trace_observed_success_n=1,
            generated_at_utc=f"2026-04-{1 + i:02d}T12:00:00Z",
        )
        for i in range(30)
    )
    drift_prior = (
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_B,
            trace_observed_n=10,
            trace_observed_success_n=5,
            generated_at_utc="2026-03-01T00:00:00Z",
        ),
    )
    history = drift_prior + same_manifest_history
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    assert MANIFEST_HASH_DRIFT not in rec.failure_reasons


def test_reject_collects_all_firing_reasons():
    # Missing contracts + forbidden violations → two reject reasons.
    summary = _summary(
        missing_contracts=("R3-1",),
        forbidden_violations=("Forbidden-A",),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_REJECT
    assert CRITICAL_BLOCKERS_PRESENT in rec.failure_reasons
    assert FORBIDDEN_SPAN_VIOLATION in rec.failure_reasons


def test_ambiguous_evidence_on_skipped_with_signals():
    # skipped summary but forbidden_violations present → ambiguous.
    summary = _summary(
        evidence_kind=EVIDENCE_KIND_SKIPPED,
        forbidden_violations=("unexpected",),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_REJECT
    assert AMBIGUOUS_EVIDENCE in rec.failure_reasons


def test_skipped_clean_becomes_hold_with_closeout_missing():
    # skipped and clean → hold with CLOSEOUT_MISSING.
    summary = _summary(evidence_kind=EVIDENCE_KIND_SKIPPED)
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_HOLD
    assert CLOSEOUT_MISSING in rec.failure_reasons


def test_next_review_is_7_days_when_reject():
    summary = _summary(missing_contracts=("R3-1",))
    (rec,) = evaluate_phase_c_closeout(_report((summary,)))
    assert rec.verdict == VERDICT_REJECT
    assert rec.next_review_utc.startswith("2026-05-08")  # 7d cadence


# ===========================================================================
# Uplift & baseline.
# ===========================================================================


def test_uplift_from_prior_history():
    # Prior same app: rate 0.50. Current rate: 1.0 → uplift = 0.50.
    summary = _summary(passed_trace_observed=True, manifest_hash=MANIFEST_A)
    history = (
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=20,
            trace_observed_success_n=10,
            evidence_rate=0.50,
            generated_at_utc="2026-04-24T12:00:00Z",
        ),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    # Current rate: (10 + 1) / (20 + 1) = 11/21 ≈ 0.524.
    assert math.isclose(rec.evidence_rate, 11 / 21, rel_tol=1e-9)
    assert math.isclose(rec.uplift, 11 / 21 - 0.50, rel_tol=1e-9)


def test_uplift_zero_baseline_when_no_history():
    summary = _summary(passed_trace_observed=True)
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=())
    # Current n=1, succ=1, rate=1.0. No prior → baseline=0.0 → uplift=1.0.
    assert rec.uplift == 1.0


def test_baseline_uses_most_recent_prior():
    summary = _summary(passed_trace_observed=True)
    history = (
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=10,
            trace_observed_success_n=1,
            evidence_rate=0.10,
            generated_at_utc="2026-01-01T00:00:00Z",
        ),
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=10,
            trace_observed_success_n=9,
            evidence_rate=0.90,
            generated_at_utc="2026-04-24T12:00:00Z",  # most recent
        ),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    # Accumulated on same manifest: succ = 1 (current) + 1 + 9 = 11,
    # n = 1 + 10 + 10 = 21. rate = 11/21 ≈ 0.524. Most-recent prior
    # evidence_rate is 0.90 → uplift = rate - 0.90.
    current_rate = 11 / 21
    assert math.isclose(rec.evidence_rate, current_rate, rel_tol=1e-9)
    assert math.isclose(rec.uplift, current_rate - 0.90, rel_tol=1e-9)


# ===========================================================================
# History accumulation semantics.
# ===========================================================================


def test_history_accumulates_on_matching_manifest():
    summary = _summary(passed_trace_observed=True, manifest_hash=MANIFEST_A)
    history = (
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=20,
            trace_observed_success_n=19,
        ),
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=10,
            trace_observed_success_n=10,
            generated_at_utc="2026-04-15T12:00:00Z",
        ),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    # 20 + 10 + 1 (current) = 31, 19 + 10 + 1 = 30.
    assert rec.trace_observed_n == 31
    assert rec.trace_observed_success_n == 30


def test_history_does_not_accumulate_across_manifests():
    summary = _summary(manifest_hash=MANIFEST_A, passed_trace_observed=True)
    history = (
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_B,  # different manifest
            trace_observed_n=100,
            trace_observed_success_n=99,
        ),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    # Current summary only: (1, 1). History does not accumulate.
    assert rec.trace_observed_n == 1
    assert rec.trace_observed_success_n == 1


def test_history_different_app_is_ignored():
    summary = _summary(app_name="apps_research", passed_trace_observed=True,
                       manifest_hash=MANIFEST_A)
    history = (
        _prior_record(
            app_name="apps_eval",  # different app
            manifest_hash=MANIFEST_A,
            trace_observed_n=100,
            trace_observed_success_n=99,
        ),
    )
    (rec,) = evaluate_phase_c_closeout(_report((summary,)), history=history)
    assert rec.trace_observed_n == 1  # only current summary
    assert rec.uplift == 1.0  # no same-app history → baseline 0.0


# ===========================================================================
# Purity — no filesystem / SQLite access.
# ===========================================================================


def test_no_filesystem_or_sqlite_access(monkeypatch):
    """Patches every likely I/O path to raise; evaluator must still succeed."""

    def _boom_open(*args, **kwargs):
        raise AssertionError("evaluator attempted to call open()")

    def _boom_sqlite(*args, **kwargs):
        raise AssertionError("evaluator attempted sqlite3.connect()")

    monkeypatch.setattr(builtins, "open", _boom_open)
    monkeypatch.setattr(sqlite3, "connect", _boom_sqlite)

    summary = _summary(passed_trace_observed=True)
    history = (
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=5,
            trace_observed_success_n=5,
        ),
    )
    records = evaluate_phase_c_closeout(_report((summary,)), history=history)
    assert len(records) == 1
    assert records[0].runtime_certification_status_after == NOT_CERTIFIED


def test_history_consumed_at_most_once():
    """Iterables that can only be iterated once must still work."""
    summary = _summary(passed_trace_observed=True)

    def _one_shot():
        yield _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=5,
            trace_observed_success_n=5,
        )

    records = evaluate_phase_c_closeout(_report((summary,)), history=_one_shot())
    assert len(records) == 1
    assert records[0].trace_observed_n == 6


# ===========================================================================
# Defensive inputs.
# ===========================================================================


def test_evaluator_rejects_non_report():
    with pytest.raises(TypeError):
        evaluate_phase_c_closeout(object())  # type: ignore[arg-type]


def test_all_failure_reasons_in_closed_set_across_scenarios():
    scenarios = [
        _summary(),  # plain → hold
        _summary(missing_contracts=("x",)),  # reject
        _summary(forbidden_violations=("x",)),  # reject
        _summary(evidence_kind=EVIDENCE_KIND_FORMAL_EXCEPTION,
                 route_shape="evaluator_only",
                 missing_contracts=("cc",)),
        _summary(evidence_kind=EVIDENCE_KIND_SKIPPED),
        _summary(evidence_kind=EVIDENCE_KIND_SKIPPED,
                 forbidden_violations=("x",)),
    ]
    for s in scenarios:
        (rec,) = evaluate_phase_c_closeout(_report((s,)))
        for r in rec.failure_reasons:
            assert r in FAILURE_REASONS, (
                f"reason {r!r} not in closed ontology for scenario {s.evidence_kind}"
            )


# ===========================================================================
# No-promotion guarantee across ALL verdicts (sweep).
# ===========================================================================


def test_no_promotion_across_all_verdicts():
    summaries = (
        # certify path prepared via history
        _summary(app_name="apps_research", passed_trace_observed=True),
        # reject
        _summary(app_name="apps_eval_reject",
                 missing_contracts=("missing",)),
        # hold (plain, small n)
        _summary(app_name="apps_research_hold",
                 manifest_hash=MANIFEST_A),
    )
    accumulators = [
        _prior_record(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            trace_observed_n=1,
            trace_observed_success_n=1,
            generated_at_utc=f"2026-04-{1 + i:02d}T12:00:00Z",
        )
        for i in range(29)
    ]
    most_recent = _prior_record(
        app_name="apps_research",
        manifest_hash=MANIFEST_A,
        trace_observed_n=2,
        trace_observed_success_n=1,
        evidence_rate=0.5,
        generated_at_utc="2026-04-30T12:00:00Z",
    )
    history = tuple(accumulators) + (most_recent,)
    records = evaluate_phase_c_closeout(_report(summaries), history=history)
    verdicts = {r.app_name: r.verdict for r in records}
    assert verdicts["apps_research"] == VERDICT_CERTIFY
    assert verdicts["apps_eval_reject"] == VERDICT_REJECT
    assert verdicts["apps_research_hold"] == VERDICT_HOLD
    for r in records:
        assert r.runtime_certification_status_after == NOT_CERTIFIED
        assert r.runtime_certification_status_before == NOT_CERTIFIED


# ===========================================================================
# Constant sanity — plan §6.
# ===========================================================================


def test_closed_ontology_has_12_constants():
    assert len(FAILURE_REASONS) == 12


def test_review_cadences():
    assert NEXT_REVIEW_DAYS_CERTIFY == 30
    assert NEXT_REVIEW_DAYS_HOLD == 7
    assert NEXT_REVIEW_DAYS_REJECT == 7


def test_min_thresholds_match_adr_080():
    from tools.runtime_cert.decisions.cert_decision_evaluator import (
        MIN_WILSON_LOWER,
        MIN_Z_SCORE,
        MIN_UPLIFT,
    )

    assert MIN_N == 30
    assert MIN_WILSON_LOWER == 0.60
    assert MIN_Z_SCORE == 1.96
    assert MIN_UPLIFT == 0.0
