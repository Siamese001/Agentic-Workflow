---
plan_id: exec-summary-qwen-regen-token-budget-c4e8a1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary Qwen Regen Token Budget — Remediation

Close the gap between **first-call** token budgeting (pre-dispatch trim) and **retry/regen** Qwen calls (synthesis regen, judge regen, X2 repair) so multi-turn runs stay inside `VLLM_MAX_MODEL_LEN` without silent truncation, transport-timeout masquerading as success, or **fake-accepted** regen cycles.

> **Review:** BASICALLY SAFE TO EXECUTE (2026-05-25).  
> **Hardening status:** NEEDS HARDENING applied (2026-05-25) — directionally safe; scope locked to **runtime transport/budget only**.  
> **Related (completed):** [exec-summary-token-budget-a8f3c2.md](exec-summary-token-budget-a8f3c2.md) — optional-only first-call trim.  
> **Research SSOT:** [executive_summary_qwen_regen_token_budget_research_20260525.md](docs/reports/apps_rg/executive_summary_qwen_regen_token_budget_research_20260525.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-26
PLAN_HARDENING: applied-2026-05-25
PLAN_REVIEW: basically-safe-to-execute-2026-05-25
PLAN_COMPLETE: plan=exec-summary-qwen-regen-token-budget-c4e8a1 note="W1–W4 implemented; unit/contract proof PASS; D3 Brown budget soak deferred follow-up"
DEFERRED_SCOPE: D3 Brown REAL_LLM budget soak — operator guide command; not blocking code closeout
NOTION_PAGE_ID: 36b27693-f55c-81df-89b9-dc0414ffd751

---

## Scope lock (non-negotiable)

**In scope:** Runtime transport/budget hardening for `apps_rg` executive_summary — regen dispatch wrapper, fail-closed guards, tiered `max_tokens`, thread compaction without judging-contract drift, receipts, static bypass checks, contract tests, Brown **budget-behavior** proof.

**Out of scope (do not broaden):**

- Prompt/rubric changes, judge threshold changes, X1D disposition policy
- Claiming Claude/judge **quality** remediation (this plan proves **budget safety**, not judge agreement)
- `agentic_core` edits unless W4 escalates with `touches_agentic_core=true` + author gate (see W4 boundary)

---

## Context (SCQA)

- **Situation** — First-call trim works ([executive_summary_token_budget.py](apps_rg/runtime/sections/executive_summary_token_budget.py)). Regen paths reuse/grow `messages[]` without a fresh context budget.
- **Complication** — Historical defect: cycles `accepted=true` without `provider_response_judge_regen.json`; `delta_token_budget_exceeded`; up to ~9 Qwen completions per run.
- **Question** — How do we harden **all** regen Qwen dispatch without weakening evidence or judge contracts?
- **Answer** — Single mandatory `budgeted_qwen_regen_call(...)` wrapper, fail-closed pre-dispatch, artifact-backed acceptance, defined judge-thread preservation, run-level `executive_summary_qwen_call_plan.json`.

---

## Non-negotiable invariants

| ID | Invariant |
|----|-----------|
| I1 | Every regen-capable Qwen call uses `budgeted_qwen_regen_call(...)` — no direct `call_qwen_vllm(...)` in synthesis/judge/X2 repair paths |
| I2 | Over-budget regen: `dispatch_allowed=false`, `transport_dispatched=false`, `accepted=false`, explicit `block_reason`; **no** `score_deltas` synthesis |
| I3 | Regen `accepted=true` only when same **`call_id`** has matching provider response artifact, `parse_ok=true`, and linked rows in receipts + call plan |
| I4 | Judge thread compaction may drop **unbounded full assistant JSON history** only — must preserve rubric, candidate, facts, dimensions, critique (see W1.4) |
| I5 | Regen `max_tokens` ≤ scratch cap; default regen **1024**, scratch **2048** |
| I6 | `budget_allowed=true` + `transport_timeout=true` ≠ accepted; timeout is transport failure, not budget pass |
| I7 | `provider_context_window` receipt must not claim server truth unless `server_context_window_verified=true` |
| I8 | **Strongest gate:** over-budget, transport timeout, missing response artifact, or parse failure → **`accepted` must never be true** |

---

## Static bypass — allowed direct-call exceptions (concrete)

The static test (`tests/_apps_contract/test_exec_summary_regen_qwen_dispatch_ssot.py`) must encode this allowlist **before** implementation so the check is neither too loose nor too brittle.

| Call class | Allowed path | Rule |
|------------|--------------|------|
| **Scratch first-call** | `executive_summary_lane.py` — single post–token-budget dispatch site (existing `call_qwen_vllm` after `build_qwen_request` + first-pass `apply_executive_summary_token_budget_policy`) | Exactly **one** lane-local scratch generation dispatch; may remain direct `call_qwen_vllm` **or** migrate to `budgeted_qwen_scratch_call(...)` if introduced — but **not** required for W1 |
| **Post-scratch regen/repair** | `budgeted_qwen_regen_call(...)` only | `retry_qwen_for_synthesis`, `retry_qwen_for_judge_remediation`, `repair_judge_regen_after_x2_fail`, and any future exec-summary regen helper |
| **Wrapper internals** | Inside `budgeted_qwen_regen_call` / `executive_summary_qwen_regen_dispatch.py` | May call `call_qwen_vllm` — this is the **only** permitted direct transport site for regen |
| **Forbidden** | Any other `call_qwen_vllm` in `executive_summary_lane.py`, `executive_summary_judge_remediation.py`, `executive_summary_judge_regen_loop.py`, or synthesis repair helpers **outside** scratch site + wrapper | Test fails with file:line |

**Test implementation note:** Allowlist = fixed set of symbols/files (not “grep and hope”). Deny `call_qwen_vllm` in remediation modules except wrapper module.

---

## Regen call identity — deterministic artifact naming

Every regen dispatch allocates a stable **`call_id`** before budget check. The same `call_id` links request, response, receipt row, call-plan row, and judge-cycle record.

**`call_id` format (deterministic):**

```text
{phase}-{cycle_index:02d}-{attempt_index:02d}-{short_hash8}
```

Examples: `judge_regen-01-01-a3f2b1c4`, `synthesis_regen-00-02-9e81d0aa`, `judge_x2_repair-02-01-44c0e1b2`

**Required index fields (on receipt row, call-plan row, cycle record):**

| Field | Values / notes |
|-------|----------------|
| `call_id` | Primary join key across all artifacts |
| `phase` | `scratch` \| `synthesis_regen` \| `judge_regen` \| `judge_x2_repair` |
| `cycle_index` | Judge regen outer loop index (0 for non-cyclic phases) |
| `attempt_index` | Inner attempt within phase (synthesis 0..N, regen 0..0 per cycle) |
| `call_site` | Function name (e.g. `retry_qwen_for_judge_remediation`) |

**Artifact filename pattern (when written to disk):**

| Artifact | Pattern |
|----------|---------|
| Provider request | `provider_request_{phase}_cycle{cycle_index:02d}_attempt{attempt_index:02d}_{call_id}.json` |
| Provider response | `provider_response_{phase}_cycle{cycle_index:02d}_attempt{attempt_index:02d}_{call_id}.json` |

Legacy names (`provider_response_judge_regen.json`) may remain as **symlink or latest-cycle alias** only if documented in receipt; verifier uses **`call_id`**, not glob alone.

**Verifier join (D8):** For each `calls[]` entry with `accepted=true`, prove same `call_id` has: `provider_request_*`, `provider_response_*`, parse OK, `provider_response_present=true`, and (for judge) linked `score_deltas` referencing that `call_id`.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.0–W1.5 | Wrapper + guards + receipts + call plan + tests | ~55K | Parity for judge soak | ✅ DONE | No bypass; artifact-backed acceptance; call plan |
| W2 | W2.1–W2.2 | Context SSOT + deterministic 85% first-pass | ~25K | Env may be unverified | ✅ DONE | Labeled window source; deterministic trim order |
| W3 | W3.1–W3.2 | Operator docs polish (call plan SSOT in W1) | ~15K | W1 ships call plan | ✅ DONE | Guide env table + timeout guidance |
| W4 | W4.1 | Apps-only delta policy via public seam | ~15K | **Blocked** if core code edit | ✅ DONE | No silent core change under apps plan |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.0 | `budgeted_qwen_regen_call` SSOT | `executive_summary_qwen_regen_dispatch.py` (new) or `executive_summary_token_budget.py` | Caller-by-caller guard drift | ~15K | 🔲 TODO |
| W1.1 | Token estimate + allow | `executive_summary_token_budget.py` | No regen input math | ~10K | 🔲 TODO |
| W1.2 | Wire synthesis/judge/X2 repair | `executive_summary_lane.py`, `executive_summary_judge_remediation.py` | Direct `call_qwen_vllm` bypass | ~12K | 🔲 TODO |
| W1.3 | Tiered output caps | `executive_summary_repair_policy.py` | 2048 steals input | ~8K | 🔲 TODO |
| W1.4 | Judge thread preservation contract | `executive_summary_judge_regen_loop.py`, remediation | Vague "latest anchor" | ~10K | 🔲 TODO |
| W1.5 | Call plan + regen receipts + `call_id` | lane emit | Multi-call invisibility | ~10K | 🔲 TODO |
| W2.1 | Context window provenance | `executive_summary_token_budget.py` | Env ≠ server | ~12K | 🔲 TODO |
| W2.2 | Deterministic 85% first-pass | `executive_summary_token_budget.py` | Optional trim ambiguity | ~13K | 🔲 TODO |
| W3.1 | Operator guide | `executive_summary_operator_guide.md` | Docs | ~8K | 🔲 TODO |
| W3.2 | Timeout classification docs | guide + receipt field glossary | G6 runtime | ~7K | 🔲 TODO |
| W4.1 | Apps config → contract seam only | `executive_summary_same_authority_regen_bridge.py` | Core boundary | ~15K | 🔲 TODO |

---

## Gap Register

| ID | Gap | Severity | Wave |
|----|-----|----------|------|
| G1 | No mandatory regen dispatch wrapper | P0 | W1 |
| G2 | Fake-accepted regen without provider artifacts | P0 | W1 |
| G3 | Judge thread growth / vague compaction | P0 | W1 |
| G4 | Regen uses scratch `max_tokens=2048` | P1 | W1 |
| G5 | `VLLM_MAX_MODEL_LEN` unverified vs server | P1 | W2 |
| G6 | First-pass 85% policy non-deterministic | P1 | W2 |
| G7 | No run-level call plan at W1 closeout | P1 | W1 |
| G8 | Transport timeout confused with budget success | P1 | W1 |
| G9 | W4 may silently touch `agentic_core` | P2 | W4 |
| G10 | Operator docs omit token env matrix | P3 | W3 |

---

## Out Of Scope

- X1D judge thresholds, rubric content, prompt/PA changes
- PASS/ALLOW claims based on judge quality improvement
- Mocked/DEV_DEFAULT_MOCK provider paths as budget proof
- Full tokenizer unless estimates proven wrong

---

## Wave 1 — Regen-safe context (P0)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:

- **W1.0** — Introduce lane-local **`budgeted_qwen_regen_call(...)`** (single SSOT). Allocate **`call_id`** + index fields **before** budget check; write provider artifacts using deterministic naming; internally estimate thread tokens, apply regen `max_tokens`, fail-closed or delegate to `call_qwen_vllm`, append to `calls[]`. **Forbidden:** synthesis regen, judge regen, X2 repair calling `call_qwen_vllm` directly (see static bypass table).

- **W1.1** — `estimate_regen_thread_tokens(messages)` + `regen_dispatch_allowed(...)` in [executive_summary_token_budget.py](apps_rg/runtime/sections/executive_summary_token_budget.py).

- **W1.2** — Migrate **all** regen surfaces to wrapper:
  - `retry_qwen_for_synthesis` ([executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py))
  - `retry_qwen_for_judge_remediation` ([executive_summary_judge_remediation.py](apps_rg/runtime/sections/executive_summary_judge_remediation.py))
  - `repair_judge_regen_after_x2_fail` (same)

- **W1.3** — `APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS` default **1024**; enforce `regen_max_tokens <= scratch_max_tokens` in wrapper.

- **W1.4** — **Judge thread preservation contract** (reduces context; does **not** change judging contract):

  | Preserved in thread | May remove |
  |---------------------|------------|
  | Frozen system + judge rubric | Unbounded stacked full assistant JSON turns |
  | Original candidate `resume_display_text` under review | Duplicate prior regen proposals beyond latest |
  | Allowed fact packet or stable digest/ref | |
  | Prior failed **dimension IDs** + concise critique | |
  | Latest regen proposal (one assistant turn max) | |

  Add test/assertion: compaction cannot drop evidence packet, allowed fact IDs, rubric, score dimensions, or original candidate text required for faithful re-judge.

- **W1.5** — Artifacts (W1 closeout **requires** these):
  - `executive_summary_qwen_call_plan.json` — `calls[]` with **`call_id`** join key + `phase`, `cycle_index`, `attempt_index`, artifact path refs
  - `regen_token_budget_receipt.json` — **`calls[]`** only (same `call_id` values as call plan); no orphan rows
  - Per-call provider files using deterministic naming pattern (see **Regen call identity**)

**Per-call receipt fields (required on each regen record):**

`call_id`, `call_site`, `phase`, `attempt_index`, `cycle_index`, `provider_request_ref`, `provider_response_ref`, `estimated_input_tokens`, `max_output_tokens`, `reserved_tokens`, `provider_context_window`, `available_input_tokens`, `headroom_tokens`, `headroom_pct`, `dispatch_allowed`, `block_reason`, `budget_allowed`, `transport_dispatched`, `transport_timeout`, `provider_response_present`, `parse_ok`, `accepted`

**Acceptance (W1 — mandatory):**

- Every regen-capable Qwen call passes through **`budgeted_qwen_regen_call(...)`**. No direct synthesis/judge/X2 repair `call_qwen_vllm(...)` may bypass the wrapper.
- **Static bypass check** (`test_exec_summary_regen_qwen_dispatch_ssot.py`): enforce **Static bypass — allowed direct-call exceptions** table exactly (scratch single site OR wrapper-internal only for regen).
- A regen cycle may be marked **`accepted=true` only if** same **`call_id`** has matching provider response artifact, `parse_ok=true`, and rows in both `regen_token_budget_receipt.json` and `executive_summary_qwen_call_plan.json`.
- Over-budget regen must **fail closed before provider dispatch**: `dispatch_allowed=false`, `transport_dispatched=false`, `accepted=false`, explicit `block_reason`. Status **`budget_blocked`** for judge cycles. **No** synthetic `score_deltas` on block.
- **Negative test:** over-window judge regen fixture → no provider call, no accepted cycle, budget-block receipt; disposition non-ALLOW or REVIEW/BLOCK as appropriate.
- **Artifact cross-check (by `call_id`):** every accepted judge regen entry joins request + response files + parsed output + `score_deltas` via shared `call_id` (not filename glob alone).
- Judge thread compaction preserves frozen rubric/system, candidate output, fact packet/digest, dimensions, critique, latest proposal; removes unbounded assistant JSON history only.
- **W1 closeout includes** `executive_summary_qwen_call_plan.json` (W3 only polishes operator ergonomics).
- **Contract tests (one per surface):**
  - synthesis regen guard invoked
  - judge regen guard invoked
  - X2 repair regen guard invoked
  - over-budget blocks before transport
  - accepted regen requires provider response artifact
  - regen `max_tokens` defaults 1024 and never exceeds scratch cap

**Brown soak (budget proof — not judge-quality proof):**

- Requires: `REAL_LLM` (not `DEV_DEFAULT_MOCK`), canonical CLI recorded, `x3_disposition.json`, scratch + each **accepted** regen `provider_request`/`provider_response`, `executive_summary_qwen_call_plan.json`, `regen_token_budget_receipt.json`
- **Non-claim:** Claude may still soft-fail; proof is budget behavior, not all judges pass
- `proof_eligible=true` only when manifest/disposition rules allow; do not equate with judge certification

---

## Wave 2 — Capacity alignment (P1)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:

- **W2.1** — Context window provenance on `token_budget_receipt.json` and call-plan records:

  | Field | Values |
  |-------|--------|
  | `provider_context_window_source` | `ENV_VLLM_MAX_MODEL_LEN` \| `SERVER_MODELS_METADATA` \| `UNKNOWN` |
  | `server_context_window_verified` | true/false |
  | `server_context_window_warning` | set when env-only (e.g. "operator-declared, not server-proven") |

  `/v1/models` auto-detect remains **deferred**; receipt must **not** imply env is true server value unless verified.

- **W2.2** — **Deterministic** first-pass ≤85% policy (not optional):

  1. Trim **optional-only** payload (E0 examples, Y0, JD/briefing prose, optional C0 lines) — same protected set as v2 trim
  2. Recompute budget estimate
  3. If still > 85% of `available_input_tokens` → **fail closed** before scratch dispatch

  **Forbidden:** trim S0/I0/C0 proof-bearing regions, R0 schema JSON, SRFS shape markers, HIGH fact lines.

  Emit deterministic trim receipt with before/after token estimates.

**Acceptance**:

- Brown `token_budget_receipt.json` shows `provider_context_window_source` + warning when unverified
- First-pass either ≤85% after optional trim or `TOKEN_BUDGET_EXCEEDED` fail-closed with trim receipt

---

## Wave 3 — Operator ergonomics (P2)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:

- **W3.1** — Extend [executive_summary_operator_guide.md](docs/apps_rg/executive_summary_operator_guide.md): token/retry env table, receipt field glossary, Brown budget-soak command (distinct from judge-cert soak).

- **W3.2** — Document timeout vs budget: `APPS_RG_QWEN_TIMEOUT_SECONDS` recommendation (90–120 for long threads); clarify I6 invariant in operator-facing language.

**Acceptance**:

- Call plan artifact documented (implementation proof remains W1)
- No new runtime behavior in W3 unless docs-only gaps found

---

## Wave 4 — Apps-only delta policy (P2, boundary-gated)

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Boundary (mandatory):**

- Plan metadata: `touches_agentic_core: false`
- W4 **blocked** for any edit inside `agentic_core/` except consuming an **existing public** contract field on `IncrementalRepairContract` already supported by [executive_summary_same_authority_regen_bridge.py](apps_rg/runtime/sections/executive_summary_same_authority_regen_bridge.py)
- If `prompt_lock.py` or runner logic must change → stop W4, set `touches_agentic_core=true`, `core_addition_author_gate_required=true`, separate author-gate receipt — **do not** slip core changes under this apps plan

**Phases**:

- **W4.1** — Pass `max_delta_tokens` from `APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS` (default 512, max 768) **only** via apps bridge into existing contract API

**Acceptance**:

- No `agentic_core` file diff unless plan metadata escalated
- Compact dimension deltas still pass shape guard

---

## Definition of Done

| DoD ID | Criterion | Verification |
|--------|-----------|--------------|
| D1 | Wrapper + estimate + allow API + unit tests | `pytest tests/unit/apps_rg/test_executive_summary_token_budget_regen.py` |
| D2 | Regen `max_tokens` ≤ scratch; default 1024 | Wrapper + provider_request artifacts |
| D3 | Brown **budget** soak (hardened — not exit-0 alone) | REAL_LLM, call plan, regen receipts, provider artifacts; explicit non-claim if Claude fails |
| D4 | `executive_summary_qwen_call_plan.json` on real run | W1 closeout artifact |
| D5 | Plan + research on disk; Notion Plans row | `PLAN_CREATED` / `PLAN_EXISTS` |
| D6 | Static bypass matches concrete allowlist (scratch site + wrapper only) | `tests/_apps_contract/test_exec_summary_regen_qwen_dispatch_ssot.py` |
| D7 | Negative over-window: no dispatch, no accepted cycle | Unit/contract fixture |
| D8 | Accepted regen verified by **`call_id`** join across request, response, parse, score_deltas, receipts | Contract verifier |
| D9 | W4 apps-only; no unauthorized `agentic_core` diff | `git diff -- agentic_core/` empty for W4-only wave OR escalated metadata |

### Verification vs Deferral

| Item | Status | Notes |
|------|--------|-------|
| vLLM `/v1/models` auto-detect | DEFERRED | W2.1 uses labeled `provider_context_window_source` |
| Real tokenizer | DEFERRED | If estimates wrong in production |
| agentic_core 32k unify | DEFERRED | apps lane-local |
| Judge quality / all judges pass | **OUT OF SCOPE** | Budget plan only |

---

## Recommended env defaults (post-W1)

| Variable | Suggested | Notes |
|----------|-----------|-------|
| `VLLM_MAX_MODEL_LEN` | Match server (16384 or 32768) | Operator-declared unless W2.1 verified |
| `APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS` | 2048 | Scratch only |
| `APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS` | 1024 | All regen/repair via wrapper |
| `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS` | 1 prod / 3 soak | |
| `APPS_RG_QWEN_TIMEOUT_SECONDS` | 90–120 | Transport; see I6 |
| `APPS_RG_QWEN_TRANSPORT_MAX_ATTEMPTS` | 3 | Transport retries only |

---

## ADG_GRAPH_LAYER_EVIDENCE

| MV | Use |
|----|-----|
| `mv_fanin_top` | `executive_summary_token_budget.py`, lane, judge_remediation |
| `mv_fanout_top` | All `budgeted_qwen_regen_call` consumers |

---
