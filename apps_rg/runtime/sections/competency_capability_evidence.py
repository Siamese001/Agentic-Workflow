"""Competency capability bundle evidence — C0 consumption for the competencies section.

Proof authority is graph-backed competency capability bundles plus linked source facts,
not generic taxonomy labels, flat skill lists, or default_fid backfill. Base resume and
archive material are calibration/provenance only — never prose hydration.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.sections.competency_capability_registry import (
    REQUIRED_CAPABILITY_FAMILIES,
    get_bundles_for_section,
    validate_competency_bundle,
)

COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER = "COMPETENCY_CAPABILITY_EVIDENCE_PACK"

_AUTHORITY_HEADER_LINES: tuple[str, ...] = (
    "proof_authority = graph_competency_bundles_plus_linked_source_facts",
    "base_resume_usage = calibration_only",
    "archive_usage = provenance_inventory_only",
    "jd_usage = targeting_only",
    "examples_usage = style_only",
    "generic_taxonomy_label = display_wrapper_only_not_proof",
    "flat_skill_list_or_default_fid_support = forbidden",
    (
        "Generate the competencies section organically from competency capability bundles. "
        "Do not copy or paraphrase base resume or archive competency text. "
        "Preserve or exceed the base resume's rigor, specificity, and senior executive engineering signal."
    ),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _skill_rows_by_id(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    graph = load_augmented_skills_graph(repo_root=repo_root or _repo_root())
    out: dict[str, dict[str, Any]] = {}
    for row in graph.get("skill_rows") or []:
        if isinstance(row, dict):
            sid = str(row.get("skill_id") or "").strip()
            if sid:
                out[sid] = row
    return out


def build_competency_capability_section_packet(
    section_id: str = "competencies",
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build machine-readable competency capability packet (proof_pool metadata / C0)."""
    bundles = get_bundles_for_section(section_id)
    skill_index = _skill_rows_by_id(repo_root)
    records: list[dict[str, Any]] = []
    families_present: set[str] = set()
    graph_skill_node_ids_by_category: dict[str, list[str]] = {}
    source_fact_ids_by_category: dict[str, list[str]] = {}

    for bundle in bundles:
        ok, violations = validate_competency_bundle(bundle)
        if not ok:
            raise ValueError(
                f"Invalid competency bundle {bundle.get('competency_bundle_id')}: {violations}"
            )
        families_present.add(str(bundle.get("capability_family") or ""))
        skill_nodes: list[dict[str, Any]] = []
        for sid in bundle.get("graph_skill_node_ids") or []:
            row = skill_index.get(str(sid))
            if row:
                skill_nodes.append(
                    {
                        "skill_id": sid,
                        "allowed_phrases": list(row.get("allowed_phrases") or [])[:6],
                        "activation_status": row.get("activation_status"),
                        "confidence_grade": row.get("confidence_grade"),
                    }
                )
            else:
                skill_nodes.append({"skill_id": sid, "allowed_phrases": []})
        for cat_id in bundle.get("target_taxonomy_category_ids") or []:
            graph_skill_node_ids_by_category.setdefault(str(cat_id), [])
            for sid in bundle.get("graph_skill_node_ids") or []:
                if sid not in graph_skill_node_ids_by_category[str(cat_id)]:
                    graph_skill_node_ids_by_category[str(cat_id)].append(str(sid))
            source_fact_ids_by_category.setdefault(str(cat_id), [])
            for fid in bundle.get("linked_source_fact_ids") or []:
                if fid not in source_fact_ids_by_category[str(cat_id)]:
                    source_fact_ids_by_category[str(cat_id)].append(str(fid))
        records.append(
            {
                "competency_bundle_id": bundle["competency_bundle_id"],
                "capability_family": bundle["capability_family"],
                "display_label_candidate": bundle["display_label_candidate"],
                "target_taxonomy_category_ids": list(bundle.get("target_taxonomy_category_ids") or []),
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "employer_bindings": list(bundle.get("employer_bindings") or []),
                "role_episode_bindings": list(bundle.get("role_episode_bindings") or []),
                "evidence_strength": bundle.get("evidence_strength"),
                "external_claim_policy": bundle.get("external_claim_policy"),
                "activation_status": bundle.get("activation_status"),
                "base_rigor_family_match": bundle.get("base_rigor_family_match"),
                "seniority_signal": bundle.get("seniority_signal"),
                "technical_density_signal": bundle.get("technical_density_signal"),
                "commercial_or_operating_scope_signal": bundle.get("commercial_or_operating_scope_signal"),
                "target_relevance_rationale": bundle.get("target_relevance_rationale"),
                "vocabulary_anchors": list(bundle.get("vocabulary_anchors") or []),
                "bound_skills": skill_nodes,
            }
        )

    return {
        "section_id": section_id,
        "proof_authority": "graph_competency_bundles_plus_linked_source_facts",
        "base_resume_usage": "calibration_only",
        "archive_usage": "provenance_inventory_only",
        "jd_usage": "targeting_only",
        "examples_usage": "style_only",
        "competency_bundles": records,
        "competency_bundle_ids": [r["competency_bundle_id"] for r in records],
        "capability_families_present": sorted(f for f in families_present if f),
        "required_capability_families": list(REQUIRED_CAPABILITY_FAMILIES),
        "graph_skill_node_ids_by_category": graph_skill_node_ids_by_category,
        "source_fact_ids_by_category": source_fact_ids_by_category,
        "consumption_mode": "competency_bundle_required",
        "flat_taxonomy_only_forbidden": True,
        "default_fid_only_support_forbidden": True,
    }


