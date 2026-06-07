"""Wave 8: apps_rg gates are classified by product authority."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from apps_rg.runtime.contracts.gate_taxonomy import (
    VALID_GATE_CLASSES,
    classify_gate_id,
    explicit_gate_classes,
    is_release_blocker,
    load_gate_taxonomy,
    taxonomy_path,
)
from apps_rg.runtime.rigor.lane_registry import LANE_CRITICAL_GATES
from apps_rg.runtime.sections.section_product_shape_ssot import (
    RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
    RETIRED_IBM_BULLETS_X2_GATE_IDS,
    RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS,
    RETIRED_UNIFY_BULLETS_X2_GATE_IDS,
    product_shape_gate_ids_by_lane,
)

REPO = Path(__file__).resolve().parents[3]
ASSUMPTIONS = REPO / "apps_rg" / "runtime" / "contracts" / "apps_rg_assumptions.yaml"
RUNTIME_PROFILE = (
    REPO
    / "apps_rg"
    / "config"
    / "domain_contract"
    / "runtime_gate_profile.resume_generation.v1.json"
)


def test_gate_taxonomy_contract_parses_and_declares_three_classes() -> None:
    data = load_gate_taxonomy()
    assert taxonomy_path().is_file()
    assert set(data["classes"]) == VALID_GATE_CLASSES
    explicit = explicit_gate_classes(data)
    assert explicit["C0-G-002"] == "advisory"
    assert explicit["U0-G-003"] == "release_blocker"


def test_assumption_ledger_gate_ids_are_classified() -> None:
    data = yaml.safe_load(ASSUMPTIONS.read_text(encoding="utf-8"))
    gates = {
        gate_id
        for row in data["assumptions"]
        for gate_id in (row.get("gate_ids") or [])
    }
    assert gates
    for gate_id in gates:
        assert classify_gate_id(gate_id) in VALID_GATE_CLASSES

    assert classify_gate_id("C0-G-002") == "advisory"
    assert classify_gate_id("L2-G-002") == "advisory"
    for gate_id in gates - {"C0-G-002", "L2-G-002"}:
        assert is_release_blocker(gate_id), gate_id


def test_runtime_gate_profile_gates_carry_taxonomy_class() -> None:
    data = json.loads(RUNTIME_PROFILE.read_text(encoding="utf-8"))
    assert data["gate_taxonomy_ref"] == "apps_rg/runtime/contracts/apps_rg_gate_taxonomy.yaml"
    for stage_data in data["stages"].values():
        for gate in stage_data.get("required_gates") or []:
            gate_id = gate["gate_id"]
            assert gate["gate_class"] == classify_gate_id(gate_id)
            assert gate["gate_class"] == "release_blocker"


def test_generated_lane_critical_gates_are_release_blockers() -> None:
    for lane, gate_ids in LANE_CRITICAL_GATES.items():
        assert gate_ids, lane
        for gate_id in gate_ids:
            assert classify_gate_id(gate_id) == "release_blocker", f"{lane}: {gate_id}"


def test_product_shape_gates_are_release_blockers() -> None:
    for lane, gate_ids in product_shape_gate_ids_by_lane().items():
        assert gate_ids, lane
        for gate_id in gate_ids:
            assert is_release_blocker(gate_id), f"{lane}: {gate_id}"


def test_retired_x2_gate_ids_are_debug_metrics() -> None:
    retired = (
        RETIRED_EXEC_SUMMARY_X2_GATE_IDS
        | RETIRED_UNIFY_BULLETS_X2_GATE_IDS
        | RETIRED_IBM_BULLETS_X2_GATE_IDS
        | RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS
    )
    assert retired
    for gate_id in retired:
        assert classify_gate_id(gate_id) == "debug_metric", gate_id
