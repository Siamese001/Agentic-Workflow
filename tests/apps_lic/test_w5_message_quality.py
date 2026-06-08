import json
from pathlib import Path

import yaml

from apps_lic.engines.e2e_acceptance import ACCEPTANCE_MODE_STRICT_TARGET_FIT
from apps_lic.engines.message_quality import (
    BANNED_GENERIC_PHRASES,
    GATE_BANNED_GENERIC_PHRASE,
    GATE_IDENTICAL_DRAFTS,
    GATE_UNSUPPORTED_SENDER_CLAIM,
    NGRAM_SIMILARITY_CEILING,
    PROVIDER_BACKED_GENERATION_POLICY,
    REASON_MISSING_JD_TITLE_OR_REQ,
    REASON_UNSUPPORTED_SENDER_CLAIM,
    STATUS_MESSAGE_QUALITY_PASS,
    apply_message_quality_variants,
    validate_message_quality,
)
from apps_lic.engines.x1d_preflight import X1D_MODE_FAKE
from scripts.apps_lic.run_aig_30_profile_e2e import run_aig_30_profile_e2e


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "tests" / "apps_lic" / "fixtures" / "aig_30_profiles.json"
W6_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "whole_message_generation.v1.yaml"
)


def _fixture_rows() -> tuple[dict, ...]:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return tuple(dict(row) for row in fixture["profiles"])


def _clear_rows(rows):
    return tuple(row for row in rows if row.get("exit_disposition") == "clear_draft")


def test_w5_quality_variants_make_at_least_five_recruiter_messages_non_identical() -> None:
    rows = apply_message_quality_variants(_fixture_rows())
    recruiter_rows = [
        row
        for row in _clear_rows(rows)
        if row["derived_class"] == "RECRUITER"
    ]

    assert len(recruiter_rows) >= 5
    assert len({row["draft_text"] for row in recruiter_rows}) >= 5
    assert {row["message_quality_status"] for row in recruiter_rows} == {STATUS_MESSAGE_QUALITY_PASS}
    assert all(row["rhetorical_angle"] for row in recruiter_rows)
    assert all(row["recipient_class_cta"] for row in recruiter_rows)


def test_w5_quality_report_passes_24_clear_aig_drafts_after_variants() -> None:
    rows = apply_message_quality_variants(_fixture_rows())
    report = validate_message_quality(rows)

    assert report.passed is True
    assert report.status == STATUS_MESSAGE_QUALITY_PASS
    assert report.clear_draft_count == 24
    assert report.diversity_passed_count == 24
    assert report.max_ngram_similarity <= NGRAM_SIMILARITY_CEILING
    assert report.violations == ()


def test_w5_role_specific_variants_preserve_jd_title_and_req_for_recruiting_targets() -> None:
    rows = apply_message_quality_variants(_fixture_rows())
    recruiting_rows = [
        row
        for row in _clear_rows(rows)
        if row["message_type"] == "role_specific"
        and row["derived_class"] in {"RECRUITER", "SENIOR_TA"}
    ]

    assert recruiting_rows
    for row in recruiting_rows:
        assert row["jd_position_name"] in row["draft_text"]
        assert row["jd_requisition_number"] in row["draft_text"]
        assert row["claims_used"]


