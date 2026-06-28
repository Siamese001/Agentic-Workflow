"""W1: voice_repair must not inject judge-failing S5/S6 (regen unblock)."""

from __future__ import annotations

import re

from apps_rg.runtime.sections.executive_summary_voice_repair import (
    _JUDGE_FAIL_S5_SUBSTRING,
    _S5_CREDENTIAL_DUMP_RE,
    apply_voice_repair_to_parsed,
    build_metric_grounded_s5,
    repair_generic_filler_prose,
)

_JUDGE_FAIL_S5 = _JUDGE_FAIL_S5_SUBSTRING

_FACTS_WITH_METRICS = [
    {
        "fact_id": "fact_quant_hpc_001",
        "claim_text": "Re-architected monolithic risk analytics with containerized HPC microservices, trimming stress-testing cycles by 40%.",
    },
    {
        "fact_id": "fact_quant_hpc_003",
        "claim_text": "Built advanced quantitative foundation with FSA credential and capital modeling.",
    },
    {
        "fact_id": "fact_governance_003",
        "claim_text": "Basel III and CCAR data lineage cut regulatory reporting errors by 40%.",
    },
]

_RETIRED_PROVIDER_LIKE_SIX = (
    "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, and "
    "commercialization into one IT strategy and innovation agenda for decentralized regulated enterprises. "
    "Designed and operationalized a governed agentic AI platform with deterministic routing and multi-agent orchestration, ensuring validation-ready delivery. "
    "Platform commercialization generated $22M in IP-led revenue and expanded gross margins by 20%, while scaling the ML engineering organization from 8 to 28 specialists. "
    "Implemented Basel III and CCAR lineage frameworks that reduced regulatory reporting errors by 40%, accelerating IT strategy velocity. "
    "Quantitative rigor from risk analytics practice improved stress-testing cycles by 40%, enhancing platform investment decisions. "
    "Innovation incubation and architecture standards will extend governed platform capabilities across decentralized units while preserving lineage discipline."
)

_CREDENTIAL_DUMP_S5 = (
    "Built advanced quantitative foundation through derivatives pricing, multi-Greek hedging, "
    "capital modeling, and FSA credential across Towers Perrin and ING."
)


def test_retired_provider_like_s5_metric_preserved_after_voice_repair() -> None:
    parsed = {
        "resume_display_text": _RETIRED_PROVIDER_LIKE_SIX,
        "claim_ledger": [{"claim_text": "stub", "source_fact_ids": ["fact_quant_hpc_001"]}],
    }
    out, receipt = apply_voice_repair_to_parsed(parsed, selected_facts=_FACTS_WITH_METRICS)
    text = str(out.get("resume_display_text") or "")
    assert _JUDGE_FAIL_S5.lower() not in text.lower()
    assert "40%" in text
    assert "stress-testing" in text.lower() or "stress testing" in text.lower()


def test_s5_credential_dump_pattern_requires_inventory_stack() -> None:
    assert not _S5_CREDENTIAL_DUMP_RE.search(
        "Quantitative rigor from risk analytics practice improved stress-testing cycles by 40%, "
        "enhancing platform investment decisions."
    )
    assert _S5_CREDENTIAL_DUMP_RE.search(_CREDENTIAL_DUMP_S5)


def test_single_fsa_metric_sentence_not_classified_as_dump() -> None:
    s5 = (
        "Leveraging FSA credentials and capital modeling, quantitative discipline improved "
        "platform investment decisions by 40% in regulated programs."
    )
    assert not _S5_CREDENTIAL_DUMP_RE.search(s5)
    repaired, receipt = repair_generic_filler_prose(
        " ".join(
            [
                "Enterprise technology leader who unifies governed AI platforms into one IT strategy.",
                "From that platform footprint, commercialization generated $22M in IP-led revenue.",
                "Against that lineage backdrop, Basel III frameworks cut errors by 40%.",
                "Complementing that regulatory foundation, re-architected risk analytics with HPC microservices.",
                s5,
                "Innovation incubation can federate governed capabilities across units.",
            ]
        ),
        selected_facts=_FACTS_WITH_METRICS,
    )
    assert _JUDGE_FAIL_S5.lower() not in repaired.lower()
    assert "40%" in repaired


def test_credential_dump_s5_replaced_with_metric_grounded_not_judge_fail() -> None:
    six = (
        "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, and "
        "commercialization into one IT strategy and innovation agenda for decentralized regulated enterprises. "
        "From that platform footprint, platform commercialization generated $22M in IP-led revenue and expanded gross margins by 20%. "
        "Against that lineage backdrop, Basel III and CCAR data lineage frameworks cut regulatory reporting errors by 40%. "
        "Complementing that regulatory foundation, re-architected monolithic risk analytics with containerized HPC microservices, trimming stress-testing cycles by 40%. "
        f"{_CREDENTIAL_DUMP_S5} "
        "Governed platform delivery, engineering scale, and regulatory-grade controls extend that arc toward enterprise architecture modernization."
    )
    repaired, receipt = repair_generic_filler_prose(six, selected_facts=_FACTS_WITH_METRICS)
    assert receipt.get("repaired") is True
    assert _JUDGE_FAIL_S5.lower() not in repaired.lower()
    assert "derivatives pricing" not in repaired.lower()
    assert re.search(r"\b40%|\$22M", repaired)


def test_build_metric_grounded_s5_never_emits_judge_fail_substring() -> None:
    s5 = build_metric_grounded_s5(_FACTS_WITH_METRICS)
    assert _JUDGE_FAIL_S5.lower() not in s5.lower()
    assert "40%" in s5 or "FSA" in s5
