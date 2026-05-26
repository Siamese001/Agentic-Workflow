"""Frozen L2 + judge fixtures for executive_summary acceptance scenarios."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.sections.executive_summary_lane_done_policy import (
    _X3_ALLOW,
    _X3_SOFT_FAIL,
    x3_disposition_for_judges,
)

_FROZEN_RESUME_TEXT = (
    "Technology strategy executive builds governed agentic AI platforms for regulated enterprise delivery. "
    "The leader scales deterministic routing, orchestration, and policy-gated execution across global programs. "
    "Platform lifecycle work ties enterprise architecture decisions to commercial adoption and operating discipline. "
    "Prior delivery outcomes show measurable platform modernization grounded in selected executive facts. "
    "Cross-functional leadership aligns innovation portfolios with governance and risk management expectations. "
    "Selected facts support a cohesive SVP narrative without naming the target company in resume prose."
)

_FROZEN_CLAIM_LEDGER: list[dict[str, Any]] = [
    {
        "claim_text": "governed agentic AI platforms",
        "source_fact_ids": ["bul_unify_001"],
    },
    {
        "claim_text": "enterprise architecture and commercial adoption",
        "source_fact_ids": ["bul_unify_002"],
    },
]


def frozen_l2_output(*, runtime_generation_status: str = "REAL_LLM") -> dict[str, Any]:
    return {
        "runtime_generation_status": runtime_generation_status,
        "resume_display_text": _FROZEN_RESUME_TEXT,
        "claim_ledger": list(_FROZEN_CLAIM_LEDGER),
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
    }


def _pass_judge(provider_key: str, *, score: float = 0.92) -> dict[str, Any]:
    return {
        "provider_key": provider_key,
        "provider_name": provider_key,
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS",
        "pass": True,
        "decisive_failure": False,
        "normalized_score": score,
        "normalized_threshold": 0.8,
        "score": round(score * 5.0, 2),
        "findings": [],
        "fail_reasons": [],
        "remediation_suggestions": [],
    }


def _soft_fail_judge(
    provider_key: str,
    *,
    findings: list[str],
    score: float = 0.68,
) -> dict[str, Any]:
    return {
        "provider_key": provider_key,
        "provider_name": provider_key,
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "decisive_failure": False,
        "normalized_score": score,
        "normalized_threshold": 0.8,
        "score": round(score * 5.0, 2),
        "findings": findings,
        "fail_reasons": [],
        "remediation_suggestions": [],
    }


def scenario_two_pass_one_soft_shippable_draft() -> dict[str, Any]:
    """X2 PASS + 2/3 judges pass + 1 mild soft-fail → DRAFT_READY, no regen."""
    judges = [
        _soft_fail_judge(
            "anthropic_claude",
            findings=["wording could be tighter for executive tone"],
            score=0.79,
        ),
        _pass_judge("gemini_pro"),
        _pass_judge("openai_chatgpt"),
    ]
    return {
        "scenario_id": "two_pass_one_soft_shippable_draft",
        "l2_output": frozen_l2_output(),
        "x3_disposition": x3_disposition_for_judges(
            x3_code=_X3_SOFT_FAIL,
            x3_pass=False,
        ),
        "x1d_judges": judges,
        "manifest": {"proof_eligible": False},
        "expected": {
            "draft_ready": True,
            "certified": False,
            "process_exit_code": 0,
            "operator_status": "DRAFT_READY",
            "disposition_tier": "draft",
            "proof_eligible": False,
            "judge_regen_triggered": True,
            "judge_regen_trigger_mode": "any_judge_below_floor",
            "judge_regen_skip_reason": None,
            "soft_judge_only_rescore_eligible": False,
        },
    }


def scenario_two_pass_one_soft_solitary_severe_regen() -> dict[str, Any]:
    """X2 PASS + 2/3 pass + 1 severe synthesis soft-fail → regen triggers once."""
    judges = [
        _soft_fail_judge(
            "anthropic_claude",
            findings=[
                "Summary reads as stacked bullets; weak IT strategy and enterprise architecture synthesis",
            ],
            score=0.68,
        ),
        _pass_judge("gemini_pro"),
        _pass_judge("openai_chatgpt"),
    ]
    return {
        "scenario_id": "two_pass_one_soft_solitary_severe_regen",
        "l2_output": frozen_l2_output(),
        "x3_disposition": x3_disposition_for_judges(
            x3_code=_X3_SOFT_FAIL,
            x3_pass=False,
        ),
        "x1d_judges": judges,
        "manifest": {"proof_eligible": False},
        "expected": {
            "draft_ready": True,
            "certified": False,
            "process_exit_code": 0,
            "operator_status": "DRAFT_READY",
            "disposition_tier": "draft",
            "proof_eligible": False,
            "judge_regen_triggered": True,
            "judge_regen_trigger_mode": "any_judge_below_floor",
            "judge_regen_skip_reason": None,
            "soft_judge_only_rescore_eligible": False,
        },
    }


def scenario_certified_three_pass() -> dict[str, Any]:
    """X2 PASS + unanimous judges → CERTIFIED."""
    judges = [
        _pass_judge("anthropic_claude"),
        _pass_judge("gemini_pro"),
        _pass_judge("openai_chatgpt"),
    ]
    return {
        "scenario_id": "certified_three_pass",
        "l2_output": frozen_l2_output(),
        "x3_disposition": x3_disposition_for_judges(
            x3_code=_X3_ALLOW,
            x3_pass=True,
        ),
        "x1d_judges": judges,
        "manifest": {"proof_eligible": True},
        "expected": {
            "draft_ready": True,
            "certified": True,
            "process_exit_code": 0,
            "operator_status": "CERTIFIED",
            "disposition_tier": "certified",
            "proof_eligible": True,
            "judge_regen_triggered": False,
            "judge_regen_skip_reason": "all_model_backed_judges_pass",
            "soft_judge_only_rescore_eligible": False,
        },
    }


ACCEPTANCE_SCENARIOS = (
    scenario_two_pass_one_soft_shippable_draft(),
    scenario_two_pass_one_soft_solitary_severe_regen(),
    scenario_certified_three_pass(),
)
