---
slug: notion-plans-status-rca-followups-b8e3f2
title: Notion Plans Status RCA — Follow-up Fixes
status: Completed
created: 2026-05-10
tier: T2
parent_plan: notion-plans-status-bulk-recovery-c4e2f9
ai_summary: |
  - Closes the 6 deferred-scope items from RCA NOTION_PLANS_STATUS_RCA_2026-05-10.md
  - W1 (P1): fix backfill_historical_plan_statuses.py default-to-Not-Started bug + build dedupe helper for Plans DB writers
  - W2 (P2): triage 8 non-Not-Started duplicate slugs + add hourly cache auto-refresh hook
  - W3 (P3): fix wave-lifecycle-writer test pollution of prod Notion + add Plans DB write telemetry
  - Pattern source: tools/notion/restore_plan_statuses_from_cache.py (already built); _plan_registration.py (extend)
  - Non-goals: rewriting all 41 Notion writers (only Plans-DB writers in scope)
  - Success: zero Plans DB duplicates; backfill defaults safely; cache refreshes hourly; tests don't pollute prod
---

# Notion Plans Status RCA — Follow-up Fixes

## 1. Context

On 2026-05-10 ~10:50 UTC, the Notion Plans DB suffered a bulk Status overwrite that flipped ~170 rows to `Not Started`, plus accumulated 11 slugs with duplicate rows. Same-day recovery via `tools/notion/restore_plan_statuses_from_cache.py` brought live Not Started count from 180 → 1 (legitimate). Recovery plan: `notion-plans-status-bulk-recovery-c4e2f9`.

Full RCA: `@docs/architecture/rca/NOTION_PLANS_STATUS_RCA_2026-05-10.md`. Three independent failure modes identified:

- **Cause A**: `backfill_historical_plan_statuses.py:158` defaults to `"Not Started"` when plan markdown lacks frontmatter `status:` — overwrote 89 rows. Single-line fix.
- **Cause B**: 41 files write to Notion; Cursor Agent-direct `mcp7_API-post-page` calls don't dedup → 11 slugs got phantom duplicate rows.
- **Cause C**: `_plan_registration.py` cache TTL=1h but no scheduled refresh; 9h stale at incident time missed user edits.

This plan implements the 6 RCA action items in 3 waves.

## 2. Non-Goals

- **NOT** rewriting all 41 Notion writers (only Plans-DB writers in scope).
- **NOT** changing the 2026-05-03 status taxonomy rename (Draft→Not Started, Live→In Progress) — that's working correctly.
- **NOT** retroactively patching any historical row state — recovery (`c4e2f9`) handled that.

## 3. ADG_HOTSPOT_REPORT

Not applicable — this plan touches `tools/notion/` and `.windsurf/scripts/` which are infrastructure-layer, not L0..L6 code.

## 4. ADG_GRAPH_LAYER_EVIDENCE

Not applicable — no production code paths in scope.

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1, W1.P2 | P1 fixes — backfill default + dedup helper | ~6k | RCA root causes correct; Notion API dedup-by-slug works | 🟡 PENDING | Backfill skips no-ground-truth rows; new helper used by all Plans-DB POST callers; CI gate green |
| W2 | W2.P1, W2.P2 | P2 hygiene — 8 duplicate triage + hourly cache refresh | ~4k | duplicates have a clear "winner" copy per slug | 🟡 PENDING | 8 slugs deduplicated; cache refreshes within 1h |
| W3 | W3.P1, W3.P2 | P3 observability — test pollution + telemetry | ~3k | tests use a stable identifier we can guard | 🟡 PENDING | Unit tests don't hit prod Notion; every Plans-DB write logged |

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Fix `backfill_historical_plan_statuses.py` default-to-Not-Started | `tools/notion/backfill_historical_plan_statuses.py` (1 line); test in `tests/unit/tools_notion/` | none — single-line change | 1k | 🟡 PENDING |
| W1.P2 | Build `register_plan_idempotent()` helper + pre-MCP gate + weekly CI dedup gate | `tools/notion/_plan_registration_helpers.py` (new), `.windsurf/scripts/pre_mcp_gate.py` (extend), `ops_scripts/ci/check_notion_plans_no_duplicates.py` (new) | 3 surfaces; needs careful schema (block at MCP layer when slug exists) | 5k | 🟡 PENDING |
| W2.P1 | Triage remaining 8 non-Not-Started duplicate slugs | one-shot script in `artifacts/notion/`; manual user-judgement per slug | semantic ambiguity for some duplicates | 2k | 🟡 PENDING |
| W2.P2 | Hourly cache auto-refresh | `.windsurf/scripts/pre_user_prompt_plan_registration_refresh.py` (new) | mustn't slow turn-start; needs background subprocess | 2k | 🟡 PENDING |
| W3.P1 | Fix wave-lifecycle-writer test pollution | `tests/unit/tools_notion/test_wave_lifecycle_writer.py` (mock or NOTION_TOKEN guard) | identifies which test fixtures leak | 1k | 🟡 PENDING |
| W3.P2 | Plans DB write telemetry | `tools/notion/wave_lifecycle_writer.py` (extend logger), grep all Plans-DB writers and standardize log line | cross-cutting; many touch points | 2k | 🟡 PENDING |

