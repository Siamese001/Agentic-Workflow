"""apps_rg section C0 authority law — ownership split from agentic_core C0 builders."""

from __future__ import annotations

import os
from typing import Any

from agentic_core.runtime.c0.evidence_metrics_extractor import SupportTarget

from apps_rg.runtime.c02_chroma_lifecycle import C0_AUTHORITY_LEDGER_GRAPH_PRIMARY

# Re-export SSOT authority mode label for bridge/receipts.
C0_AUTHORITY_MODE = C0_AUTHORITY_LEDGER_GRAPH_PRIMARY

AUTHORITY_CLASS_LEDGER_GRAPH_PROOF = "LEDGER_GRAPH_PROOF"
AUTHORITY_CLASS_SPINE_ENRICHMENT = "SPINE_ENRICHMENT_NON_AUTHORITATIVE"

C01_ARTIFACT = "c01_retrieval_plan.json"
C02_ATOMS_ARTIFACT = "c02_atoms.json"
C02_VECTOR_QUERY_ARTIFACT = "c02_vector_query.json"

PROOF_RETRIEVAL_SOURCE_PREFIXES: tuple[str, ...] = (
    "fact:",
    "ledger:",
    "proof_pool:",
    "srfs:",
)

NON_PROOF_CONTEXT_PREFIXES: tuple[str, ...] = (
    "jd_payload",
    "resume_payload",
    "briefing_payload",
    "targeting_only",
)


def resolve_spine_chroma_enrich(
    *,
    explicit: bool | None = None,
    merge_canonical_c0: bool | None = None,
) -> bool:
    """Explicit spine Chroma enrichment — off by default on section lanes."""
    if explicit is not None:
        return explicit
    if merge_canonical_c0 is not None:
        return merge_canonical_c0
    return os.environ.get("APPS_RG_SPINE_CHROMA_ENRICH", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def section_chroma_write_in_c02(spine_chroma_enrich: bool) -> bool:
    """One Chroma policy: write in C0.2 OR query in C0.5 enrich — not both by default."""
    if spine_chroma_enrich:
        return False
    from apps_rg.runtime.c02_chroma_lifecycle import product_section_skip_lane_upsert

    return not product_section_skip_lane_upsert()


def c03_skills_graph_receipt_flags(*, core_graph_rag_ran: bool = False) -> dict[str, bool]:
    """Disambiguate apps skills graph from core GraphRAG C0.3."""
    return {
        "apps_rg_c03_skills_graph_used": True,
        "core_c03_graph_rag_used": core_graph_rag_ran,
        "canonical_c0_3_claimed": core_graph_rag_ran,
    }


def proof_support_target() -> SupportTarget:
    """Proof-supporting retrieval sources for c0_metrics (not JD/resume/briefing)."""
    return SupportTarget.from_prefix_list(
        list(PROOF_RETRIEVAL_SOURCE_PREFIXES),
        label="apps_rg_proof_authority",
    )


def bridge_authority_fields(*, spine_chroma_enrich: bool) -> dict[str, Any]:
    return {
        "c0_authority_mode": C0_AUTHORITY_MODE,
        "spine_chroma_enrich": spine_chroma_enrich,
        "ledger_graph_primary": True,
        "jd_targeting_only": True,
        "briefing_targeting_only": True,
        "base_resume_static_anchors_only": True,
    }


__all__ = [
    "AUTHORITY_CLASS_LEDGER_GRAPH_PROOF",
    "AUTHORITY_CLASS_SPINE_ENRICHMENT",
    "C01_ARTIFACT",
    "C02_ATOMS_ARTIFACT",
    "C02_VECTOR_QUERY_ARTIFACT",
    "C0_AUTHORITY_MODE",
    "NON_PROOF_CONTEXT_PREFIXES",
    "PROOF_RETRIEVAL_SOURCE_PREFIXES",
    "bridge_authority_fields",
    "c03_skills_graph_receipt_flags",
    "proof_support_target",
    "resolve_spine_chroma_enrich",
    "section_chroma_write_in_c02",
]
