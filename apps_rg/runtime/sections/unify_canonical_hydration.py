"""Deterministic Unify bullet alignment to canonical base-resume employment.

When graph-skills proof pools emit drifted LLM bullets (missing locked metrics or wrong
bul_unify_* binding), hydrate from canonical employment facts without weakening X2 gates.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from apps_rg.runtime.validators.unify_bullets_x2 import (
    DEFAULT_DISTRIBUTION,
    PROTECTED_BULLET_DEFAULT,
    UNIFY_BULLET_IDS,
)

_GRAPH_SKILLS_EVIDENCE = "augmented_skills_graph"

_SIX_MONTHS_RE = re.compile(
    r"\b(?:six|6)\s+months\s+to\s+(?:just\s+)?(?:three|3)\s+weeks\b",
    re.IGNORECASE,
)


def sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _canonicalize_unify_metric_text(text: str) -> str:
    if not text:
        return text
    return _SIX_MONTHS_RE.sub("six months to three weeks", text)


def _combined_bullet_text(parsed: dict[str, Any]) -> str:
    parts: list[str] = []
    for bullet in parsed.get("bullets") or []:
        if isinstance(bullet, dict):
            parts.append(str(bullet.get("bullet_text") or ""))
    return "\n".join(parts)


def unify_core_metrics_missing(parsed: dict[str, Any]) -> bool:
    combined = _combined_bullet_text(parsed)
    if not all(phrase in combined for phrase in ("$22M", "20%", "six months to three weeks")):
        return True
    if "8" not in combined or "28" not in combined:
        return True
    protected = next(
        (b for b in (parsed.get("bullets") or []) if b.get("bullet_id") == PROTECTED_BULLET_DEFAULT),
        None,
    )
    if not isinstance(protected, dict):
        return True
    if str(protected.get("rewrite_intensity", "")).upper() != "LIGHT_PROTECTED":
        return True
    pt = str(protected.get("bullet_text") or "")
    if not all(token in pt for token in ("$22M", "20%", "8", "28")):
        return True
    return False


def _parsed_ledger_lacks_bul_unify_roots(parsed: dict[str, Any]) -> bool:
    bullets = parsed.get("bullets") or []
    if len(bullets) < len(UNIFY_BULLET_IDS):
        return True
    for bullet in bullets:
        if not isinstance(bullet, dict):
            return True
        src = bullet.get("source_fact_ids") or []
        if not any(str(s).startswith("bul_unify_") for s in src):
            return True
    return False


def should_hydrate_unify_bullets_from_canonical(
    runtime_payload: dict[str, Any],
    parsed: dict[str, Any] | None = None,
) -> bool:
    """Deprecated: base-resume bullet hydration is forbidden (graph/ledger only)."""
    _ = runtime_payload, parsed
    return False


def hydrate_parsed_unify_bullets_from_canonical_resume(
    parsed: dict[str, Any],
    *,
    runtime_payload: dict[str, Any],
    canon_facts: list[dict[str, Any]],
    canon_allowed: set[str],
    default_intensity_by_bullet: dict[str, str],
) -> set[str]:
    """Forbidden: base-resume bullet paste removed; use graph plan + LLM rewrite."""
    _ = parsed, runtime_payload, canon_facts, canon_allowed, default_intensity_by_bullet
    raise ValueError(
        "hydrate_parsed_unify_bullets_from_canonical_resume is forbidden; "
        "use augmented_skills_graph + LLM rewrite from ledger claim_text"
    )
