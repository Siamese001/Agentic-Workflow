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


def _competencies_weak_fragments():
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    term = lambda t: {"text": t, "source_fact_id": "bul_unify_001", "source_fact_ids": ["bul_unify_001"]}
    weak = [
        {
            "category_label": "Technology Strategy & Innovation",
            "terms": [term("designed"), term("platform leads"), term("including senior engineers")],
            "source_fact_ids": ["bul_unify_001"],
        },
        {
            "category_label": "AI Platform Leadership",
            "terms": [term("led"), term("built"), term("managed")],
            "source_fact_ids": ["bul_unify_002"],
        },
    ]
    for i in range(5):
        weak.append(
            {
                "category_label": f"Engineering Area {i}",
                "terms": [
                    term("agentic platform orchestration"),
                    term("policy-gated routing"),
                    term("runtime governance"),
                ],
                "source_fact_ids": ["bul_unify_001"],
            }
        )
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
        resume_support_blob="agentic platform orchestration governance engineering",
        allowed_fact_ids={"bul_unify_001", "bul_unify_002"},
        runtime_generation_status="REAL_LLM",
    )


def _competencies_weak_unapproved_labels():
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    term = lambda t: {"text": t, "source_fact_id": "bul_unify_001", "source_fact_ids": ["bul_unify_001"]}
    weak = []
    for i, label in enumerate(
        (
            "Random Cat",
            "Misc Skills",
            "Foo Bar",
            "Data Platforms",
            "Sales Accounts",
            "Engineering Cluster",
        )
    ):
        weak.append(
            {
                "category_label": label,
                "terms": [
                    term("agentic platform orchestration"),
                    term("policy-gated routing"),
                    term("runtime governance"),
                ],
                "source_fact_ids": ["bul_unify_001"],
            }
        )
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


def _headline_weak_segment_decomposition():
    from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates

    hl = "SVP Engineering | Governed Agentic Platforms | Runtime Infrastructure | Regulated Delivery"
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


