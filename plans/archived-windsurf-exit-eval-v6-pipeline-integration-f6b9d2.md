---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\exit-eval-v6-pipeline-integration-f6b9d2.md'
original_relative_path: 'exit-eval-v6-pipeline-integration-f6b9d2.md'
source_sha256: 65f9e9209126520dd3cc36ee8f8fed1acb4c6ce743d97291b770eee45c6a5357
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Exit Eval v6 — End-to-End Pipeline Integration

Plan ID: exit-eval-v6-pipeline-integration-f6b9d2

## Goal

Single entry point that takes raw runtime receipts and returns the final X3
disposition packet plus an optional UWG receipt for commit paths.

## Scope

`agentic_core/L3_orchestration/exit_eval/v6/pipeline.py`:

- `ExitEvalPipeline` orchestrator with optional `UwgBackends`.
- `run_exit_eval(receipts) -> ExitEvalResult` glue:
  1. `validate_required_receipts` -> if any failure, build X3A immediately.
  2. `bind_run_identity` -> if mismatch, build X3A.
  3. `normalize_to_packet` -> ExitReviewPacket.
  4. `run_all_x1_gates` -> 10 verdicts.
  5. `aggregate_decision` -> X2 decision.
  6. `build_x3_packet` -> the X3* packet.
  7. If COMMIT_REQUEST -> call `process_commit_request` and merge UwgReceipt.
- `ExitEvalResult` dataclass: `disposition`, `x3_packet`, `verdicts`, `decision`,
  `uwg_receipt`, `preflight_failures`.
