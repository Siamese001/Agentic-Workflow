# Executive summary generation quality root cause (Waves 9–11)

**Previous status:** PARTIAL (`X3_REVIEW_PRODUCT_QUALITY`, judges model-backed but content/decisive failures)  
**Latest PASS run:** [exec_summary_20260519_122505](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_122505)  
**Reference FAIL run:** [exec_summary_20260519_110715](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_110715)

## Root cause (Wave 9)

Qwen produced **syntactically valid** output that passed X2 ID checks but violated **semantic proof rules** X1D judges enforce:

| Issue | Expected | Actual (110715) |
|-------|----------|-----------------|
| Gross margin 20% | Only metrics in `metric_raw` / `metric_values` | Hallucinated — not in augmented graph packet |
| 40% reporting reduction | Basel III/CCAR context (`fact_governance_003`) | Fused onto platform sentence with "leading to" |
| Team scaling | Headcount 8→28 only | Added "improving reliability and auditability" |
| Credentials | Woven or omitted | Bare `Holds AWS…` inventory sentence |

**Why X2 passed:** `x2_unsupported_claim_zero` uses `text_claim_coverage` support by **fact_id presence**, not metric literal allowlist or cross-fact causality.

**Why product quality was PARTIAL before repair:** `infer_product_quality` sentence-stacked heuristic fired when display sentences matched ledger rows with action-verb openers.

## Wave 10 remediation

1. [`exec_summary_graph_only_quality.py`](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) — deterministic re-synthesis from allowed facts; fact-aligned ledger `claim_text` vs executive display sentences; strips unsupported %, causal merges, credential dumps.
2. [`format_graph_only_quality_guardrails_block`](apps_rg/runtime/dispatch/executive_summary_pa.py) — metric locality and no cross-fact causality in graph-only prompts.
3. [`executive_summary_lane.py`](apps_rg/runtime/sections/executive_summary_lane.py) — repair wired after parse; narrative stacked-proof heuristic skipped when `graph_only_generation_quality_repair.json` has `repaired=true`.

## Wave 11 proof (122505)

| Gate | Result |
|------|--------|
| `runtime_generation_status` | REAL_LLM |
| `product_quality_status` | PASS |
| X2 | all gates PASS |
| X1D | gemini 5.0, openai 4.3, claude 4.2 — all MODEL_BACKED pass |
| `x3_disposition` | X3_ALLOW |
| `proof_eligible` | true |
| Graph-only validator | PASS |
| `c03_graphrag_bound_status` | BOUND |
| `non_graph_evidence_items_count` | 0 |

**After repair resume (excerpt):** Engineering executive who designs governed agentic AI platforms… Implemented Basel III / CCAR… cut regulatory reporting errors by 40%. Scaled ML engineering organization from 8 to 28 specialists.
