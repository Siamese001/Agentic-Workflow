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


def test_build_ambiguity_register_is_empty_when_required_signals_present() -> None:
    assert (
        build_ambiguity_register(
            {
                "target_company": "Acme",
                "target_role": "VP AI",
                "target_level": "executive",
                "job_description_text": "Lead AI strategy",
                "source_resume_text": "Resume body",
            }
        )
        == {}
    )


def test_build_ambiguity_register_records_missing_l1_planning_inputs() -> None:
    register = build_ambiguity_register(
        {
            "target_company": "Acme",
            "job_description_text": "",
            "source_resume_text": "",
        }
    )

    assert register["schema_version"] == "apps_rg_ambiguity_register_v1"
    assert register["register_id"].startswith("amb-")
    assert {entry["code"] for entry in register["entries"]} == {
        "TARGET_ROLE_MISSING",
        "TARGET_LEVEL_UNSPECIFIED",
        "JOB_DESCRIPTION_EMPTY",
        "SOURCE_RESUME_EMPTY",
    }
