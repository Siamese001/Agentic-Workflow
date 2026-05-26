"""W2: graph-lane support_target_met + graph_payload_digest SSOT."""

from __future__ import annotations

from apps_rg.fact_inventory.augmented_skills_graph import (
    graph_payload_digest,
    load_augmented_skills_graph,
    resolve_augmented_skills_graph_authority,
)
from apps_rg.runtime.bindings.section_lane_c0_metrics import fec_from_section_bridge
from apps_rg.runtime.c03_graphrag_bound import build_executive_summary_c03_graphrag_bound
from apps_rg.runtime.c0.section_support_target import (
    derive_graph_lane_support_target_met,
    graph_lane_proof_support_target,
    proof_pool_retrieval_sources,
)
from apps_rg.runtime.graph_selection_rationale import emit_graph_selection_rationale


def test_graph_payload_digest_matches_authority_resolver() -> None:
    graph = load_augmented_skills_graph()
    auth = resolve_augmented_skills_graph_authority()
    assert auth["skills_authority_status"] == "PASS"
    assert graph_payload_digest(graph) == auth["graph_digest"]


def test_fec_from_section_bridge_support_target_met_true() -> None:
    bridge = {
        "support_status": "SUPPORTED",
        "proof_source": "augmented_skills_graph",
        "allowed_fact_ids": ["fact_governance_003", "fact_exec_002"],
        "final_evidence_contract_snapshot": {
            "support_status": "SUPPORTED",
            "evidence_items": [
                {"source_fact_id": "fact_governance_003"},
                {"source_fact_id": "fact_exec_002"},
            ],
        },
    }
    fec = fec_from_section_bridge(bridge, run_id="test_run")
    assert fec.support_target_met is True
    assert any(src.startswith("proof_pool:") for src in fec.retrieval_sources)


def test_c03_bound_support_target_met_aligned() -> None:
    doc = build_executive_summary_c03_graphrag_bound(
        graph={"graph_edges": []},
        graph_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        graph_digest="abc",
        selected_fact_ids=["fact_a", "fact_b"],
    )
    assert doc["support_target_met"] is True
    assert doc["support_target_derivation"] == "graph_lane_v1"
    snap = doc["final_evidence_contract_snapshot"]
    assert snap["support_target_met"] is True


def test_graph_lane_support_target_requires_proof_pool_prefix() -> None:
    target = graph_lane_proof_support_target()
    sources = proof_pool_retrieval_sources(["fact_a"], proof_source="augmented_skills_graph")
    assert target.required_source_prefixes == ("proof_pool",)
    met = derive_graph_lane_support_target_met(
        support_status="PASS",
        allowed_fact_ids=["fact_a"],
        evidence_item_count=1,
    )
    assert met is True
    from agentic_core.runtime.c0.evidence_metrics_extractor import _compute_target_met

    assert _compute_target_met(sources, target) is True


def test_graph_selection_rationale_digest_full_payload() -> None:
    graph = load_augmented_skills_graph()
    expected = graph_payload_digest(graph)
    doc = emit_graph_selection_rationale(
        section_id="executive_summary",
        target_company="Acme",
        target_role="SVP IT",
        jd_text="enterprise architecture data platforms",
        graph_digest=expected,
    )
    assert doc["graph_digest"] == expected
    assert doc.get("graph_digest_scope") == "full_graph_payload"
