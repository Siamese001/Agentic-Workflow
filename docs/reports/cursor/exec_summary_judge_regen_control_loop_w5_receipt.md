# W5 Receipt — Live Proof + Closeout

**Plan:** [exec-summary-judge-regen-control-loop-f8a3c2.md](../../.cursor/plans/exec-summary-judge-regen-control-loop-f8a3c2.md)  
**Wave:** W5 (H-7, H-9)  
**Date:** 2026-05-26

## Canonical CLI

**Run dir:** [exec_summary_20260526_080609](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_080609)  
**Exit:** `0` (~230s)  
**Verifier:** `python tools/cursor/verify_exec_summary_judge_regen_w5_artifacts.py <run_dir>` → **passed**

## Highlights

- `schema_version: 2`, `final_publish_baseline: scratch`, `regen_outcome: no_acceptable_candidate`
- All regen cycles: `publish_eligible: false`, `reject_gate: delta_scope_violation` (G5)
- `publish_integrity_receipt.json`: digests match

## Closeout

- [exec_summary_judge_regen_control_loop_closeout_20260526.md](exec_summary_judge_regen_control_loop_closeout_20260526.md)
- [no_agentic_core_diff_receipt.json](no_agentic_core_diff_receipt.json)

## W5.1

Floor matrix aggregation not executed (optional index).
