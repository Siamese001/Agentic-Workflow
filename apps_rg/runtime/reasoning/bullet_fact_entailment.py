"""Selection-time numeric fact-entailment (W4.3, G15/G17) — deterministic, zero LLM calls.

A pool candidate can cite the correct ``source_fact_id`` while claiming a numeric
magnitude (e.g. "$10M ARR") absent from that fact. The id-level validity filter
(``_selector_valid_bullet_paths``) cannot see this — the drift historically surfaced only
at the X1D judge / X2 wall, after the Claude selector had already merged the candidate.
This module compares each bullet's NUMERIC TOKENS against a per-slot evidence corpus and
lets the selector exclude non-entailed candidates BEFORE pool formatting.

Corpus provenance: strictly ``runtime_payload["selected_fact_plan"]`` (C0-pool facts via
``load_section_proof_for_lane`` — NOT base-resume ``extract_*_employment`` rows) plus the
slot's role-episode-bundle NON-metric text.

Shared-bundle metric-leak restriction (closeout2 evidence): ibm slots bul_ibm_001-003
share ``reb_ibm_technical_presales_gtm``, whose ``linked_metric_outcome_ids``
carry "$10M ARR"-class tokens. Including those bundle metric
fields in every sharing slot's corpus would entail cross-slot metric drift — the exact
failure this filter exists to stop. Metric-magnitude authority is therefore restricted to
the slot's OWN fact ``claim_text`` + ``metric_raw``; bundle text contributes only the
non-metric fields (title, time_window, operating_context, bullet_intent, scope signals).
Unify needs no equivalent: ``UNIFY_BULLET_SLOT_BUNDLE_MAP`` binds a distinct bundle per
slot (regression-tested).

Exclusion only — bullet text is never rewritten. Fail-open per slot when the corpus is
missing (recorded in the receipt). Kill-switch: ``APPS_RG_SELECTOR_FACT_ENTAILMENT_BYPASS=1``.
"""

from __future__ import annotations

import re
from typing import Any

ENTAILMENT_BYPASS_ENV = "APPS_RG_SELECTOR_FACT_ENTAILMENT_BYPASS"
ENTAILMENT_RECEIPT_FILENAME = "bullet_pool_fact_entailment.json"
ENTAILMENT_REJECTION_REASON = "numeric_token_not_entailed"
CORPUS_SOURCE_LABEL = "selected_fact_plan_c0_pool_facts_plus_bundle_non_metric_text"

# Plain integers below this are list ordinals / small counts, not metric claims.
_MIN_BARE_NUMBER = 10

# Ordered alternation: currency first so "$10M" is never re-tokenized as bare "10".
_NUMERIC_TOKEN_RE = re.compile(
    r"""
    (?P<currency>\$\s*\d[\d,]*(?:\.\d+)?(?:\s*(?:mm|million|billion|thousand|bn|k|m|b)\b)?)
    | (?P<percent>\d[\d,]*(?:\.\d+)?\s*(?:%|percent\b))
    | (?P<multiplier>\d+(?:\.\d+)?\s*x\b)
    | (?P<worded>\d[\d,]*(?:\.\d+)?\s+(?:million|billion|thousand)\b)
    | (?P<bare>\d[\d,]*(?:\.\d+)?)
    """,
    re.IGNORECASE | re.VERBOSE,
)

_NORMALIZE_RE = re.compile(
    r"^\$?\s*(?P<num>\d[\d,]*(?:\.\d+)?)\s*(?P<suffix>mm|million|billion|thousand|bn|k|m|b|%|percent|x)?$",
    re.IGNORECASE,
)

_SCALE_SUFFIXES = {
    "k": 1_000.0,
    "thousand": 1_000.0,
    "m": 1_000_000.0,
    "mm": 1_000_000.0,
    "million": 1_000_000.0,
    "b": 1_000_000_000.0,
    "bn": 1_000_000_000.0,
    "billion": 1_000_000_000.0,
}

# Bundle fields admitted into the slot corpus. Deliberately EXCLUDES the metric-bearing
# fields (linked_metric_outcome_ids, held_metrics, excluded_metrics,
# notes) — see shared-bundle metric-leak restriction in the module docstring.
_BUNDLE_NON_METRIC_TEXT_FIELDS = ("title", "time_window", "operating_context", "bullet_intent")
_BUNDLE_NON_METRIC_LIST_FIELDS = ("executive_scope_signals", "architecture_scope_signals")


def extract_numeric_tokens(text: str) -> list[str]:
    """Extract metric-bearing numeric tokens (currency, percent, multiplier, worded scale,
    bare integers >= 10) from ``text`` in document order."""
    tokens: list[str] = []
    for match in _NUMERIC_TOKEN_RE.finditer(str(text or "")):
        raw = match.group(0).strip()
        if match.lastgroup == "bare":
            try:
                value = float(raw.replace(",", ""))
            except ValueError:
                continue
            if value < _MIN_BARE_NUMBER:
                continue
        tokens.append(raw)
    return tokens


