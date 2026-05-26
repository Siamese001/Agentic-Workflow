"""W3: c03_promotion_candidates.json transparency (pool-wins, no auto-promote)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.c0.c03_allowlist_coherence import (
    build_exec_summary_allowlist_receipt,
    filter_c03_evidence_to_allowed_pool,
)
from apps_rg.runtime.c0.c03_promotion_candidates import (
    REASON_POOL_WINS_DG1_A,
    SCHEMA,
    build_c03_promotion_candidates_receipt,
)
from apps_rg.runtime.graph_skills_run_artifacts import (
    PROMOTION_CANDIDATES_FILENAME,
    persist_graph_skills_lane_artifacts,
)
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture
def brown_jd() -> str:
    path = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
    if not path.is_file():
        pytest.skip("Brown JD fixture missing")
    return path.read_text(encoding="utf-8")


def test_promotion_receipt_scored_filtered_neighbors() -> None:
    track = {
        "role_family_key": "SVP_ENGINEERING_AI_PLATFORM",
        "track_weights": {"track_genai_agentic": 0.35, "track_data_tech_cloud_ml": 0.4},
        "selected_facts": [
            {
                "fact_id": "fact_partnerships_gtm_001",
                "career_track": "track_data_tech_cloud_ml",
                "skill_id": "skill_cloud_gtm",
                "graph_hop_path": [
                    {"edge_type": "a", "from": "t", "to": "p"},
                    {"edge_type": "b", "from": "p", "to": "s"},
                    {"edge_type": "c", "from": "s", "to": "f"},
                ],
            }
        ],
    }
    doc = build_c03_promotion_candidates_receipt(
        filtered_out_fact_ids=["fact_partnerships_gtm_001"],
        allowed_fact_ids={"fact_exec_001"},
        track_expansion=track,
        jd_text="enterprise architecture data platforms revenue gtm",
    )
    assert doc["schema"] == SCHEMA
    assert doc["promoted_fact_ids"] == []
    assert doc["auto_promote_enabled"] is False
    row = doc["candidates"][0]
    assert row["fact_id"] == "fact_partnerships_gtm_001"
    assert row["promotion_eligible"] is False
    assert row["reason"] == REASON_POOL_WINS_DG1_A
    assert row["track_weight"] == 0.4
    assert row["edge_distance"] == 2
    assert row["jd_keyword_overlap"]["score"] > 0


def test_allowlist_receipt_embeds_promotion_candidates() -> None:
    allowed = {"fact_exec_001"}
    c03 = {"final_evidence_contract_snapshot": {"evidence_items": []}}
    track = {"c03_selected_fact_ids": ["fact_exec_001", "fact_gtm_002"], "selected_facts": []}
    _, filt = filter_c03_evidence_to_allowed_pool(c03, allowed, track_expansion=track)
    receipt = build_exec_summary_allowlist_receipt(
        allowed_fact_ids=allowed,
        allowlist_filter_receipt=filt,
        track_expansion=track,
        proof_pool_digest="abc",
        jd_text="gtm revenue cloud",
    )
    promo = receipt.get("c03_promotion_candidates")
    assert isinstance(promo, dict)
    assert "fact_gtm_002" in promo.get("c03_filtered_out_fact_ids", [])


def test_persist_promotion_candidates_artifact(tmp_path: Path) -> None:
    promo = build_c03_promotion_candidates_receipt(
        filtered_out_fact_ids=["fact_x"],
        allowed_fact_ids={"fact_a"},
        track_expansion=None,
        jd_text="",
    )
    payload = {
        "target_company": "Acme",
        "target_role": "SVP",
        "jd_text": "enterprise architecture",
        "proof_pool_metadata": {"c03_promotion_candidates": promo},
    }
    out = persist_graph_skills_lane_artifacts(
        tmp_path,
        section_id="executive_summary",
        runtime_payload=payload,
    )
    assert out[PROMOTION_CANDIDATES_FILENAME]
    loaded = json.loads((tmp_path / PROMOTION_CANDIDATES_FILENAME).read_text(encoding="utf-8"))
    assert loaded["schema"] == SCHEMA
    assert loaded["candidate_count"] == 1


def test_brown_pool_has_promotion_candidates(brown_jd: str) -> None:
    pool = resolve_section_proof_pool(
        section="executive_summary",
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        jd_text=brown_jd,
        product_visible=False,
    )
    meta = pool.proof_pool_metadata
    promo = meta.get("c03_promotion_candidates") or (
        (meta.get("exec_summary_allowlist_receipt") or {}).get("c03_promotion_candidates")
    )
    assert isinstance(promo, dict)
    filtered = promo.get("c03_filtered_out_fact_ids") or []
    assert filtered, "Brown graph expansion should filter neighbors for promotion receipt"
    assert promo.get("promoted_fact_ids") == []
    for row in promo.get("candidates") or []:
        assert row.get("promotion_eligible") is False
