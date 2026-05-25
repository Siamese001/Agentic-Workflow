# Brown Live Proof — Judge Regen Loop Closure

**Plan:** [exec-summary-judge-regen-loop-closure-d8f3a1.md](../../.cursor/plans/exec-summary-judge-regen-loop-closure-d8f3a1.md)  
**Parent:** [core-same-authority-incremental-regen-e7a4b1.md](../../.cursor/plans/core-same-authority-incremental-regen-e7a4b1.md) (chassis COMPLETED)  
**Run:** `exec_summary_20260525_124637`  
**Date:** 2026-05-25

## STATUS: PASS (DoD-5 + DoD-6)

## Command

```bash
set APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1
set APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN=1
python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --provider qwen_vllm --allow-non-allow-exit-zero --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Exit code:** 0

## Loop closure (DoD-5)

| Check | Evidence |
|-------|----------|
| Core regen PASS | [same_authority_regen_receipt.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_124637/same_authority_regen_receipt.json) `accepted: true` |
| Cycle accepted | [judge_remediation_cycles.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_124637/judge_remediation_cycles.json) `cycles[0].accepted: true`, no `reverted` |
| No post-regen X2 revert | `stopped_reason: max_cycles_reached` (not `post_regen_x2_failed_*`) |

## Ordering proof (DoD-6)

1. [x2_gate_outputs_pre_regen.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_124637/x2_gate_outputs_pre_regen.json) — snapshot before regen (`snapshot_label: pre_regen`)
2. Same-authority regen + [judge_regen_prepare_receipt.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_124637/judge_regen_prepare_receipt.json)
3. [x2_gate_outputs_post_regen.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_124637/x2_gate_outputs_post_regen.json) — `x2_failed: 0`, `failed_gates: []`
4. [post_regen_x1d_rescore_receipt.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_124637/post_regen_x1d_rescore_receipt.json) — judge rescore after post-regen X2 green

## W4 snapshots

| Artifact | Present |
|----------|---------|
| `x2_gate_outputs_pre_regen.json` | yes |
| `x2_gate_outputs_post_regen.json` | yes |

## Honest limits

- `all_judges_pass: false` after one cycle — acceptable per plan (X3 REVIEW tier; operator-ship deferred).
- First Brown attempt `124058` failed loop closure (coverage monotonicity); fixed via ledger preserve + snapshot writer + shape-only X2 repair gate.

## Patch summary (this session)

- [executive_summary_judge_regen_loop.py](../../../apps_rg/runtime/sections/executive_summary_judge_regen_loop.py): named X2 snapshots; `preserve_judge_regen_claim_ledger_from_baseline`
- [executive_summary_lane.py](../../../apps_rg/runtime/sections/executive_summary_lane.py): preserve after prepare; gate `repair_judge_regen_after_x2_fail` to shape-only failures
- [executive_summary_synthesis_monotonic.py](../../../apps_rg/runtime/sections/executive_summary_synthesis_monotonic.py): coverage gate IDs → evidence-weave monotonicity context
