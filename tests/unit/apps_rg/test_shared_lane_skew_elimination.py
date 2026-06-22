from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
from apps_rg.runtime.sections.competencies_pa import build_competencies_assembly_input
from apps_rg.runtime.sections.competency_capability_evidence import (
    attach_competency_bundles_to_proof_pool_metadata,
    build_competency_capability_section_packet,
    format_competency_capability_evidence_pack,
)
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)
from apps_rg.runtime.sections.headline_positioning_evidence import (
    attach_headline_positioning_bundles_to_proof_pool_metadata,
    build_headline_positioning_section_packet,
    format_headline_positioning_evidence_pack,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
ANTHROPIC_JD = REPO_ROOT / "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt"
ANTHROPIC_BRIEF = REPO_ROOT / "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_briefing.md"
GRAPH_BACKED_SECTIONS = (
    "executive_summary",
    "headline",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "insurtech_bullets",
    "insurtech_narrative",
    "ey_bullets",
    "ey_narrative",
)


def _build_plan(section_id: str, *, target_role: str, jd_text: str, briefing_text: str = "") -> dict:
    plan, ordered, allowed = build_selected_graph_evidence_plan_for_section(
        repo_root=REPO_ROOT,
        section_id=section_id,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
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


def test_competencies_shared_lane_depth_floor_eliminates_thin_ey_node_for_anthropic_jd() -> None:
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    plan = _build_plan(
        "competencies",
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
    )

    pre = plan["graph_evidence_depth_pre_report"]
    post = plan["graph_evidence_depth_report"]
    comparison = plan["graph_evidence_depth_comparison_report"]
    ey_fact = next(fact for fact in plan["facts"] if fact["fact_id"] == "reb_ey_insurance_core_modernization")

    assert plan["target_role_profile"] == "ai_partnerships_gtm"
    assert pre["status"] == "insufficient_depth"
    assert pre["thin_item_ids"] == ["reb_ey_insurance_core_modernization"]
    assert post["status"] == "judge_grade"
    assert post["thin_item_ids"] == []
    assert post["item_rich_ratio"] == 1.0
    assert post["unique_detail_count"] > pre["unique_detail_count"]
    assert len(ey_fact["metric_outcome_ids"]) >= 2
    assert comparison["status_transition"] == "insufficient_depth->judge_grade"
    assert comparison["delta"]["thin_item_count"] == -1
    assert comparison["delta"]["semantic_coverage_pp"] > 0.0


def test_competencies_proof_pool_exposes_pre_and_post_depth_reports() -> None:
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=REPO_ROOT,
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
        product_visible=False,
    )

    meta = pool.proof_pool_metadata
    assert meta["graph_evidence_depth_pre_report"]["status"] == "insufficient_depth"
    assert meta["graph_evidence_depth_report"]["status"] == "judge_grade"
    assert meta["graph_evidence_depth_post_report"]["status"] == "judge_grade"
    assert meta["graph_evidence_depth_comparison_report"]["delta"]["thin_item_count"] == -1


def test_competencies_proof_pool_binds_to_single_canonical_graph_plan() -> None:
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=REPO_ROOT,
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
        product_visible=False,
    )

    meta = pool.proof_pool_metadata
    plan = meta["selected_graph_evidence_plan"]
    receipt = meta["graph_selection_binding_receipt"]

    assert pool.selected_fact_plan["plan_digest"] == plan["plan_digest"]
    assert pool.proof_pool_digest == plan["plan_digest"]
    assert meta["canonical_section_graph_plan_digest"] == plan["plan_digest"]
    assert receipt["schema_version"] == "graph_selection_binding_receipt_v1"
    assert receipt["selected_graph_plan_is_selected_fact_plan"] is True
    assert receipt["proof_pool_digest"] == plan["plan_digest"]
    assert receipt["pass"] is True


def test_selected_graph_plan_emits_candidate_conservation_receipts() -> None:
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    plan = _build_plan(
        "competencies",
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
    )

    traversal = plan["graph_traversal_receipt"]
    candidate_receipt = plan["graph_candidate_receipt"]
    decision_ledger = plan["graph_candidate_decision_ledger"]

    assert plan["plan_id"].startswith("competencies:")
    assert len(plan["plan_digest"]) == 64
    assert traversal["schema_version"] == "graph_traversal_receipt_v1"
    assert traversal["candidate_conservation"]["pass"] is True
    assert traversal["candidate_conservation"]["role_episode_roots_rejected"] > 0
    assert traversal["frontier_size_by_hop_depth"]["0_role_episode_roots"] > len(plan["selected_nodes"])
    assert candidate_receipt["schema_version"] == "graph_candidate_receipt_v1"
    assert candidate_receipt["candidate_conservation_pass"] is True
    assert candidate_receipt["rejected_candidate_count"] > 0
    assert all(row["plan_digest"] == plan["plan_digest"] for row in decision_ledger)


