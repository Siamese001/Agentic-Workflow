"""Regression tests for exec-summary word-budget trim and canonical arc rebuild (X3_ALLOW fixes)."""

from __future__ import annotations

import re

from apps_rg.runtime.sections.executive_summary_voice_repair import (
    _rebuild_canonical_six_sentence_arc,
    _trim_paragraph_word_budget,
    polish_executive_summary_judge_alignment,
)
from apps_rg.runtime.validators.executive_summary_x2 import EXEC_SUMMARY_MAX_WORDS


def _word_count(sentences: list[str]) -> int:
    return len(re.findall(r"\S+", " ".join(sentences)))


def test_trim_paragraph_word_budget_removes_established_through_on_fsa_sentence() -> None:
    sentences = [
        "Enterprise technology leader who unifies governed AI platforms for regulated enterprises.",
        "Applied across enterprise programs, Basel III and CCAR data lineage cut regulatory reporting errors by 40%.",
        "Software dependency graph intelligence enables accelerated legacy-system analysis across enterprise complexity.",
        (
            "That regulatory foundation is grounded in quantitative rigor established through "
            "FSA-chartered actuarial work in capital modeling and portfolio stress analytics, "
            "informing data governance and AI strategy at scale."
        ),
        (
            "Against that delivery foundation, directed large-scale regulatory IT transformations "
            "and legacy-modernization programs for major financial institutions across enterprise "
            "risk, compliance, data, cloud, and architecture domains."
        ),
        (
            "Innovation incubation and architecture standards will federate governed platform "
            "capabilities across autonomous business units without weakening lineage discipline."
        ),
    ]
    assert _word_count(sentences) > EXEC_SUMMARY_MAX_WORDS
    trimmed = _trim_paragraph_word_budget(sentences, max_words=EXEC_SUMMARY_MAX_WORDS)
    assert _word_count(trimmed) <= EXEC_SUMMARY_MAX_WORDS
    fsa_sentence = trimmed[3].lower()
    assert "established through" not in fsa_sentence
    assert "through fsa-chartered" in fsa_sentence


def test_trim_paragraph_word_budget_noop_when_under_cap() -> None:
    sentences = [
        "Short executive summary sentence one.",
        "Short executive summary sentence two.",
        "Short executive summary sentence three.",
        "Short executive summary sentence four.",
        "Short executive summary sentence five.",
        "Short executive summary sentence six.",
    ]
    trimmed = _trim_paragraph_word_budget(sentences, max_words=EXEC_SUMMARY_MAX_WORDS)
    assert trimmed == sentences


def test_rebuild_canonical_six_sentence_arc_preserves_identity_thesis() -> None:
    s1 = "Enterprise technology leader who unifies governed AI platforms for regulated enterprises."
    degenerate = [s1] * 5
    facts = [
        {"fact_id": "fact_governance_003", "claim_text": "Basel III cut errors 40%"},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Dependency graph intelligence"},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA-chartered actuarial work"},
        {"fact_id": "fact_consulting_001", "claim_text": "Directed regulatory IT transformations"},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML engineering organization"},
    ]
    rebuilt = _rebuild_canonical_six_sentence_arc(degenerate, selected_facts=facts)
    assert len(rebuilt) == 6
    assert rebuilt[0] == s1
    assert "basel iii" in rebuilt[1].lower()
    assert "dependency graph" in rebuilt[2].lower()
    assert "8 to 28" in rebuilt[5].lower()


def test_polish_rebuilds_canonical_arc_when_llm_returns_five_sentences() -> None:
    """Regression: graph_only_repair collapsing to 5 sentences must not silently skip polish."""
    parsed = {
        "resume_display_text": (
            "Enterprise technology leader who unifies governed AI platforms for regulated enterprises. "
            "Designed and operationalized a governed agentic AI platform with deterministic routing. "
            "Platform commercialization generated $22M in IP-led revenue. "
            "Implemented Basel III and CCAR lineage frameworks that reduced regulatory reporting errors by 40%. "
            "Innovation incubation will extend governed platform capabilities across business units."
        ),
        "claim_ledger": [],
    }
    facts = [
        {"fact_id": "fact_engineering_platform_001", "claim_text": "Governed agentic AI platform"},
        {"fact_id": "fact_governance_003", "claim_text": "Basel III cut errors 40%"},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Dependency graph intelligence"},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA-chartered actuarial work"},
        {"fact_id": "fact_consulting_001", "claim_text": "Directed regulatory IT transformations"},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML engineering organization"},
    ]
    polished, receipt = polish_executive_summary_judge_alignment(parsed, selected_facts=facts)
    text = str(polished.get("resume_display_text") or "")
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    assert len(sents) == 6
    assert "canonical_arc_rebuild" in (receipt.get("actions") or [])
    assert receipt.get("applied") is True
