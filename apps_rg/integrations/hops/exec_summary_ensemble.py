"""HOP-4B-EXEC-SUMMARY — Ensemble+Judge generation for the executive summary.

Locked specs (D9): 80-120 words across 3-4 sentences. 3 prompt variations
with structural diversity. Provenance traces every claim. Critical-tier —
failure aborts pipeline.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P4.2).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from apps_rg.integrations.hops._ensemble_runner import EnsembleResult, run_ensemble
from apps_rg.integrations.length_budget import budget_for_section

SECTION_ID = "hop_4b_exec_summary"
TIER = "critical"


def generate_exec_summary(
    *,
    company: str,
    archetype: str,
    marquee_outcomes: Iterable[str],
    strategic_priorities: Iterable[str],
    jd_facets: Iterable[str],
    company_facets: Iterable[str],
    mirror_terms: Iterable[str],
    seed_text: str = "",
    years_of_experience: Optional[int] = None,
    archive_dir: Optional[Path] = None,
) -> EnsembleResult:
    # Target length mirrors the seed (base master_resume.executive_summary)
    # so the generated summary is not shorter than the candidate's authentic
    # baseline. Fallback 120 words when no seed is available.
    seed_word_count = len(seed_text.split()) if seed_text else 0
    # Anchor to seed (the base master's authentic exec_summary length).
    # No arbitrary floor — if the base is 150 words, we target 150, not 110.
    target_words = seed_word_count if seed_word_count >= 90 else 120
    # Sentence count scales with length.
    target_sentences = 3 if target_words < 120 else (4 if target_words < 150 else 5)
    budget = budget_for_section(
        "exec_summary",
        target_words=target_words,
        target_sentences=target_sentences,
        tolerance=0.15,  # tightened: forces LLM to stay close to target
    )
    word_band = f"{int(target_words * 0.90)}-{int(target_words * 1.15)}"
    # Minimum word floor — the LLM tends to stay in the lower half of any
    # band; give it an explicit "must be at least" number.
    min_words = int(target_words * 0.90)

    seed = seed_text or (
        f"{archetype} with measurable outcomes across enterprise AI delivery, "
        f"now positioning for {company}'s strategic priorities."
    )
    # Build a neutral authenticity-guard clause: accurate tenure, no
    # target-company name dropped into the prose (that reads as contrived
    # customization to recruiters).
    tenure_clause = (
        f"The candidate has approximately {years_of_experience} years of experience — "
        f"use '{years_of_experience}+ years' or a similar accurate phrasing; "
        "NEVER downplay with '15+ years' or smaller figures. "
        if years_of_experience and years_of_experience >= 12
        else ""
    )
    authenticity_clause = (
        "AUTHENTICITY: Do NOT name the target company in the prose — "
        "position the candidate by archetype + capabilities, not by flattery. "
        f"{tenure_clause}"
    )
    prompt_variants = [
        ("structural_a_archetype_first", _prompt_archetype_first(archetype, word_band, target_sentences, min_words, authenticity_clause)),
        ("structural_b_outcome_first", _prompt_outcome_first(list(marquee_outcomes), word_band, target_sentences, min_words, authenticity_clause)),
        ("structural_c_priorities_first", _prompt_priorities_first(list(strategic_priorities), word_band, target_sentences, min_words, authenticity_clause)),
    ]
    return run_ensemble(
        section_id=SECTION_ID,
        seed_text=seed,
        prompt_variants=prompt_variants,
        budget=budget,
        mirror_terms=mirror_terms,
        jd_facets=jd_facets,
        company_facets=company_facets,
        archive_dir=archive_dir,
    )


def _prompt_archetype_first(archetype: str, word_band: str, sentences: int, min_words: int, authenticity: str) -> str:
    return (
        f"Write an executive summary of {word_band} words (MUST be at least {min_words} words) "
        f"across {sentences} sentences for a senior-executive resume. "
        f"{authenticity}"
        f"Sentence 1 leads with the archetype '{archetype}' plus accurate tenure. "
        "Sentence 2 cites two specific quantified outcomes (with %, $, or scale figures). "
        "Sentence 3 names the engagement model. Remaining sentences name the value thesis. "
        f"Do not come in shorter than {min_words} words — the band exists for brevity, not for "
        "under-delivery. Forbidden filler: leading, world-class, cutting-edge, leverage, synergy, "
        "enabled, robust, comprehensive. Return only the prose."
    )


def _prompt_outcome_first(outcomes, word_band: str, sentences: int, min_words: int, authenticity: str) -> str:
    sample = "; ".join(str(o) for o in outcomes[:3])
    return (
        f"Write an executive summary of {word_band} words (MUST be at least {min_words} words) "
        f"across {sentences} sentences. "
        f"{authenticity}"
        f"Sentence 1 opens with one quantified outcome from: {sample}. "
        "Subsequent sentences position the candidate by capability and name the consulting "
        f"engagement model. Do not come in shorter than {min_words} words. "
        "No filler intensifiers. Return only the prose."
    )


def _prompt_priorities_first(priorities, word_band: str, sentences: int, min_words: int, authenticity: str) -> str:
    sample = "; ".join(str(p) for p in priorities[:3])
    return (
        f"Write an executive summary of {word_band} words (MUST be at least {min_words} words) "
        f"across {sentences} sentences. "
        f"{authenticity}"
        f"Sentence 1 frames a strategic priority the candidate solves "
        f"(from: {sample}) — describe the priority WITHOUT naming the target company. "
        "Sentence 2 cites a candidate's matching delivered outcome. "
        f"Sentence 3 names the engagement model. Do not come in shorter than {min_words} words. "
        "No filler intensifiers. Return only the prose."
    )


__all__ = ["SECTION_ID", "TIER", "generate_exec_summary"]
