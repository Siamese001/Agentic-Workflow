"""Unify narrative lane nuance: single sentence, word budget, non-empty ledger."""

from __future__ import annotations

from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

UNIFY_NARRATIVE_CRITICAL_GATES = frozenset(
    {
        "x2_unify_narrative_exactly_one_sentence",
        "x2_unify_narrative_word_budget",
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
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output="{}",
        x1d_judges=[],
        allowed_fact_ids={"bul_unify_001"},
    )
    assert any(
        g.gate_id == "x2_unify_narrative_requires_finalized_bullets" and not g.pass_ for g in gates
    )
