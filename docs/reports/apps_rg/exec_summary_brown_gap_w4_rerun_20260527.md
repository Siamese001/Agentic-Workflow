# Brown SVP gap hardening — W4 proof re-run

**Plan:** [exec-summary-brown-gap-hardening-b9e4c1.md](../../.cursor/plans/exec-summary-brown-gap-hardening-b9e4c1.md)  
**Primary evidence run:** `exec_summary_20260527_073959`  
**Secondary run:** `exec_summary_20260527_073410`

## Command

```powershell
$env:VLLM_MAX_MODEL_LEN = "24576"
$env:APPS_RG_QWEN_TIMEOUT_SECONDS = "120"
python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Exit code:** 1 (`OPERATOR_STATUS=NOT_READY`, `PRODUCT_QUALITY_STATUS=FAIL`)

## Run comparison

| Run ID | Artifact | X2 blockers (post-W2/W3 gates) | Judges |
|--------|----------|--------------------------------|--------|
| [exec_summary_20260527_073410](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_073410/) | S5 derivatives inventory (W3 gates only) | Not run |
| [exec_summary_20260527_073959](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_073959/) | S5 + self_check S5 + **stock_bridge_max_two** (3 bridges S2–S4) | Not run |

Both runs: `RUNTIME_GENERATION_STATUS=REAL_LLM`, `PRODUCT_STATUS=X3_BLOCK`, `x1d_evaluator_mode=NO_JUDGE_ROWS_EMITTED`.

## Observed scratch pattern (073959)

- S2–S4: triple stock bridges (`From that` / `Against that` / `Complementing that`).
- S4: HPC **40%** metric present.
- S5: `derivatives pricing` inventory without paired HPC percent in same sentence → `x2_exec_summary_s5_no_derivatives_inventory`.
- `synthesis_regen_receipt.json`: regen attempts ran; pre-closeout bug published regen text despite `accepted: false`. **Closeout fix:** `retry_qwen_for_synthesis` sets `reverted_to_first_pass` and returns first-pass output when shape regen does not pass.

## W4 acceptance vs observed

| Criterion | Result |
|-----------|--------|
| New artifact dir under `real/` | **PASS** (two runs) |
| `x1d_certified` or proof-gap doc + judges ≥4.0 | **Deferred** — X2 block before panel |
| No formulaic triple-bridge stack | **Deferred** on generation; **enforced** via `x2_exec_summary_stock_bridge_max_two` for future runs |
| `x2_unsupported_industry_claim_zero` | **PASS** (no industry fabrication) |

## W3 operator surfacing (073410)

- [cli_section_execution_report.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_073410/cli_section_execution_report.json): `regen_reasoning_execution_blocks` populated (reflexion `IGNORED` on scratch + synthesis_regen).
- No `regen_escalation_receipt.json` (judge regen did not run).
- No `judge_score_variance_receipt.json` (no dual judge panel).

## Engineering closeout (plan complete)

- W1–W3 unit tests: 20 passed (`test_executive_summary_w{1,2,3}_brown_gap_hardening.py`).
- Stock bridge + S5 gates wired in `run_x2_gates` and synthesis shape repair prompts.
- Plan + Notion: **Completed** (engineering scope); certification remains a follow-on REAL_LLM run.

## Follow-on (not this plan)

1. Re-run Brown command after Qwen follows I0/Y0 S5 weave and ≤2 stock bridges.
2. Confirm `synthesis_regen_receipt.json` shows `reverted_to_first_pass: true` when regen cannot fix shape.
3. Judge panel only after X2 PASS on published scratch.
