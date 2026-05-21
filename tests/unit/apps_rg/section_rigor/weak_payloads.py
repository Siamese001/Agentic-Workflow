"""Deliberately weak section payloads — each must trip a named X2 gate."""

from __future__ import annotations

import json
from typing import Any

from tests.unit.apps_rg.section_rigor.lane_registry import WeakFailCase


def _gate_pass(results: list, gate_id: str) -> bool:
    for g in results:
        gid = getattr(g, "gate_id", None) or (g.get("gate_id") if isinstance(g, dict) else None)
        if gid == gate_id:
            return bool(getattr(g, "pass_", g.get("pass") if isinstance(g, dict) else False))
    raise AssertionError(f"missing gate {gate_id}")


def _fake_judges() -> list[dict[str, Any]]:
    return [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
    ]


def _competencies_weak_generic_keywords():
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    term = lambda t: {"text": t, "source_fact_id": "bul_unify_001", "source_fact_ids": ["bul_unify_001"]}
    weak = [
        {
            "category_label": f"Cat {i}",
            "terms": [term("team scaling"), term("pipeline analytics"), term("synergy modeling")],
            "source_fact_ids": ["bul_unify_001"],
        }
        for i in range(6)
    ]
    parsed = {
        "competencies": weak,
        "selected_fact_plan": {"selected_fact_ids": ["bul_unify_001"]},
        "claim_ledger": [
            {
                "claim_id": "c1",
                "claim_text": "Built agentic AI platforms with runtime governance.",
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False, "briefing_used_as_proof": False},
    }
    return run_competencies_x2_gates(
        competencies=weak,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=[],
        resume_support_blob="agentic platform orchestration governance",
        allowed_fact_ids={"bul_unify_001", "bul_unify_002"},
        runtime_generation_status="REAL_LLM",
    )


def _competencies_weak_two_items():
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    term = lambda t: {"text": t, "source_fact_id": "bul_unify_001", "source_fact_ids": ["bul_unify_001"]}
    weak = [
        {
            "category_label": f"Cat {i}",
            "terms": [term("team scaling"), term("margin expansion")],
            "source_fact_ids": ["bul_unify_001"],
        }
        for i in range(6)
    ]
    parsed = {
        "competencies": weak,
        "selected_fact_plan": {"selected_fact_ids": ["bul_unify_001"]},
        "claim_ledger": [
            {
                "claim_id": "c1",
                "claim_text": "Built agentic AI platforms with runtime governance.",
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False, "briefing_used_as_proof": False},
    }
    return run_competencies_x2_gates(
        competencies=weak,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=[],
        resume_support_blob="agentic platform orchestration governance",
        allowed_fact_ids={"bul_unify_001", "bul_unify_002"},
        runtime_generation_status="REAL_LLM",
    )


def _headline_weak_pipe_segments():
    from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates

    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure"
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": {"section_id": "headline", "required_fact_ids": ["bul_unify_001"]},
        "claim_ledger": [{"claim_text": hl, "source_fact_ids": ["bul_unify_001"]}],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False, "briefing_used_as_proof": False},
    }
    return run_headline_x2_gates(
        headline_line=hl,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="enterprise platform",
        target_company="",
        target_title="SVP Engineering",
        resume_support_blob=json.dumps({"employment": [], "header": {"name": "A B"}}),
        employer_names_lower=["contoso"],
        allowed_fact_ids={"bul_unify_001"},
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
    )


def _unify_bullets_weak_count():
    from apps_rg.runtime.validators.unify_bullets_x2 import run_unify_bullets_x2_gates

    bullets = [{"bullet_id": f"bul_unify_00{i}", "text": f"Bullet {i}."} for i in range(1, 4)]
    parsed = {
        "bullets": bullets,
        "claim_ledger": [],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
    }
    return run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="",
        allowed_fact_ids=set(),
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=_fake_judges(),
    )


def _executive_summary_weak_empty_claim_text():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    text = "Governed agentic AI platform delivery across enterprise systems."
    return run_x2_gates(
        resume_display_text=text,
        parsed_output={"resume_display_text": text},
        claim_ledger=[{"claim_text": "", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Synthetic Enterprise Corp.",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="MOCKED",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        x1d_judges=_fake_judges(),
    )


def _unify_narrative_weak_empty_sentence():
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    parsed = {"narrative_sentence": "", "claim_ledger": [], "jd_alignment": {"targeting_only": True}}
    return run_unify_narrative_x2_gates(
        narrative_sentence="",
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=_fake_judges(),
        allowed_fact_ids=set(),
    )


def _ibm_bullets_weak_count():
    from apps_rg.runtime.validators.ibm_bullets_x2 import run_ibm_bullets_x2_gates

    bullets = [{"bullet_id": "bul_ibm_001", "text": "Only one."}]
    parsed = {"bullets": bullets, "claim_ledger": [], "jd_alignment": {"targeting_only": True}}
    return run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="",
        allowed_fact_ids=set(),
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=_fake_judges(),
    )


def _ibm_narrative_weak_empty_sentence():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    parsed = {"narrative_sentence": "", "claim_ledger": [], "jd_alignment": {"targeting_only": True}}
    return run_ibm_narrative_x2_gates(
        narrative_sentence="",
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=_fake_judges(),
        allowed_fact_ids=[],
    )


def all_weak_fail_cases() -> tuple[WeakFailCase, ...]:
    return (
        WeakFailCase(
            "competencies",
            "x2_competencies_no_all_generic_skill_phrase",
            _competencies_weak_generic_keywords,
        ),
        WeakFailCase("competencies", "x2_competencies_min_items_per_category", _competencies_weak_two_items),
        WeakFailCase("headline", "x2_headline_pipe_four_segments", _headline_weak_pipe_segments),
        WeakFailCase("unify_bullets", "x2_unify_bullet_count_6", _unify_bullets_weak_count),
        WeakFailCase(
            "executive_summary",
            "x2_claim_ledger_claim_text_non_empty",
            _executive_summary_weak_empty_claim_text,
        ),
        WeakFailCase(
            "unify_narrative",
            "x2_unify_narrative_exactly_one_sentence",
            _unify_narrative_weak_empty_sentence,
        ),
        WeakFailCase("ibm_bullets", "x2_ibm_bullet_count_5", _ibm_bullets_weak_count),
        WeakFailCase(
            "ibm_narrative",
            "x2_ibm_narrative_exactly_one_sentence",
            _ibm_narrative_weak_empty_sentence,
        ),
    )


__all__ = ["all_weak_fail_cases", "_gate_pass"]
