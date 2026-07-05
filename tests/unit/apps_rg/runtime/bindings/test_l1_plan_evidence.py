"""apps-test-model: APP CONTRACT."""

from __future__ import annotations

from apps_rg.runtime.bindings.l1_plan_evidence import (
    build_ambiguity_register,
    build_validation_receipt_id,
)


def test_build_validation_receipt_id_is_stable_and_request_scoped() -> None:
    first = build_validation_receipt_id(
        request_id="req-1234567890",
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-a",
    )
    second = build_validation_receipt_id(
        request_id="req-1234567890",
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-a",
    )
    changed = build_validation_receipt_id(
        request_id="req-1234567890",
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-b",
    )

    assert first == second
    assert first != changed
    assert first.startswith("l1val-req-1234-")


def test_build_ambiguity_register_is_stable_when_required_signals_present() -> None:
    first = build_ambiguity_register(
        {
            "target_company": "Acme",
            "target_role": "VP AI",
            "target_level": "executive",
            "job_description_text": "Lead AI strategy",
            "source_resume_text": "Resume body",
        },
        request_id="req-ok",
        planning_profile_digest="digest-ok",
    )
    second = build_ambiguity_register(
        {
            "target_company": "Acme",
            "target_role": "VP AI",
            "target_level": "executive",
            "job_description_text": "Lead AI strategy",
            "source_resume_text": "Resume body",
        },
        request_id="req-ok",
        planning_profile_digest="digest-ok",
    )

    assert first == second
    assert first["schema_version"] == "apps_rg_ambiguity_register_v2"
    assert first["entries"] == []
    assert first["max_severity"] == "none"
    assert first["blocks_progress"] is False
    assert first["hitl_hint"] == "none"
    assert first["register_digest"].startswith("sha256:")


def test_build_ambiguity_register_records_missing_l1_planning_inputs() -> None:
    register = build_ambiguity_register(
        {
            "target_company": "Acme",
            "job_description_text": "",
            "source_resume_text": "",
        }
    )

    assert register["schema_version"] == "apps_rg_ambiguity_register_v2"
    assert register["register_id"].startswith("amb-")
    assert register["register_digest"].startswith("sha256:")
    assert register["max_severity"] == "high"
    assert register["blocks_progress"] is True
    assert register["hitl_hint"] == "required"
    assert {entry["code"] for entry in register["entries"]} == {
        "TARGET_ROLE_MISSING",
        "TARGET_LEVEL_UNSPECIFIED",
        "JOB_DESCRIPTION_EMPTY",
        "SOURCE_RESUME_EMPTY",
    }
