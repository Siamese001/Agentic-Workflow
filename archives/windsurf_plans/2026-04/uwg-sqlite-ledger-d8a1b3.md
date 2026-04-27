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
