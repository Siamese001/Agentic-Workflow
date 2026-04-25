"""W9 tests — KPI producers for previously un-emitted KPIs."""

from __future__ import annotations

from system_learning.engines.v6_kpi_board import V6KPIName
from system_learning.engines.v7_kpi_board import UnifiedKPIBoard, V7KPIName
from system_learning.engines.v7_kpi_producers import (
    AbstainCalibrationTracker,
    CitationDriftTracker,
    ExemplarHitTracker,
    GauntletFalsePromoteTracker,
    GoldenSetRegressionTracker,
    HeldProposalAgingTracker,
    OrphanArtifactTracker,
    ReplayDivergenceLocalizer,
    SaturationWatcher,
)


# ---- ReplayDivergenceLocalizer -------------------------------------------


def test_replay_localization_rate_all_localized():
    r = ReplayDivergenceLocalizer()
    r.record_replay(succeeded=False, localized_to="span:s1")
    r.record_replay(succeeded=False, localized_to="surface:prompt.X")
    assert r.localization_rate == 1.0


def test_replay_localization_rate_partial():
    r = ReplayDivergenceLocalizer()
    r.record_replay(succeeded=False, localized_to="span:s1")
    r.record_replay(succeeded=False, localized_to=None)
    assert r.localization_rate == 0.5


def test_replay_succeeded_does_not_count():
    r = ReplayDivergenceLocalizer()
    r.record_replay(succeeded=True)
    r.record_replay(succeeded=True)
    assert r.localization_rate == 1.0  # vacuous-true with no failures


def test_replay_localizer_publishes_v6_kpi():
    r = ReplayDivergenceLocalizer()
    r.record_replay(succeeded=False, localized_to="span:1")
    r.record_replay(succeeded=False, localized_to=None)
    board = UnifiedKPIBoard()
    r.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION)
    assert sample.value == 0.5


# ---- SaturationWatcher ----------------------------------------------------


def test_saturation_watch_no_evals_returns_zero():
    w = SaturationWatcher()
    assert w.compute(now_epoch=1000.0) == 0.0


def test_saturation_watch_all_static():
    w = SaturationWatcher()
    w.register_capability_eval("e1", 0.0)
    w.register_capability_eval("e2", 0.0)
    # 30 days = 30*86400 seconds, both are >= that
    assert w.compute(now_epoch=31 * 86400.0) == 1.0


def test_saturation_watch_half_static():
    w = SaturationWatcher()
    w.register_capability_eval("e1", 0.0)  # very old
    w.register_capability_eval("e2", 31 * 86400.0)  # fresh
    assert w.compute(now_epoch=31 * 86400.0) == 0.5


def test_saturation_publishes_v6_kpi():
    w = SaturationWatcher()
    w.register_capability_eval("e1", 0.0)
    board = UnifiedKPIBoard()
    w.publish_kpi_sample(board, now_epoch=31 * 86400.0)
    sample = board.latest(V6KPIName.SATURATION_WATCH)
    assert sample.value == 1.0


# ---- ExemplarHitTracker ---------------------------------------------------


def test_exemplar_hit_rate_above_target():
    t = ExemplarHitTracker()
    for _ in range(3):
        t.record_eligible_plan(used_exemplar=True)
    for _ in range(7):
        t.record_eligible_plan(used_exemplar=False)
    assert t.hit_rate == 0.3


def test_exemplar_hit_rate_zero_eligible():
    t = ExemplarHitTracker()
    assert t.hit_rate == 0.0


def test_exemplar_publishes_v6_kpi():
    t = ExemplarHitTracker()
    t.record_eligible_plan(used_exemplar=True)
    t.record_eligible_plan(used_exemplar=False)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.EXEMPLAR_HIT_RATE)
    assert sample.value == 0.5


# ---- GauntletFalsePromoteTracker ------------------------------------------


