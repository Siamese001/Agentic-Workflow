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

required = {
    "fact_exec_002", "fact_governance_003", "fact_engineering_platform_002",
    "fact_engineering_platform_001", "fact_quant_hpc_003", "fact_consulting_001",
}

# Test the actual degenerate input from run 225447 (after graph_only repair)
degenerate_225447 = (
    "Enterprise technology leader who aligns governed AI platforms, regulatory lineage, and digital innovation programs into one IT strategy agenda for decentralized regulated enterprises. "
    "Designs and operates platform runtimes with deterministic controls and traceable execution, ensuring innovation scales without sacrificing validation-ready delivery. "
    "Building on that foundation, platform revenue outcomes. "
    "Against that delivery foundation, Basel III lineage discipline reduced financial reporting errors by 40%, accelerating IT strategy velocity without turning compliance into a delivery bottleneck. "
    "That quantitative and governance foundation enables federated platform capabilities across decentralized operating units, preserving lineage discipline and investment rigor at enterprise scale."
)

variants = {
    "degenerate_225447 (5 sentences)": degenerate_225447,
    "canonical_212812 (6 sentences)": (
        "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, and digital innovation programs into one IT strategy and innovation agenda for decentralized regulated enterprises. "
        "Through that operating model, Basel III and CCAR data lineage, cataloging, and automated validation frameworks cut regulatory reporting errors by 40%. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis, exposes architecture dependency chains, and improves transformation visibility across enterprise complexity. "
        "That regulatory foundation is grounded in quantitative rigor established through FSA-chartered actuarial work in capital modeling and portfolio stress analytics, informing data governance and AI strategy at scale. "
        "Against that delivery foundation, directed large-scale regulatory IT transformations and legacy-modernization programs for major financial institutions across risk, compliance, data, cloud, and architecture domains. "
        "In parallel, the ML engineering organization grew from 8 to 28 specialists, including senior engineers and platform leads."
    ),
}

for name, text in variants.items():
    parsed = {"resume_display_text": text, "claim_ledger": []}
    p, r = polish_executive_summary_judge_alignment(parsed, selected_facts=facts)
    out = p["resume_display_text"]
    wc = len(re.findall(r"\S+", out))
    from apps_rg.runtime.validators.executive_summary_x2 import split_sentences
    sents = split_sentences(out)
    cited = {fid for row in p.get("claim_ledger", []) for fid in row.get("source_fact_ids", [])}
    missing = required - cited
    print(f"=== {name} ===")
    print(f"  input_sentences={len(split_sentences(text))} output_sentences={len(sents)} words={wc}")
    print(f"  actions={r['actions']}")
    print(f"  missing_required_facts={missing}")
    for i, s in enumerate(sents):
        print(f"  S{i+1}: {s[:90]}")
    print()
