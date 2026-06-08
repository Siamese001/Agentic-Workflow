"""apps_rg section C0 authority law — ownership split from agentic_core C0 builders."""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.c0.evidence_metrics_extractor import SupportTarget

from apps_rg.runtime.c0.constants import C0_AUTHORITY_LEDGER_GRAPH_PRIMARY

C0_AUTHORITY_MODE = C0_AUTHORITY_LEDGER_GRAPH_PRIMARY

AUTHORITY_CLASS_LEDGER_GRAPH_PROOF = "LEDGER_GRAPH_PROOF"
AUTHORITY_CLASS_SPINE_ENRICHMENT = "SPINE_ENRICHMENT_NON_AUTHORITATIVE"
# G11/G14 (plan apps-rg-e2e-gap-remediation-7e2d9c): base-resume / JD / briefing context contributes
# identity + targeting only — never proof authority for generated content.
AUTHORITY_CLASS_NON_PROOF_CONTEXT = "NON_PROOF_CONTEXT_NON_AUTHORITATIVE"

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


def section_chroma_write_in_c02() -> bool:
    """True when same-run C0.2 lane upsert is allowed (product default: skip)."""
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


def is_non_proof_context_source(source: str) -> bool:
    """True when an evidence source is base-resume / JD / briefing context — identity/targeting only."""
    s = str(source or "")
    return any(s == prefix or s.startswith(prefix) for prefix in NON_PROOF_CONTEXT_PREFIXES)


def assert_base_resume_identity_only(evidence_items: Any) -> None:
    """Enforce ``base_resume_static_anchors_only``: non-proof context never carries proof authority.

    Base-resume / JD / briefing items contribute identity + targeting context only; they must never
    be tagged ``LEDGER_GRAPH_PROOF`` or otherwise admitted as proof evidence for generated content
    (gaps G11/G14). The prefix scheme already excludes them from ``proof_support_target``; this guard
    locks the declared constraint so a future change that mistags them as proof fails loud.
    """
    for item in evidence_items or ():
        source = str(getattr(item, "source", "") or "")
        if not is_non_proof_context_source(source):
            continue
        authority = str(getattr(item, "authority_class", "") or "")
        if authority == AUTHORITY_CLASS_LEDGER_GRAPH_PROOF:
            raise ValueError(
                f"base-resume/JD context source {source!r} is tagged proof authority "
                f"{authority!r}; base resume contributes identity only, never proof (G11/G14)."
            )


def bridge_authority_fields() -> dict[str, Any]:
    return {
        "c0_authority_mode": C0_AUTHORITY_MODE,
        "ledger_graph_primary": True,
        "jd_targeting_only": True,
        "briefing_targeting_only": True,
        "base_resume_static_anchors_only": True,
    }


__all__ = [
    "AUTHORITY_CLASS_LEDGER_GRAPH_PROOF",
    "AUTHORITY_CLASS_NON_PROOF_CONTEXT",
    "AUTHORITY_CLASS_SPINE_ENRICHMENT",
    "assert_base_resume_identity_only",
    "is_non_proof_context_source",
    "C01_ARTIFACT",
    "C02_ATOMS_ARTIFACT",
    "C02_VECTOR_QUERY_ARTIFACT",
    "C0_AUTHORITY_MODE",
    "NON_PROOF_CONTEXT_PREFIXES",
    "PROOF_RETRIEVAL_SOURCE_PREFIXES",
    "bridge_authority_fields",
    "c03_skills_graph_receipt_flags",
    "proof_support_target",
    "section_chroma_write_in_c02",
]
