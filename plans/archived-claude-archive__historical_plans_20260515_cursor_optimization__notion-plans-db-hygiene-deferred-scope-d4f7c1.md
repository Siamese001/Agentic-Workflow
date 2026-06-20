---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\notion-plans-db-hygiene-deferred-scope-d4f7c1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\notion-plans-db-hygiene-deferred-scope-d4f7c1.md'
source_sha256: 59e106c3dabc8cd364382048679bfe226b3cd89bb4b64f651263b3245b2dd37c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: notion-plans-db-hygiene-deferred-scope-d4f7c1
title: Notion Plans DB Hygiene — Deferred Scope (Post-RCA)
status: Completed
created: 2026-05-10
tier: T2
parent_plan: notion-plans-status-rca-followups-b8e3f2
ai_summary: |
  - Deferred scope items from RCA NOTION_PLANS_STATUS_RCA_2026-05-10 and plan b8e3f2.
  - Scope: harden remaining 37 Notion writers (only Plans-DB writers used register_plan_idempotent so far),
    cache-on-write discipline, telemetry log rotation, pre_mcp_gate Plans-DB block, MCP Registry / Backlog
    DB write hygiene, backfill_historical_plan_statuses CI hardening.
  - Non-goals: changing status taxonomy, rewriting non-Notion infra, touching L0..L6 production paths.
  - Not to be implemented until parent plan b8e3f2 is merged, pushed, and verified green.
dod_exempt: false
---

# Notion Plans DB Hygiene — Deferred Scope (Post-RCA)

## 1. Context

Plan `notion-plans-status-rca-followups-b8e3f2` (completed 2026-05-10) closed the three primary root
causes of the Plans DB bulk-overwrite incident. Several hardening items were intentionally deferred
to keep that plan bounded. This plan captures all of them in one place so they can be prioritised
and sequenced independently.

Parent RCA: `docs/architecture/rca/NOTION_PLANS_STATUS_RCA_2026-05-10.md`  
Parent recovery plan: `.windsurf/plans/notion-plans-status-bulk-recovery-c4e2f9.md`  
Immediate fix plan: `.windsurf/plans/notion-plans-status-rca-followups-b8e3f2.md`

---

## 2. Deferred Scope Items

### DS-1 — Migrate remaining Notion writers to `register_plan_idempotent`

**Source**: `b8e3f2` §9 Out of Scope / RCA §3.2  
**Priority**: P2  
**Why deferred**: Only `register_ondisk_plans_batch.py` was migrated in b8e3f2. The remaining ~40
Notion-writing files were out of scope.

**Detail**:  
Run `grep -r "API-post-page\|mcp7_API-post-page\|/v1/pages" tools/ .windsurf/scripts/` and produce
a complete inventory. For each file that creates a Plans DB row:
- Replace the raw POST with `register_plan_idempotent()` from `tools/notion/_plan_registration_helpers.py`.
- Add `log_plans_db_write()` telemetry at all PATCH/status-update paths.
- Write a unit test asserting the file calls `register_plan_idempotent` not a bare HTTP POST.

