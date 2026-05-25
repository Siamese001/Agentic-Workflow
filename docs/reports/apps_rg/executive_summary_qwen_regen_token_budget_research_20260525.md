# Executive Summary — Qwen Token Budget Research (Regen & Retries)

**Date:** 2026-05-25  
**Plan:** [exec-summary-qwen-regen-token-budget-c4e8a1.md](../../.cursor/plans/exec-summary-qwen-regen-token-budget-c4e8a1.md)  
**Prior work:** [executive_summary_token_budget_waves_closeout_receipt.md](executive_summary_token_budget_waves_closeout_receipt.md) (first-call trim only)  
**Hardening:** Plan hardened 2026-05-25 — mandatory `budgeted_qwen_regen_call` wrapper, artifact-backed acceptance, W1 ships `executive_summary_qwen_call_plan.json`, scope locked to transport/budget only (not judge quality).

---

## Executive summary

Token policy for `apps_rg` executive summary is **strong for the first Qwen call** but **does not budget regen/retry traffic**. Brown proofs fill **~91–95%** of the 16k input window on scratch generation; synthesis and judge regen then **append assistant JSON and repair blocks** to `messages[]` with the same **2048** output cap, risking context overflow, transport timeouts, and (historically) regen cycles marked accepted without an LLM rewrite.

---

## Findings

### 1. First-call budget (working)

- SSOT: [executive_summary_token_budget.py](../../apps_rg/runtime/sections/executive_summary_token_budget.py)
- Formula: `available_input = VLLM_MAX_MODEL_LEN - max_output - 512`
- Estimator: `len(text)/3 × 1.12` (labeled approximate in receipt)
- Optional trim: E0, Y0, JD/briefing prose, optional C0 fact lines — never I0/R0/evidence contract

**Brown example** ([exec_summary_20260525_132429](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_132429/token_budget_receipt.json)):

| Field | Value |
|-------|-------|
| `provider_context_window` | 16384 |
| `requested_max_output_tokens` | 2048 |
| `available_input_tokens` | 13824 |
| `compiled_prompt_tokens_after_trim` | 12625 |
| Headroom (estimate) | ~1199 |

### 2. Output cap (scratch — adequate)

- `APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS` default **2048** ([executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py) L38–40)
- Replaced stale `build_qwen_request` default of **700**
- Typical completion (6 sentences + `claim_ledger` + `self_check` + `executive_strategy_thesis`): ~800–1400 tokens

### 3. Regen paths (ungoverned input)

| Path | Max calls | Context growth |
|------|-----------|----------------|
| Scratch | 1 | System compile only |
| Synthesis regen | +2 | `messages` + assistant + repair user ([retry_qwen_for_synthesis](../../apps_rg/runtime/sections/executive_summary_lane.py)) |
| Judge regen | +3 cycles | Thread += assistant each cycle ([extend_regen_thread_after_success](../../apps_rg/runtime/sections/executive_summary_judge_regen_loop.py)) |
| Judge X2 repair | +0–3 | Long synthesis repair user on `_regen_messages` |

**No** second pass of `apply_executive_summary_token_budget_policy()` before regen dispatch.

### 4. Core same-authority delta (512 tokens)

- Separate from vLLM context: [DEFAULT_MAX_DELTA_TOKENS = 512](../../agentic_core/L2_execution/regen/prompt_lock.py)
- Bloated prescriptive deltas caused `delta_token_budget_exceeded`; compact dimension-only deltas + thread fallback mitigate (2026-05-25)

### 5. Context window documentation drift

| Source | Default |
|--------|---------|
| apps_rg `VLLM_MAX_MODEL_LEN` | 16384 |
| agentic_core `QWEN_MAX_MODEL_LEN` | 32768 |

Operators must set env to match **actual** vLLM deployment.

### 6. Transport vs semantic retries

- `APPS_RG_QWEN_TRANSPORT_MAX_ATTEMPTS` default **3** per HTTP completion ([qwen_transport_diag.py](../../apps_rg/runtime/qwen_transport_diag.py))
- Independent of synthesis/judge **semantic** attempt caps

---

## Gaps (prioritized)

| ID | Gap | Severity |
|----|-----|----------|
| G1 | No input budget on regen threads | P0 |
| G2 | Judge regen stacks full system + growing chat | P0 |
| G3 | Regen uses scratch `max_tokens=2048` | P1 |
| G4 | 16k vs 32k SSOT mismatch | P1 |
| G5 | Core `max_delta_tokens` not apps-env tunable | P2 |
| G6 | 60s timeout on long regen | P2 |
| G7 | No per-run Qwen call plan artifact | P2 |
| G8 | Operator guide missing token env table | P3 |

---

## Remediation waves (summary)

See plan [exec-summary-qwen-regen-token-budget-c4e8a1.md](../../.cursor/plans/exec-summary-qwen-regen-token-budget-c4e8a1.md).

1. **W1** — `estimate_regen_thread_tokens`, fail-closed regen guard, `APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS=1024`, judge thread cap  
2. **W2** — Align `VLLM_MAX_MODEL_LEN`; first-pass ≤85% fill policy  
3. **W3** — `executive_summary_qwen_call_plan.json` + operator guide  
4. **W4** — Optional apps env for `max_delta_tokens` (≤768)

---

## Proof artifacts & tools

- Per-run: `token_budget_receipt.json` (first call only today)
- Analysis: [analyze_judge_regen_score_trajectory.py](../../ops_scripts/apps_rg/analyze_judge_regen_score_trajectory.py)
- Contract: [test_executive_summary_token_budget_contract.py](../../tests/_apps_contract/test_executive_summary_token_budget_contract.py)

---

## Recommended env (target state)

```text
VLLM_MAX_MODEL_LEN=16384          # or 32768 if server supports it
APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS=2048
APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS=1024   # proposed
APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS=1        # 3 for soak
APPS_RG_QWEN_TIMEOUT_SECONDS=90
APPS_RG_QWEN_TRANSPORT_MAX_ATTEMPTS=3
```

---

## Non-claims

- Not a PASS on full judge certification (X3/X1D unchanged)
- Not proof that 2048 is insufficient for scratch (no systematic `finish_reason=length` evidence in sampled runs)
