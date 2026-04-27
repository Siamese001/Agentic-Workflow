"""Tests for v6 BUS P/T pipeline primitives — Wave 4 of exit-eval-v6 deferred-scope.

Covers runtime_to_regression_dataset_flow.md sections:
- §3.1 BusTRow append-only shape + actor tagging (H2 link)
- §3.2 promotion heuristic 8-signal weights + score function
- §3.3 CurationDecision verdict invariants
- §3.4 GoldenSetTrack enum + GoldenSetVersion immutability + graduation predicate
- §5 retention policy constants
- §6 invariants (no-runtime-mutation marker, anonymization fail-closed)
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6 import (
    BUS_PT_DEFAULT_RETENTION_DAYS,
    CANDIDATE_POOL_RETENTION_DAYS,
    GOLDEN_SET_RETENTION_INDEFINITE,
    GRADUATION_K,
    GRADUATION_PASSK_THRESHOLD,
    GRADUATION_WINDOW,
    PROMOTION_HEURISTIC_WEIGHTS,
    BusTRow,
    CandidatePoolEntry,
    CurationDecision,
    CurationVerdict,
    GoldenSetTrack,
    GoldenSetVersion,
    assert_anonymization_fail_closed,
    assert_no_runtime_mutation,
    graduates_to_regression,
    promotion_score,
)


# ============================================================
# §3.4 Golden Set tracks
# ============================================================


def test_golden_set_track_three_values() -> None:
    assert {t.value for t in GoldenSetTrack} == {"capability", "regression", "adversarial"}


# ============================================================
# §5 Retention policy
# ============================================================


def test_bus_pt_retention_default_90_days() -> None:
    assert BUS_PT_DEFAULT_RETENTION_DAYS == 90


def test_candidate_pool_retention_30_days() -> None:
    assert CANDIDATE_POOL_RETENTION_DAYS == 30


def test_golden_set_retention_indefinite_flag() -> None:
    assert GOLDEN_SET_RETENTION_INDEFINITE is True


# ============================================================
# §3.2 Promotion heuristic — 8 signals + weights
# ============================================================


@pytest.mark.parametrize(
    "signal,weight",
    [
        ("x3b_escalation", 3.0),
        ("x1f_adversarial_failure", 2.5),
        ("x1e_trajectory_suspect", 2.0),
        ("passk_dip", 1.8),
        ("judge_abstained", 1.5),
        ("near_miss", 1.5),
        ("novel_trajectory_class", 1.3),
        ("routine_pass", 0.2),
    ],
)
def test_promotion_heuristic_weight_per_signal(signal: str, weight: float) -> None:
    """§3.2 table: each signal has its named weight."""
    assert PROMOTION_HEURISTIC_WEIGHTS[signal] == weight


def test_promotion_heuristic_exactly_eight_signals() -> None:
    """§3.2 table has exactly 8 promotion signals."""
    assert len(PROMOTION_HEURISTIC_WEIGHTS) == 8


def test_promotion_score_no_signals_is_zero() -> None:
    assert promotion_score({}) == 0.0


def test_promotion_score_all_signals_sums_weights() -> None:
    """All 8 signals firing produces sum of weights."""
    all_on = {k: True for k in PROMOTION_HEURISTIC_WEIGHTS}
    expected = sum(PROMOTION_HEURISTIC_WEIGHTS.values())
    assert promotion_score(all_on) == expected
    # 3.0+2.5+2.0+1.8+1.5+1.5+1.3+0.2 = 13.8
    assert abs(promotion_score(all_on) - 13.8) < 1e-9


def test_promotion_score_x3b_signal_alone_is_3_0() -> None:
    """§3.2: X3B escalation is highest single signal at 3.0."""
    assert promotion_score({"x3b_escalation": True}) == 3.0


def test_promotion_score_unknown_signals_ignored() -> None:
    """§3.2: extra signals don't crash (forward-compat)."""
    assert promotion_score({"some_future_signal": True}) == 0.0