Files known to have raw Plans-DB write paths (non-exhaustive):
- `tools/notion/plan_registration_backfill.py` (disabled writes)
- `.windsurf/scripts/_plan_registration.py` (queue flush path)
- `tools/windsurf/wave_execution_state.py` (start command's `_register_if_needed`)
- `tools/notion/apply_plan_derived_status.py` (PATCH status only — add telemetry)
- `tools/notion/repair_notion_plan_statuses.py` (PATCH status only — add telemetry)
- `tools/notion/backfill_historical_plan_statuses.py` (PATCH status only — add telemetry)

---

### DS-2 — Cache-on-write discipline (not just hourly poll)

**Source**: `b8e3f2` §7 Verification vs Deferral, `NOTION_PLANS_STATUS_RCA_2026-05-10.md` §4.3  
**Priority**: P2  
**Why deferred**: Hourly background refresh (W2.P2) is sufficient for now; cache-on-write is a
deeper change.

**Detail**:  
Every successful Plans-DB write should invalidate + update the relevant cache entry in
`.windsurf/state/plan_registration_cache.json` immediately, without waiting for the next hourly
background refresh. This requires:

1. `register_plan_idempotent()` calls `_update_cache_entry(slug, page_id, status)` after a
   successful `created` action.
2. `apply_plan_derived_status.py` and `repair_notion_plan_statuses.py` call
   `_update_cache_status(slug, new_status)` after a successful PATCH.
3. `_update_cache_entry` / `_update_cache_status` use file locking (`fcntl` on Unix /
   `msvcrt` on Windows) to prevent race conditions when two hooks fire concurrently.
4. Unit tests: write + concurrent-write race simulation.

---

### DS-3 — Pre-MCP gate: block Cascade-direct `mcp7_API-post-page` to Plans DB

**Source**: RCA §3.2/§3.4 layer-1 defense (partially implemented — CI gate done, hook-level block
not done)  
**Priority**: P2  
**Why deferred**: `post_cascade_plans_dup_audit.py` is advisory only; hard block via
`pre_mcp_tool_use` hook was deferred from b8e3f2.

**Detail**:  
Extend `.windsurf/scripts/pre_mcp_gate.py` (or add a `pre_mcp_tool_use` hook) to:

1. When `API-post-page` is invoked and parent is Plans DB (`data_source_id ac53d31b-…`):
   - Extract `Slug` from the payload.
   - Query cache: if slug exists and is non-archived, block the MCP call and return a structured
     error: `DUPLICATE_BLOCKED: slug=<slug> existing_page_id=<id>`.
   - If cache is stale/missing: refresh first (sync, not background), then check.
2. Bypass: `NOTION_PLANS_DUP_MCP_BYPASS=1`.
3. Unit test: synthetic payload with known-existing slug → asserts `DUPLICATE_BLOCKED`.

---

### DS-4 — Telemetry log rotation + gitignore enforcement

**Source**: `b8e3f2` §10 Risk: "Telemetry log grows unbounded"  
**Priority**: P3  
**Why deferred**: Log was created this session; rotation is premature until volume is observed.

**Detail**:  
- `artifacts/windsurf/plans_db_writes.jsonl` and `artifacts/windsurf/wave_lifecycle_notion.jsonl`:
  rotate when > 10 MB (move to `plans_db_writes.jsonl.1`, clear active file).
- Rotation function in `tools/notion/_plan_registration_helpers.py::_rotate_if_large()`, called
  inside `_log()`.
- Confirm both paths are in `.gitignore` (they should be — `artifacts/windsurf/*.jsonl` is
  gitignored; verify).
- Add CI gate `ops_scripts/ci/check_notion_telemetry_log_size.py` that warns at > 5 MB,
  errors at > 20 MB.

---

### DS-5 — DoD-7 7-day observation window: verify tests no longer pollute prod Notion

**Source**: `b8e3f2` §7 Verification vs Deferral DoD-7  
**Priority**: P3 (observation only — no code change unless pollution reappears)

**Detail**:  
From 2026-05-17 onwards, inspect `artifacts/windsurf/wave_lifecycle_notion.jsonl` for entries
with `slug` matching `x-aaaaaa`, `demo-plan-abc123`, or `page-123`. If any appear after that
date, the `tests/unit/tools_notion/conftest.py` autouse fixture is not working as intended and
a deeper fix (e.g. blanket env-var patch in conftest.py root) is needed.

Check script (one-liner):
```bash
grep -E '"x-aaaaaa"|"demo-plan-abc123"|"page-123"' artifacts/windsurf/wave_lifecycle_notion.jsonl \
  | grep -v '"2026-05-1[0]T'
```
If output is non-empty after 2026-05-17, open a bug and implement the root fix.

---

### DS-6 — Extend `check_notion_plans_no_duplicates.py` to Backlog Items DB

**Source**: RCA §3.2 "Other Notion DBs" left out of scope  
**Priority**: P3

**Detail**:  
The dedup CI gate currently only checks the Plans DB. The Backlog Items DB
(`data_source fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7`) also accumulates rows written by multiple
scripts and could develop the same phantom-duplicate problem.

Extend `ops_scripts/ci/check_notion_plans_no_duplicates.py` (or create a sibling
`check_notion_backlog_no_duplicates.py`) with:
- Filter: by `Slug` (or equivalent unique property) across non-archived Backlog rows.
- Fail-closed on duplicate count > 0.
- Cache from `artifacts/notion/backlog_snapshot.json` when available.

---

### DS-7 — Harden `backfill_historical_plan_statuses.py --ci` mode

**Source**: RCA §2.3 "Why CI didn't catch it"  
**Priority**: P3

**Detail**:  
The `--ci` mode of `backfill_historical_plan_statuses.py` exits 2 on drift — but "drift" is
calculated using the same `_extract_status_from_plan()` function that had the `return "Not Started"`
default. Even with the single-line fix (b8e3f2 W1.P1), the `--ci` mode still has a logical flaw:
it reports "drift" for any plan where the disk has `None` status and Notion has anything other
than Not Started — which is not actually drift, it's just "we don't know the disk status".

Fix: in `--ci` mode, exclude rows where `disk_status is None` from the drift count entirely.
Add a separate counter `no_ground_truth_skipped` to the summary so the operator can see the
exemption count without it inflating the drift total.

---

## 3. Priority Matrix

| DS-# | Title | Priority | Estimated effort | Dependencies |
|---|---|---|---|---|
| DS-3 | Pre-MCP gate block for Plans DB POST | P2 | Medium (~100 lines + tests) | DS-2 (cache freshness for gate to query) |
| DS-1 | Migrate remaining ~40 Notion writers to helper | P2 | Large (multi-file; 1 wave per ~10 writers) | DS-3 complete (gate ensures no bypass) |
| DS-2 | Cache-on-write discipline | P2 | Medium (~80 lines + file-lock + tests) | DS-1 (so all writers go through helper) |
| DS-4 | Telemetry log rotation + gitignore | P3 | Small (~30 lines) | None |
| DS-7 | Harden `backfill --ci` drift count | P3 | Small (~15 lines + tests) | None |
| DS-6 | Extend dedup gate to Backlog DB | P3 | Small (~50 lines) | None |
| DS-5 | 7-day pollution observation | P3 | Observation only; no code | None |

**Recommended execution order**: DS-7 → DS-4 → DS-3 → DS-2 → DS-1 → DS-6, DS-5 (parallel observation)

---

## 4. Non-Goals

- Re-running the 2026-05-10 recovery (that is complete and verified).
- Changing the Plans DB status taxonomy (current taxonomy is correct and enforced).
- Modifying any L0..L6 production pipeline code.
- Rewriting Notion writers outside the Plans DB surface (Backlog Items, MCP Registry, etc.) in
  this plan — they get their own assessment.

---

## 5. Wave Structure (placeholder — populate before execution)

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | W1.P1, W1.P2 | DS-7 (backfill CI mode) + DS-4 (telemetry rotation) | ~3k | ✅ Done |
| W2 | W2.P1 | DS-3 (pre-MCP gate / pre_user_prompt dup surface) | ~5k | ✅ Done |
| W3 | W3.P1 | DS-2 (cache-on-write) + DS-4 (CI gate NP7) | ~5k | ✅ Done |
| W4 | W4.P1..W4.P3 | DS-1 (telemetry for top PATCH writers: wave_lifecycle, repair, restore) | ~8k | ✅ Done |
| W5 | W5.P1, W5.P2 | DS-6 (Backlog DB dedup gate NP6) + DS-5 (observation verdict) | ~3k | ✅ Done (DS-6); DS-5 pending 2026-05-17 |
| W6 | W6.P1 | DS-1 remainder (apply_derived, backfill; event= kwarg fix all 5 writers) — child plan ds1-telemetry-remaining-writers-a8c4f2 | ~2k | ✅ Done |

---

## 6. Definition of Done

| ID | Criterion | Verification |
|---|---|---|
| DoD-1 | All 40+ Plans-DB POST paths use `register_plan_idempotent` | grep shows zero raw `mcp7_API-post-page` to Plans parent outside helper |
| DoD-2 | Cache-on-write: every successful POST/PATCH updates cache immediately | Unit test: POST → inspect cache file within 100ms |
| DoD-3 | Pre-MCP gate hard-blocks duplicate POST | Test: synthetic payload for existing slug → `DUPLICATE_BLOCKED` returned |
| DoD-4 | Telemetry logs rotated at 10MB; both paths in `.gitignore` | CI gate green; `git check-ignore artifacts/windsurf/*.jsonl` shows ignored |
| DoD-5 | `backfill --ci` excludes no-ground-truth rows from drift count | Unit test: plan with no frontmatter status → not counted in drift |
| DoD-6 | Backlog Items DB dedup gate passes on clean state, fails on synthetic dup | CI gate test fixture |
| DoD-7 | No test slugs appear in `wave_lifecycle_notion.jsonl` for 7 days post b8e3f2 merge | Manual grep check on 2026-05-17 |

---

## 7. References

- Parent RCA: `docs/architecture/rca/NOTION_PLANS_STATUS_RCA_2026-05-10.md`
- Completed fix plan: `.windsurf/plans/notion-plans-status-rca-followups-b8e3f2.md`
- Helper module: `tools/notion/_plan_registration_helpers.py`
- Dedup CI gate: `ops_scripts/ci/check_notion_plans_no_duplicates.py`
- Cache refresh hook: `.windsurf/scripts/pre_user_prompt_plan_registration_refresh.py`
- Telemetry viewer: `tools/notion/show_plans_db_writes.py`
- Constitutional: §25 (MCP serialization), §28 (SQLite/grep hierarchy), §36 (plan registration)
- Rules: `notion-plans-taxonomy.md`, `plan-registration-enforcement.md`
