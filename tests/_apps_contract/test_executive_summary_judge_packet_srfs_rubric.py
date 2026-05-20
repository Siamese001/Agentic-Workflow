"""Regression: executive_summary X1D judge packet rubric follows SRFS activation."""

from __future__ import annotations

from apps_rg.runtime.judges.executive_summary_judge_packet import (
    GRAPH_ONLY_GRADE_ONLY_RUBRIC,
    GRAPH_ONLY_JUDGE_RUBRIC_REF,
    JUDGE_RUBRIC_REF,
    SRFS_GRADE_ONLY_RUBRIC,
    build_executive_summary_judge_packet,
)


def test_judge_packet_uses_srfs_rubric_when_srfs_integration_active() -> None:
    packet = build_executive_summary_judge_packet(
        resume_display_text="Engineering executive building governed platforms.",
        claim_ledger=[
            {
                "claim_text": "Engineering executive building governed platforms.",
                "source_fact_ids": ["fact_engineering_platform_001"],
            }
        ],
        allowed_fact_packet=[
            {
                "fact_id": "fact_engineering_platform_001",
                "claim_text": "Designed governed agentic AI platform capabilities.",
            }
        ],
        allowed_fact_ids={"fact_engineering_platform_001"},
        target_title="SVP Engineering",
        target_company="Acme",
        jd_text="JD targeting only.",
        briefing_text="Briefing context only.",
        parsed_output={"resume_display_text": "Engineering executive building governed platforms."},
        srfs_integration={
            "artifact_path_resolved": "artifacts/apps_rg/fact_inventory/selected_role_fact_set_active.json",
            "executive_summary_selected_fact_ids": ["fact_engineering_platform_001"],
        },
    )
    assert packet["rubric_ref"] == JUDGE_RUBRIC_REF
    assert packet["rubric"] == SRFS_GRADE_ONLY_RUBRIC
    assert "five-sentence" in packet["rubric"].lower()


def test_judge_packet_uses_graph_only_rubric_without_srfs() -> None:
    packet = build_executive_summary_judge_packet(
        resume_display_text="Led platform delivery.",
        claim_ledger=[
            {"claim_text": "Led platform delivery.", "source_fact_ids": ["fact_fixture_001"]}
        ],
        allowed_fact_packet=[
            {"fact_id": "fact_fixture_001", "claim_text": "Led platform delivery."}
        ],
        allowed_fact_ids={"fact_fixture_001"},
        target_title="SVP Engineering",
        target_company="Acme",
        jd_text="JD targeting only.",
        briefing_text="Briefing context only.",
        parsed_output={"resume_display_text": "Led platform delivery."},
        srfs_integration=None,
    )
    assert packet["rubric_ref"] == GRAPH_ONLY_JUDGE_RUBRIC_REF
    assert packet["rubric"] == GRAPH_ONLY_GRADE_ONLY_RUBRIC
    assert "2–3 dense executive sentences" in packet["rubric"]
