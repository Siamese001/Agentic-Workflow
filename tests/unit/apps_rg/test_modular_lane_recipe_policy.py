"""Unit tests: modular lane eligibility and recipe-level PASS policy (v1)."""

from __future__ import annotations

import json

from apps_rg.l2_recipe.modular_lane_recipe_policy import (
    RECIPE_PASS_POLICY_VERSION,
    classify_modular_lane_recipe_eligibility,
    summarize_modular_lane_recipe_policy,
)
from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult


def _row(
    *,
    lane: str = "headline",
    gen: str = "REAL_LLM",
    attempted: bool = True,
    schema: str = "lane_x2_pass",
    x3: str = "X3_ALLOW",
) -> dict:
    return {
        "section_lane": lane,
        "generation_status": gen,
        "provider_call_attempted": attempted,
        "section_schema_validation_status": schema,
        "decisive_reason_code": x3,
    }


def test_judge_provider_blocked_x2_pass_is_degraded_not_fatal() -> None:
    r = _row(x3="X3_REVIEW_JUDGE_PROVIDER_BLOCKED")
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=True) == "DEGRADED_ALLOWED"


def test_x3_block_with_x2_pass_is_degraded_judge_path() -> None:
    r = _row(x3="X3_BLOCK")
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=True) == "DEGRADED_ALLOWED"


def test_mocked_generation_is_fatal() -> None:
    r = _row(gen="MOCKED", x3="X3_ALLOW")
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=True) == "FATAL"


def test_missing_lane_run_is_fatal() -> None:
    r = _row(gen="MISSING_LANE_RUN", schema="missing", x3="PHASE1_NO_RUN_DIR")
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=True) == "FATAL"


def test_lane_x2_fail_is_fatal() -> None:
    r = _row(schema="lane_x2_fail", x3="X3_BLOCK")
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=True) == "FATAL"


def test_blocked_deterministic_x3_fatal_even_if_x2_pass() -> None:
    r = _row(x3="X3_BLOCKED_DETERMINISTIC_GATES")
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=True) == "FATAL"


def test_mocked_plumbing_x3_fatal() -> None:
    r = _row(x3="X3_REVIEW_MOCKED_PLUMBING_ONLY")
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=True) == "FATAL"


def test_provider_not_attempted_fatal() -> None:
    r = _row(attempted=False, x3="X3_ALLOW")
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=True) == "FATAL"


def test_enforce_off_classifies_pass() -> None:
    r = _row(gen="MOCKED", schema="lane_x2_fail", attempted=False)
    assert classify_modular_lane_recipe_eligibility(r, enforce_product_lane_requirements=False) == "PASS"


def test_summarize_counts_and_why_string() -> None:
    rows = [
        _row(lane="headline", x3="X3_REVIEW_JUDGE_PROVIDER_BLOCKED"),
        _row(lane="executive_summary", x3="X3_ALLOW"),
    ]
    s = summarize_modular_lane_recipe_policy(rows, enforce_product_lane_requirements=True)
    assert s["recipe_pass_policy_version"] == RECIPE_PASS_POLICY_VERSION
    assert s["fatal_lane_failures"] == []
    assert len(s["degraded_allowed_lane_warnings"]) == 1
    assert s["judge_provider_blocked_count"] == 1
    assert s["deterministic_lane_pass_count"] == 2
    assert "Recipe PASS allowed under v1" in s["why_recipe_pass_allowed_despite_lane_warnings"]


def test_summarize_fatal_list() -> None:
    rows = [_row(lane="executive_summary", schema="lane_x2_fail", x3="X3_BLOCK")]
    s = summarize_modular_lane_recipe_policy(rows, enforce_product_lane_requirements=True)
    assert len(s["fatal_lane_failures"]) == 1
    assert s["degraded_allowed_lane_warnings"] == []
    assert s["why_recipe_pass_allowed_despite_lane_warnings"] == ""


def test_ok_for_recipe_false_when_extras_fatal_policy() -> None:
    mr = ModularR4GenerationResult(
        generated_resume={"headline": "A | B | C"},
        section_provider_calls_ref="m",
        section_output_refs={},
        merge_receipt_ref="m",
        schema_validation_receipt_ref="m",
        final_schema_valid=True,
        decisive_status="PASS",
        failure_reason="",
        provider_call_count=7,
        locked_sections_provider_calls_detected=False,
        lanes_executed=7,
        lane_outputs_valid=True,
        final_merge_attempted=True,
        rg_output_merge_receipt_ref="m",
        extras={
            "recipe_lane_policy": {
                "fatal_lane_failures": [{"section_lane": "executive_summary", "reason": "x"}],
            },
        },
    )
    assert mr.ok_for_recipe_context() is False


def test_section_calls_contract_phase1_v2_roundtrip() -> None:
    """Golden shape: policy blob is JSON-serializable."""
    rows = [_row(x3="X3_REVIEW_JUDGE_PROVIDER_BLOCKED")]
    s = summarize_modular_lane_recipe_policy(rows, enforce_product_lane_requirements=True)
    json.dumps(s)
