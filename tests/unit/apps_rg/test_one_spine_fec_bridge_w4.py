"""Wave 4: RouteContract → section FEC bridge → section PA (product-visible kill switch)."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.spine.c0_fec_compose import (
    FEC_BRIDGE_MODE_SECTION,
    SectionFecBridgePreconditionError,
    assert_section_pa_fec_preconditions,
    build_section_fec_bridge,
    fec_bridge_kill_switch_enabled,
    resolve_pa_proof_authority_for_compile,
)
from apps_rg.runtime.spine.front_contracts import (
    SectionFrontSpineBridge,
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.sections.executive_summary_pa import compile_executive_summary_prompt

REPO = Path(__file__).resolve().parents[3]


def _args(**overrides: object) -> SimpleNamespace:
    base = {
        "target_company": "Acme Corp",
        "target_title": "VP Engineering",
        "target_role": "VP Engineering",
        "jd_text": "Lead platform engineering and agentic systems.",
        "briefing": "Emphasize regulated delivery.",
        "base_resume_ref": "",
        "selected_role_fact_set": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _minimal_pool(*, pp_meta: dict | None = None) -> SectionProofPool:
    facts = [{"fact_id": "bul_acme_001", "claim_text": "Built platform."}]
    plan = {"facts": facts}
    meta = pp_meta or {
        "proof_pool_type": "augmented_skills_graph",
        "augmented_skills_graph_present": True,
        "graph_ref": "apps_rg/fixtures/graph.json",
        "graph_version": "v1",
        "c03_graphrag_bound": {
            "support_status": "SUPPORTED",
            "graph_lineage_refs": ["ref:graph:version:v1"],
            "final_evidence_contract_snapshot": {
                "evidence_items": [{"evidence_id": "evidence:graph:bul_acme_001"}],
                "support_status": "SUPPORTED",
            },
        },
    }
    return SectionProofPool(
        section="executive_summary",
        proof_source="augmented_skills_graph",
        proof_pool_ref="apps_rg/fixtures/graph.json",
        proof_pool_digest="abc",
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=["bul_acme_001"],
        allowed_fact_ids={"bul_acme_001"},
        bullet_rows=[],
        proof_pool_metadata=meta,
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="base.json",
        base_resume_json_hash="hash",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )


def _front_spine(section_id: str = "executive_summary") -> SectionFrontSpineBridge:
    return build_section_front_spine_from_args(
        section_id=section_id,
        args=_args(),
        repo_root=REPO,
    )


def test_fec_kill_switch_enabled_by_default():
    assert fec_bridge_kill_switch_enabled() is True


def test_pa_blocked_without_fec_bridge_product_visible():
    payload = {
        "product_visible": True,
        "selected_fact_plan": {"facts": [{"fact_id": "bul_acme_001", "claim_text": "x"}]},
        "allowed_fact_ids": ["bul_acme_001"],
        "proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"},
    }
    with pytest.raises(SectionFecBridgePreconditionError, match="requires section_fec_bridge"):
        assert_section_pa_fec_preconditions(payload)


def test_fec_bridge_requires_route_contract_ref_at_build():
    spine = _front_spine()
    broken = SectionFrontSpineBridge(
        section_id="executive_summary",
        validated_request=spine.validated_request,
        l1_plan=spine.l1_plan,
        route=None,
    )
    with pytest.raises(SectionFecBridgePreconditionError, match="RouteContract"):
        build_spine_c0_fec_artifact(
            section_id="executive_summary",
            front_spine=broken,
            pool=_minimal_pool(),
        )


def test_fec_bridge_references_route_and_proof_pool():
    bridge = build_spine_c0_fec_artifact(
        section_id="executive_summary",
        front_spine=_front_spine(),
        pool=_minimal_pool(),
    )
    doc = bridge.bridge_doc
    assert doc["route_contract_ref"] == "route_contract.json"
    assert doc["proof_pool_ref"]
    assert doc["proof_pool_digest"] == "abc"
    assert doc["fec_bridge_mode"] == FEC_BRIDGE_MODE_SECTION


def test_fec_bridge_carries_lineage_and_support_status():
    bridge = build_spine_c0_fec_artifact(
        section_id="executive_summary",
        front_spine=_front_spine(),
        pool=_minimal_pool(),
    )
    doc = bridge.bridge_doc
    assert doc["support_status"] == "SUPPORTED"
    assert doc["graph_lineage_refs"]
    assert doc["citation_lineage_refs"]
    assert doc["srfs_ref"] == ""


def test_fec_bridge_does_not_claim_canonical_c0_stages():
    bridge = build_spine_c0_fec_artifact(
        section_id="executive_summary",
        front_spine=_front_spine(),
        pool=_minimal_pool(),
    )
    doc = bridge.bridge_doc
    assert doc["canonical_c0_2_claimed"] is False
    assert doc["canonical_c0_3_claimed"] is False
    assert doc["canonical_c0_5_claimed"] is False
    assert doc["canonical_c0_5_fec"] is False
    assert doc["fec_shape_only"] is True


def test_pa_consumes_fec_bridge_not_raw_proof_pool():
    bridge = build_spine_c0_fec_artifact(
        section_id="executive_summary",
        front_spine=_front_spine(),
        pool=_minimal_pool(),
    )
    payload = {
        "product_visible": True,
        "section_fec_bridge": bridge.bridge_doc,
        "raw_proof_pool_direct_to_pa": False,
        "proof_pool_metadata": {"proof_pool_type": "should_not_be_used"},
        "selected_fact_plan": bridge.bridge_doc["source_fact_ids"]
        and {"facts": [{"fact_id": "bul_acme_001", "claim_text": "Built platform."}]},
        "allowed_fact_ids": ["bul_acme_001"],
        "target_title": "VP",
        "target_company": "Acme",
        "jd_text": "jd",
        "briefing": "brief",
    }
    pa_meta, consumed = resolve_pa_proof_authority_for_compile(payload)
    assert consumed is True
    assert pa_meta.get("fec_bridge_mode") == FEC_BRIDGE_MODE_SECTION
    assert pa_meta.get("proof_pool_type") == "augmented_skills_graph"


def test_compile_blocked_without_fec_bridge():
    payload = {
        "product_visible": True,
        "selected_fact_plan": {"facts": [{"fact_id": "bul_acme_001", "claim_text": "x"}]},
        "allowed_fact_ids": ["bul_acme_001"],
        "target_title": "VP",
        "target_company": "Acme",
        "jd_text": "jd",
        "briefing": "brief",
        "proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"},
    }
    with pytest.raises(SectionFecBridgePreconditionError):
        compile_executive_summary_prompt(payload, run_id="run-test")


def test_fixture_dev_bypass_allows_raw_proof_pool_non_product():
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        payload = {
            "product_visible": True,
            "selected_fact_plan": {"facts": [{"fact_id": "bul_acme_001", "claim_text": "x"}]},
            "allowed_fact_ids": ["bul_acme_001"],
            "target_title": "VP",
            "target_company": "Acme",
            "jd_text": "jd",
            "briefing": "brief",
            "proof_pool_metadata": {
                "proof_pool_type": "base_resume_fallback",
                "skills_source_authority_status": "BLOCKED",
            },
        }
        pa_meta, consumed = resolve_pa_proof_authority_for_compile(payload)
        assert consumed is False
        assert pa_meta.get("proof_pool_type") == "base_resume_fallback"
    finally:
        deactivate_fixture_dev_bypass()


def test_raw_proof_pool_direct_flag_blocked():
    bridge = build_spine_c0_fec_artifact(
        section_id="executive_summary",
        front_spine=_front_spine(),
        pool=_minimal_pool(),
    )
    payload = {
        "product_visible": True,
        "section_fec_bridge": bridge.bridge_doc,
        "raw_proof_pool_direct_to_pa": True,
    }
    with pytest.raises(SectionFecBridgePreconditionError, match="raw_proof_pool_direct_to_pa"):
        assert_section_pa_fec_preconditions(payload)
