"""Executive-grade competencies rigor checks (deterministic, apps_rg)."""
from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.sections.competencies_certification_contract import (
    check_competencies_no_reserved_certification_category,
    is_credential_competency_term,
)
from apps_rg.runtime.sections.competencies_term_phrase import term_phrase

MIN_CATEGORY_COUNT = 6
MAX_CATEGORY_COUNT = 8
MIN_ITEMS_PER_CATEGORY = 3
MAX_ITEMS_PER_CATEGORY = 6

# Executive / platform narrative alignment (targeting coherence — not JD-as-proof).
ROLE_ALIGNMENT_TERMS: frozenset[str] = frozenset(
    {
        "agentic",
        "platform",
        "orchestration",
        "governance",
        "runtime",
        "retrieval",
        "graphrag",
        "microservices",
        "lakehouse",
        "databricks",
        "evaluation",
        "telemetry",
        "roadmap",
        "commercialization",
        "enterprise",
        "regulatory",
        "basel",
        "ccar",
        "derivatives",
        "hedging",
        "ml",
        "engineering",
        "architecture",
        "infrastructure",
        "cloud",
        "aws",
        "api",
        "vector",
        "policy",
        "sandbox",
        "deterministic",
        "innovation",
        "strategy",
        "leadership",
        "scale",
    }
)

GENERIC_SKILL_WORDS: frozenset[str] = frozenset(
    {
        "team",
        "scaling",
        "data",
        "sales",
        "accounts",
        "revenue",
        "budget",
        "synergy",
        "pipeline",
        "analytics",
        "adoption",
        "optimization",
        "modeling",
        "reporting",
        "delivery",
        "execution",
        "decision",
        "making",
        "enterprise",
        "operations",
        "margin",
        "expansion",
        "gross",
        "margins",
    }
)

CAPABILITY_CONTEXT_WORDS: frozenset[str] = frozenset(
    {
        "engineering",
        "platform",
        "architecture",
        "orchestration",
        "governance",
        "runtime",
        "organization",
        "commercialization",
        "scale-out",
        "scaleout",
        "roadmap",
        "operating",
        "model",
        "system",
        "infrastructure",
        "framework",
        "controls",
        "lifecycle",
        "reliability",
        "evaluation",
        "leadership",
        "delivery",
        "governance",
        "method",
        "discipline",
        "practice",
        "strategy",
        "ip",
        "services",
        "alliance",
        "adoption",
    }
)

_METRICS_ONLY_RE = re.compile(
    r"(?:\bteam\s+scaling\b|"
    r"\bmargin\s+expansion\b|"
    r"\bexpanding\s+gross\s+margins\b|"
    r"\bsynergy\s+modeling\b|"
    r"\bpipeline\s+analytics\b|"
    r"\b\d+\s*%\b|"
    r"\bgross\s+margins\b)",
    re.IGNORECASE,
)


