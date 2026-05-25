"""Wave 5A: FEC bridge propagated to all product-visible section lanes."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.dispatch.input_authority_prompt_block import finalize_section_compiled_with_proof_pool
from apps_rg.runtime.spine.c0_fec_compose import (
    FEC_BRIDGE_MODE_SECTION,
    FEC_BRIDGE_RECEIPT,
    SectionFecBridgePreconditionError,
    build_spine_c0_fec_artifact,
    wire_spine_c0_fec_for_section,
)
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.proof_pool_resolver import SectionProofPool, resolve_section_proof_pool

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def _patch_spine_c0_retrieve(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit FEC bridge tests use minimal pools — mock spine C0 retrieve and skip evidence room."""
    deactivate_fixture_dev_bypass()
    monkeypatch.setenv("APPS_RG_C0_EVIDENCE_ROOM", "0")
    from agentic_core.runtime.contracts.final_evidence_contract import (
        FinalEvidenceContract,
        SUPPORT_STATUS_PASS,
    )
    from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF

    def _fake_c0_retrieve(**_: object) -> FinalEvidenceContract:
        return FinalEvidenceContract(
            request_id="req-fec-bridge-test",
            run_id="run-fec-bridge-test",
            app_id="apps_rg",
            trace_id="trace-fec-bridge-test",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="digest-test",
            graph_expansion_refs=(C0_GRAPH_LANE_NA_REF,),
            dense_search_refs=("chromadb:fact_vectors:test",),
        )

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        _fake_c0_retrieve,
    )


W5A_SECTIONS = (
    "headline",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
    "executive_summary",
)


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


def _minimal_pool(section: str) -> SectionProofPool:
    fid = f"bul_{section}_001"
    return SectionProofPool(
        section=section,
        proof_source="augmented_skills_graph",
        proof_pool_ref="apps_rg/fixtures/graph.json",
        proof_pool_digest="digest",
        selected_fact_plan={"facts": [{"fact_id": fid, "claim_text": "Built platform."}]},
        allowed_fact_ids_ordered=[fid],
        allowed_fact_ids={fid},
        bullet_rows=[],
        proof_pool_metadata={
            "proof_pool_type": "augmented_skills_graph",
            "augmented_skills_graph_present": True,
            "graph_ref": "apps_rg/fixtures/graph.json",
            "graph_version": "v1",
            "c03_graphrag_bound": {
                "support_status": "SUPPORTED",
                "graph_lineage_refs": ["ref:graph:version:v1"],
                "final_evidence_contract_snapshot": {
                    "evidence_items": [{"evidence_id": f"evidence:graph:{fid}"}],
                    "support_status": "SUPPORTED",
                },
            },
        },
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


@pytest.mark.parametrize("section_id", W5A_SECTIONS)
def test_fec_bridge_builds_per_section(section_id: str):
    spine = build_section_front_spine_from_args(
        section_id=section_id,
        args=_args(),
        repo_root=REPO,
    )
    pool = _minimal_pool(section_id)
    bridge = build_spine_c0_fec_artifact(
        section_id=section_id,
        front_spine=spine,
        pool=pool,
    )
    doc = bridge.bridge_doc
    assert doc["fec_bridge_mode"] == FEC_BRIDGE_MODE_SECTION
    assert doc["route_contract_ref"] == "route_contract.json"
    assert doc["canonical_c0_5_claimed"] is True


@pytest.mark.parametrize("section_id", W5A_SECTIONS)
def test_wire_emits_artifacts(tmp_path: Path, section_id: str):
    spine = build_section_front_spine_from_args(
        section_id=section_id,
        args=_args(),
        repo_root=REPO,
    )
    pool = _minimal_pool(section_id)
    payload: dict = {"allowed_fact_ids": list(pool.allowed_fact_ids_ordered)}
    wire_spine_c0_fec_for_section(
        artifact_dir=tmp_path,
        section_id=section_id,
        front_spine=spine,
        pool=pool,
        runtime_payload=payload,
    )
    assert (tmp_path / "final_evidence_contract_bridge.json").is_file()
    assert (tmp_path / FEC_BRIDGE_RECEIPT).is_file()
    assert (tmp_path / "route_contract.json").is_file()
    assert (tmp_path / "c0_metrics.json").is_file()
    assert payload.get("section_fec_bridge")
    assert payload.get("c0_metrics_ref") == "c0_metrics.json"
    assert payload.get("support_status")


def test_finalize_section_compile_blocked_without_fec_bridge():
    from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt

    fake_art = type("A", (), {"messages": [{"role": "user", "content": "x"}], "template_id": "t", "prompt_hash": "h", "slot_count": 1})()
    compiled = SectionCompiledPrompt(
        section_id="unify_bullets",
        apps_rg_prompt_template_ref="ref",
        artifact=fake_art,
    )
    payload = {
        "allowed_fact_ids": ["bul_x"],
        "proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"},
    }
    with pytest.raises(SectionFecBridgePreconditionError):
        finalize_section_compiled_with_proof_pool(compiled, runtime_payload=payload)


def test_fixture_bypass_allows_raw_proof_pool_non_product():
    from apps_rg.runtime.spine.c0_fec_compose import resolve_pa_proof_authority_for_compile

    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        payload = {
            "allowed_fact_ids": ["bul_x"],
            "proof_pool_metadata": {"proof_pool_type": "broad_skills_ledger"},
        }
        pp, consumed = resolve_pa_proof_authority_for_compile(payload)
        assert consumed is False
        assert pp.get("proof_pool_type") == "broad_skills_ledger"
    finally:
        deactivate_fixture_dev_bypass()


def test_proof_pool_still_requires_front_spine():
    with pytest.raises(Exception, match="SectionFrontSpineBridge"):
        resolve_section_proof_pool(
            section="competencies",
            repo_root=REPO,
            product_visible=True,
        )
