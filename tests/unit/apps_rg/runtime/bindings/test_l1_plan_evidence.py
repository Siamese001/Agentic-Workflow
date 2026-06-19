from __future__ import annotations

from apps_rg.runtime.bindings.l1_plan_evidence import (
    build_ambiguity_register,
    build_completion_criteria,
    build_planning_capsule_ref,
    build_planning_prior_set_ref,
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
    assert register["max_severity"] == "high"
    assert register["entry_count"] == 4
    assert {entry["code"] for entry in register["entries"]} == {
        "TARGET_ROLE_MISSING",
        "TARGET_LEVEL_UNSPECIFIED",
        "JOB_DESCRIPTION_EMPTY",
        "SOURCE_RESUME_EMPTY",
    }


def test_build_ambiguity_register_is_deterministic_and_carries_planner_actions() -> None:
    register_a = build_ambiguity_register(
        {
            "target_company": "Acme",
            "job_description_text": "",
            "source_resume_text": "",
        }
    )
    register_b = build_ambiguity_register(
        {
            "target_company": "Acme",
            "job_description_text": "",
            "source_resume_text": "",
        }
    )

    assert register_a == register_b
    entry = next(item for item in register_a["entries"] if item["code"] == "JOB_DESCRIPTION_EMPTY")
    assert entry["severity_rank"] == 3
    assert entry["default_assumption_allowed"] is False
    assert entry["planner_action"] == "stop_and_request_input"


def test_build_planning_prior_and_capsule_refs_are_stable_and_version_bound() -> None:
    prior_set_ref = build_planning_prior_set_ref(
        generation_mode="strategic_tailor",
        target_level="EXECUTIVE",
        planning_prior_refs=("apps_rg/profiles/rg_planning_profile.yaml",),
        prompt_bom_refs=("apps_rg/prompts/resume_v1",),
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-a",
    )
    prior_set_ref_same = build_planning_prior_set_ref(
        generation_mode="strategic_tailor",
        target_level="EXECUTIVE",
        planning_prior_refs=("apps_rg/profiles/rg_planning_profile.yaml",),
        prompt_bom_refs=("apps_rg/prompts/resume_v1",),
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-a",
    )
    prior_set_ref_changed = build_planning_prior_set_ref(
        generation_mode="strategic_tailor",
        target_level="EXECUTIVE",
        planning_prior_refs=("apps_rg/profiles/rg_planning_profile.yaml",),
        prompt_bom_refs=("apps_rg/prompts/resume_v1",),
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-b",
    )

    assert prior_set_ref == prior_set_ref_same
    assert prior_set_ref != prior_set_ref_changed
    assert prior_set_ref.startswith("l1priors-")

    completion_criteria = build_completion_criteria(
        active_generation_mode=True,
        planning_prior_set_ref=prior_set_ref,
        ambiguity_register={
            "entries": (
                {
                    "code": "TARGET_LEVEL_UNSPECIFIED",
                    "severity": "low",
                },
                {
                    "code": "JOB_DESCRIPTION_EMPTY",
                    "severity": "high",
                },
            ),
        },
        planning_prior_refs=("apps_rg/profiles/rg_planning_profile.yaml",),
        prompt_bom_refs=("apps_rg/prompts/resume_v1",),
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-a",
    )
    capsule_ref = build_planning_capsule_ref(
        generation_mode="strategic_tailor",
        target_level="EXECUTIVE",
        task_plan=("validate_ingress", "load_profiles"),
        required_capabilities=("ingress_validation", "planning_projection"),
        planning_prior_set_ref=prior_set_ref,
        completion_criteria=completion_criteria,
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-a",
    )
    capsule_ref_changed = build_planning_capsule_ref(
        generation_mode="strategic_tailor",
        target_level="EXECUTIVE",
        task_plan=("validate_ingress", "load_profiles"),
        required_capabilities=("ingress_validation", "planning_projection"),
        planning_prior_set_ref=prior_set_ref,
        completion_criteria={**completion_criteria, "max_refinement_passes": 2},
        profile_manifest_digest="profile-a",
        planning_profile_digest="plan-a",
    )

    assert completion_criteria["schema_version"] == "apps_rg_completion_criteria_v1"
    assert completion_criteria["planning_mode"] == "bounded_refinement"
    assert completion_criteria["max_refinement_passes"] == 1
    assert completion_criteria["max_ambiguity_severity"] == "high"
    assert completion_criteria["ambiguity_policy"]["high"] == "stop_and_request_input"
    assert capsule_ref.startswith("l1plan-")
    assert capsule_ref != capsule_ref_changed
