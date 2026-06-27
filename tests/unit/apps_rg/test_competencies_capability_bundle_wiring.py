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
    append_competencies_path_diversity_to_messages,
    build_competency_capability_section_packet,
    enrich_competencies_visible_graph_surface,
    format_competency_capability_evidence_pack,
    hydrate_competency_bundle_graph_evidence,
    is_flat_taxonomy_only_packet,
    stamp_competency_bundle_bindings,
)
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)
from apps_rg.runtime.sections.competencies_lane_execution import (
    _format_competencies_graph_sourcing_assessment,
)
from apps_rg.runtime.sections.competencies_rigor import (
    check_competencies_visible_terms_svp_agentic_richness,
)
from apps_rg.runtime.validators import competencies_quality_x2 as q

_REPO_ROOT = Path(__file__).resolve().parents[3]
ANTHROPIC_JD = _REPO_ROOT / "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt"
ANTHROPIC_BRIEF = (
    _REPO_ROOT / "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_briefing.md"
)


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


def _competencies_from_graph_plan(plan: dict) -> list[dict]:
    labels = [
        "Platform Productization",
        "Partnerships Ecosystem Execution",
        "Distributed Systems Engineering",
        "Engineering Leadership",
        "Cloud HPC Modernization",
        "Data Governance Security",
        "Agentic Platforms",
        "Runtime Governance",
    ]
    competencies: list[dict] = []
    for idx, fact in enumerate(plan.get("facts") or []):
        if not isinstance(fact, dict):
            continue
        label = labels[idx % len(labels)]
        source_fact_id = str(fact.get("fact_id") or f"fact_{idx}")
        skill_ids = [str(x) for x in (fact.get("graph_skill_node_ids") or []) if str(x).strip()]
        if not skill_ids:
            skill_ids = [f"skill_fallback_{idx}"]
        terms = [
            {
                "term": f"{label.lower()} proof path",
                "text": f"{label.lower()} proof path",
                "source_fact_id": source_fact_id,
                "source_fact_ids": [source_fact_id],
                "graph_skill_node_ids": skill_ids[:2],
                "source_skill_ids": skill_ids[:2],
                "support_class": "FACT_AND_SKILL_GRAPH",
            },
            {
                "term": f"{label.lower()} operating model",
                "text": f"{label.lower()} operating model",
                "source_fact_id": source_fact_id,
                "source_fact_ids": [source_fact_id],
                "graph_skill_node_ids": skill_ids[:2],
                "source_skill_ids": skill_ids[:2],
                "support_class": "FACT_AND_SKILL_GRAPH",
            },
        ]
        competencies.append(
            {
                "category_id": label.lower().replace(" ", "_"),
                "category_label": label,
                "competency_bundle_id": f"ccb_{label.lower().replace(' ', '_')}",
                "graph_skill_node_ids": skill_ids[:3],
                "source_fact_ids": [source_fact_id],
                "selection_score": round(0.94 - idx * 0.03, 2),
                "terms": terms,
            }
        )
    return competencies


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


def test_competencies_path_diversity_framing_biases_graph_neighborhoods():
    msgs = append_competencies_path_diversity_to_messages(
        [{"role": "user", "content": "base"}],
        path_index=3,
        temperature=0.41,
    )
    text = msgs[-1]["content"]
    assert "COMPETENCIES_PATH_DIVERSITY" in text
    assert "llmops evaluation and reliability" in text
    assert "candidate-neighborhood expansion" in text
    assert "JD and briefing text are targeting context only, never proof" in text


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


def test_source_fact_concentration_limit_fails_anthropic_shape():
    comps = _good_competencies() + [
        _good_category(
            "partner",
            "Cloud & Partner Ecosystems",
            ["hyperscaler alliance co-sell", "partner ecosystem gtm", "joint revenue execution"],
        )
    ]
    for idx, cat in enumerate(comps):
        cat["selection_score"] = round(0.91 - idx * 0.01, 2)
    for cat in comps[:7]:
        cat["source_fact_ids"] = ["fact_engineering_platform_001"]
        for term in cat["terms"]:
            term["source_fact_ids"] = ["fact_engineering_platform_001"]
    comps[7]["source_fact_ids"] = [
        "fact_partnerships_gtm_001",
        "fact_partnerships_gtm_002",
    ]
    for term in comps[7]["terms"]:
        term["source_fact_ids"] = ["fact_partnerships_gtm_001"]

    receipt = q.build_competencies_graph_sufficiency_receipt(comps)
    assert receipt["dominant_source_fact_id"] == "fact_engineering_platform_001"
    assert receipt["dominant_source_fact_category_share"] == pytest.approx(0.875)

    result = q.check_source_fact_concentration_limit(comps)
    assert result.passed is False
    assert "fact_engineering_platform_001" in str(result.observed_value)


