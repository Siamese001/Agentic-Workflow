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
    if parsed is not None:
        if unify_core_metrics_missing(parsed):
            return True
        if _parsed_ledger_lacks_bul_unify_roots(parsed):
            return True
    pp = runtime_payload.get("proof_pool_metadata") or {}
    source_type = str(pp.get("claim_evidence_source_type") or "")
    facts = (runtime_payload.get("selected_fact_plan") or {}).get("facts") or []
    bul_in_plan = sum(1 for f in facts if str(f.get("fact_id") or "").startswith("bul_unify_"))
    if source_type == "candidate_fact_ledger":
        return len(facts) < len(UNIFY_BULLET_IDS) or bul_in_plan < len(UNIFY_BULLET_IDS)
    if source_type == _GRAPH_SKILLS_EVIDENCE:
        return bul_in_plan < len(UNIFY_BULLET_IDS)
    return False


def hydrate_parsed_unify_bullets_from_canonical_resume(
    parsed: dict[str, Any],
    *,
    runtime_payload: dict[str, Any],
    canon_facts: list[dict[str, Any]],
    canon_allowed: set[str],
    default_intensity_by_bullet: dict[str, str],
) -> set[str]:
    """In-place: six canonical Unify bullets + claim_ledger; returns expanded allowed_fact_ids."""
    pool_allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    allowed_out = pool_allowed | {str(x) for x in canon_allowed}
    by_canon = {str(f.get("fact_id")): f for f in canon_facts if f.get("fact_id")}

    bullets: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    for bid in UNIFY_BULLET_IDS:
        canon = by_canon.get(bid)
        if not canon:
            continue
        text = _canonicalize_unify_metric_text(str(canon.get("claim_text") or ""))
        metric_raw = str(canon.get("metric_raw") or "")
        src: list[str] = [bid]
        if metric_raw:
            mid = f"{bid}_metric_{sha16(metric_raw)[:8]}"
            if mid in allowed_out:
                src.append(mid)
        intensity = default_intensity_by_bullet.get(bid, "MODERATE")
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "rewrite_intensity": intensity,
                "has_metric": bool(canon.get("has_metric")),
                "metric_raw": metric_raw or None,
                "source_fact_ids": src,
            }
        )
        ledger.append({"claim_text": text, "source_fact_ids": list(src)})

    parsed["bullets"] = bullets
    parsed["claim_ledger"] = ledger
    counts = {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    for row in bullets:
        key = str(row.get("rewrite_intensity", "")).upper()
        if key in counts:
            counts[key] += 1
    parsed["rewrite_distribution"] = {**counts, "total": sum(counts.values())}
    clog = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
    clog.append(
        {
            "operation": "hydrate_unify_bullets_from_canonical_resume",
            "reason": "canonical_unify_resume_hydration",
        }
    )
    parsed["change_log"] = clog
    runtime_payload["allowed_fact_ids"] = sorted(allowed_out)
    return allowed_out
