# Executive summary context limits SSOT — closeout

> **Plan:** [exec-summary-context-limits-ssot-b7e4a1](../../.cursor/plans/exec-summary-context-limits-ssot-b7e4a1.md)  
> **Notion:** `36c27693-f55c-81c5-bb94-cb6e67754828`  
> **SSOT module:** [executive_summary_context_limits.py](../../apps_rg/runtime/sections/executive_summary_context_limits.py)

## Summary

Consolidated executive-summary char caps, output-token defaults, reserved tokens, first-pass utilization (0.92), and `VLLM_MAX_MODEL_LEN` resolution into one apps_rg module. Consumers import resolvers instead of duplicating literals or reading env at import time.

## Changes

| Area | Before | After |
|------|--------|-------|
| Briefing/JD/bullet char caps | Scattered defaults (12k briefing in lane ingress) | `context_limits` + briefing/targeting_cap/bullet selector |
| Context window | `24576` literal in `token_budget` | `resolve_provider_context_window()` → L0 `QWEN_LOCAL_MAX_MODEL_LEN` |
| Scratch/regen max output | Duplicate `2048` in lane (import-time), regen_dispatch | `resolve_scratch_max_output_tokens()` / `resolve_regen_max_output_tokens()` |
| First-pass gate | `DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX` (0.92) | Code constant only — not env-overridable |

## Bug fixed during closeout

Removed a shadow `resolve_provider_context_window()` in `executive_summary_token_budget.py` that called `resolve_context_window_provenance()` recursively (5 test failures).

## E2E (live Brown @ 24k)

- Receipt: [exec_summary_context_limits_ssot_e2e_20260526.md](exec_summary_context_limits_ssot_e2e_20260526.md)
- Run: [exec_summary_20260526_203341](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_203341) — **X3_ALLOW**, `dispatch_allowed=true`, `provider_context_window=24576`

## Proof

```text
pytest tests/unit/apps_rg/runtime/sections/test_executive_summary_context_limits.py \
  tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py \
  tests/unit/apps_rg/runtime/sections/test_executive_summary_targeting_cap.py \
  tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py \
  tests/unit/apps_rg/test_executive_summary_token_budget_regen.py \
  tests/unit/agentic_core/L0_routing/config/test_max_model_len_ssot.py -q
→ 38 passed
```

## Out of scope (unchanged)

- Per-section lane `*_QWEN_MAX_TOKENS` (headline, unify, ibm)
- `agentic_core` repair_policy regen flags
- Mandatory new `.env` keys (catalog in `.env.example` only)