def _headline_weak_silent_row_drop():
    from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates

    hl = "SVP Engineering | Governed Agentic Platforms | Runtime Infrastructure | Regulated Delivery"
    parsed = {
        "headline_line": hl,
        "_headline_ledger_rows_dropped": 1,
        "selected_fact_plan": {"section_id": "headline", "required_fact_ids": []},
        "claim_ledger": [],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False, "briefing_used_as_proof": False},
    }
    return run_headline_x2_gates(
        headline_line=hl,
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="",
        target_company="",
        target_title="SVP Engineering",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids=set(),
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


def _exec_summary_jd_alignment() -> dict:
    return {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "companion_context_used_as_proof": False,
    }


def _executive_summary_weak_legacy_two_sentences():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    text = "Engineering executive leads platform delivery. Outcomes stay grounded in facts."
    return run_x2_gates(
        resume_display_text=text,
        parsed_output={
            "resume_display_text": text,
            "jd_alignment": _exec_summary_jd_alignment(),
        },
        claim_ledger=[{"claim_text": "platform delivery", "source_fact_ids": ["bul_unify_001"]}],
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


def _executive_summary_weak_credential_dump():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    text = (
        "Engineering executive builds governed agentic AI platforms for enterprise delivery. "
        "The leader scales platform lifecycle and commercial adoption across programs. "
        "Delivery outcomes remain grounded in selected executive facts. "
        "AWS Certified Machine Learning Engineer, AWS Certified Solutions Architect, Databricks Lakehouse "
        "Fundamentals, and Fellow of the Society of Actuaries credentials reinforce leadership."
    )
    return run_x2_gates(
        resume_display_text=text,
        parsed_output={
            "resume_display_text": text,
            "jd_alignment": _exec_summary_jd_alignment(),
        },
        claim_ledger=[{"claim_text": "platform delivery", "source_fact_ids": ["bul_unify_001"]}],
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


def _executive_summary_weak_empty_claim_text():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    text = (
        "Engineering executive builds governed agentic AI platforms for enterprise delivery. "
        "The leader scales platform lifecycle and commercial adoption across programs. "
        "Delivery outcomes remain grounded in selected executive facts. "
        "Prior roles show measurable outcomes grounded in selected executive facts."
    )
    return run_x2_gates(
        resume_display_text=text,
        parsed_output={
            "resume_display_text": text,
            "jd_alignment": _exec_summary_jd_alignment(),
        },
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


def _unify_narrative_weak_word_budget():
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    narrative = " ".join(["platform"] * 60)
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_unify_001"]}]
    parsed = {"narrative_sentence": narrative, "claim_ledger": ledger, "jd_alignment": {"targeting_only": True}}
    return run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=parsed,
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=_fake_judges(),
        allowed_fact_ids={"bul_unify_001"},
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


def _ibm_narrative_weak_meta_disclaimer():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    narrative = (
        "At IBM, led cloud foundations without claiming IBM delivered modern agentic platform products."
    )
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}]
    return run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        companion_aware=False,
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=_fake_judges(),
        allowed_fact_ids=["bul_ibm_001"],
    )


def _unify_bullets_weak_empty_claim_text():
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates

    bullets, parsed = [], {"bullets": [], "claim_ledger": [], "rewrite_distribution": {}}
    for bid in UNIFY_BULLET_IDS:
        text = f"Outcome for {bid}."
        bullets.append({"bullet_id": bid, "bullet_text": text, "rewrite_intensity": "MODERATE", "source_fact_ids": [bid]})
    bullets[0]["bullet_text"] = "Valid text."
    ledger = [{"claim_text": "", "source_fact_ids": ["bul_unify_001"]}]
    for b in bullets[1:]:
        ledger.append({"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]})
    parsed = {"bullets": bullets, "claim_ledger": ledger, "rewrite_distribution": {"HEAVY": 2, "MODERATE": 3, "LIGHT_PROTECTED": 1, "total": 6}}
    return run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=_fake_judges(),
    )


def _unify_bullets_weak_rewrite_distribution():
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates

    bullets = [{"bullet_id": bid, "bullet_text": f"Text {bid}.", "rewrite_intensity": "HEAVY", "source_fact_ids": [bid]} for bid in UNIFY_BULLET_IDS]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    parsed = {
        "bullets": bullets,
        "claim_ledger": ledger,
        "rewrite_distribution": {"HEAVY": 6, "MODERATE": 0, "LIGHT_PROTECTED": 0, "total": 6},
    }
    return run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )


def _unify_bullets_weak_metric_anchor():
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates

    bullets = []
    ledger = []
    for bid in UNIFY_BULLET_IDS:
        text = f"Governance outcome for {bid} without numeric anchors."
        if bid == "bul_unify_006":
            text = "Scaled global platform programs without revenue or margin figures."
        bullets.append({"bullet_id": bid, "bullet_text": text, "rewrite_intensity": "MODERATE", "source_fact_ids": [bid]})
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
    parsed = {"bullets": bullets, "claim_ledger": ledger, "rewrite_distribution": {"HEAVY": 2, "MODERATE": 3, "LIGHT_PROTECTED": 1, "total": 6}}
    return run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )


def _unify_bullets_weak_text_claim_coverage():
    from apps_rg.runtime.validators.unify_bullets_x2 import (
        UNIFY_BULLET_IDS,
        build_unify_bullets_text_claim_coverage,
        run_unify_bullets_x2_gates,
    )

    bullets = [{"bullet_id": bid, "bullet_text": f"Delivery {bid}.", "rewrite_intensity": "MODERATE", "source_fact_ids": [bid]} for bid in UNIFY_BULLET_IDS]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    cov = build_unify_bullets_text_claim_coverage(bullets, ledger, set(UNIFY_BULLET_IDS))
    row0 = dict(cov["sentences"][0])
    mc = [dict(row0["material_claims"][0])]
    mc[0]["claim_text"] = bullets[-1]["bullet_text"]
    row0["material_claims"] = mc
    cov["sentences"] = [row0, *cov["sentences"][1:]]
    parsed = {"bullets": bullets, "claim_ledger": ledger, "text_claim_coverage": cov}
    return run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )


def _unify_narrative_weak_requires_finalized():
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    narrative = "Led enterprise platform delivery and commercialization across regulated programs."
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_unify_001"]}]
    return run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts="",
        companion_bullets_status="NOT_FINALIZED",
        companion_bullets_reason="x3_not_ALLOW:X3_BLOCK",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output="{}",
        x1d_judges=_fake_judges(),
        allowed_fact_ids={"bul_unify_001"},
    )