def test_promotion_score_rejects_non_bool_values() -> None:
    with pytest.raises(ValueError, match="must be bool"):
        promotion_score({"x3b_escalation": 1})  # type: ignore[dict-item]


def test_promotion_score_routine_pass_lowest_priority() -> None:
    """§3.2: routine pass = 0.2, indicates 'sample only'."""
    assert PROMOTION_HEURISTIC_WEIGHTS["routine_pass"] == min(
        PROMOTION_HEURISTIC_WEIGHTS.values()
    )


# ============================================================
# §3.1 BusTRow shape
# ============================================================


def test_bus_t_row_minimal_construction() -> None:
    row = BusTRow(run_id="run-1")
    assert row.run_id == "run-1"
    assert row.actor == "agent"  # default per §H2
    assert row.trajectory == []
    assert row.environment_snapshot == {}


def test_bus_t_row_actor_judge_for_h2_compliance() -> None:
    """v4_hardening §H2.1: judge trajectories tagged actor='judge'."""
    row = BusTRow(run_id="run-judge", actor="judge")
    assert row.actor == "judge"


def test_bus_t_row_disposition_field() -> None:
    row = BusTRow(run_id="r", disposition="X3F")
    assert row.disposition == "X3F"


# ============================================================
# §3.2 CandidatePoolEntry shape
# ============================================================


def test_candidate_pool_entry_default_not_anonymized() -> None:
    """§6.2: entries default to NOT anonymized; gate must flip the bit."""
    entry = CandidatePoolEntry(
        run_id="r1",
        trajectory_class="support_ticket",
        normalized_input_hash="h1",
        output_class="refund_processed",
        promotion_score=2.5,
    )
    assert entry.anonymized is False
    assert entry.frequency_count == 1


def test_candidate_pool_entry_carries_signals() -> None:
    entry = CandidatePoolEntry(
        run_id="r2",
        trajectory_class="x",
        normalized_input_hash="h",
        output_class="o",
        promotion_score=3.0,
        signals={"x3b_escalation": True},
    )
    assert entry.signals["x3b_escalation"] is True


def test_assert_anonymization_fail_closed_blocks_unanonymized() -> None:
    """§6.2: unanonymized entry MUST NOT proceed to curation."""
    entry = CandidatePoolEntry(
        run_id="bad",
        trajectory_class="x",
        normalized_input_hash="h",
        output_class="o",
        promotion_score=1.0,
        anonymized=False,
    )
    with pytest.raises(ValueError, match="not anonymized"):
        assert_anonymization_fail_closed(entry)


def test_assert_anonymization_fail_closed_passes_anonymized() -> None:
    entry = CandidatePoolEntry(
        run_id="ok",
        trajectory_class="x",
        normalized_input_hash="h",
        output_class="o",
        promotion_score=1.0,
        anonymized=True,
    )
    assert assert_anonymization_fail_closed(entry) is None  # no raise


# ============================================================
# §3.3 CurationDecision invariants
# ============================================================


def test_curation_promote_requires_track() -> None:
    with pytest.raises(ValueError, match="PROMOTE requires a track"):
        CurationDecision(
            candidate_run_id="r",
            verdict=CurationVerdict.PROMOTE,
            curator_id="alice",
            decision_at_ms=0,
            track=None,  # missing
            confirmed_anonymization=True,
        )


def test_curation_promote_requires_anonymization_confirm() -> None:
    """§3.3 step 1: curator confirms anonymization."""
    with pytest.raises(ValueError, match="confirmed_anonymization=True"):
        CurationDecision(
            candidate_run_id="r",
            verdict=CurationVerdict.PROMOTE,
            curator_id="alice",
            decision_at_ms=0,
            track=GoldenSetTrack.REGRESSION,
            confirmed_anonymization=False,
        )


def test_curation_promote_happy_path() -> None:
    d = CurationDecision(
        candidate_run_id="r",
        verdict=CurationVerdict.PROMOTE,
        curator_id="alice",
        decision_at_ms=1,
        track=GoldenSetTrack.CAPABILITY,
        confirmed_anonymization=True,
        intent_label="user wants refund",
    )
    assert d.verdict is CurationVerdict.PROMOTE
    assert d.track is GoldenSetTrack.CAPABILITY


