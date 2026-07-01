"""Unit tests for canonical apps_rg section judge policy matrix."""

from __future__ import annotations

from pathlib import Path

import yaml

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

_SSOT = Path(__file__).resolve().parents[3] / "apps_rg" / "config" / "provider_profiles.yaml"


def _yaml_judge_model(tier: str, provider_key: str) -> str:
    data = yaml.safe_load(_SSOT.read_text(encoding="utf-8"))
    return str(data["judge_models"][tier][provider_key])


def _yaml_runtime_limit(path: str) -> str:
    data = yaml.safe_load(_SSOT.read_text(encoding="utf-8"))
    current = data["runtime_limits"]
    for part in path.split("."):
        current = current[part]
    return str(current)


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
    assert matrix["executive_summary"]["judge_runtime_profile"] == {
        "judge_weight": 3,
        "max_output_tokens": 8192,
        "max_output_tokens_hard_cap": 8192,
        "max_attempts": 3,
        "retry_backoff_base_seconds": 0.5,
        "retry_backoff_max_seconds": 4.0,
    }
    assert matrix["headline"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["headline"]["judge_runtime_profile"] == {
        "judge_weight": 2,
        "max_output_tokens": 4096,
        "max_output_tokens_hard_cap": 8192,
        "max_attempts": 2,
        "retry_backoff_base_seconds": 0.5,
        "retry_backoff_max_seconds": 1.0,
    }
    assert matrix["unify_bullets"]["judge_tier"] == JudgeTier.BULLET_REWRITE_QUALITY.value
    assert matrix["ibm_bullets"]["judge_tier"] == JudgeTier.BULLET_REWRITE_QUALITY.value
    assert matrix["insurtech_bullets"]["judge_tier"] == JudgeTier.BULLET_REWRITE_QUALITY.value
    assert matrix["ey_bullets"]["judge_tier"] == JudgeTier.BULLET_REWRITE_QUALITY.value
    assert matrix["unify_bullets"]["judge_runtime_profile"] == matrix["ibm_bullets"]["judge_runtime_profile"]
    assert matrix["unify_bullets"]["judge_runtime_profile"] == {
        "judge_weight": 2,
        "max_output_tokens": 4096,
        "max_output_tokens_hard_cap": 8192,
        "max_attempts": 2,
        "retry_backoff_base_seconds": 0.5,
        "retry_backoff_max_seconds": 1.0,
    }
    assert matrix["unify_narrative"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["ibm_narrative"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["insurtech_narrative"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["ey_narrative"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["unify_narrative"]["judge_runtime_profile"] == matrix["unify_bullets"]["judge_runtime_profile"]
    assert matrix["competencies"]["judge_runtime_profile"] == matrix["unify_bullets"]["judge_runtime_profile"]
    assert matrix["competencies"]["judge_required_for_proof"] is True
    assert matrix["competencies"]["judge_tier"] == JudgeTier.STANDARD_REASONING.value
    assert matrix["competencies"]["generator_model_class"] == "EXTERNAL_CLAUDE"
    assert matrix["competencies"]["required_judge_providers"] == ["openai_chatgpt"]
    assert matrix["final_aggregate_resume"]["judge_tier"] == JudgeTier.ENHANCED_REASONING.value
    assert matrix["final_aggregate_resume"]["judge_runtime_profile"] == matrix["executive_summary"]["judge_runtime_profile"]


def test_allow_non_allow_exit_zero_does_not_force_plumbing_when_product_passes() -> None:
    args = type(
        "Args",
        (),
        {
            "mock_judges": False,
            "provider": "retired_provider_profile",
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


def test_competencies_proof_bundle_blocks_when_required_judges_missing() -> None:
    args = type("Args", (), {"mock_judges": False, "provider": "external_claude"})()
    bundle = compute_lane_proof_bundle(
        args,
        section_id="competencies",
        runtime_generation_status="REAL_LLM",
        x1d_judges=[],
        x2_gates=[{"gate_id": "x2_ok", "pass": True}],
        x3=_FakeX3(),
    )
    assert bundle["judge_required_for_proof"] is True
    assert bundle["required_judge_rows_missing"] is True
    assert bundle["judge_proof_eligible"] is False
    assert bundle["proof_eligible"] is False


def test_competencies_proof_bundle_requires_proof_eligible_judge() -> None:
    args = type("Args", (), {"mock_judges": False, "provider": "external_claude"})()
    openai_judge = {
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS",
        "pass": True,
        "decisive_failure": False,
        "normalized_score": 0.9,
        "normalized_threshold": 0.8,
        "provider_key": "openai_chatgpt",
        "proof_eligible_judge": True,
        "advisory_only": False,
    }
    bundle = compute_lane_proof_bundle(
        args,
        section_id="competencies",
        runtime_generation_status="REAL_LLM",
        x1d_judges=[openai_judge],
        x2_gates=[{"gate_id": "x2_ok", "pass": True}],
        x3=_FakeX3(),
    )
    assert bundle["judge_required_for_proof"] is True
    assert bundle["required_judge_rows_missing"] is False
    assert bundle["judge_proof_eligible"] is True
    assert bundle["proof_eligible"] is True


def test_forbidden_models_fail_proof_resolution() -> None:
    assert is_forbidden_proof_judge_model("gemini-2.0-flash")
    assert is_forbidden_proof_judge_model("gpt-4o-mini")
    r = resolve_section_proof_judge_model(
        "headline",
        "gemini_pro",
        {"APPS_RG_GOOGLE_JUDGE_MODEL": "gemini-2.0-flash"},
    )
    assert r.model_actual == _yaml_judge_model("standard", "gemini_pro")
    assert r.model_source == "yaml_judge_models"


def test_anthropic_judge_tier_yaml_ssot_ignores_env() -> None:
    env = {
        "APPS_RG_ANTHROPIC_JUDGE_MODEL_ENHANCED": "claude-opus-4-6",
        "APPS_RG_ANTHROPIC_JUDGE_MODEL_STANDARD": "claude-sonnet-4-6",
        "ANTHROPIC_MODEL": "claude-haiku-4-5",
    }
    enhanced = resolve_section_proof_judge_model("executive_summary", "anthropic_claude", env)
    assert enhanced.model_actual == _yaml_judge_model("enhanced", "anthropic_claude")
    assert enhanced.model_source == "yaml_judge_models"
    standard = resolve_section_proof_judge_model("headline", "anthropic_claude", env)
    assert standard.model_actual == _yaml_judge_model("standard", "anthropic_claude")
    assert standard.model_source == "yaml_judge_models"


def test_openai_judge_tier_yaml_ssot_ignores_env() -> None:
    assert openai_chat_completions_eligible("gpt-5.5") is True
    assert openai_chat_completions_eligible("gpt-5.5-pro") is False
    env = {
        "APPS_RG_OPENAI_JUDGE_MODEL_ENHANCED": "gpt-5.5-pro",
        "APPS_RG_OPENAI_JUDGE_MODEL_STANDARD": "gpt-5.5",
        "OPENAI_MODEL": "gpt-5.1",
    }
    enhanced = resolve_section_proof_judge_model("executive_summary", "openai_chatgpt", env)
    assert enhanced.model_actual == _yaml_judge_model("enhanced", "openai_chatgpt")
    assert enhanced.model_source == "yaml_judge_models"
    assert enhanced.reasoning_effort == _yaml_runtime_limit("judge.openai_enhanced_reasoning_effort")
    standard = resolve_section_proof_judge_model("headline", "openai_chatgpt", env)
    assert standard.model_actual == _yaml_judge_model("standard", "openai_chatgpt")
    assert standard.model_source == "yaml_judge_models"
    assert standard.reasoning_effort is None


def test_google_judge_tier_yaml_ssot_ignores_env() -> None:
    env = {
        "APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED": "gemini-3.1-pro-preview",
        "APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD": "gemini-2.5-pro",
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-flash",
    }
    enhanced = resolve_section_proof_judge_model("executive_summary", "gemini_pro", env)
    assert enhanced.model_actual == _yaml_judge_model("enhanced", "gemini_pro")
    assert enhanced.model_source == "yaml_judge_models"
    standard = resolve_section_proof_judge_model("headline", "gemini_pro", env)
    assert standard.model_actual == _yaml_judge_model("standard", "gemini_pro")
    assert standard.model_source == "yaml_judge_models"
    bullet = resolve_section_proof_judge_model("ibm_bullets", "gemini_pro", env)
    assert bullet.model_actual == _yaml_judge_model("standard", "gemini_pro")
    assert bullet.model_source == "yaml_judge_models"


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


def test_competencies_x3_blocks_without_required_judges() -> None:
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
        judge_required_for_allow=True,
    )
    assert x3.x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"
    assert x3.proof_eligible_allow_requires == "every_configured_x1d_judge_model_backed_pass"


def test_competencies_policy_requires_llm_judge_for_proof() -> None:
    p = get_section_judge_policy("competencies")
    assert p.judge_required_for_proof is True
    assert p.required_judge_providers == ("openai_chatgpt",)
    assert "anthropic_claude" not in p.required_judge_providers
    openai = resolve_section_proof_judge_model("competencies", "openai_chatgpt", {})
    assert openai.model_actual == "gpt-5.5"
    assert openai.proof_eligible_judge is True
    rubric = ""
    from apps_rg.runtime.judges import competencies_x1d

    rubric = competencies_x1d.COMPETENCIES_RUBRIC
    assert "REQUIRED proof taxonomy grading" in rubric
    assert "gates product proof eligibility" in rubric.lower()
    assert "distinct ATS query clusters" in rubric
    assert "graph-backed differentiation" in rubric.lower()
