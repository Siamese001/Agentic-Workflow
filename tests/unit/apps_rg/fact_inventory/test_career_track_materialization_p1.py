"""P1-W1..W3 career track materialization invariants (graph-skills-hardening-f3a8c1)."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    load_master_skills_arsenal_ledger,
    validate_arsenal_ledger_shape,
)
from apps_rg.fact_inventory.materialize_career_tracks_p1 import (
    EPOCH_TO_TRACK,
    verify_p1_invariants,
)

REPO = Path(__file__).resolve().parents[4]
LEDGER_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"


@pytest.fixture
def ledger() -> dict:
    return load_master_skills_arsenal_ledger(path=LEDGER_PATH)


def test_career_track_nodes_and_metadata(ledger: dict) -> None:
    gm = ledger["graph_metadata"]
    assert gm.get("career_track_count") == 3
    track_nodes = [n for n in ledger["graph_nodes"] if n.get("node_type") == "career_track"]
    assert len(track_nodes) == 3
    track_ids = {n["node_id"] for n in track_nodes}
    assert track_ids == {
        "track_actuarial_risk_derivatives",
        "track_data_tech_cloud_ml",
        "track_genai_agentic",
    }


def test_each_epoch_has_one_primary_career_track(ledger: dict) -> None:
    epoch_tracks: dict[str, list[str]] = defaultdict(list)
    for edge in ledger["graph_edges"]:
        if edge.get("edge_type") != "career_track_contains_epoch":
            continue
        if edge.get("primary") is True:
            epoch_tracks[str(edge["target_node_id"])].append(str(edge["source_node_id"]))
    for epoch_id, expected_track in EPOCH_TO_TRACK.items():
        primaries = epoch_tracks.get(epoch_id, [])
        assert len(primaries) == 1, f"{epoch_id} primaries={primaries}"
        assert primaries[0] == expected_track


def test_pillar_trading_hpc_maps_to_track_data_tech(ledger: dict) -> None:
    trading = [
        e
        for e in ledger["graph_edges"]
        if e.get("edge_type") == "career_track_contains_pillar"
        and e.get("target_node_id") == "pillar_trading_hpc"
        and e.get("primary") is True
    ]
    assert len(trading) == 1
    assert trading[0]["source_node_id"] == "track_data_tech_cloud_ml"


def test_career_sequence_edges_non_causal(ledger: dict) -> None:
    seq = [
        e
        for e in ledger["graph_edges"]
        if e.get("edge_type") == "career_track_precedes_career_track"
    ]
    assert len(seq) == 2
    assert all(e.get("causal") is False for e in seq)
    assert all("non-causal" in str(e.get("rationale", "")).lower() for e in seq)


def test_employment_spine_from_base_resume(ledger: dict) -> None:
    base = json.loads(
        (REPO / "apps_rg/resume/base/amit_ayer_base_resume_v1.json").read_text(encoding="utf-8")
    )
    exp_ids = {str(e["fact_id"]) for e in base["facts"]["employment"]}
    emp_nodes = {
        n["node_id"]
        for n in ledger["graph_nodes"]
        if n.get("node_type") == "employment"
    }
    assert len(emp_nodes) == len(exp_ids)
    for exp_id in exp_ids:
        assert f"employment_{exp_id}" in emp_nodes


def test_employment_primary_track_coverage(ledger: dict) -> None:
    for edge in ledger["graph_edges"]:
        if edge.get("edge_type") != "employment_in_career_track":
            continue
        assert edge.get("primary") is True
        assert str(edge["target_node_id"]).startswith("track_")


def test_active_skill_rows_have_fact_id_links(ledger: dict) -> None:
    for row in ledger["skill_rows"]:
        status = str(row.get("activation_status") or "")
        if not status.startswith("ACTIVE"):
            continue
        assert row.get("fact_id_links"), f"{row['skill_id']} ACTIVE without fact_id_links"


def test_verify_p1_invariants_passes(ledger: dict) -> None:
    validate_arsenal_ledger_shape(ledger)
    report = verify_p1_invariants(ledger)
    assert report["career_track_count"] == 3
    assert report["trading_hpc_ok"] is True
    assert report["non_causal_sequence_only"] is True
    assert not report["violations"]
    assert not report["active_without_facts"]
