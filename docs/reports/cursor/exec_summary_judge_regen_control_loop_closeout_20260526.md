# Closeout — Executive Summary Judge Regen Control Loop

**Plan:** [exec-summary-judge-regen-control-loop-f8a3c2.md](../../.cursor/plans/exec-summary-judge-regen-control-loop-f8a3c2.md)  
**Date:** 2026-05-26  
**Canonical live run:** [exec_summary_20260526_080609](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_080609)

## North star (achieved)

Judge-directed regen is closed-loop control: cycles are accepted only on measured improvement gates; publish selects the best frozen candidate; receipts never imply success on `output_changed` alone.

## Waves delivered

| Wave | Focus | Status |
|------|--------|--------|
| W0 | Plan lock + Notion + traceability | DONE |
| W1 | G3 trigger-judge monotonicity | DONE |
| W2 | G1 ledger metric sync (fail-closed) | DONE |
| W3 | `CandidateSnapshot` pool + best-of publish | DONE |
| W4 | schema v2, `delta_class`, G5, stderr | DONE |
| W5 | Canonical CLI proof + closeout | DONE |

## W5.0 — Canonical CLI (PASS)

**Command** (floor 4.2, judge regen on):

```text
APPS_RG_EXEC_SUMMARY_JUDGE_PASS_FLOOR=4.2
APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1
APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN=1
VLLM_MAX_MODEL_LEN=32768
python -m apps_rg --section executive_summary --target-company "Brown & Brown" ...
```

**Result:** `exit_code=0`, `artifact_dir_workspace=artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_080609`

**Verifier:** [verify_exec_summary_judge_regen_w5_artifacts.py](../../tools/cursor/verify_exec_summary_judge_regen_w5_artifacts.py) → `passed: true` (all § W5.0 artifacts present)

| Check | Live value |
|-------|------------|
| `judge_remediation_cycles.json` `schema_version` | `2` |
| `final_publish_baseline` | `scratch` |
| `regen_outcome` | `no_acceptable_candidate` |
| `publish_integrity_receipt` digests match | yes |
| Operator disposition | `DRAFT_READY` (floor 4.2 not met — expected) |

**Live control-loop behavior:** All three regen cycles rejected with `reject_gate=delta_scope_violation` (G5 — 6/6 sentences edited vs `connective_S2_S5` budget 4). Scratch published via pool argmax. Stderr: `Judge regen cycle 1 rejected: delta_scope_violation (floor 4.2). Published scratch`.

**Motivating Brown regression (070105):** Pre-plan cycle accepted Claude 4.0→3.6; post-plan paths reject via G3/G5/pool (unit + fixture tests).

## W5.1 — Floor matrix (optional)

Not run in this closeout (3× live runs ~2h). Helper updated: [run_exec_summary_floor_matrix.py](../../tools/cursor/run_exec_summary_floor_matrix.py). Plan PASS does not require matrix alone.

## H-9 — No `agentic_core` diff

Receipt: [no_agentic_core_diff_receipt.json](no_agentic_core_diff_receipt.json) — `agentic_core_files_changed: []`, `passed: true`

## Test evidence (unit)

```text
pytest tests/unit/apps_rg/test_executive_summary_judge_remediation.py
     tests/unit/apps_rg/test_executive_summary_g1_ledger_metric_sync.py
     tests/unit/apps_rg/test_executive_summary_candidate_pool.py
     tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py
     tests/unit/apps_rg/test_executive_summary_judge_regen_loop.py
     tests/unit/ops_scripts/cursor/test_verify_exec_summary_judge_regen_w5_artifacts.py
→ 44+ passed (2026-05-26)
```

## Key artifacts (canonical run)

- [judge_remediation_cycles.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_080609/judge_remediation_cycles.json)
- [candidate_pool_summary.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_080609/candidate_pool_summary.json)
- [publish_integrity_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_080609/publish_integrity_receipt.json)
- [exec_summary_judge_regen_w5_verify_receipt.json](exec_summary_judge_regen_w5_verify_receipt.json)

## Receipts by wave

- [w0](exec_summary_judge_regen_control_loop_w0_receipt.md) · [w1](exec_summary_judge_regen_control_loop_w1_receipt.md) · [w2](exec_summary_judge_regen_control_loop_w2_receipt.md) · [w3](exec_summary_judge_regen_control_loop_w3_receipt.md) · [w4](exec_summary_judge_regen_control_loop_w4_receipt.md) · [w5](exec_summary_judge_regen_control_loop_w5_receipt.md)

## Sibling handoff

[exec-summary-failed-run-persistence-notion-e7c4b2.md](../../.cursor/plans/exec-summary-failed-run-persistence-notion-e7c4b2.md) should mirror publish selection from `candidate_pool_summary.json` / cycles v2 only — no parallel selector.
