---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\adg-phase1-phase2-closure-2026-04-19.md'
original_relative_path: 'adg-phase1-phase2-closure-2026-04-19.md'
source_sha256: 1688400d071d01c96b6d9dec3c0c018c195b2d257ceb387ee514ca0ab539603e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG MCP Phase 1 + Phase 2 Closure Report (2026-04-19)

## Scope and Guardrails
- Objective: complete 2-phase blocker closure sequence and end with a single aligned GO/NO-GO decision.
- Constraint enforcement: no production P1 remediation edits in this closure run.
- Snapshot truth requirement: runtime MCP tools and ingest/runtime resolver paths must converge on one authoritative snapshot.

## Phase 1 — Canonical Run Completion
- Canonical entrypoint executed: `python tools/generate/generate_full_adg.py`.
- Fresh successful completion proof: exit code `0` on run producing `adg_indexed_04192026_0728.sqlite`.
- Post-commit P0 integration path used current-run sqlite source via:
  - `tools/generate/generate_full_adg.py::_resolve_post_commit_sqlite()`
  - `tools/generate/integration/p0_wave_plan.py::_emit_p0_remediation_wave_plan(..., sqlite_path=prod_sqlite_path)`
  - `tools/adg/core/p0_wave_plan.py::build_p0_remediation_wave_plan(sqlite_path, ...)`
- Fail-fast schema guard already active and validated in `tools/generate/validation/integrity.py::_check_sqlite_integrity()`:
  - requires tables: `nodes`, `edges`, `violations`, `meta`.
- No `sqlite3.OperationalError: no such table: nodes` observed during successful end-to-end completion.

## Phase 2 Authority Alignment (Implementation Evidence)

### Resolver authority (single source of truth)
- `tools/adg/shared_modules/path_resolver.py`
  - `latest_sqlite()` now filters snapshot candidates to valid `%m%d%Y_%H%M` IDs.
  - Selection uses `max(valid_files, key=mtime)`.
  - Synthetic/sentinel names (for example `adg_indexed_99999999_9999.sqlite`) are excluded.

### Runtime/MCP path wiring
- `tools/adg/core/sqlite_backend.py`
  - `_connect()` obtains active snapshot via `latest_sqlite()`.
  - `health()` compares current path with `latest_sqlite()` to determine staleness.
- `tools/adg/core/service.py`
  - Service snapshot ID is sourced from SQLite status timestamp.
  - `reopen()` refreshes `_adg_snapshot_id` after SQLite reopen to keep cache-key namespace aligned.
- `tools/adg/mcp/tool_handlers.py`
  - `adg_health` and `adg_status` call `runtime.reload_latest_snapshot()` before returning data.

### Redis ingest path wiring
- `tools/adg/adg_redis_ingest.py`
  - `_find_latest_sqlite()` uses the same valid-timestamp filtering and mtime-based latest selection logic.

### Reporting/burndown path wiring (final drift fix)
- `tools/generate/reporting/reports.py`
  - `_resolve_reporting_sqlite()` now uses shared `latest_sqlite()` from `tools/adg/shared_modules/path_resolver.py`.
  - This removes sentinel contamination in mismatch detection (`adg_indexed_99999999_9999.sqlite` no longer treated as authoritative latest).

## Targeted Verification

### Unit tests (snapshot alignment)
- Test file: `tests/unit/tools/adg/test_snapshot_selection_alignment.py`
- Result: `3 passed`.
- Coverage of risks:
  - `test_latest_sqlite_ignores_invalid_timestamp_files`
  - `test_redis_ingest_finds_latest_valid_snapshot`
  - `test_sqlite_backend_connect_uses_latest_valid_snapshot`

### Unit tests (post-commit sqlite + reporting mismatch)
- Test slice: `tests/unit/tools/generate/test_generate_full_adg_failfast.py -k "PostCommitSqliteResolution or BurndownProvenance or P0TwoPassRunnerIntegration"`
- Result: `10 passed`.
- Additional post-fix slice: `-k "BurndownProvenance"`.
- Result: `3 passed`.

### Live MCP alignment checks
- `adg_health`
  - mode: `full`
  - sqlite: `healthy`
  - redis: `healthy`
  - `adg_snapshot_id`: `04192026_0728`
  - sqlite path: `artifacts/adg/adg_indexed_04192026_0728.sqlite`
- `adg_status`
  - timestamp: `04192026_0728`
  - sqlite path: `artifacts/adg/adg_indexed_04192026_0728.sqlite`
- `adg_runtime_info`
  - snapshot_id: `04192026_0728`
  - sqlite_path: `artifacts/adg/adg_indexed_04192026_0728.sqlite`
- `adg_reload`
  - response: `Already using latest snapshot.`

### Confirmatory rebaseline (aligned snapshot)
- Burndown provenance source: `adg_indexed_04192026_0728.sqlite`
- `source_mismatch_with_latest`: `false`
- P0: net `0`, guardian `0`, gross `0`
- P1: net `505`, guardian `463`, gross `968`
- P2: net `1220`, guardian `362`, gross `1582`
- P1 by kind (gross / guardian / net):
  - `log_and_swallow`: `532 / 294 / 238`
  - `return_none_swallow`: `167 / 26 / 141`
  - `silent_exception_swallow`: `113 / 39 / 74`
  - `broad_exception_catch`: `156 / 104 / 52`

## Convergence Check
- Resolver path (`latest_sqlite`) and ingest resolver (`_find_latest_sqlite`) apply equivalent validity and selection rules.
- MCP health/status/runtime surfaces report the same snapshot timestamp and SQLite path.
- Sentinel contamination risk (`99999999_9999`) is blocked by valid timestamp parsing and verified by tests.

## Final Decision
## GO

Rationale:
- Prompt 1 blocker is closed: canonical run now completes cleanly end-to-end on fresh snapshot artifacts.
- Prompt 2 blocker is closed: filesystem latest, burndown provenance, and MCP active snapshot all align to `04192026_0728`.
- No production P1 remediation edits were performed in this sequence.
