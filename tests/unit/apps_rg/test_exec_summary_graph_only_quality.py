"""Unit tests for graph-only executive_summary quality repair."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
    apply_graph_only_generation_quality_repair,
    build_graph_only_executive_summary_from_facts,
)


def _sample_facts() -> list[dict]:
    return [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": (
                "Designed and operationalized governed agentic AI platform capabilities "
                "for regulated enterprise workflows, including deterministic routing."
            ),
            "metric_raw": "",
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": (
                "Implemented Basel III / CCAR data lineage frameworks that cut "
                "regulatory reporting errors by 40%."
            ),
            "metric_raw": "40% reporting error reduction",
        },
        {
            "fact_id": "fact_exec_002",
            "claim_text": "Scaled ML engineering organization from 8 to 28 specialists.",
            "metric_raw": "team 8 to 28",
        },
    ]


def test_build_graph_only_summary_omits_gross_margin() -> None:
    allowed = {
        "fact_engineering_platform_001",
        "fact_governance_003",
        "fact_governance_003_metric_e5abeb74",
        "fact_exec_002",
        "fact_exec_002_metric_c880fce9",
    }
    resume, ledger = build_graph_only_executive_summary_from_facts(_sample_facts(), allowed)
    assert "gross margin" not in resume.lower()
    assert "40%" in resume
    assert "8 to 28" in resume or "8 to  28" in resume
    assert not any("Holds AWS" in resume for _ in [0])
    assert len(ledger) <= 3


def test_apply_repair_strips_hallucinated_margin() -> None:
    allowed = {
        "fact_engineering_platform_001",
        "fact_governance_003",
        "fact_governance_003_metric_e5abeb74",
        "fact_exec_002",
        "fact_exec_002_metric_c880fce9",
    }
    parsed = {
        "resume_display_text": (
            "Platform leader. Built systems leading to 40% error reduction and "
            "20% expansion in gross margins. Scaled team improving reliability; "
            "Holds AWS Certified Machine Learning Engineer credentials."
        ),
        "claim_ledger": [
            {
                "claim_text": "Merged claim leading to 40% and 20% gross margins",
                "source_fact_ids": [
                    "fact_engineering_platform_001",
                    "fact_governance_003",
                ],
            }
        ],
    }
    repaired, meta = apply_graph_only_generation_quality_repair(
        parsed,
        allowed_fact_ids=allowed,
        plan_facts=_sample_facts(),
    )
    assert meta["had_unsupported_gross_margin"] is True
    assert "gross margin" not in str(repaired.get("resume_display_text") or "").lower()
    assert "20%" not in str(repaired.get("resume_display_text") or "")
