from __future__ import annotations

from apps_eval.l6_eval_ladder import EvalLevel, build_l6_eval_execution_receipt


def test_micro_eval_can_be_deterministic_without_live_writer() -> None:
    receipt = build_l6_eval_execution_receipt(
        eval_level=EvalLevel.MICRO,
        deterministic_only=True,
        writer_live=False,
        graders_live=False,
    )
    assert receipt.execution_claim_status == "PASS"
    assert receipt.current_run_authority == "NONE"


def test_deterministic_fixture_cannot_claim_lane_or_suite() -> None:
    for level in (EvalLevel.LANE, EvalLevel.SUITE):
        receipt = build_l6_eval_execution_receipt(
            eval_level=level,
            deterministic_only=True,
            writer_live=False,
            graders_live=False,
        )
        assert receipt.execution_claim_status == "FAIL"
        assert "deterministic_fixture_cannot_claim_lane_or_suite_eval" in receipt.reason_codes
        assert "live_writer_required" in receipt.reason_codes
        assert "live_graders_required" in receipt.reason_codes


def test_meta_eval_requires_human_labels_and_fresh_calibration() -> None:
    receipt = build_l6_eval_execution_receipt(
        eval_level=EvalLevel.META,
        deterministic_only=False,
        writer_live=False,
        graders_live=True,
        human_labels_present=False,
        calibration_fresh=False,
    )
    assert receipt.execution_claim_status == "FAIL"
    assert "human_labels_required" in receipt.reason_codes
    assert "fresh_calibration_required" in receipt.reason_codes

    passing = build_l6_eval_execution_receipt(
        eval_level=EvalLevel.META,
        deterministic_only=False,
        writer_live=False,
        graders_live=True,
        human_labels_present=True,
        calibration_fresh=True,
    )
    assert passing.execution_claim_status == "PASS"
