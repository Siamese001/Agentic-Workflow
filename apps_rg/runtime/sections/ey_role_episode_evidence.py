"""EY role-episode evidence — proof-pool attachment + evidence-pack markers.

Mirror of ibm_role_episode_evidence.py (plan apps-rg-insurtech-ey-unlock-a4c0f0 W2/P2). Makes the
ey_bullets/ey_narrative proof pool non-empty by attaching graph-backed role-episode bundles to the
proof_pool_metadata. Identity is employment-spine only; skills and claims are grounded in real
graph nodes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.sections.ey_graph_role_episode_registry import (
    BUNDLES_PATH as EY_BUNDLES_PATH,
    EY_EMPLOYER_ID,
    EY_EMPLOYER_NODE_ID,
    EY_TIME_WINDOW,
    get_bundles_for_section,
    validate_bundle,
)
from apps_rg.runtime.sections.role_episode_metric_registry import (
    approved_metric_outcome_ids_from_path,
    metric_outcome_nodes_from_path,
)
from apps_rg.runtime.sections.role_episode_bullet_sufficiency import (
    build_role_episode_bullet_traversal_sufficiency_receipt,
)

GRAPH_BULLET_EVIDENCE_PACK_MARKER = "EY_ROLE_EPISODE_EVIDENCE_PACK"
EY_ROLE_EPISODE_EVIDENCE_MARKER = GRAPH_BULLET_EVIDENCE_PACK_MARKER

EY_BULLET_SLOT_IDS: tuple[str, ...] = (
    "bul_ey_001",
    "bul_ey_002",
    "bul_ey_003",
)

# Output slots remain presentation ids; claim evidence uses role_episode_bundle_id.
EY_BULLET_SLOT_BUNDLE_MAP: dict[str, str] = {
    "bul_ey_001": "reb_ey_regulatory_analytics_modernization",
    "bul_ey_002": "reb_ey_ccar_capital_liquidity_stress_testing",
    "bul_ey_003": "reb_ey_capital_optimization_solvency",
}

def _ey_metric_outcome_nodes() -> dict[str, dict[str, Any]]:
    return metric_outcome_nodes_from_path(EY_BUNDLES_PATH)


# Graph-native allow-list for approved EY metric binding.
PROMOTABLE_METRIC_OUTCOME_IDS: tuple[str, ...] = approved_metric_outcome_ids_from_path(
    EY_BUNDLES_PATH
)

FORBIDDEN_METRIC_SUBSTRINGS: tuple[str, ...] = (
    "25%", "30%", "35%", "50%",
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


def _bundle_allowed_metric_outcome_ids(bundle: dict[str, Any]) -> list[str]:
    """Return graph-native metric outcome IDs linked to this bundle."""
    linked = [str(x) for x in (bundle.get("linked_metric_outcome_ids") or []) if str(x).strip()]
    if linked:
        return linked
    nodes = _ey_metric_outcome_nodes()
    return [
        mid
        for mid, node in nodes.items()
        if bundle.get("role_episode_bundle_id") in (node.get("bundle_bindings") or [])
    ]


def build_ey_graph_traversal_sufficiency_receipt(
    *,
    section_id: str = "ey_bullets",
    slot_bundle_map: dict[str, str] | None = None,
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Receipt proving EY final slots select from the larger role frontier."""
    pkt = packet or build_ey_role_episode_section_packet(section_id)
    return build_role_episode_bullet_traversal_sufficiency_receipt(
        section_id=section_id,
        slot_ids=EY_BULLET_SLOT_IDS,
        slot_bundle_map=slot_bundle_map or dict(EY_BULLET_SLOT_BUNDLE_MAP),
        packet=pkt,
        employer_label="EY",
    )


