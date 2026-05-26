"""Prove section_c03_graph_binding is classified honestly — not a renamed shim."""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest

from apps_rg.runtime.c03_graphrag_bound import build_executive_summary_c03_graphrag_bound
from apps_rg.runtime.integrated_product_proof_gate import validate_integrated_product_proof
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.section_spine_terminology import (
    BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT,
    BINDING_KIND_SECTION_C03_GRAPH_BINDING,
    GRAPH_EXPANSION_MODE_INCIDENT_EDGE_V1,
    SPINE_C03_GRAPHRAG_PROOF_KEYS,
    classify_section_c03_graph_binding,
    spine_c03_graphrag_proof_present,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_PY_ROOTS = (
    REPO_ROOT / "apps_rg" / "runtime",
    REPO_ROOT / "apps_rg" / "cache",
)


def test_old_shim_symbol_absent_from_active_runtime_python() -> None:
    for root in RUNTIME_PY_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert "section_graph_binding_shim" not in text, path.as_posix()


def test_section_binding_emits_explicit_classification() -> None:
    doc = build_executive_summary_c03_graphrag_bound(
        graph={"graph_edges": [{"edge_id": "e1", "source_node_id": "node_fact_a", "target_node_id": "x"}]},
        graph_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        graph_digest="digest",
        selected_fact_ids=["fact_a"],
    )
    assert doc["binding_kind"] == BINDING_KIND_SECTION_C03_GRAPH_BINDING
    assert doc["binding_classification"] == BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT
    assert doc["is_full_c0_3_graphrag"] is False
    assert doc["can_satisfy_integrated_product_proof"] is False
    assert doc["section_local_graph_context_only"] is True
    assert doc.get("graph_expansion_mode") == GRAPH_EXPANSION_MODE_INCIDENT_EDGE_V1
    assert doc.get("graph_hop_paths_count_semantics")


def test_section_local_binding_is_not_product_c03() -> None:
    doc = build_executive_summary_c03_graphrag_bound(
        graph={"graph_edges": []},
        graph_ref="ref",
        graph_digest="d",
        selected_fact_ids=["f1"],
    )
    assert classify_section_c03_graph_binding(doc) == BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT
    assert spine_c03_graphrag_proof_present(doc) is False
    for key in SPINE_C03_GRAPHRAG_PROOF_KEYS:
        assert key not in doc or not doc.get(key)


def test_full_c03_claim_requires_route_acl_proof() -> None:
    section_doc = build_executive_summary_c03_graphrag_bound(
        graph={"graph_edges": []},
        graph_ref="ref",
        graph_digest="d",
        selected_fact_ids=["f1"],
    )
    assert spine_c03_graphrag_proof_present(section_doc) is False
    spine_doc = {
        "binding_kind": "spine",
        "route_bound": "route:apps_rg:R4",
        "acl_bound": "acl:tenant:default",
        "graph_lineage_refs": ["ref:graph:version:1"],
        "support_status": "SUPPORTED",
    }
    assert spine_c03_graphrag_proof_present(spine_doc) is True
    assert classify_section_c03_graph_binding(spine_doc) == "FULL_C0_3_GRAPHRAG_BINDING"


def test_product_proof_guard_rejects_section_fec_shaped_artifacts(tmp_path: Path) -> None:
    doc = build_executive_summary_c03_graphrag_bound(
        graph={"graph_edges": []},
        graph_ref="ref",
        graph_digest="d",
        selected_fact_ids=["f1"],
    )
    (tmp_path / "c03_graphrag_bound.json").write_text(json.dumps(doc), encoding="utf-8")
    (tmp_path / "run_manifest.json").write_text(
        '{"section_id": "executive_summary", "command": "python -m apps_rg --section executive_summary"}',
        encoding="utf-8",
    )
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert result.section_mode is True


def test_fixture_dev_bypass_requires_pytest(monkeypatch: pytest.MonkeyPatch) -> None:
    deactivate_fixture_dev_bypass()
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    with pytest.raises(RuntimeError, match="test-only"):
        activate_fixture_dev_bypass(non_product_certified=True)


def test_fixture_dev_bypass_under_pytest() -> None:
    assert os.environ.get("PYTEST_CURRENT_TEST")
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        assert True
    finally:
        deactivate_fixture_dev_bypass()


def test_old_shim_module_path_not_importable() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("apps_rg.runtime.section_graph_binding_shim")
