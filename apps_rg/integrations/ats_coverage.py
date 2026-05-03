"""ATS Keyword Coverage + Title Match — resume-level diagnostic + title guarantee.

These functions run AFTER all per-section HOPs complete, over the full
assembled resume. They provide:

  1. ATS keyword coverage DIAGNOSTIC: reports what fraction of the JD's
     `must_have` terms appear in the authentic narrative sections. This
     is informational — it surfaces gaps so the user can decide whether
     to revise bullets or accept the coverage. NO new resume section is
     created; NO text is injected into narrative sections.

  2. Title match: the headline MUST contain the exact JD target-role
     string (or a close variant). ATS title-matching scorers weight this
     heavily. The headline is an APPROVED section — prepending the
     target title into it is an in-place edit of an existing field, not
     a new section.

Authenticity guardrail (user directive 2026-05-01):
  - No new resume sections are ever added.
  - No keyword injection into any field. Coverage is achieved purely
    through authentic narrative content (bullets, summary, competencies,
    headline) produced by the HOPs.
  - The only mutation this module performs is prepending the JD target
    title to the `headline` field when absent — and only to the headline.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md
(ATS hardening extension, 2026-05-01).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

_log = logging.getLogger(__name__)


# Threshold below which we inject missing terms rather than blocking.
DEFAULT_COVERAGE_FLOOR = 0.70  # 70% of JD must_have terms must appear


@dataclass
class ATSCoverageResult:
    must_have_total: int
    must_have_covered: int
    missing: List[str]
    coverage: float
    passed: bool

    def as_dict(self) -> dict:
        return {
            "must_have_total": self.must_have_total,
            "must_have_covered": self.must_have_covered,
            "missing": self.missing,
            "coverage": round(self.coverage, 4),
            "passed": self.passed,
        }


def _word_re(term: str) -> re.Pattern:
    escaped = re.escape(term.strip())
    return re.compile(rf"(?<![\w-]){escaped}(?![\w-])", re.IGNORECASE)


def _tokenize_sections(resume_data: Dict) -> str:
    """Flatten the resume to one searchable text blob for coverage scoring."""
    parts: List[str] = []

    def _add(v):
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                _add(item)
        elif isinstance(v, dict):
            for vv in v.values():
                _add(vv)

    for key in (
        "headline",
        "executive_summary",
        "summary",
        "competencies",
        "core_competencies",
        "engineering_and_platform_competencies",
        "strategic_and_technical_competencies",
        "skills",
        "ats_keywords",
        "marquee_outcomes",
        "professional_experience",
        "experience",
        "roles",
        "early_career",
        "certifications_and_credentials",
        "education",
    ):
        if key in resume_data:
            _add(resume_data[key])
    return "\n".join(str(p) for p in parts)


def compute_ats_coverage(
    resume_data: Dict,
    *,
    must_have: Iterable[str],
    floor: float = DEFAULT_COVERAGE_FLOOR,
) -> ATSCoverageResult:
    """Compute the fraction of JD must_have terms present anywhere in resume."""
    terms = [t.strip() for t in must_have if t and t.strip()]
    if not terms:
        return ATSCoverageResult(0, 0, [], 1.0, True)

    blob = _tokenize_sections(resume_data)
    covered: List[str] = []
    missing: List[str] = []
    for term in terms:
        if _word_re(term).search(blob):
            covered.append(term)
        else:
            missing.append(term)

    coverage = len(covered) / len(terms)
    passed = coverage >= floor
    return ATSCoverageResult(
        must_have_total=len(terms),
        must_have_covered=len(covered),
        missing=missing,
        coverage=coverage,
        passed=passed,
    )


# NOTE: a previous revision of this module exposed
# `inject_missing_keywords_into_ats_block()` which appended missing JD terms
# into a dedicated `ats_keywords` list rendered as "Additional Skills" in
# the DOCX. That helper was REMOVED per user directive 2026-05-01 — the
# approved resume sections are fixed, and no keyword padding may be added.
# If you're looking for that function: don't reintroduce it. Improve
# organic coverage upstream in the HOPs instead.


# ----------------------------------------------------------------- title-match


_TITLE_NORM = re.compile(r"[^a-z0-9]+")


def _normalize_title(s: str) -> str:
    return _TITLE_NORM.sub(" ", (s or "").lower()).strip()


def headline_contains_title(headline: str, target_title: str) -> bool:
    """True if headline contains target_title (loose word-order match)."""
    if not target_title:
        return True
    norm_h = _normalize_title(headline)
    norm_t = _normalize_title(target_title)
    if not norm_t:
        return True
    # Exact substring first.
    if norm_t in norm_h:
        return True
    # All tokens present (allows reordering): 'SVP, Agentic Transformation'
    # matches 'Agentic Transformation SVP'.
    #
    # P6.1 investigation (2026-05-03): Kept _SENIORITY_SKIP after runtime
    # discovery that `owner.headline` is STATIC in apps_shared/data/master_resume.json
    # (not LLM-generated). Removing the skip caused ensure_title_in_headline to
    # forcibly prepend target_title when candidate's static brand didn't include
    # the exact target domain word (e.g. "SVP Engineering" vs "SVP, Agentic
    # Transformation"). The proper fix requires wiring the headline_ensemble
    # HOP-4A-HEADLINE into the pipeline (currently absent from pipeline
    # checkpoints). See docs/reports for W10/P6.1 investigation findings.
    _SENIORITY_SKIP = {"svp", "evp", "vp", "md", "gm", "cto", "ceo", "coo", "caio", "cdo", "ciso"}
    title_tokens = [t for t in norm_t.split() if len(t) > 3 and t not in _SENIORITY_SKIP]
    if not title_tokens:
        return True
    return all(tok in norm_h for tok in title_tokens)


def ensure_title_in_headline(
    resume_data: Dict,
    *,
    target_title: str,
    prefix_style: str = "prefix",
) -> Tuple[str, bool]:
    """Guarantee the headline contains the JD target-role title.

    Returns (new_headline, was_modified). Does NOT touch the headline if
    it already contains the title (loose match).
    """
    headline = (resume_data.get("headline") or "").strip()
    if not target_title.strip():
        return headline, False
    if headline_contains_title(headline, target_title):
        return headline, False

    clean_title = target_title.strip().strip(",")
    if not headline:
        new = clean_title
    elif prefix_style == "prefix":
        new = f"{clean_title} — {headline}"
    else:
        new = f"{headline} | {clean_title}"
    resume_data["headline"] = new
    _log.info("[ats_coverage] headline modified to include target title: %s", clean_title)
    return new, True


# ----------------------------------------------------------------- combined


def apply_ats_hardening(
    resume_data: Dict,
    *,
    jd_must_have: Iterable[str],
    target_title: str = "",
    coverage_floor: float = DEFAULT_COVERAGE_FLOOR,
) -> Dict:
    """Apply title-match guarantee + compute ATS coverage diagnostic.

    The ONLY in-place edit this function performs is prepending the JD
    target title to the `headline` field when absent. No new sections are
    added, no text is injected into any other field. Missing JD terms are
    surfaced in the returned coverage_result for scorecard visibility —
    the user / upstream HOPs can decide whether to revise narrative
    sections to improve organic coverage.

    Returns a dict with:
      - title_modified: bool — whether the headline was rewritten
      - headline_after: str — the resulting headline
      - keywords_injected: always False (policy lock — authenticity)
      - coverage_result: dict — coverage, missing terms, pass/fail vs floor
    """
    new_headline, title_modified = ensure_title_in_headline(
        resume_data, target_title=target_title
    )
    # Coverage is computed AFTER the title-match edit so the title's own
    # tokens count toward must-have coverage. No injection happens — if
    # coverage is below the floor, the user sees the missing terms in the
    # scorecard and can revise narrative sections upstream.
    coverage = compute_ats_coverage(
        resume_data, must_have=jd_must_have, floor=coverage_floor
    )
    return {
        "title_modified": title_modified,
        "headline_after": new_headline,
        "keywords_injected": False,  # policy: never inject — authenticity
        "coverage_result": coverage.as_dict(),
    }


__all__ = [
    "ATSCoverageResult",
    "DEFAULT_COVERAGE_FLOOR",
    "apply_ats_hardening",
    "compute_ats_coverage",
    "ensure_title_in_headline",
    "headline_contains_title",
]
