"""Native C0.3 skills-graph binding — schema, ACL, route binding, PA metadata."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from apps_rg.runtime.integrated_product_proof_gate import validate_integrated_product_proof
from apps_rg.runtime.native_c03_skills_graph import (
    CONTRACT_TYPE_NATIVE_C03,
    NATIVE_C03_FIRST_WAVE_SECTIONS,
    SkillsGraphAclDecision,
    SkillsGraphAclPolicy,
    build_native_c03_final_evidence,
    default_acl_policy,
    enrich_proof_pool_with_native_c03,
    evaluate_skills_graph_acl,
    extract_route_context,
    merge_native_c03_into_proof_pool_metadata,
    native_c03_pa_metadata,
    validate_native_c03_contract,
)
from apps_rg.runtime.proof_pool_resolver import SectionProofPool, resolve_section_proof_pool
from apps_rg.runtime.section_spine_terminology import (
    BINDING_CLASSIFICATION_FULL_C03,
    BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT,
    classify_section_c03_graph_binding,
)
from apps_rg.runtime.c03_graphrag_bound import build_executive_summary_c03_graphrag_bound


def _route_spine() -> SimpleNamespace:
    return SimpleNamespace(
        route_id="R3_SIMPLE_GROUNDED_READ",
        route_family="evidence_grounded_generation",
        support_target="executive_summary",
        execution_form="SIMPLE_GROUNDED_READ",
        grounding_required=True,
        graph_policy=SimpleNamespace(graph_expansion_allowed=True),
    )


def _minimal_graph() -> dict:
    return {
        "graph_edges": [
            {
                "edge_id": "e1",
                "source_node_id": "node_fact_a",
                "target_node_id": "node_x",
            }
        ],
        "graph_metadata": {"node_count": 2, "edge_count": 1},
        "skill_rows": [],
    }


def test_native_c03_requires_route_and_acl_fields() -> None:
    route_ctx = extract_route_context(SimpleNamespace(route=_route_spine()))
    acl = evaluate_skills_graph_acl(
        section_id="executive_summary",
        route_ctx=route_ctx,
        selected_fact_ids=["fact_a"],
        graph=_minimal_graph(),
        policy=default_acl_policy(section_id="executive_summary", product_visible=True),
        product_visible=True,
    )
    doc = build_native_c03_final_evidence(
        section_id="executive_summary",
        graph=_minimal_graph(),
        graph_ref="apps_rg/fact_inventory/graph.json",
        graph_digest="abc123",
        selected_fact_ids=["fact_a"],
        route_ctx=route_ctx,
        acl=acl,
    )
    assert doc is not None
    assert doc["route_bound"] is True
    assert doc["acl_bound"] is True
    assert doc["graph_lineage_refs"]
    assert doc["source_lineage_refs"]
    assert doc["support_status"] == "SUPPORTED"
    assert doc["binding_classification"] == BINDING_CLASSIFICATION_FULL_C03
    assert doc["canonical_c0_3_claimed"] is True
    assert doc["fec_shape_only"] is False
    ok, missing = validate_native_c03_contract(doc)
    assert ok, missing


def test_blocked_fact_excluded_from_evidence_items() -> None:
    route_ctx = extract_route_context(SimpleNamespace(route=_route_spine()))
    policy = default_acl_policy(section_id="executive_summary", product_visible=True)
    acl = evaluate_skills_graph_acl(
        section_id="executive_summary",
        route_ctx=route_ctx,
        selected_fact_ids={"fact_allowed", "fact_blocked"},
        graph=_minimal_graph(),
        policy=policy,
        product_visible=True,
    )
    acl = SkillsGraphAclDecision(
        allowed_fact_ids=frozenset({"fact_allowed"}),
        allowed_graph_node_ids=frozenset({"node_fact_fact_allowed"}),
        blocked_fact_ids=frozenset({"fact_blocked"}),
        blocked_node_ids=frozenset(),
        blocked_source_ids=frozenset(),
        acl_scope="section:executive_summary",
        source_scope="augmented_skills_graph",
        product_proof_eligible=False,
        pa_evidence_eligible=True,
    )
    doc = build_native_c03_final_evidence(
        section_id="executive_summary",
        graph=_minimal_graph(),
        graph_ref="g.json",
        graph_digest="d",
        selected_fact_ids=["fact_allowed"],
        route_ctx=route_ctx,
        acl=acl,
    )
    assert doc is not None
    ids = {str(i.get("evidence_id")) for i in doc["evidence_items"]}
    assert all("fact_blocked" not in x for x in ids)
    assert any("fact_blocked" in x for x in doc["excluded_evidence_refs"])


def test_empty_support_not_product_eligible() -> None:
    route_ctx = extract_route_context(SimpleNamespace(route=_route_spine()))
    acl = SkillsGraphAclDecision(
        allowed_fact_ids=frozenset(),
        allowed_graph_node_ids=frozenset(),
        blocked_fact_ids=frozenset({"fact_x"}),
        blocked_node_ids=frozenset(),
        blocked_source_ids=frozenset(),
        acl_scope="section:executive_summary",
        source_scope="augmented_skills_graph",
        product_proof_eligible=False,
        pa_evidence_eligible=False,
    )
    doc = build_native_c03_final_evidence(
        section_id="executive_summary",
        graph=_minimal_graph(),
        graph_ref="g.json",
        graph_digest="d",
        selected_fact_ids=[],
        route_ctx=route_ctx,
        acl=acl,
    )
    assert doc is None


def test_pa_metadata_marks_data_only() -> None:
    route_ctx = extract_route_context(SimpleNamespace(route=_route_spine()))
    acl = evaluate_skills_graph_acl(
        section_id="competencies",
        route_ctx=route_ctx,
        selected_fact_ids=["skill_fact_1"],
        graph=_minimal_graph(),
        policy=default_acl_policy(section_id="competencies", product_visible=True),
        product_visible=True,
    )
    doc = build_native_c03_final_evidence(
        section_id="competencies",
        graph=_minimal_graph(),
        graph_ref="g.json",
        graph_digest="d",
        selected_fact_ids=["skill_fact_1"],
        route_ctx=route_ctx,
        acl=acl,
    )
    assert doc is not None
    pa = native_c03_pa_metadata(doc)
    assert pa["c03_pa_data_only"] is True
    assert pa["c03_not_instruction"] is True
    for item in doc["evidence_items"]:
        assert item.get("data_only") is True
        assert item.get("not_instruction") is True


def test_section_local_remains_non_product_c03() -> None:
    local = build_executive_summary_c03_graphrag_bound(
        graph=_minimal_graph(),
        graph_ref="ref",
        graph_digest="d",
        selected_fact_ids=["f1"],
    )
    assert classify_section_c03_graph_binding(local) == BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT
    assert local["binding_classification"] == BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT
    assert local["is_full_c0_3_graphrag"] is False


def test_merge_native_c03_alongside_section_local() -> None:
    local = build_executive_summary_c03_graphrag_bound(
        graph=_minimal_graph(),
        graph_ref="ref",
        graph_digest="digest",
        selected_fact_ids=["fact_a"],
    )
    meta = {"c03_graphrag_bound": local, "graph_ref": "ref", "graph_digest": "digest"}
    merged = merge_native_c03_into_proof_pool_metadata(
        meta,
        section_id="executive_summary",
        front_spine=SimpleNamespace(route=_route_spine(), product_visible=True),
        graph=_minimal_graph(),
        graph_ref="ref",
        graph_digest="digest",
        selected_fact_ids=["fact_a"],
    )
    assert merged["native_c03_status"] == "EMITTED"
    assert merged["c03_binding_classification"] == BINDING_CLASSIFICATION_FULL_C03
    assert merged["c03_graphrag_bound"]["binding_classification"] == BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT


def test_product_proof_rejects_section_local_binding_claim(tmp_path: Path) -> None:
    local = build_executive_summary_c03_graphrag_bound(
        graph={"graph_edges": []},
        graph_ref="r",
        graph_digest="d",
        selected_fact_ids=["f"],
    )
    local["can_satisfy_integrated_product_proof"] = True
    (tmp_path / "c03_graphrag_bound.json").write_text(json.dumps(local), encoding="utf-8")
    (tmp_path / "run_manifest.json").write_text(
        '{"section_id":"executive_summary"}',
        encoding="utf-8",
    )
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"


def test_product_proof_rejects_fec_shape_full_c03_claim(tmp_path: Path) -> None:
    snap = {
        "fec_shape_only": True,
        "canonical_c0_3_claimed": True,
        "binding_classification": "FEC_SHAPE_ONLY_NOT_C0_3",
    }
    (tmp_path / "final_evidence_contract_snapshot.json").write_text(
        json.dumps(snap),
        encoding="utf-8",
    )
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"


def test_product_proof_blocks_false_full_c03_without_route_acl(tmp_path: Path) -> None:
    fake = {
        "binding_classification": BINDING_CLASSIFICATION_FULL_C03,
        "canonical_c0_3_claimed": True,
        "route_bound": False,
        "acl_bound": False,
    }
    (tmp_path / "native_c03_final_evidence.json").write_text(
        json.dumps(fake),
        encoding="utf-8",
    )
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert "binding_classification" in result.decisive_reason or "false_full_c03" in result.decisive_reason


@pytest.mark.parametrize("section_id", sorted(NATIVE_C03_FIRST_WAVE_SECTIONS))
def test_first_wave_sections_in_matrix(section_id: str) -> None:
    from apps_rg.runtime.native_c03_skills_graph import SECTION_NATIVE_C03_EXPANSION_MATRIX

    assert SECTION_NATIVE_C03_EXPANSION_MATRIX[section_id]["native_c03_enabled"] is True


def test_executive_summary_resolve_emits_native_c03_when_front_spine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.runtime.section_front_spine_bridge import SectionFrontSpineBridge

    repo = Path(__file__).resolve().parents[3]
    front = SectionFrontSpineBridge(
        section_id="executive_summary",
        validated_request=object(),
        l1_plan=object(),
        route=_route_spine(),
        product_visible=True,
    )

    def _fake_srfs(*args, **kwargs):
        plan = {
            "section_id": "executive_summary",
            "facts": [{"fact_id": "fact_a", "claim_text": "Led platform."}],
        }
        meta = {"proof_pool_type": "selected_role_fact_set"}
        return plan, ["fact_a"], {"fact_a"}, meta

    monkeypatch.setattr(
        "apps_rg.runtime.proof_pool_resolver.resolve_srfs_section_proof_bundle",
        _fake_srfs,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.proof_pool_resolver.resolve_augmented_skills_graph_authority",
        lambda **k: {
            "skills_authority_status": "PASS",
            "graph_ref": "apps_rg/fact_inventory/graph.json",
            "graph_digest": "deadbeef",
        },
    )
    with patch(
        "apps_rg.fact_inventory.augmented_skills_graph.load_augmented_skills_graph",
        return_value=_minimal_graph(),
    ):
        pool = resolve_section_proof_pool(
            section="executive_summary",
            selected_role_fact_set_path="artifacts/fake/srfs.json",
            front_spine=front,
            repo_root=repo,
        )
    meta = pool.proof_pool_metadata or {}
    assert meta.get("native_c03_status") == "EMITTED"
    assert meta.get("c03_binding_classification") == BINDING_CLASSIFICATION_FULL_C03
    native = meta.get("native_c03_final_evidence")
    assert isinstance(native, dict)
    assert native.get("contract_type") == CONTRACT_TYPE_NATIVE_C03
