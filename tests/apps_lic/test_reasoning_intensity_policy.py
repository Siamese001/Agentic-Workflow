"""Reasoning-intensity policy tests for apps_lic."""

from __future__ import annotations

import json
from pathlib import Path

from apps_lic.engines.qa_report_engine import QaReportEngine
from apps_lic.engines.validation_engine import ValidationEngine
from apps_lic.policy.reasoning_intensity import (
    JUDGE_EVIDENCE_SUPPORT,
    JUDGE_LINKEDIN_TONE,
    JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    JUDGE_SAFETY_NO_FABRICATION,
    JUDGE_SCHEMA_POLICY_NO_SEND,
    R1_STANDARD,
    R2_DELIBERATE,
    R3_STRICT,
    SC_1,
    SC_2,
    SC_3,
    select_reasoning_policy,
)
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.runtime.u0.adapter import apps_lic_u0_adapt
from apps_lic.runtime.bindings.l1_binding import l1_plan_apps_lic


def test_default_policy_is_sc1_r1_with_x2_gates_and_x1d_judge() -> None:
    raw = build_cli_ingress_raw(
        manual_brief="Context for a concise LinkedIn introduction."
    )
    validated, _reflection = apps_lic_u0_adapt(raw)
    plan = l1_plan_apps_lic(validated)
    policy = plan.task_spec["reasoning_policy"]

    assert policy["sc_level"] == SC_1
    assert policy["reasoning_intensity"] == R1_STANDARD
    assert policy["judge_profile"] == "normal_default"
    assert policy["judges"] == [
        JUDGE_SCHEMA_POLICY_NO_SEND,
        JUDGE_LINKEDIN_TONE,
        JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    ]
    assert policy["x2_deterministic_gates"] == [
        JUDGE_SCHEMA_POLICY_NO_SEND,
        JUDGE_LINKEDIN_TONE,
    ]
    assert policy["x1d_llm_judges"] == [
        JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    ]
    assert policy["x1d_runs_after_x2"] is True
    assert policy["max_candidates"] == 1
    assert policy["validation_repair_passes"] == 1
    assert policy["fail_closed_on_empty_evidence"] is True
    assert policy["no_send_authority"] is True
    assert plan.candidate_generation_expected_hint is False


