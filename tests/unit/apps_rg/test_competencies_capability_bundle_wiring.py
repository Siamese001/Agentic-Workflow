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
    build_competency_capability_section_packet,
    format_competency_capability_evidence_pack,
    is_flat_taxonomy_only_packet,
    stamp_competency_bundle_bindings,
)
from apps_rg.runtime.validators import competencies_quality_x2 as q

_REPO_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _good_category(cat_id: str, label: str, terms: list[str]) -> dict:
    return {
        "category_id": cat_id,
        "category_label": label,
        "competency_bundle_id": f"ccb_{cat_id}",
        "graph_skill_node_ids": ["skill_governed_agentic_systems_architecture"],
        "source_fact_ids": ["fact_engineering_platform_001"],
        "terms": [
            {
                "term": t,
                "text": t,
                "source_fact_ids": ["fact_engineering_platform_001"],
                "graph_skill_node_ids": ["skill_governed_agentic_systems_architecture"],
                "support_class": "FACT_AND_SKILL_GRAPH",
            }
            for t in terms
        ],
    }


def _good_competencies() -> list[dict]:
    return [
        _good_category(
            "agentic", "AI Platform Leadership",
            ["governed agentic systems architecture", "multi-agent orchestration fabric", "agentic control plane"],
        ),
        _good_category(
            "governance", "Governance, Risk & Compliance",
            ["runtime gate mesh design", "fail-closed gate semantics", "policy-bound runtime controls"],
        ),
        _good_category(
            "retrieval", "Retrieval Engineering",
            ["dense-sparse-exact retrieval design", "graph-aware grounding", "context engineering"],
        ),
        _good_category(
            "llmops", "Reliability & Evaluation",
            ["audit-grade observability", "evaluation gauntlet design", "multi-judge calibration"],
        ),
        _good_category(
            "distributed", "Distributed Systems",
            ["cloud-native microservices", "streaming analytics pipelines", "lakehouse data platform"],
        ),
        _good_category(
            "productization", "Platform Productization",
            ["platform commercialization", "reusable platform architecture", "demoable accelerators"],
        ),
        _good_category(
            "leadership", "Engineering Leadership",
            ["engineering organization scale-out", "platform operating model", "board-level alignment"],
        ),
    ]


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
    payload: dict = {}
    pack = format_competency_capability_evidence_pack(payload, section_id="competencies")
    assert COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER in pack
    assert "proof_authority = graph_competency_bundles_plus_linked_source_facts" in pack
    assert "base_resume_usage = calibration_only" in pack
    assert "archive_usage = provenance_inventory_only" in pack
    assert "jd_usage = targeting_only" in pack
    assert "competency_bundle_id" in pack
    assert payload.get("competency_bundle_ids")


def test_proof_pool_attach_sets_consumption_flags():
    meta = attach_competency_bundles_to_proof_pool_metadata({}, section_id="competencies")
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


# ---------------------------------------------------------------------------
# X2 gates — pass on good output
# ---------------------------------------------------------------------------


def test_good_competencies_pass_bundle_gates():
    comps = _good_competencies()
    assert q.check_competency_bundle_id_per_category(comps).passed
    assert q.check_graph_skill_node_ids_per_category(comps).passed
    assert q.check_source_fact_ids_or_graph_lineage_per_category(comps).passed
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
    # upgraded with bundle binding → passes
    comps[0]["competency_bundle_id"] = "ccb_partnerships_ecosystem_execution"
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
    meta = attach_competency_bundles_to_proof_pool_metadata(
        {"proof_pool_type": "augmented_skills_graph", "graph_skills_proof_pool": True},
        section_id="competencies",
    )
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
