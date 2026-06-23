"""Executive-grade competencies rigor checks (deterministic, apps_rg)."""
from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.sections.competencies_certification_contract import (
    check_competencies_no_reserved_certification_category,
    is_credential_competency_term,
)
from apps_rg.runtime.sections.competencies_term_phrase import term_phrase

MIN_CATEGORY_COUNT = 8
MAX_CATEGORY_COUNT = 8
# Variance-class alignment (2026-06): the graph pool now exposes the exact final
# category set. Selection rigor (min_score 0.72 + per-category graph_skill_node_ids
# X2 gate) is unchanged.
CANDIDATE_CATEGORY_COUNT = 8
# Floor raised 2->3 (plan apps-rg-aig-remaining-lanes-closeout-d4e1f7 W2): the generic-category
# graph-terms gate (GENERIC_CATEGORY_MIN_GRAPH_TERMS=3) requires >=3 graph-backed terms per generic
# category, but a floor of 2 let the prompt request "2-6 terms", so the model emitted exactly 2
# (both graph-backed) and failed x2_competencies_generic_category_blocked_without_graph. Aligning the
# floor to 3 makes the prompt request 3-6 terms; this TIGHTENS the gate, never weakens it.
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

_METRIC_VALUE_TERM_RE = re.compile(
    r"(?:\bteam\s+scaling\b|"
    r"\bmargin\s+expansion\b|"
    r"\boperating\s+margin\b|"
    r"\brevenue\s+growth\b|"
    r"\bexpanding\s+gross\s+margins\b|"
    r"\bsynergy\s+modeling\b|"
    r"\bpipeline\s+analytics\b|"
    r"(?<!\w)\d+\s*%(?!\w)|"
    r"\$\s*\d+|"
    r"\b\d+(?:\.\d+)?\s*(?:m|mm|b|bn|k)\b|"
    r"\bgross\s+margins\b)",
    re.IGNORECASE,
)
_METRICS_ONLY_RE = _METRIC_VALUE_TERM_RE

_MUNDANE_VISIBLE_COMPETENCY_PHRASES: frozenset[str] = frozenset(
    {
        "audit-grade observability",
        "cloud architecture",
        "cloud partner ecosystem gtm",
        "cloud-native data engineering",
        "delivery governance",
        "enterprise adoption",
        "hyperscaler alliance co-sell",
        "hyperscaler co-sell",
        "joint revenue execution",
        "joint solution development",
        "multi-agent orchestration",
        "operating model design",
        "partner enablement",
        "platform commercialization",
        "regulated reference architecture",
        "runtime policy controls",
        "stakeholder alignment",
    }
)

_SVP_AGENTIC_MECHANISM_TOKENS: frozenset[str] = frozenset(
    {
        "agent",
        "agentic",
        "ai",
        "applied",
        "architecture",
        "assembly",
        "audit-grade",
        "cloud-native",
        "co-sellable",
        "commercialization",
        "context",
        "control",
        "decision",
        "dense-sparse",
        "engineering",
        "evaluation",
        "evaluation-ready",
        "execution",
        "fail-closed",
        "graphrag",
        "governance",
        "governed",
        "hyperscaler",
        "lakehouse",
        "microservices",
        "operating",
        "orchestration",
        "policy",
        "policy-bound",
        "prompt",
        "relationship-aware",
        "reliability",
        "retrieval",
        "runtime",
        "sandboxed",
        "telemetry",
        "workflow",
        "workflows",
    }
)

_SVP_EXECUTION_CONTEXT_TOKENS: frozenset[str] = frozenset(
    {
        "adoption",
        "alliance",
        "agents",
        "architectures",
        "assurance",
        "behavior",
        "buyers",
        "cadences",
        "design",
        "ecosystems",
        "enterprise",
        "executive",
        "executive-aligned",
        "factory",
        "gate",
        "intelligence",
        "motions",
        "partners",
        "paths",
        "planes",
        "pipelines",
        "platform",
        "prototype",
        "ranking",
        "reference",
        "regulated",
        "scale",
        "scale-out",
        "systems",
        "trails",
        "workflows",
    }
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
        if not _METRIC_VALUE_TERM_RE.search(ph):
            continue
        if is_credential_competency_term(ph):
            continue
        return False, f"metric_value_as_competency label={label!r} phrase={ph!r}"
    return True, None


def _tokenize_phrase(phrase: str) -> list[str]:
    return re.findall(r"[a-z][a-z0-9+/-]*", phrase.strip().lower())


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


def check_competencies_no_metric_ids_in_source_fact_ids(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        label = str(cat.get("category_label") or "").strip()
        for raw in cat.get("source_fact_ids") or []:
            fid = str(raw).strip()
            if fid.startswith("metric_"):
                return False, f"metric_id_in_category_source_fact_ids label={label!r} id={fid!r}"
        for term in cat.get("terms") or []:
            if not isinstance(term, dict):
                continue
            phrase = term_phrase(term)
            raw_ids = list(term.get("source_fact_ids") or [])
            if term.get("source_fact_id") is not None:
                raw_ids.append(term.get("source_fact_id"))
            for raw in raw_ids:
                fid = str(raw).strip()
                if fid.startswith("metric_"):
                    return False, f"metric_id_in_term_source_fact_ids label={label!r} phrase={phrase!r} id={fid!r}"
    return True, None


def check_competencies_visible_terms_svp_agentic_richness(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """Visible graph-surface terms must be specific, believable SVP/agentic capability phrases."""
    if not isinstance(competencies, list):
        return True, None
    visible = [cat for cat in competencies if isinstance(cat, dict) and cat.get("visible_graph_surface") is True]
    if not visible:
        return True, None
    for cat in visible:
        label = str(cat.get("resume_display_label") or cat.get("category_label") or "").strip()
        for raw in cat.get("terms") or []:
            phrase = term_phrase(raw) if isinstance(raw, dict) else str(raw or "").strip()
            if not phrase:
                continue
            normalized = re.sub(r"\s+", " ", phrase.strip().lower())
            if normalized in _MUNDANE_VISIBLE_COMPETENCY_PHRASES:
                return False, f"mundane_visible_competency label={label!r} phrase={phrase!r}"
            if len(phrase.split()) < 5:
                return False, f"visible_competency_too_short_for_svp_signal label={label!r} phrase={phrase!r}"
            tokens = set(_tokenize_phrase(phrase))
            mechanism_hits = sorted(tokens & _SVP_AGENTIC_MECHANISM_TOKENS)
            context_hits = sorted(tokens & _SVP_EXECUTION_CONTEXT_TOKENS)
            if not mechanism_hits:
                return False, f"visible_competency_missing_agentic_mechanism label={label!r} phrase={phrase!r}"
            if not context_hits:
                return False, f"visible_competency_missing_svp_execution_context label={label!r} phrase={phrase!r}"
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
    "CANDIDATE_CATEGORY_COUNT",
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
    "check_competencies_no_metric_ids_in_source_fact_ids",
    "check_competencies_no_all_generic_skill_phrase",
    "check_competencies_visible_terms_svp_agentic_richness",
    "check_competencies_keyword_repetition_limit",
    "check_competencies_role_alignment_terms",
    "check_competencies_term_support_ids_present",
]