def normalize_numeric_token(token: str) -> tuple[str, str] | None:
    """Normalize a numeric token to ``(magnitude, unit)``.

    Units: ``usd`` (currency), ``pct`` (percent), ``x`` (multiplier), ``count`` (other).
    "$10M", "$10,000,000", and "10 million" all normalize to magnitude "10000000".
    """
    s = str(token or "").strip().lower()
    if not s:
        return None
    is_usd = s.startswith("$")
    m = _NORMALIZE_RE.match(s)
    if m is None:
        return None
    try:
        value = float(m.group("num").replace(",", ""))
    except ValueError:
        return None
    suffix = (m.group("suffix") or "").lower()
    unit = "usd" if is_usd else "count"
    if suffix in ("%", "percent"):
        unit = "pct" if not is_usd else unit
    elif suffix == "x" and not is_usd:
        unit = "x"
    if suffix in _SCALE_SUFFIXES:
        value *= _SCALE_SUFFIXES[suffix]
    if value == int(value):
        magnitude = str(int(value))
    else:
        magnitude = str(round(value, 6))
    return magnitude, unit


def _entailment_units_compatible(bullet_unit: str, corpus_unit: str) -> bool:
    """pct<->pct, x<->x, usd<->usd-or-count, count<->any (intentional under-exclusion)."""
    if bullet_unit == "pct":
        return corpus_unit == "pct"
    if bullet_unit == "x":
        return corpus_unit == "x"
    if bullet_unit == "usd":
        return corpus_unit in ("usd", "count")
    return True


def _normalized_token_set(text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for raw in extract_numeric_tokens(text):
        norm = normalize_numeric_token(raw)
        if norm is not None and norm not in out:
            out.append(norm)
    return out


def numeric_entailment_check(bullet_text: str, corpus_text: str) -> tuple[bool, list[str]]:
    """Return ``(entailed, missing_tokens)`` for ``bullet_text`` against ``corpus_text``.

    Entailed when every numeric token in the bullet matches a corpus token with the same
    magnitude and a compatible unit. A bullet with no numeric tokens is entailed.
    """
    corpus_norms = _normalized_token_set(corpus_text)
    missing: list[str] = []
    for raw in extract_numeric_tokens(bullet_text):
        norm = normalize_numeric_token(raw)
        if norm is None:
            continue
        magnitude, unit = norm
        entailed = any(
            magnitude == c_mag and _entailment_units_compatible(unit, c_unit)
            for c_mag, c_unit in corpus_norms
        )
        if not entailed and raw not in missing:
            missing.append(raw)
    return (not missing, missing)


def _slot_bundle_lookup_for_lane(section_lane: str) -> tuple[dict[str, str], Any]:
    """Lazy per-lane (slot->bundle map, get_bundle_by_id) — empty map for other lanes."""
    lane = str(section_lane or "").strip().lower()
    if lane == "unify_bullets":
        from apps_rg.runtime.sections.unify_graph_role_episode_registry import get_bundle_by_id
        from apps_rg.runtime.sections.unify_role_episode_evidence import (
            UNIFY_BULLET_SLOT_BUNDLE_MAP,
        )

        return dict(UNIFY_BULLET_SLOT_BUNDLE_MAP), get_bundle_by_id
    if lane == "ibm_bullets":
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import get_bundle_by_id
        from apps_rg.runtime.sections.ibm_role_episode_evidence import (
            IBM_BULLET_SLOT_BUNDLE_MAP,
        )

        return dict(IBM_BULLET_SLOT_BUNDLE_MAP), get_bundle_by_id
    return {}, None


def _bundle_non_metric_text(bundle: dict[str, Any]) -> str:
    parts: list[str] = []
    for field in _BUNDLE_NON_METRIC_TEXT_FIELDS:
        value = str(bundle.get(field) or "").strip()
        if value:
            parts.append(value)
    for field in _BUNDLE_NON_METRIC_LIST_FIELDS:
        for entry in bundle.get(field) or []:
            value = str(entry or "").strip()
            if value:
                parts.append(value)
    return " ".join(parts)


def build_slot_entailment_corpus(
    section_lane: str,
    selected_fact_plan: dict[str, Any] | None,
) -> dict[str, str]:
    """Per-slot entailment corpus keyed by ``fact_id`` (== bullet slot id).

    Corpus per slot = the slot's OWN plan fact ``claim_text`` + ``metric_raw`` (the only
    metric-magnitude authority) + the slot's bundle non-metric text. Returns ``{}`` when
    the plan is absent/malformed (downstream filter fails open).
    """
    plan = selected_fact_plan if isinstance(selected_fact_plan, dict) else {}
    facts = plan.get("facts")
    if not isinstance(facts, list):
        return {}
    bundle_map, get_bundle = _slot_bundle_lookup_for_lane(section_lane)
    corpus: dict[str, str] = {}
    for fact in facts:
        if not isinstance(fact, dict):
            continue
        slot_id = str(fact.get("fact_id") or "").strip()
        if not slot_id:
            continue
        parts = [
            str(fact.get("claim_text") or "").strip(),
            str(fact.get("metric_raw") or "").strip(),
        ]
        bundle_id = bundle_map.get(slot_id, "")
        if bundle_id and get_bundle is not None:
            try:
                bundle = get_bundle(bundle_id)
            except (OSError, ValueError, KeyError):
                bundle = None
            if isinstance(bundle, dict):
                parts.append(_bundle_non_metric_text(bundle))
        text = " ".join(p for p in parts if p).strip()
        if text:
            corpus[slot_id] = text
    return corpus


__all__ = [
    "CORPUS_SOURCE_LABEL",
    "ENTAILMENT_BYPASS_ENV",
    "ENTAILMENT_RECEIPT_FILENAME",
    "ENTAILMENT_REJECTION_REASON",
    "build_slot_entailment_corpus",
    "extract_numeric_tokens",
    "normalize_numeric_token",
    "numeric_entailment_check",
]
