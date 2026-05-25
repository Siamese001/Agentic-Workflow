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
