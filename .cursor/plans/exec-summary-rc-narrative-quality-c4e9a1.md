# Plan: exec-summary-rc-narrative-quality-c4e9a1

## Objective

Fix the remaining structural quality failures in the `executive_summary` section that cause
`X3_REVIEW_JUDGE_SOFT_FAIL` (Claude score 3.6 vs 4.0 threshold) AFTER the commercialization
root causes were fixed in `exec-summary-rc-composition-hardcode-b3d7e1`.

**The commercialization word is now gone.** This plan addresses the narrative quality defects
that remain.

## Parent Plan Chain

- `exec-summary-rc-structural-repair-f4a8c2` (Notion: 36d27693-f55c-8131-b67c-fc0aa960d9dc)
- `exec-summary-rc-composition-hardcode-b3d7e1` (Notion: 36d27693-f55c-8177-acd3-eb29f6fd1a91)

## Root Causes

### RC-H: graph_only_generation_quality_repair overwrites good first-pass connective tissue

**Evidence**: The first-pass LLM output for run `full_resume_6276402f4ef5` showed:
- S2: "Designs and operates platform runtime with deterministic controls..."
- S3: "Building on that foundation, supply-chain platform modernization..."

Good thesis-referent connectors following W4 instructions. But the first pass also included
`$22M` and `20%` values from `fact_engineering_platform_006` which is NOT in the allowed fact
pool for this run. The `graph_only_generation_quality_repair` fired because `20%` is an
unsupported_percent_token. The repair rewrites the ENTIRE text with a template that produces
bare achievement openers (S3: "Scaled the ML engineering organization...").

**Files**: `apps_rg/runtime/sections/executive_summary_lane.py` (graph_only repair invocation)
and/or the repair template logic itself.

**Fix direction**: When graph_only repair fires for unsupported_percent_tokens only (not for
mechanical_opener_stack or cross_fact_conflation), preserve the good connective tissue of
non-violating sentences. Only strip/replace the sentence(s) containing the unsupported token.

### RC-I: DISPLAY_OVERRIDE verbatim compliance not enforced

**Evidence**: 
- `fact_quant_hpc_003` DISPLAY_OVERRIDE = "Quantitative rigor was established through
  FSA-chartered actuarial work in capital modeling and portfolio stress analytics across
  early-career roles."
- Actual output S4: "Established quantitative rigor through FSA-chartered actuarial work in
  capital modeling and portfolio stress analytics, which informed data governance and AI strategy."
  (paraphrase, not verbatim)

- `fact_engineering_platform_002` DISPLAY_OVERRIDE = "Software dependency graph intelligence
  enables accelerated legacy-system analysis, exposes architecture dependency chains, and
  improves transformation visibility across enterprise complexity."
- Actual output S6: "Built and applied software dependency graph intelligence to accelerate
  legacy-system analysis, improve architecture visibility, and position the enterprise for
  faster M&A integration and modernization." (paraphrase, not verbatim)

The X2 gate enforces the fragment check but not DISPLAY_OVERRIDE verbatim compliance. The
model substitutes a paraphrase.

**Fix direction**: Add X2 gate for verbatim DISPLAY_OVERRIDE compliance — if a
`DISPLAY_OVERRIDE` fact is in the claim ledger, the sentence containing it must include a
sufficiently close match (7-gram overlap or substring anchor check).

### RC-J: $22m style echo from E0 example pattern persists across synthesis regen

**Evidence**: Both synthesis regen attempts (cycles 00-01 and 00-02) also echo "$22m" even
with the E0 example now using placeholder `$[X]M`. The model pattern-locks to this value
from the evidence capsule's fact context (fact_engineering_platform_006 appears in the
evidence even if it's not in the allowed pool for this run's selected_fact_plan).

**Fix direction**: Ensure that `fact_engineering_platform_006` (the $22M fact) is excluded
from the evidence capsule for runs where it is not in `selected_fact_plan.facts`. Cross-
reference the synthesis regen prompt construction to avoid injecting unsupported facts into
the context.

### RC-K: S4 actuarial sentence lacks strategic connection to SVP IT thesis

**Evidence**: Claude finding: "S4 mentions FSA-chartered actuarial work and capital modeling;
while fact-supported, the connection to the SVP IT Strategy & Innovation thesis is weak and
reads as resume filler."

The DISPLAY_OVERRIDE for `fact_quant_hpc_003` only addresses the sentence content; it doesn't
add a connector to S1/S3. The sentence opens without a thesis-referent bridge.

**Fix direction**: Update `fact_quant_hpc_003` DISPLAY_OVERRIDE to include a connector at the
start, e.g., "That governance discipline is grounded in an FSA-chartered actuarial foundation
spanning capital modeling and portfolio stress analytics — a quantitative rigor that informs
data governance and AI strategy at scale."

## Waves

### W1: Surgical sentence repair in graph_only when only unsupported_percent_tokens fires
**File**: `apps_rg/runtime/sections/executive_summary_lane.py` (or repair module)
**Change**: When `needs_repair` is triggered solely by `unsupported_percent_tokens` (all other
flags False), strip only the sentences containing the unsupported tokens rather than full rewrite.
Preserve good connective tissue from non-violating sentences.

### W2: X2 gate for DISPLAY_OVERRIDE substring compliance
**File**: `apps_rg/runtime/validators/executive_summary_x2.py`
**Change**: Add `check_exec_summary_display_override_compliance` gate. For each fact in
`FACT_C0_DISPLAY_OVERRIDES`, if the fact appears in claim_ledger, verify the override's
leading 8-word anchor appears in `resume_display_text`.

### W3: Fix fact_quant_hpc_003 DISPLAY_OVERRIDE to include strategic connector
**File**: `apps_rg/runtime/sections/executive_summary_synthesis_contract.py`
**Change**: Update `FACT_C0_DISPLAY_OVERRIDES["fact_quant_hpc_003"]` to start with a
thesis-referent connector so S4 links to S1 explicitly.

### W4: Exclude unsupported facts from synthesis regen evidence capsule
**File**: `apps_rg/runtime/sections/executive_summary_lane.py` (synthesis regen prompt builder)
**Change**: Filter the evidence capsule facts for synthesis regen to only include facts
present in `selected_fact_plan.facts`. This prevents $22M and 20% from leaking in.

### W5: Unit tests for W1-W4

### W6: Brown SVP proof re-run targeting exit code 0

## NOTION_PAGE_ID

36d27693-f55c-81cb-b868-f2f3ddc3a5aa

## Status

NOT_STARTED
