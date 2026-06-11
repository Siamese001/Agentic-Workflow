---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg_token_budgeting_rules.md'
original_relative_path: 'adg_token_budgeting_rules.md'
source_sha256: 7df5294488506c0d5a25c618601d8ba15349a01429c0e3ba29d30c5a7c028d49
recovered_status: LOST_RECOVERED
last_commit: 'fd8afcb3494'
last_commit_date: '2026-04-11 11:10:04 -0400'
created_date: '2026-04-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Token Budgeting Rules — C0 Bridge
**Stage 1 Design — No code changes**
**Date:** 2026-04-11 | Scope: Token budgeting for C0-sourced EvidenceBundle through existing PA infrastructure

---

## 1. Executive Summary

The existing `token_budgeter.py` is fully functional for C0 bridge use. The critical difference from ADG-file-sourced packets is that C0 `text_snippet` values are **unbounded prose strings** whereas ADG file adapters produce **structured JSON rows** (compact, predictable size). Without upstream truncation, a single C0 span can consume the entire `must_use_evidence` allocation. This document defines the constraints the `c0_to_pa_adapter` must enforce **before** calling `_assemble()`, so that the existing `apply_budget()` function operates correctly and produces deterministic, bounded output.

**Core rule:** The adapter is the boundedness gate. `apply_budget()` is the overflow gate. Both must operate correctly for the bridge to be safe.

---

## 2. Existing Budget Infrastructure (Baseline)

### 2.1 `TokenBudget` per packet type

| Packet type | `total` | `system_policy` | `task` | `must_use_evidence` | `optional_evidence` | `contradiction_meta` |
|-------------|---------|----------------|--------|---------------------|--------------------|--------------------|
| `determinism_rca` | 8,000 | 800 | 400 | 5,600 | 800 | 400 |
| `p0_failure` | 6,000 | 800 | 400 | 4,000 | 400 | 400 |
| `ratchet_review` | 6,000 | 800 | 400 | 4,000 | 400 | 400 |
| `unknown_unresolved_triage` | 6,000 | 800 | 400 | 4,000 | 400 | 400 |
| `hotspot_investigation` | 8,000 | 800 | 400 | 5,600 | 800 | 400 |
| `infrastructure_boundary` | 6,000 | 800 | 400 | 4,000 | 400 | 400 |
| `graph_path_explanation` | 6,000 | 800 | 400 | 4,000 | 400 | 400 |
| `executive_summary` | 4,000 | 800 | 400 | 2,000 | 400 | 400 |

**For the C0 bridge, the primary targets are `executive_summary` (4,000 total) and `graph_path_explanation` (6,000 total).** Most C0 runtime queries will route to these two.

### 2.2 `_assemble()` fixed-token computation

```python
fixed_tokens = (
    estimate_tokens(template.system_block, "text")   # ~100–150 tokens
    + estimate_tokens(template.policy_block, "text") # ~150–200 tokens
    + estimate_tokens(task_block, "text")             # ~50–200 tokens
)
```

For `executive_summary`:
- `system_block` ≈ 120 tokens
- `policy_block` = `_SHARED_POLICY` (7 rules) ≈ 180 tokens
- `task_block` ≈ 80–150 tokens
- Total fixed ≈ **380–450 tokens**
- Remaining for evidence, contradictions, schema, replay: ≈ **3,550–3,620 tokens**

`apply_budget()` receives `fixed_tokens` and deducts them from `template.token_budget.total` to compute available evidence budget. The existing implementation is correct — no change needed.

### 2.3 `estimate_tokens()` — token counting method

Defined in `token_budgeter.py`:
```python
def estimate_tokens(text: str, block_type: str = "text") -> int:
    base = len(text) // 4  # approximate 4 chars per token
    ...
```

**For C0 bridge:** `text_snippet` character count / 4 is the token estimate for each span. This is correct and sufficient. No change to the estimation function.

---

## 3. C0-Specific Pre-budgeting Constraints (Adapter Responsibility)

These constraints are enforced by `c0_to_pa_adapter` **before** passing `EvidenceItem` objects to `_assemble()`. They ensure `apply_budget()` receives well-bounded input.

### 3.1 `text_snippet` Maximum Length

**Rule:** Each `CitedSpan.text_snippet` is truncated to a maximum of **512 characters** before placement in `EvidenceItem.data["text_snippet"]`.

**Rationale:**
- 512 chars ≈ 128 tokens per span
- `executive_summary` has 2,000 tokens for `must_use_evidence`
- At 128 tokens/span, the adapter can include up to 15 spans before the must-use budget is consumed
- In practice, high-relevance spans are far fewer (target: 3–8 per query)
- Truncation at 512 is conservative enough to preserve meaning; most embedding retrieval chunks are 256–512 chars

**Truncation rule:** Truncate at the last whitespace before character 512 (word-boundary truncation). Append `"..."` to signal truncation. Log truncation as a gap string: `"truncated_span:<span_id>"`.

**Exception:** If `text_snippet` is already ≤ 512 chars, pass through unchanged.

### 3.2 Maximum Spans per Packet

