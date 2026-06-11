---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\uwg-sqlite-ledger-d8a1b3.md'
original_relative_path: 'uwg-sqlite-ledger-d8a1b3.md'
source_sha256: 2d0919cf7a80af6ce70a7b8623d248a3d28c921687ccef9c84d1abaf89c7cc4d
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# UWG SQLite Ledger

Plan ID: uwg-sqlite-ledger-d8a1b3

## Goal

Replace `InMemoryLedger` with a durable SQLite-backed ledger that survives
process restart and supports cross-process hash-chain consistency.

## Scope

`agentic_core/L3_orchestration/exit_eval/v6/sqlite_ledger.py`:

- `SqliteLedger(path, *, table='uwg_ledger')` implementing `LedgerProtocol`.
- Schema: `(seq INTEGER PRIMARY KEY, prev_hash, commit_request_id, payload_json, hash, created_at)`.
- `WAL` journal mode for concurrent readers.
- `head_hash()` reads the highest-seq row.
- `entries()` snapshot for tests/audit.
- `head_seq()` for fast count.
