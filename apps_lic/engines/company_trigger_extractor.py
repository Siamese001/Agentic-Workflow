"""Company-trigger extractor for HOP2 research artifacts.

W2-P4 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Pure-function surface that scans an evidence_pack (list of research
artifact dicts emitted by ``HOP2ResearchAgent``) and produces a ranked
list of ``CompanyTrigger`` instances. Each trigger includes the raw
excerpt so HOP5 can compose opener lines like:

    "Noticed {company}'s {observation}" -> "Noticed Acme's Series C raise"

Rules are keyword-driven, not LLM-based, so extraction is deterministic
and cheap. Trigger strength is upgraded when a keyword co-occurs with a
quantifier (dollar amount, percentage, date within 30 days). This keeps
extraction explainable and unit-testable.
"""

from __future__ import annotations

import re
from typing import Final, Iterable, Mapping, Tuple

from apps_lic.types.outreach_trigger_types import (
    STRENGTH_BANDS,
    CompanyTrigger,
)

# ----------------------------------------------------------------------
# Keyword + quantifier regex table. Each trigger_type maps to a tuple of
# (regex_pattern, human_readable_keyword). Patterns are case-insensitive
# when applied via ``re.search(pattern, text, re.IGNORECASE)``.
# ----------------------------------------------------------------------
_TRIGGER_RULES: Final[Mapping[str, Tuple[Tuple[str, str], ...]]] = {
    "funding_round": (
        (r"\bseries\s+[A-K](?:\s+(?:round|funding|raise))?\b", "Series round"),
        (r"\braise[ds]?\b.{0,40}\$[0-9]+", "raised capital"),
        (r"\bIPO\b", "IPO"),
        (r"\bseed\s+(?:round|funding)\b", "seed round"),
    ),
    "leadership": (
        (r"\b(?:appoint|hire|announce)[a-z]*\s+.{0,40}\b(?:CEO|CFO|COO|CTO|CIO|CRO|Chief)\b", "leadership appointment"),
        (r"\bnew\s+(?:CEO|CFO|COO|CTO|CIO|CRO)\b", "new executive"),
        (r"\b(?:CEO|CFO|COO|CTO) transition\b", "executive transition"),
    ),
    "product_launch": (
        (r"\b(?:launche[sd]?|release[sd]?|unveil[sed]*)\s+.{0,40}(?:product|platform|feature|app)\b", "product launch"),
        (r"\bgeneral availability\b", "GA release"),
        (r"\bpublic beta\b", "public beta"),
    ),
    "earnings": (
        (r"\b(?:Q[1-4]|quarterly)\s+(?:earnings|results|revenue)\b", "quarterly earnings"),
        (r"\bbeat\s+(?:estimates|consensus|expectations)\b", "earnings beat"),
        (r"\bguidance\s+(?:raised?|lowered?|updated?)\b", "guidance change"),
    ),
    "acquisition": (
        (r"\bacqui(?:red|sition|res)\b", "acquisition"),
        (r"\bmerge[rd]?\s+with\b", "merger"),
    ),
    "expansion": (
        (r"\bexpand(?:ed|ing|s)?\s+(?:into|to)\b.{0,30}\b(?:market|region|europe|asia|apac|emea|latam)\b", "market expansion"),
        (r"\bnew\s+(?:office|headquarters|HQ)\b", "new office"),
    ),
    "award": (
        (r"\b(?:named|ranked|included)\s+(?:on|in)\s+.{0,40}\b(?:top|best)\s+\d+\b", "top-N list"),
        (r"\baward(?:ed|s)?\b", "award"),
        (r"\brecogni[sz]ed\s+(?:as|for)\b", "recognition"),
    ),
}

# Quantifier patterns that upgrade a match from weak→moderate→strong.
# Dollar amounts, percentages, named sources, and recent-date anchors.
_DOLLAR_RE: Final[re.Pattern[str]] = re.compile(r"\$[0-9][0-9,.]*\s*(?:M|B|K|million|billion|thousand)?", re.IGNORECASE)
_PERCENT_RE: Final[re.Pattern[str]] = re.compile(r"\b[0-9]+(?:\.[0-9]+)?\s*%")
_QUOTE_RE: Final[re.Pattern[str]] = re.compile(r'["\u201c][^"\u201d]{5,}["\u201d]')
_RECENT_DATE_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:this week|last week|today|yesterday|this month|Q[1-4]\s*20[2-3][0-9])\b",
    re.IGNORECASE,
)

