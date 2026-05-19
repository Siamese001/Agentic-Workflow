"""P1-W4 closeout validator — C0.3 binding + hybrid track coverage + authority."""
from __future__ import annotations

from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import assert_skills_not_broad_ledger_authority
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    GRAPH_EXPANSION_MODE_TRACK_WEIGHTED,
    TrackWeightedExpansionContractError,
)


def validate_p1_w4_track_weighted_closeout(
    payload: dict[str, Any],
    *,
    hybrid_fixture: bool = True,
    min_tracks_with_facts: int = 2,
) -> None:
    """Fail closed when P1-W4 C0.3 binding or hybrid contract is not met."""
    errors: list[str] = []

    if str(payload.get("c03_graph_bound_status") or "") != "BOUND":
        errors.append(
            f"c03_graph_bound_status must be BOUND; got {payload.get('c03_graph_bound_status')!r}"
        )

    hop_count = int(payload.get("c03_graph_hop_paths_count") or 0)
    if hop_count < 1:
        errors.append("c03_graph_hop_paths_count must be >= 1")

    sample = payload.get("graph_hop_paths_sample") or []
    if not sample and hop_count < 1:
        errors.append("graph hop paths missing")

    if int(payload.get("non_graph_evidence_items_count") or 0) > 0:
        errors.append(
            f"non_graph_evidence_items_count must be 0; got {payload.get('non_graph_evidence_items_count')}"
        )

    if payload.get("broad_skills_ledger_used_as_authority") is True:
        errors.append("broad_skills_ledger_used_as_authority must be false")

    if str(payload.get("graph_expansion_mode") or "") != GRAPH_EXPANSION_MODE_TRACK_WEIGHTED:
        errors.append(
            f"graph_expansion_mode must be {GRAPH_EXPANSION_MODE_TRACK_WEIGHTED}; "
            f"got {payload.get('graph_expansion_mode')!r}"
        )

    edge_types = payload.get("graph_hop_edge_types_used") or []
    if not edge_types:
        errors.append("graph_hop_edge_types_used must be non-empty")

    if not str(payload.get("c03_binding_surface") or "").strip():
        errors.append("c03_binding_surface required")

    if not str(payload.get("c03_graph_expansion_ref") or "").strip():
        errors.append("c03_graph_expansion_ref required")

    tracks = list(payload.get("c03_selected_tracks") or payload.get("tracks_with_facts") or [])
    if hybrid_fixture and len(tracks) < min_tracks_with_facts:
        errors.append(
            f"hybrid fixture requires >={min_tracks_with_facts} tracks; got {tracks}"
        )

    try:
        assert_skills_not_broad_ledger_authority(payload)
    except ValueError as exc:
        errors.append(str(exc))

    if errors:
        raise TrackWeightedExpansionContractError("; ".join(errors))


def main() -> None:
    """CLI: validate hybrid P1-W4 expansion + closeout receipt on disk."""
    import json
    from pathlib import Path

    from apps_rg.fact_inventory.track_weighted_graph_expansion import (
        HYBRID_JD_FIXTURE,
        ROOT,
        build_track_weighted_expansion,
        infer_projection_role_family_key,
        load_augmented_skills_graph,
    )

    graph = load_augmented_skills_graph(repo_root=ROOT)
    role_key = infer_projection_role_family_key(
        target_role="SVP Engineering Agentic AI",
        jd_text=HYBRID_JD_FIXTURE,
    )
    hybrid = build_track_weighted_expansion(
        graph=graph,
        role_family_key=role_key,
        jd_text=HYBRID_JD_FIXTURE,
        enforce_hybrid_contract=True,
        bind_c03=True,
        repo_root=ROOT,
    )
    validate_p1_w4_track_weighted_closeout(hybrid)

    closeout_path = ROOT / "docs/reports/apps_rg/career_track_p1_w4_closeout_receipt.json"
    if closeout_path.is_file():
        closeout = json.loads(closeout_path.read_text(encoding="utf-8"))
        proof = {**hybrid, **(closeout.get("c03_binding_proof") or {})}
        validate_p1_w4_track_weighted_closeout(proof)

    print(
        json.dumps(
            {
                "status": "PASS",
                "c03_graph_bound_status": hybrid.get("c03_graph_bound_status"),
                "tracks_with_facts": hybrid.get("tracks_with_facts"),
                "closeout_receipt": str(closeout_path) if closeout_path.is_file() else None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()


__all__ = ["validate_p1_w4_track_weighted_closeout", "main"]
