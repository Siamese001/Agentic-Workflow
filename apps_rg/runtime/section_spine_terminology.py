"""One-spine terminology SSOT — section lane vs canonical governed spine (apps_rg-local).

Section CLI (``python -m apps_rg --section <lane>``) is a **lane-scoped invocation target**
into modular section runtimes. It is **not** a second canonical C0/GraphRAG spine.

Use these constants in receipts, tests, and docs — do not label static JSON graph binding
as full canonical C0.3 GraphRAG or canonical C0.5 FinalEvidenceContract unless the
governed spine actually emitted those contracts.
"""
from __future__ import annotations

from typing import Any, Mapping

# Canonical product spine (integrated R4 / dispatch without --section).
CANONICAL_SPINE_CHAIN: tuple[str, ...] = (
    "U0",
    "L1",
    "L0",
    "C0",
    "PA",
    "L2",
    "Exit",
    "UWG",
    "L4",
    "L6",
)

# Section lane modular chain (executive_summary exemplar; other lanes analogous).
SECTION_LANE_CHAIN: tuple[str, ...] = (
    "CLI",
    "canonical_dispatch.section_branch",
    "section_front_spine_bridge",
    "U0",
    "L1",
    "L0",
    "proof_pool_resolver",
    "section_graph_binding_shim",
    "section_PA",
    "section_L2",
    "section_X2",
    "section_X1D",
    "section_X3",
    "section_L6_shadow",
)

BINDING_KIND_SECTION_GRAPH_SHIM = "section_graph_binding_shim"
LEGACY_C03_ARTIFACT_BASENAME = "c03_graphrag_bound.json"
LEGACY_FEC_SNAPSHOT_BASENAME = "final_evidence_contract_snapshot.json"
RECOMMENDED_BINDING_ARTIFACT_BASENAME = "section_graph_binding.json"
RECOMMENDED_FEC_SNAPSHOT_BASENAME = "section_graph_binding_fec_snapshot.json"

# Governed spine contract types (agentic_spine_contracts_master.json).
CANONICAL_CONTRACT_TYPES: tuple[str, ...] = (
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
    "FinalEvidenceContract",
    "PromptEnvelope",
    "CompiledPromptArtifact",
    "L2ExecutionPacket",
    "SealedL2Artifact",
    "ExitDispositionReceipt",
    "RuntimeExhaustBundle",
)

# Contracts a section lane does NOT emit today (inventory / guardrails).
SECTION_LANE_MISSING_CANONICAL_CONTRACTS: tuple[str, ...] = CANONICAL_CONTRACT_TYPES

INPUT_AUTHORITY_GRAPH_SUBSTRATE_LINE = (
    "- CLAIM SUPPORT POOL (AUGMENTED SKILLS GRAPH): section graph binding (C0.3-shim) — "
    "static master_skills_arsenal ledger neighbors; not full agentic_core graph traverse — "
    "sole substrate for factual claims; candidate_fact_ledger rows are lineage substrate only"
)

EXPLICIT_NON_CLAIMS: tuple[str, ...] = (
    "no claim of full canonical C0.2 dense retrieval unless Chroma/BGE dense path ran",
    "no claim of full canonical C0.3 graph traverse unless RouteContract + ACL-bound traverse ran",
    "no claim of canonical C0.5 FinalEvidenceContract unless spine FEC was emitted and consumed by spine PA",
    "no claim of durable write unless UWG commit path executed",
    "section runtime_exhaust_bundle.json is lane-local exhaust refs, not spine RuntimeExhaustBundle",
)


def is_spine_final_evidence_contract(doc: Mapping[str, Any] | None) -> bool:
    """True only for governed-spine FEC (contract_type + producer_stage), not lane FEC-shaped snapshots."""
    if not doc or not isinstance(doc, Mapping):
        return False
    ct = str(doc.get("contract_type") or "").strip()
    if ct == "FinalEvidenceContract":
        return True
    prod = str(doc.get("producer_stage") or doc.get("producer") or "").strip().lower()
    if prod in {"c0", "c0_retrieve", "agentic_core.c0"}:
        return True
    return False


