"""Deterministic offline closure of C0.3 skill authority and topology."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
)

RECONCILIATION_VERSION = "apps_rg.c03_graph_authority_reconciliation.v1"

# These mappings complete taxonomy fields omitted by the C0.3 granularity
# catalog. They classify graph structure only; they do not create claim proof.
C03_DOMAIN_TAXONOMY: dict[str, tuple[str, str]] = {
    "domain_agentic_runtime_governance": (
        "track_genai_agentic",
        "epoch_agentic_ai_runtime_architecture",
    ),
    "domain_graph_retrieval_evidence": (
        "track_genai_agentic",
        "epoch_agentic_ai_runtime_architecture",
    ),
    "domain_ai_platform_engineering": (
        "track_data_tech_cloud_ml",
        "epoch_cloud_data_platform_engineering",
    ),
    "domain_regulated_ai_controls": (
        "track_actuarial_risk_derivatives",
        "epoch_enterprise_risk_governance",
    ),
    "domain_partner_gtm_commercialization": (
        "track_data_tech_cloud_ml",
        "epoch_partner_gtm_revenue_leadership",
    ),
    "domain_enterprise_delivery_operating_model": (
        "track_data_tech_cloud_ml",
        "epoch_ai_platform_commercialization",
    ),
}

_PILLAR_DOMAIN_OVERRIDES = {
    "pillar_agentic_runtime_governance": "domain_agentic_runtime_governance",
}
_ACTIVE_LIFECYCLES = frozenset({"ACTIVE", "ACTIVE_CONFIRMED"})


class GraphAuthorityReconciliationError(ValueError):
    """Raised when existing canonical data cannot close a required field."""


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def classify_assertion_eligibility(row: Mapping[str, Any]) -> tuple[bool, str | None]:
    """Return the standalone assertion disposition for one canonical skill."""
    if str(row.get("activation_status") or "") not in _ACTIVE_LIFECYCLES:
        return False, "LIFECYCLE_NOT_ACTIVE"
    if not _strings(row.get("fact_id_links")):
        return False, "NO_CANDIDATE_FACT"
    if not _strings(row.get("allowed_sections")):
        return False, "NO_ALLOWED_SECTION"
    if not skill_row_eligible_for_external_claim(dict(row)):
        return False, "NOT_EXTERNAL_CLAIM_ELIGIBLE"
    return True, None


def _track_by_pillar(edges: list[dict[str, Any]]) -> dict[str, str]:
    candidates: dict[str, set[str]] = {}
    for edge in edges:
        if edge.get("edge_type") != "career_track_contains_pillar":
            continue
        pillar = str(edge.get("target_node_id") or "").strip()
        track = str(edge.get("source_node_id") or "").strip()
        if pillar and track:
            candidates.setdefault(pillar, set()).add(track)
    ambiguous = {pillar: tracks for pillar, tracks in candidates.items() if len(tracks) != 1}
    if ambiguous:
        raise GraphAuthorityReconciliationError(
            f"ambiguous career-track pillar authority: {ambiguous}"
        )
    return {pillar: next(iter(tracks)) for pillar, tracks in candidates.items()}


def _domain_taxonomy(
    nodes: list[dict[str, Any]],
) -> dict[str, tuple[str, str]]:
    taxonomy = dict(C03_DOMAIN_TAXONOMY)
    for node in nodes:
        domain_id = str(node.get("node_id") or "").strip()
        track = str(node.get("career_track") or "").strip()
        if domain_id in taxonomy and track and taxonomy[domain_id][0] != track:
            raise GraphAuthorityReconciliationError(
                f"catalog track drift for {domain_id}: {track}"
            )
    return taxonomy


def _edge(
    *,
    edge_id: str,
    edge_type: str,
    source: str,
    target: str,
    rationale: str,
    external_claim_policy: str,
) -> dict[str, Any]:
    return {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "source_node_id": source,
        "target_node_id": target,
        "rationale": rationale,
        "projection_behavior": "graph_traversal",
        "external_claim_policy": external_claim_policy,
        "validation_status": "validated",
    }


def _new_skill_node(row: Mapping[str, Any]) -> dict[str, Any]:
    skill_id = str(row["skill_id"])
    phrases = _strings(row.get("allowed_phrases"))
    snippets = _strings(row.get("source_snippets"))
    source_refs = sorted(set(_strings(row.get("fact_id_links")) + _strings(row.get("source_resume_files"))))
    return {
        "node_id": skill_id,
        "node_type": "skill_row",
        "label": phrases[0] if phrases else skill_id,
        "description": snippets[0] if snippets else f"Canonical skill identity for {skill_id}.",
        "support_level": str(row.get("support_level") or "INTERNAL_ONLY"),
        "visibility_rule": str(row.get("visibility_rule") or "never_external"),
        "activation_status": str(row.get("activation_status") or "DRAFT"),
        "evidence_risk": str(row.get("evidence_risk") or "high").lower(),
        "source_refs": source_refs,
        "projection_behavior": "non_retrieval_identity",
        "external_claim_policy": "skill_projection_not_proof",
    }


def reconcile_graph_authority(ledger: dict[str, Any]) -> dict[str, Any]:
    """Return a zero-loss, idempotent authority-closed graph payload."""
    payload = copy.deepcopy(ledger)
    rows = payload.get("skill_rows")
    nodes = payload.get("graph_nodes")
    edges = payload.get("graph_edges")
    if not isinstance(rows, list) or not isinstance(nodes, list) or not isinstance(edges, list):
        raise GraphAuthorityReconciliationError("ledger rows, nodes, and edges must be lists")

    track_by_pillar = _track_by_pillar(edges)
    domain_taxonomy = _domain_taxonomy(nodes)
    node_by_id = {
        str(node.get("node_id") or "").strip(): node
        for node in nodes
        if isinstance(node, dict) and str(node.get("node_id") or "").strip()
    }

    existing_triples = {
        (
            str(edge.get("edge_type") or ""),
            str(edge.get("source_node_id") or ""),
            str(edge.get("target_node_id") or ""),
        )
        for edge in edges
        if isinstance(edge, dict)
    }
    additions: list[dict[str, Any]] = []
    eligible_count = 0

    for row in rows:
        if not isinstance(row, dict):
            raise GraphAuthorityReconciliationError("skill_rows entries must be objects")
        skill_id = str(row.get("skill_id") or "").strip()
        if not skill_id:
            raise GraphAuthorityReconciliationError("skill row has blank skill_id")

        domain_id = str(row.get("domain_id") or "").strip()
        pillar = str(row.get("pillar") or "").strip()
        if not domain_id:
            domain_id = _PILLAR_DOMAIN_OVERRIDES.get(pillar, pillar if pillar in domain_taxonomy else "")
            if not domain_id:
                raise GraphAuthorityReconciliationError(f"no domain authority for {skill_id}")
            row["domain_id"] = domain_id

        track = str(row.get("career_track_id") or "").strip()
        epoch = str(row.get("career_epoch") or "").strip()
        domain_assignment = domain_taxonomy.get(domain_id)
        if not track:
            track = (domain_assignment or (None, None))[0] or track_by_pillar.get(pillar, "")
            if not track:
                raise GraphAuthorityReconciliationError(f"no career-track authority for {skill_id}")
            row["career_track_id"] = track
        if not epoch:
            epoch = (domain_assignment or (None, None))[1] or ""
            if not epoch:
                raise GraphAuthorityReconciliationError(f"no career-epoch authority for {skill_id}")
            row["career_epoch"] = epoch

        hop_path = row.get("graph_hop_path")
        if isinstance(hop_path, list) and hop_path and str(hop_path[0]) == "track_unknown":
            hop_path[0] = track

        eligible, reason = classify_assertion_eligibility(row)
        row["retrieval_eligible"] = eligible
        if eligible:
            row.pop("retrieval_ineligibility_reason", None)
            eligible_count += 1
        else:
            row["retrieval_ineligibility_reason"] = reason

        node = node_by_id.get(skill_id)
        if node is None:
            node = _new_skill_node(row)
            nodes.append(node)
            node_by_id[skill_id] = node
        source_refs = sorted(
            set(_strings(node.get("source_refs")))
            | set(_strings(row.get("fact_id_links")))
            | set(_strings(row.get("source_resume_files")))
        )
        node["source_refs"] = source_refs
        node["retrieval_eligible"] = eligible
        if eligible:
            node.pop("retrieval_ineligibility_reason", None)
        else:
            node["retrieval_ineligibility_reason"] = reason
            node["external_claim_policy"] = "skill_projection_not_proof"
            node["projection_behavior"] = "non_retrieval_identity"

        required_edges = [
            (
                "capability_domain_contains_skill",
                domain_id,
                skill_id,
                f"edge:authority_domain:{domain_id}->{skill_id}",
                "Canonical skill-row domain authority",
            ),
            (
                "epoch_contains_skill",
                epoch,
                skill_id,
                f"edge:authority_epoch:{epoch}->{skill_id}",
                "Canonical skill-row career-epoch authority",
            ),
        ]
        for fact_id in _strings(row.get("fact_id_links")):
            required_edges.append(
                (
                    "skill_supported_by_fact",
                    skill_id,
                    fact_id,
                    f"edge:authority_fact:{skill_id}->{fact_id}",
                    "Exact canonical skill-row fact binding",
                )
            )
        for edge_type, source, target, edge_id, rationale in required_edges:
            triple = (edge_type, source, target)
            if triple in existing_triples:
                continue
            additions.append(
                _edge(
                    edge_id=edge_id,
                    edge_type=edge_type,
                    source=source,
                    target=target,
                    rationale=rationale,
                    external_claim_policy=(
                        str(row.get("external_claim_policy") or "skill_projection_not_proof")
                        if eligible
                        else "skill_projection_not_proof"
                    ),
                )
            )
            existing_triples.add(triple)

    identity = node_by_id.get("identity_amit_ayer_governed_ai_platform_leader")
    if identity is not None:
        identity["external_claim_policy"] = "skill_projection_not_proof"
        identity["projection_behavior"] = "identity_anchor_not_claim_proof"

    edges.extend(sorted(additions, key=lambda edge: edge["edge_id"]))
    graph_metadata = payload.setdefault("graph_metadata", {})
    graph_metadata["node_count"] = len(nodes)
    graph_metadata["edge_count"] = len(edges)
    metadata = payload.setdefault("metadata", {})
    metadata["skill_row_count"] = len(rows)
    metadata["c03_graph_authority_reconciliation"] = {
        "version": RECONCILIATION_VERSION,
        "canonical_skill_count": len(rows),
        "eligible_assertion_count": eligible_count,
        "non_retrieval_eligible_count": len(rows) - eligible_count,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }
    return payload


__all__ = [
    "C03_DOMAIN_TAXONOMY",
    "GraphAuthorityReconciliationError",
    "RECONCILIATION_VERSION",
    "classify_assertion_eligibility",
    "reconcile_graph_authority",
]
