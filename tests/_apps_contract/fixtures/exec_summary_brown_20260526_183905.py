"""Minimal Brown SVP exec-summary shape from RCA run exec_summary_20260526_183905.

Strings copied from artifacts/apps_rg/runtime_proofs/executive_summary/real/
exec_summary_20260526_183905/parsed_output.json (no secrets).
"""

from __future__ import annotations

SOURCE_RUN_ID = "exec_summary_20260526_183905"

BROWN_RESUME_DISPLAY_TEXT = (
    "Enterprise technology leader aligning governed AI platforms, regulatory lineage, "
    "and commercialization into one IT strategy and innovation agenda for decentralized "
    "regulated enterprises. Designs and operates platform runtime with deterministic "
    "controls and traceable execution so innovation scales without sacrificing "
    "validation-ready delivery. From that platform footprint, platform commercialization "
    "and team growth from 8 to 28 specialists convert delivery complexity into enterprise "
    "program adoption. Complementing that delivery foundation, Basel III and CCAR lineage "
    "discipline accelerates lineage-ready IT strategy velocity without turning governance "
    "into a control checklist. Quantitative rigor from capital and risk analytics practice "
    "sharpens platform investment and stress-analytics decisions for regulated program scale. "
    "Looking ahead, architecture standards and innovation incubation programs can turn "
    "governed platform delivery into decentralized unit adoption while preserving lineage "
    "discipline."
)

BROWN_S5_FRAGMENT = (
    "Quantitative rigor from capital and risk analytics practice sharpens platform "
    "investment and stress-analytics decisions for regulated program scale."
)

BROWN_S6_FRAGMENT = "Looking ahead, architecture standards and innovation incubation"

BROWN_CLAIM_LEDGER: list[dict] = [
    {
        "claim": (
            "Enterprise technology leader aligning governed AI platforms, regulatory lineage, "
            "and commercialization into one IT strategy and innovation agenda for decentralized "
            "regulated enterprises."
        ),
        "claim_text": (
            "Holds AWS Certified Machine Learning Engineer - Associate, AWS Certified "
            "Solutions Architect - Professional, Databricks Lakehouse Fundamentals, and "
            "Fellow of the Society of Actuaries credentials."
        ),
        "source_fact_ids": ["fact_certs_001"],
    },
    {
        "claim": (
            "Designs and operates platform runtime with deterministic controls and traceable "
            "execution so innovation scales without sacrificing validation-ready delivery."
        ),
        "claim_text": (
            "Designed and operationalized governed agentic AI platform capabilities for "
            "regulated enterprise workflows, including deterministic routing, multi-agent "
            "orchestration, GraphRAG retrieval, sandboxed execution, policy gating, validation "
            "controls, and replayable execution traces."
        ),
        "source_fact_ids": ["fact_engineering_platform_001"],
    },
    {
        "claim": (
            "From that platform footprint, platform commercialization and team growth from 8 "
            "to 28 specialists convert delivery complexity into enterprise program adoption."
        ),
        "claim_text": (
            "Scaled ML engineering organization from 8 to 28 specialists, including senior "
            "engineers and platform leads."
        ),
        "source_fact_ids": ["fact_exec_002"],
    },
    {
        "claim": (
            "Complementing that delivery foundation, Basel III and CCAR lineage discipline "
            "accelerates lineage-ready IT strategy velocity without turning governance into a "
            "control checklist."
        ),
        "claim_text": (
            "Implemented Basel III / CCAR data lineage, cataloging, and automated validation "
            "frameworks that cut regulatory reporting errors by 40%."
        ),
        "source_fact_ids": ["fact_governance_003"],
    },
    {
        "claim": BROWN_S5_FRAGMENT,
        "claim_text": (
            "Built advanced quantitative foundation through derivatives pricing, multi-Greek "
            "hedging, capital modeling, and FSA credential across Towers Perrin, ING, and Aetna."
        ),
        "source_fact_ids": ["fact_quant_hpc_003"],
    },
]

BROWN_ALLOWED_FACT_IDS = frozenset(
    {
        "fact_certs_001",
        "fact_engineering_platform_001",
        "fact_exec_002",
        "fact_governance_003",
        "fact_quant_hpc_003",
    }
)

BROWN_SELF_CHECK = {
    "every_material_claim_in_claim_ledger": True,
    "no_first_person": True,
    "s6_starts_with_looking_ahead": True,
}

BROWN_TARGET_ROLE = "SVP IT Strategy & Innovation"
BROWN_TARGET_COMPANY = "Brown & Brown"