def attach_competency_bundles_to_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str = "competencies",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Merge competency capability packet into proof_pool_metadata (competencies only)."""
    if section_id != "competencies":
        return meta
    packet = build_competency_capability_section_packet(section_id, repo_root=repo_root)
    out = dict(meta)
    out["competency_capability_bundle_consumption"] = True
    out["competency_capability_bundle_consumption_mode"] = "competency_bundle_required"
    out["competency_capability_bundles"] = packet["competency_bundles"]
    out["competency_bundle_ids"] = packet["competency_bundle_ids"]
    out["competency_capability_section_packet"] = packet
    out["graph_expansion_consumes_competency_bundles"] = True
    out["flat_taxonomy_only_graph_context_forbidden"] = True
    return out


def is_flat_taxonomy_only_packet(packet: dict[str, Any]) -> bool:
    """True when graph context is only generic taxonomy with no bundle/skill binding."""
    if packet.get("competency_bundle_id") or packet.get("competency_bundle_ids"):
        return False
    if packet.get("competency_bundles"):
        return False
    inner = packet.get("competency_capability_section_packet") or {}
    if isinstance(inner, dict) and inner.get("competency_bundles"):
        return False
    if packet.get("graph_skill_node_ids") and not packet.get("competency_bundle_id"):
        return True
    return True


def format_competency_capability_evidence_pack(
    runtime_payload: dict[str, Any],
    *,
    section_id: str = "competencies",
) -> str:
    """C0 body: competency capability bundles as proof authority (graph-backed, per family)."""
    packet = build_competency_capability_section_packet(section_id)
    runtime_payload["competency_capability_section_packet"] = packet
    runtime_payload["competency_bundle_ids"] = packet["competency_bundle_ids"]

    header_lines = [
        f"{COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER} "
        "(proof substrate — compose categories from competency_bundle_id + bound_skills + linked source facts):",
        *_AUTHORITY_HEADER_LINES,
        "- Each emitted category MUST cite a competency_bundle_id and its graph_skill_node_ids.",
        "- Each major term MUST bind to graph_skill_node_ids and linked source_fact_ids or approved graph lineage.",
        "- Generic taxonomy labels may be display wrappers only — never proof on their own.",
        "- A term attached only to default_fid is NOT proof.",
        "- Required capability families to cover (>=7): "
        + ", ".join(REQUIRED_CAPABILITY_FAMILIES[:7]) + ".",
    ]
    header = "\n".join(header_lines)

    blocks: list[str] = []
    for rec in packet["competency_bundles"]:
        lines = [
            f"COMPETENCY_BUNDLE {rec['competency_bundle_id']} | family: {rec['capability_family']}",
            f"  display_label_candidate: {rec['display_label_candidate']}",
            f"  target_taxonomy_category_ids: {rec['target_taxonomy_category_ids']}",
            f"  graph_skill_node_ids: {rec['graph_skill_node_ids']}",
            f"  linked_source_fact_ids: {rec['linked_source_fact_ids']}",
            f"  evidence_strength: {rec['evidence_strength']} | activation: {rec['activation_status']}",
            f"  base_rigor_family_match: {rec['base_rigor_family_match']}",
            f"  seniority_signal: {rec['seniority_signal']} | technical_density_signal: {rec['technical_density_signal']}",
            f"  target_relevance_rationale: {rec['target_relevance_rationale']}",
            "  vocabulary_anchors (structured anchors only — no base/archive prose):",
        ]
        for anchor in rec.get("vocabulary_anchors") or []:
            lines.append(f"    - {anchor}")
        if rec.get("employer_bindings") or rec.get("role_episode_bindings"):
            lines.append(
                f"  bindings: employer={rec.get('employer_bindings')} role_episode={rec.get('role_episode_bindings')}"
            )
        blocks.append("\n".join(lines))

    return header + "\n\n" + "\n\n".join(blocks)


def stamp_competency_bundle_bindings(
    competencies: list[dict[str, Any]],
    *,
    packet: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Stamp competency_bundle_id + graph_skill_node_ids onto categories by taxonomy mapping.

    Runtime seam: makes the final output bind each category to a graph-backed bundle. Does
    not invent terms; only attaches graph lineage metadata for categories whose category_id
    is a target of a competency bundle.
    """
    if not isinstance(competencies, list):
        return competencies
    pkt = packet or build_competency_capability_section_packet("competencies")
    by_category: dict[str, dict[str, Any]] = {}
    for rec in pkt.get("competency_bundles") or []:
        for cat_id in rec.get("target_taxonomy_category_ids") or []:
            by_category.setdefault(str(cat_id), rec)
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        cid = str(cat.get("category_id") or "").strip()
        rec = by_category.get(cid)
        if not rec:
            continue
        cat["competency_bundle_id"] = rec["competency_bundle_id"]
        cat["capability_family"] = rec["capability_family"]
        existing_nodes = list(cat.get("graph_skill_node_ids") or [])
        for sid in rec.get("graph_skill_node_ids") or []:
            if sid not in existing_nodes:
                existing_nodes.append(sid)
        cat["graph_skill_node_ids"] = existing_nodes
    return competencies


__all__ = [
    "COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER",
    "attach_competency_bundles_to_proof_pool_metadata",
    "build_competency_capability_section_packet",
    "format_competency_capability_evidence_pack",
    "is_flat_taxonomy_only_packet",
    "stamp_competency_bundle_bindings",
]
