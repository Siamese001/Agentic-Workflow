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
    prompt_variants = [
        ("lead_with_archetype", _prompt_archetype(archetype, company, jd_facets, target_role)),
        ("marquee", _prompt_marquee(list(marquee_outcomes), company, target_role)),
        ("pain_point", _prompt_pain_point(list(pain_points), company, target_role)),
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
    if target_role:
        return f"{target_role} | {archetype} scaling enterprise AI for {company}"[:140]
    return f"{archetype} | scaled enterprise AI delivery for {company}"[:140]


def _title_clause(target_role: str) -> str:
    if not target_role.strip():
        return ""
    return (
        f"The headline MUST contain the exact target role '{target_role.strip()}' "
        "(or its close variant) as the opening phrase. "
    )


def _prompt_archetype(archetype: str, company: str, jd_facets: Iterable[str], target_role: str = "") -> str:
    return (
        f"Write a 9-14 word resume headline (fits one line). "
        f"{_title_clause(target_role)}"
        f"Lead with the archetype '{archetype}' for a candidate targeting {company}. "
        "No filler intensifiers. "
        f"Mirror at most 2 JD facets from: {list(jd_facets)[:10]}. "
        "MUST be 9-14 words total. Return only the headline on a single line."
    )


def _prompt_marquee(marquee_outcomes, company: str, target_role: str = "") -> str:
    sample = "; ".join(str(o) for o in marquee_outcomes[:3])
    return (
        f"Write a 9-14 word resume headline (fits one line). "
        f"{_title_clause(target_role)}"
        f"Feature one specific outcome from: {sample}. "
        f"Position the candidate for {company}. No filler. "
        "MUST be 9-14 words total. Return only the headline on a single line."
    )


def _prompt_pain_point(pain_points, company: str, target_role: str = "") -> str:
    sample = "; ".join(str(p) for p in pain_points[:3])
    return (
        f"Write a 9-14 word resume headline (fits one line). "
        f"{_title_clause(target_role)}"
        f"Frame the candidate as the answer to a specific pain point from: {sample}. "
        f"For {company}. No filler. "
        "MUST be 9-14 words total. Return only the headline on a single line."
    )


__all__ = ["SECTION_ID", "TIER", "generate_headline"]
