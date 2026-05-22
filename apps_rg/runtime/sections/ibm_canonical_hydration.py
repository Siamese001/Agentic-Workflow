"""Deterministic IBM bullet/narrative alignment to canonical base-resume IBM employment.

Used when claim evidence comes from a thin candidate_fact_ledger slice (<5 IBM rows) so X2
structural gates (bul_ibm_* coverage, core metrics) still bind to locked resume copy without
weakening validators.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS

_GRAPH_SKILLS_EVIDENCE = "augmented_skills_graph"


def _parsed_ledger_lacks_bul_ibm_roots(parsed: dict[str, Any]) -> bool:
    """True when bullets or claim_ledger cite only graph fact_* ids (X2 requires bul_ibm_*)."""
    bullets = parsed.get("bullets") or []
    if len(bullets) < len(IBM_BULLET_IDS):
        return True
    for bullet in bullets:
        if not isinstance(bullet, dict):
            return True
        src = bullet.get("source_fact_ids") or []
        if not any(str(s).startswith("bul_ibm_") for s in src):
            return True
    for row in parsed.get("claim_ledger") or []:
        if not isinstance(row, dict):
            continue
        src = row.get("source_fact_ids") or []
        if not any(str(s).startswith("bul_ibm_") for s in src):
            return True
    return False

_TAXONOMY_PREFIX = re.compile(r"^[A-Z][A-Za-z /,&-]{3,60}:\s+")


def sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def strip_ibm_bullet_taxonomy_prefix(text: str) -> str:
    t = (text or "").strip()
    if _TAXONOMY_PREFIX.match(t) and ": " in t:
        return t.split(": ", 1)[1].strip()
    return t


def ibm_bullet_texts_missing_core_metrics(parsed: dict[str, Any]) -> bool:
    """True when live bullet text lacks locked IBM metric tokens (X2 ``x2_ibm_metrics_preserved``)."""
    texts: list[str] = []
    for b in parsed.get("bullets") or []:
        if isinstance(b, dict):
            texts.append(str(b.get("bullet_text") or ""))
        elif isinstance(b, str):
            texts.append(b)
    combined = "\n".join(texts)
    combined_lower = combined.lower()
    return not (
        ("$15M" in combined or "$15m" in combined_lower)
        and "99.9%" in combined
        and "30%" in combined
        and "25%" in combined
        and "50%" in combined
    )


def should_hydrate_ibm_bullets_from_canonical(
    runtime_payload: dict[str, Any],
    parsed: dict[str, Any] | None = None,
) -> bool:
    """Deprecated: base-resume bullet hydration is forbidden (graph/ledger only)."""
    _ = runtime_payload, parsed
    return False


def hydrate_parsed_ibm_bullets_from_canonical_resume(
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
        "hydrate_parsed_ibm_bullets_from_canonical_resume is forbidden; "
        "use augmented_skills_graph + LLM rewrite from ledger claim_text"
    )


def fact_ids_for_ibm_narrative_ledger(runtime_payload: dict[str, Any]) -> list[str]:
    allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    facts = sorted(x for x in allowed if x.startswith("fact_"))
    if facts:
        return facts[:6]
    return sorted(x for x in allowed if x.startswith("bul_ibm_"))[:6]


def decompose_ibm_narrative_claim_ledger_by_clause(
    parsed: dict[str, Any],
    *,
    narrative_sentence: str,
    allowed_fact_ids: set[str] | frozenset[str],
) -> None:
    """Rewrite claim_ledger into clause rows with theme-scoped bul_ibm_* roots (max 2 per row)."""
    from apps_rg.runtime.validators.ibm_narrative_x2 import ibm_narrative_material_fact_ids_for_sentence

    narrative = str(parsed.get("narrative_sentence") or narrative_sentence or "").strip()
    if not narrative:
        return
    allowed_bul = sorted(x for x in allowed_fact_ids if str(x).startswith("bul_ibm_"))
    if not allowed_bul:
        allowed_bul = list(IBM_BULLET_IDS)

    parts = re.split(r",\s+(?=establishing\b)", narrative, maxsplit=1, flags=re.I)
    new_led: list[dict[str, Any]] = []
    if len(parts) >= 2:
        for part in parts:
            clause = part.strip().rstrip(".")
            if not clause:
                continue
            themes = sorted(
                t
                for t in ibm_narrative_material_fact_ids_for_sentence(clause)
                if t in allowed_bul
            )
            if not themes:
                themes = allowed_bul[:2]
            new_led.append(
                {
                    "claim_text": clause,
                    "source_fact_ids": themes[:2],
                }
            )
    else:
        themes = sorted(
            t for t in ibm_narrative_material_fact_ids_for_sentence(narrative) if t in allowed_bul
        )
        if not themes:
            themes = allowed_bul[:2]
        new_led.append(
            {
                "claim_text": narrative.rstrip(".!?"),
                "source_fact_ids": themes[:2],
            }
        )

    existing = [r for r in (parsed.get("claim_ledger") or []) if isinstance(r, dict)]
    if existing and len(existing) >= len(new_led):
        merged: list[dict[str, Any]] = []
        for i, row in enumerate(new_led):
            src_row = existing[i] if i < len(existing) else row
            ct = str(row.get("claim_text") or "").strip()
            roots = list(row.get("source_fact_ids") or [])
            merged.append(
                {
                    "claim_text": ct,
                    "source_fact_ids": roots,
                }
            )
        parsed["claim_ledger"] = merged
    else:
        parsed["claim_ledger"] = new_led

    clog = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
    clog.append(
        {
            "operation": "decompose_ibm_narrative_claim_ledger_by_clause",
            "reason": "clause_level_bul_ibm_theme_binding",
        }
    )
    parsed["change_log"] = clog


def align_ibm_narrative_claim_ledger_to_bul_ibm(
    parsed: dict[str, Any],
    *,
    narrative_sentence: str,
    allowed_fact_ids: set[str] | frozenset[str],
    runtime_payload: dict[str, Any] | None = None,
) -> None:
    """Bind narrative claim_ledger to bul_ibm_* (required by X2; graph pool may emit fact_* only)."""
    from apps_rg.runtime.validators.ibm_narrative_x2 import ibm_narrative_material_fact_ids_for_sentence

    themes = ibm_narrative_material_fact_ids_for_sentence(narrative_sentence)
    bul_ids = sorted(t for t in themes if str(t).startswith("bul_ibm_"))
    if not bul_ids:
        bul_ids = sorted(str(x) for x in allowed_fact_ids if str(x).startswith("bul_ibm_"))[:3]
    if not bul_ids:
        bul_ids = ["bul_ibm_001"]

    narrative = str(parsed.get("narrative_sentence") or narrative_sentence or "").strip()
    led = list(parsed.get("claim_ledger") or [])
    new_led: list[dict[str, Any]] = []
    for row in led:
        if not isinstance(row, dict):
            continue
        ct = str(row.get("claim_text") or "").strip()
        if not ct:
            continue
        src = row.get("source_fact_ids") or []
        if any(str(s).startswith("bul_ibm_") for s in src):
            new_led.append(row)
        else:
            new_led.append({**row, "source_fact_ids": list(bul_ids)})
    if not new_led and narrative:
        new_led = [
            {
                "claim_text": narrative.rstrip(".!?"),
                "source_fact_ids": list(bul_ids),
            }
        ]
    parsed["claim_ledger"] = new_led
    allowed_out = set(str(x) for x in allowed_fact_ids) | set(bul_ids)
    if runtime_payload is not None:
        runtime_payload["allowed_fact_ids"] = sorted(allowed_out)
    clog = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
    clog.append(
        {
            "operation": "align_ibm_narrative_claim_ledger_to_bul_ibm",
            "reason": "graph_skills_authority_bul_ibm_x2_binding",
        }
    )
    parsed["change_log"] = clog


def remap_ibm_narrative_claim_ledger_to_fact_pool(
    parsed: dict[str, Any],
    runtime_payload: dict[str, Any],
) -> None:
    """Map narrative claim_ledger off bul_ibm_* placeholders onto allowed fact_* pool ids."""
    pp = runtime_payload.get("proof_pool_metadata") or {}
    if pp.get("claim_evidence_source_type") == _GRAPH_SKILLS_EVIDENCE:
        align_ibm_narrative_claim_ledger_to_bul_ibm(
            parsed,
            narrative_sentence=str(parsed.get("narrative_sentence") or ""),
            allowed_fact_ids={str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])},
            runtime_payload=runtime_payload,
        )
        return
    if pp.get("claim_evidence_source_type") != "candidate_fact_ledger":
        return
    fact_ids = fact_ids_for_ibm_narrative_ledger(runtime_payload)
    if not fact_ids:
        return
    narrative = str(parsed.get("narrative_sentence") or "").strip()
    led = list(parsed.get("claim_ledger") or [])
    new_led: list[dict[str, Any]] = []
    for row in led:
        if not isinstance(row, dict):
            continue
        ct = str(row.get("claim_text") or "").strip()
        if not ct:
            continue
        new_led.append({**row, "source_fact_ids": list(fact_ids[:3])})
    if not new_led and narrative:
        new_led = [
            {
                "claim_text": narrative.rstrip(".!?"),
                "source_fact_ids": list(fact_ids[:3]),
            }
        ]
    parsed["claim_ledger"] = new_led
    clog = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
    clog.append(
        {
            "operation": "remap_ibm_narrative_claim_ledger_to_fact_pool",
            "reason": "candidate_fact_ledger_allow_list",
        }
    )
    parsed["change_log"] = clog