def test_false_promote_rate_under_threshold():
    t = GauntletFalsePromoteTracker()
    for _ in range(99):
        t.record_promotion(was_reverted=False)
    t.record_promotion(was_reverted=True)
    assert t.false_promote_rate == 0.01


def test_false_promote_rate_zero_when_no_promotions():
    t = GauntletFalsePromoteTracker()
    assert t.false_promote_rate == 0.0


def test_false_promote_publishes_v6_kpi():
    t = GauntletFalsePromoteTracker()
    t.record_promotion(was_reverted=False)
    t.record_promotion(was_reverted=True)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE)
    assert sample.value == 0.5


# ---- HeldProposalAgingTracker ---------------------------------------------


def test_held_proposal_p95_no_proposals():
    t = HeldProposalAgingTracker()
    assert t.p95_age_seconds(now_epoch=1000.0) == 0.0


def test_held_proposal_p95_single():
    t = HeldProposalAgingTracker()
    t.record_hold_start("p1", start_epoch=900.0)
    assert t.p95_age_seconds(now_epoch=1000.0) == 100.0


def test_held_proposal_p95_picks_high_age():
    t = HeldProposalAgingTracker()
    for i in range(100):
        t.record_hold_start(f"p{i}", start_epoch=1000.0 - i * 60.0)
    # Ages are 0, 60, 120, ..., 5940. p95 idx = round(0.95 * 99) = 94 → age 5640.
    age = t.p95_age_seconds(now_epoch=1000.0)
    assert age == 5640.0


def test_held_proposal_release_drops_from_calc():
    t = HeldProposalAgingTracker()
    t.record_hold_start("p1", start_epoch=0.0)
    t.record_hold_release("p1")
    assert t.p95_age_seconds(now_epoch=1000.0) == 0.0


def test_held_proposal_publishes_v7_kpi():
    t = HeldProposalAgingTracker()
    t.record_hold_start("p1", start_epoch=900.0)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board, now_epoch=1000.0)
    sample = board.latest(V7KPIName.HELD_PROPOSAL_AGING_P95)  # type: ignore[arg-type]
    assert sample.value == 100.0


# ---- GoldenSetRegressionTracker -------------------------------------------


def test_golden_set_pass_rate_all_pass():
    t = GoldenSetRegressionTracker()
    for _ in range(99):
        t.record_golden_case(critical=True, passed=True)
    assert t.pass_rate == 1.0


def test_golden_set_pass_rate_one_fail_in_100():
    t = GoldenSetRegressionTracker()
    for _ in range(99):
        t.record_golden_case(critical=True, passed=True)
    t.record_golden_case(critical=True, passed=False)
    assert t.pass_rate == 0.99


def test_golden_set_ignores_non_critical():
    t = GoldenSetRegressionTracker()
    t.record_golden_case(critical=False, passed=False)
    assert t.pass_rate == 1.0  # no critical samples → vacuous-true 1.0


def test_golden_set_publishes_v7_kpi():
    t = GoldenSetRegressionTracker()
    t.record_golden_case(critical=True, passed=True)
    t.record_golden_case(critical=True, passed=False)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.GOLDEN_SET_REGRESSION_PASS_RATE)  # type: ignore[arg-type]
    assert sample.value == 0.5


# ---- OrphanArtifactTracker ------------------------------------------------


def test_orphan_artifact_rate_zero():
    t = OrphanArtifactTracker()
    for _ in range(10):
        t.record_artifact(is_orphan=False)
    assert t.orphan_rate == 0.0


def test_orphan_artifact_rate_at_threshold():
    t = OrphanArtifactTracker()
    for _ in range(199):
        t.record_artifact(is_orphan=False)
    t.record_artifact(is_orphan=True)
    # 1/200 = 0.005 = 0.5%
    assert t.orphan_rate == 0.005


def test_orphan_publishes_v7_kpi():
    t = OrphanArtifactTracker()
    t.record_artifact(is_orphan=True)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.ORPHAN_ARTIFACT_RATE)  # type: ignore[arg-type]
    assert sample.value == 1.0


