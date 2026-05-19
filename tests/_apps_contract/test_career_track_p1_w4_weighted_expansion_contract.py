"""P1-W4 contract: hybrid JD >=2 tracks; no broad_skills_ledger skills authority."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import (
    assert_skills_not_broad_ledger_authority,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    TrackWeightedExpansionContractError,
    build_track_weighted_expansion,
    capture_agentic_core_isolation,
)
from apps_rg.fact_inventory.validate_p1_w4_track_weighted_closeout import (
    validate_p1_w4_track_weighted_closeout,
)

REPO = Path(__file__).resolve().parents[2]
HYBRID_FIXTURE = REPO / "docs/reports/apps_rg/fixtures/p1_w4_hybrid_jd_fixture.json"
SINGLE_FIXTURE = REPO / "docs/reports/apps_rg/fixtures/p1_w4_single_track_jd_fixture.json"
RECEIPT = REPO / "docs/reports/apps_rg/career_track_p1_w4_track_weighted_expansion_receipt.json"
CLOSEOUT = REPO / "docs/reports/apps_rg/career_track_p1_w4_closeout_receipt.json"


def test_receipt_file_proves_hybrid_multi_track() -> None:
    assert RECEIPT.is_file(), "run write_p1_w4_receipts or pytest unit receipt test first"
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    hybrid = data["hybrid_fixture"]
    assert len(hybrid["tracks_with_facts"]) >= 2
    assert hybrid["broad_skills_ledger_used_as_authority"] is False
    hops = hybrid.get("graph_hop_paths_sample") or []
    assert hops and isinstance(hops[0], list)
    c03 = data["c03_binding_proof"]
    assert c03["c03_graph_bound_status"] == "BOUND"
    assert c03["non_graph_evidence_items_count"] == 0
    assert c03["graph_expansion_mode"] == "TRACK_WEIGHTED_MULTI_HOP"
    validate_p1_w4_track_weighted_closeout(hybrid)


def test_closeout_receipt_agentic_core_isolation() -> None:
    assert CLOSEOUT.is_file()
    data = json.loads(CLOSEOUT.read_text(encoding="utf-8"))
    iso = data["agentic_core_isolation"]
    assert iso["touched_by_this_wave"] is False
    live = capture_agentic_core_isolation(repo_root=REPO)
    assert live["touched_by_this_wave"] is False


def test_hybrid_fixture_contract() -> None:
    fx = json.loads(HYBRID_FIXTURE.read_text(encoding="utf-8"))
    graph = load_augmented_skills_graph(repo_root=REPO)
    out = build_track_weighted_expansion(
        graph=graph,
        role_family_key=fx["expected_role_family_key"],
        jd_text=fx["jd_text"],
        enforce_hybrid_contract=True,
        min_tracks_with_facts=fx["expected_min_tracks_with_facts"],
        bind_c03=True,
    )
    assert_skills_not_broad_ledger_authority(out)
    assert len(out["tracks_with_facts"]) >= 2
    assert out["c03_graph_bound_status"] == "BOUND"
    validate_p1_w4_track_weighted_closeout(out)


def test_single_track_fixture_fails_hybrid_contract() -> None:
    fx = json.loads(SINGLE_FIXTURE.read_text(encoding="utf-8"))
    graph = load_augmented_skills_graph(repo_root=REPO)
    with pytest.raises(TrackWeightedExpansionContractError):
        build_track_weighted_expansion(
            graph=graph,
            role_family_key="QUANT_TRADING",
            jd_text=fx["jd_text"],
            weight_override=fx["weight_override"],
            enforce_hybrid_contract=True,
            min_tracks_with_facts=2,
        )


def test_broad_skills_ledger_not_skills_authority_on_expansion_path() -> None:
    graph = load_augmented_skills_graph(repo_root=REPO)
    out = build_track_weighted_expansion(
        graph=graph,
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        jd_text=json.loads(HYBRID_FIXTURE.read_text(encoding="utf-8"))["jd_text"],
        enforce_hybrid_contract=True,
    )
    assert out["skills_authority_source_type"] == "augmented_skills_graph"
    assert out["broad_skills_ledger_used_as_authority"] is False
    assert_skills_not_broad_ledger_authority(out)
