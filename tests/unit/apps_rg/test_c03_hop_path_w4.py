"""W4: track-weighted hop-path materialization + c0_graph_lane_receipt parity."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.track_weighted_graph_expansion import GRAPH_EXPANSION_MODE_TRACK_WEIGHTED
from apps_rg.runtime.c03_graphrag_bound import build_section_c03_graphrag_bound
from apps_rg.runtime.c0.c03_hop_path_materialization import (
    GraphHopPathAllowlistError,
    attach_track_weighted_hop_paths_to_c03_bound,
    materialize_c03_hop_paths,
)
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
from apps_rg.runtime.section_spine_terminology import (
    GRAPH_EXPANSION_MODE_INCIDENT_EDGE_V1,
    GRAPH_EXPANSION_MODE_TRACK_WEIGHTED_MULTI_HOP,
    GRAPH_HOP_PATHS_COUNT_SEMANTICS_TRACK_WEIGHTED,
)
from apps_rg.runtime.spine.c0_graph_lane_receipt import build_c0_graph_lane_receipt_from_bridge

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture
def brown_jd() -> str:
    path = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
    if not path.is_file():
        pytest.skip("Brown JD fixture missing")
    return path.read_text(encoding="utf-8")


def test_materialize_hop_paths_from_track_expansion() -> None:
    track = {
        "graph_expansion_mode": GRAPH_EXPANSION_MODE_TRACK_WEIGHTED,
        "selected_facts": [
            {
                "fact_id": "fact_exec_001",
                "career_track": "track_genai_agentic",
                "graph_hop_path": [
                    {"edge_type": "career_track_contains_pillar", "from": "t", "to": "p"},
                    {"edge_type": "skill_supported_by_fact", "from": "s", "to": "f"},
                ],
            }
        ],
    }
    doc = materialize_c03_hop_paths(
        track_expansion=track,
        allowed_fact_ids={"fact_exec_001"},
    )
    assert doc["graph_expansion_mode"] == GRAPH_EXPANSION_MODE_TRACK_WEIGHTED
    assert doc["graph_hop_paths_count"] == 1
    assert doc["graph_hop_paths_count_semantics"] == GRAPH_HOP_PATHS_COUNT_SEMANTICS_TRACK_WEIGHTED
    assert "fact_exec_001" in doc["graph_hop_paths_by_fact_id"]


def test_materialize_hop_paths_fails_when_allowed_ids_do_not_match() -> None:
    track = {
        "graph_expansion_mode": GRAPH_EXPANSION_MODE_TRACK_WEIGHTED,
        "selected_facts": [
            {
                "fact_id": "fact_exec_001",
                "graph_hop_path": [{"edge_type": "career_track_contains_pillar"}],
            }
        ],
    }
    with pytest.raises(GraphHopPathAllowlistError, match="do not match allowed_fact_ids"):
        materialize_c03_hop_paths(
            track_expansion=track,
            allowed_fact_ids={"fact_governance_001"},
        )


def test_attach_hop_paths_updates_c03_bound_and_evidence() -> None:
    c03 = build_section_c03_graphrag_bound(
        section_id="executive_summary",
        graph={"graph_edges": []},
        graph_ref="ref",
        graph_digest="d",
        selected_fact_ids=["fact_exec_001"],
    )
    track = {
        "graph_expansion_mode": GRAPH_EXPANSION_MODE_TRACK_WEIGHTED,
        "selected_facts": [
            {
                "fact_id": "fact_exec_001",
                "graph_hop_path": [{"edge_type": "career_track_contains_pillar"}],
            }
        ],
    }
    bound = attach_track_weighted_hop_paths_to_c03_bound(
        c03,
        track,
        allowed_fact_ids={"fact_exec_001"},
    )
    assert bound.get("graph_expansion_mode") == GRAPH_EXPANSION_MODE_TRACK_WEIGHTED_MULTI_HOP
    assert bound.get("graph_hop_paths_count", 0) >= 1
    items = bound["final_evidence_contract_snapshot"]["evidence_items"]
    assert any(isinstance(it.get("graph_hop_path"), list) and it["graph_hop_path"] for it in items)


def test_incident_edge_when_no_track_hops() -> None:
    doc = materialize_c03_hop_paths(track_expansion=None, incident_edge_refs_count=3)
    assert doc["graph_expansion_mode"] == GRAPH_EXPANSION_MODE_INCIDENT_EDGE_V1
    assert doc["graph_hop_paths_count"] == 0
    assert doc["graph_incident_edge_refs_count"] == 3


def test_c0_graph_lane_receipt_from_bridge_includes_hop_paths() -> None:
    bridge = {
        "section_id": "executive_summary",
        "proof_pool_metadata": {
            "c03_graphrag_bound": {
                "graph_expansion_mode": GRAPH_EXPANSION_MODE_TRACK_WEIGHTED_MULTI_HOP,
                "graph_hop_paths_by_fact_id": {"fact_a": [{"edge_type": "x"}]},
                "graph_hop_paths_count": 1,
                "graph_hop_paths_count_semantics": GRAPH_HOP_PATHS_COUNT_SEMANTICS_TRACK_WEIGHTED,
                "graph_hop_paths_sample": [[{"edge_type": "x"}]],
                "support_status": "SUPPORTED",
            }
        },
    }
    receipt = build_c0_graph_lane_receipt_from_bridge(bridge, section_id="executive_summary")
    assert receipt["graph_expansion_mode"] == GRAPH_EXPANSION_MODE_TRACK_WEIGHTED_MULTI_HOP
    assert receipt["graph_hop_paths_by_fact_id"].get("fact_a")
    assert receipt["graph_hop_paths_count"] == 1


def test_brown_exec_summary_pool_keeps_role_episode_bundle_fallback_non_proof(
    brown_jd: str,
) -> None:
    pool = resolve_section_proof_pool(
        section="executive_summary",
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        jd_text=brown_jd,
        product_visible=False,
    )

    meta = pool.proof_pool_metadata
    assert meta["track_weighted_seed_fallback_used"] is True
    assert meta["track_weighted_seed_namespace"] == "role_episode_bundle"
    assert meta["track_weighted_hop_paths_attached_to_c03"] is False
    assert (meta.get("graph_targeting_capsule") or {}).get("skill_ids")
    assert (meta.get("c03_graphrag_bound") or {}).get("graph_hop_paths_count") == 0


def test_anthropic_exec_summary_pool_falls_back_for_role_episode_bundle_seeds() -> None:
    jd_path = REPO / "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt"
    briefing_path = REPO / "artifacts/apps_research/runs/research-run-266d27c0bed5/briefing.md"
    if not jd_path.is_file() or not briefing_path.is_file():
        pytest.skip("Anthropic JD or briefing fixture missing")

    pool = resolve_section_proof_pool(
        section="executive_summary",
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd_text=jd_path.read_text(encoding="utf-8"),
        briefing_text=briefing_path.read_text(encoding="utf-8"),
        repo_root=REPO,
        product_visible=False,
    )

    meta = pool.proof_pool_metadata
    assert meta["track_weighted_seed_fallback_used"] is True
    assert meta["track_weighted_seed_namespace"] == "role_episode_bundle"
    assert meta["track_weighted_hop_paths_attached_to_c03"] is False
    assert (meta.get("graph_targeting_capsule") or {}).get("skill_ids")
    assert (meta.get("c03_graphrag_bound") or {}).get("graph_hop_paths_count") == 0
