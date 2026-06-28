"""IBM narrative word/char budget X2 gate (SSOT NARRATIVE_MAX_*)."""

from __future__ import annotations

from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates


def _gate_map(gates: list) -> dict[str, bool]:
    return {g.gate_id: g.pass_ for g in gates}


def test_ibm_narrative_word_budget_gate_present_and_passes_in_band() -> None:
    narrative = (
        "At IBM, delivered cloud-native analytics platforms with strong uptime and modernization "
        "outcomes across financial services clients and partner ecosystems."
    )
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        claim_ledger=[
            {"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]},
        ],
        companion_bullet_texts="",
        jd_text="Targeting only.",
        parsed_output={"narrative_sentence": narrative, "claim_ledger": []},
        raw_output="{}",
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        runtime_generation_status="REAL_LLM",
    )
    by_id = _gate_map(gates)
    assert "x2_ibm_narrative_word_budget" in by_id
    assert by_id["x2_ibm_narrative_word_budget"] is True
    assert by_id["x2_ibm_narrative_exactly_one_sentence"] is True


def test_ibm_narrative_word_budget_fails_over_58_words() -> None:
    words = " ".join(["enterprise"] * 60)
    narrative = f"At IBM, {words}."
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        claim_ledger=[{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}],
        companion_bullet_texts="",
        jd_text="Targeting only.",
        parsed_output={"narrative_sentence": narrative},
        raw_output="{}",
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        runtime_generation_status="REAL_LLM",
    )
    by_id = _gate_map(gates)
    assert by_id.get("x2_ibm_narrative_word_budget") is False


def test_ibm_narrative_word_budget_fails_over_360_chars() -> None:
    narrative = "At IBM, " + ("analytics " * 90) + "."
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        claim_ledger=[{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}],
        companion_bullet_texts="",
        jd_text="Targeting only.",
        parsed_output={"narrative_sentence": narrative},
        raw_output="{}",
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        runtime_generation_status="REAL_LLM",
    )
    assert _gate_map(gates).get("x2_ibm_narrative_word_budget") is False


def test_ibm_narrative_exactly_one_sentence_fails_two_sentences() -> None:
    narrative = "At IBM, modernized platforms. The team improved uptime."
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        claim_ledger=[{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}],
        companion_bullet_texts="",
        jd_text="Targeting only.",
        parsed_output={"narrative_sentence": narrative},
        raw_output="{}",
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        runtime_generation_status="REAL_LLM",
    )
    by_id = _gate_map(gates)
    assert by_id.get("x2_ibm_narrative_exactly_one_sentence") is False
