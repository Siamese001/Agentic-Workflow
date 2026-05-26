# Executive summary claim-coverage hardening — W4 live receipt

> **Plan:** [exec-summary-claim-coverage-hardening-a1f3e8.md](../../.cursor/plans/exec-summary-claim-coverage-hardening-a1f3e8.md)  
> **RCA baseline:** [exec_summary_20260526_183905](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_183905) (X3_BLOCK on X2)  
> **W4 live run:** [exec_summary_20260526_191701](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701)

## Command

```powershell
$env:VLLM_MAX_MODEL_LEN = '24576'
$env:APPS_RG_EXEC_SUMMARY_VERIFY_VLLM_CONTEXT_WINDOW = '1'

python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd_exec.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md
```

- **Elapsed:** ~258s  
- **vLLM preflight:** `max_model_len=24576` (`SERVER_MODELS_METADATA`)  
- **Exit:** 0 (lane `COMMAND_PASS_PRODUCT_REVIEW_OR_BLOCK`; not proof-eligible ALLOW)

## Plan acceptance vs RCA run

| Check | RCA `183905` | W4 `191701` |
|-------|----------------|-------------|
| `dispatch_allowed` / 24k budget | true (~59% util) | true (59.48% util) |
| `x2_unsupported_claim_zero` | **FAIL** (S5 false UNSUPPORTED) | **PASS** |
| `x2_sentence_coverage_pass` | FAIL | **PASS** |
| `x2_claim_ledger_row_count_matches_sentence_count` | n/a (pre-W1) | **PASS** (6 sentences, 6 ledger rows) |
| `x2_self_check_claim_ledger_consistent` | n/a | **PASS** |
| `product_quality_status` | FAIL | **PASS** |
| `x1d_llm_judge_outputs.json` | `{"judges": []}` (panel skipped) | **3 judges** (panel ran) |
| `x1d_evaluator_mode` | `BLOCKED_PROVIDER_UNAVAILABLE` (misleading) | `MODEL_BACKED` |
| `x3_code` | `X3_BLOCK` (X2) | `X3_REVIEW_JUDGE_SOFT_FAIL` (`anthropic_claude` below threshold) |

### S5 (W0 target)

Sentence 5 in [text_claim_coverage.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701/text_claim_coverage.json):

- **Display:** quantitative rigor / capital and risk analytics paraphrase  
- **Support:** `SUPPORTED` via `fact_quant_hpc_003`  
- **Not** the pre-W0 false UNSUPPORTED on fact wording alone.

### S6 / W1

- Model emitted **6** `claim_ledger` rows (including forward capstone).  
- W1 row-count and self_check gates **PASS**.  
- **Note:** Coverage still binds S6 to the **credentials** row (`fact_certs_001`) via token overlap — a separate matcher-quality gap; it does not reproduce the RCA “no ledger row” failure mode.

## Key artifacts

| Artifact | Link |
|----------|------|
| Run root | [exec_summary_20260526_191701](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701) |
| [token_budget_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701/token_budget_receipt.json) | 24k verified, `dispatch_allowed: true` |
| [text_claim_coverage.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701/text_claim_coverage.json) | `overall_pass: true` |
| [x2_gate_outputs.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701/x2_gate_outputs.json) | `x2_failed_gates: []` |
| [x3_disposition.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701/x3_disposition.json) | `X3_REVIEW_JUDGE_SOFT_FAIL` |
| [x1d_llm_judge_outputs.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701/x1d_llm_judge_outputs.json) | gemini + openai pass; anthropic soft-fail |
| [parsed_output.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701/parsed_output.json) | REAL_LLM JSON |

## Waves shipped (code)

| Wave | Summary |
|------|---------|
| W0 | Display `claim` + fact `claim_text` coverage matcher |
| W1 | Row-count, self_check cross-check, claim-field materialization gates |
| W2 | `NO_JUDGE_ROWS_EMITTED` when judge list empty |
| W3 | Brown fixture + contract tests |
| W4 | This live run |

## Status

**PARTIAL** for full product certification (`X3_ALLOW` / all judges pass). **PASS** for the claim-coverage hardening plan scope: S5 checker bug fixed in production path, W1 gates live, judges ran after clean X2, X3 label honest when judges absent.

**Remaining (out of plan):** S6→wrong-row coverage binding; anthropic judge threshold; optional sixth-row semantic quality in prompts.