def test_bundle_graph_hydration_repairs_anthropic_default_fact_collapse():
    """apps-test-model: APP CONTRACT

    Regression: taxonomy projection assigned one default fact to most Anthropic
    partnership categories after self-consistency paths had distinct graph facts.
    """
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=_REPO_ROOT,
        section_id="competencies",
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
    )
    meta = attach_competency_bundles_to_proof_pool_metadata(
        {
            "proof_pool_type": "augmented_skills_graph",
            "selected_graph_evidence_plan": plan,
        },
        section_id="competencies",
    )
    packet = meta["competency_capability_section_packet"]
    fallback_fact = "metric_ey_core_workflow_maps_count"
    allowed = {
        str(fid)
        for fid in (plan.get("allowed_graph_evidence_ids") or [])
        if str(fid).strip()
    } | {fallback_fact}
    categories: list[dict] = []
    for idx, rec in enumerate(packet["competency_bundles"][:8]):
        label = str(rec.get("display_label_candidate") or f"Category {idx}")
        categories.append(
            {
                "category_id": str((rec.get("target_taxonomy_category_ids") or [f"cat_{idx}"])[0]),
                "category_label": label,
                "competency_bundle_id": rec["competency_bundle_id"],
                "capability_family": rec["capability_family"],
                "graph_skill_node_ids": list(rec.get("graph_skill_node_ids") or [])[:2],
                "source_fact_ids": [fallback_fact],
                "terms": [
                    {
                        "term": f"{label} graph execution",
                        "text": f"{label} graph execution",
                        "source_fact_id": fallback_fact,
                        "source_fact_ids": [fallback_fact],
                        "proof_source": "default_fid_backfill",
                    }
                ],
            }
        )

    hydrate_competency_bundle_graph_evidence(
        categories,
        packet=packet,
        allowed_fact_ids=allowed,
        selected_graph_evidence_plan=plan,
    )
    parsed = {
        "competencies_rejected_neighbor_audit": {
            "schema_version": "competencies_rejected_neighbor_audit_v1",
            "audit_status": "present",
            "candidate_label_count": 12,
            "candidate_variant_count": 48,
            "selected_count": len(categories),
            "rejected_neighbor_count": 40,
        }
    }

    assert all(cat.get("selection_score") is not None for cat in categories)
    assert len({cat["selection_score"] for cat in categories}) > 1
    assert q.check_source_fact_concentration_limit(categories).passed is True
    assert q.check_per_category_confidence_nonconstant(categories).passed is True
    granularity = q.check_competencies_graph_granularity_gates(
        categories,
        meta,
        parsed,
        jd_text=jd_text,
        briefing_text=brief_text,
    )
    assert granularity.passed is True


