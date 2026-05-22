"""Regression: executive_summary X1D judge packet rubric follows SRFS activation."""

from __future__ import annotations

from apps_rg.runtime.judges.executive_summary_judge_packet import (
    GRAPH_ONLY_GRADE_ONLY_RUBRIC,
    GRAPH_ONLY_JUDGE_RUBRIC_REF,
    JUDGE_RUBRIC_REF,
    SRFS_GRADE_ONLY_RUBRIC,
    build_executive_summary_judge_packet,
)


def test_judge_packet_always_uses_graph_rubric_after_d2() -> None:
    resume = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise delivery. "
        "The platform generated proof-backed revenue outcomes while scaling engineering delivery. "
        "Implementation of Basel III data lineage frameworks reduced regulatory reporting errors. "
        "Re-architected risk analytics with containerized microservices achieved faster calculations."
    )
    packet = build_executive_summary_judge_packet(
        resume_display_text=resume,
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
        parsed_output={"resume_display_text": resume},
    )
    assert packet["rubric_ref"] == GRAPH_ONLY_JUDGE_RUBRIC_REF
    assert packet["rubric"] == GRAPH_ONLY_GRADE_ONLY_RUBRIC
    assert "4–5" in packet["rubric"] or "4-5" in packet["rubric"]
    assert "no_credential_dump" in packet["rubric"] or "credential inventory" in packet["rubric"].lower()
    assert "s1 thesis" not in packet["rubric"].lower() or "retired" in packet["rubric"].lower()
    gates = packet["deterministic_gate_summary"]
    assert gates["x2_exec_summary_no_credential_dump"]["pass"] is True
    assert gates["x2_exec_summary_no_mechanism_inventory"]["pass"] is True


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
    )
    assert packet["rubric_ref"] == GRAPH_ONLY_JUDGE_RUBRIC_REF
    assert packet["rubric"] == GRAPH_ONLY_GRADE_ONLY_RUBRIC
    assert "4–5 dense executive sentences" in packet["rubric"]
