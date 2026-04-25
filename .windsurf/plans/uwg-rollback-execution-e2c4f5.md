# UWG Rollback Execution

Plan ID: uwg-rollback-execution-e2c4f5

## Goal

Consume the `rollback_plan` carried in `X3CommitRequestPacket` and undo the L4
mutation when U5 (read-surface refresh) fails after U4 (ledger append) succeeded,
or when an operator triggers an explicit rollback.

## Scope

`agentic_core/L3_orchestration/exit_eval/v6/rollback.py`:

- `RollbackOutcome` enum: `EXECUTED`, `SKIPPED_NO_PLAN`, `FAILED`.
- `RollbackStep` and `RollbackPlan` dataclasses (validated shape).
- `RollbackHandler` protocol: `execute(step)` per step kind.
- Built-in `NoopRollbackHandler` and `SequentialRollbackExecutor` that walks
  the steps in order and aborts on the first failure.
- Hooks `process_commit_request` so a U5 failure with a rollback plan triggers
  the executor and embeds the result in the receipt.