# Excerpt window around the match (before + after chars).
_EXCERPT_BEFORE: Final[int] = 80
_EXCERPT_AFTER: Final[int] = 160
_EXCERPT_MAX: Final[int] = 240


def extract_triggers(
    evidence_pack: Iterable[Mapping[str, object]],
) -> list[CompanyTrigger]:
    """Scan an evidence_pack and extract structured triggers.

    Args:
        evidence_pack: Sequence of artifact dicts, each expected to have
            keys ``artifact_id`` (str) and ``summary`` (str). Missing or
            non-string values are tolerated — the artifact is silently
            skipped rather than raising.

    Returns:
        List of ``CompanyTrigger`` sorted by (strength desc,
        trigger_type asc). Empty list when no triggers match — never
        raises.
    """
    results: list[CompanyTrigger] = []
    for artifact in evidence_pack:
        summary = artifact.get("summary", "") if isinstance(artifact, Mapping) else ""
        if not isinstance(summary, str) or not summary.strip():
            continue
        source_id = str(artifact.get("artifact_id", ""))
        for trigger in _extract_from_text(summary, source_id):
            results.append(trigger)
    results.sort(key=_sort_key)
    return results


def extract_best_trigger(
    evidence_pack: Iterable[Mapping[str, object]],
) -> CompanyTrigger | None:
    """Convenience: return the single highest-strength trigger or None.

    This is the shape HOP5 actually consumes when composing the opener
    line — a single trigger with maximum signal.
    """
    triggers = extract_triggers(evidence_pack)
    return triggers[0] if triggers else None


# ----------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------


def _extract_from_text(text: str, source_id: str) -> list[CompanyTrigger]:
    """Apply every rule to one text blob. Returns all matches."""
    matches: list[CompanyTrigger] = []
    for trigger_type, rules in _TRIGGER_RULES.items():
        for pattern, keyword_label in rules:
            m = re.search(pattern, text, re.IGNORECASE)
            if m is None:
                continue
            excerpt = _build_excerpt(text, m.start(), m.end())
            strength = _score_strength(excerpt)
            matches.append(
                CompanyTrigger(
                    trigger_type=trigger_type,
                    raw_excerpt=excerpt,
                    strength=strength,
                    source_id=source_id,
                    matched_keyword=keyword_label,
                )
            )
    return matches


def _build_excerpt(text: str, start: int, end: int) -> str:
    """Return up to _EXCERPT_MAX chars of context around the match."""
    lo = max(0, start - _EXCERPT_BEFORE)
    hi = min(len(text), end + _EXCERPT_AFTER)
    excerpt = text[lo:hi].strip()
    if len(excerpt) > _EXCERPT_MAX:
        excerpt = excerpt[: _EXCERPT_MAX - 1].rstrip() + "\u2026"
    return excerpt


def _score_strength(excerpt: str) -> str:
    """Promote a match from weak→moderate→strong based on quantifiers."""
    score = 0
    if _DOLLAR_RE.search(excerpt):
        score += 2
    if _PERCENT_RE.search(excerpt):
        score += 1
    if _QUOTE_RE.search(excerpt):
        score += 1
    if _RECENT_DATE_RE.search(excerpt):
        score += 1
    if score >= 3:
        return "strong"
    if score >= 1:
        return "moderate"
    return "weak"


_STRENGTH_ORDER: Final[Mapping[str, int]] = {s: i for i, s in enumerate(STRENGTH_BANDS)}


def _sort_key(trigger: CompanyTrigger) -> tuple[int, str]:
    """Strong first, then alphabetical by trigger_type for determinism."""
    return (_STRENGTH_ORDER.get(trigger.strength, 99), trigger.trigger_type)


__all__ = [
    "extract_best_trigger",
    "extract_triggers",
]