**Rule:** Maximum **20 CitedSpan objects** per `C0EvidenceContract` → `EvidenceBundle`.

**Rationale:**
- 20 spans × 128 tokens/span = 2,560 tokens — within the `hotspot_investigation`/`determinism_rca` must_use budget
- For `executive_summary` (2,000 token must-use budget): the adapter should further reduce to max **15 spans** when targeting `executive_summary`
- For `graph_path_explanation` (4,000 token must-use budget): up to 20 spans are safe

**Per-packet max span table:**

| Packet type | Max spans | Rationale |
|-------------|----------|-----------|
| `executive_summary` | 15 | 2,000 token budget; must stay bounded |
| `graph_path_explanation` | 20 | 4,000 token budget; path evidence may be detailed |
| All ADG-file-first types | N/A | C0 spans not expected here; abstain path fires |

**Span pruning priority before the cap:** If `cited_spans` count exceeds the max, prune lowest `relevance_score` spans first, preserving the highest-relevance spans. This is adapter-side pruning, before `apply_budget()` runs.

### 3.3 Minimum Span Count to Proceed

**Rule:** If `len(contract.cited_spans) == 0` after any pruning, do not call `_assemble()`. Return the pre-populated abstain bundle immediately.

**Rule:** If `len(contract.cited_spans) > 0` but all spans have `relevance_score < 0.10`, treat as effectively empty. Log gap: `"all_spans_below_minimum_relevance"`. Route to abstain.

### 3.4 Span Ordering for Budget Priority

**Rule:** The adapter sorts `cited_spans` by `relevance_score` descending **before** constructing `EvidenceItem` objects. This ensures that when `apply_budget()` trims must-use evidence, it trims from the end (lowest relevance) first.

**Implementation note:** `apply_budget()` trims `must_use_evidence` by popping from the end of the list when budget is exceeded. The adapter's pre-sort directly controls trim order.

### 3.5 Reserved Budget for Non-Evidence Blocks

The following blocks are never trimmed by `apply_budget()` and must always fit within the total budget. The adapter must ensure the non-evidence blocks consume no more than their allocated share:

| Block | Allocation | Notes |
|-------|-----------|-------|
| `system_block` | ~150 tokens | Fixed per packet type; immutable |
| `policy_block` | ~200 tokens | `_SHARED_POLICY` 7 rules; immutable |
| `task_block` | ≤ 200 tokens | Adapter/dispatcher must not exceed 200 tokens |
| `contradiction_flags` | ≤ 100 tokens per flag, max 4 flags | Total ≤ 400 tokens |
| `abstain_instructions` | ~80 tokens (base) + ≤ 100 tokens (gap augment) | Total ≤ 180 tokens |
| `refine_instructions` | ~100 tokens (base) + ≤ 80 tokens (overflow note) | Total ≤ 180 tokens |
| `output_schema` | ~50–100 tokens per packet | Fixed per packet type; immutable |
| `replay_metadata` | ≤ 200 tokens | C0 extras add ~50 tokens to the base |

**Total non-evidence overhead estimate:**
- Conservative: ~980 tokens (system + policy + task + contradictions + instructions + schema + replay)
- For `executive_summary` (4,000 total): evidence budget ≈ **3,020 tokens**
- For `graph_path_explanation` (6,000 total): evidence budget ≈ **5,020 tokens**

**Rule:** The `task_block` supplied by the L3 dispatcher must be truncated to 200 tokens if longer. Dispatcher responsibility.

### 3.6 Contradiction Flag Budget

**Rule:** Maximum **4 `ContradictionFlag` objects** per `EvidenceBundle` when C0-sourced.

**Rationale:** Each serialized flag is ~50–100 tokens. 4 flags = max 400 tokens, fitting within the `contradiction_meta` budget allocation across all packet types.

**If more than 4 contradictions exist:** Keep the 4 highest-severity flags (major > minor). Log the count of suppressed flags in `replay_metadata["suppressed_contradiction_count"]`.

### 3.7 Replay Metadata Budget

**C0 extras added to `replay_metadata` via `replay_extras`:**

| Field | Typical token cost |
|-------|-------------------|
| `retrieval_id` (UUID) | ~5 tokens |
| `request_id` (UUID) | ~5 tokens |
| `evidence_hmac` (SHA-256 hex) | ~18 tokens |
| `coverage_score` (float) | ~3 tokens |
| `abstain_hint` (bool) | ~2 tokens |
| `confidence_band` (string) | ~3 tokens |
| **C0 extras subtotal** | **~36 tokens** |

Existing base `replay` fields (`snapshot_ids`, `commit_shas`, `artifact_digests`, `source_artifacts`) are empty or short for C0-sourced bundles. Total `replay_metadata` token cost ≈ **50–80 tokens**. Well within the 200-token estimate.

---

## 4. Span Prioritization Rules

When the span list must be reduced (either by the adapter before `_assemble()` or by `apply_budget()` inside `_assemble()`), spans are ranked by the following criteria in strict priority order:

