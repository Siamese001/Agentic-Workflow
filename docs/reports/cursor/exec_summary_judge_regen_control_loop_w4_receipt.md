# W4 Receipt — Receipts + Narrow Deltas

**Plan:** [exec-summary-judge-regen-control-loop-f8a3c2.md](../../.cursor/plans/exec-summary-judge-regen-control-loop-f8a3c2.md)  
**Wave:** W4 (H-8, G5, delta_class, operator stderr)  
**Date:** 2026-05-26

## Summary

- `judge_remediation_cycles.json` now emits **schema v2** (`schema_version: 2`) with `delta_class`, `regen_outcome`, `cert_publish_guard`, and publish digests.
- **G5** `evaluate_g5_delta_scope` rejects over-broad sentence edits per `delta_class` budget.
- Default regen delta lines no longer mandate full S2–S6 rewrite unless `APPS_RG_EXEC_SUMMARY_EXPLORATORY_FULL_PARAGRAPH_REGEN=1`.
- Operator **stderr one-liner** on G3/G5 reject and after publish finalize.
- Floor matrix helper adds `reject_gate`, `publish_baseline`, `regen_outcome`, `published_candidate_digest`.

## Files

- [executive_summary_regen_delta_policy.py](../../apps_rg/runtime/sections/executive_summary_regen_delta_policy.py) — new
- [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py)
- [executive_summary_judge_remediation.py](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py)
- [executive_summary_repair_policy.py](../../apps_rg/runtime/sections/executive_summary_repair_policy.py)
- [run_exec_summary_floor_matrix.py](../../tools/cursor/run_exec_summary_floor_matrix.py)
- [test_executive_summary_regen_delta_policy.py](../../tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py)

## Proof

```text
pytest tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py -q -o addopts= → 11 passed
pytest tests/unit/apps_rg/test_executive_summary_candidate_pool.py -q -o addopts= → 8 passed
```

## Caveats

- Plan PASS still requires **W5** canonical CLI Brown proof (INV-6).
- v1 cycle receipts remain read-only legacy; new runs emit v2 only.
