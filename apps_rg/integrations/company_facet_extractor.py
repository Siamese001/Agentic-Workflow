"""HOP-2.6-COMPANY-FACETS — Extract weighted facet vectors from a CompanyBrief.

Produces a dict suitable for the JD-align scoring formula
    score = w_jd × jd_match + w_co × co_match + w_lang × lang_score
with default weights 0.50/0.35/0.15.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P2.3 + P2.4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from apps_rg.types.company_research import CompanyBrief

DEFAULT_WEIGHTS: Dict[str, float] = {"jd": 0.50, "co": 0.35, "lang": 0.15}


@dataclass(frozen=True)
class CompanyFacets:
    company: str
    verticals: List[str] = field(default_factory=list)
    buyer_archetypes: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    engagement_model: List[str] = field(default_factory=list)
    ownership_signal: List[str] = field(default_factory=list)
    differentiation: List[str] = field(default_factory=list)
    language_to_mirror: List[str] = field(default_factory=list)
    language_to_avoid: List[str] = field(default_factory=list)
    alignment_weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))

    def all_terms(self) -> List[str]:
        seen = set()
        out: List[str] = []
        for bucket in (
            self.verticals,
            self.buyer_archetypes,
            self.tech_stack,
            self.engagement_model,
            self.ownership_signal,
            self.differentiation,
            self.language_to_mirror,
        ):
            for term in bucket:
                norm = term.strip().lower()
                if norm and norm not in seen:
                    seen.add(norm)
                    out.append(term.strip())
        return out


def extract_company_facets(
    brief: CompanyBrief,
    *,
    weights: Dict[str, float] | None = None,
) -> CompanyFacets:
    """Pull facet vectors from a CompanyBrief without LLM cost.

    Pure deterministic extraction — fast and reproducible.
    """
    overview = brief.overview
    customer = brief.customer_profile
    engagement = []
    if customer.typical_engagement_size:
        engagement.append(customer.typical_engagement_size)
    if "consulting" in (overview.tagline or "").lower():
        engagement.append("consulting engagement")
    ownership_signal = [overview.ownership] if overview.ownership else []
    if any("partner" in cue.lower() for cue in brief.cultural_cues):
        ownership_signal.append("partnership-led")
    return CompanyFacets(
        company=brief.company,
        verticals=list(customer.verticals),
        buyer_archetypes=list(customer.buyer_titles),
        tech_stack=list(brief.tech_stack_signals),
        engagement_model=engagement,
        ownership_signal=ownership_signal,
        differentiation=list(overview.core_offerings) + list(brief.strategic_priorities),
        language_to_mirror=list(brief.language_to_mirror),
        language_to_avoid=list(brief.language_to_avoid),
        alignment_weights=dict(weights or DEFAULT_WEIGHTS),
    )


def score_text_against_company(
    text: str,
    facets: CompanyFacets,
) -> Dict[str, float]:
    """Compute facet coverage scores for a single bullet/section.

    Returns dict with keys: co_match (0..1), lang_score (0..1), mirror_density (0..1).
    Caller blends with JD score externally.
    """
    if not text:
        return {"co_match": 0.0, "lang_score": 0.0, "mirror_density": 0.0}

    lower = text.lower()
    tokens = [t for t in _tokenize(lower) if t]
    n_tokens = max(1, len(tokens))

    # co_match — fraction of facet groups that have at least one hit.
    groups = [
        facets.verticals,
        facets.buyer_archetypes,
        facets.tech_stack,
        facets.engagement_model,
        facets.differentiation,
    ]
    hits = 0
    for group in groups:
        if any(_term_present(term, lower) for term in group):
            hits += 1
    co_match = hits / max(1, len([g for g in groups if g]))

    # lang_score — fraction of language_to_mirror terms that appear.
    if facets.language_to_mirror:
        present = sum(1 for term in facets.language_to_mirror if _term_present(term, lower))
        lang_score = present / len(facets.language_to_mirror)
    else:
        lang_score = 0.0

    # mirror_density — combined (mirror) term tokens divided by total tokens.
    mirror_terms = facets.language_to_mirror + facets.differentiation
    mirror_tokens = 0
    for term in mirror_terms:
        if _term_present(term, lower):
            mirror_tokens += len(_tokenize(term.lower()))
    mirror_density = min(1.0, mirror_tokens / n_tokens)

    return {
        "co_match": round(co_match, 4),
        "lang_score": round(lang_score, 4),
        "mirror_density": round(mirror_density, 4),
    }


def _term_present(term: str, lower_text: str) -> bool:
    if not term:
        return False
    return term.strip().lower() in lower_text


def _tokenize(text: str) -> List[str]:
    out: List[str] = []
    word: List[str] = []
    for ch in text:
        if ch.isalnum() or ch in {"-", "_"}:
            word.append(ch)
        else:
            if word:
                out.append("".join(word))
                word = []
    if word:
        out.append("".join(word))
    return out


__all__ = [
    "CompanyFacets",
    "DEFAULT_WEIGHTS",
    "extract_company_facets",
    "score_text_against_company",
]
