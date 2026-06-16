"""C0.4 — deterministic evidence stratification.

Ordering/ranking signals are produced earlier by C0.2 hybrid retrieval. This
phase assigns allowed/excluded strata and does not invoke a model reranker.
"""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.c0.constants import (
    CONFIDENCE_PENDING,
    GRAPH_STRENGTH_ADJACENT_ONLY,
    GRAPH_STRENGTH_CONTRADICTED,
    NOT_PROOF,
    PROOF_ELIGIBLE,
    STRATUM_BACKGROUND,
    STRATUM_CONTRADICTS,
    STRATUM_EXCLUDED,
    STRATUM_MUST_USE,
    STRATUM_SUPPORTING,
)

C02Atom = dict[str, Any]


def stratify_c04_evidence(
    *,
    section_id: str,
    atoms: list[C02Atom],
    graph_bindings: list[dict[str, Any]],
    lane_requires_proof: bool = False,
) -> dict[str, Any]:
    """Assign strata; exclude invalid / JD / unsupported adjacency."""
    binding_by_fact = {b["fact_id"]: b for b in graph_bindings}
    strata: dict[str, list[str]] = {
        STRATUM_MUST_USE: [],
        STRATUM_SUPPORTING: [],
        STRATUM_BACKGROUND: [],
        STRATUM_CONTRADICTS: [],
        STRATUM_EXCLUDED: [],
    }
    for atom in atoms:
        fid = str(atom.get("fact_id") or "")
        if not fid:
            continue
        blocked = section_id in list(atom.get("blocked_sections") or [])
        if blocked or atom.get("proof_status") == NOT_PROOF:
            strata[STRATUM_EXCLUDED].append(fid)
            continue
        gb = binding_by_fact.get(fid) or {}
        if gb.get("graph_support_strength") == GRAPH_STRENGTH_CONTRADICTED:
            strata[STRATUM_CONTRADICTS].append(fid)
            continue
        if gb.get("graph_support_strength") == GRAPH_STRENGTH_ADJACENT_ONLY and not gb.get(
            "claim_support_allowed"
        ):
            strata[STRATUM_BACKGROUND].append(fid)
            continue
        if lane_requires_proof and atom.get("proof_status") != PROOF_ELIGIBLE:
            if atom.get("confidence") == CONFIDENCE_PENDING:
                strata[STRATUM_EXCLUDED].append(fid)
                continue
            strata[STRATUM_BACKGROUND].append(fid)
            continue
        graph_grounded = (
            gb.get("binding_source") == "skill_fact_links"
            and gb.get("graph_support_strength") != GRAPH_STRENGTH_ADJACENT_ONLY
            and gb.get("claim_support_allowed")
        )
        if atom.get("proof_status") == PROOF_ELIGIBLE or (
            graph_grounded and not lane_requires_proof
        ):
            strata[STRATUM_MUST_USE].append(fid)
        else:
            strata[STRATUM_SUPPORTING].append(fid)
    allowed = (
        strata[STRATUM_MUST_USE]
        + strata[STRATUM_SUPPORTING]
        + strata[STRATUM_BACKGROUND]
    )
    return {
        "schema_version": "c04_stratify_v1",
        "section_id": section_id,
        "strata": strata,
        "allowed_fact_ids": allowed,
        "excluded_fact_ids": strata[STRATUM_EXCLUDED] + strata[STRATUM_CONTRADICTS],
    }


__all__ = ["stratify_c04_evidence"]
