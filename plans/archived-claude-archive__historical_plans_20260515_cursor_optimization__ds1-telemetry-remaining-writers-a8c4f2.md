---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\ds1-telemetry-remaining-writers-a8c4f2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\ds1-telemetry-remaining-writers-a8c4f2.md'
source_sha256: ac906af89557785a45464da8b6c05ae109c2e0714772f5ce03714011836d56e8
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: ds1-telemetry-remaining-writers-a8c4f2
title: DS-1 Remaining Telemetry Writers
status: Completed
created: 2026-05-10
tier: T1
parent_plan: notion-plans-db-hygiene-deferred-scope-d4f7c1
plan_type: governance
dod_exempt: false
ai_summary: |
  - Target: tools/notion/apply_plan_derived_status.py + backfill_historical_plan_statuses.py
  - Closes DS-1 partial gap: two remaining PATCH writers lack log_plans_db_write telemetry.
  - wave_execution_state.py already covered transitively via wlw.apply_spec (DS-1 wave_lifecycle_writer).
  - New files: none. Edit: 2 files, 2 telemetry call sites.
  - Pattern source: notion-plans-db-hygiene-deferred-scope-d4f7c1 DS-1.
  - Non-goals: changing patch logic, adding new CI gates, touching L0..L6.
  - Success: both writers emit to plans_db_writes.jsonl; unit tests verify import + call.
---

# DS-1 Remaining Telemetry Writers

Wire `log_plans_db_write` into the two remaining Notion PATCH writers that DS-1 left incomplete.

---

## Context (SCQA)

- **Situation**: DS-1 added unified Plans-DB write telemetry to `wave_lifecycle_writer.py`, `repair_notion_plan_statuses.py`, and `restore_plan_statuses_from_cache.py`. Two PATCH writers remain untouched.
- **Complication**: `apply_plan_derived_status.py` and `backfill_historical_plan_statuses.py` both issue live Notion PATCH calls with no telemetry entry in `plans_db_writes.jsonl`.
- **Question**: How do we close the DS-1 telemetry gap for the two remaining writers?
- **Answer**: Add a single `log_plans_db_write(...)` call at each writer's successful PATCH site — same pattern as the three already done.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `tools/notion/apply_plan_derived_status.py` | PATCH site at `_patch_page` success branch | ✅ Read |
| `tools/notion/backfill_historical_plan_statuses.py` | PATCH site at `_req("PATCH", ...)` success branch | ✅ Read |
| `tools/windsurf/wave_execution_state.py` | Confirmed calls `wlw.apply_spec` — telemetry already covered | ✅ Read |

---

## Wave Structure

| Wave | Focus | Status |
|---|---|---|
| W1 | Wire telemetry into `apply_plan_derived_status.py` + `backfill_historical_plan_statuses.py` + fix `event=` kwarg across all 5 writers | ✅ Done |

---

## Out Of Scope

- `wave_execution_state.py` — already covered transitively via `wlw.apply_spec`
- Any new CI gates
- Changing PATCH logic, throttle, or error handling in either file

---

## Definition of Done

| ID | Criterion | Verification |
|---|---|---|
| DoD-1 | `apply_plan_derived_status.py` imports and calls `log_plans_db_write` after successful PATCH | grep + unit test |
| DoD-2 | `backfill_historical_plan_statuses.py` imports and calls `log_plans_db_write` after successful PATCH | grep + unit test |
| DoD-3 | Import smoke: `python -c "from tools.notion.apply_plan_derived_status import main"` exits 0 | run_command |
| DoD-4 | Import smoke: `python -c "from tools.notion.backfill_historical_plan_statuses import main"` exits 0 | run_command |
| DoD-5 | No regressions in existing tests | pytest tests/unit/tools_notion/ |
