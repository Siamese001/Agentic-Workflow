"""C0.4 executive_summary stratify shaping after graph compression."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.c0.constants import (
    GRAPH_STRENGTH_ADJACENT_ONLY,
    STRATUM_BACKGROUND,
    STRATUM_MUST_USE,
    STRATUM_SUPPORTING,
)

C02Atom = dict[str, Any]


def shape_executive_summary_c04(
    c04: dict[str, Any],
    *,
    bindings: list[dict[str, Any]],
    atoms: list[C02Atom],
) -> dict[str, Any]:
    """Demote mechanism-overloaded facts; preserve MUST_USE for non-overloaded proof-eligible atoms."""
    if str(c04.get("section_id") or "") != "executive_summary":
        return c04
    out = dict(c04)
    strata = {k: list(v) for k, v in (out.get("strata") or {}).items()}
    binding_by_fact = {str(b.get("fact_id") or ""): b for b in bindings}
    must = list(strata.get(STRATUM_MUST_USE) or [])
    supporting = list(strata.get(STRATUM_SUPPORTING) or [])
    background = list(strata.get(STRATUM_BACKGROUND) or [])
    reordered_must: list[str] = []
    demoted: list[str] = []
    cert_demoted: list[str] = []
    for fid in list(must):
        if str(fid).startswith("fact_certs_"):
            cert_demoted.append(fid)
            if fid not in background:
                background.append(fid)
    for fid in cert_demoted:
        if fid in must:
            must.remove(fid)
        if fid in supporting:
            supporting.remove(fid)
    for fid in must:
        b = binding_by_fact.get(fid) or {}
        if b.get("mechanism_overloaded") and fid.startswith("fact_engineering_platform"):
            demoted.append(fid)
            if fid not in supporting:
                supporting.append(fid)
        else:
            reordered_must.append(fid)
    for fid in demoted:
        if fid in reordered_must:
            reordered_must.remove(fid)
    non_overloaded = [f for f in reordered_must if not (binding_by_fact.get(f) or {}).get("mechanism_overloaded")]
    overloaded_tail = [f for f in reordered_must if (binding_by_fact.get(f) or {}).get("mechanism_overloaded")]
    reordered_must = non_overloaded + overloaded_tail
    strata[STRATUM_MUST_USE] = reordered_must
    strata[STRATUM_SUPPORTING] = supporting
    out["strata"] = strata
    out["allowed_fact_ids"] = (
        reordered_must + supporting + background
    )
    compression_rows = []
    for b in bindings:
        if not b.get("mechanism_overloaded") and int(b.get("skill_binding_count_before") or 0) <= 4:
            continue
        compression_rows.append(
            {
                "fact_id": b.get("fact_id"),
                "skill_binding_count_before": b.get("skill_binding_count_before"),
                "skill_binding_count_after": b.get("skill_binding_count_after"),
                "executive_capability_phrases": b.get("executive_capability_phrases"),
                "suppressed_skill_count": len(b.get("suppressed_skill_refs") or []),
            }
        )
    out["exec_summary_compression"] = {
        "schema_version": "c04_exec_summary_compression_v1",
        "demoted_cert_facts_to_background": cert_demoted,
        "demoted_overloaded_to_supporting": demoted,
        "compression_applied": bool(compression_rows),
        "facts": compression_rows,
        "pa_instruction": (
            "Lead with executive outcomes and role fit; use at most two mechanism terms in "
            "sentence 1. Prefer executive_capability_phrases over skill-id vocabulary."
        ),
    }
    return out


__all__ = ["shape_executive_summary_c04"]
