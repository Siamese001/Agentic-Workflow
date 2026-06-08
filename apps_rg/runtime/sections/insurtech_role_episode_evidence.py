"""InsurTech role-episode evidence — proof-pool attachment + evidence-pack markers.

Mirror of ibm_role_episode_evidence.py (plan apps-rg-insurtech-ey-unlock-a4c0f0 W2/P2). Makes the
insurtech_bullets/insurtech_narrative proof pool non-empty by attaching graph-backed role-episode
bundles (each anchored to a base-resume bullet) to the proof_pool_metadata. Identity is verbatim
from the base resume; skills are grounded in real graph nodes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.sections.insurtech_graph_role_episode_registry import (
    INSURTECH_EMPLOYER_ID,
    INSURTECH_EMPLOYER_NODE_ID,
    INSURTECH_TIME_WINDOW,
    get_bundles_for_section,
    validate_bundle,
)

GRAPH_BULLET_EVIDENCE_PACK_MARKER = "INSURTECH_ROLE_EPISODE_EVIDENCE_PACK"
INSURTECH_ROLE_EPISODE_EVIDENCE_MARKER = GRAPH_BULLET_EVIDENCE_PACK_MARKER

INSURTECH_BULLET_SLOT_IDS: tuple[str, ...] = (
    "bul_insurtech_001",
    "bul_insurtech_002",
    "bul_insurtech_003",
)

# One primary role episode bundle per bullet slot (employer-bound themes; anchors base-resume bullets).
INSURTECH_BULLET_SLOT_BUNDLE_MAP: dict[str, str] = {
    "bul_insurtech_001": "reb_insurtech_legacy_cloud_modernization",
    "bul_insurtech_002": "reb_insurtech_cloud_governance_security",
    "bul_insurtech_003": "reb_insurtech_operational_resilience",
}

# Base-resume InsurTech metrics are HELD (single canonical source), none promotable pre-X2 (P4).
PROMOTABLE_METRIC_OUTCOME_IDS: tuple[str, ...] = ()

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
    """Map bundle promotable_metrics to stable outcome IDs. Empty pre-X2 (metrics are HELD)."""
    return []


def build_insurtech_role_episode_section_packet(
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
                "time_window": bundle["time_window"],
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "linked_archive_signal_ids": list(bundle.get("linked_archive_signal_ids") or []),
                "allowed_metric_outcome_ids": _bundle_allowed_metric_outcome_ids(bundle),
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
        "employer": INSURTECH_EMPLOYER_ID,
        "employer_node_id": INSURTECH_EMPLOYER_NODE_ID,
        "time_window": INSURTECH_TIME_WINDOW,
        "role_episode_bundles": bundle_records,
        "role_episode_bundle_ids": [b["role_episode_bundle_id"] for b in bundle_records],
        "consumption_mode": "role_episode_bundle_required",
        "flat_skill_only_forbidden": True,
        "promotable_metric_outcome_ids": list(PROMOTABLE_METRIC_OUTCOME_IDS),
        "forbidden_metric_substrings": list(FORBIDDEN_METRIC_SUBSTRINGS),
    }


def attach_role_episode_bundles_to_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Merge role episode bundle packet into proof_pool_metadata (insurtech_* sections only)."""
    if section_id not in ("insurtech_bullets", "insurtech_narrative"):
        return meta
    packet = build_insurtech_role_episode_section_packet(section_id, repo_root=repo_root)
    out = dict(meta)
    out["role_episode_bundle_consumption"] = True
    out["role_episode_bundle_consumption_mode"] = "role_episode_bundle_required"
    out["role_episode_bundles"] = packet["role_episode_bundles"]
    out["role_episode_bundle_ids"] = packet["role_episode_bundle_ids"]
    out["insurtech_role_episode_section_packet"] = packet
    out["graph_expansion_consumes_role_episode_bundles"] = True
    out["flat_skill_only_graph_context_forbidden"] = True
    return out


__all__ = [
    "GRAPH_BULLET_EVIDENCE_PACK_MARKER",
    "INSURTECH_BULLET_SLOT_BUNDLE_MAP",
    "INSURTECH_BULLET_SLOT_IDS",
    "INSURTECH_ROLE_EPISODE_EVIDENCE_MARKER",
    "PROMOTABLE_METRIC_OUTCOME_IDS",
    "attach_role_episode_bundles_to_proof_pool_metadata",
    "build_insurtech_role_episode_section_packet",
]
