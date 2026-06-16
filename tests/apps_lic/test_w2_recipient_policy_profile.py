from __future__ import annotations

from pathlib import Path

from apps_lic.engines.recipient_classification import CLASS_HIRING_MANAGER
from apps_lic.engines.validation_exit import JUDGE_EVIDENCE_SUPPORT
from apps_lic.types.recipient_archetype_mapping import ARCHETYPE_EXECUTIVE
from apps_lic.types.recipient_policy_profile import (
    SCORE_PROFILE_X1D_MIN_REQUIRED,
    SCORE_PROFILE_X2_ONLY,
    build_recipient_policy_profile,
)
from scripts.apps_lic.run_post_w7_live_12_archetype_matrix import (
    THRESHOLD_PROFILE_ID,
    _matrix_violations,
    _write_report,
)


def test_w2_recipient_policy_profile_explains_slot_class_archetype_split() -> None:
    profile = build_recipient_policy_profile(
        requested_slot="Executive",
        actual_linkedin_title="VP of Product Management",
        derived_recipient_class=CLASS_HIRING_MANAGER,
        expected_prompt_archetype=ARCHETYPE_EXECUTIVE,
        message_type="trigger_based_insight",
        required_route_family="INMAIL",
        required_x1d_judge_profile_ids=[],
    )

    packet = profile.to_packet()

    assert packet["policy_profile_id"] == (
        "apps_lic.recipient_policy.executive.hiring_manager.executive."
        "trigger_based_insight.inmail.v1"
    )
    assert packet["requested_slot"] == "Executive"
    assert packet["actual_linkedin_title"] == "VP of Product Management"
    assert packet["derived_lic_recipient_class"] == CLASS_HIRING_MANAGER
    assert packet["mapped_prompt_archetype"] == ARCHETYPE_EXECUTIVE
    assert packet["minimum_score_profile_id"] == SCORE_PROFILE_X2_ONLY
    assert "requested_slot_differs_from_derived_class:EXECUTIVE!=HIRING_MANAGER" in packet["reason_codes"]
    assert "requested_slot_maps_to_prompt_archetype:EXECUTIVE->EXECUTIVE" in packet["reason_codes"]
    assert "executive_archetype_has_no_required_x1d_current_policy" in packet["reason_codes"]


def test_w2_recipient_policy_profile_records_required_x1d_thresholds() -> None:
    profile = build_recipient_policy_profile(
        requested_slot="Recruiter",
        actual_linkedin_title="Senior Technical Recruiter",
        derived_recipient_class="RECRUITER",
        expected_prompt_archetype="RECRUITER",
        message_type="role_specific",
        required_route_family="INMAIL",
        required_x1d_judge_profile_ids=[JUDGE_EVIDENCE_SUPPORT],
        x1d_thresholds_by_judge_id={JUDGE_EVIDENCE_SUPPORT: 0.86},
    )

    packet = profile.to_packet()

    assert packet["minimum_score_profile_id"] == SCORE_PROFILE_X1D_MIN_REQUIRED
    assert packet["minimum_x1d_threshold"] == 0.86
    assert packet["x1d_thresholds_by_judge_id"] == {JUDGE_EVIDENCE_SUPPORT: 0.86}
    assert "required_x1d_profiles_present" in packet["reason_codes"]


def test_w2_matrix_acceptance_does_not_fail_slot_class_split_when_profile_explains_it() -> None:
    profile = build_recipient_policy_profile(
        requested_slot="Executive",
        actual_linkedin_title="VP of Product Management",
        derived_recipient_class=CLASS_HIRING_MANAGER,
        expected_prompt_archetype=ARCHETYPE_EXECUTIVE,
        message_type="trigger_based_insight",
        required_route_family="INMAIL",
        required_x1d_judge_profile_ids=[],
    )
    row = {
        "profile_id": "fixture_exec_hiring_manager",
        "company": "Neo4j",
        "requested_slot": "Executive",
        "expected_mapped_archetype": ARCHETYPE_EXECUTIVE,
        "mapped_recipient_archetype": ARCHETYPE_EXECUTIVE,
        "expected_recipient_class": CLASS_HIRING_MANAGER,
        "derived_recipient_class": CLASS_HIRING_MANAGER,
        "outcome_authorized": True,
        "message_route": "INMAIL",
        "message_channel": "linkedin_inmail",
        "subject_line": "VP of Product Management, Agentic AI fit at Neo4j",
        "body_chars": 600,
        "proof_bundle_status": "PASS",
        "canonical_producer": "apps_lic.runtime.dispatch.canonical_dispatch",
        "no_send_assertion": True,
        "no_l4_write_assertion": True,
        "no_connector_post_assertion": True,
        "c0_recipient_class_status": "RECIPIENT_CLASS_DERIVED",
        "generation_generator": "claude_opus_4_8_primary",
        "generation_qa_notes": [],
        "draft_text": "Hi Firat, test draft.\n\nAmit",
        "proof_packet_id": "proof:test",
        "selected_candidate_id": "candidate:test",
        "x2_result": "X2_VALIDATION_PASS",
        "x1d_result": "X1D_NOT_REQUIRED",
        **profile.to_row_fields(),
    }

    violations = _matrix_violations((row,))

    assert not any(item.get("reason") == "expected_lic_class_not_matched" for item in violations)
    assert "requested_slot_differs_from_derived_class:EXECUTIVE!=HIRING_MANAGER" in row[
        "recipient_policy_reason_codes"
    ]