### Priority 1: Relevance score (primary sort key)
- `relevance_score >= 0.70` → HIGH band — preserve first
- `0.50 <= relevance_score < 0.70` → MEDIUM band — preserve after HIGH
- `0.30 <= relevance_score < 0.50` → LOW band — include only if budget allows
- `relevance_score < 0.30` → DISCARD — do not include (log as gap: `"low_relevance_span:<span_id>"`)

### Priority 2: Source diversity (secondary sort key)
Within the same relevance band, prefer spans from **different `source_ref` files** over multiple spans from the same file. Reason: L2 reasoning benefits from cross-source grounding more than depth on one file.

**Rule:** Maximum **3 spans from the same `source_ref`** in any one bundle.

### Priority 3: Position in retrieval order (tiebreaker)
If relevance scores are equal, preserve the span's original retrieval order (C0's ranked retrieval output is already ordered by relevance). No additional sorting needed.

---

## 5. `apply_budget()` Interaction with C0 Evidence

The existing `apply_budget()` function in `token_budgeter.py` handles C0 evidence correctly because:

1. **Trim order:** `opt_items` trimmed first → then `must_items` (if still over budget after optional trim). For C0 bridge: `opt_items=[]`, so only `must_items` (C0 spans) are trimmed. Trimming happens from the end of the list — the adapter's `relevance_score` pre-sort ensures lowest-relevance spans are trimmed first.

2. **Overflow strategies** apply in this order (existing implementation):
   - `"summarize"` — truncate individual evidence items to a shorter summary
   - `"narrow"` — drop the lowest-priority items
   - `"split"` — not supported in current implementation; returns `overflow_action="split"`
   - `"abstained"` — emit abstain packet

3. **`budget_status` values:** `"within_budget"`, `"trimmed"`, `"abstained"` — all three apply naturally to C0 evidence.

4. **`summary_note`:** If overflow action is `"summarize"` or `"narrow"`, `BudgetResult.summary_note` is populated. `_assemble()` prepends it to `refine_instructions`. This behavior is correct for C0 evidence — no change needed.

**C0-specific rule:** If `apply_budget()` triggers `overflow_action="abstained"` (budget is so tight even must-use evidence cannot fit), the bridge must treat this identically to `abstain_hint=True`: return `assembly_result="fail"` and do **not** write the packet to `artifacts/adg/packets/`.

---

## 6. Token Budget Summary Tables

### 6.1 `executive_summary` — Primary C0 Bridge Packet

| Block | Allocated | C0 Typical | Status |
|-------|----------|-----------|--------|
| `system_block` | ~120 tok | ~120 tok | Fixed |
| `policy_block` | ~180 tok | ~180 tok | Fixed |
| `task_block` | ≤ 200 tok | ~100 tok | Dispatcher bounded |
| `must_use_evidence` | 2,000 tok | 3–15 spans × ≤128 tok = 384–1,920 tok | Within budget |
| `optional_evidence` | 400 tok | 0 tok (no optional for C0) | Unused |
| `contradiction_flags` | 400 tok | 0–4 flags × 50–100 tok = 0–400 tok | Bounded |
| `abstain_instructions` | ~180 tok | ~120–180 tok | Bounded |
| `refine_instructions` | ~180 tok | ~120–180 tok | Bounded |
| `output_schema` | ~80 tok | ~80 tok | Fixed |
| `replay_metadata` | ~200 tok | ~50–80 tok | Within budget |
| **TOTAL** | **4,000 tok** | **~1,354–3,260 tok** | **Within budget** |

**Comfortable headroom at 15 spans.** Risk of overflow only above ~22 spans at max snippet length.

### 6.2 `graph_path_explanation` — Conditional C0 Bridge Packet

| Block | Allocated | C0 Typical | Status |
|-------|----------|-----------|--------|
| `must_use_evidence` | 4,000 tok | 3–20 spans × ≤128 tok = 384–2,560 tok | Within budget |
| Other blocks | ~1,600 tok combined | ~700–1,000 tok | Within budget |
| **TOTAL** | **6,000 tok** | **~1,084–3,560 tok** | **Within budget** |

**Very comfortable headroom.** Only at max spans (20) and max snippet length (512 chars) does total approach 4,560 tokens — still within the 6,000 budget.

---

## 7. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| `estimate_tokens()` uses char/4 approximation — accurate to ±15% | **Confirmed** from `token_budgeter.py` |
| `apply_budget()` trims `must_use_evidence` from the end of the list | **Confirmed** from implementation |
| `opt_items=[]` for pure C0 bundles — optional budget entirely unused | **Confirmed** from bridge design |
| 512-char truncation threshold preserves semantic meaning for most retrieval chunks | **Design assumption** — based on typical embedding chunk sizes of 256–512 chars |
| 15-span limit for `executive_summary` produces meaningful evidence coverage | **Design assumption** — calibrated to 2,000 token must-use budget at 128 tok/span |
| `relevance_score < 0.10` treated as effectively empty span | **Design choice** — below meaningful retrieval signal |
| L3 dispatcher's `task_block` will not exceed 200 tokens | **Adapter enforcement assumption** — must be documented as dispatcher contract |