def test_named_company_policy_escalates_to_sc2_without_sensitive_strictness() -> None:
    raw = build_cli_ingress_raw(
        manual_brief="Recruiting context for an AI engineering search.",
        campaign_objective="Draft a concise note about AI engineering hiring.",
        lead_profile={
            "verified_name": "Nina K.",
            "title": "Strategic technical recruiter and Sourcer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
    )

    policy = select_reasoning_policy(raw)

    assert policy["sc_level"] == SC_2
    assert policy["reasoning_intensity"] == R2_DELIBERATE
    assert policy["max_candidates"] == 2
    assert "named_target_contact" in policy["escalation_triggers"]
    assert "named_company" in policy["escalation_triggers"]


def test_executive_or_high_stakes_policy_escalates_to_sc3() -> None:
    raw = build_cli_ingress_raw(
        manual_brief="AIG VP Global Head of Agentic AI Solutions briefing.",
        campaign_objective=(
            "Draft a concise LinkedIn message about AIG's VP Global Head of "
            "Agentic AI Solutions opportunity."
        ),
        lead_profile={
            "verified_name": "Scott Hallworth",
            "title": "Executive Vice President and Chief Digital Officer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
    )

    policy = select_reasoning_policy(raw)

    assert policy["sc_level"] == SC_3
    assert policy["reasoning_intensity"] == R3_STRICT
    assert policy["judge_profile"] == "high_risk_strict"
    assert policy["max_candidates"] == 3
    assert policy["judges"] == [
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE,
        JUDGE_SAFETY_NO_FABRICATION,
        JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    ]
    assert policy["x2_deterministic_gates"] == [
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE,
        JUDGE_SAFETY_NO_FABRICATION,
    ]
    assert policy["x1d_llm_judges"] == [
        JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    ]
    assert "executive_or_high_stakes" in policy["escalation_triggers"]


def test_weak_evidence_fails_closed_and_does_not_authorize_sc_compensation() -> None:
    report = ValidationEngine().execute(
        {
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
            "draft_message": {
                "message_text": (
                    "Hi Scott, AIG's Agentic AI role reads like an "
                    "operating-model rewrite across underwriting and claims. "
                    "I have built governed agent workflows with evals and "
                    "telemetry baked in. Worth a brief call?"
                ),
                "channel": "linkedin",
                "recipient_class": "executive",
                "unsupported_claims": [],
            },
            "evidence_bundle": {"count": 1, "support_status": "WEAK"},
        }
    )["validation_report"]

    assert report["passed"] is False
    assert "evidence_support_weak_fail_closed" in report["issues"]
    assert "sc_escalation_forbidden_on_weak_evidence" in report["issues"]


def test_qa_default_and_strict_profiles_use_x2_x1d_hybrid_counts(monkeypatch) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_X1D_JUDGE_STUB", "1")
    draft = {
        "message_text": (
            "Hi Scott, AIG's Agentic AI role reads like an operating-model "
            "rewrite across underwriting and claims. I have built governed "
            "agent workflows with evals and telemetry baked in. Worth a brief call?"
        ),
        "channel": "linkedin",
        "recipient_class": "executive",
        "unsupported_claims": [],
        "candidate_count": 1,
        "generation_temperature": 0.82,
        "top_p": 0.92,
        "attempts": 1,
        "max_generation_attempts": 1,
    }

    default_qa = QaReportEngine().execute(
        {
            "draft_message": draft,
            "validation_report": {"passed": True, "issues": []},
            "evidence_bundle": {"count": 4, "support_status": "PASS"},
        }
    )["qa_report"]
    assert default_qa["sc_level"] == SC_1
    assert default_qa["reasoning_intensity"] == R1_STANDARD
    assert default_qa["judge_count"] == 3
    assert default_qa["active_judges"] == [
        JUDGE_SCHEMA_POLICY_NO_SEND,
        JUDGE_LINKEDIN_TONE,
        JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    ]
    assert default_qa["x2_deterministic_gate_count"] == 2
    assert default_qa["x1d_llm_judge_count"] == 1
    assert default_qa["x2_gates_passed"] is True

    strict_policy = {
        **default_qa["reasoning_policy"],
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
    }
    strict_qa = QaReportEngine().execute(
        {
            "reasoning_policy": strict_policy,
            "draft_message": {**draft, "candidate_count": 3},
            "validation_report": {"passed": True, "issues": []},
            "evidence_bundle": {"count": 4, "support_status": "PASS"},
        }
    )["qa_report"]
    assert strict_qa["sc_level"] == SC_3
    assert strict_qa["reasoning_intensity"] == R3_STRICT
    assert strict_qa["judge_count"] == 4
    assert strict_qa["x2_deterministic_gate_count"] == 3
    assert strict_qa["x1d_llm_judge_count"] == 1
    assert strict_qa["quality_contract"]["self_consistency_samples"] == 3
    assert strict_qa["quality_contract"]["x1_x2_x3_exit_retries"] == 0
    assert (
        strict_qa["x1d_llm_judge_outputs"][
            JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D
        ]["provider_status"]
        == "TEST_STUB_PASS"
    )


def test_x1d_judge_skips_when_x2_gates_fail() -> None:
    qa = QaReportEngine().execute(
        {
            "draft_message": {
                "message_text": "Hi Scott, potential synergies?",
                "channel": "linkedin",
                "recipient_class": "executive",
                "unsupported_claims": [],
                "candidate_count": 1,
            },
            "validation_report": {
                "passed": False,
                "issues": ["antipattern:GENERIC_SYNERGY_ASK"],
            },
            "evidence_bundle": {"count": 4, "support_status": "PASS"},
        }
    )["qa_report"]

    assert qa["x2_gates_passed"] is False
    assert (
        qa["x1d_llm_judge_outputs"][
            JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D
        ]["provider_status"]
        == "SKIPPED_X2_FAILED"
    )


def test_x1d_judge_cannot_compensate_for_weak_c0_evidence() -> None:
    qa = QaReportEngine().execute(
        {
            "draft_message": {
                "message_text": (
                    "Hi Scott, AIG's Agentic AI role reads like an "
                    "operating-model rewrite across underwriting and claims. "
                    "I have built governed agent workflows with evals and "
                    "telemetry baked in. Worth a brief call?"
                ),
                "channel": "linkedin",
                "recipient_class": "executive",
                "unsupported_claims": [],
                "candidate_count": 1,
            },
            "validation_report": {"passed": True, "issues": []},
            "evidence_bundle": {"count": 1, "support_status": "WEAK"},
        }
    )["qa_report"]

    assert qa["x2_gates_passed"] is True
    assert (
        qa["x1d_llm_judge_outputs"][
            JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D
        ]["provider_status"]
        == "SKIPPED_C0_EVIDENCE_WEAK"
    )


def test_default_reasoning_policy_e2e_manifest(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    monkeypatch.setenv("APPS_LIC_TEST_X1D_JUDGE_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Context for a concise LinkedIn introduction."
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "default_r1")

    manifest = json.loads((result.artifact_dir / "spine_run_manifest.json").read_text())
    l2 = json.loads((result.artifact_dir / "l2_execution_receipt.json").read_text())
    draft = json.loads(l2["payload"]["generated_content"])

    assert result.terminal_r5 is False
    assert manifest["sc_level"] == SC_1
    assert manifest["reasoning_intensity"] == R1_STANDARD
    assert manifest["judge_count"] == 3
    assert manifest["x2_deterministic_gate_count"] == 2
    assert manifest["x1d_llm_judge_count"] == 1
    assert manifest["max_candidates"] == 1
    assert manifest["evidence_support_status"] == "PASS"
    assert draft["sc_level"] == SC_1
    assert draft["reasoning_intensity"] == R1_STANDARD
    assert draft["candidate_count"] == 1


def test_strict_reasoning_policy_e2e_manifest_for_executive(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    monkeypatch.setenv("APPS_LIC_TEST_X1D_JUDGE_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="AIG VP Global Head of Agentic AI Solutions briefing.",
        campaign_objective=(
            "Draft a concise LinkedIn message about AIG's VP Global Head of "
            "Agentic AI Solutions opportunity."
        ),
        lead_profile={
            "verified_name": "Scott Hallworth",
            "title": "Executive Vice President and Chief Digital Officer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "strict_r3")

    manifest = json.loads((result.artifact_dir / "spine_run_manifest.json").read_text())
    l2 = json.loads((result.artifact_dir / "l2_execution_receipt.json").read_text())
    draft = json.loads(l2["payload"]["generated_content"])

    assert result.terminal_r5 is False
    assert manifest["sc_level"] == SC_3
    assert manifest["reasoning_intensity"] == R3_STRICT
    assert manifest["judge_count"] == 4
    assert manifest["x2_deterministic_gate_count"] == 3
    assert manifest["x1d_llm_judge_count"] == 1
    assert manifest["max_candidates"] == 3
    assert manifest["evidence_support_status"] == "PASS"
    assert draft["sc_level"] == SC_3
    assert draft["reasoning_intensity"] == R3_STRICT
    assert draft["candidate_count"] == 3