def test_w2_full_message_report_renders_policy_profile(tmp_path: Path) -> None:
    profile = build_recipient_policy_profile(
        requested_slot="Executive",
        actual_linkedin_title="VP of Product Management",
        derived_recipient_class=CLASS_HIRING_MANAGER,
        expected_prompt_archetype=ARCHETYPE_EXECUTIVE,
        message_type="trigger_based_insight",
        required_route_family="INMAIL",
        required_x1d_judge_profile_ids=[],
    )
    row = {
        "company": "Neo4j",
        "requested_slot": "Executive",
        "contact_name": "Firat T.",
        "contact_title": "VP of Product Management",
        "derived_recipient_class": CLASS_HIRING_MANAGER,
        "mapped_recipient_archetype": ARCHETYPE_EXECUTIVE,
        "message_type": "trigger_based_insight",
        "message_route": "INMAIL",
        "message_channel": "linkedin_inmail",
        "subject_line": "Agentic AI platform note",
        "subject_chars": 24,
        "body_chars": 42,
        "gate_score_10": 10.0,
        "apps_lic_disposition": "CLEAR_DRAFT",
        "source": "https://www.linkedin.com/in/firat",
        "draft_text": "Hi Firat,\n\nTest message.\n\nAmit",
        "gate_score_basis": "x2_applicable_gate_pass_ratio",
        "score_type": "X2 pass ratio",
        "gate_threshold_10": None,
        "x1d_policy_clearance": "x1d_not_required_not_acceptable_by_policy",
        "threshold_profile_id": THRESHOLD_PROFILE_ID,
        "policy_profile_id": profile.policy_profile_id,
        "x2_failed_gate_ids": [],
        "x1d_judge_scores_10": [],
        **profile.to_row_fields(),
    }
    summary = {
        "run_id": "test",
        "acceptance_passed": True,
        "profile_count": 1,
        "quality_violation_count": 0,
    }

    _write_report(tmp_path, summary, (row,))

    report = (tmp_path / "full_messages.md").read_text(encoding="utf-8")
    assert "Policy Profile" in report
    assert profile.policy_profile_id in report
    assert "requested_slot_differs_from_derived_class" in report


def test_w8_full_message_report_makes_score_type_and_judge_thresholds_visible(tmp_path: Path) -> None:
    profile = build_recipient_policy_profile(
        requested_slot="Recruiter",
        actual_linkedin_title="Senior Technical Recruiter",
        derived_recipient_class="RECRUITER",
        expected_prompt_archetype="RECRUITER",
        message_type="role_specific",
        required_route_family="INMAIL",
        required_x1d_judge_profile_ids=[JUDGE_EVIDENCE_SUPPORT],
        x1d_thresholds_by_judge_id={JUDGE_EVIDENCE_SUPPORT: 0.86},
    )
    row = {
        "company": "AIG",
        "requested_slot": "Recruiter",
        "contact_name": "Nina K.",
        "contact_title": "Senior Technical Recruiter",
        "derived_recipient_class": "RECRUITER",
        "mapped_recipient_archetype": "RECRUITER",
        "message_type": "role_specific",
        "message_route": "INMAIL",
        "message_channel": "linkedin_inmail",
        "subject_line": "AI platform role fit",
        "subject_chars": 20,
        "body_chars": 64,
        "gate_score_10": 9.1,
        "gate_threshold_10": 8.6,
        "apps_lic_disposition": "CLEAR_DRAFT",
        "source": "https://www.linkedin.com/in/nina",
        "draft_text": "Hi Nina,\n\nTest message.\n\nAmit",
        "gate_score_basis": "min_required_live_x1d_judge",
        "score_type": "Live X1D min score",
        "x2_failed_gate_ids": [],
        "x1d_policy_clearance": "required_live_x1d_judge_evidence_present",
        "threshold_profile_id": THRESHOLD_PROFILE_ID,
        "policy_profile_id": profile.policy_profile_id,
        "x1d_judge_scores_10": [
            {
                "judge_id": JUDGE_EVIDENCE_SUPPORT,
                "score_10": 9.1,
                "threshold_10": 8.6,
                "passed": True,
                "issues": [],
                "required_repairs": [],
            }
        ],
        **profile.to_row_fields(),
    }
    summary = {
        "run_id": "test",
        "acceptance_passed": True,
        "profile_count": 1,
        "quality_violation_count": 0,
    }

    _write_report(tmp_path, summary, (row,))

    report = (tmp_path / "full_messages.md").read_text(encoding="utf-8")
    assert "Score Type" in report
    assert "Live X1D min score" in report
    assert THRESHOLD_PROFILE_ID in report
    assert "| Judge | Score/10 | Threshold/10 | Passed |" in report
    assert f"| {JUDGE_EVIDENCE_SUPPORT} | 9.1 | 8.6 | True |" in report
