"""Employer role-episode graphs must not use base-resume bullet artifacts as proof."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FI = REPO / "apps_rg" / "fact_inventory"

GRAPH_FILES = [
    FI / "unify_role_episode_bundles.json",
    FI / "ibm_role_episode_bundles.json",
    FI / "insurtech_role_episode_bundles.json",
    FI / "ey_role_episode_bundles.json",
]

FORBIDDEN_BULLET_PREFIXES = ("bul_unify_", "bul_ibm_", "bul_insurtech_", "bul_ey_")
FORBIDDEN_PROVENANCE_PHRASES = (
    "base_resume anchored",
    "base-resume anchored",
    "canonical single source bul_",
)


def test_role_episode_graphs_exclude_base_resume_bullet_artifacts() -> None:
    for path in GRAPH_FILES:
        raw = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_PROVENANCE_PHRASES:
            assert phrase not in raw, f"{path.name} contains vestigial provenance phrase {phrase!r}"
        for prefix in FORBIDDEN_BULLET_PREFIXES:
            assert prefix not in raw, f"{path.name} contains base/output bullet id {prefix!r}"


def test_role_episode_graphs_mark_base_resume_identity_only() -> None:
    for path in GRAPH_FILES:
        doc = json.loads(path.read_text(encoding="utf-8"))
        invariants = doc.get("invariants") or {}
        assert invariants.get("base_resume_hydration_excluded") is True
        assert invariants.get("base_resume_claim_authority") is False
        assert invariants.get("base_resume_bullet_ids_excluded") is True
        assert invariants.get("identity_spine_only") is True
        assert invariants.get("graph_bundle_id_claim_authority") is True
        for bundle in doc.get("bundles") or []:
            linked = bundle.get("linked_source_fact_ids") or []
            assert all(
                not str(source_id).startswith(FORBIDDEN_BULLET_PREFIXES)
                for source_id in linked
            ), f"{path.name}:{bundle.get('role_episode_bundle_id')} linked to bullet id"