def _unify_narrative_weak_empty_claim():
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    narrative = "Led enterprise platform delivery and commercialization across regulated programs."
    ledger = [{"claim_text": "   ", "source_fact_ids": ["bul_unify_001"]}]
    return run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="- bul_unify_001: text",
        companion_bullets_status="ACCEPTED_FINALIZED",
        x1d_judges=_fake_judges(),
        allowed_fact_ids={"bul_unify_001"},
    )


def _ibm_bullets_weak_empty_claim():
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS, run_ibm_bullets_x2_gates

    bullets = [{"bullet_id": bid, "bullet_text": f"IBM {bid}.", "rewrite_intensity": "MODERATE", "source_fact_ids": [bid]} for bid in IBM_BULLET_IDS]
    ledger = [{"claim_text": "", "source_fact_ids": ["bul_ibm_001"]}]
    parsed = {"bullets": bullets, "claim_ledger": ledger, "rewrite_distribution": {"HEAVY": 0, "MODERATE": 3, "LIGHT_PROTECTED": 2, "total": 5}}
    return run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(IBM_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )


def _ibm_bullets_weak_metric_anchor():
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS, run_ibm_bullets_x2_gates

    bullets = []
    ledger = []
    for bid in IBM_BULLET_IDS:
        text = f"Cloud foundations for {bid} without KPI restatement."
        if bid == "bul_ibm_005":
            text = "Led hyperscaler alliances without revenue or uptime metrics."
        bullets.append({"bullet_id": bid, "bullet_text": text, "rewrite_intensity": "MODERATE", "source_fact_ids": [bid]})
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
    parsed = {"bullets": bullets, "claim_ledger": ledger, "rewrite_distribution": {"HEAVY": 0, "MODERATE": 3, "LIGHT_PROTECTED": 2, "total": 5}}
    return run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(IBM_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )


def _ibm_bullets_weak_heavy_distribution():
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS, run_ibm_bullets_x2_gates

    bullets = [{"bullet_id": bid, "bullet_text": f"IBM {bid}.", "rewrite_intensity": "HEAVY", "source_fact_ids": [bid]} for bid in IBM_BULLET_IDS]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    parsed = {"bullets": bullets, "claim_ledger": ledger, "rewrite_distribution": {"HEAVY": 5, "MODERATE": 0, "LIGHT_PROTECTED": 0, "total": 5}}
    return run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(IBM_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )


def _ibm_narrative_weak_career_bridge():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    narrative = (
        "At IBM, led cloud foundations, establishing discipline that supported later production AI "
        "platform leadership."
    )
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}]
    return run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="- bul_ibm_001: text",
        companion_bullets_status="ACCEPTED_FINALIZED",
        companion_aware=True,
        x1d_judges=_fake_judges(),
        allowed_fact_ids=["bul_ibm_001"],
    )


def _ibm_narrative_weak_requires_finalized():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    narrative = (
        "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations for regulated "
        "financial services delivery."
    )
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}]
    return run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts="",
        companion_bullets_status="PENDING",
        companion_bullets_reason="ibm_bullets_not_accepted_finalized",
        companion_aware=True,
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        x1d_judges=_fake_judges(),
        allowed_fact_ids=["bul_ibm_001"],
    )


def _unify_bullets_weak_mechanism_stack():
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates

    stack = (
        "deterministic routing, multi-agent orchestration, GraphRAG, sandboxed execution, policy gating"
    )
    bullets = []
    ledger = []
    for bid in UNIFY_BULLET_IDS:
        text = stack if bid in {"bul_unify_001", "bul_unify_002"} else f"Delivery outcome for {bid}."
        if bid == "bul_unify_004":
            text = "Reduced cycle from six months to three weeks."
        if bid == "bul_unify_006":
            text = "Generated $22M revenue, 20% margin, scaled 8 to 28 specialists."
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "rewrite_intensity": "MODERATE",
                "source_fact_ids": [bid],
            }
        )
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
    parsed = {
        "bullets": bullets,
        "claim_ledger": ledger,
        "rewrite_distribution": {"HEAVY": 2, "MODERATE": 3, "LIGHT_PROTECTED": 1, "total": 6},
    }
    return run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
    )


