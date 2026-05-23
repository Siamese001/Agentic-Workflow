"""Graph-only executive summary must produce six sentences and pass X2 shape gates."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
    build_graph_only_executive_summary_from_facts,
)
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MIN_SENTENCES,
    check_exec_summary_paragraph_max_words,
    check_exec_summary_sentence_count_6,
)


def _plan_facts() -> list[dict]:
    return [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": "Designed governed agentic AI platform capabilities for regulated enterprise workflows.",
        },
        {
            "fact_id": "fact_engineering_platform_006",
            "claim_text": "Platform commercialization generated $22M in IP-led revenue.",
            "metric_raw": "$22M",
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": "Basel III and CCAR data lineage frameworks cut regulatory reporting errors by 40%.",
            "metric_raw": "40%",
        },
        {
            "fact_id": "fact_exec_002",
            "claim_text": "Scaled the ML engineering organization from 8 to 28 specialists.",
        },
        {
            "fact_id": "fact_quant_hpc_001",
            "claim_text": "Containerized risk analytics microservices trimmed stress-testing cycles by 40%.",
        },
        {
            "fact_id": "fact_quant_hpc_003",
            "claim_text": "Quantitative depth spans derivatives pricing and regulated risk analytics.",
        },
    ]


def test_graph_only_builds_six_sentences_and_passes_x2() -> None:
    allowed = {f["fact_id"] for f in _plan_facts()}
    resume, ledger = build_graph_only_executive_summary_from_facts(_plan_facts(), allowed)
    assert len(split_sentences(resume)) == EXEC_SUMMARY_MIN_SENTENCES
    assert check_exec_summary_sentence_count_6(resume)[0] is True
    assert check_exec_summary_paragraph_max_words(resume)[0] is True
    assert len(ledger) >= 1
