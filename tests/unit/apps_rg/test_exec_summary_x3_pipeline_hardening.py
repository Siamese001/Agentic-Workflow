"""Regression tests for executive_summary X3_ALLOW pipeline hardening (May 2026).

Covers bug-fix seams from graph-only repair / judge-polish / judge-regen pre-accept:
- canonical six-sentence arc rebuild when polish sees <6 sentences
- deterministic word-budget trim before regen rejection
- unify unsupported metric claim detection
- cross-section signal guard edge cases
"""
from __future__ import annotations

import re

from apps_rg.runtime.sections.cross_section_signal_guards import (
    base_archive_ngram_overlap,
    detect_jd_only_phrases,
    is_flat_skill_only_graph_packet,
)
from apps_rg.runtime.sections.executive_summary_voice_repair import (
    _rebuild_canonical_six_sentence_arc,
    _trim_paragraph_word_budget,
    polish_executive_summary_judge_alignment,
)
from apps_rg.runtime.validators.executive_summary_x2 import EXEC_SUMMARY_MAX_WORDS
from apps_rg.runtime.validators.unify_role_episode_x2 import detect_unsupported_metric_claims


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _canonical_selected_facts() -> list[dict]:
    return [
        {"fact_id": "fact_governance_003", "claim_text": "Basel lineage cut errors 40%."},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Graph intelligence."},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA quantitative foundation."},
        {"fact_id": "fact_consulting_001", "claim_text": "Regulatory IT transformations."},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML org 8 to 28."},
    ]


def test_rebuild_canonical_six_sentence_arc_from_degenerate_five() -> None:
    s1 = (
        "Enterprise technology leader who unifies governed AI platforms into one "
        "IT strategy agenda for regulated enterprises."
    )
    degenerate = [s1] + ["Short filler sentence."] * 4
    rebuilt = _rebuild_canonical_six_sentence_arc(degenerate, selected_facts=_canonical_selected_facts())
    assert len(rebuilt) == 6
    assert rebuilt[0] == s1
    assert "Basel III" in rebuilt[1]


def test_polish_skips_when_arc_cannot_reach_six_sentences() -> None:
    parsed = {
        "resume_display_text": "Only one sentence after graph-only repair collapse.",
        "claim_ledger": [],
    }
    polished, receipt = polish_executive_summary_judge_alignment(
        parsed, selected_facts=[{"fact_id": "fact_governance_003", "claim_text": "stub"}],
    )
    assert receipt.get("applied") is not True
    assert polished.get("resume_display_text") == parsed["resume_display_text"]


def test_trim_paragraph_word_budget_trims_fsa_established_through() -> None:
    """Regression: regen drafts at 141-145 words must trim (not reject) before X2."""
    sents = [
        "Enterprise technology leader who unifies governed AI platforms into one IT strategy agenda for regulated enterprises.",
        "From that platform footprint, platform commercialization generated $22M in IP-led revenue and expanded gross margins by 20%.",
        "Against that lineage backdrop, Basel III and CCAR data lineage frameworks cut regulatory reporting errors by 40%.",
        "Complementing that regulatory foundation, re-architected monolithic risk analytics with containerized HPC microservices, trimming stress-testing cycles by 40%.",
        (
            "That regulatory foundation is grounded in quantitative rigor established through "
            "FSA-chartered actuarial work in capital modeling and portfolio stress analytics, "
            "informing data governance and AI strategy at scale."
        ),
        "Innovation incubation will extend governed platform capabilities across business units while preserving lineage discipline.",
    ]
    # Pad into the regen failure band (141-145 words) — one FSA trim should suffice.
    while _word_count(" ".join(sents)) < 141:
        sents[0] += " platform"
    before = _word_count(" ".join(sents))
    assert 141 <= before <= 145, f"fixture should sit in regen trim band, got {before}"
    trimmed = _trim_paragraph_word_budget(sents, max_words=EXEC_SUMMARY_MAX_WORDS)
    after = _word_count(" ".join(trimmed))
    assert after <= EXEC_SUMMARY_MAX_WORDS
    assert after < before
    assert "established through" not in trimmed[4].lower()


def test_detect_unsupported_metric_claims_blocks_unapproved_dollars() -> None:
    assert detect_unsupported_metric_claims(
        "Platform expansion unlocked $5M in new operating savings within eighteen months."
    )
    assert not detect_unsupported_metric_claims(
        "Platform commercialization generated $22M in IP-led revenue and 20% margin expansion."
    )


def test_cross_section_jd_only_phrase_empty_inputs() -> None:
    assert detect_jd_only_phrases("", "some jd text", min_run=6) == []
    assert detect_jd_only_phrases("output text", "", min_run=6) == []


def test_cross_section_flat_skill_packet_requires_bundle_for_proof() -> None:
    assert is_flat_skill_only_graph_packet({"graph_skill_node_ids": ["skill_1"]})
    assert not is_flat_skill_only_graph_packet(
        {"graph_skill_node_ids": ["skill_1"], "role_episode_bundle_id": "reb_1"}
    )
    assert base_archive_ngram_overlap("any text", []) == 0.0
