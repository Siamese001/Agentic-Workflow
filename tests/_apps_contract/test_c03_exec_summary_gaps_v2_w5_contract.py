"""W5 contract: consolidated C03 gaps v2 gates (W0–W4) on Brown proof pool."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import graph_payload_digest, load_augmented_skills_graph
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
from apps_rg.runtime.section_spine_terminology import GRAPH_EXPANSION_MODE_TRACK_WEIGHTED_MULTI_HOP

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def brown_jd() -> str:
    path = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
    if not path.is_file():
        pytest.skip("Brown JD fixture missing")
    return path.read_text(encoding="utf-8")


def test_w5_brown_pool_c03_gaps_v2_invariants(brown_jd: str) -> None:
    pool = resolve_section_proof_pool(
        section="executive_summary",
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        jd_text=brown_jd,
        product_visible=False,
    )
    meta = pool.proof_pool_metadata
    c03 = meta.get("c03_graphrag_bound") or {}
    assert meta.get("canonical_c0_3_claimed") is False
    assert c03.get("graph_expansion_mode") == GRAPH_EXPANSION_MODE_TRACK_WEIGHTED_MULTI_HOP
    assert c03.get("support_target_met") is True
    assert c03.get("graph_hop_paths_by_fact_id")
    promo = meta.get("c03_promotion_candidates") or {}
    assert promo.get("promoted_fact_ids") == []
    graph = load_augmented_skills_graph(repo_root=REPO)
    digest = graph_payload_digest(graph)
    auth = (meta.get("evidence_authority") or {}).get("graph_digest") or meta.get("graph_digest")
    if auth:
        assert auth == digest