## 7. Definition of Done

| ID | Criterion | Verification |
|---|---|---|
| DoD-1 | `backfill_historical_plan_statuses.py --patch` no longer overwrites rows lacking on-disk ground truth | Unit test: plan with no `status:` frontmatter → script does not include in drift_items |
| DoD-2 | All Plans-DB POST callers route through `register_plan_idempotent()` | `grep_search` shows no direct `data_sources/.../query` POST in `tools/notion/` outside the helper |
| DoD-3 | Pre-MCP gate blocks `mcp7_API-post-page` to Plans DB when slug already exists | Synthetic test: emit duplicate POST → gate exits non-zero |
| DoD-4 | CI gate `check_notion_plans_no_duplicates.py` exits 0 with current state, fails on synthetic duplicate | Test fixture creates duplicate, gate detects |
| DoD-5 | 8 remaining non-Not-Started duplicates resolved (each triaged + archived/kept) | `python artifacts/notion/_find_duplicates.py` shows 0 duplicate slugs |
| DoD-6 | Cache refresh runs at session start when older than 1h | `pre_user_prompt_plan_registration_refresh.py` exits 0; `fetched_at_epoch` updates |
| DoD-7 | Unit tests no longer hit prod Notion | `wave_lifecycle_notion.jsonl` shows no test-slug entries (`x-aaaaaa`, `demo-plan-abc123`, `page-123`) for 7 days post-fix |
| DoD-8 | Every Plans-DB write logs to `artifacts/windsurf/plans_db_writes.jsonl` with slug + page_id + status_before + status_after + writer_path | Code grep shows every PATCH/POST in plans-related writers calls the logger |

### Verification vs Deferral

| Claim | Verification this plan | Deferred to |
|---|---|---|
| Backfill no longer corrupts | DoD-1 unit test + manual `--dry-run` against current state | — |
| Dedup architecture in place | DoD-2/3/4 | — |
| Cache freshness improved | DoD-6 + 1-week observation | Cache-on-write upgrade (not just hourly poll) |
| Test pollution stopped | DoD-7 (7-day observation window) | — |

## 8. Files In Scope

- `.windsurf/plans/notion-plans-status-rca-followups-b8e3f2.md` (this plan)
- `tools/notion/backfill_historical_plan_statuses.py` (1-line fix)
- `tools/notion/_plan_registration_helpers.py` (NEW)
- `tools/notion/wave_lifecycle_writer.py` (telemetry extension)
- `.windsurf/scripts/pre_mcp_gate.py` (extend)
- `.windsurf/scripts/pre_user_prompt_plan_registration_refresh.py` (NEW)
- `ops_scripts/ci/check_notion_plans_no_duplicates.py` (NEW)
- `tests/unit/tools_notion/test_backfill_historical_plan_statuses.py` (NEW or extend)
- `tests/unit/tools_notion/test_wave_lifecycle_writer.py` (mock guards)
- `tests/unit/windsurf_scripts/test_plan_registration_refresh.py` (NEW)

## 9. Out of Scope

Anything outside `tools/notion/`, `.windsurf/scripts/`, `ops_scripts/ci/`, `tests/unit/tools_notion/`, `tests/unit/windsurf_scripts/`. Other Notion DBs (Backlog, MCP Registry, etc.) are intentionally excluded.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Pre-MCP gate blocks legitimate registration on cache-miss | Refresh cache before gate fires; whitelist via env var for incident response |
| Hourly refresh slows session start | Background subprocess; cap timeout 5s; never block prompt |
| Telemetry log grows unbounded | Rotate at 10MB; gitignore the file |
| Duplicate triage picks wrong "winner" | Always preserve loser via `in_trash=true` (recoverable), never DELETE |

## 11. References

- RCA: `@docs/architecture/rca/NOTION_PLANS_STATUS_RCA_2026-05-10.md`
- Recovery plan: `@.windsurf/plans/notion-plans-status-bulk-recovery-c4e2f9.md`
- Constitutional: §25, §35, §36
- Rules: `notion-plans-taxonomy.md`, `notion-plan-wave-deferral.md`, `plan-registration-enforcement.md`
- Bug source: `@tools/notion/backfill_historical_plan_statuses.py:127-158`
- Trigger commit: `90883aafa105806b980b43c8cf4fb11108e6731c`