def build_ey_role_episode_section_packet(
    section_id: str,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build machine-readable role episode packet for a section (C0.3 / proof_pool metadata)."""
    bundles = get_bundles_for_section(section_id)
    skill_index = _skill_rows_by_id(repo_root)
    bundle_records: list[dict[str, Any]] = []
    for bundle in bundles:
        is_valid, violations = validate_bundle(bundle)
        if not is_valid:
            raise ValueError(
                f"Invalid role episode bundle {bundle.get('role_episode_bundle_id')}: {violations}"
            )
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
        bundle_records.append(
            {
                "role_episode_bundle_id": bundle["role_episode_bundle_id"],
                "employer": bundle["employer"],
                "employer_node_id": bundle["employer_node_id"],
                "title": bundle.get("title"),
                "time_window": EY_TIME_WINDOW,
                "bundle_theme": bundle.get("bundle_theme"),
                "claim_text": bundle.get("claim_text"),
                "support_level": bundle.get("support_level"),
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "linked_archive_signal_ids": list(bundle.get("linked_archive_signal_ids") or []),
                "allowed_metric_outcome_ids": _bundle_allowed_metric_outcome_ids(bundle),
                "metric_candidates": list(bundle.get("metric_candidates") or []),
                "held_metrics": list(bundle.get("held_metrics") or []),
                "excluded_metrics": list(bundle.get("excluded_metrics") or []),
                "executive_scope_signals": list(bundle.get("executive_scope_signals") or []),
                "architecture_scope_signals": list(bundle.get("architecture_scope_signals") or []),
                "operating_context": bundle.get("operating_context"),
                "bullet_intent": bundle.get("bullet_intent"),
                "section_eligibility": list(bundle.get("section_eligibility") or []),
                "bound_skills": skill_nodes,
            }
        )
    return {
        "section_id": section_id,
        "employer": EY_EMPLOYER_ID,
        "employer_node_id": EY_EMPLOYER_NODE_ID,
        "time_window": EY_TIME_WINDOW,
        "role_episode_bundles": bundle_records,
        "role_episode_bundle_ids": [b["role_episode_bundle_id"] for b in bundle_records],
        "consumption_mode": "role_episode_bundle_required",
        "flat_skill_only_forbidden": True,
        "promotable_metric_outcome_ids": list(PROMOTABLE_METRIC_OUTCOME_IDS),
        "approved_metric_outcome_ids": list(PROMOTABLE_METRIC_OUTCOME_IDS),
        "forbidden_metric_substrings": list(FORBIDDEN_METRIC_SUBSTRINGS),
        "base_resume_usage": "identity_spine_only",
        "graph_claim_authority_ids": [b["role_episode_bundle_id"] for b in bundle_records],
    }


def attach_role_episode_bundles_to_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Merge role episode bundle packet into proof_pool_metadata (ey_* sections only)."""
    if section_id not in ("ey_bullets", "ey_narrative"):
        return meta
    packet = build_ey_role_episode_section_packet(section_id, repo_root=repo_root)
    out = dict(meta)
    out["role_episode_bundle_consumption"] = True
    out["role_episode_bundle_consumption_mode"] = "role_episode_bundle_required"
    out["role_episode_bundles"] = packet["role_episode_bundles"]
    out["role_episode_bundle_ids"] = packet["role_episode_bundle_ids"]
    out["ey_role_episode_section_packet"] = packet
    out["graph_expansion_consumes_role_episode_bundles"] = True
    out["flat_skill_only_graph_context_forbidden"] = True
    out["approved_metric_outcome_ids"] = packet["approved_metric_outcome_ids"]
    return out


__all__ = [
    "EY_BULLET_SLOT_BUNDLE_MAP",
    "EY_BULLET_SLOT_IDS",
    "EY_ROLE_EPISODE_EVIDENCE_MARKER",
    "GRAPH_BULLET_EVIDENCE_PACK_MARKER",
    "PROMOTABLE_METRIC_OUTCOME_IDS",
    "attach_role_episode_bundles_to_proof_pool_metadata",
    "build_ey_graph_traversal_sufficiency_receipt",
    "build_ey_role_episode_section_packet",
]
