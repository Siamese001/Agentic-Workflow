from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
from apps_rg.runtime.sections.competency_capability_evidence import (
    build_competency_capability_section_packet,
    format_competency_capability_evidence_pack,
)
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)
from apps_rg.runtime.sections.headline_positioning_evidence import (
    build_headline_positioning_section_packet,
    format_headline_positioning_evidence_pack,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _build_plan(section_id: str, *, target_role: str, jd_text: str) -> dict:
    plan, ordered, allowed = build_selected_graph_evidence_plan_for_section(
        repo_root=REPO_ROOT,
        section_id=section_id,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text="",
    )
    assert ordered
    assert allowed
    return plan


def test_agentic_shared_lane_selection_caps_raw_insurtech_density() -> None:
    plan = _build_plan(
        "competencies",
        target_role="SVP Agentic Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform control plane",
    )

    diag = plan["skew_diagnostics"]
    assert plan["target_role_profile"] == "svp_agentic_engineering"
    assert diag["raw_skill_counts_by_employer"]["insurtech"] > diag["raw_skill_counts_by_employer"]["unify"]
    assert diag["max_raw_skill_count_employer"] == "insurtech"
    assert diag["max_selected_skill_count_employer"] == "unify"
    assert diag["selected_skill_counts_by_employer"]["unify"] > diag["selected_skill_counts_by_employer"]["insurtech"]
    assert set(plan["selected_employer_roots"]) == {"unify", "ibm", "insurtech", "ey"}

    selected_skill_ids = set(plan["selected_skill_ids"])
    allowed_graph_ids = set(plan["allowed_graph_evidence_ids"])
    assert selected_skill_ids.issubset(allowed_graph_ids)
    for fact in plan["facts"]:
        bundle_id = fact["role_episode_bundle_id"]
        assert len(fact["graph_skill_node_ids"]) <= plan["skill_caps_by_root"][bundle_id]
        assert len(fact["metric_outcome_ids"]) <= plan["metric_caps_by_root"][bundle_id]


def test_insurance_shared_lane_selection_reweights_to_insurance_roots() -> None:
    plan = _build_plan(
        "competencies",
        target_role="SVP IT Strategy & Innovation",
        jd_text=(
            "Brown & Brown insurance brokerage policy administration Guidewire claims "
            "underwriting cloud enterprise architecture"
        ),
    )

    diag = plan["skew_diagnostics"]
    assert plan["target_role_profile"] == "insurance_it_strategy"
    assert diag["selected_skill_counts_by_employer"]["insurtech"] > diag["selected_skill_counts_by_employer"]["unify"]
    assert diag["selected_metric_counts_by_employer"]["insurtech"] > diag["selected_metric_counts_by_employer"]["unify"]
    assert plan["selected_employer_roots"]["insurtech"]
    assert "insurance_domain_modernization" in plan["selected_competency_families"]


def test_selected_graph_plan_filters_headline_and_competency_prompt_bundles() -> None:
    jd_text = (
        "Brown & Brown insurance brokerage policy administration Guidewire claims "
        "underwriting cloud enterprise architecture"
    )
    competency_plan = _build_plan(
        "competencies",
        target_role="SVP IT Strategy & Innovation",
        jd_text=jd_text,
    )
    competency_payload = {
        "jd_text": jd_text,
        "proof_pool_metadata": {"selected_graph_evidence_plan": competency_plan},
    }
    format_competency_capability_evidence_pack(competency_payload)
    all_competency_ids = set(build_competency_capability_section_packet()["competency_bundle_ids"])
    filtered_competency_ids = set(competency_payload["competency_bundle_ids"])
    assert filtered_competency_ids == all_competency_ids
    assert competency_payload["competency_capability_section_packet"]["selected_graph_evidence_plan_applied"] is True
    assert "ccb_insurance_domain_erm" in filtered_competency_ids
    assert "ccb_agentic_platforms" in filtered_competency_ids
    assert "ccb_partnerships_ecosystem_execution" in filtered_competency_ids

    headline_plan = _build_plan(
        "headline",
        target_role="SVP IT Strategy & Innovation",
        jd_text=jd_text,
    )
    headline_payload = {
        "jd_text": jd_text,
        "proof_pool_metadata": {"selected_graph_evidence_plan": headline_plan},
    }
    format_headline_positioning_evidence_pack(headline_payload)
    all_headline_ids = set(build_headline_positioning_section_packet()["headline_positioning_bundle_ids"])
    filtered_headline_ids = set(headline_payload["headline_positioning_bundle_ids"])
    assert filtered_headline_ids < all_headline_ids
    assert "hpb_regulated_ai_systems" in filtered_headline_ids
    assert "hpb_agentic_ai_platforms" not in filtered_headline_ids


def test_headline_resolver_exposes_selected_graph_plan_before_bundle_attach() -> None:
    pool = resolve_section_proof_pool(
        section="headline",
        repo_root=REPO_ROOT,
        target_role="SVP Agentic Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform control plane",
        product_visible=False,
    )

    meta = pool.proof_pool_metadata
    plan = meta.get("selected_graph_evidence_plan")
    assert isinstance(plan, dict)
    assert plan["section_id"] == "headline"
    assert meta["selected_role_fact_set_used"] is False
    assert meta["graph_evidence_plan_used"] is True
    assert "hpb_agentic_ai_platforms" in meta["headline_positioning_bundle_ids"]
    assert "hpb_distributed_ai_infrastructure" not in meta["headline_positioning_bundle_ids"]