def test_visible_graph_surface_uses_partnership_first_bundle_labels_and_terms():
    """apps-test-model: APP CONTRACT

    Regression: graph receipts improved while competencies_display.txt still showed
    the old generic taxonomy phrases in static order.
    """
    packet = build_competency_capability_section_packet("competencies")
    by_id = {row["competency_bundle_id"]: row for row in packet["competency_bundles"]}
    bundle_ids = [
        "ccb_partner_applied_ai_architecture",
        "ccb_agentic_platforms",
        "ccb_runtime_governance",
        "ccb_retrieval_context_engineering",
        "ccb_llmops_reliability",
        "ccb_distributed_systems_engineering",
        "ccb_platform_productization",
        "ccb_engineering_leadership",
    ]
    parsed = {"competencies": []}
    for idx, bundle_id in enumerate(bundle_ids):
        rec = by_id[bundle_id]
        parsed["competencies"].append(
            {
                "category_id": str((rec.get("target_taxonomy_category_ids") or [f"cat_{idx}"])[0]),
                "category_label": "Technology Strategy & Innovation" if idx == 0 else "AI Platform Leadership",
                "competency_bundle_id": bundle_id,
                "graph_skill_node_ids": list(rec.get("graph_skill_node_ids") or []),
                "source_fact_ids": ["fact_engineering_platform_001"],
                "terms": [
                    {
                        "term": "Enterprise technology roadmap ownership",
                        "text": "Enterprise technology roadmap ownership",
                        "source_fact_ids": ["fact_engineering_platform_001"],
                    }
                ],
            }
        )

    receipt = enrich_competencies_visible_graph_surface(
        parsed,
        packet=packet,
        allowed_fact_ids={"fact_engineering_platform_001"},
    )

    competencies = parsed["competencies"]
    assert competencies[0]["competency_bundle_id"] == "ccb_partner_applied_ai_architecture"
    assert competencies[0]["resume_display_label"] == "Partner Applied AI Architecture"
    assert "partner-ready applied AI reference architectures" in [
        term["text"] for term in competencies[0]["terms"]
    ]
    assert competencies[1]["resume_display_label"] == "Governed Agentic AI Platform Architecture"
    assert all(cat.get("visible_graph_surface") is True for cat in competencies)
    assert receipt["order_policy"] == "anthropic_partnership_relevance_first"
    assert receipt["enriched_category_count"] == 8
    assert "Enterprise technology roadmap ownership" not in [
        term["text"] for term in competencies[1]["terms"]
    ]
    assert all(
        "20%" not in term["text"]
        for cat in competencies
        for term in cat["terms"]
    )
    assert all(len(cat["terms"]) == 3 for cat in competencies)
    assert all(
        5 <= len(term["text"].split()) <= 7
        for cat in competencies
        for term in cat["terms"]
    )
    richness_ok, richness_reason = check_competencies_visible_terms_svp_agentic_richness(competencies)
    assert richness_ok, richness_reason


def test_partner_applied_ai_architecture_bundle_is_root_bound_for_anthropic():
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=_REPO_ROOT,
        section_id="competencies",
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
    )
    meta = attach_competency_bundles_to_proof_pool_metadata(
        {
            "proof_pool_type": "augmented_skills_graph",
            "selected_graph_evidence_plan": plan,
        },
        section_id="competencies",
    )
    bundle = next(
        b for b in meta["competency_capability_bundles"]
        if b["competency_bundle_id"] == "ccb_partner_applied_ai_architecture"
    )
    assert bundle["allowed_partner_roots"] == [
        "reb_unify_partner_channel_cosell",
        "reb_ibm_aws_alliance_partner_cosell_gtm",
    ]
    assert "employment_exp_insurtech_001" in bundle["forbidden_partner_roots"]
    assert "employment_exp_ey_001" in bundle["forbidden_partner_roots"]

    comps = [
        {
            "category_label": "Partner Applied AI Architecture",
            "competency_bundle_id": "ccb_partner_applied_ai_architecture",
            "capability_family": "partner_applied_ai_architecture",
            "graph_skill_node_ids": list(bundle["graph_skill_node_ids"]),
            "source_fact_ids": ["reb_unify_partner_channel_cosell"],
            "terms": [
                {
                    "text": "partner-ready applied AI reference architectures",
                    "source_fact_ids": ["reb_unify_partner_channel_cosell"],
                    "source_skill_ids": ["skill_partner_joint_solution_development"],
                }
            ],
        }
    ]
    assert q.check_partner_architecture_bundle_present(comps, meta).passed
    assert q.check_partner_architecture_terms_require_bundle(comps, meta).passed
    assert q.check_partner_terms_source_roots(comps, meta).passed


