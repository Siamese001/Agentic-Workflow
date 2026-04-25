"""W7 tests for Exit v6 + L2 v4 + L5 v5 engines."""

from __future__ import annotations

from system_learning.engines.exit_v6_engines import (
    ClearanceReceiptTracker,
    ExitDispositionTracker,
    L2ExecuteV4Tracker,
    L5GovernanceV5Tracker,
    X3Disposition,
)
from system_learning.engines.v7_kpi_board import UnifiedKPIBoard, V7KPIName


# ---- ExitDispositionTracker ----------------------------------------------


def test_disposition_uniqueness_all_unique():
    t = ExitDispositionTracker()
    t.record_disposition("r1", X3Disposition.COMMIT)
    t.record_disposition("r2", X3Disposition.ANSWER_ONLY)
    t.record_disposition("r3", X3Disposition.UNKNOWN, unknown_routed_to="X3B")
    assert t.disposition_uniqueness_rate == 1.0


def test_disposition_uniqueness_duplicate_flagged():
    t = ExitDispositionTracker()
    t.record_disposition("r1", X3Disposition.COMMIT)
    t.record_disposition("r1", X3Disposition.ANSWER_ONLY)  # duplicate
    t.record_disposition("r2", X3Disposition.COMMIT)
    assert t.disposition_uniqueness_rate == 0.5


def test_silent_fallback_count():
    t = ExitDispositionTracker()
    t.observe_run("r1")
    t.observe_run("r2")
    t.observe_run("r3")
    t.record_disposition("r1", X3Disposition.COMMIT)
    assert t.silent_fallback_count == 2


def test_safe_abstain_rate():
    t = ExitDispositionTracker()
    t.record_disposition("r1", X3Disposition.SAFE_ABSTAIN, was_ambiguous=True)
    t.record_disposition("r2", X3Disposition.SAFE_ABSTAIN, was_ambiguous=True)
    t.record_disposition("r3", X3Disposition.COMMIT, was_ambiguous=True)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.SAFE_ABSTAIN_RATE)  # type: ignore[arg-type]
    assert sample.value == 2 / 3


def test_unknown_routing_correctness():
    t = ExitDispositionTracker()
    t.record_disposition("r1", X3Disposition.UNKNOWN, unknown_routed_to="X3B")
    t.record_disposition("r2", X3Disposition.UNKNOWN, unknown_routed_to="X3A")
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.UNKNOWN_TO_X3B_ROUTING_CORRECTNESS)  # type: ignore[arg-type]
    assert sample.value == 0.5


def test_disposition_publishes_uniqueness_and_silent_fallback():
    t = ExitDispositionTracker()
    t.observe_run("r1")
    t.observe_run("r2")
    t.record_disposition("r1", X3Disposition.COMMIT)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    uniq = board.latest(V7KPIName.X3_DISPOSITION_UNIQUENESS)  # type: ignore[arg-type]
    silent = board.latest(V7KPIName.SILENT_FALLBACK_COUNT)  # type: ignore[arg-type]
    assert uniq.value == 1.0
    assert silent.value == 1.0


# ---- ClearanceReceiptTracker ---------------------------------------------


def test_commit_path_clearance_completeness():
    t = ClearanceReceiptTracker()
    t.record_commit_run(has_clearance_receipt=True)
    t.record_commit_run(has_clearance_receipt=True)
    t.record_commit_run(has_clearance_receipt=False)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.COMMIT_PATH_CLEARANCE_COMPLETENESS)  # type: ignore[arg-type]
    assert sample.value == 2 / 3


def test_answer_only_clearance_completeness():
    t = ClearanceReceiptTracker()
    t.record_answer_only_run(has_clearance_receipt=True)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.ANSWER_ONLY_CLEARANCE_COMPLETENESS)  # type: ignore[arg-type]
    assert sample.value == 1.0


def test_committed_artifact_uwg_receipt_completeness():
    t = ClearanceReceiptTracker()
    t.record_committed_artifact(has_uwg_receipt=False)
    t.record_committed_artifact(has_uwg_receipt=True)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.COMMITTED_ARTIFACT_UWG_RECEIPT_COMPLETENESS)  # type: ignore[arg-type]
    assert sample.value == 0.5


def test_unauthorized_l4_write_attempts():
    t = ClearanceReceiptTracker()
    t.record_unauthorized_write_attempt()
    t.record_unauthorized_write_attempt()
    t.record_unauthorized_write_attempt()
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.UNAUTHORIZED_L4_WRITE_ATTEMPTS)  # type: ignore[arg-type]
    assert sample.value == 3.0


# ---- L2ExecuteV4Tracker --------------------------------------------------


