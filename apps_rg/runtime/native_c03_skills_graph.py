"""Native C0.3 skills-graph evidence — route/ACL-bound, separate from section-local binding.

Section-local graph context remains ``section_c03_graph_binding`` /
``SECTION_GRAPH_CONTEXT_BINDING_NOT_PRODUCT_C0_3``. This module emits
``AppsRgC03FinalEvidenceContract`` with ``FULL_C0_3_GRAPHRAG_BINDING`` only when
RouteContract + ACL evaluation succeed.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from apps_rg.fact_inventory.augmented_skills_graph import (
    SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
    graph_version_from_payload,
)
from apps_rg.runtime.c03_graphrag_bound import (
    FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF,
    SUPPORT_STATUS_SUPPORTED,
    _collect_graph_expansion_refs,
    _collect_graph_lineage_refs,
    _fact_node_ids,
)
from apps_rg.runtime.section_spine_terminology import (
    BINDING_CLASSIFICATION_FULL_C03,
    BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT,
)

CONTRACT_TYPE_NATIVE_C03 = "AppsRgC03FinalEvidenceContract"
CONTRACT_VERSION_NATIVE_C03 = "apps_rg_native_c03_v1"
ARTIFACT_BASENAME_NATIVE_C03 = "native_c03_final_evidence.json"

from apps_rg.runtime.c0_mandatory_policy import C03_MANDATORY_SECTIONS

NATIVE_C03_FIRST_WAVE_SECTIONS: frozenset[str] = C03_MANDATORY_SECTIONS

ALL_CANONICAL_SECTIONS: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "insurtech_bullets",
    "insurtech_narrative",
    "ey_bullets",
    "ey_narrative",
    "competencies",
)

SECTION_NATIVE_C03_EXPANSION_MATRIX: dict[str, dict[str, Any]] = {
    "executive_summary": {
        "wave": "W2",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "competencies": {
        "wave": "W3",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "headline": {
        "wave": "W5",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "unify_bullets": {
        "wave": "W5",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "unify_narrative": {
        "wave": "W5",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "ibm_bullets": {
        "wave": "W5",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "ibm_narrative": {
        "wave": "W5",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "insurtech_bullets": {
        "wave": "W6",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "insurtech_narrative": {
        "wave": "W6",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "ey_bullets": {
        "wave": "W6",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
    "ey_narrative": {
        "wave": "W6",
        "native_c03_enabled": True,
        "default_proof_source": "augmented_skills_graph",
        "tests_required": True,
    },
}


@dataclass(frozen=True, slots=True)
class SkillsGraphAclPolicy:
    """Minimal ACL for augmented skills graph evidence (apps_rg-local)."""

    section_allowlist: frozenset[str]
    source_authority_class: str = SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    min_confidence: float = 0.0
    claim_eligibility_tier: str = "product_visible"
    route_family_allowlist: frozenset[str] = frozenset()
    product_scope: str = "section_dev"
    max_graph_hop_depth: int = 2
    max_selected_nodes: int = 64


@dataclass(frozen=True, slots=True)
class SkillsGraphAclDecision:
    allowed_fact_ids: frozenset[str]
    allowed_graph_node_ids: frozenset[str]
    blocked_fact_ids: frozenset[str]
    blocked_node_ids: frozenset[str]
    blocked_source_ids: frozenset[str]
    acl_scope: str
    source_scope: str
    product_proof_eligible: bool
    pa_evidence_eligible: bool
    reason_codes: tuple[str, ...] = field(default_factory=tuple)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_hex(text: str | bytes) -> str:
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()


def default_acl_policy(*, section_id: str, product_visible: bool) -> SkillsGraphAclPolicy:
    return SkillsGraphAclPolicy(
        section_allowlist=frozenset({section_id}),
        product_scope="whole_run_product" if product_visible else "section_dev",
    )


def extract_route_context(front_spine: Any) -> dict[str, Any]:
    """Bind native C0.3 to RouteContract from section front spine."""
    route = getattr(front_spine, "route", None)
    if route is None:
        return {}
    graph_policy = getattr(route, "graph_policy", None)
    expansion_allowed = True
    if graph_policy is not None:
        expansion_allowed = bool(getattr(graph_policy, "graph_expansion_allowed", True))
    return {
        "route_contract_ref": "route_contract.json",
        "route_id": str(getattr(route, "route_id", "") or ""),
        "route_family": str(getattr(route, "route_family", "") or ""),
        "support_target": str(getattr(route, "support_target", "") or getattr(route, "route_id", "") or ""),
        "execution_form": str(getattr(route, "execution_form", "") or ""),
        "grounding_required": bool(getattr(route, "grounding_required", False)),
        "graph_expansion_allowed": expansion_allowed,
    }


def evaluate_skills_graph_acl(
    *,
    section_id: str,
    route_ctx: Mapping[str, Any],
    selected_fact_ids: Iterable[str],
    graph: Mapping[str, Any],
    policy: SkillsGraphAclPolicy,
    product_visible: bool,
) -> SkillsGraphAclDecision:
    """Evaluate whether graph nodes/facts may enter native C0.3 evidence."""
    reasons: list[str] = []
    fact_set = {str(x).strip() for x in selected_fact_ids if str(x).strip()}
    allowed_facts: set[str] = set()
    blocked_facts: set[str] = set()
    allowed_nodes: set[str] = set()
    blocked_nodes: set[str] = set()

    if section_id not in policy.section_allowlist:
        reasons.append("section_not_allowlisted")
        blocked_facts.update(fact_set)
    else:
        allowed_facts.update(fact_set)

    route_family = str(route_ctx.get("route_family") or "")
    if route_family and policy.route_family_allowlist and route_family not in policy.route_family_allowlist:
        reasons.append("route_family_denied")
        blocked_facts.update(allowed_facts)
        allowed_facts.clear()

    if not bool(route_ctx.get("graph_expansion_allowed", True)):
        reasons.append("graph_expansion_disallowed_by_route")
        blocked_facts.update(allowed_facts)
        allowed_facts.clear()

    node_ids = _fact_node_ids(allowed_facts)
    for nid in node_ids:
        allowed_nodes.add(nid)

    edge_cap = policy.max_graph_hop_depth * 32
    for edge in list(graph.get("graph_edges") or [])[:edge_cap]:
        if not isinstance(edge, dict):
            continue
        eid = str(edge.get("edge_id") or "")
        if eid.startswith("blocked:"):
            blocked_nodes.add(str(edge.get("source_node_id") or edge.get("source") or ""))

    product_eligible = product_visible and not reasons and bool(allowed_facts)
    pa_eligible = bool(allowed_facts) and section_id in policy.section_allowlist

    return SkillsGraphAclDecision(
        allowed_fact_ids=frozenset(allowed_facts),
        allowed_graph_node_ids=frozenset(allowed_nodes),
        blocked_fact_ids=frozenset(blocked_facts),
        blocked_node_ids=frozenset(n for n in blocked_nodes if n),
        blocked_source_ids=frozenset(),
        acl_scope=f"section:{section_id}",
        source_scope=policy.source_authority_class,
        product_proof_eligible=product_eligible,
        pa_evidence_eligible=pa_eligible,
        reason_codes=tuple(reasons),
    )


def validate_native_c03_contract(doc: Mapping[str, Any] | None) -> tuple[bool, tuple[str, ...]]:
    """Fail-closed validation for FULL_C0_3_GRAPHRAG_BINDING claims."""
    if not doc or not isinstance(doc, Mapping):
        return False, ("missing_contract",)
    missing: list[str] = []
    if str(doc.get("contract_type") or "") != CONTRACT_TYPE_NATIVE_C03:
        missing.append("contract_type")
    if not doc.get("route_bound"):
        missing.append("route_bound")
    if not doc.get("acl_bound"):
        missing.append("acl_bound")
    if not list(doc.get("graph_lineage_refs") or []):
        missing.append("graph_lineage_refs")
    if not list(doc.get("source_lineage_refs") or []):
        missing.append("source_lineage_refs")
    if not str(doc.get("support_status") or "").strip():
        missing.append("support_status")
    if str(doc.get("binding_classification") or "") != BINDING_CLASSIFICATION_FULL_C03:
        missing.append("binding_classification")
    if not doc.get("apps_rg_c03_skills_graph_used"):
        missing.append("apps_rg_c03_skills_graph_used")
    if doc.get("canonical_c0_3_claimed"):
        missing.append("canonical_c0_3_claimed_must_be_false_without_core_graphrag")
    return (not missing, tuple(missing))


def build_native_c03_final_evidence(
    *,
    section_id: str,
    graph: dict[str, Any],
    graph_ref: str,
    graph_digest: str,
    selected_fact_ids: Iterable[str],
    route_ctx: Mapping[str, Any],
    acl: SkillsGraphAclDecision,
    evidence_items: list[dict[str, Any]] | None = None,
    graph_hop_bounds: int = 2,
    product_visible: bool = False,
    whole_run_envelope: bool = False,
) -> dict[str, Any] | None:
    """Build native C0.3 contract; None when route/ACL proof insufficient."""
    if not route_ctx.get("route_id"):
        return None
    if not acl.allowed_fact_ids:
        return None

    fact_allowed = set(acl.allowed_fact_ids)
    fact_blocked = set(acl.blocked_fact_ids)
    items: list[dict[str, Any]] = []
    excluded_refs: list[str] = []
    for fid in sorted(fact_blocked):
        excluded_refs.append(f"excluded:fact:{fid}")
    for item in evidence_items or []:
        if not isinstance(item, dict):
            continue
        fid = str(item.get("evidence_id") or item.get("source_fact_id") or "").replace("evidence:graph:", "")
        if fid in fact_allowed or not fid:
            items.append(item)
        else:
            excluded_refs.append(f"excluded:item:{fid}")

    if not items and fact_allowed:
        for fid in sorted(fact_allowed):
            items.append(
                {
                    "evidence_id": f"evidence:graph:{fid}",
                    "source": graph_ref,
                    "source_class": "augmented_skills_graph",
                    "graph_node_ref": f"node_fact_{fid.split('_metric_', 1)[0]}",
                    "authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
                    "data_only": True,
                    "not_instruction": True,
                }
            )

    graph_expansion_refs = list(
        _collect_graph_expansion_refs(graph, selected_fact_ids=fact_allowed)
    )
    graph_lineage_refs = list(_collect_graph_lineage_refs(graph, selected_fact_ids=fact_allowed))
    source_lineage_refs = [
        f"ref:source:{SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH}",
        f"ref:graph:{graph_ref}",
    ]
    for fid in sorted(fact_allowed)[:32]:
        source_lineage_refs.append(f"ref:source_fact:{fid}")

    support_status = SUPPORT_STATUS_SUPPORTED if items and fact_allowed else "EMPTY"
    if support_status in FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF:
        support_status = "EMPTY"

    ts = _utc_now()
    digest_material = {
        "section_id": section_id,
        "graph_digest": graph_digest,
        "facts": sorted(fact_allowed),
        "route_id": route_ctx.get("route_id"),
    }
    final_digest = _sha256_hex(json.dumps(digest_material, sort_keys=True))[:32]

    citation_map = {fid: [f"ref:graph:fact_lineage:{fid}"] for fid in sorted(fact_allowed)}

    can_product = bool(acl.product_proof_eligible and whole_run_envelope)

    return {
        "contract_type": CONTRACT_TYPE_NATIVE_C03,
        "contract_version": CONTRACT_VERSION_NATIVE_C03,
        "generated_at_utc": ts,
        "section_id": section_id,
        "route_contract_ref": str(route_ctx.get("route_contract_ref") or "route_contract.json"),
        "route_id": str(route_ctx.get("route_id") or ""),
        "route_family": str(route_ctx.get("route_family") or ""),
        "support_target": str(route_ctx.get("support_target") or route_ctx.get("route_id") or ""),
        "graph_source": "augmented_skills_graph",
        "graph_source_version": graph_version_from_payload(graph),
        "graph_expansion_allowed": bool(route_ctx.get("graph_expansion_allowed", True)),
        "route_bound": True,
        "acl_bound": True,
        "acl_scope": acl.acl_scope,
        "source_scope": acl.source_scope,
        "freshness_profile": "apps_rg_static_graph_v1",
        "graph_hop_bounds": graph_hop_bounds,
        "graph_query_seed": str(route_ctx.get("support_target") or section_id),
        "selected_graph_nodes": sorted(acl.allowed_graph_node_ids),
        "selected_source_fact_ids": sorted(fact_allowed),
        "graph_lineage_refs": graph_lineage_refs,
        "source_lineage_refs": source_lineage_refs,
        "citation_map": citation_map,
        "evidence_items": items,
        "evidence_strata": {
            "graph_substrate": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "targeting_inputs": "non_proof",
        },
        "support_status": support_status,
        "excluded_evidence_refs": excluded_refs,
        "blocked_source_refs": sorted(acl.blocked_source_ids),
        "blocked_node_ids": sorted(acl.blocked_node_ids),
        "contradiction_report": {"conflicts": []},
        "final_evidence_digest": final_digest,
        "graph_ref": graph_ref,
        "graph_digest": graph_digest,
        "graph_sig": _sha256_hex(f"{graph_digest}:{','.join(sorted(fact_allowed))}")[:32],
        "graph_expansion_refs": graph_expansion_refs,
        "apps_rg_c03_skills_graph_used": True,
        "core_c03_graph_rag_used": False,
        "canonical_c0_3_claimed": False,
        "binding_classification": BINDING_CLASSIFICATION_FULL_C03,
        "binding_kind": "native_c03_skills_graph",
        "fec_shape_only": False,
        "canonical_final_evidence_contract_emitted": True,
        "section_local_graph_context_only": False,
        "can_satisfy_integrated_product_proof": can_product,
        "product_proof_eligible": can_product,
        "pa_data_only": True,
        "explicit_non_claims": [
            "graph nodes and evidence_items are PA data only — not instructions",
            "JD/briefing are targeting only unless explicitly source-authorized",
            "section CLI alone does not satisfy integrated product proof",
        ],
        "producer_stage": "apps_rg.native_c03_skills_graph",
    }


def native_c03_pa_metadata(contract: Mapping[str, Any]) -> dict[str, Any]:
    """PA compile metadata — evidence is data-only."""
    return {
        "c03_contract_ref": ARTIFACT_BASENAME_NATIVE_C03,
        "c03_binding_classification": str(contract.get("binding_classification") or ""),
        "c03_support_status": str(contract.get("support_status") or ""),
        "c03_allowed_fact_ids": list(contract.get("selected_source_fact_ids") or []),
        "c03_graph_lineage_refs": list(contract.get("graph_lineage_refs") or []),
        "c03_source_lineage_refs": list(contract.get("source_lineage_refs") or []),
        "c03_excluded_evidence_refs": list(contract.get("excluded_evidence_refs") or []),
        "c03_route_bound": bool(contract.get("route_bound")),
        "c03_acl_bound": bool(contract.get("acl_bound")),
        "c03_pa_data_only": True,
        "c03_not_instruction": True,
    }


def merge_native_c03_into_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str,
    front_spine: Any,
    graph: dict[str, Any],
    graph_ref: str,
    graph_digest: str,
    selected_fact_ids: Iterable[str],
    product_visible: bool = True,
    whole_run_envelope: bool = False,
) -> dict[str, Any]:
    """Attach native C0.3 alongside section-local c03_graphrag_bound (unchanged)."""
    from apps_rg.runtime.c03_graphrag_bound import (
        build_executive_summary_c03_graphrag_bound,
        build_section_c03_graphrag_bound,
    )

    out = dict(meta)
    if not isinstance(out.get("c03_graphrag_bound"), dict):
        fact_ids = list(selected_fact_ids)
        if section_id == "executive_summary":
            out["c03_graphrag_bound"] = build_executive_summary_c03_graphrag_bound(
                graph=graph,
                graph_ref=graph_ref,
                graph_digest=graph_digest,
                selected_fact_ids=fact_ids,
            )
        else:
            out["c03_graphrag_bound"] = build_section_c03_graphrag_bound(
                section_id=section_id,
                graph=graph,
                graph_ref=graph_ref,
                graph_digest=graph_digest,
                selected_fact_ids=fact_ids,
            )
    if section_id not in NATIVE_C03_FIRST_WAVE_SECTIONS:
        out["native_c03_status"] = "SECTION_NOT_IN_WAVE"
        return out

    route_ctx = extract_route_context(front_spine)
    if not route_ctx.get("route_id"):
        out["native_c03_status"] = "ROUTE_MISSING"
        out["c03_binding_classification"] = BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT
        return out

    policy = default_acl_policy(section_id=section_id, product_visible=product_visible)
    acl = evaluate_skills_graph_acl(
        section_id=section_id,
        route_ctx=route_ctx,
        selected_fact_ids=selected_fact_ids,
        graph=graph,
        policy=policy,
        product_visible=product_visible,
    )

    fec_items = None
    fec_snap = out.get("final_evidence_contract_snapshot")
    if isinstance(fec_snap, dict):
        fec_items = list(fec_snap.get("evidence_items") or [])

    native = build_native_c03_final_evidence(
        section_id=section_id,
        graph=graph,
        graph_ref=graph_ref,
        graph_digest=graph_digest,
        selected_fact_ids=acl.allowed_fact_ids,
        route_ctx=route_ctx,
        acl=acl,
        evidence_items=fec_items,
        product_visible=product_visible,
        whole_run_envelope=whole_run_envelope,
    )
    if native is None:
        out["native_c03_status"] = "ACL_OR_ROUTE_BLOCKED"
        out["c03_binding_classification"] = BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT
        return out

    ok, missing = validate_native_c03_contract(native)
    if not ok:
        out["native_c03_status"] = f"CONTRACT_INVALID:{','.join(missing)}"
        out["c03_binding_classification"] = BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT
        return out

    out["native_c03_final_evidence"] = native
    out["native_c03_status"] = "EMITTED"
    out["c03_binding_classification"] = BINDING_CLASSIFICATION_FULL_C03
    out["c03_pa_metadata"] = native_c03_pa_metadata(native)
    out["native_c03_artifact_basename"] = ARTIFACT_BASENAME_NATIVE_C03
    # Section-local binding classification unchanged on c03_graphrag_bound key.
    if isinstance(out.get("c03_graphrag_bound"), dict):
        local = dict(out["c03_graphrag_bound"])
        local["paired_native_c03_ref"] = ARTIFACT_BASENAME_NATIVE_C03
        out["c03_graphrag_bound"] = local
    from apps_rg.runtime.c0_mandatory_policy import apps_rg_c03_graph_mandatory, is_c03_mandatory_section

    if apps_rg_c03_graph_mandatory() and is_c03_mandatory_section(section_id):
        if out.get("native_c03_status") != "EMITTED":
            raise RuntimeError(
                f"C0.3 skills graph mandatory for {section_id}: "
                f"status={out.get('native_c03_status')}"
            )
    return out


def enrich_proof_pool_with_native_c03(
    pool: Any,
    *,
    front_spine: Any,
    repo_root: Path,
    whole_run_envelope: bool | None = None,
) -> Any:
    """Return SectionProofPool with native C0.3 metadata merged when eligible."""
    from dataclasses import replace

    section = str(getattr(pool, "section", "") or "")
    if section not in NATIVE_C03_FIRST_WAVE_SECTIONS or front_spine is None:
        return pool
    envelope = whole_run_envelope
    if envelope is None:
        envelope = bool(getattr(front_spine, "whole_run_envelope", False))
    meta = dict(getattr(pool, "proof_pool_metadata", None) or {})
    graph_ref = str(meta.get("graph_ref") or pool.proof_pool_ref or "")
    graph_digest = str(meta.get("graph_digest") or "")
    if not graph_digest and graph_ref:
        graph_digest = _sha256_hex(graph_ref)
    from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph

    graph = load_augmented_skills_graph(repo_root=repo_root)
    merged = merge_native_c03_into_proof_pool_metadata(
        meta,
        section_id=section,
        front_spine=front_spine,
        graph=graph,
        graph_ref=graph_ref,
        graph_digest=graph_digest,
        selected_fact_ids=getattr(pool, "allowed_fact_ids_ordered", []) or [],
        product_visible=bool(getattr(front_spine, "product_visible", True)),
        whole_run_envelope=bool(envelope),
    )
    from apps_rg.runtime.c0_mandatory_policy import apps_rg_c03_graph_mandatory, is_c03_mandatory_section

    if apps_rg_c03_graph_mandatory() and is_c03_mandatory_section(section):
        if merged.get("native_c03_status") != "EMITTED":
            raise RuntimeError(
                f"C0.3 skills graph mandatory for {section}: "
                f"status={merged.get('native_c03_status')}"
            )
    return replace(pool, proof_pool_metadata=merged)


__all__ = [
    "ALL_CANONICAL_SECTIONS",
    "ARTIFACT_BASENAME_NATIVE_C03",
    "BINDING_CLASSIFICATION_FULL_C03",
    "CONTRACT_TYPE_NATIVE_C03",
    "CONTRACT_VERSION_NATIVE_C03",
    "NATIVE_C03_FIRST_WAVE_SECTIONS",
    "SECTION_NATIVE_C03_EXPANSION_MATRIX",
    "SkillsGraphAclDecision",
    "SkillsGraphAclPolicy",
    "build_native_c03_final_evidence",
    "default_acl_policy",
    "enrich_proof_pool_with_native_c03",
    "evaluate_skills_graph_acl",
    "extract_route_context",
    "merge_native_c03_into_proof_pool_metadata",
    "native_c03_pa_metadata",
    "validate_native_c03_contract",
]