# ---- CitationDriftTracker -------------------------------------------------


def test_citation_drift_zero_when_baseline_matches():
    t = CitationDriftTracker(baseline_precision=0.9)
    t.record_precision_sample(0.9)
    t.record_precision_sample(0.9)
    assert t.drift == 0.0


def test_citation_drift_picks_up_decline():
    t = CitationDriftTracker(baseline_precision=0.9)
    t.record_precision_sample(0.7)
    t.record_precision_sample(0.7)
    assert abs(t.drift - 0.2) < 1e-9


def test_citation_drift_publishes_v7_kpi():
    t = CitationDriftTracker(baseline_precision=0.9)
    t.record_precision_sample(0.7)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.CITATION_SUPPORT_DRIFT)  # type: ignore[arg-type]
    assert abs(sample.value - 0.2) < 1e-9


# ---- AbstainCalibrationTracker --------------------------------------------


def test_abstain_calibration_drift_zero_at_target():
    t = AbstainCalibrationTracker(target_rate=0.05)
    # 5/100 false abstains = 0.05 target = 0 drift
    for _ in range(95):
        t.record_abstain_decision(was_correct=True)
    for _ in range(5):
        t.record_abstain_decision(was_correct=False)
    assert abs(t.calibration_drift) < 1e-9


def test_abstain_calibration_drift_above_target():
    t = AbstainCalibrationTracker(target_rate=0.05)
    for _ in range(80):
        t.record_abstain_decision(was_correct=True)
    for _ in range(20):
        t.record_abstain_decision(was_correct=False)
    # 20/100 = 0.20 vs target 0.05 = drift 0.15
    assert abs(t.calibration_drift - 0.15) < 1e-9


def test_abstain_calibration_publishes_v7_kpi():
    t = AbstainCalibrationTracker(target_rate=0.05)
    t.record_abstain_decision(was_correct=False)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.ABSTAIN_REFUSAL_CALIBRATION_DRIFT)  # type: ignore[arg-type]
    # 1/1 false-rate = 1.0, drift = |1.0 - 0.05| = 0.95
    assert abs(sample.value - 0.95) < 1e-9


# ---- Reset semantics ------------------------------------------------------


def test_all_trackers_support_reset():
    """Every W9 tracker provides a ``reset()`` that zeros state."""
    trackers = [
        ReplayDivergenceLocalizer(),
        SaturationWatcher(),
        ExemplarHitTracker(),
        GauntletFalsePromoteTracker(),
        HeldProposalAgingTracker(),
        GoldenSetRegressionTracker(),
        OrphanArtifactTracker(),
        CitationDriftTracker(),
        AbstainCalibrationTracker(),
    ]
    for t in trackers:
        # mutate some state, then reset
        if hasattr(t, "record_replay"):
            t.record_replay(succeeded=False)  # type: ignore[attr-defined]
        if hasattr(t, "register_capability_eval"):
            t.register_capability_eval("e", 0.0)  # type: ignore[attr-defined]
        if hasattr(t, "record_eligible_plan"):
            t.record_eligible_plan(used_exemplar=True)  # type: ignore[attr-defined]
        if hasattr(t, "record_promotion"):
            t.record_promotion(was_reverted=True)  # type: ignore[attr-defined]
        if hasattr(t, "record_hold_start"):
            t.record_hold_start("p")  # type: ignore[attr-defined]
        if hasattr(t, "record_golden_case"):
            t.record_golden_case(critical=True, passed=False)  # type: ignore[attr-defined]
        if hasattr(t, "record_artifact"):
            t.record_artifact(is_orphan=True)  # type: ignore[attr-defined]
        if hasattr(t, "record_precision_sample"):
            t.record_precision_sample(0.5)  # type: ignore[attr-defined]
        if hasattr(t, "record_abstain_decision"):
            t.record_abstain_decision(was_correct=False)  # type: ignore[attr-defined]
        t.reset()
    # All resets returned without error.
