import json
from pathlib import Path

import yaml

from apps_lic.engines.e2e_acceptance import (
    ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE,
    ACCEPTANCE_MODE_STRICT_TARGET_FIT,
    NO_WEAKENING_REQUIRED_GATE_IDS,
    ROW_ALL_CLEAR_REMEDIATION_REQUIRED,
    ROW_POLICY_CORRECT_BLOCK,
    evaluate_e2e_acceptance,
)
from apps_lic.engines.validation_exit import GATE_RECIPIENT_CLASS, GATE_ROLE_OWNERSHIP_FIT


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "apps_lic" / "config" / "domain_contract" / "apps_lic_redesign_w0_contracts.yaml"
BASELINE_PATH = ROOT / "apps_lic" / "contracts" / "apps_lic_redesign_w0_baseline.md"
AIG_30_RESULTS_PATH = (
    ROOT
    / "artifacts"
    / "apps_lic"
    / "e2e_aig_30_linkedin_profiles_20260608"
    / "results.json"
)
AIG_30_FIXTURE_PATH = ROOT / "tests" / "apps_lic" / "fixtures" / "aig_30_profiles.json"


def load_contract() -> dict:
    with CONTRACT_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_aig_30_rows() -> list[dict]:
    if not AIG_30_RESULTS_PATH.exists():
        with AIG_30_FIXTURE_PATH.open(encoding="utf-8") as handle:
            return json.load(handle)["profiles"]
    with AIG_30_RESULTS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)["rows"]


def test_w0_artifacts_are_contract_freeze_only() -> None:
    contract = load_contract()

    assert BASELINE_PATH.exists()
    assert contract["w0_status"]["wave"] == "W0"
    assert contract["w0_status"]["implemented_as_contract_freeze_only"] is True
    assert contract["w0_status"]["no_runtime_behavior_changes"] is True


def test_five_message_types_are_frozen() -> None:
    contract = load_contract()

    assert contract["canonical_message_types"]["values"] == [
        "general_intro",
        "role_specific",
        "trigger_based_insight",
        "referral_ask",
        "follow_up",
    ]


def test_recipient_class_must_be_derived_by_c0() -> None:
    contract = load_contract()

    assert contract["recipient_classes"]["mandatory"] is True
    assert contract["recipient_classes"]["derivation_authority"] == "C0"
    assert contract["u0_seed_contract"]["authority_limits"]["recipient_class"] == "hint_only_must_be_derived_by_c0"
    assert contract["recipient_class_derivation"]["authority"] == "C0"
    assert "public_profile_snippets" in contract["recipient_class_derivation"]["c0_must_use"]
    assert "role_ownership_signals" in contract["recipient_class_derivation"]["c0_must_use"]


def test_role_specific_recruiter_and_senior_ta_require_jd_title_and_req() -> None:
    contract = load_contract()
    role_specific = contract["message_type_requirement_matrix"]["role_specific"]
    jd_contract = contract["jd_facts_contract"]

    assert role_specific["jd_required"] is True
    assert jd_contract["globally_optional"] is True
    assert jd_contract["required_fields_for_recruiter_or_senior_ta_role_specific"] == [
        "position_name",
        "requisition_number",
    ]
    assert role_specific["requirements_by_recipient_class"]["RECRUITER"]["required_fields"] == [
        "position_name",
        "requisition_number",
    ]
    assert role_specific["requirements_by_recipient_class"]["SENIOR_TA"]["required_fields"] == [
        "position_name",
        "requisition_number",
    ]


def test_c0_does_not_silently_ingest_or_write_vectors_during_inference() -> None:
    contract = load_contract()
    c0 = contract["c0_evidence_packet_contract"]

    assert c0["inference_may_write_vectors"] is False
    assert c0["silent_evidence_acquisition"] == "denied"
    assert c0["governed_ingestion_boundary"]["ingestion_is_separate_from_inference"] is True
    assert "C0_OPPORTUNITY_INGESTION_REQUIRED" in c0["readiness_status_values"]
    assert "C0_VECTOR_BACKEND_UNAVAILABLE" in c0["readiness_status_values"]


