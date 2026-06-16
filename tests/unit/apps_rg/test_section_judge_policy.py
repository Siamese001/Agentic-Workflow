"""Unit tests for canonical apps_rg section judge policy matrix."""

from __future__ import annotations

import pytest

from apps_rg.runtime.judges.grade_only_judge_packet import build_grade_only_judge_packet
from apps_rg.runtime.judges.section_judge_profile import (
    is_forbidden_proof_judge_model,
    openai_chat_completions_eligible,
    resolve_section_proof_judge_model,
)
from apps_rg.runtime.section_judge_policy import (
    JudgeTier,
    get_section_judge_policy,
    policy_matrix_export,
)
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import compute_lane_proof_bundle


class _FakeX3:
    x3_code = "X3_ALLOW"

    @property
    def pass_(self) -> bool:
        return True

    authorization_scope = "PRODUCT_QUALITY"


def test_section_judge_policy_matrix() -> None:
    matrix = policy_matrix_export()
    assert matrix["executive_summary"]["judge_required_for_proof"] is True
    assert matrix["executive_summary"]["judge_tier"] == JudgeTier.ENHANCED_REASONING.value
    assert matrix["headline"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["unify_bullets"]["judge_tier"] == JudgeTier.BULLET_REWRITE_QUALITY.value
    assert matrix["ibm_bullets"]["judge_tier"] == JudgeTier.BULLET_REWRITE_QUALITY.value
    assert matrix["insurtech_bullets"]["judge_tier"] == JudgeTier.BULLET_REWRITE_QUALITY.value
    assert matrix["ey_bullets"]["judge_tier"] == JudgeTier.BULLET_REWRITE_QUALITY.value
    assert matrix["unify_narrative"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["ibm_narrative"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["insurtech_narrative"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["ey_narrative"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["competencies"]["judge_required_for_proof"] is False
    assert matrix["competencies"]["judge_tier"] == JudgeTier.OPTIONAL_ADVISORY_TAXONOMY_ONLY.value
    assert matrix["final_aggregate_resume"]["judge_tier"] == JudgeTier.ENHANCED_REASONING.value


def test_allow_non_allow_exit_zero_does_not_force_plumbing_when_product_passes() -> None:
    args = type(
        "Args",
        (),
        {
            "mock_judges": False,
            "provider": "qwen_vllm",
            "allow_non_allow_exit_zero": True,
            "allow_test_mock_judges": False,
            "allow_test_mock_provider": False,
        },
    )()
    judge = {
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS",
        "pass": True,
        "decisive_failure": False,
        "normalized_score": 0.9,
        "normalized_threshold": 0.8,
        "provider_key": "openai_chatgpt",
        "proof_eligible_judge": True,
    }
    bundle = compute_lane_proof_bundle(
        args,
        section_id="executive_summary",
        runtime_generation_status="REAL_LLM",
        x1d_judges=[judge, judge, judge],
        x2_gates=[{"gate_id": "x2_ok", "pass": True}],
        x3=_FakeX3(),
    )
    assert bundle["proof_eligible"] is True
    assert bundle["allow_non_allow_exit_zero_cli"] is True


def test_competencies_proof_bundle_does_not_require_judges() -> None:
    args = type("Args", (), {"mock_judges": False, "provider": "qwen_vllm"})()
    bundle = compute_lane_proof_bundle(
        args,
        section_id="competencies",
        runtime_generation_status="REAL_LLM",
        x1d_judges=[],
        x2_gates=[{"gate_id": "x2_ok", "pass": True}],
        x3=_FakeX3(),
    )
    assert bundle["judge_required_for_proof"] is False
    assert bundle["judge_proof_eligible"] is False
    assert bundle["proof_eligible"] is True


def test_forbidden_models_fail_proof_resolution() -> None:
    assert is_forbidden_proof_judge_model("gemini-2.0-flash")
    assert is_forbidden_proof_judge_model("gpt-4o-mini")
    r = resolve_section_proof_judge_model(
        "headline",
        "gemini_pro",
        {"APPS_RG_GOOGLE_JUDGE_MODEL": "gemini-2.0-flash"},
    )
    assert r.blocked or r.model_actual != "gemini-2.0-flash"


def test_anthropic_judge_tier_specific_env() -> None:
    env = {
        "APPS_RG_ANTHROPIC_JUDGE_MODEL_ENHANCED": "claude-opus-4-6",
        "APPS_RG_ANTHROPIC_JUDGE_MODEL_STANDARD": "claude-sonnet-4-6",
        "ANTHROPIC_MODEL": "claude-haiku-4-5",
    }
    enhanced = resolve_section_proof_judge_model("executive_summary", "anthropic_claude", env)
    assert enhanced.model_actual == "claude-opus-4-6"
    standard = resolve_section_proof_judge_model("headline", "anthropic_claude", env)
    assert standard.model_actual == "claude-sonnet-4-6"


def test_openai_judge_tier_specific_env() -> None:
    assert openai_chat_completions_eligible("gpt-5.5") is True
    assert openai_chat_completions_eligible("gpt-5.5-pro") is False
    env = {
        "APPS_RG_OPENAI_JUDGE_MODEL_ENHANCED": "gpt-5.5-pro",
        "APPS_RG_OPENAI_JUDGE_MODEL_STANDARD": "gpt-5.5",
        "OPENAI_MODEL": "gpt-5.1",
    }
    enhanced = resolve_section_proof_judge_model("executive_summary", "openai_chatgpt", env)
    assert enhanced.model_actual == "gpt-5.5"
    # The env pin gpt-5.5-pro is chat-ineligible, so the resolver uses the
    # provider_profiles.yaml judge_models SSOT.
    assert enhanced.model_source == "yaml_judge_models"
    assert enhanced.reasoning_effort == "high"
    standard = resolve_section_proof_judge_model("headline", "openai_chatgpt", env)
    assert standard.model_actual == "gpt-5.5"
    assert standard.reasoning_effort is None


def test_google_judge_tier_specific_env() -> None:
    env = {
        "APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED": "gemini-3.1-pro-preview",
        "APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD": "gemini-2.5-pro",
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-flash",
    }
    enhanced = resolve_section_proof_judge_model("executive_summary", "gemini_pro", env)
    assert enhanced.model_actual == "gemini-3.1-pro-preview"
    assert enhanced.model_source == "APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED"
    standard = resolve_section_proof_judge_model("headline", "gemini_pro", env)
    assert standard.model_actual == "gemini-2.5-pro"
    assert standard.model_source == "APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD"
    bullet = resolve_section_proof_judge_model("ibm_bullets", "gemini_pro", env)
    assert bullet.model_actual == "gemini-2.5-pro"


def test_grade_only_judge_packet_shape() -> None:
    packet = build_grade_only_judge_packet(
        section_id="headline",
        candidate_output={"headline_line": "SVP Engineering | a | b | c"},
        section_rubric="rubric",
        rubric_ref="test",
        targeting_context={"jd_text": "jd", "briefing": "b"},
    )
    assert packet["judge_task"] == "GRADE_ONLY"
    assert packet["proof_boundary"]["judges_must_not_rewrite"] is True
    assert packet["targeting_context"]["jd_text"] == "jd"
    assert packet["grading_only_instructions"]
    assert "Do NOT write replacement" in packet["grading_only_instructions"]


def test_competencies_x3_allow_without_required_judges() -> None:
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    usage_ledger = {
        "schema": "section_input_usage_ledger_v1",
        "evidence_boundary": {
            "non_evidence_inputs_used_as_claim_evidence": False,
            "non_evidence_inputs_in_source_fact_ids": False,
        },
        "claim_support_summary": {
            "claims_with_targeting_input_in_source_fact_ids": 0,
            "claims_with_context_input_in_source_fact_ids": 0,
        },
    }
    x3 = aggregate_x3(
        resume_display_text="cat1: term",
        claim_ledger=[],
        x2_gates=[{"gate_id": "x2_ok", "pass": True}],
        x1d_judges=[],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=usage_ledger,
        judge_required_for_allow=False,
    )
    assert x3.x3_code == "X3_ALLOW"
    assert x3.proof_eligible_allow_requires == "x2_pass_only_x1d_advisory_optional"


def test_competencies_policy_does_not_require_llm_for_proof() -> None:
    p = get_section_judge_policy("competencies")
    assert p.judge_required_for_proof is False
    rubric = ""
    from apps_rg.runtime.judges import competencies_x1d

    rubric = competencies_x1d.COMPETENCIES_RUBRIC
    assert "OPTIONAL ADVISORY" in rubric
    assert "does not gate product proof" in rubric.lower()
