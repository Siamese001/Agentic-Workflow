"""Unit tests for graph-only executive_summary quality repair."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
    apply_graph_only_generation_quality_repair,
    build_graph_only_executive_summary_from_facts,
)
from apps_rg.runtime.sections.executive_summary_composition import is_mechanism_inventory_sentence
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_evidence_utilization,
    check_exec_summary_mechanical_opener_stack,
    check_synthesis_quality,
    split_sentences,
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
                "Productized agentic AI primitives, generating $22M in IP-led revenue "
                "and expanding gross margins by 20%."
            ),
            "metric_raw": "$22M IP-led revenue|20% gross margin expansion",
        },
        {
            "fact_id": "fact_certs_001",
            "claim_text": "Holds AWS Certified Machine Learning Engineer credentials.",
            "metric_raw": "",
        },
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": "Designed governed agentic AI platforms for regulated workflows.",
            "metric_raw": "",
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": "Implemented Basel III / CCAR data lineage that cut reporting errors by 40%.",
            "metric_raw": "40% reporting error reduction",
        },
        {
            "fact_id": "fact_quant_hpc_001",
            "claim_text": "Re-architected risk analytics with HPC, trimming cycles by 40%.",
            "metric_raw": "40% faster calculations / stress testing",
        },
        {
            "fact_id": "fact_quant_hpc_003",
            "claim_text": "Built quantitative foundation through derivatives pricing.",
            "metric_raw": "",
        },
    ]


def test_build_graph_only_passes_mechanism_inventory_on_opener() -> None:
    allowed = {str(row["fact_id"]) for row in _seven_fact_pool()}
    resume, _ledger = build_graph_only_executive_summary_from_facts(_seven_fact_pool(), allowed)
    sents = split_sentences(resume)
    assert len(sents) >= 4
    inv, reason = is_mechanism_inventory_sentence(sents[0])
    assert inv is False, reason


def test_build_graph_only_passes_synthesis_and_mechanical_opener_gates() -> None:
    allowed = {str(row["fact_id"]) for row in _seven_fact_pool()}
    resume, _ledger = build_graph_only_executive_summary_from_facts(_seven_fact_pool(), allowed)
    stack_ok, stack_reason = check_exec_summary_mechanical_opener_stack(resume)
    assert stack_ok, stack_reason
    synth_ok, synth_reason = check_synthesis_quality(resume)
    assert synth_ok, synth_reason


def test_build_graph_only_five_ledger_rows_when_pool_seven() -> None:
    allowed = {str(row["fact_id"]) for row in _seven_fact_pool()}
    _resume, ledger = build_graph_only_executive_summary_from_facts(_seven_fact_pool(), allowed)
    assert len(ledger) >= 5
    util_ok, util_reason = check_exec_summary_evidence_utilization(
        _resume,
        {"claim_ledger": ledger},
        selected_facts=_seven_fact_pool(),
    )
    assert util_ok, util_reason


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
