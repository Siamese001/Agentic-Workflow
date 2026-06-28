"""IBM narrative lane nuance: single sentence, meta-disclaimer ban, clause ledger."""

from __future__ import annotations

from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

IBM_NARRATIVE_CRITICAL_GATES = frozenset(
    {
        "x2_ibm_narrative_exactly_one_sentence",
        "x2_ibm_narrative_exactly_one_sentence_mechanical",
        "x2_ibm_narrative_forbidden_opener",
        "x2_ibm_narrative_metric_cap",
        "x2_ibm_narrative_bullet_overlap_threshold",
        "x2_ibm_narrative_word_budget",
        "x2_ibm_narrative_requires_finalized_bullets",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_ibm_narrative_no_meta_disclaimer_in_display",
        "x2_ibm_narrative_claim_ledger_clause_decomposition",
    }
)


def test_empty_claim_text_fails_claim_ledger_gate() -> None:
    narrative = (
        "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations for regulated "
        "financial services delivery."
    )
    ledger = [{"claim_text": "", "source_fact_ids": ["bul_ibm_001"]}]
    gates = run_ibm_narrative_x2_gates(
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
        allowed_fact_ids=["bul_ibm_001"],
    )
    assert any(g.gate_id == "x2_claim_ledger_claim_text_non_empty" and not g.pass_ for g in gates)


def test_career_bridge_phrase_fails_clause_decomposition_gate() -> None:
    narrative = (
        "At IBM, led cloud foundations, establishing discipline that supported later production AI leadership."
    )
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}]
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="- bul_ibm_001: text",
        companion_bullets_status="ACCEPTED_FINALIZED",
        companion_aware=True,
        provider_requested="mock",
        provider_attempted="mock",
        raw_output="{}",
        x1d_judges=[],
        allowed_fact_ids=["bul_ibm_001"],
    )
    assert any(
        g.gate_id == "x2_ibm_narrative_claim_ledger_clause_decomposition" and not g.pass_ for g in gates
    )


def test_real_llm_requires_finalized_ibm_companion() -> None:
    narrative = (
        "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations for regulated "
        "financial services delivery."
    )
    ledger = [{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}]
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": ledger},
        claim_ledger=ledger,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts="",
        companion_bullets_status="PENDING",
        companion_bullets_reason="ibm_bullets_not_accepted_finalized",
        companion_aware=True,
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        raw_output="{}",
        x1d_judges=[],
        allowed_fact_ids=["bul_ibm_001"],
    )
    assert any(
        g.gate_id == "x2_ibm_narrative_requires_finalized_bullets" and not g.pass_ for g in gates
    )