def test_partner_architecture_terms_fail_when_bound_to_insurtech_root():
    meta = {
        "competency_capability_bundle_consumption": True,
        "selected_graph_evidence_plan": {
            "target_role_profile": "ai_partnerships_gtm",
            "facts": [
                {
                    "fact_id": "reb_insurtech_cloud_modernization",
                    "role_episode_bundle_id": "reb_insurtech_cloud_modernization",
                    "employer_lane": "insurtech",
                    "source_fact_ids": ["reb_insurtech_cloud_modernization"],
                    "graph_skill_node_ids": ["skill_cloud_migration"],
                }
            ],
        },
        "competency_capability_bundles": [
            {
                "competency_bundle_id": "ccb_insurance_domain_erm",
                "capability_family": "insurance_domain_modernization",
                "employer_bindings": ["employment_exp_insurtech_001"],
                "role_episode_bindings": ["reb_insurtech_cloud_modernization"],
            }
        ],
    }
    comps = [
        {
            "category_label": "Partner Applied AI Architecture",
            "competency_bundle_id": "ccb_insurance_domain_erm",
            "capability_family": "insurance_domain_modernization",
            "graph_skill_node_ids": ["skill_cloud_migration"],
            "source_fact_ids": ["reb_insurtech_cloud_modernization"],
            "terms": [
                {
                    "text": "partner-ready applied AI reference architectures",
                    "source_fact_ids": ["reb_insurtech_cloud_modernization"],
                    "source_skill_ids": ["skill_cloud_migration"],
                }
            ],
        }
    ]
    assert not q.check_partner_architecture_terms_require_bundle(comps, meta).passed
    assert not q.check_partner_terms_source_roots(comps, meta).passed


def test_per_category_confidence_nonconstant_requires_real_category_scores():
    comps = _good_competencies()[:3]
    assert q.check_per_category_confidence_nonconstant(comps).passed is False

    for cat in comps:
        cat["selection_score"] = 0.9
    assert q.check_per_category_confidence_nonconstant(comps).passed is False

    comps[1]["selection_score"] = 0.86
    comps[2]["selection_score"] = 0.78
    assert q.check_per_category_confidence_nonconstant(comps).passed is True


def test_rejected_neighbor_audit_required_for_bundle_mode_traversal_proof():
    assert q.check_competencies_rejected_neighbor_audit_present({}).passed is False
    parsed = {
        "competencies_rejected_neighbor_audit": {
            "schema_version": "competencies_rejected_neighbor_audit_v1",
            "audit_status": "present",
            "candidate_label_count": 10,
            "candidate_variant_count": 12,
            "selected_count": 8,
            "rejected_neighbor_count": 2,
            "rejected_neighbors": [
                {"category_label": "Alternative Platform Governance"},
                {"category_label": "Alliance Operating Systems"},
            ],
        }
    }
    result = q.check_competencies_rejected_neighbor_audit_present(parsed)
    assert result.passed is True
    assert result.gate_id == "x2_competencies_rejected_neighbor_audit_present"