def test_curation_reject_requires_reason() -> None:
    with pytest.raises(ValueError, match="REJECT requires rejection_reason"):
        CurationDecision(
            candidate_run_id="r",
            verdict=CurationVerdict.REJECT,
            curator_id="alice",
            decision_at_ms=0,
            rejection_reason="",
        )


def test_curation_quarantine_requires_reason() -> None:
    with pytest.raises(ValueError, match="QUARANTINE requires quarantine_reason"):
        CurationDecision(
            candidate_run_id="r",
            verdict=CurationVerdict.QUARANTINE,
            curator_id="alice",
            decision_at_ms=0,
            quarantine_reason="",
        )


def test_curation_reject_with_reason_ok() -> None:
    d = CurationDecision(
        candidate_run_id="r",
        verdict=CurationVerdict.REJECT,
        curator_id="alice",
        decision_at_ms=0,
        rejection_reason="output contains untranscribed PII despite anonymization",
    )
    assert d.verdict is CurationVerdict.REJECT


# ============================================================
# §3.4 GoldenSetVersion immutability + graduation
# ============================================================


def test_golden_set_version_immutable_default_true() -> None:
    """§6.3: golden-set versions are immutable post-publish."""
    v = GoldenSetVersion(
        version_tag="regression-v1",
        track=GoldenSetTrack.REGRESSION,
        case_count=100,
        published_at_ms=0,
    )
    assert v.immutable is True


def test_graduation_constants_per_spec() -> None:
    """§3.4 graduation: pass^k >= 0.95 over k=10 weekly."""
    assert GRADUATION_PASSK_THRESHOLD == 0.95
    assert GRADUATION_K == 10
    assert GRADUATION_WINDOW == "weekly"


def test_graduates_to_regression_at_threshold_with_k_10() -> None:
    """Boundary: exactly 0.95 pass^k over k=10 graduates."""
    assert graduates_to_regression(0.95, 10) is True


def test_graduates_to_regression_below_threshold_blocks() -> None:
    assert graduates_to_regression(0.94, 10) is False


def test_graduates_to_regression_below_k_blocks() -> None:
    """§3.4: graduation needs k >= 10."""
    assert graduates_to_regression(0.99, 9) is False


def test_graduates_to_regression_zero_window_blocks() -> None:
    assert graduates_to_regression(0.99, 10, window_count=0) is False


# ============================================================
# §6 No-runtime-mutation invariant marker
# ============================================================


def test_assert_no_runtime_mutation_is_callable_marker() -> None:
    """§6.1: documenting marker for static review; never raises by itself."""
    # Just verify it's a no-op assertion that records adherence
    assert assert_no_runtime_mutation("candidate_pool_dedup") is None
    assert assert_no_runtime_mutation("curation_review") is None


# ============================================================
# Integration: package exports + full reachability
# ============================================================


def test_v6_package_exports_bus_pt_pipeline_symbols() -> None:
    from agentic_core.L3_orchestration.exit_eval import v6

    for name in [
        "BUS_PT_DEFAULT_RETENTION_DAYS",
        "CANDIDATE_POOL_RETENTION_DAYS",
        "GOLDEN_SET_RETENTION_INDEFINITE",
        "GRADUATION_K",
        "GRADUATION_PASSK_THRESHOLD",
        "GRADUATION_WINDOW",
        "PROMOTION_HEURISTIC_WEIGHTS",
        "BusTRow",
        "CandidatePoolEntry",
        "CurationDecision",
        "CurationVerdict",
        "GoldenSetTrack",
        "GoldenSetVersion",
        "assert_anonymization_fail_closed",
        "assert_no_runtime_mutation",
        "graduates_to_regression",
        "promotion_score",
    ]:
        assert hasattr(v6, name), f"v6.{name} missing"
        assert name in v6.__all__, f"{name} not in v6.__all__"
