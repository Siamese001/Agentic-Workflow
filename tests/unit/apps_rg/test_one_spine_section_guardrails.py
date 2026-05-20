"""One-spine guardrails: section CLI must not claim full canonical C0 without spine contracts."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.c03_graphrag_bound import build_executive_summary_c03_graphrag_bound
from apps_rg.runtime.one_spine_inventory import build_one_spine_section_path_inventory
from apps_rg.runtime.section_spine_terminology import (
    BINDING_KIND_SECTION_GRAPH_SHIM,
    CANONICAL_SPINE_CHAIN,
    enrich_section_graph_binding_doc,
    is_section_graph_binding_doc,
    is_spine_final_evidence_contract,
    section_lane_spine_classification,
)
from apps_rg.runtime.sections.executive_summary_proof_bundle import (
    build_runtime_exhaust_bundle,
    build_section_runtime_proof_bundle,
)


def test_inventory_two_paths_and_canonical_target():
    inv = build_one_spine_section_path_inventory()
    assert inv["two_paths_found"] is True
    assert list(inv["canonical_spine_target"]) == list(CANONICAL_SPINE_CHAIN)
    assert inv["path_a_section_cli"]["exemplar_lane"] == "executive_summary"
    assert inv["path_b_canonical_r4"]["dispatch"].endswith("run_integrated_single_action_spine")


def test_section_graph_binding_shim_not_spine_fec():
    doc = build_executive_summary_c03_graphrag_bound(
        graph={"graph_edges": [], "graph_metadata": {}},
        graph_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        graph_digest="abc",
        selected_fact_ids=["fact_a"],
    )
    assert is_section_graph_binding_doc(doc)
    assert doc["binding_kind"] == BINDING_KIND_SECTION_GRAPH_SHIM
    assert doc["canonical_contract_claims"]["FinalEvidenceContract"] is False
    snap = doc["final_evidence_contract_snapshot"]
    assert snap.get("fec_shape_only") is True
    assert snap.get("canonical_final_evidence_contract_emitted") is False
    assert is_spine_final_evidence_contract(snap) is False


def test_grounded_canonical_path_requires_spine_fec_not_shim_snapshot():
    shim_snap = {
        "schema_version": "final_evidence_contract_snapshot_v1",
        "support_status": "SUPPORTED",
        "fec_shape_only": True,
    }
    assert is_spine_final_evidence_contract(shim_snap) is False
    spine_fec = {
        "contract_type": "FinalEvidenceContract",
        "producer_stage": "C0",
        "support_status": "SUPPORTED",
    }
    assert is_spine_final_evidence_contract(spine_fec) is True


def test_section_runtime_exhaust_does_not_claim_spine_runtime_exhaust_bundle(tmp_path: Path):
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "x3_disposition.json").write_text('{"x3_code": "ALLOW"}', encoding="utf-8")
    exhaust = build_runtime_exhaust_bundle(
        repo_root=tmp_path,
        artifact_dir=ad,
        x3={"x3_code": "ALLOW"},
        failed_gate_ids=[],
    )
    assert exhaust.get("claims_spine_runtime_exhaust_bundle") is False
    assert exhaust.get("lane_local_runtime_exhaust") is True
    assert exhaust["spine_classification"]["is_canonical_c0_path"] is False


def test_section_proof_bundle_declares_incomplete_l7(tmp_path: Path):
    bundle = build_section_runtime_proof_bundle(
        repo_root=tmp_path,
        artifact_dir=tmp_path / "run",
        inventory={"artifacts": []},
        exhaust_rel=None,
    )
    assert bundle["proof_status"] == "INCOMPLETE"
    assert bundle["certified"] is False
    assert bundle["spine_classification"]["spine_mode"] == "section_lane_modular"


def test_enrich_idempotent():
    base = {"schema_version": "c03_graphrag_bound_v1"}
    once = enrich_section_graph_binding_doc(base)
    twice = enrich_section_graph_binding_doc(once)
    assert twice["binding_kind"] == BINDING_KIND_SECTION_GRAPH_SHIM


def test_section_lane_classification_explicit_non_claims():
    spine = section_lane_spine_classification()
    claims = " ".join(spine["explicit_non_claims"]).lower()
    assert "c0.2" in claims
    assert "c0.3" in claims
    assert "c0.5" in claims or "final evidence" in claims
    assert "uwg" in claims
