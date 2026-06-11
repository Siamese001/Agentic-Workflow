---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-gates-baseline-bootstrap-f1a2b3.md'
original_relative_path: 'runtime-gates-baseline-bootstrap-f1a2b3.md'
source_sha256: 99eab83f2aefa9cd6a4bfadb392773139d14c4e0cffeae29b5a465c3baaf4059
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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
