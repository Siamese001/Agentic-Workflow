"""JD Planner — L1 semantic planning over Job Description payload.

Extracts planning parameters from a parsed Job Description so L2 HOPs
can execute against typed fields instead of raw strings. Pure — no LLM
calls, no network. Deterministic mapping driven by regex + vocabulary.

Inputs (from pre-L0 intake):
    - jd_path: Path to job_description.json
    - target_company: Captured from prompt [1/3]

Outputs (consumed by L0 routing + L2 execution):
    - target_role: normalized role slug from JD.title
    - seniority_band: {junior, mid, senior, staff, principal, executive}
    - max_pages: 1 (junior/mid) or 2 (senior+)
    - role_family: {engineering, product, sales, executive, ...}
    - ats_keywords: deduped list from JD description

This module belongs to L1 because it performs semantic reasoning over
content (NOT just file-exists admission). Do not move to L0.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

_log = logging.getLogger(__name__)

# Seniority vocabulary — ordered high→low for first-match longest wins
_SENIORITY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(chief|c[eooft]o|ceo|cto|cfo|coo|cio|chro|caio|svp|evp)\b", re.I), "executive"),
    (re.compile(r"\b(vp|vice\s+president|director|head\s+of)\b", re.I), "executive"),
    (re.compile(r"\b(principal|distinguished|fellow)\b", re.I), "principal"),
    (re.compile(r"\b(staff|senior\s+staff|architect)\b", re.I), "staff"),
    (re.compile(r"\b(senior|sr\.?|lead)\b", re.I), "senior"),
    (re.compile(r"\b(mid[-\s]?level|ii|iii)\b", re.I), "mid"),
    (re.compile(r"\b(junior|jr\.?|entry|associate|i\b)\b", re.I), "junior"),
)

_ROLE_FAMILY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(engineer|engineering|developer|architect|sre|devops)\b", re.I), "engineering"),
    (re.compile(r"\b(product\s+manager|product\s+owner|pm|cpo)\b", re.I), "product"),
    (re.compile(r"\b(data\s+scient|ml\s+engineer|ai\s+engineer|machine\s+learning)\b", re.I), "ml"),
    (re.compile(r"\b(sales|account\s+executive|ae|bd|business\s+development)\b", re.I), "sales"),
    (re.compile(r"\b(design|designer|ux|ui)\b", re.I), "design"),
    (re.compile(r"\b(finance|controller|accountant)\b", re.I), "finance"),
    (re.compile(r"\b(consulting|consultant|partner)\b", re.I), "consulting"),
    (re.compile(r"\b(transformation|chief|svp|evp|vp)\b", re.I), "executive"),
)

_MAX_PAGES_BY_SENIORITY: dict[str, int] = {
    "junior": 1,
    "mid": 1,
    "senior": 2,
    "staff": 2,
    "principal": 2,
    "executive": 2,
}

# Stop words for ATS keyword extraction
_ATS_STOPWORDS: frozenset[str] = frozenset(
    "the a an and or but in on at to for of with by from as is are was were "
    "be been being have has had do does did will would could should may "
    "might must shall can you your we our us they them their this that these "
    "those what which who whom whose when where why how all any both each "
    "few more most other some such no nor not only own same so than too very "
    "just about over under after before during between into through".split()
)


@dataclass(frozen=True)
class JDPlan:
    """L1 planning output from parsing a JD.

    Attributes:
        target_role: Raw title string from JD.title (preserved case).
        target_role_slug: Lowercase-underscored form for caching/ids.
        seniority_band: Normalized seniority tier.
        role_family: Normalized role family.
        max_pages: Resume length ceiling (1 for junior/mid, 2 for senior+).
        company: Target company (echoed for symmetry).
        ats_keywords: Deduped keywords extracted from JD description.
        raw_jd: Original parsed dict for downstream consumers.
    """

    target_role: str
    target_role_slug: str
    seniority_band: str
    role_family: str
    max_pages: int
    company: str
    ats_keywords: tuple[str, ...] = field(default_factory=tuple)
    raw_jd: dict = field(default_factory=dict)


def plan_from_jd(jd_path: Path, target_company: str) -> JDPlan:
    """Parse a JD and return the L1 planning output.

    Raises:
        FileNotFoundError: JD file missing (admission should have caught).
        ValueError: JD has no usable title field.
        json.JSONDecodeError: JD is not valid JSON.
    """
    if not jd_path.exists():
        raise FileNotFoundError(f"JD not found: {jd_path}")

    with open(jd_path, encoding="utf-8") as f:
        jd = json.load(f)

    title = str(jd.get("title", "")).strip()
    if not title:
        raise ValueError(f"JD at {jd_path} has no 'title' field — cannot plan")

    description = str(jd.get("description", ""))
    jd_company = str(jd.get("company", "")).strip()
    company = target_company.strip() or jd_company

    seniority = _classify_seniority(title)
    family = _classify_family(title)
    keywords = _extract_ats_keywords(description)

    return JDPlan(
        target_role=title,
        target_role_slug=_slugify(title),
        seniority_band=seniority,
        role_family=family,
        max_pages=_MAX_PAGES_BY_SENIORITY[seniority],
        company=company,
        ats_keywords=keywords,
        raw_jd=jd,
    )


def _classify_seniority(title: str) -> str:
    """Map title → seniority band. First-match wins (patterns ordered high→low)."""
    for pat, band in _SENIORITY_PATTERNS:
        if pat.search(title):
            return band
    return "mid"  # safe default


def _classify_family(title: str) -> str:
    """Map title → role family."""
    for pat, family in _ROLE_FAMILY_PATTERNS:
        if pat.search(title):
            return family
    return "general"


def _slugify(title: str) -> str:
    """Convert 'SVP, Agentic Transformation' → 'svp_agentic_transformation'."""
    s = re.sub(r"[^\w\s-]", "", title.lower())
    s = re.sub(r"[-\s]+", "_", s).strip("_")
    return s[:80]  # cap for path safety


def _extract_ats_keywords(description: str, *, max_keywords: int = 50) -> tuple[str, ...]:
    """Extract deduped 2-3 word n-grams from JD description.

    Simple heuristic — NOT semantic. Real ATS keyword extraction happens
    in L2 via ats_coverage_engine. This is seeding for intent-hashing.
    """
    if not description:
        return ()
    # Normalize and tokenize
    text = re.sub(r"[^\w\s-]", " ", description.lower())
    tokens = [t for t in text.split() if len(t) >= 3 and t not in _ATS_STOPWORDS and not t.isdigit()]

    # Dedupe preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            ordered.append(t)
        if len(ordered) >= max_keywords:
            break
    return tuple(ordered)


def describe_plan(plan: JDPlan) -> str:
    """Human-readable one-line summary for logs and intake banner."""
    return (
        f"role='{plan.target_role}' "
        f"company='{plan.company}' "
        f"seniority={plan.seniority_band} "
        f"family={plan.role_family} "
        f"max_pages={plan.max_pages} "
        f"keywords={len(plan.ats_keywords)}"
    )