@pytest.mark.parametrize("section_id", GRAPH_BACKED_SECTIONS)
def test_graph_backed_sections_emit_selection_receipt_parity(section_id: str) -> None:
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")

    plan = _build_plan(
        section_id,
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
    )

    candidate_receipt = plan.get("graph_candidate_receipt")
    traversal_receipt = plan.get("graph_traversal_receipt")
    decision_ledger = plan.get("graph_candidate_decision_ledger")

    assert plan["plan_id"].startswith(f"{section_id}:")
    assert len(plan["plan_digest"]) == 64
    assert isinstance(decision_ledger, list)
    assert decision_ledger
    assert candidate_receipt["schema_version"] == "graph_candidate_receipt_v1"
    assert candidate_receipt["section_id"] == section_id
    assert candidate_receipt["plan_id"] == plan["plan_id"]
    assert candidate_receipt["plan_digest"] == plan["plan_digest"]
    assert candidate_receipt["candidate_conservation_pass"] is True
    assert traversal_receipt["schema_version"] == "graph_traversal_receipt_v1"
    assert traversal_receipt["section_id"] == section_id
    assert traversal_receipt["plan_id"] == plan["plan_id"]
    assert traversal_receipt["plan_digest"] == plan["plan_digest"]
    assert traversal_receipt["candidate_conservation"]["pass"] is True
    assert all(row["plan_id"] == plan["plan_id"] for row in decision_ledger)
    assert all(row["plan_digest"] == plan["plan_digest"] for row in decision_ledger)


def test_competencies_prompt_assembly_blocks_missing_canonical_graph_plan() -> None:
    with pytest.raises(ValueError, match="canonical selected_graph_evidence_plan missing"):
        build_competencies_assembly_input(
            {
                "target_title": "Manager, Applied AI Architecture Partnerships",
                "target_company": "Anthropic",
                "jd_text": "partnerships co-sell applied AI architecture",
                "briefing_text": "partnership ecosystem and commercial motion",
                "product_visible": False,
                "allowed_fact_ids": ["bul_test"],
                "canonical_final_evidence_contract": {"allowed_fact_ids": ["bul_test"]},
                "selected_fact_plan": {
                    "section_id": "competencies",
                    "selection_method": "test",
                    "required_fact_ids": ["bul_test"],
                },
                "proof_pool_metadata": {"competency_capability_bundle_consumption": {"present": True}},
            },
            "bul_test: governed platform proof",
            request_id="test",
            run_id="test",
            trace_root="test",
        )


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
    competency_meta = attach_competency_bundles_to_proof_pool_metadata(
        {
            "proof_pool_type": "augmented_skills_graph",
            "selected_graph_evidence_plan": competency_plan,
        },
        section_id="competencies",
    )
    competency_payload = {
        "jd_text": jd_text,
        "proof_pool_metadata": competency_meta,
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
    headline_meta = attach_headline_positioning_bundles_to_proof_pool_metadata(
        {
            "proof_pool_type": "augmented_skills_graph",
            "selected_graph_evidence_plan": headline_plan,
        },
        section_id="headline",
    )
    headline_payload = {
        "jd_text": jd_text,
        "proof_pool_metadata": headline_meta,
    }
    format_headline_positioning_evidence_pack(headline_payload)
    all_headline_ids = set(build_headline_positioning_section_packet()["headline_positioning_bundle_ids"])
    filtered_headline_ids = set(headline_payload["headline_positioning_bundle_ids"])
    assert filtered_headline_ids < all_headline_ids
    assert "hpb_regulated_ai_systems" in filtered_headline_ids
    assert "hpb_agentic_ai_platforms" not in filtered_headline_ids


def test_shared_lane_plan_exposes_briefing_signal_packet() -> None:
    jd_text = "SVP engineering platform leadership"
    briefing_text = (
        "## Company Strategy & Operating Pressure\n"
        "- The role must solve operating-model friction and clarify decision rights.\n\n"
        "## Leadership & Stakeholder Map\n"
        "- CEO, CIO, and business leaders need a tighter delivery cadence.\n\n"
        "## AI, Data, Platform, Architecture Signals\n"
        "- Platform modernization and architecture governance are forward-looking priorities.\n\n"
        "## Recent Events & Urgency\n"
        "- Recent integration pressure and roadmap changes create urgency.\n"
    )
    plan = build_selected_graph_evidence_plan_for_section(
        repo_root=REPO_ROOT,
        section_id="executive_summary",
        target_role="SVP IT Strategy & Innovation",
        jd_text=jd_text,
        briefing_text=briefing_text,
    )
    packet = plan[0]["briefing_signal_packet"]
    assert packet["schema"] == "briefing_signal_packet_v1"
    assert packet["theme_counts"]["strategy"] >= 1
    assert packet["theme_counts"]["operating_model"] >= 1
    assert packet["theme_counts"]["leadership"] >= 1
    assert packet["theme_counts"]["forward_looking"] >= 1
    assert packet["dominant_themes"][0] in {"strategy", "operating_model"}


def test_headline_resolver_exposes_selected_graph_plan_before_bundle_attach() -> None:
    pool = resolve_section_proof_pool(
        section="headline",
        repo_root=REPO_ROOT,
        target_role="SVP Agentic Engineering",
        jd_text=(
            "agentic multi-agent GraphRAG runtime platform control plane "
            "enterprise deployment partner enablement technical close ecosystem revenue"
        ),
        briefing_text=ANTHROPIC_BRIEF.read_text(encoding="utf-8"),
        product_visible=False,
    )

    meta = pool.proof_pool_metadata
    plan = meta.get("selected_graph_evidence_plan")
    assert isinstance(plan, dict)
    policy = plan.get("concentration_policy")
    assert isinstance(policy, dict)
    assert plan["section_id"] == "headline"
    assert policy["distribution_kind"] == "employer_lane"
    assert len(policy["rows"]) == 4
    assert meta["selected_role_fact_set_used"] is False
    assert meta["graph_evidence_plan_used"] is True
    assert len(meta["headline_positioning_bundle_ids"]) == 4
    assert all(str(bundle_id).startswith("hpb_") for bundle_id in meta["headline_positioning_bundle_ids"])
