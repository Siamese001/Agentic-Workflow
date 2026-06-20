"""C0.3/C0.4 executive_summary graph ref classes, projection, and compression."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.c0.c03_graph_expansion import expand_c03_graph_bindings
from apps_rg.runtime.c0.c03_graph_ref_policy import (
    MAX_CLAIM_SUPPORT_SKILLS_PER_FACT,
    RoleFamilyProjectionError,
    build_graph_targeting_for_pa,
    compress_binding_for_executive_summary,
    resolve_role_family_projection,
)
from apps_rg.runtime.c0.c04_exec_summary_shaping import shape_executive_summary_c04
from apps_rg.runtime.spine.c0_fec_compose import resolve_pa_proof_authority_for_compile
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_jd_alignment_proof_flags,
    check_exec_summary_no_mechanism_inventory,
)

REPO = Path(__file__).resolve().parents[5]


def test_resolve_role_family_brokerage_not_generic_fallback() -> None:
    proj = resolve_role_family_projection("INSURANCE_BROKERAGE_IT_INNOVATION", repo_root=REPO)
    assert proj["projection_source"] == "sqlite_role_family_projection"
    assert proj["fallback_pillar_bridge_used"] is False
    assert "pillar_insurance_brokerage_distribution" in proj["pillar_hint_ids"]
    assert proj["targeting_degraded_explicit"] is False
    assert proj["release_eligible_targeting_proof"] is True


def test_resolve_role_family_projection_unknown_role_fails_closed() -> None:
    with pytest.raises(RoleFamilyProjectionError, match="missing role_family_projection row"):
        resolve_role_family_projection("COMPLETELY_UNKNOWN_ROLE_XYZ_NO_MATCH", repo_root=REPO)


def test_compress_overloaded_engineering_platform_binding() -> None:
    binding = {
        "fact_id": "fact_engineering_platform_001",
        "graph_node_refs": [
            "skill_deterministic_route_selection",
            "skill_managed_workflow_orchestration",
            "skill_governed_agentic_systems_architecture",
            "skill_graph_aware_relationship_grounding",
            "skill_runtime_gate_mesh_design",
            "skill_sandboxed_execution_design",
            "skill_route_replay_and_idempotency_design",
            "skill_bounded_agent_execution",
            "skill_dense_sparse_exact_retrieval_design",
            "skill_layered_runtime_spine_design",
            "skill_authority_ordered_prompt_packaging",
            "skill_side_effect_bounded_action_design",
            "skill_replayable_runtime_design",
            "skill_app_overlay_runtime_binding",
            "skill_agentic_control_plane_design",
            "skill_route_contract_design",
            "skill_reusable_ai_ip_design",
            "skill_sr_cloud_data_platform_engineering",
            "skill_app_specific_runtime_overlay_design",
        ],
        "skill_cluster_refs": ["pillar_agentic_ai_platforms", "pillar_actuarial_foundation"],
    }
    proj = resolve_role_family_projection("INSURANCE_BROKERAGE_IT_INNOVATION", repo_root=REPO)
    out = compress_binding_for_executive_summary(binding, role_family_projection=proj)
    assert len(out["claim_support_graph_refs"]) <= MAX_CLAIM_SUPPORT_SKILLS_PER_FACT
    assert out["mechanism_overloaded"] is True
    assert out["executive_capability_phrases"]
    assert len(out["suppressed_skill_refs"]) >= 10


def test_receipt_only_refs_excluded_from_pa_authority() -> None:
    bindings = [
        {
            "fact_id": "fact_exec_002",
            "claim_support_graph_refs": ["skill_enterprise_workflow_adoption"],
            "targeting_graph_refs": ["pillar_executive_leadership"],
            "receipt_only_lineage_refs": ["ledger:fact_exec_002"],
        }
    ]
    proj = resolve_role_family_projection("INSURANCE_BROKERAGE_IT_INNOVATION", repo_root=REPO)
    receipt = ["ref:graph:edge:edge_skill_fact_skill_ai_platform_commercialization_fact_exec_002"]
    pa_block = build_graph_targeting_for_pa(
        bindings=bindings,
        role_family_projection=proj,
        receipt_only_lineage_refs=receipt,
    )
    payload = {
        "product_visible": True,
        "section_fec_bridge": {
            "fec_bridge_mode": "section_fec_bridge",
            "route_contract_ref": "route_contract.json",
            "pa_proof_authority_metadata": {
                **pa_block,
                "receipt_only_json_expansion_excluded_from_pa": True,
                "graph_expansion_refs": receipt,
            },
        },
    }
    pa, via = resolve_pa_proof_authority_for_compile(payload)
    assert via is True
    assert "ref:graph:edge:" not in str(pa.get("graph_expansion_refs") or "")
    assert pa_block["claim_support_graph_refs"] == ["skill_enterprise_workflow_adoption"]


def test_jd_alignment_fails_on_fallback_pillar_bridge() -> None:
    parsed = {
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "graph_targeting": {
                "fallback_pillar_bridge_used": True,
                "release_eligible_targeting_proof": True,
                "targeting_degraded_explicit": False,
                "projection_source": "missing_no_taxonomy_pillars",
            },
        }
    }
    ok, reason = check_exec_summary_jd_alignment_proof_flags(parsed)
    assert ok is False
    assert reason and "fallback_pillar_bridge" in reason


def test_jd_alignment_rejects_degraded_taxonomy_projection() -> None:
    parsed = {
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "graph_targeting": {
                "fallback_pillar_bridge_used": False,
                "release_eligible_targeting_proof": False,
                "targeting_degraded_explicit": True,
                "projection_source": "taxonomy_pillar_hints_synthesized",
                "sqlite_projection_row_found": False,
            },
        }
    }
    ok, reason = check_exec_summary_jd_alignment_proof_flags(parsed)
    assert ok is False
    assert reason and "sqlite_role_family_projection" in reason


def test_mechanism_gate_reports_dominant_fact_and_bindings() -> None:
    text = (
        "Engineered governed AI platforms emphasizing deterministic routing, multi-agent orchestration, "
        "graph-aware retrieval, and policy gating for regulated workflows."
    )
    parsed = {
        "c0_graph_diagnostics": {
            "dominant_source_fact_id": "fact_engineering_platform_001",
            "dominant_claim_support_graph_refs": [
                "skill_deterministic_route_selection",
                "skill_managed_workflow_orchestration",
            ],
            "dominant_suppressed_skill_refs": ["skill_sandboxed_execution_design"],
        }
    }
    ok, reason = check_exec_summary_no_mechanism_inventory(text, parsed)
    assert ok is False
    assert reason
    assert "fact_engineering_platform_001" in reason
    assert "skill_deterministic_route_selection" in reason


def test_c04_demotes_overloaded_platform_fact() -> None:
    bindings = [
        {
            "fact_id": "fact_engineering_platform_001",
            "mechanism_overloaded": True,
            "skill_binding_count_before": 19,
            "skill_binding_count_after": 4,
            "claim_support_allowed": True,
            "binding_source": "skill_fact_links",
            "graph_support_strength": "DIRECT",
        },
        {
            "fact_id": "fact_exec_002",
            "mechanism_overloaded": False,
            "claim_support_allowed": True,
            "binding_source": "skill_fact_links",
            "graph_support_strength": "DIRECT",
        },
    ]
    atoms = [
        {"fact_id": "fact_engineering_platform_001", "proof_status": "proof_eligible"},
        {"fact_id": "fact_exec_002", "proof_status": "proof_eligible"},
    ]
    c04 = {
        "schema_version": "c04_stratify_v1",
        "section_id": "executive_summary",
        "strata": {"MUST_USE": ["fact_engineering_platform_001", "fact_exec_002"], "SUPPORTING": [], "BACKGROUND": [], "CONTRADICTS": [], "EXCLUDED": []},
        "allowed_fact_ids": ["fact_engineering_platform_001", "fact_exec_002"],
        "excluded_fact_ids": [],
    }
    shaped = shape_executive_summary_c04(c04, bindings=bindings, atoms=atoms)
    assert "fact_engineering_platform_001" in shaped["exec_summary_compression"]["demoted_overloaded_to_supporting"]
    assert shaped["strata"]["MUST_USE"][0] == "fact_exec_002"