def test_w5_identical_normalized_drafts_block_even_when_names_differ() -> None:
    rows = [
        {
            "id": "r1",
            "profile_id": "r1",
            "name": "Alice One",
            "derived_class": "RECRUITER",
            "message_type": "role_specific",
            "exit_disposition": "clear_draft",
            "jd_position_name": "VP, Global Head of Agentic AI Solutions",
            "jd_requisition_number": "JR2601998",
            "claims_used": ["sp_agentic_platform"],
            "draft_text": (
                "Hi Alice, AIG's VP, Global Head of Agentic AI Solutions (JR2601998) "
                "reads like a platform governance mandate. My relevant proof: designed and "
                "operationalized a governed agentic AI platform for regulated enterprise workflows. "
                "Would a targeted resume review help?"
            ),
        },
        {
            "id": "r2",
            "profile_id": "r2",
            "name": "Bob Two",
            "derived_class": "RECRUITER",
            "message_type": "role_specific",
            "exit_disposition": "clear_draft",
            "jd_position_name": "VP, Global Head of Agentic AI Solutions",
            "jd_requisition_number": "JR2601998",
            "claims_used": ["sp_agentic_platform"],
            "draft_text": (
                "Hi Bob, AIG's VP, Global Head of Agentic AI Solutions (JR2601998) "
                "reads like a platform governance mandate. My relevant proof: designed and "
                "operationalized a governed agentic AI platform for regulated enterprise workflows. "
                "Would a targeted resume review help?"
            ),
        },
    ]

    report = validate_message_quality(rows)

    assert report.passed is False
    assert any(violation.gate_id == GATE_IDENTICAL_DRAFTS for violation in report.violations)


def test_w5_banned_generic_phrase_and_unsupported_sender_claims_block() -> None:
    rows = [
        {
            "id": "bad",
            "profile_id": "bad",
            "name": "Casey Target",
            "derived_class": "RECRUITER",
            "message_type": "general_intro",
            "exit_disposition": "clear_draft",
            "claims_used": ["sp_not_in_corpus"],
            "draft_text": (
                "Hi Casey, hope you're doing well. I came across your profile and would love to connect."
            ),
        }
    ]

    report = validate_message_quality(rows)
    gates = {violation.gate_id for violation in report.violations}
    reasons = {violation.reason_code for violation in report.violations}

    assert report.passed is False
    assert GATE_BANNED_GENERIC_PHRASE in gates
    assert GATE_UNSUPPORTED_SENDER_CLAIM in gates
    assert REASON_UNSUPPORTED_SENDER_CLAIM in reasons
    assert "hope you're doing well" in BANNED_GENERIC_PHRASES


def test_w5_missing_jd_title_or_req_blocks_role_specific_recruiter_copy() -> None:
    rows = [
        {
            "id": "missing-jd",
            "profile_id": "missing-jd",
            "name": "Robin Target",
            "derived_class": "RECRUITER",
            "message_type": "role_specific",
            "exit_disposition": "clear_draft",
            "jd_position_name": "VP, Global Head of Agentic AI Solutions",
            "jd_requisition_number": "JR2601998",
            "claims_used": ["sp_agentic_platform"],
            "draft_text": (
                "Hi Robin, the AIG role reads like a platform governance mandate. "
                "My relevant proof: designed and operationalized a governed agentic AI platform "
                "for regulated enterprise workflows. Would a targeted resume review help?"
            ),
        }
    ]

    report = validate_message_quality(rows)

    assert report.passed is False
    assert any(violation.reason_code == REASON_MISSING_JD_TITLE_OR_REQ for violation in report.violations)


def test_w5_runner_summary_carries_quality_report_and_passes(tmp_path: Path) -> None:
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    results = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    clear_messages = (tmp_path / "messages_clear_drafts.md").read_text(encoding="utf-8")

    assert summary["message_quality_passed"] is True
    assert summary["message_quality"]["clear_draft_count"] == 24
    assert summary["message_quality"]["violation_count"] == 0
    assert results["message_quality"]["passed"] is True
    assert "My relevant proof:" in clear_messages
    assert "which maps to the platform and governance work behind this kind of mandate" not in clear_messages


def test_w5_provider_backed_generation_requires_explicit_config() -> None:
    with W6_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    provider_path = config["provider_backed_generation"]
    policy = PROVIDER_BACKED_GENERATION_POLICY.to_packet()

    assert provider_path["enabled_by_default"] is False
    assert provider_path["requires_explicit_config"] is True
    assert provider_path["draft_only_required"] is True
    assert provider_path["no_send_authority"] is True
    assert provider_path["high_temperature_bounds"]["generator_temperature_min"] >= 0.90
    assert policy["enabled_by_default"] is False
    assert policy["requires_explicit_config"] is True
    assert policy["whole_message_only"] is True
