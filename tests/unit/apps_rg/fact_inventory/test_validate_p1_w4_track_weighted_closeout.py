"""P1-W4 closeout validator — fail-closed contract gates."""
from __future__ import annotations

import pytest

from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    TrackWeightedExpansionContractError,
)
from apps_rg.fact_inventory.validate_p1_w4_track_weighted_closeout import (
    validate_p1_w4_track_weighted_closeout,
)


def test_validator_rejects_not_bound() -> None:
    with pytest.raises(TrackWeightedExpansionContractError) as exc:
        validate_p1_w4_track_weighted_closeout(
            {
                "c03_graph_bound_status": "NOT_BOUND",
                "c03_graph_hop_paths_count": 5,
                "graph_hop_paths_sample": [[{"edge_type": "career_track_contains_pillar"}]],
                "non_graph_evidence_items_count": 0,
                "broad_skills_ledger_used_as_authority": False,
                "graph_expansion_mode": "TRACK_WEIGHTED_MULTI_HOP",
                "graph_hop_edge_types_used": ["career_track_contains_pillar"],
                "c03_binding_surface": "apps_rg/fact_inventory/track_weighted_graph_expansion",
                "c03_graph_expansion_ref": "ref:graph:track_weighted_expansion:abc",
                "c03_selected_tracks": ["track_a", "track_b"],
                "skills_authority_source_type": "augmented_skills_graph",
            }
        )
    assert "BOUND" in str(exc.value)


def test_validator_rejects_missing_hops() -> None:
    with pytest.raises(TrackWeightedExpansionContractError):
        validate_p1_w4_track_weighted_closeout(
            {
                "c03_graph_bound_status": "BOUND",
                "c03_graph_hop_paths_count": 0,
                "graph_hop_paths_sample": [],
                "non_graph_evidence_items_count": 0,
                "broad_skills_ledger_used_as_authority": False,
                "graph_expansion_mode": "TRACK_WEIGHTED_MULTI_HOP",
                "graph_hop_edge_types_used": [],
                "c03_binding_surface": "x",
                "c03_graph_expansion_ref": "ref:graph:track_weighted_expansion:abc",
                "c03_selected_tracks": ["track_a", "track_b"],
                "skills_authority_source_type": "augmented_skills_graph",
            }
        )


def test_validator_rejects_broad_skills_ledger_authority() -> None:
    with pytest.raises(TrackWeightedExpansionContractError):
        validate_p1_w4_track_weighted_closeout(
            {
                "c03_graph_bound_status": "BOUND",
                "c03_graph_hop_paths_count": 2,
                "graph_hop_paths_sample": [[{"edge_type": "x"}]],
                "non_graph_evidence_items_count": 0,
                "broad_skills_ledger_used_as_authority": True,
                "graph_expansion_mode": "TRACK_WEIGHTED_MULTI_HOP",
                "graph_hop_edge_types_used": ["x"],
                "c03_binding_surface": "x",
                "c03_graph_expansion_ref": "ref:graph:track_weighted_expansion:abc",
                "c03_selected_tracks": ["track_a", "track_b"],
                "skills_authority_source_type": "broad_skills_ledger",
            }
        )


def test_validator_rejects_single_track_hybrid() -> None:
    with pytest.raises(TrackWeightedExpansionContractError):
        validate_p1_w4_track_weighted_closeout(
            {
                "c03_graph_bound_status": "BOUND",
                "c03_graph_hop_paths_count": 1,
                "graph_hop_paths_sample": [[{"edge_type": "career_track_contains_pillar"}]],
                "non_graph_evidence_items_count": 0,
                "broad_skills_ledger_used_as_authority": False,
                "graph_expansion_mode": "TRACK_WEIGHTED_MULTI_HOP",
                "graph_hop_edge_types_used": ["career_track_contains_pillar"],
                "c03_binding_surface": "x",
                "c03_graph_expansion_ref": "ref:graph:track_weighted_expansion:abc",
                "c03_selected_tracks": ["track_genai_agentic"],
                "skills_authority_source_type": "augmented_skills_graph",
            },
            hybrid_fixture=True,
            min_tracks_with_facts=2,
        )
