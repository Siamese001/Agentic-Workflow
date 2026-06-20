"""Targeted tests for competencies graph-skill rigor wiring (competency capability bundles).

Covers: registry guards, bundle data integrity, C0 evidence packet, proof-pool attach,
X2 gate behavior (bundle id / graph nodes / lineage / default_fid / generic taxonomy /
JD-only / coverage / rigor / density), calibration-vs-source discipline, and config gate.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from apps_rg.runtime.sections import competency_capability_registry as reg
from apps_rg.runtime.sections.competency_capability_evidence import (
    COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER,
    attach_competency_bundles_to_proof_pool_metadata,
    augment_bound_category_family_terms,
    build_competency_capability_section_packet,
    format_competency_capability_evidence_pack,
    is_flat_taxonomy_only_packet,
    stamp_competency_bundle_bindings,
)
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)
from apps_rg.runtime.validators import competencies_quality_x2 as q

_REPO_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _good_category(
    cat_id: str,
    label: str,
    bundle_id: str,
    capability_family: str,
    fact_ids: list[str],
    skill_ids: list[str],
    terms: list[str],
) -> dict:
    return {
        "category_id": cat_id,
        "category_label": label,
        "competency_bundle_id": bundle_id,
        "capability_family": capability_family,
        "graph_skill_node_ids": list(skill_ids),
        "source_fact_ids": list(fact_ids),
        "terms": [
            {
                "term": t,
                "text": t,
                "source_fact_ids": [fact_ids[0]],
                "graph_skill_node_ids": [skill_ids[0]],
                "support_class": "FACT_AND_SKILL_GRAPH",
            }
            for t in terms
        ],
    }


def _good_competencies() -> list[dict]:
    return [
        _good_category(
            "agentic", "AI Platform Leadership",
            "ccb_agentic_platforms", "agentic_platforms",
            ["fact_engineering_platform_001"],
            ["skill_governed_agentic_systems_architecture"],
            ["governed agentic systems architecture", "multi-agent orchestration fabric", "agentic control plane"],
        ),
        _good_category(
            "governance", "Governance, Risk & Compliance",
            "ccb_runtime_governance", "runtime_governance",
            ["fact_engineering_platform_001"],
            ["skill_runtime_gate_mesh_design"],
            ["runtime gate mesh design", "fail-closed gate semantics", "policy-bound runtime controls"],
        ),
        _good_category(
            "retrieval", "Retrieval Engineering",
            "ccb_retrieval_context_engineering", "retrieval_context_engineering",
            ["fact_engineering_platform_003"],
            ["skill_context_engineering"],
            ["dense-sparse-exact retrieval design", "graph-aware grounding", "context engineering"],
        ),
        _good_category(
            "llmops", "Reliability & Evaluation",
            "ccb_llmops_reliability", "llmops_reliability",
            ["fact_engineering_platform_003", "fact_engineering_platform_004"],
            ["skill_audit_grade_observability"],
            ["audit-grade observability", "evaluation gauntlet design", "multi-judge calibration"],
        ),
        _good_category(
            "distributed", "Distributed Systems",
            "ccb_distributed_systems_engineering", "distributed_systems_engineering",
            ["fact_engineering_platform_002"],
            ["skill_sr_cloud_data_platform_engineering"],
            ["cloud-native microservices", "streaming analytics pipelines", "lakehouse data platform"],
        ),
        _good_category(
            "productization", "Platform Productization",
            "ccb_platform_productization", "platform_productization",
            ["fact_engineering_platform_006"],
            ["skill_agentic_platform_productization"],
            ["platform commercialization", "reusable platform architecture", "demoable accelerators"],
        ),
        _good_category(
            "leadership", "Engineering Leadership",
            "ccb_engineering_leadership", "engineering_leadership",
            ["fact_exec_001"],
            ["skill_svp_it_strategy_innovation"],
            ["engineering organization scale-out", "platform operating model", "board-level alignment"],
        ),
    ]


def _competencies_proof_meta(extra_fields: dict | None = None) -> dict:
    plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=_REPO_ROOT,
        section_id="competencies",
        target_role="SVP Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform control plane",
        briefing_text="regulated enterprise",
    )
    meta: dict = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
        "selected_graph_evidence_plan": plan,
    }
    if extra_fields:
        meta.update(extra_fields)
    return attach_competency_bundles_to_proof_pool_metadata(meta, section_id="competencies")


# ---------------------------------------------------------------------------
# Bundle data / registry integrity
# ---------------------------------------------------------------------------


def test_all_bundles_valid_and_required_families_present():
    bundles = reg.get_bundles_for_section("competencies")
    assert bundles, "no competency bundles for section"
    families = set()
    for b in bundles:
        ok, violations = reg.validate_competency_bundle(b)
        assert ok, f"{b.get('competency_bundle_id')}: {violations}"
        families.add(b["capability_family"])
    for required in reg.REQUIRED_CAPABILITY_FAMILIES:
        assert required in families, f"missing required family {required}"


def test_required_family_bundles_one_per_family():
    fam_bundles = reg.required_family_bundles()
    for fam in reg.REQUIRED_CAPABILITY_FAMILIES:
        assert fam in fam_bundles, f"no active bundle for {fam}"
        assert fam_bundles[fam].get("graph_skill_node_ids")


# ---------------------------------------------------------------------------
# Registry guards
# ---------------------------------------------------------------------------


def test_assert_competency_bundle_id_present_raises_when_absent():
    with pytest.raises(reg.CompetencyBundleError):
        reg.assert_competency_bundle_id_present({"category_label": "Cloud & Partner Ecosystems"})
    reg.assert_competency_bundle_id_present({"competency_bundle_id": "ccb_agentic_platforms"})


def test_reject_flat_taxonomy_only_bundle():
    with pytest.raises(reg.CompetencyBundleError):
        reg.reject_flat_taxonomy_only_bundle(
            {"display_label_candidate": "Cloud & Partner Ecosystems", "graph_skill_node_ids": []}
        )
    # graph-backed bundle is accepted
    reg.reject_flat_taxonomy_only_bundle(
        {"display_label_candidate": "Cloud & Partner Ecosystems", "graph_skill_node_ids": ["skill_x"]}
    )


def test_reject_default_fid_only_support():
    with pytest.raises(reg.CompetencyBundleError):
        reg.reject_default_fid_only_support(
            {"term": "x", "proof_source": "default_fid_backfill"}
        )
    # has graph node → ok
    reg.reject_default_fid_only_support(
        {"term": "x", "proof_source": "default_fid_backfill", "graph_skill_node_ids": ["skill_x"]}
    )


def test_reject_jd_only_skill():
    with pytest.raises(reg.CompetencyBundleError):
        reg.reject_jd_only_skill({"term": "kubernetes orchestration"}, jd_text="we need kubernetes orchestration")
    # graph-supported term → ok even if in JD
    reg.reject_jd_only_skill(
        {"term": "kubernetes orchestration", "graph_skill_node_ids": ["skill_x"]},
        jd_text="we need kubernetes orchestration",
    )


def test_reject_archive_and_base_prose_hydration():
    prose = "Led the modernization of the platform to deliver value across the enterprise and reduce risk."
    with pytest.raises(reg.CompetencyBundleError):
        reg.reject_archive_prose_hydration(prose)
    with pytest.raises(reg.CompetencyBundleError):
        reg.reject_base_resume_prose_hydration(prose)
    # short capability phrase is fine
    reg.reject_archive_prose_hydration("runtime gate mesh design")
    reg.reject_base_resume_prose_hydration("runtime gate mesh design")


def test_classify_support_distinguishes_sources():
    assert reg.classify_support({"graph_skill_node_ids": ["s"]}) == reg.SUPPORT_GRAPH_BACKED
    assert reg.classify_support({"competency_bundle_id": "ccb_x"}) == reg.SUPPORT_GRAPH_BACKED
    assert reg.classify_support({"term": "x", "proof_source": "default_fid_backfill"}) == reg.SUPPORT_FALLBACK_DEFAULT
    assert reg.classify_support({"term": "kubernetes"}, jd_text="kubernetes") == reg.SUPPORT_JD_ONLY
    assert (
        reg.classify_support({"term": "scaled teams"}, base_or_archive_blob_lower="scaled teams")
        == reg.SUPPORT_ARCHIVE_OR_BASE_CALIBRATION
    )


# ---------------------------------------------------------------------------
# C0 evidence pack + proof pool attach
# ---------------------------------------------------------------------------


def test_c0_evidence_pack_has_marker_and_authority_lines():
    payload: dict = {"proof_pool_metadata": _competencies_proof_meta()}
    pack = format_competency_capability_evidence_pack(payload, section_id="competencies")
    assert COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER in pack
    assert "proof_authority = graph_competency_bundles_plus_linked_source_facts" in pack
    assert "base_resume_usage = calibration_only" in pack
    assert "archive_usage = provenance_inventory_only" in pack
    assert "jd_usage = targeting_only" in pack
    assert "competency_bundle_id" in pack
    assert payload.get("competency_bundle_ids")


def test_proof_pool_attach_sets_consumption_flags():
    meta = _competencies_proof_meta()
    assert meta["competency_capability_bundle_consumption"] is True
    assert meta["competency_capability_bundle_consumption_mode"] == "competency_bundle_required"
    assert meta["competency_capability_bundles"]
    assert meta["flat_taxonomy_only_graph_context_forbidden"] is True
    # non-competencies section is untouched
    assert attach_competency_bundles_to_proof_pool_metadata({}, section_id="headline") == {}


def test_is_flat_taxonomy_only_packet():
    assert is_flat_taxonomy_only_packet({"graph_skill_node_ids": ["s"]}) is True
    assert is_flat_taxonomy_only_packet({"competency_bundle_ids": ["ccb_x"]}) is False
    packet = build_competency_capability_section_packet("competencies")
    assert is_flat_taxonomy_only_packet({"competency_capability_section_packet": packet}) is False


def test_stamp_competency_bundle_bindings_attaches_ids():
    cats = [
        {"category_id": "ai_platform_leadership", "category_label": "AI Platform Leadership", "terms": []},
        {"category_id": "governance_risk_compliance", "category_label": "Governance", "terms": []},
    ]
    stamp_competency_bundle_bindings(cats)
    assert cats[0]["competency_bundle_id"]
    assert cats[0]["graph_skill_node_ids"]
    assert cats[1]["competency_bundle_id"]


def test_stamp_competency_bundle_bindings_resolves_overlapping_category_targets():
    cats = [
        {"category_id": "tech_strategy_innovation", "category_label": "Technology Strategy & Innovation", "terms": []},
        {"category_id": "ai_platform_leadership", "category_label": "AI Platform Leadership", "terms": []},
        {"category_id": "engineering_delivery_leadership", "category_label": "Engineering & Delivery Leadership", "terms": []},
        {"category_id": "llmops_reliability", "category_label": "LLMOps & Reliability", "terms": []},
        {"category_id": "cloud_partner_ecosystems", "category_label": "Cloud & Partner Ecosystems", "terms": []},
    ]

    stamp_competency_bundle_bindings(cats)

    by_id = {c["category_id"]: c for c in cats}
    assert by_id["tech_strategy_innovation"]["competency_bundle_id"] == "ccb_retrieval_context_engineering"
    assert by_id["ai_platform_leadership"]["competency_bundle_id"] == "ccb_agentic_platforms"
    assert by_id["engineering_delivery_leadership"]["competency_bundle_id"] == "ccb_engineering_leadership"
    assert by_id["llmops_reliability"]["competency_bundle_id"] == "ccb_llmops_reliability"
    assert by_id["cloud_partner_ecosystems"]["competency_bundle_id"] == "ccb_partnerships_ecosystem_execution"


def test_required_family_gate_counts_partnerships_bundle_family():
    comps = _good_competencies() + [
        _good_category(
            "partnerships",
            "Cloud & Partner Ecosystems",
            "ccb_partnerships_ecosystem_execution",
            "partnerships_ecosystem_execution",
            ["fact_partnerships_gtm_002"],
            ["skill_partner_ibm_aws_alliance_joint_revenue"],
            ["hyperscaler alliance co-sell", "cloud partner ecosystem GTM", "joint revenue execution"],
        )
    ]
    canonical_families = [
        "agentic_platforms",
        "runtime_governance",
        "retrieval_context_engineering",
        "llmops_reliability",
        "distributed_systems_engineering",
        "platform_productization",
        "engineering_leadership",
        "partnerships_ecosystem_execution",
    ]
    for comp, family in zip(comps, canonical_families, strict=True):
        comp["capability_family"] = family
    comps[-1]["competency_bundle_id"] = "ccb_partnerships_ecosystem_execution"

    result = q.check_required_capability_families_covered(comps, min_families=8)

    assert result.passed
    assert "partnerships_ecosystem_execution" in result.observed_value["matched_families"]


def test_missing_family_augmentation_rebinds_target_category_to_injected_bundle():
    packet = {
        "competency_bundles": [
            {
                "competency_bundle_id": "ccb_retrieval_context_engineering",
                "capability_family": "retrieval_context_engineering",
                "graph_skill_node_ids": ["skill_context_engineering"],
                "linked_source_fact_ids": ["fact_engineering_platform_003"],
                "vocabulary_anchors": ["dense-sparse-exact retrieval design"],
            }
        ]
    }
    cats = [
        {
            "category_id": "tech_strategy_innovation",
            "category_label": "Technology Strategy & Innovation",
            "competency_bundle_id": "ccb_agentic_platforms",
            "capability_family": "agentic_platforms",
            "graph_skill_node_ids": ["skill_agentic_control_plane_design"],
            "source_fact_ids": ["fact_engineering_platform_001"],
            "terms": [
                {"term": "Agentic control plane", "source_fact_ids": ["fact_engineering_platform_001"]},
            ],
        }
    ]

    augment_bound_category_family_terms(
        cats,
        packet=packet,
        allowed_fact_ids={"fact_engineering_platform_003"},
    )

    assert cats[0]["competency_bundle_id"] == "ccb_retrieval_context_engineering"
    assert cats[0]["capability_family"] == "retrieval_context_engineering"
    assert any(
        t.get("term") == "Dense-Sparse-Exact Retrieval Design"
        for t in cats[0]["terms"]
        if isinstance(t, dict)
    )


# ---------------------------------------------------------------------------
# X2 gates — pass on good output
# ---------------------------------------------------------------------------


def test_good_competencies_pass_bundle_gates():
    comps = _good_competencies()
    meta = _competencies_proof_meta({"graph_skills_proof_pool": True})
    assert q.check_competency_bundle_id_per_category(comps).passed
    assert q.check_graph_skill_node_ids_per_category(comps).passed
    assert q.check_source_fact_ids_or_graph_lineage_per_category(comps).passed
    assert q.check_competency_bundle_source_fact_alignment(comps, meta).passed
    assert q.check_competency_source_fact_dominance(comps).passed
    assert q.check_default_fid_only_support_forbidden(comps).passed
    assert q.check_generic_taxonomy_only_category_forbidden(comps).passed
    assert q.check_jd_only_skill_forbidden(comps, "unrelated job text").passed
    assert q.check_required_capability_families_covered(comps, min_families=7).passed
    assert q.check_competency_rigor_floor(comps).passed
    assert q.check_technical_density_floor(comps).passed


# ---------------------------------------------------------------------------
# X2 gates — fail on violations
# ---------------------------------------------------------------------------


def test_missing_bundle_id_per_category_fails():
    comps = _good_competencies()
    comps[0].pop("competency_bundle_id")
    assert not q.check_competency_bundle_id_per_category(comps).passed


def test_missing_graph_skill_node_ids_fails():
    comps = _good_competencies()
    comps[0]["graph_skill_node_ids"] = []
    assert not q.check_graph_skill_node_ids_per_category(comps).passed


def test_no_source_facts_or_lineage_fails():
    comps = _good_competencies()
    comps[0]["source_fact_ids"] = []
    comps[0]["graph_skill_node_ids"] = []
    comps[0].pop("competency_bundle_id")
    assert not q.check_source_fact_ids_or_graph_lineage_per_category(comps).passed


def test_bundle_fact_mismatch_fails_when_category_uses_broad_fact():
    comps = _good_competencies()
    meta = _competencies_proof_meta({"graph_skills_proof_pool": True})
    llmops = next(c for c in comps if c["competency_bundle_id"] == "ccb_llmops_reliability")
    llmops["source_fact_ids"] = ["fact_engineering_platform_001"]
    for term in llmops["terms"]:
        term["source_fact_ids"] = ["fact_engineering_platform_001"]
        term["source_fact_id"] = "fact_engineering_platform_001"

    result = q.check_competency_bundle_source_fact_alignment(comps, meta)

    assert not result.passed
    assert result.observed_value[0]["competency_bundle_id"] == "ccb_llmops_reliability"
    assert result.observed_value[0]["reason"] == "no_bundle_fact_intersection"


def test_repeated_source_fact_dominance_fails_anthropic_collapse_pattern():
    comps = _good_competencies()
    partner = {
        "category_id": "cloud_partner_ecosystems",
        "category_label": "Cloud & Partner Ecosystems",
        "competency_bundle_id": "ccb_partnerships_ecosystem_execution",
        "capability_family": "partnerships_ecosystem_execution",
        "graph_skill_node_ids": ["skill_partner_ibm_aws_alliance_joint_revenue"],
        "source_fact_ids": ["fact_partnerships_gtm_002"],
        "terms": [
            {
                "term": "cloud partner ecosystem GTM",
                "text": "cloud partner ecosystem GTM",
                "source_fact_ids": ["fact_partnerships_gtm_002"],
                "graph_skill_node_ids": ["skill_partner_ibm_aws_alliance_joint_revenue"],
            }
        ],
    }
    comps.append(partner)
    for cat in comps[:7]:
        cat["source_fact_ids"] = ["fact_engineering_platform_001"]
        for term in cat["terms"]:
            term["source_fact_ids"] = ["fact_engineering_platform_001"]
            term["source_fact_id"] = "fact_engineering_platform_001"

    result = q.check_competency_source_fact_dominance(comps)

    assert not result.passed
    assert result.observed_value["dominant_source_facts"][0]["source_fact_id"] == "fact_engineering_platform_001"
    assert result.observed_value["dominant_source_facts"][0]["category_count"] == 7


def test_default_fid_only_support_fails():
    comps = _good_competencies()
    comps[0]["terms"][0] = {"term": "laundered term", "proof_source": "default_fid_backfill"}
    assert not q.check_default_fid_only_support_forbidden(comps).passed


def test_generic_taxonomy_only_category_fails_without_graph():
    comps = [
        {
            "category_id": "cloud_partner_ecosystems",
            "category_label": "Cloud & Partner Ecosystems",
            "terms": [{"term": "partnerships", "proof_source": "default_fid_backfill"}],
        }
    ]
    assert not q.check_generic_taxonomy_only_category_forbidden(comps).passed
    # Bundle binding is necessary but not sufficient.
    comps[0]["competency_bundle_id"] = "ccb_partnerships_ecosystem_execution"
    assert not q.check_generic_taxonomy_only_category_forbidden(comps).passed


def test_generic_category_with_bundle_but_zero_graph_terms_fails():
    comps = [
        {
            "category_id": "cloud_partner_ecosystems",
            "category_label": "Cloud & Partner Ecosystems",
            "competency_bundle_id": "ccb_partnerships_ecosystem_execution",
            "graph_skill_node_ids": ["skill_partner_ecosystem"],
            "terms": [
                {"term": "partnerships", "proof_source": "default_fid_backfill"},
                {"term": "ecosystems", "proof_source": "default_fid_backfill"},
                {"term": "co-sell", "proof_source": "default_fid_backfill"},
            ],
        }
    ]

    result = q.check_generic_taxonomy_only_category_forbidden(comps)

    assert not result.passed
    assert result.observed_value[0]["reasons"] == ["too_few_graph_backed_terms"]


def test_generic_category_passes_only_with_bundle_category_skills_and_supported_terms():
    comps = [
        {
            "category_id": "cloud_partner_ecosystems",
            "category_label": "Cloud & Partner Ecosystems",
            "competency_bundle_id": "ccb_partnerships_ecosystem_execution",
            "graph_skill_node_ids": ["skill_partner_ecosystem"],
            "terms": [
                {
                    "term": "cloud partner ecosystem GTM",
                    "source_skill_ids": ["skill_partner_ecosystem"],
                    "source_fact_ids": ["fact_partner_001"],
                },
                {
                    "term": "co-sell enablement mechanics",
                    "source_skill_ids": ["skill_partner_enablement"],
                    "source_fact_ids": ["fact_partner_002"],
                },
                {
                    "term": "technical close motion",
                    "graph_skill_node_ids": ["skill_solution_close"],
                    "source_fact_ids": ["fact_partner_003"],
                },
            ],
        }
    ]

    assert q.check_generic_taxonomy_only_category_forbidden(comps).passed


def test_jd_only_skill_fails():
    comps = [
        {
            "category_id": "x",
            "category_label": "X",
            "terms": [{"term": "real time fraud detection"}],
        }
    ]
    assert not q.check_jd_only_skill_forbidden(comps, "we need real time fraud detection").passed


def test_required_families_not_covered_fails():
    comps = _good_competencies()[:2]  # only 2 families' worth of tokens
    assert not q.check_required_capability_families_covered(comps, min_families=7).passed


def test_rigor_and_density_floors_fail_on_thin_output():
    thin = [{"category_id": "x", "category_label": "X", "terms": [{"term": "ok"}, {"term": "team"}]}]
    assert not q.check_competency_rigor_floor(thin).passed
    assert not q.check_technical_density_floor(thin).passed


# ---------------------------------------------------------------------------
# X2 orchestrator emits bundle gates only in bundle mode
# ---------------------------------------------------------------------------


def test_run_competencies_x2_emits_bundle_gates_in_bundle_mode():
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    comps = _good_competencies()[:6]
    parsed = {
        "categories": comps,
        "competencies": comps,
        "selected_fact_plan": {"section_id": "competencies"},
        "claim_ledger": [],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
    }
    meta = _competencies_proof_meta({"graph_skills_proof_pool": True})
    gates = run_competencies_x2_gates(
        competencies=comps,
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="unrelated",
        bullet_texts_lower=[],
        resume_support_blob="governed agentic runtime gate retrieval evaluation microservices platform leadership",
        allowed_fact_ids={"fact_engineering_platform_001"},
        runtime_generation_status="REAL_LLM",
        proof_pool_metadata=meta,
    )
    gate_ids = {g.gate_id for g in gates}
    for gid in (
        "x2_competencies_capability_bundles_in_proof_pool",
        "x2_competency_bundle_id_required_per_category",
        "x2_graph_skill_node_ids_required_per_category",
        "x2_source_fact_ids_or_graph_lineage_required_per_category",
        "x2_competency_bundle_source_fact_alignment",
        "x2_competency_source_fact_dominance",
        "x2_default_fid_only_support_forbidden",
        "x2_generic_taxonomy_only_category_forbidden",
        "x2_jd_only_skill_forbidden",
        "x2_required_capability_families_covered",
        "x2_competency_rigor_floor_met",
        "x2_technical_density_floor_met",
    ):
        assert gid in gate_ids, f"missing bundle gate {gid}"


def test_run_competencies_x2_omits_bundle_gates_without_bundle_mode():
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    comps = _good_competencies()[:6]
    parsed = {
        "categories": comps,
        "competencies": comps,
        "selected_fact_plan": {"section_id": "competencies"},
        "claim_ledger": [],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
    }
    gates = run_competencies_x2_gates(
        competencies=comps,
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="unrelated",
        bullet_texts_lower=[],
        resume_support_blob="x",
        allowed_fact_ids={"fact_engineering_platform_001"},
        runtime_generation_status="REAL_LLM",
        proof_pool_metadata={},
    )
    gate_ids = {g.gate_id for g in gates}
    assert "x2_competency_bundle_id_required_per_category" not in gate_ids


# ---------------------------------------------------------------------------
# Config gate
# ---------------------------------------------------------------------------


def _competencies_profile() -> dict:
    path = _REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "section_retrieval_profile.yaml"
    profile = yaml.safe_load(path.read_text(encoding="utf-8"))
    for sec in profile.get("sections", []):
        if isinstance(sec, dict) and sec.get("section_id") == "competencies":
            return sec
    raise AssertionError("competencies section not found in section_retrieval_profile.yaml")


def test_competencies_graph_expansion_enabled_only_in_bundle_only_mode():
    sec = _competencies_profile()
    assert sec.get("graph_expansion_allowed") is True
    assert sec.get("competency_bundle_consumption") == "required"
    assert sec.get("graph_expansion_mode") == "competency_bundle_only"


def test_fec_bridge_pa_metadata_preserves_competency_bundle_consumption():
    from apps_rg.runtime.proof_pool_resolver import SectionProofPool
    from apps_rg.runtime.spine.c0_fec_compose import _build_pa_proof_authority_metadata

    pp_meta = _competencies_proof_meta(
        {
            "augmented_skills_graph_present": True,
            "c03_graphrag_bound": {"support_status": "SUPPORTED"},
        }
    )
    pool = SectionProofPool(
        section="competencies",
        proof_source="augmented_skills_graph",
        proof_pool_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        proof_pool_digest="digest-test",
        selected_fact_plan={"facts": [{"fact_id": "bul_test_001", "claim_text": "x"}]},
        allowed_fact_ids_ordered=["bul_test_001"],
        allowed_fact_ids={"bul_test_001"},
        bullet_rows=[],
        proof_pool_metadata=pp_meta,
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
    pa_meta = _build_pa_proof_authority_metadata(
        pp_meta,
        pool=pool,
        route_contract_ref="route:test",
    )
    assert pa_meta.get("competency_capability_bundle_consumption") is True
    assert pa_meta.get("competency_capability_bundles")
    assert pa_meta.get("competency_bundle_ids")
