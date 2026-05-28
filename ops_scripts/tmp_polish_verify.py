import re
from apps_rg.runtime.sections.executive_summary_voice_repair import polish_executive_summary_judge_alignment

facts = [
    {"fact_id": "fact_exec_002", "claim_text": "Scaled ML org 8 to 28"},
    {"fact_id": "fact_governance_003", "claim_text": "Basel III cut errors 40%"},
    {"fact_id": "fact_engineering_platform_002", "claim_text": "Graph intelligence"},
    {"fact_id": "fact_engineering_platform_001", "claim_text": "Agentic AI platform"},
    {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA work"},
    {"fact_id": "fact_consulting_001", "claim_text": "Consulting"},
]

variants = {
    "canonical_212812": (
        "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, and digital innovation programs into one IT strategy and innovation agenda for decentralized regulated enterprises. "
        "Through that operating model, Basel III and CCAR data lineage, cataloging, and automated validation frameworks cut regulatory reporting errors by 40%. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis, exposes architecture dependency chains, and improves transformation visibility across enterprise complexity. "
        "That regulatory foundation is grounded in quantitative rigor established through FSA-chartered actuarial work in capital modeling and portfolio stress analytics, informing data governance and AI strategy at scale. "
        "Against that delivery foundation, directed large-scale regulatory IT transformations and legacy-modernization programs for major financial institutions across risk, compliance, data, cloud, and architecture domains. "
        "In parallel, the ML engineering organization grew from 8 to 28 specialists, including senior engineers and platform leads."
    ),
    "missing_fsa_consulting": (
        "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, and digital innovation into one IT strategy agenda. "
        "Designs and operationalizes a governed agentic AI platform for regulated enterprise workflows, improving control-plane delivery and audit-ready execution. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis, exposes architecture dependency chains, and improves transformation visibility across enterprise complexity. "
        "Implementing Basel III / CCAR data lineage frameworks reduces regulatory reporting errors by 40%. "
        "Innovation incubation and architecture standards can federate governed platform capabilities across autonomous business units. "
        "The ML engineering organization grew from 8 to 28 specialists, including senior engineers and platform leads."
    ),
    "duplicate_graph": (
        "Enterprise technology leader who aligns governed AI platforms, regulatory lineage, and digital innovation. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis across enterprise complexity. "
        "Built and applied software dependency graph intelligence to accelerate legacy-system analysis, improve architecture visibility. "
        "Basel III and CCAR data lineage reduced regulatory reporting errors by 40%, accelerating IT strategy velocity. "
        "FSA-chartered actuarial work in capital modeling and portfolio stress analytics informs data governance and AI strategy. "
        "The ML engineering organization grew from 8 to 28 specialists, including senior engineers and platform leads."
    ),
}

required = {
    "fact_exec_002", "fact_governance_003", "fact_engineering_platform_002",
    "fact_engineering_platform_001", "fact_quant_hpc_003", "fact_consulting_001",
}

for name, text in variants.items():
    parsed = {"resume_display_text": text, "claim_ledger": []}
    p, r = polish_executive_summary_judge_alignment(parsed, selected_facts=facts)
    out = p["resume_display_text"]
    wc = len(re.findall(r"\S+", out))
    cited = {fid for row in p.get("claim_ledger", []) for fid in row.get("source_fact_ids", [])}
    missing = required - cited
    print(f"=== {name} ===")
    print(f"  words={wc}")
    print(f"  actions={r['actions']}")
    print(f"  missing_required_facts={missing}")
    for i, s in enumerate(out.split(". ")):
        print(f"  S{i+1}: {s[:90]}")
    print()
