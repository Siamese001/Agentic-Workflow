"""Graph-only repair must not regress X2 mechanism/utilization gates."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
    apply_graph_only_generation_quality_repair,
)
from apps_rg.runtime.sections.executive_summary_composition import is_mechanism_inventory_sentence
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_evidence_utilization,
    check_exec_summary_no_mechanism_inventory,
)


def _seven_fact_pool() -> list[dict]:
    return [
        {
            "fact_id": "fact_exec_002",
            "claim_text": "Scaled ML engineering organization from 8 to 28 specialists.",
            "metric_raw": "team 8 to 28",
        },
        {
            "fact_id": "fact_engineering_platform_006",
            "claim_text": (
                "Productized agentic AI primitives into reusable platform services, "
                "generating $22M in IP-led revenue and expanding gross margins by 20%."
            ),
            "metric_raw": "$22M IP-led revenue|20% gross margin expansion",
        },
        {
            "fact_id": "fact_certs_001",
            "claim_text": "Holds AWS Certified Machine Learning Engineer and FSA credentials.",
            "metric_raw": "",
        },
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": (
                "Designed governed agentic AI platform capabilities for regulated workflows, "
                "including deterministic routing and orchestration."
            ),
            "metric_raw": "",
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": "Implemented Basel III / CCAR data lineage that cut reporting errors by 40%.",
            "metric_raw": "40% reporting error reduction",
        },
        {
            "fact_id": "fact_quant_hpc_001",
            "claim_text": "Re-architected risk analytics with HPC, trimming stress-testing cycles by 40%.",
            "metric_raw": "40% faster calculations / stress testing",
        },
        {
            "fact_id": "fact_quant_hpc_003",
            "claim_text": (
                "Built quantitative foundation through derivatives pricing and capital modeling."
            ),
            "metric_raw": "",
        },
    ]


def _allowed_for_seven() -> set[str]:
    return {str(row["fact_id"]) for row in _seven_fact_pool()}


def test_repair_would_regress_x2_when_mechanism_inventory_introduced() -> None:
    from apps_rg.runtime.sections.exec_summary_graph_only_quality import _repair_would_regress_x2

    facts = _seven_fact_pool()
    before_resume = (
        "Technology strategy executive delivering governed AI platforms for regulated environments. "
        "Implemented Basel III frameworks that cut regulatory reporting errors by 40%. "
        "Re-architected risk analytics to enable real-time stress testing. "
        "Led productization generating $22M in IP-led revenue."
    )
    before_parsed = {
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "b", "source_fact_ids": ["fact_governance_003"]},
            {"claim_text": "c", "source_fact_ids": ["fact_quant_hpc_001"]},
            {"claim_text": "d", "source_fact_ids": ["fact_engineering_platform_006"]},
            {"claim_text": "e", "source_fact_ids": ["fact_quant_hpc_003"]},
        ]
    }
    after_resume = (
        "Technology strategy executive with deterministic routing, multi-agent orchestration, "
        "and GraphRAG retrieval for regulated enterprise workflows."
    )
    after_parsed = {"claim_ledger": before_parsed["claim_ledger"][:1]}
    regress, reason = _repair_would_regress_x2(
        before_resume,
        before_parsed,
        after_resume,
        after_parsed,
        plan_facts=facts,
    )
    assert regress is True
    assert reason is not None and "mechanism_inventory" in reason


def test_repair_applied_output_passes_mechanism_inventory() -> None:
    from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
        build_graph_only_executive_summary_from_facts,
    )

    facts = _seven_fact_pool()
    allowed = _allowed_for_seven()
    resume, ledger = build_graph_only_executive_summary_from_facts(facts, allowed)
    inv, reason = is_mechanism_inventory_sentence(resume.split(". ")[0] + ".")
    assert inv is False, reason
    parsed = {"resume_display_text": resume, "claim_ledger": ledger}
    util_ok, util_reason = check_exec_summary_evidence_utilization(
        resume, parsed, selected_facts=facts
    )
    assert util_ok, util_reason
    assert len(ledger) >= 5
