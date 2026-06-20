"""Contract: executive_summary C03/track expansion ⊆ allowed_fact_ids (pool-wins)."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.track_weighted_graph_expansion import TrackWeightedExpansionContractError
from apps_rg.runtime.c0.c03_allowlist_coherence import (
    filter_c03_evidence_to_allowed_pool,
)
from apps_rg.runtime.c0.exec_summary_graph_targeting_capsule import (
    NON_PROOF_BANNER,
    build_graph_targeting_capsule,
    format_graph_targeting_capsule_for_pa,
)
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def brown_jd() -> str:
    path = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
    if not path.is_file():
        pytest.skip("Brown JD fixture missing")
    return path.read_text(encoding="utf-8")


def test_filter_c03_strips_out_of_pool_evidence_items() -> None:
    allowed = {"fact_exec_001", "fact_governance_001"}
    c03 = {
        "final_evidence_contract_snapshot": {
            "evidence_items": [
                {"evidence_id": "evidence:graph:fact_exec_001", "source_fact_id": "fact_exec_001"},
                {
                    "evidence_id": "evidence:track_weighted:fact_solutions_002",
                    "graph_node_ref": "node_fact:fact_solutions_002",
                },
            ]
        }
    }
    track = {"c03_selected_fact_ids": ["fact_exec_001", "fact_solutions_002"]}
    filtered, receipt = filter_c03_evidence_to_allowed_pool(c03, allowed, track_expansion=track)
    items = filtered["final_evidence_contract_snapshot"]["evidence_items"]
    assert len(items) == 1
    assert items[0]["source_fact_id"] == "fact_exec_001"
    assert "fact_solutions_002" in receipt["c03_filtered_out_fact_ids"]
    assert receipt["allowlist_mismatch"] is False
    assert "fact_solutions_002" in receipt.get("c03_expansion_surplus_fact_ids", [])


def test_graph_targeting_capsule_non_proof_banner_and_caps() -> None:
    track = {
        "c03_selected_skill_ids": [f"skill_test_{i}" for i in range(12)],
        "selected_skills": [
            {"skill_id": f"skill_test_{i}", "pillar": "pillar_agentic", "career_track": "track_a", "weight": 1.0 - i * 0.05}
            for i in range(12)
        ],
    }
    cap = build_graph_targeting_capsule(track, role_family_key="SVP_ENGINEERING_AI_PLATFORM")
    assert cap["claim_support_allowed"] is False
    assert len(cap["skill_entries"]) <= 8
    pa = format_graph_targeting_capsule_for_pa(cap)
    assert NON_PROOF_BANNER.split("—")[0].strip() in pa
    assert "GRAPH_TARGETING_CAPSULE" in pa


def test_resolve_executive_summary_proof_pool_blocks_when_allowed_facts_lack_hop_paths(
    brown_jd: str,
) -> None:
    with pytest.raises(
        TrackWeightedExpansionContractError,
        match="seed_fact_ids have no matching track-weighted graph hop paths",
    ):
        resolve_section_proof_pool(
            section="executive_summary",
            target_company="Brown & Brown",
            target_role="SVP IT Strategy & Innovation",
            jd_text=brown_jd,
            product_visible=False,
        )
