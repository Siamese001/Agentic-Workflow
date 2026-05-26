# Executive Summary — Judge Regen Prompt Loop W2 Receipt

**Date:** 2026-05-26  
**Plan:** [exec-summary-judge-regen-prompt-loop-b9e4c3](../../.cursor/plans/exec-summary-judge-regen-prompt-loop-b9e4c3.md)  
**Run dir:** [exec_summary_20260526_084014](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_084014)  
**Baseline (pre-fix):** [exec_summary_20260526_081949](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_081949)

## Command

```powershell
$env:APPS_RG_EXEC_SUMMARY_JUDGE_PASS_FLOOR='4.2'
$env:APPS_RG_EXEC_SUMMARY_JUDGE_REGEN='1'
$env:APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN='1'
$env:VLLM_MAX_MODEL_LEN='32768'
python -m apps_rg --section executive_summary --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt `
  --provider qwen_vllm --allow-non-allow-exit-zero `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Result:** `exit_code=0`, `OPERATOR_STATUS=DRAFT_READY`, `elapsed_ms≈202399`

## W2 acceptance vs baseline

| Check | Baseline `081949` | W2 `084014` |
|-------|-------------------|-------------|
| Cycle 1 `delta_class` | `connective_S2_S5` | **`S6_forward_synthesis`** |
| REGEN delta format | `REGEN_DELTA` (stale across cycles) | **`REGEN_DELTA_v1`** with `EDIT_BUDGET` + S6-only instruction |
| Multi-cycle regen | 3 cycles (stale delta cycles 2–3) | **1 cycle** — stopped `regen_not_accepted` |
| Cycle 2 delta differs | No (byte-identical) | N/A (no cycle 2) |

## Root cause of early stop (fixed 2026-05-26)

[judge_remediation_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_084014/judge_remediation_receipt.json) (pre-fix):

- `finish_reason: length` at `max_output_tokens=1024` — JSON truncated mid-`self_check`
- `parse_ok: false` — `Unterminated string`
- `output_changed: false` — parse failure left `resume_display_text` at scratch anchor

**Fixes:** regen default `max_output_tokens` 1024→2048; `salvage_truncated_executive_summary_json`; core-runner parse fail falls back to `thread_append`; budget ledger `parse_ok` uses real JSON parse.

Prompt-loop routing **did** fire correctly before the parse failure.

## Verifier outputs

- [exec_summary_regen_prompt_loop_w2_verify_20260526.json](exec_summary_regen_prompt_loop_w2_verify_20260526.json) — `cycle1_delta_class_s6: true`
- W5 artifact checklist — `passed: true` on `084014`

## Status

**PARTIAL** — Primary W2 hypotheses proven (S6 class + prescriptive delta). Multi-cycle thread/delta-diff proof deferred until Qwen regen returns parseable JSON (operator re-run or parse-repair seam).
