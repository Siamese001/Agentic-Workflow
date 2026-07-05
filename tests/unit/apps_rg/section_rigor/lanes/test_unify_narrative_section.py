"""Unify narrative lane nuance: single sentence, word budget, non-empty ledger."""

from __future__ import annotations

import json

from apps_rg.runtime.sections.unify_narrative_lane import normalize_unify_narrative_parsed
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

UNIFY_NARRATIVE_CRITICAL_GATES = frozenset(
    {
        "x2_unify_narrative_exactly_one_sentence",
        "x2_unify_narrative_exactly_one_sentence_mechanical",
        "x2_unify_narrative_forbidden_opener",
        "x2_unify_narrative_metric_cap",
        "x2_unify_narrative_bullet_overlap_threshold",
        "x2_unify_narrative_word_budget",
        "x2_unify_narrative_requires_finalized_bullets",
        "x2_claim_ledger_claim_text_non_empty",
    }
)


def test_word_budget_fails_when_narrative_exceeds_58_words() -> None:
    narrative = " ".join(["word"] * 60)
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_unify_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=[],
        allowed_fact_ids={"bul_unify_001"},
    )
    assert any(g.gate_id == "x2_unify_narrative_word_budget" and not g.pass_ for g in gates)


def test_empty_claim_text_fails_claim_ledger_gate() -> None:
    narrative = "Led enterprise platform delivery and commercialization across regulated programs."
    ledger = [{"claim_text": "", "source_fact_ids": ["bul_unify_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=[],
        allowed_fact_ids={"bul_unify_001"},
    )
    assert any(g.gate_id == "x2_claim_ledger_claim_text_non_empty" and not g.pass_ for g in gates)


def test_real_llm_requires_finalized_companion_when_missing() -> None:
    narrative = "Led enterprise platform delivery and commercialization across regulated programs."
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_unify_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts="",
        companion_bullets_status="MISSING",
        companion_bullets_reason="unify_bullets_l2_output_not_found",
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        raw_output="{}",
        x1d_judges=[],
        allowed_fact_ids={"bul_unify_001"},
    )
    assert any(
        g.gate_id == "x2_unify_narrative_requires_finalized_bullets" and not g.pass_ for g in gates
    )


def test_unify_narrative_normalization_trims_metric_recap_before_x2() -> None:
    narrative = (
        "Owned the end-to-end mandate transforming Unify Consulting's agentic AI practice into a commercial engine, "
        "architecting governed runtime systems and productized IP that drove $22M revenue and scaled the engineering "
        "organization from 8 to 28."
    )
    companion = (
        "- bul_unify_006: Platform Commercialization and Engineering Leadership: drove $22M revenue, 20% margin, "
        "scaled the engineering organization from 8 to 28, and compressed six months to three weeks."
    )
    parsed = {
        "narrative_sentence": narrative,
        "claim_ledger": [{"claim_text": narrative, "source_fact_ids": ["bul_unify_006"]}],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "bul_unify_006",
                    "claim_text": "Platform Commercialization and Engineering Leadership",
                }
            ]
        },
        "jd_alignment": {"targeting_only": True},
        "change_log": [],
        "self_check": {},
    }
    runtime_payload = {
        "selected_fact_plan": parsed["selected_fact_plan"],
        "allowed_fact_ids": ["bul_unify_006"],
        "briefing": "",
        "jd_text": "enterprise strategy and platform governance",
    }
    normalized = normalize_unify_narrative_parsed(parsed, runtime_payload, companion_text=companion)
    assert normalized is not None
    assert "scaled the engineering organization from 8 to 28" not in normalized["narrative_sentence"].lower()
    assert "expanded the engineering team" in normalized["narrative_sentence"].lower()
    assert any(
        step.get("operation") == "companion_metric_budget_deterministic_trim"
        for step in normalized.get("change_log") or []
    )
    gates = run_unify_narrative_x2_gates(
        narrative_sentence=normalized["narrative_sentence"],
        parsed_output=normalized,
        claim_ledger=normalized["claim_ledger"],
        jd_text=runtime_payload["jd_text"],
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=companion,
        companion_bullets_status="ACCEPTED_FINALIZED",
        companion_bullets_reason="ok",
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        raw_output=json.dumps(normalized, ensure_ascii=False),
        x1d_judges=[],
        allowed_fact_ids={"bul_unify_006"},
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_narrative_metric_cap"].pass_ is True
    assert by_id["x2_no_companion_ngram_copy"].pass_ is True


def test_unify_narrative_normalization_trims_exact_companion_overlap_phrase() -> None:
    narrative = (
        "Stewarded Unify Consulting's shift from bespoke agentic AI engagements into a productized platform "
        "operating model, anchoring the control-plane architecture and IP-led revenue engine that scaled "
        "engineering from 8 to 28 while expanding margins across regulated financial-services enterprises."
    )
    companion = (
        "- bul_unify_006: Platform Commercialization and Engineering Leadership: drove $22M revenue, 20% margin, "
        "scaled the engineering organization from 8 to 28, and compressed six months to three weeks."
    )
    parsed = {
        "narrative_sentence": narrative,
        "claim_ledger": [{"claim_text": narrative, "source_fact_ids": ["bul_unify_006"]}],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "bul_unify_006",
                    "claim_text": "Platform Commercialization and Engineering Leadership",
                }
            ]
        },
        "jd_alignment": {"targeting_only": True},
        "change_log": [],
        "self_check": {},
    }
    runtime_payload = {
        "selected_fact_plan": parsed["selected_fact_plan"],
        "allowed_fact_ids": ["bul_unify_006"],
        "briefing": "",
        "jd_text": "enterprise strategy and platform governance",
    }
    normalized = normalize_unify_narrative_parsed(parsed, runtime_payload, companion_text=companion)
    assert normalized is not None
    assert "from 8 to 28" not in normalized["narrative_sentence"].lower()
    gates = run_unify_narrative_x2_gates(
        narrative_sentence=normalized["narrative_sentence"],
        parsed_output=normalized,
        claim_ledger=normalized["claim_ledger"],
        jd_text=runtime_payload["jd_text"],
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=companion,
        companion_bullets_status="ACCEPTED_FINALIZED",
        companion_bullets_reason="ok",
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        raw_output=json.dumps(normalized, ensure_ascii=False),
        x1d_judges=[],
        allowed_fact_ids={"bul_unify_006"},
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_no_companion_ngram_copy"].pass_ is True


def test_unify_narrative_normalization_collapses_live_comma_stack_before_x2() -> None:
    narrative = (
        "Owned Unify Consulting's governed agentic AI platform mandate, turning architecture, "
        "partner distribution, and productized services into a commercial engine for regulated "
        "enterprises through reusable IP, scalable delivery, and disciplined adoption."
    )
    companion = (
        "- bul_unify_001: Own SVP-level architecture for a governed agentic AI platform.\n"
        "- bul_unify_002: Built Unify's global AI channel program.\n"
        "- bul_unify_006: Productized agentic AI primitives into reusable platform services."
    )
    parsed = {
        "narrative_sentence": narrative,
        "claim_ledger": [
            {
                "claim_text": "Owned SVP-level governed agentic AI platform architecture.",
                "source_fact_ids": ["reb_unify_agentic_platform_architecture"],
            },
            {
                "claim_text": "Built partner distribution around reusable AI platform services.",
                "source_fact_ids": ["reb_unify_partner_channel_cosell"],
            },
            {
                "claim_text": "Converted platform capability into reusable IP.",
                "source_fact_ids": ["reb_unify_platform_commercialization_leadership"],
            },
        ],
        "selected_fact_plan": {"facts": []},
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_jd_themes": ["partner architecture"],
            "selected_briefing_themes": [],
            "targeting_rationale": "Targeting only.",
        },
        "change_log": [],
        "self_check": {},
    }
    runtime_payload = {
        "selected_fact_plan": parsed["selected_fact_plan"],
        "allowed_fact_ids": [
            "reb_unify_agentic_platform_architecture",
            "reb_unify_partner_channel_cosell",
            "reb_unify_platform_commercialization_leadership",
        ],
        "briefing": "",
        "jd_text": "partner architecture",
    }

    normalized = normalize_unify_narrative_parsed(parsed, runtime_payload, companion_text=companion)
    assert normalized is not None
    assert normalized["narrative_sentence"].count(",") < 5
    assert any(
        step.get("operation") == "comma_stack_deterministic_trim"
        for step in normalized.get("change_log") or []
    )

    gates = run_unify_narrative_x2_gates(
        narrative_sentence=normalized["narrative_sentence"],
        parsed_output=normalized,
        claim_ledger=normalized["claim_ledger"],
        jd_text=runtime_payload["jd_text"],
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=companion,
        companion_bullets_status="ACCEPTED_FINALIZED",
        companion_bullets_reason="ok",
        provider_requested="external_openai",
        provider_attempted="external_openai",
        raw_output=json.dumps(normalized, ensure_ascii=False),
        x1d_judges=[],
        allowed_fact_ids=set(runtime_payload["allowed_fact_ids"]),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_no_six_bullet_summary"].pass_ is True