def _flatten_phrases(competencies: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """(category_label, phrase) pairs."""
    out: list[tuple[str, str]] = []
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        label = str(cat.get("category_label") or "").strip()
        for raw in cat.get("terms") or []:
            ph = term_phrase(raw) if isinstance(raw, dict) else str(raw or "").strip()
            if ph:
                out.append((label, ph))
    return out


def check_competencies_category_count(competencies: list[dict[str, Any]]) -> tuple[bool, str | None]:
    n = len(competencies) if isinstance(competencies, list) else 0
    if MIN_CATEGORY_COUNT <= n <= MAX_CATEGORY_COUNT:
        return True, None
    return False, f"category_count={n} required={MIN_CATEGORY_COUNT}-{MAX_CATEGORY_COUNT}"


def check_competencies_min_items_per_category(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    if not isinstance(competencies, list):
        return False, "competencies_not_list"
    for i, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            return False, f"category_{i}_not_object"
        terms = cat.get("terms")
        count = 0
        if isinstance(terms, list):
            for t in terms:
                ph = term_phrase(t) if isinstance(t, dict) else str(t or "").strip()
                if ph:
                    count += 1
        if count < MIN_ITEMS_PER_CATEGORY or count > MAX_ITEMS_PER_CATEGORY:
            label = str(cat.get("category_label") or "?")
            return (
                False,
                f"idx={i} label={label!r} term_count={count} required={MIN_ITEMS_PER_CATEGORY}-{MAX_ITEMS_PER_CATEGORY}",
            )
    return True, None


def check_competencies_no_credential_relisting(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    return check_competencies_no_reserved_certification_category(competencies)


def _is_low_rigor_two_word_phrase(phrase: str) -> bool:
    words = [w.lower() for w in re.findall(r"[a-z][a-z0-9+/-]*", phrase.strip())]
    if len(words) != 2:
        return False
    if all(w in GENERIC_SKILL_WORDS for w in words):
        return True
    return False


def check_competencies_no_low_rigor_two_word_items(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    for label, ph in _flatten_phrases(competencies):
        if _is_low_rigor_two_word_phrase(ph):
            return False, f"low_rigor_two_word label={label!r} phrase={ph!r}"
    return True, None


def check_competencies_role_alignment_terms(
    competencies: list[dict[str, Any]],
    *,
    min_distinct_hits: int = 6,
) -> tuple[bool, str | None]:
    blob = " ".join(ph.lower() for _, ph in _flatten_phrases(competencies))
    hits = {t for t in ROLE_ALIGNMENT_TERMS if t in blob}
    if len(hits) >= min_distinct_hits:
        return True, None
    return False, f"role_alignment_hits={len(hits)} required>={min_distinct_hits} sample={sorted(hits)[:8]}"


def check_competencies_no_metrics_as_skills_without_capability_context(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    for label, ph in _flatten_phrases(competencies):
        if not _METRICS_ONLY_RE.search(ph):
            continue
        low = ph.lower()
        if any(ctx in low for ctx in CAPABILITY_CONTEXT_WORDS):
            continue
        if is_credential_competency_term(ph):
            continue
        return False, f"metrics_as_skill label={label!r} phrase={ph!r}"
    return True, None


def _tokenize_phrase(phrase: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[a-z][a-z0-9+/-]*", phrase.strip())]


def check_competencies_no_all_generic_skill_phrase(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """Reject terms where every token is a banned generic skill scrap word."""
    for label, ph in _flatten_phrases(competencies):
        tokens = _tokenize_phrase(ph)
        if len(tokens) < 2:
            continue
        if tokens and all(t in GENERIC_SKILL_WORDS for t in tokens):
            return False, f"all_generic_tokens label={label!r} phrase={ph!r}"
    return True, None


def check_competencies_approved_category_labels(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    from apps_rg.runtime.sections.competencies_v3_contract import (
        approved_category_labels,
        resolve_approved_category_label,
    )

    approved = approved_category_labels()
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        raw = str(cat.get("category_label") or "").strip()
        resolved = resolve_approved_category_label(raw)
        if not resolved or resolved not in approved:
            return False, f"unapproved_category_label={raw!r}"
    return True, None


def check_competencies_term_support_ids_present(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        for raw in cat.get("terms") or []:
            if not isinstance(raw, dict):
                continue
            phrase = term_phrase(raw)
            if not phrase:
                continue
            sids = [str(x) for x in (raw.get("source_fact_ids") or []) if str(x).strip()]
            skills = [str(x) for x in (raw.get("source_skill_ids") or []) if str(x).strip()]
            if not sids and not skills:
                return False, f"missing_support_ids phrase={phrase!r}"
    return True, None


def check_competencies_no_fragment_or_one_word_terms(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    from apps_rg.runtime.sections.competencies_capability_projection import is_raw_fragment_term

    for label, ph in _flatten_phrases(competencies):
        wc = len(ph.split())
        if wc < 2 and not re.match(r"^[A-Z0-9]{2,}$", ph.strip()):
            return False, f"one_word_or_bare label={label!r} phrase={ph!r}"
        if is_raw_fragment_term(ph):
            return False, f"raw_fragment label={label!r} phrase={ph!r}"
    return True, None


def check_competencies_keyword_repetition_limit(
    competencies: list[dict[str, Any]],
    *,
    max_token_repeat: int = 3,
) -> tuple[bool, str | None]:
    """Stricter than legacy x2_no_keyword_stuffing (was <=5)."""
    freq: dict[str, int] = {}
    for _, ph in _flatten_phrases(competencies):
        for w in _tokenize_phrase(ph):
            if w in GENERIC_SKILL_WORDS or len(w) < 4:
                continue
            freq[w] = freq.get(w, 0) + 1
    if not freq:
        return True, None
    worst = max(freq.items(), key=lambda kv: kv[1])
    if worst[1] > max_token_repeat:
        return False, f"token={worst[0]!r} repeat={worst[1]} max={max_token_repeat}"
    return True, None


__all__ = [
    "MAX_CATEGORY_COUNT",
    "MAX_ITEMS_PER_CATEGORY",
    "MIN_CATEGORY_COUNT",
    "MIN_ITEMS_PER_CATEGORY",
    "ROLE_ALIGNMENT_TERMS",
    "check_competencies_approved_category_labels",
    "check_competencies_category_count",
    "check_competencies_min_items_per_category",
    "check_competencies_no_credential_relisting",
    "check_competencies_no_fragment_or_one_word_terms",
    "check_competencies_no_low_rigor_two_word_items",
    "check_competencies_no_metrics_as_skills_without_capability_context",
    "check_competencies_no_all_generic_skill_phrase",
    "check_competencies_keyword_repetition_limit",
    "check_competencies_role_alignment_terms",
    "check_competencies_term_support_ids_present",
]
