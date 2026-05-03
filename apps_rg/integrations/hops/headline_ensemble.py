"""HOP-4A-HEADLINE — Ensemble+Judge generation for the resume headline.

Locked specs (D9): 10-14 word headline, 3 prompt variations, aggressive
filler-intensifier filter. Critical-tier — failure aborts pipeline.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P4.1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from apps_rg.integrations.hops._ensemble_runner import EnsembleResult, run_ensemble
from apps_rg.integrations.length_budget import budget_for_section

SECTION_ID = "hop_4a_headline"
TIER = "critical"


def generate_headline(
    *,
    company: str,
    archetype: str,
    marquee_outcomes: Iterable[str],
    pain_points: Iterable[str],
    jd_facets: Iterable[str],
    company_facets: Iterable[str],
    mirror_terms: Iterable[str],
    seed_text: str = "",
    target_role: str = "",
    archive_dir: Optional[Path] = None,
) -> EnsembleResult:
    # 9-14 word hard cap so the headline fits on a single resume line after
    # rendering at 11pt bold. When target_role is supplied, the LLM is asked
    # to weave it into the headline directly (so ensure_title_in_headline
    # later becomes a no-op and no prepend-bloat happens).
    budget = budget_for_section("headline", target_words=11, target_sentences=1, tolerance=0.25)

    base_seed = seed_text or _archetype_seed(archetype, company, target_role)
    mirror_list = list(mirror_terms)
    prompt_variants = [
        ("lead_with_archetype", _prompt_archetype(archetype, company, jd_facets, target_role, mirror_list)),
        ("marquee", _prompt_marquee(list(marquee_outcomes), company, target_role, mirror_list)),
        ("pain_point", _prompt_pain_point(list(pain_points), company, target_role, mirror_list)),
    ]
    return run_ensemble(
        section_id=SECTION_ID,
        seed_text=base_seed,
        prompt_variants=prompt_variants,
        budget=budget,
        mirror_terms=mirror_terms,
        jd_facets=jd_facets,
        company_facets=company_facets,
        archive_dir=archive_dir,
    )


def _archetype_seed(archetype: str, company: str, target_role: str = "") -> str:
    archetype = (archetype or "Agentic Transformation Leader").strip()
    return f"{archetype} | Scaling Pilot to Production | Driving Organizational Readiness"[:140]


def _title_clause(target_role: str) -> str:
    """Return a context note about the target role without forcing literal repetition.
    The job title already appears on the resume header — the headline should add
    signal, not repeat it.
    """
    if not target_role.strip():
        return ""
    return (
        f"The candidate is applying for '{target_role.strip()}'. "
        "Do NOT repeat the job title verbatim — the headline must add new signal. "
    )


def _prompt_archetype(archetype: str, company: str, jd_facets: Iterable[str], target_role: str = "", mirror_list: list | None = None) -> str:
    facets = list(jd_facets)[:6]
    top_mirrors = (mirror_list or [])[:3]
    return (
        f"Write a resume headline in EXACTLY this format: [Segment A] | [Segment B] | [Segment C]\n"
        "Each segment is 3-5 words. Total 9-15 words across all three segments (pipes not counted).\n"
        f"{_title_clause(target_role)}"
        f"Archetype: '{archetype}'. Target company: {company}.\n"
        f"You MUST use at least one of these exact phrases verbatim in the headline: {top_mirrors}.\n"
        "No filler intensifiers. No generic buzzwords. No job title repetition.\n"
        "Return ONLY the headline text on a single line, with the two pipe characters."
    )


def _prompt_marquee(marquee_outcomes, company: str, target_role: str = "", mirror_list: list | None = None) -> str:
    sample = "; ".join(str(o) for o in marquee_outcomes[:2])
    top_mirrors = (mirror_list or [])[:2]
    return (
        f"Write a resume headline in EXACTLY this format: [Segment A] | [Segment B] | [Segment C]\n"
        "Each segment is 3-5 words. Total 9-15 words across all three segments (pipes not counted).\n"
        f"{_title_clause(target_role)}"
        f"Segment A: one concrete outcome from: {sample}.\n"
        f"Segments B and C: differentiators for {company}. Use one of these exact phrases: {top_mirrors}.\n"
        "No filler, no job title repetition, no generic buzzwords.\n"
        "Return ONLY the headline text on a single line, with the two pipe characters."
    )


def _prompt_pain_point(pain_points, company: str, target_role: str = "", mirror_list: list | None = None) -> str:
    top_pain = str(pain_points[0]) if pain_points else "moving clients from pilot to production"
    top_mirrors = (mirror_list or [])[:2]
    return (
        f"Write a resume headline in EXACTLY this format: [Segment A] | [Segment B] | [Segment C]\n"
        "Each segment is 3-5 words. Total 9-15 words across all three segments (pipes not counted).\n"
        f"{_title_clause(target_role)}"
        f"Frame around this specific pain point: {top_pain[:160]}.\n"
        f"You MUST use at least one of these exact phrases verbatim: {top_mirrors}.\n"
        "No generic buzzwords, no job title repetition, no filler.\n"
        "Return ONLY the headline text on a single line, with the two pipe characters."
    )


__all__ = ["SECTION_ID", "TIER", "generate_headline"]
