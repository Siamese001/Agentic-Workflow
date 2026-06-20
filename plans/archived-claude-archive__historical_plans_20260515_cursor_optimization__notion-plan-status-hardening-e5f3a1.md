---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\notion-plan-status-hardening-e5f3a1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\notion-plan-status-hardening-e5f3a1.md'
source_sha256: 42b764045d2d06cb078d93579ed04b0868d1e34d31adecc4786b0adcfd218e2e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: notion-plan-status-hardening-e5f3a1
status: In Progress
created: 2026-05-12
dod_exempt: false
---

# Notion Plan Status Hardening — e5f3a1

## Summary

Harden the wave lifecycle system to prevent retrospective/completed plans from
having their Notion status incorrectly flipped to "In Progress". This closes
the race condition where:

1. Cascade emits `PLAN_CREATED:` for a plan that is simultaneously set to
   Completed via `API-post-page`.
2. On the next turn `wave_execution_state.py start` is called, which calls
   `_notion_sync(plan, "wave_start", wave=1)`.
3. Because the Notion lookup may see a timing window, or because the status
   lookup sees the wrong prior state, it flips to In Progress.

**Belt-and-suspenders approach:**
- Arm 1 (primary): Guard `_cmd_start` to skip the `wave_start` Notion sync
  when the current Notion status is already `Completed`.
- Arm 2 (secondary): Update `_FLIPPABLE_TO_IN_PROGRESS` in helpers to only
  allow the flip from `Not Started` and `Waiting` — Completed is already
  excluded, but we make this explicit in the `wave_start` doc comment.
- Arm 3 (belt-and-suspenders for marker path): Add a `COMPLETED_GUARD` in
  `patch_for_marker` for `wave_start` that logs a warning and no-ops when
  current_status is Completed.
- Arm 4 (CI gate): Add `check_notion_plan_lifecycle_guard.py` that validates
  the guard logic is present in `wave_execution_state.py` and
  `_wave_lifecycle_helpers.py`.

## RCA

Root cause: `_cmd_start` in `wave_execution_state.py` calls
`_notion_sync(plan, "wave_start", wave=1)` unconditionally. If the Notion
lookup returns `current_status=None` (plan not yet registered or timing race),
`patch_for_marker` treats `None` as not in `_FLIPPABLE_TO_IN_PROGRESS` and
does NOT flip — **unless** the status happens to be `Not Started` at lookup
time due to timing. For retrospective plans created-and-completed in the same
turn, the `start` command was intended for a different (new) plan's lifecycle
but the slug was reused or emitted in an ambiguous context.

Secondary cause: The protocol for retrospective plans (plans authored to
document already-completed work) did NOT have a machine-readable guard
preventing `wave_execution_state.py start` from being called on them.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | W1.P1 | Status guard in wave_execution_state.py | ~500 | ✅ DONE |
| W2 | W2.P1 | patch_for_marker Completed guard + doc | ~200 | ✅ DONE |
| W3 | W3.P1, W3.P2 | CI gate + tests | ~800 | ✅ DONE |
| W4 | W4.P1 | Rule update + memory writeback | ~200 | ✅ DONE |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Status |
|----------|-------|---------------|--------|
| W1.P1 | Start guard | tools/windsurf/wave_execution_state.py | ✅ DONE |
| W2.P1 | Helper guard | tools/notion/_wave_lifecycle_helpers.py | ✅ DONE |
| W3.P1 | CI gate | ops_scripts/ci/check_notion_plan_lifecycle_guard.py | ✅ DONE |
| W3.P2 | Tests | tests/unit/tools/notion/test_wave_lifecycle_guard.py | ✅ DONE |
| W4.P1 | Rule + memory | .windsurf/rules/notion-plan-wave-deferral.md | ✅ DONE |

## Definition of Done

| ID | Criterion | Verification |
|----|-----------|-------------|
| DoD-1 | `wave_execution_state.py start` on a Completed plan does NOT flip status | Unit test + manual check |
| DoD-2 | `patch_for_marker(wave_start, "Completed")` returns is_noop=True for status | Unit test |
| DoD-3 | CI gate exits 0 with no violations | `python ops_scripts/ci/check_notion_plan_lifecycle_guard.py` |
| DoD-4 | All new + existing tests pass | pytest tests/ |
| DoD-5 | Rule updated with retrospective-plan protocol | `.windsurf/rules/notion-plan-wave-deferral.md` |

## Verification-vs-Deferral

| Item | Verified? | Deferred? |
|------|-----------|-----------|
| Notion live status check after fix | Deferred (no live Notion test in CI) | Yes |
| Race window < 1s coverage | Deferred (requires real network timing) | Yes |
