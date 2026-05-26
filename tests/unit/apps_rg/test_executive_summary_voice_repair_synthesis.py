"""Synthesis-quality voice repair (Claude-fail antipatterns)."""

from __future__ import annotations

import re

from apps_rg.runtime.sections.executive_summary_voice_repair import (
    repair_generic_filler_prose,
    strip_unsupported_source_sensitive_prose,
)

_BAD_S5_S6 = (
    "Technology strategy executive who aligns enterprise IT direction, governed AI platform delivery, "
    "and innovation programs for regulated enterprise scale. "
    "Building on that platform foundation, platform commercialization generated $22M in IP-led revenue. "
    "Through that operating model, Basel III frameworks cut regulatory reporting errors by 40%. "
    "That regulatory lineage work extended to re-architecting monolithic risk analytics with containerized HPC microservices. "
    "Built advanced quantitative foundation through derivatives pricing, multi-Greek hedging, capital modeling, and FSA credential rigor. "
    "Governed platform delivery, engineering scale, and regulatory-grade controls extend that arc toward enterprise architecture modernization."
)


_FACTS = [
    {
        "fact_id": "fact_quant_hpc_001",
        "claim_text": "Re-architected monolithic risk analytics, trimming stress-testing cycles by 40%.",
    },
    {
        "fact_id": "fact_quant_hpc_003",
        "claim_text": "FSA credential and capital modeling foundation.",
    },
    {
        "fact_id": "fact_governance_003",
        "claim_text": "Basel III / CCAR lineage cut regulatory reporting errors by 40%.",
    },
]


def test_repair_synthesis_quality_rewrites_s5_s6_and_s4_bridge() -> None:
    out, receipt = repair_generic_filler_prose(_BAD_S5_S6, selected_facts=_FACTS)
    assert receipt.get("repaired") is True
    assert "enterprise technology leader who unifies" in out.lower()
    assert "derivatives pricing" not in out.lower()
    assert "extend that arc toward" not in out.lower()
    assert "that regulatory lineage work extended to" not in out.lower()
    assert "governance discipline" not in out.lower()
    assert "rather than listing credential" not in out.lower()
    assert "re-architecting monolithic" not in out.lower() or "re-architected monolithic" in out.lower()
    assert "capital-markets rigor informs which platform investments" not in out.lower()
    assert "innovation incubation" in out.lower()
    assert re.search(r"\b40%|\$[\d,]+", out)


def test_strip_unsupported_audit_ready_when_facts_lack_audit() -> None:
    parsed = {
        "resume_display_text": (
            "Technology leader who scales innovation without sacrificing audit-ready delivery. "
            "Basel III lineage accelerates audit-ready velocity."
        ),
        "claim_ledger": [],
    }
    facts = [
        {
            "fact_id": "fact_governance_003",
            "claim_text": "Implemented Basel III / CCAR data lineage and automated validation frameworks.",
        }
    ]
    out, receipt = strip_unsupported_source_sensitive_prose(parsed, selected_facts=facts)
    text = str(out["resume_display_text"]).lower()
    assert receipt.get("repaired") is True
    assert "audit" not in text
    assert "lineage-ready" in text