def is_section_graph_binding_doc(doc: Mapping[str, Any] | None) -> bool:
    if not doc or not isinstance(doc, Mapping):
        return False
    kind = str(doc.get("binding_kind") or "").strip()
    if kind == BINDING_KIND_SECTION_GRAPH_SHIM:
        return True
    sv = str(doc.get("schema_version") or "").strip()
    return sv in {"c03_graphrag_bound_v1", "section_graph_binding_v1"}


def enrich_section_graph_binding_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Add truthful spine labels without breaking legacy keys."""
    out = dict(doc)
    out["binding_kind"] = BINDING_KIND_SECTION_GRAPH_SHIM
    out["spine_lane_mode"] = "section_cli_modular"
    out["canonical_spine_chain_target"] = list(CANONICAL_SPINE_CHAIN)
    out["legacy_artifact_name"] = LEGACY_C03_ARTIFACT_BASENAME
    out["recommended_artifact_name"] = RECOMMENDED_BINDING_ARTIFACT_BASENAME
    fec_snap = out.get("final_evidence_contract_snapshot")
    if isinstance(fec_snap, dict):
        fec_enriched = dict(fec_snap)
        fec_enriched["fec_shape_only"] = True
        fec_enriched["canonical_final_evidence_contract_emitted"] = False
        fec_enriched["recommended_artifact_name"] = RECOMMENDED_FEC_SNAPSHOT_BASENAME
        out["final_evidence_contract_snapshot"] = fec_enriched
    out["canonical_contract_claims"] = {
        "ValidatedRequest": False,
        "L1PlanContract": False,
        "RouteContract": False,
        "FinalEvidenceContract": False,
        "PromptEnvelope": False,
        "CompiledPromptArtifact": False,
        "L2ExecutionPacket": False,
        "SealedL2Artifact": False,
        "ExitDispositionReceipt": False,
        "RuntimeExhaustBundle": False,
    }
    out["explicit_non_claims"] = list(EXPLICIT_NON_CLAIMS)
    return out


def section_lane_spine_classification() -> dict[str, Any]:
    from apps_rg.runtime.section_front_spine_bridge import (
        DOWNSTREAM_MISSING_CANONICAL_CONTRACTS,
        FRONT_SPINE_CONTRACTS,
    )

    return {
        "spine_mode": "section_lane_modular",
        "invocation": "python -m apps_rg --section <lane>",
        "is_second_spine": False,
        "is_canonical_c0_path": False,
        "observed_chain": list(SECTION_LANE_CHAIN),
        "canonical_target_chain": list(CANONICAL_SPINE_CHAIN),
        "front_spine_contracts_emitted": list(FRONT_SPINE_CONTRACTS),
        "missing_canonical_contracts": list(DOWNSTREAM_MISSING_CANONICAL_CONTRACTS),
        "explicit_non_claims": list(EXPLICIT_NON_CLAIMS),
    }


__all__ = [
    "BINDING_KIND_SECTION_GRAPH_SHIM",
    "CANONICAL_CONTRACT_TYPES",
    "CANONICAL_SPINE_CHAIN",
    "EXPLICIT_NON_CLAIMS",
    "INPUT_AUTHORITY_GRAPH_SUBSTRATE_LINE",
    "LEGACY_C03_ARTIFACT_BASENAME",
    "LEGACY_FEC_SNAPSHOT_BASENAME",
    "RECOMMENDED_BINDING_ARTIFACT_BASENAME",
    "RECOMMENDED_FEC_SNAPSHOT_BASENAME",
    "SECTION_LANE_CHAIN",
    "SECTION_LANE_MISSING_CANONICAL_CONTRACTS",
    "enrich_section_graph_binding_doc",
    "is_section_graph_binding_doc",
    "is_spine_final_evidence_contract",
    "section_lane_spine_classification",
]