def test_anthropic_partnership_traversal_receipt_proves_graph_breadth_and_axes():
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=_REPO_ROOT,
        section_id="competencies",
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
    )
    meta = attach_competency_bundles_to_proof_pool_metadata(
        {
            "proof_pool_type": "augmented_skills_graph",
            "selected_graph_evidence_plan": plan,
        },
        section_id="competencies",
    )
    comps = _competencies_from_graph_plan(plan)
    parsed = {
        "competencies_rejected_neighbor_audit": {
            "schema_version": "competencies_rejected_neighbor_audit_v1",
            "audit_status": "present",
            "candidate_label_count": 12,
            "candidate_variant_count": 48,
            "selected_count": len(comps),
            "rejected_neighbor_count": 40,
            "rejected_neighbors": [{"category_label": "Alternative Partnership Operating Model"}],
        }
    }

    receipt = q.build_competencies_graph_sufficiency_receipt(
        comps,
        proof_pool_metadata=meta,
        parsed_output=parsed,
        jd_text=jd_text,
        briefing_text=brief_text,
        x1d_judges=[{"provider_key": "fixture_judge", "score": 0.84}],
    )
    traversal = receipt["traversal_sufficiency_receipt"]

    assert traversal["target_role_profile"] == "ai_partnerships_gtm"
    assert traversal["graph_evidence_depth_status"] == "judge_grade"
    assert traversal["candidate_nodes_visited_count"] > traversal["selected_unique_leaf_skill_count"]
    assert traversal["selected_role_episode_root_ids"]
    assert traversal["selected_leaf_skill_ids"]
    assert traversal["selected_metric_outcome_ids"]
    assert traversal["rejected_sibling_skill_ids"]
    assert traversal["frontier_size_by_hop_depth"]["1_leaf_skill_candidates"] >= 16
    assert traversal["frontier_size_by_hop_depth"]["2_metric_outcome_candidates"] >= 8
    assert traversal["rejected_sibling_skill_count"] > 0
    assert traversal["selected_vs_rejected_candidate_comparison"]["selector_rejected_neighbor_count"] == 40
    assert traversal["role_specific_axis_coverage"]["missing_axes"] == []
    assert receipt["confidence_nonconstant"] is True
    assert len(receipt["unique_category_confidence_values"]) > 1
    first_breakdown = receipt["categories"][0]["confidence_breakdown"]
    assert first_breakdown["judge_score_available"] is True
    assert set(first_breakdown) >= {
        "graph_path_specificity",
        "source_fact_diversity",
        "selector_score",
        "judge_score",
        "jd_brief_alignment",
        "penalties",
    }
    output_lines = _format_competencies_graph_sourcing_assessment(
        receipt,
        x2_gates=[
            {"gate_id": "x2_competencies_graph_traversal_sufficiency", "pass": True},
            {"gate_id": "x2_competencies_graph_granularity_gates", "pass": True},
        ],
        traversal_receipt_ref="artifacts/test/competencies_graph_traversal_sufficiency_receipt.json",
    )
    output_text = "\n".join(output_lines)
    assert "GRAPH_SOURCING_ASSESSMENT:" in output_text
    assert "SCHEMA_ORDER: role -> role_episode_roots -> skills -> metrics" in output_text
    assert "ROLE: profile=ai_partnerships_gtm" in output_text
    assert "ROLE_EPISODE_ROOTS:" in output_text
    assert "SKILLS:" in output_text
    assert "METRICS:" in output_text
    assert "REJECTED_SIBLINGS:" in output_text
    assert "SELECTED_VS_REJECTED:" in output_text
    assert "ROLE_AXIS_COVERAGE:" in output_text
    assert "CONFIDENCE:" in output_text
    assert "ASSESSMENT: ACCEPTABLE" in output_text
    assert "GRAPH_RECEIPT: artifacts/test/competencies_graph_traversal_sufficiency_receipt.json" in output_text


def test_anthropic_partnership_graph_sufficiency_and_granularity_gates_pass():
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=_REPO_ROOT,
        section_id="competencies",
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
    )
    meta = attach_competency_bundles_to_proof_pool_metadata(
        {
            "proof_pool_type": "augmented_skills_graph",
            "selected_graph_evidence_plan": plan,
        },
        section_id="competencies",
    )
    comps = _competencies_from_graph_plan(plan)
    parsed = {
        "competencies_rejected_neighbor_audit": {
            "schema_version": "competencies_rejected_neighbor_audit_v1",
            "audit_status": "present",
            "candidate_label_count": 12,
            "candidate_variant_count": 48,
            "selected_count": len(comps),
            "rejected_neighbor_count": 40,
        }
    }

    traversal_result = q.check_competencies_graph_traversal_sufficiency(
        comps,
        meta,
        parsed,
        jd_text=jd_text,
        briefing_text=brief_text,
    )
    granularity_result = q.check_competencies_graph_granularity_gates(
        comps,
        meta,
        parsed,
        jd_text=jd_text,
        briefing_text=brief_text,
    )

    assert traversal_result.passed is True
    assert traversal_result.observed_value["target_role_profile"] == "ai_partnerships_gtm"
    assert granularity_result.passed is True
    assert granularity_result.observed_value["missing_role_axes"] == []


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
        "x2_default_fid_only_support_forbidden",
        "x2_generic_taxonomy_only_category_forbidden",
        "x2_jd_only_skill_forbidden",
        "x2_required_capability_families_covered",
        "x2_competency_rigor_floor_met",
        "x2_technical_density_floor_met",
        "x2_competencies_source_fact_concentration_limit",
        "x2_competencies_per_category_confidence_nonconstant",
        "x2_competencies_rejected_neighbor_audit_present",
        "x2_competencies_graph_traversal_sufficiency",
        "x2_competencies_graph_granularity_gates",
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