def test_w0_acceptance_modes_are_frozen_for_aig_30() -> None:
    contract = load_contract()
    modes = contract["e2e_acceptance_modes"]["modes"]

    assert contract["e2e_acceptance_modes"]["default_mode"] == ACCEPTANCE_MODE_STRICT_TARGET_FIT
    assert set(modes) == {ACCEPTANCE_MODE_STRICT_TARGET_FIT, ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE}
    assert modes[ACCEPTANCE_MODE_STRICT_TARGET_FIT]["current_aig_30_expected"] == {
        "profile_count": 30,
        "clear_draft_count": 24,
        "policy_correct_block_count": 6,
        "policy_correct_block_ids": [
            "daisuke_hayashi",
            "kathleen_gerstner",
            "dennis_najar",
            "anirudh_r",
            "karthikeya_gowd",
            "indu_sri",
        ],
    }
    assert modes[ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE]["current_aig_30_expected"] == {
        "full_30_without_remediation_passes": False,
        "remediation_required_count": 6,
    }
    assert tuple(contract["no_weakening_invariants"]["required_gate_ids"]) == NO_WEAKENING_REQUIRED_GATE_IDS


def test_strict_target_fit_accepts_24_clear_and_6_policy_correct_blocks() -> None:
    rows = load_aig_30_rows()

    report = evaluate_e2e_acceptance(
        rows,
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        expected_profile_count=30,
        expected_clear_draft_count=24,
        expected_policy_correct_block_count=6,
    )

    assert report.passed is True
    assert report.clear_draft_count == 24
    assert report.policy_correct_block_count == 6
    assert report.no_weakening_violations == ()
    assert {
        row.profile_id
        for row in report.rows
        if row.status == ROW_POLICY_CORRECT_BLOCK
    } == {
        "daisuke_hayashi",
        "kathleen_gerstner",
        "dennis_najar",
        "anirudh_r",
        "karthikeya_gowd",
        "indu_sri",
    }


def test_all_clear_eligible_fails_full_30_until_blocked_rows_are_remediated() -> None:
    rows = load_aig_30_rows()

    report = evaluate_e2e_acceptance(
        rows,
        mode=ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE,
        expected_profile_count=30,
    )

    assert report.passed is False
    assert report.clear_draft_count == 24
    assert report.remediation_required_count == 6
    assert {
        row.profile_id
        for row in report.rows
        if row.status == ROW_ALL_CLEAR_REMEDIATION_REQUIRED
    } == {
        "daisuke_hayashi",
        "kathleen_gerstner",
        "dennis_najar",
        "anirudh_r",
        "karthikeya_gowd",
        "indu_sri",
    }


def test_strict_mode_keeps_daisuke_blocked_for_role_ownership_region_mismatch() -> None:
    rows = load_aig_30_rows()
    daisuke = next(row for row in rows if row["id"] == "daisuke_hayashi")

    report = evaluate_e2e_acceptance([daisuke], mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT)
    result = report.rows[0]

    assert result.status == ROW_POLICY_CORRECT_BLOCK
    assert result.reason == "role_ownership_or_region_fit_block"
    assert GATE_ROLE_OWNERSHIP_FIT in result.failed_gates


def test_unknown_contacts_do_not_become_sendable_drafts_under_strict_mode() -> None:
    rows = [
        row
        for row in load_aig_30_rows()
        if row["id"] in {"kathleen_gerstner", "dennis_najar", "anirudh_r", "karthikeya_gowd", "indu_sri"}
    ]

    report = evaluate_e2e_acceptance(rows, mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT)

    assert report.passed is True
    assert report.clear_draft_count == 0
    assert report.policy_correct_block_count == 5
    assert all(row.status == ROW_POLICY_CORRECT_BLOCK for row in report.rows)
    assert all(GATE_RECIPIENT_CLASS in row.failed_gates for row in report.rows)


def test_reasoning_and_judge_depth_match_v2_policy() -> None:
    contract = load_contract()
    judge = contract["x1d_judge_contract"]
    policy = contract["reasoning_policy"]

    assert policy["default"]["sc_level"] == "SC-1"
    assert policy["policy_by_message_and_recipient"]["general_intro"]["RECRUITER"]["x1d_llm_judges"] == 0
    assert policy["policy_by_message_and_recipient"]["trigger_based_insight"]["CEO"]["x1d_llm_judges"] == 2
    assert judge["default_model"] == "GPT-5.5"
    assert judge["independence_required_from_generator"] is True
    assert judge["llm_judge_depth"]["ceo"] == 2


def test_baseline_documents_current_gaps() -> None:
    baseline = BASELINE_PATH.read_text(encoding="utf-8")

    assert "Current canonical apps_lic C0 behavior is inline-evidence only." in baseline
    assert "PA uses temperature `0.5`." in baseline
    assert "LinkedIn caps are broadly `60` words for cold and `80` words" in baseline
    assert "No runtime behavior changes" in baseline
