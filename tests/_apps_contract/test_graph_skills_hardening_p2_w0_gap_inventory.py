"""P2-W0 contract: gap inventory is complete, inventory-only, Part 1 refs preserved."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.track_weighted_graph_expansion import ROOT
from apps_rg.fact_inventory.validate_p2_w0_graph_skills_gap_inventory import (
    load_and_validate_inventory,
    validate_p2_w0_graph_skills_gap_inventory,
)

INVENTORY_JSON = ROOT / "docs/reports/apps_rg/graph_skills_hardening_gap_inventory.json"


def test_p2_w0_inventory_json_validates() -> None:
    payload = load_and_validate_inventory(repo_root=ROOT)
    assert payload["inventory_only"] is True
    assert payload["live_competencies_x3_allow_claimed"] is False
    assert payload["competencies_graph_proof_pool_implemented"] is True
    assert (payload.get("p2_w1a_supersession") or {}).get("gap_closed") is True


def test_p2_w1_through_p2_w9_targets_listed() -> None:
    payload = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
    targets = payload.get("p2_wave_targets") or {}
    for i in range(1, 10):
        wave = f"P2-W{i}"
        assert wave in targets, wave
        block = targets[wave]
        assert block.get("target_files"), f"{wave} target_files"
        assert block.get("acceptance_test"), f"{wave} acceptance_test"


def test_broad_skills_ledger_gap_superseded_by_p2_w1a() -> None:
    payload = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
    assert payload["broad_skills_ledger_accepted_future_authority"] is False
    cur = payload["broad_skills_ledger_current_state"]
    assert cur["is_current_proof_pool_authority"] is False
    assert cur["accepted_future_product_authority"] is False
    assert cur.get("superseded_by_p2_w1a") is True


def test_part1_w4_w5_receipt_refs_present() -> None:
    payload = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
    refs = payload["part1_proof_refs"]
    assert (ROOT / refs["p1_w4_closeout_receipt_ref"]).is_file()
    assert (ROOT / refs["p1_w5_projection_receipt_ref"]).is_file()
    assert refs["p1_w4_c03_graph_bound_status"] == "BOUND"
    assert refs["p1_w5_live_competencies_runtime_modified"] is False


def test_inventory_module_cli_passes() -> None:
    from apps_rg.fact_inventory.validate_p2_w0_graph_skills_gap_inventory import main

    main()


def test_causal_inventory_validator_rejects_x3_claim() -> None:
    bad = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
    bad["live_competencies_x3_allow_claimed"] = True
    with pytest.raises(Exception):
        validate_p2_w0_graph_skills_gap_inventory(bad)
