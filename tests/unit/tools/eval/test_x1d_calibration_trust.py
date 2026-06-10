from __future__ import annotations

from tools.eval.x1d_calibration_trust import CANONICAL_CALIBRATION_METRIC, evaluate_trust


def _receipt() -> dict:
    return {
        "provider_mode": "live",
        "required_provider_count": 2,
        "calibration": {
            "metric": CANONICAL_CALIBRATION_METRIC,
            "value": 0.72,
            "threshold": 0.6,
            "snapshot_id": "calib-2026-06-10",
            "status": "FRESH",
        },
        "judge_scores": [
            {
                "judge_id": "j1",
                "provider": "gemini_pro",
                "provider_mode": "live",
                "calibration_snapshot_id": "calib-2026-06-10",
                "score": 4,
            },
            {
                "judge_id": "j2",
                "provider": "openai_chatgpt",
                "provider_mode": "live",
                "calibration_snapshot_id": "calib-2026-06-10",
                "score": 4,
            },
        ],
    }


def test_fresh_kappa_snapshot_with_quorum_is_trusted() -> None:
    decision = evaluate_trust(_receipt())

    assert decision.trusted is True
    assert decision.reason_codes == []
    assert decision.calibrated_provider_count == 2


def test_raw_agreement_metric_is_not_accepted() -> None:
    receipt = _receipt()
    receipt["calibration"]["metric"] = "raw_agreement"

    decision = evaluate_trust(receipt)

    assert decision.trusted is False
    assert "CALIBRATION_METRIC_MISMATCH" in decision.reason_codes
    assert "RAW_AGREEMENT_NOT_ACCEPTED" in decision.reason_codes


def test_stale_or_below_threshold_calibration_fails_closed() -> None:
    receipt = _receipt()
    receipt["calibration"]["status"] = "STALE"
    receipt["calibration"]["value"] = 0.4

    decision = evaluate_trust(receipt)

    assert decision.trusted is False
    assert "CALIBRATION_STALE" in decision.reason_codes
    assert "CALIBRATION_BELOW_THRESHOLD" in decision.reason_codes


def test_each_judge_score_must_bind_matching_snapshot() -> None:
    receipt = _receipt()
    receipt["judge_scores"][1]["calibration_snapshot_id"] = "old-calib"

    decision = evaluate_trust(receipt)

    assert decision.trusted is False
    assert "JUDGE_SCORE_1_SNAPSHOT_MISMATCH" in decision.reason_codes
    assert "QUORUM_NOT_MET" in decision.reason_codes


def test_provider_mode_mismatch_blocks_trust() -> None:
    receipt = _receipt()
    receipt["judge_scores"][0]["provider_mode"] = "mock"

    decision = evaluate_trust(receipt)

    assert decision.trusted is False
    assert "JUDGE_SCORE_0_PROVIDER_MODE_MISMATCH" in decision.reason_codes
    assert "QUORUM_NOT_MET" in decision.reason_codes
