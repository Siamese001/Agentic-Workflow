"""Unit tests for repair_headline_segment_citations_for_grounding.

Closes Bug:HeadlineSegmentMiscitationByQwen — Qwen sometimes cites a fact_id with zero
shared content nouns for a segment. The repair function should re-bind such segments
to the best-covering facts from selected_fact_plan.facts.
"""

from __future__ import annotations

from apps_rg.runtime.validators.headline_x2 import (
    check_headline_xyz_literal_grounding,
    repair_headline_segment_citations_for_grounding,
)


def _plan(facts: list[tuple[str, str]]) -> dict:
    return {"selected_fact_plan": {"facts": [{"fact_id": fid, "claim_text": text} for fid, text in facts]}}


def test_recitation_fixes_zero_grounded_segment():
    headline_line = "SVP Engineering | Databricks Lakehouse Workflows | Microservices Telemetry | AI Lifecycle Standardization"
    parsed = _plan([
        ("fact_engineering_platform_005",
         "Architected cloud-native microservices across AWS and Databricks Lakehouse, integrating pipelines."),
        ("fact_engineering_platform_004",
         "Standardized AI lifecycle practices across intake, validation, execution, monitoring."),
        ("fact_quant_hpc_002",
         "Engineered an AI-driven automated trading platform using parallel HPC workflows."),
        ("fact_engineering_platform_003",
         "Strengthened retrieval quality, context assembly, evaluation gates, telemetry instrumentation."),
    ])
    claim_ledger = [
        {"claim_text": "Databricks Lakehouse Workflows", "source_fact_ids": ["fact_engineering_platform_005"]},
        {"claim_text": "Microservices Telemetry", "source_fact_ids": ["fact_quant_hpc_002"]},
        {"claim_text": "AI Lifecycle Standardization", "source_fact_ids": ["fact_engineering_platform_004"]},
    ]

    repaired, receipt = repair_headline_segment_citations_for_grounding(
        headline_line=headline_line,
        parsed_output=parsed,
        claim_ledger=claim_ledger,
    )
    assert receipt["any_changed"] is True
    micro_row = next(r for r in repaired if r["claim_text"] == "Microservices Telemetry")
    assert "fact_engineering_platform_005" in micro_row["source_fact_ids"]
    assert "fact_engineering_platform_003" in micro_row["source_fact_ids"]


def test_recitation_passes_x2_grounding_gate_after_repair():
    headline_line = "SVP Engineering | Databricks Lakehouse Workflows | Microservices Telemetry | AI Lifecycle Standardization"
    parsed = _plan([
        ("fact_engineering_platform_005",
         "Architected cloud-native microservices across AWS and Databricks Lakehouse pipelines."),
        ("fact_engineering_platform_004",
         "Standardized AI lifecycle practices across intake validation execution monitoring."),
        ("fact_engineering_platform_003",
         "Strengthened retrieval quality, telemetry instrumentation, evaluation gates."),
    ])
    claim_ledger = [
        {"claim_text": "Databricks Lakehouse Workflows", "source_fact_ids": ["fact_engineering_platform_005"]},
        {"claim_text": "Microservices Telemetry", "source_fact_ids": ["fact_engineering_platform_004"]},
        {"claim_text": "AI Lifecycle Standardization", "source_fact_ids": ["fact_engineering_platform_004"]},
    ]
    repaired, _ = repair_headline_segment_citations_for_grounding(
        headline_line=headline_line,
        parsed_output=parsed,
        claim_ledger=claim_ledger,
    )
    fact_id_to_text = {
        f["fact_id"]: f["claim_text"] for f in parsed["selected_fact_plan"]["facts"]
    }
    ok, _obs, reason = check_headline_xyz_literal_grounding(
        headline_line=headline_line,
        claim_ledger=repaired,
        fact_id_to_text=fact_id_to_text,
    )
    assert ok, reason


