"""W5: resume spine skill bundle + D7 FEC set equality."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.proof_pool_resolver import SectionProofPool, resolve_section_proof_pool
from apps_rg.runtime.spine.c0_fec_compose import build_spine_c0_fec_artifact
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.spine.graph_skills_fec_set_equality import (
    D7_SET_EQUALITY_LANES,
    audit_all_d7_lanes,
    audit_d7_fec_resolver_set_equality,
    extract_fec_fact_ids,
    extract_resolver_fact_ids,
)
from apps_rg.runtime.spine.resume_spine_skill_bundle import build_resume_spine_skill_bundle

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def _patch_spine_c0(monkeypatch: pytest.MonkeyPatch) -> None:
    deactivate_fixture_dev_bypass()
    monkeypatch.setenv("APPS_RG_C0_EVIDENCE_ROOM", "0")
    from agentic_core.runtime.contracts.final_evidence_contract import (
        FinalEvidenceContract,
        SUPPORT_STATUS_PASS,
    )
    from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF

    def _fake(**_: object) -> FinalEvidenceContract:
        return FinalEvidenceContract(
            request_id="req-w5",
            run_id="run-w5",
            app_id="apps_rg",
            trace_id="trace-w5",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="digest-w5",
            graph_expansion_refs=(C0_GRAPH_LANE_NA_REF,),
            dense_search_refs=("chromadb:fact_vectors:test",),
        )

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        _fake,
    )


def _args() -> SimpleNamespace:
    return SimpleNamespace(
        target_company="Acme",
        target_title="VP Engineering",
        target_role="VP Engineering",
        jd_text="Platform and agentic systems.",
        briefing="Regulated delivery.",
        base_resume_ref="",
    )


def _minimal_pool(section: str) -> SectionProofPool:
    fid = f"bul_{section}_001" if section != "executive_summary" else "fact_exec_001"
    return SectionProofPool(
        section=section,
        proof_source="augmented_skills_graph",
        proof_pool_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        proof_pool_digest="digest",
        selected_fact_plan={"facts": [{"fact_id": fid, "claim_text": "Built platform."}]},
        allowed_fact_ids_ordered=[fid],
        allowed_fact_ids={fid},
        bullet_rows=[],
        proof_pool_metadata={
            "proof_pool_type": "augmented_skills_graph",
            "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            "c03_graphrag_bound": {
                "support_status": "SUPPORTED",
                "graph_lineage_refs": ["ref:graph:version:v1"],
                "final_evidence_contract_snapshot": {
                    "evidence_items": [{"evidence_id": f"evidence:graph:{fid}", "source_fact_id": fid}],
                    "support_status": "SUPPORTED",
                },
            },
            "selected_skill_rows": [
                {
                    "skill_id": f"skill_{section}_test",
                    "fact_id_links": [fid],
                    "graph_hop_path": ["track", "pillar", f"skill_{section}_test", fid],
                    "activation_status": "ACTIVE_CONFIRMED",
                }
            ],
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


def test_build_resume_spine_skill_bundle_dedupe() -> None:
    bundle = build_resume_spine_skill_bundle(repo_root=REPO, lanes=("unify_bullets", "ibm_bullets"))
    assert bundle["schema"] == "resume_spine_skill_bundle_v1"
    assert "bundle_digest" in bundle
    assert bundle["per_lane_summary"]["unify_bullets"]["allowed_fact_count"] >= 1


def test_d7_set_equality_minimal_pool() -> None:
    pool = _minimal_pool("unify_bullets")
    spine = build_section_front_spine_from_args(section_id="unify_bullets", args=_args(), repo_root=REPO)
    bridge = build_spine_c0_fec_artifact(section_id="unify_bullets", front_spine=spine, pool=pool)
    row = audit_d7_fec_resolver_set_equality(section_id="unify_bullets", pool=pool, bridge=bridge)
    assert row["set_equal"] is True
    assert row["fec_only_ids"] == []
    assert row["resolver_only_ids"] == []
    assert row["status"] == "PASS"


def test_extract_fec_and_resolver_ids() -> None:
    pool = _minimal_pool("ibm_bullets")
    spine = build_section_front_spine_from_args(section_id="ibm_bullets", args=_args(), repo_root=REPO)
    bridge = build_spine_c0_fec_artifact(section_id="ibm_bullets", front_spine=spine, pool=pool)
    assert extract_resolver_fact_ids(pool) == extract_fec_fact_ids(bridge.bridge_doc)


@pytest.mark.slow
def test_d7_all_lanes_contract() -> None:
    # D7 canonical coverage expanded 6 -> 10 lanes (graph-skills enhancement W0-W10:
    # added insurtech/ey bullets + all four narratives + executive_summary). The pin
    # tracks len(D7_SET_EQUALITY_LANES) so a dropped lane still trips it; all 10 lanes
    # report set_equal / d7_all_pass (verified — no FEC/resolver drift).
    assert len(D7_SET_EQUALITY_LANES) == 10
    receipt = audit_all_d7_lanes(repo_root=REPO)
    assert receipt["d7_target_count"] == 10
    assert len(receipt["lanes"]) == 10
    assert receipt["d7_all_pass"] is True
    assert receipt["status"] == "PASS"
    for lane in D7_SET_EQUALITY_LANES:
        row = next(r for r in receipt["lanes"] if r["lane"] == lane)
        assert row["set_equal"], f"{lane}: {row}"


def test_resolve_pool_product_visible_false() -> None:
    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=REPO,
        product_visible=False,
    )
    assert pool.proof_source == "augmented_skills_graph"
