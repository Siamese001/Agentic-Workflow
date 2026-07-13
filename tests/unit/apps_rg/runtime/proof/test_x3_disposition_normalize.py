from apps_rg.runtime.proof.x3_disposition_normalize import (
    normalize_x3_code,
    normalize_x3_disposition,
)


def test_normalize_exact_product_allow_finish() -> None:
    assert normalize_x3_code("X3D_ALLOW_FINISH") == "ALLOW_FINISH"
    row = normalize_x3_disposition({"x3_code": "X3D_ALLOW_FINISH", "pass": True})
    assert row["live_x3_allow_claimed"] is True
    assert normalize_x3_code("X3_ALLOW") == "UNKNOWN"
    assert normalize_x3_code("ALLOW") == "UNKNOWN"


def test_normalize_review_blocks_live_claim() -> None:
    assert normalize_x3_code("X3_REVIEW_JUDGE_SOFT_FAIL") == "REVIEW"
    row = normalize_x3_disposition({"x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL", "pass": False})
    assert row["live_x3_allow_claimed"] is False


def test_normalize_unknown_when_missing() -> None:
    assert normalize_x3_code(None) == "UNKNOWN"
    assert normalize_x3_code("") == "UNKNOWN"