def all_weak_fail_cases() -> tuple[WeakFailCase, ...]:
    return (
        WeakFailCase(
            "competencies",
            "x2_competencies_no_all_generic_skill_phrase",
            _competencies_weak_generic_keywords,
        ),
        WeakFailCase("competencies", "x2_competencies_min_items_per_category", _competencies_weak_two_items),
        WeakFailCase(
            "competencies",
            "x2_competencies_no_fragment_or_one_word_terms",
            _competencies_weak_fragments,
        ),
        WeakFailCase(
            "competencies",
            "x2_competencies_approved_category_labels",
            _competencies_weak_unapproved_labels,
        ),
        WeakFailCase("headline", "x2_headline_pipe_four_segments", _headline_weak_pipe_segments),
        WeakFailCase(
            "headline",
            "x2_headline_claim_ledger_segment_decomposition",
            _headline_weak_segment_decomposition,
        ),
        WeakFailCase(
            "headline",
            "x2_headline_claim_ledger_no_silent_row_drop",
            _headline_weak_silent_row_drop,
        ),
        WeakFailCase("unify_bullets", "x2_unify_bullet_count_6", _unify_bullets_weak_count),
        WeakFailCase(
            "unify_bullets",
            "x2_unify_at_most_one_mechanism_dense_bullet",
            _unify_bullets_weak_mechanism_stack,
        ),
        WeakFailCase(
            "executive_summary",
            "x2_exec_summary_sentence_count_6",
            _executive_summary_weak_legacy_two_sentences,
        ),
        WeakFailCase(
            "executive_summary",
            "x2_exec_summary_no_credential_dump",
            _executive_summary_weak_credential_dump,
        ),
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
        WeakFailCase(
            "unify_narrative",
            "x2_unify_narrative_word_budget",
            _unify_narrative_weak_word_budget,
        ),
        WeakFailCase("ibm_bullets", "x2_ibm_bullet_count_5", _ibm_bullets_weak_count),
        WeakFailCase(
            "ibm_narrative",
            "x2_ibm_narrative_exactly_one_sentence",
            _ibm_narrative_weak_empty_sentence,
        ),
        WeakFailCase(
            "ibm_narrative",
            "x2_ibm_narrative_no_meta_disclaimer_in_display",
            _ibm_narrative_weak_meta_disclaimer,
        ),
        WeakFailCase(
            "unify_bullets",
            "x2_claim_ledger_claim_text_non_empty",
            _unify_bullets_weak_empty_claim_text,
        ),
        WeakFailCase(
            "unify_bullets",
            "x2_unify_rewrite_distribution_valid",
            _unify_bullets_weak_rewrite_distribution,
        ),
        WeakFailCase(
            "unify_bullets",
            "x2_unify_metric_anchor_bullet_ownership",
            _unify_bullets_weak_metric_anchor,
        ),
        WeakFailCase(
            "unify_bullets",
            "x2_text_claim_coverage_integrity",
            _unify_bullets_weak_text_claim_coverage,
        ),
        WeakFailCase(
            "unify_narrative",
            "x2_unify_narrative_requires_finalized_bullets",
            _unify_narrative_weak_requires_finalized,
        ),
        WeakFailCase(
            "unify_narrative",
            "x2_claim_ledger_claim_text_non_empty",
            _unify_narrative_weak_empty_claim,
        ),
        WeakFailCase(
            "ibm_bullets",
            "x2_claim_ledger_claim_text_non_empty",
            _ibm_bullets_weak_empty_claim,
        ),
        WeakFailCase(
            "ibm_bullets",
            "x2_ibm_metric_anchor_bullet_ownership",
            _ibm_bullets_weak_metric_anchor,
        ),
        WeakFailCase(
            "ibm_bullets",
            "x2_ibm_rewrite_distribution_valid",
            _ibm_bullets_weak_heavy_distribution,
        ),
        WeakFailCase(
            "ibm_narrative",
            "x2_ibm_narrative_claim_ledger_clause_decomposition",
            _ibm_narrative_weak_career_bridge,
        ),
        WeakFailCase(
            "ibm_narrative",
            "x2_ibm_narrative_requires_finalized_bullets",
            _ibm_narrative_weak_requires_finalized,
        ),
    )


__all__ = ["all_weak_fail_cases", "_gate_pass"]
