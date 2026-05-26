# Executive summary context limits SSOT — E2E receipt (2026-05-26)

> **Plan:** [exec-summary-context-limits-ssot-b7e4a1](../../.cursor/plans/exec-summary-context-limits-ssot-b7e4a1.md)  
> **Closeout:** [executive_summary_context_limits_ssot_closeout_20260526.md](executive_summary_context_limits_ssot_closeout_20260526.md)

## Layer 1 — Unit (SSOT seam)

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest `
  tests/unit/apps_rg/runtime/sections/test_executive_summary_context_limits.py `
  tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py `
  tests/unit/apps_rg/runtime/sections/test_executive_summary_targeting_cap.py `
  tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py `
  tests/unit/apps_rg/test_executive_summary_token_budget_regen.py `
  tests/unit/agentic_core/L0_routing/config/test_max_model_len_ssot.py -q
```

| Result | Detail |
|--------|--------|
| **38 passed** | ~1.3s |

## Layer 2 — Live Brown SVP @ 24k (post-SSOT)

**Pre:** `local-qwen-vllm` up, `max_model_len=24576`

```powershell
$env:VLLM_MAX_MODEL_LEN = '24576'
$env:APPS_RG_EXEC_SUMMARY_VERIFY_VLLM_CONTEXT_WINDOW = '1'
$env:APPS_RG_QWEN_TIMEOUT_SECONDS = '120'

python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd_exec.txt `
  --provider qwen_vllm `
  --allow-non-allow-exit-zero `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md
```

| Run | Artifact | X3 | Token budget |
|-----|----------|-----|----------------|
| [exec_summary_20260526_203341](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_203341) | ~169s | **X3_ALLOW** | `provider_context_window=24576`, `dispatch_allowed=true`, `first_pass_utilization_pct=59.48` (cap 92% → 20254) |

**SSOT proofs in artifact:**

| Check | Value |
|-------|--------|
| `token_budget_receipt.json` → `provider_context_window` | **24576** |
| `requested_max_output_tokens` | **2048** (SSOT scratch default) |
| `first_pass_input_utilization_max` | **0.92** |
| `targeting_context_parity_receipt.json` → `parity_match` | **true** |
| `generation_briefing_chars` | **2491** (full exec briefing ingress, not legacy 12k trim) |
| `executive_summary_qwen_call_plan.json` | `provider_context_window=24576` on all calls |

## E2E verdict

| Scope | Status |
|-------|--------|
| Context limits SSOT (code + unit) | **PASS** |
| Live 24k dispatch + budget | **PASS** |
| Product X3 on this run | **PASS** (`X3_ALLOW`) |
