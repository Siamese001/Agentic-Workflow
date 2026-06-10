from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "x1d_repair_loop_live_12_red_rows.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _all_issue_ids(rows: list[dict]) -> set[str]:
    return {
        issue
        for row in rows
        for judge in row["failed_judges"]
        for issue in judge["issues"]
    }


def _all_required_repairs(rows: list[dict]) -> set[str]:
    return {
        repair
        for row in rows
        for judge in row["failed_judges"]
        for repair in judge["required_repairs"]
    }


def test_w0_fixture_locks_failed_main_12_row_gate_scope() -> None:
    fixture = _fixture()
    rows = fixture["red_rows"]

    assert fixture["schema_version"] == (
        "apps_lic.x1d_repair_loop_live_12_red_rows_fixture.v1"
    )
    assert fixture["gate_role"] == "main_full_e2e_gate"
    assert fixture["gate_shape"] == "4_per_company_12_archetype_matrix"
    assert fixture["rca_scope"] == "live_w5_x1d_judge_feedback_repair_loop_only"
    assert len(rows) == 8
    assert {row["company_key"] for row in rows} == {"aig", "citi", "neo4j"}

    assert Counter(row["repair_stop_reason"] for row in rows) == {
        "repair_budget_exhausted": 7,
        "repair_same_as_parent": 1,
    }


def test_w0_fixture_proves_harness_and_judges_were_not_missing() -> None:
    for row in _fixture()["red_rows"]:
        assert row["x2_status"] == "X2_VALIDATION_PASS"
        assert row["x1d_status"] == "X1D_REVIEW_REQUIRED"
        assert row["x1d_missing_judge_ids"] == []
        assert row["x1d_required_judge_ids"]
        assert row["repair_attempted"] is True
        assert row["repair_iteration_count"] == 1
        assert row["repair_budget"] == 1
        assert row["parent_candidate"]["source_artifact"] == "w4_candidate_batch.json"
        assert row["repair_candidate"]["source_artifact"] == "w5_validation_exit.json"
        assert row["parent_candidate"]["digest"].startswith("sha256:")
        assert row["repair_candidate"]["digest"].startswith("sha256:")


def test_w0_fixture_preserves_same_text_and_budget_exhaustion_modes() -> None:
    rows = {row["row_id"]: row for row in _fixture()["red_rows"]}

    same_text = rows["aig_regina_gilligan"]
    assert same_text["repair_stop_reason"] == "repair_same_as_parent"
    assert (
        same_text["parent_candidate"]["digest"]
        == same_text["repair_candidate"]["digest"]
    )

    budget_exhausted_rows = [
        row
        for row in rows.values()
        if row["repair_stop_reason"] == "repair_budget_exhausted"
    ]
    assert len(budget_exhausted_rows) == 7
    assert all(
        row["parent_candidate"]["digest"] != row["repair_candidate"]["digest"]
        for row in budget_exhausted_rows
    )


def test_w0_fixture_captures_observed_live_judge_repair_directives() -> None:
    rows = _fixture()["red_rows"]
    issues = _all_issue_ids(rows)
    repairs = _all_required_repairs(rows)

    assert "duplicate_closing_signature_and_fragmented_structure" in issues
    assert "duplicate_sign_off_amit_appears_twice_structural_error" in issues
    assert "sp_platform_commercialization_claim_omitted_from_draft_despite_approval" in issues
    assert "omits_approved_commercialization_claim_sp_platform_commercialization" in issues
    assert "generic_phrasing_without_specific_aig_trigger_hook" in issues
    assert "role_name_repetition_reduces_naturalness" in issues
    assert "repetitive_role_title_overuse" in issues
    assert "word_count_158_exceeds_120_word_advisory_budget" in issues

    assert "remove_duplicate_amit_signature_and_restructure_as_single_coherent_message" in repairs
    assert "add_22m_revenue_or_margin_metric_from_sp_platform_commercialization_to_ground_scale_signal" in repairs
    assert "reduce_role_name_repetition_to_at_most_one_inline_reference" in repairs
    assert "add_specific_neo4j_trigger_signal_in_opening_sentence" in repairs


def test_w0_fixture_keeps_15_row_soak_secondary() -> None:
    secondary = _fixture()["secondary_soak"]

    assert secondary["gate_role"] == "secondary_live_company_soak"
    assert secondary["gate_shape"] == "5_per_company_15_company_validation"
    assert secondary["is_primary_gate"] is False
    assert secondary["acceptance_passed"] is True
    assert secondary["canonical_runtime_rows"] == 15
    assert secondary["quality_violation_count"] == 0
