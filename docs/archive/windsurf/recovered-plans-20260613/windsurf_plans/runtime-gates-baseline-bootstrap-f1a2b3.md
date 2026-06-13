# Runtime Gates — BaselineRegistry Bootstrap

Status: In Progress
Plan ID: runtime-gates-baseline-bootstrap-f1a2b3

## Goal

Seed `BaselineRegistry` from historical OTEL trace data so G25 RuntimeAnomaly
gate has meaningful baselines from session start instead of cold.

## Approach

CLI tool `tools/runtime_gates/bootstrap_baselines.py`:

- Read trace records from a JSON / JSONL file or directory of files.
- Each record carries `task_class`, `tokens`, `cost_usd`, `latency_ms`,
  `tool_count`, `retry_count` (subset OK).
- Run them through `BaselineRegistry.update()` — first sample seeds, rest
  EMA-blend with the registry's configured alpha.
- Persist to a target JSON file via the registry's atomic write.

## Wave Structure

| Wave | Phase | Focus | Status |
|---|---|---|---|
| W1 | 1.1 | Bootstrap tool | Done |
| W2 | 2.1 | Tests | Done |
| W3 | 3.1 | Commit + push | Done |

## Out of Scope

- Live OTEL ingest — handled by the runtime feed in production. This tool
  bootstraps the registry from a saved trace dump.
