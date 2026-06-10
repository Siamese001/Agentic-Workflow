"""AIG public-profile target category E2E tests for apps_lic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_lic.engines.qa_report_engine import QaReportEngine
from apps_lic.engines.profile_analysis_engine import classify_recipient_profile
from apps_lic.engines.validation_engine import ValidationEngine
from apps_lic.policy.reasoning_intensity import (
    JUDGE_EVIDENCE_SUPPORT,
    JUDGE_LINKEDIN_TONE,
    JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    JUDGE_SAFETY_NO_FABRICATION,
    R3_STRICT,
    SC_3,
)
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import ready_governed_opportunity_facts


AIG_BRIEFING = Path("apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md")

AIG_CONTACTS = [
    {
        "case_id": "scott_hallworth_exec",
        "expected_category": "EXECUTIVE",
        "expected_c0_category": "C_LEVEL",
        "expected_phrase": "operating-model rewrite",
        "source_url": "https://www.linkedin.com/posts/aig_we-are-pleased-to-welcome-scott-hallworth-activity-7369388053229903872-OtUM",
        "lead_profile": {
            "verified_name": "Scott Hallworth",
            "title": "Executive Vice President and Chief Digital Officer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
    },
    {
        "case_id": "daisuke_hayashi_senior_ta",
        "expected_category": "SENIOR_TA",
        "expected_phrase": "not slideware",
        "source_url": "https://jp.linkedin.com/in/daisuke-hayashi-5a308353",
        "lead_profile": {
            "verified_name": "Daisuke Hayashi",
            "title": "Head of Talent Acquisition | Inclusion",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
    },
    {
        "case_id": "nina_k_recruiter",
        "expected_category": "RECRUITER",
        "expected_phrase": "production ai",
        "source_url": "https://www.linkedin.com/in/nkshatri",
        "lead_profile": {
            "verified_name": "Nina K.",
            "title": "Strategic technical recruiter and Sourcer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
    },
]


@pytest.mark.parametrize("contact", AIG_CONTACTS, ids=lambda c: c["case_id"])
def test_public_aig_contact_profile_classification(contact: dict[str, object]) -> None:
    assert (
        classify_recipient_profile(contact["lead_profile"])
        == contact["expected_category"]
    )


@pytest.mark.parametrize("contact", AIG_CONTACTS, ids=lambda c: c["case_id"])
def test_aig_public_profile_e2e_generates_target_category_draft(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    contact: dict[str, object],
    ) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    monkeypatch.setenv("APPS_LIC_TEST_X1D_JUDGE_STUB", "1")
    briefing = AIG_BRIEFING.read_text(encoding="utf-8")
    expected_hint_category = str(contact["expected_category"])
    expected_c0_category = str(
        contact.get("expected_c0_category", expected_hint_category)
    )
    lead_profile = dict(contact["lead_profile"])

    raw = build_cli_ingress_raw(
        run_id=f"run_aig_{contact['case_id']}",
        request_id=f"req_aig_{contact['case_id']}",
        recipient_class=expected_hint_category,
        channel="linkedin",
        outreach_mode="cold",
        manual_brief=briefing,
        lead_profile=lead_profile,
        campaign_objective=(
            "Draft a concise LinkedIn message about AIG's VP Global Head of "
            "Agentic AI Solutions opportunity."
        ),
        audience_segment=expected_hint_category.lower(),
        governed_opportunity_facts=ready_governed_opportunity_facts(
            contact_text=(
                f"{lead_profile['verified_name']} | "
                f"{lead_profile['title']} | AIG"
            ),
            role_ownership_text=(
                f"{lead_profile['title']} current AIG target-owner signal."
            ),
        ),
    )

    result = run_canonical_apps_lic_spine(
        raw,
        artifact_root=tmp_path / str(contact["case_id"]),
    )

    assert result.terminal_r5 is False
    assert result.l2_execution_status in {"completed", "completed_with_gate_halt"}

    manifest = json.loads((result.artifact_dir / "spine_run_manifest.json").read_text())
    assert manifest["no_send_assertion"] is True
    assert manifest["no_l4_write_assertion"] is True
    assert manifest["apps_research_invoked"] is False
    assert manifest["derived_recipient_class"] == expected_c0_category

    l2 = json.loads((result.artifact_dir / "l2_execution_receipt.json").read_text())
    draft = json.loads(l2["payload"]["generated_content"])
    message = draft["message_text"]

    assert draft["recipient_category"] == expected_c0_category
    assert draft["recipient_class"] == expected_c0_category.lower()
    assert draft["target_contact_name"] == lead_profile["verified_name"]
    assert draft["target_contact_title"] == lead_profile["title"]
    assert message.startswith(f"Hi {lead_profile['verified_name'].split()[0]},")
    assert str(contact["expected_phrase"]) in message.lower()
    assert draft["generation_temperature"] >= 0.8
    assert draft["top_p"] >= 0.9
    assert draft["attempts"] == 1
    assert draft["max_generation_attempts"] >= draft["attempts"]
    assert draft["max_candidates"] >= 1
    assert draft["candidate_count"] == draft["max_candidates"]
    assert "potential synergies" not in message.lower()
    assert "i noticed your role" not in message.lower()
    assert "i believe my background aligns" not in message.lower()
    assert len(message) <= 600
    assert "—" not in message


def test_validation_blocks_generic_bs_message() -> None:
    generic_draft = {
        "message_text": (
            "Dear Scott, I noticed your role at AIG. I believe my background "
            "aligns well and could contribute significantly. Could we discuss "
            "potential synergies?"
        ),
        "body": "",
        "channel": "linkedin",
        "recipient_class": "executive",
        "unsupported_claims": [],
    }

    report = ValidationEngine().execute({
        "draft_message": generic_draft,
        "evidence_bundle": {"count": 4},
    })["validation_report"]

    assert report["passed"] is False
    assert "antipattern:GENERIC_ROLE_OPENER" in report["issues"]
    assert "antipattern:GENERIC_ALIGNMENT_CLAIM" in report["issues"]
    assert "antipattern:GENERIC_SYNERGY_ASK" in report["issues"]


def test_qa_report_exposes_x2_x1d_judges_and_one_shot_quality_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_X1D_JUDGE_STUB", "1")
    draft = {
        "message_text": (
            "Hi Scott, AIG's Agentic AI role reads like an operating-model "
            "rewrite across underwriting and claims. I have built governed "
            "agent workflows with evals and telemetry baked in. Worth a brief "
            "call on proof I could bring to the rollout?"
        ),
        "body": "",
        "recipient_category": "EXECUTIVE",
        "recipient_class": "executive",
        "generation_temperature": 0.82,
        "top_p": 0.92,
        "attempts": 1,
        "max_generation_attempts": 1,
        "candidate_count": 3,
        "generator": "test_provider_stub",
        "reasoning_policy": {
            "sc_level": SC_3,
            "reasoning_intensity": R3_STRICT,
            "judge_profile": "high_risk_strict",
            "judges": [
                JUDGE_EVIDENCE_SUPPORT,
                JUDGE_LINKEDIN_TONE,
                JUDGE_SAFETY_NO_FABRICATION,
                JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
            ],
            "x2_deterministic_gates": [
                JUDGE_EVIDENCE_SUPPORT,
                JUDGE_LINKEDIN_TONE,
                JUDGE_SAFETY_NO_FABRICATION,
            ],
            "x1d_llm_judges": [
                JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
            ],
            "max_candidates": 3,
            "validation_repair_passes": 1,
            "fail_closed_on_empty_evidence": True,
            "no_send_authority": True,
        },
    }

    qa = QaReportEngine().execute({
        "draft_message": draft,
        "validation_report": {"passed": True, "issues": []},
        "evidence_bundle": {"count": 4, "support_status": "PASS"},
    })["qa_report"]

    assert qa["composite_score"] >= 0.8
    assert qa["judge_count"] == 4
    assert qa["active_judges"] == [
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE,
        JUDGE_SAFETY_NO_FABRICATION,
        JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    ]
    assert qa["judge_scores"][JUDGE_EVIDENCE_SUPPORT] >= 0.5
    assert qa["judge_scores"][JUDGE_LINKEDIN_TONE] >= 0.5
    assert qa["judge_scores"][JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D] >= 0.8
    assert qa["x2_deterministic_gate_count"] == 3
    assert qa["x1d_llm_judge_count"] == 1
    assert qa["x2_gates_passed"] is True
    assert (
        qa["x1d_llm_judge_outputs"][
            JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D
        ]["provider_status"]
        == "TEST_STUB_PASS"
    )
    assert qa["quality_contract"] == {
        "generation_temperature": 0.82,
        "top_p": 0.92,
        "self_consistency_samples": 3,
        "sc_level": SC_3,
        "reasoning_intensity": R3_STRICT,
        "judge_profile": "high_risk_strict",
        "active_judges": [
            JUDGE_EVIDENCE_SUPPORT,
            JUDGE_LINKEDIN_TONE,
            JUDGE_SAFETY_NO_FABRICATION,
            JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
        ],
        "judge_count": 4,
        "x2_deterministic_gates": [
            JUDGE_EVIDENCE_SUPPORT,
            JUDGE_LINKEDIN_TONE,
            JUDGE_SAFETY_NO_FABRICATION,
        ],
        "x2_deterministic_gate_count": 3,
        "x2_gates_passed": True,
        "x1d_llm_judges": [
            JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
        ],
        "x1d_llm_judge_count": 1,
        "x1d_runs_after_x2": True,
        "x1d_max_attempts": 1,
        "x1d_failure_policy": "quality_block_not_exit_override",
        "x1d_model_backed_pass": False,
        "max_candidates": 3,
        "candidate_count": 3,
        "validation_repair_passes": 1,
        "generation_attempts": 1,
        "max_generation_attempts": 1,
        "x1_x2_x3_exit_retries": 0,
        "retry_policy": "one_exit_decision_no_x_retry",
        "fail_closed_on_empty_evidence": True,
        "no_send_authority": True,
    }
