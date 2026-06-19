"""Unit tests for the shared graph-evidence contract helpers."""

from __future__ import annotations

from apps_rg.runtime.sections.graph_evidence_contract import (
    build_graph_evidence_depth_report,
    build_graph_evidence_runtime_payload,
    build_selected_graph_evidence_plan,
)


def test_build_selected_graph_evidence_plan_preserves_section_metadata() -> None:
    plan = build_selected_graph_evidence_plan(
        section_id="headline",
        selection_method="canonical_headline",
        facts=[{"fact_id": "fact_a"}],
        required_fact_ids=["fact_a"],
        facts_semantics="candidate_fact_pool_full_records",
    )

    assert plan == {
        "section_id": "headline",
        "selection_method": "canonical_headline",
        "facts": [{"fact_id": "fact_a"}],
        "required_fact_ids": ["fact_a"],
        "facts_semantics": "candidate_fact_pool_full_records",
    }


def test_build_graph_evidence_runtime_payload_emits_both_era_keys(tmp_path) -> None:
    repo_root = tmp_path
    base_json_path = repo_root / "base.json"
    payload = build_graph_evidence_runtime_payload(
        run_id_prefix="headline",
        section_id="headline",
        prompt_id="headline_prompt_v1",
        repo_root=repo_root,
        base_json_path=base_json_path,
        base_hash="abc123",
        selected_graph_evidence_plan={"section_id": "headline", "facts": []},
        allowed_graph_evidence_ids=["fact_a", "fact_b"],
        target_title="SVP Engineering",
        target_company="Example Corp",
        jd_text="JD",
        briefing="Briefing",
        writable_context_scope="headline_only",
        extra_fields={"custom_flag": True},
    )

    assert payload["selected_graph_evidence_plan"] == {"section_id": "headline", "facts": []}
    assert payload["selected_fact_plan"] == {"section_id": "headline", "facts": []}
    assert payload["allowed_graph_evidence_ids"] == ["fact_a", "fact_b"]
    assert payload["allowed_fact_ids"] == ["fact_a", "fact_b"]
    assert payload["base_resume_json_ref"] == "base.json"
    assert payload["custom_flag"] is True


def test_depth_report_v2_ranks_weakest_link_by_support_not_position() -> None:
    report = build_graph_evidence_depth_report(
        {
            "facts": [
                {
                    "fact_id": "fact_strong_first",
                    "claim_text": "Strong graph-supported cloud platform delivery",
                    "graph_skill_node_ids": ["skill_cloud_platform"],
                    "metric_outcome_ids": ["metric_cloud_001"],
                },
                {
                    "fact_id": "fact_thin_second",
                    "claim_text": "Thin unsupported ecosystem claim",
                    "graph_skill_node_ids": [],
                    "metric_outcome_ids": [],
                },
            ],
        },
        section_id="competencies",
    )

    assert report["schema"] == "graph_evidence_depth_report_v2"
    assert report["weakest_link"]["item_id"] == "fact_thin_second"
    assert report["weakest_link"]["reason"] == "thin_fact_support"
    assert report["weakest_link"]["confidence"] < report["term_confidence_rows"][0]["confidence"]


def test_repeated_metric_ids_reduce_confidence_and_surface_penalty() -> None:
    report = build_graph_evidence_depth_report(
        {
            "facts": [
                {
                    "fact_id": "fact_a",
                    "claim_text": "Platform commercialization",
                    "graph_skill_node_ids": ["skill_productization"],
                    "metric_outcome_ids": ["metric_reused"],
                },
                {
                    "fact_id": "fact_b",
                    "claim_text": "Operating model scale",
                    "graph_skill_node_ids": ["skill_leadership"],
                    "metric_outcome_ids": ["metric_reused"],
                },
            ],
        },
        section_id="competencies",
    )

    assert report["detail_reuse_ratio"] == 0.5
    assert report["penalties"]["metric_reuse_penalty"] == 0.5
    assert report["weakest_link"]["reason"] == "repeated_metric"
    assert report["category_graph_confidence"] < 1.0


def test_jd_overlap_does_not_increase_proof_authority_score() -> None:
    source = {
        "facts": [
            {
                "fact_id": "fact_cloud",
                "claim_text": "Cloud partner ecosystem GTM",
                "graph_skill_node_ids": ["skill_partner_ecosystem"],
                "metric_outcome_ids": ["metric_partner_001"],
            }
        ],
    }
    no_targeting = build_graph_evidence_depth_report(source, section_id="competencies")
    with_targeting = build_graph_evidence_depth_report(
        {
            **source,
            "jd_text": "Cloud partner ecosystem GTM leadership",
            "briefing": "partner ecosystem",
        },
        section_id="competencies",
    )

    assert with_targeting["targeting_fit_score"] > no_targeting["targeting_fit_score"]
    assert with_targeting["proof_authority_score"] == no_targeting["proof_authority_score"]
