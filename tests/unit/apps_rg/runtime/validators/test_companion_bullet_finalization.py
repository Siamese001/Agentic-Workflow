"""Companion bullet finalization accepts REAL_LLM product PASS with judge-blocked X3."""

from __future__ import annotations

from apps_rg.runtime.validators.companion_bullet_finalization import (
    ACCEPTED_FINALIZED_COMPANION_STATUS,
    evaluate_companion_bullet_lane_finalized,
)
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS


def _bullets(ids: tuple[str, ...]) -> list[dict]:
    return [{"bullet_id": bid, "bullet_text": f"text {bid}"} for bid in ids]


def test_unify_companion_accepts_review_judge_blocked_x3() -> None:
    l2 = {
        "section_id": "unify_bullets",
        "product_quality_status": "PASS",
        "runtime_generation_status": "REAL_LLM",
        "bullets": _bullets(UNIFY_BULLET_IDS),
    }
    status, reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id="unify_bullets",
        l2_data=l2,
        x3_code="X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
        expected_bullet_ids=UNIFY_BULLET_IDS,
    )
    assert status == ACCEPTED_FINALIZED_COMPANION_STATUS
    assert reason == "ok"


def test_unify_companion_rejects_x3_block() -> None:
    l2 = {
        "section_id": "unify_bullets",
        "product_quality_status": "PASS",
        "runtime_generation_status": "REAL_LLM",
        "bullets": _bullets(UNIFY_BULLET_IDS),
    }
    status, _ = evaluate_companion_bullet_lane_finalized(
        upstream_section_id="unify_bullets",
        l2_data=l2,
        x3_code="X3_BLOCK",
        expected_bullet_ids=UNIFY_BULLET_IDS,
    )
    assert status == "NOT_FINALIZED"


def test_ibm_companion_requires_real_llm() -> None:
    l2 = {
        "section_id": "ibm_bullets",
        "product_quality_status": "PASS",
        "runtime_generation_status": "MOCK",
        "bullets": _bullets(IBM_BULLET_IDS),
    }
    status, reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id="ibm_bullets",
        l2_data=l2,
        x3_code="X3_ALLOW",
        expected_bullet_ids=IBM_BULLET_IDS,
    )
    assert status == "NOT_FINALIZED"
    assert "runtime_not_REAL_LLM" in reason
