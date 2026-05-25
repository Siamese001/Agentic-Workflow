from apps_rg.runtime.proof.x3_disposition_normalize import (
    normalize_x3_code,
    normalize_x3_disposition,
)


def test_normalize_allow_family() -> None:
    assert normalize_x3_code("X3_ALLOW") == "ALLOW_FINISH"
    row = normalize_x3_disposition({"x3_code": "X3_ALLOW", "pass": True})
    assert row["live_x3_allow_claimed"] is True


def test_normalize_review_blocks_live_claim() -> None:
    assert normalize_x3_code("X3_REVIEW_JUDGE_SOFT_FAIL") == "REVIEW"
    row = normalize_x3_disposition({"x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL", "pass": False})
    assert row["live_x3_allow_claimed"] is False


def test_normalize_unknown_when_missing() -> None:
    assert normalize_x3_code(None) == "UNKNOWN"
    assert normalize_x3_code("") == "UNKNOWN"
