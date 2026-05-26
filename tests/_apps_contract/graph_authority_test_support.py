"""Shared helpers for graph-skills / evidence_authority contract tests."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.proof_pool_resolver import SectionProofPool


def product_proof_pool_metadata(pool: SectionProofPool) -> dict[str, Any]:
    """Attach ``evidence_authority`` / ``selection_scope`` / ``layout_context`` like product CLI."""
    from apps_rg.runtime.product_evidence_authority import finalize_product_section_proof_pool

    finalized = finalize_product_section_proof_pool(pool)
    meta = finalized.proof_pool_metadata
    assert isinstance(meta, dict)
    return meta


def minimal_graph_proof_pool_metadata(
    *,
    graph_ref: str = "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
    ledger_ref: str = "apps_rg/fact_inventory/candidate_fact_ledger.json",
) -> dict[str, Any]:
    """Runtime-payload style metadata for in-process lane tests."""
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority

    meta: dict[str, Any] = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": graph_ref,
        "augmented_skills_graph_present": True,
        "skills_authority_status": "PASS",
    }
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=graph_ref,
        ledger_ref=ledger_ref,
        skills_authority_status="PASS",
    )
    return meta