def test_recitation_stays_with_selected_required_fact_ids():
    headline_line = "SVP Engineering | Microservices Modernization Architecture | Policy Governed Platforms | Regulated Cloud Delivery"
    parsed = {
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "reb_ibm_aws_modernization_architecture",
                    "claim_text": "Led AWS modernization architecture for regulated financial-services workloads moving from on-prem constraints to cloud-native delivery patterns",
                },
                {
                    "fact_id": "reb_insurtech_aws_migration_execution",
                    "claim_text": "Executed AWS migration execution classified workloads by cloud fit and completed migration waves",
                },
                {
                    "fact_id": "reb_ey_insurance_core_modernization",
                    "claim_text": "Built policy administration and insurance core modernization",
                },
                {
                    "fact_id": "skill_p2_tech_reference_architecture",
                    "claim_text": "reference architecture",
                },
                {
                    "fact_id": "skill_sr_microservices_integration_platform",
                    "claim_text": "microservices integration platform",
                },
                {
                    "fact_id": "skill_insurance_policy_administration",
                    "claim_text": "policy administration",
                },
                {
                    "fact_id": "skill_aws_migration_readiness_assessment",
                    "claim_text": "migration readiness assessment",
                },
                {
                    "fact_id": "reb_unify_distributed_ecosystem_engineering",
                    "claim_text": "Distributed cloud and data execution infrastructure",
                },
            ],
            "required_fact_ids": [
                "reb_ibm_aws_modernization_architecture",
                "reb_insurtech_aws_migration_execution",
                "reb_ey_insurance_core_modernization",
                "skill_p2_tech_reference_architecture",
                "skill_sr_microservices_integration_platform",
                "skill_insurance_policy_administration",
                "skill_aws_migration_readiness_assessment",
            ],
        }
    }
    claim_ledger = [
        {
            "claim_text": "Microservices Modernization Architecture",
            "source_fact_ids": [
                "reb_ibm_aws_modernization_architecture",
                "skill_p2_tech_reference_architecture",
                "skill_sr_microservices_integration_platform",
            ],
        },
        {
            "claim_text": "Policy Governed Platforms",
            "source_fact_ids": [
                "reb_ey_insurance_core_modernization",
                "skill_insurance_policy_administration",
            ],
        },
        {
            "claim_text": "Regulated Cloud Delivery",
            "source_fact_ids": ["reb_unify_distributed_ecosystem_engineering"],
        },
    ]

    repaired, receipt = repair_headline_segment_citations_for_grounding(
        headline_line=headline_line,
        parsed_output=parsed,
        claim_ledger=claim_ledger,
    )
    assert receipt["any_changed"] is True
    regulated_row = next(r for r in repaired if r["claim_text"] == "Regulated Cloud Delivery")
    assert "reb_unify_distributed_ecosystem_engineering" not in regulated_row["source_fact_ids"]
    assert set(regulated_row["source_fact_ids"]) <= set(parsed["selected_fact_plan"]["required_fact_ids"])


def test_recitation_no_op_when_already_grounded():
    headline_line = "SVP Engineering | Databricks Lakehouse Workflows | AI Lifecycle Standardization | Microservices Telemetry"
    parsed = _plan([
        ("fact_a", "Databricks Lakehouse pipelines for analytics."),
        ("fact_b", "Standardized the AI lifecycle across teams."),
        ("fact_c", "Microservices telemetry instrumentation."),
    ])
    claim_ledger = [
        {"claim_text": "Databricks Lakehouse Workflows", "source_fact_ids": ["fact_a"]},
        {"claim_text": "AI Lifecycle Standardization", "source_fact_ids": ["fact_b"]},
        {"claim_text": "Microservices Telemetry", "source_fact_ids": ["fact_c"]},
    ]
    _, receipt = repair_headline_segment_citations_for_grounding(
        headline_line=headline_line,
        parsed_output=parsed,
        claim_ledger=claim_ledger,
    )
    assert receipt["any_changed"] is False


def test_recitation_skips_when_no_xyz_segments():
    headline_line = "Just a single segment"
    repaired, receipt = repair_headline_segment_citations_for_grounding(
        headline_line=headline_line,
        parsed_output={"selected_fact_plan": {"facts": []}},
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["y"]}],
    )
    assert receipt["any_changed"] is False
    assert len(repaired) == 1


def test_recitation_no_op_when_plan_empty():
    headline_line = "SVP Engineering | X One | X Two | X Three"
    _, receipt = repair_headline_segment_citations_for_grounding(
        headline_line=headline_line,
        parsed_output={"selected_fact_plan": {"facts": []}},
        claim_ledger=[
            {"claim_text": "X One", "source_fact_ids": []},
            {"claim_text": "X Two", "source_fact_ids": []},
            {"claim_text": "X Three", "source_fact_ids": []},
        ],
    )
    assert receipt["any_changed"] is False