def test_pass_k_commit_reliability():
    t = L2ExecuteV4Tracker()
    t.record_pass_k_run(succeeded=True)
    t.record_pass_k_run(succeeded=True)
    t.record_pass_k_run(succeeded=False)
    t.record_pass_k_run(succeeded=True)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.PASS_K_COMMIT_RELIABILITY)  # type: ignore[arg-type]
    assert sample.value == 0.75


def test_per_trial_isolation_violations():
    t = L2ExecuteV4Tracker()
    t.record_isolation_violation()
    t.record_isolation_violation()
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.PER_TRIAL_ISOLATION_VIOLATIONS)  # type: ignore[arg-type]
    assert sample.value == 2.0


def test_bounded_work_overrun_rate():
    t = L2ExecuteV4Tracker()
    for _ in range(8):
        t.record_bounded_work_run(overran=False)
    for _ in range(2):
        t.record_bounded_work_run(overran=True)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.BOUNDED_WORK_OVERRUN_RATE)  # type: ignore[arg-type]
    assert sample.value == 0.2


def test_confidence_routing_misroute_rate():
    t = L2ExecuteV4Tracker()
    for _ in range(9):
        t.record_confidence_route(misrouted=False)
    t.record_confidence_route(misrouted=True)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.CONFIDENCE_ROUTING_MISROUTE_RATE)  # type: ignore[arg-type]
    assert sample.value == 0.1


# ---- L5GovernanceV5Tracker -----------------------------------------------


def test_guardrail_bank_pass_rate():
    t = L5GovernanceV5Tracker()
    for _ in range(95):
        t.record_guardrail_check(passed=True)
    for _ in range(5):
        t.record_guardrail_check(passed=False)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.GUARDRAIL_BANK_PASS_RATE)  # type: ignore[arg-type]
    assert sample.value == 0.95


def test_standards_fingerprint_attachment_rate():
    t = L5GovernanceV5Tracker()
    t.record_packet(has_standards_fingerprint=True)
    t.record_packet(has_standards_fingerprint=True)
    t.record_packet(has_standards_fingerprint=False)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.STANDARDS_FINGERPRINT_ATTACHMENT_RATE)  # type: ignore[arg-type]
    assert abs(sample.value - 2 / 3) < 1e-9


def test_shadow_bypass_attempts_detected():
    t = L5GovernanceV5Tracker()
    t.record_shadow_bypass_attempt()
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.SHADOW_BYPASS_ATTEMPTS_DETECTED)  # type: ignore[arg-type]
    assert sample.value == 1.0


def test_guard_model_review_agreement_rate():
    t = L5GovernanceV5Tracker()
    for _ in range(8):
        t.record_guard_review(agrees_with_human=True)
    for _ in range(2):
        t.record_guard_review(agrees_with_human=False)
    board = UnifiedKPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.GUARD_MODEL_REVIEW_AGREEMENT_RATE)  # type: ignore[arg-type]
    assert sample.value == 0.8


# ---- defaults & resets ---------------------------------------------------


def test_default_rates_are_neutral_when_no_observations():
    """All ratio KPIs return 1.0 (or 0.0 for overrun-style) with zero observations."""
    e, c, l2, gv = (
        ExitDispositionTracker(),
        ClearanceReceiptTracker(),
        L2ExecuteV4Tracker(),
        L5GovernanceV5Tracker(),
    )
    board = UnifiedKPIBoard()
    e.publish_kpi_sample(board)
    c.publish_kpi_sample(board)
    l2.publish_kpi_sample(board)
    gv.publish_kpi_sample(board)
    assert board.latest(V7KPIName.X3_DISPOSITION_UNIQUENESS).value == 1.0  # type: ignore[arg-type]
    assert board.latest(V7KPIName.SAFE_ABSTAIN_RATE).value == 1.0  # type: ignore[arg-type]
    assert board.latest(V7KPIName.PASS_K_COMMIT_RELIABILITY).value == 1.0  # type: ignore[arg-type]
    assert board.latest(V7KPIName.BOUNDED_WORK_OVERRUN_RATE).value == 0.0  # type: ignore[arg-type]
    assert board.latest(V7KPIName.GUARDRAIL_BANK_PASS_RATE).value == 1.0  # type: ignore[arg-type]


def test_resets_zero_state():
    e = ExitDispositionTracker()
    e.record_disposition("r1", X3Disposition.COMMIT)
    e.record_disposition("r1", X3Disposition.ANSWER_ONLY)
    assert e.disposition_uniqueness_rate < 1.0
    e.reset()
    assert e.disposition_uniqueness_rate == 1.0
    assert e.silent_fallback_count == 0
