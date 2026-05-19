"""Contract: section CLI is lane-scoped; inventory and guardrails are SSOT-aligned."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.one_spine_inventory import build_one_spine_section_path_inventory
from apps_rg.runtime.section_spine_terminology import (
    SECTION_LANE_MISSING_CANONICAL_CONTRACTS,
    is_spine_final_evidence_contract,
)

REPO = Path(__file__).resolve().parents[2]
INVENTORY_JSON = REPO / "docs/reports/apps_rg/one_spine_section_path_inventory.json"
CLOSEOUT_JSON = REPO / "docs/reports/apps_rg/one_spine_guardrail_closeout.json"


def test_inventory_json_on_disk_matches_builder():
    built = build_one_spine_section_path_inventory()
    if INVENTORY_JSON.is_file():
        on_disk = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
        assert on_disk["two_paths_found"] == built["two_paths_found"]
        assert on_disk["canonical_spine_target"] == built["canonical_spine_target"]
    else:
        pytest.skip("inventory report not emitted yet; run tools/apps_rg/emit_one_spine_reports.py")


def test_section_cli_missing_all_canonical_contracts():
    inv = build_one_spine_section_path_inventory()
    missing = set(inv["section_cli_status"]["missing_canonical_contracts"])
    assert missing == set(SECTION_LANE_MISSING_CANONICAL_CONTRACTS)
    for row in inv["contract_bypass_matrix"]:
        assert row["section_cli_emits_canonical"] is False
        assert row["canonical_r4_emits"] is True


def test_no_misnamed_artifact_claims_full_c0_without_fec():
    inv = build_one_spine_section_path_inventory()
    for item in inv["misnamed_c0_artifacts"]:
        if item.get("current_name", "").startswith("C0.3"):
            assert "shim" in item.get("recommended_name", "").lower() or "section graph" in item.get(
                "recommended_name", ""
            ).lower()


def test_closeout_json_when_present():
    if not CLOSEOUT_JSON.is_file():
        pytest.skip("closeout report not emitted yet")
    doc = json.loads(CLOSEOUT_JSON.read_text(encoding="utf-8"))
    assert doc.get("status") == "PARTIAL"
    assert doc.get("waves_completed") == ["1", "2"]
    assert doc.get("guardrails_added")
    assert doc.get("forbidden_files_touched", {}).get("agentic_core") is False
    suite = doc.get("suite_status") or {}
    assert suite.get("ONE_SPINE_TARGETED_TESTS") == "PASS"
    assert suite.get("UNIT_GUARDRAILS") == "PASS"
    assert suite.get("FULL_APPS_CONTRACT_SUITE") == "INCOMPLETE_ABORTED"
    assert suite.get("PRODUCT_CERTIFICATION") == "NOT_CLAIMED"
    non_claims = " ".join(doc.get("explicit_non_claims") or []).lower()
    assert "all apps_rg contract tests pass" in non_claims
    assert "product certification" in non_claims


def test_w3_front_bridge_report_when_present():
    w3 = REPO / "docs/reports/apps_rg/one_spine_front_bridge_w3.json"
    if not w3.is_file():
        pytest.skip("wave 3 report not emitted")
    doc = json.loads(w3.read_text(encoding="utf-8"))
    assert doc.get("wave") == 3
    assert doc.get("section_cli_preserved") is True
    assert doc.get("product_visible_kill_switch", {}).get("enabled") is True
    for ct in ("ValidatedRequest", "L1PlanContract", "RouteContract"):
        assert ct in doc.get("contracts_added_or_emitted", [])


def test_w4_fec_bridge_report_when_present():
    w4 = REPO / "docs/reports/apps_rg/one_spine_c0_fec_bridge_w4.json"
    if not w4.is_file():
        pytest.skip("wave 4 report not emitted")
    doc = json.loads(w4.read_text(encoding="utf-8"))
    assert doc.get("wave") == 4
    assert doc.get("status") in ("PASS", "PARTIAL", "FAIL", "BLOCKED")
    matrix = doc.get("artifact_proof_matrix") or []
    assert len(matrix) >= 10


def test_w5a_all_lanes_report_when_present():
    w5a = REPO / "docs/reports/apps_rg/one_spine_fec_bridge_w5a_all_lanes.json"
    if not w5a.is_file():
        pytest.skip("wave 5A report not emitted")
    doc = json.loads(w5a.read_text(encoding="utf-8"))
    assert doc.get("wave") == "5A"
    assert doc.get("forbidden_files_touched", {}).get("agentic_core") is False
    assert len(doc.get("lane_summaries") or {}) >= 7


def test_w5b_l2_receipts_report_when_present():
    w5b = REPO / "docs/reports/apps_rg/one_spine_l2_receipts_w5b_all_lanes.json"
    if not w5b.is_file():
        pytest.skip("wave 5B report not emitted")
    doc = json.loads(w5b.read_text(encoding="utf-8"))
    assert doc.get("wave") == "5B"
    assert doc.get("forbidden_files_touched", {}).get("agentic_core") is False
    assert len(doc.get("lane_summaries") or {}) >= 7


def test_w6_exit_receipts_report_when_present():
    w6 = REPO / "docs/reports/apps_rg/one_spine_exit_receipts_w6_all_lanes.json"
    if not w6.is_file():
        pytest.skip("wave 6 report not emitted")
    doc = json.loads(w6.read_text(encoding="utf-8"))
    assert doc.get("wave") == "6"
    assert doc.get("forbidden_files_touched", {}).get("agentic_core") is False
    assert len(doc.get("lane_summaries") or {}) >= 7
    matrix = doc.get("artifact_proof_matrix") or []
    assert len(matrix) >= 14


def test_w7_runtime_exhaust_report_when_present():
    w7 = REPO / "docs/reports/apps_rg/one_spine_runtime_exhaust_w7_all_lanes.json"
    if not w7.is_file():
        pytest.skip("wave 7 report not emitted")
    doc = json.loads(w7.read_text(encoding="utf-8"))
    assert doc.get("wave") == "7"
    assert doc.get("forbidden_files_touched", {}).get("agentic_core") is False
    assert len(doc.get("lane_summaries") or {}) >= 7
    assert len(doc.get("artifact_proof_matrix") or []) >= 13


def test_w8_certification_report_when_present():
    w8 = REPO / "docs/reports/apps_rg/one_spine_certification_w8_all_lanes.json"
    if not w8.is_file():
        pytest.skip("wave 8 report not emitted")
    doc = json.loads(w8.read_text(encoding="utf-8"))
    assert doc.get("wave") == "8"
    assert doc.get("forbidden_files_touched", {}).get("agentic_core") is False
    assert len(doc.get("lane_summaries") or {}) >= 7
    assert len(doc.get("artifact_proof_matrix") or []) >= 14


def test_w9_master_closeout_report_when_present():
    w9 = REPO / "docs/reports/apps_rg/one_spine_master_closeout_w9.json"
    if not w9.is_file():
        pytest.skip("wave 9 report not emitted")
    doc = json.loads(w9.read_text(encoding="utf-8"))
    assert doc.get("wave") == "9"
    assert doc.get("forbidden_files_touched", {}).get("agentic_core") is False
    assert len(doc.get("lane_summaries") or {}) >= 7
    assert len(doc.get("artifact_proof_matrix") or []) >= 15 * 7 - 1
    assert (REPO / "docs/reports/apps_rg/one_spine_no_two_path_proof_w9.json").is_file()
    assert (REPO / "docs/reports/apps_rg/one_spine_contract_suite_triage_w9.json").is_file()


def test_fec_shaped_snapshot_in_fixture_not_canonical():
    snap = {
        "schema_version": "final_evidence_contract_snapshot_v1",
        "fec_shape_only": True,
        "canonical_final_evidence_contract_emitted": False,
    }
    assert is_spine_final_evidence_contract(snap) is False
