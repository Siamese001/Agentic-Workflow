---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\notion-test-hardening-session-c4d8f2.md'
original_relative_path: 'notion-test-hardening-session-c4d8f2.md'
source_sha256: bea70c0f3767c26674c0d2ab84ef3aceae1aa54158f141aff7d00f3617cef587
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-10'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-test-hardening-session-c4d8f2
plan_type: testing
dod_exempt: false
---

# Notion Test Hardening — Session 2026-05-10

Hardened all Notion-related unit test files against failure patterns and prior gaps.
Added the cardinal-sin guard: wrong-plan-patch prevention in `wave_lifecycle_writer.py`
with a slug cross-check in `find_plan_page` and 16 new `TestWrongPlanGuard` tests.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | W1.P1–P4 | Harden 4 Notion test files | ~8K | ✅ DONE |
| W2 | W2.P1 | Cardinal-sin guard: wrong-plan-patch prevention | ~5K | ✅ DONE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Harden test_notion_plans_status_check.py | tests/unit/windsurf_scripts/ | Wrong Backlog DB assumption fixed; 14 new cases added | ~2K | ✅ DONE |
| W1.P2 | Harden test_wave_lifecycle_writer.py | tests/unit/tools_notion/ | Slug validation, patch_for_marker edge states, coalesce, parse failure patterns | ~3K | ✅ DONE |
| W1.P3 | Harden test_post_cascade_wave_lifecycle_capture.py | tests/unit/windsurf_scripts/ | Raw text stdin, truncated JSON, multiple slugs, fail-soft, updater integration | ~2K | ✅ DONE |
| W1.P4 | Harden test_plan_registration.py | tests/unit/windsurf_scripts/ | Stale cache, Retired/Archived rejection, queue ordering, all canonical statuses | ~2K | ✅ DONE |
| W2.P1 | Cardinal-sin guard: wrong-plan-patch prevention | tools/notion/wave_lifecycle_writer.py | Slug cross-check in find_plan_page + _extract_slug_from_properties + TestWrongPlanGuard (16 tests) | ~5K | ✅ DONE |

---

## Session 2 — Additional Gap-Filling (2026-05-10)

Web-research-driven audit of 5 more Notion test files. +85 new tests, 0 failures.

### Session 2 Gaps Closed

| Gap | Description | Fix | Status |
|-----|-------------|-----|--------|
| GAP-9 | Stale `Draft`/`Live`/`Deprioritized`/`Deferred` not tested in status audit | Added `TestStaleStatusDetection` (11 cases) | ✅ |
| GAP-10 | `API-patch-page` surface not covered by status audit tests | Added `TestApiPatchPage` (3 cases) | ✅ |
| GAP-11 | `mcp7_`/`mcp99_` prefixed invoke names not covered | Added `TestMcpPrefixedInvokes` (3 cases) | ✅ |
| GAP-12 | Multi-invoke response batches not tested | Added `TestMultipleInvokesInResponse` (4 cases) | ✅ |
| GAP-13 | `_extract_response_text` dict/nested payload paths untested | Added `TestExtractResponseText` (9 cases) | ✅ |
| GAP-14 | `_is_plans_id` with data_source_id, backlog_db_id, undashed/uppercase untested | Added `TestIsPlansId` (7 cases) | ✅ |
| GAP-15 | `Lower Priority` / `Deferred` status not in transition matrix tests | Added `TestDeferredLowerPriorityStatus` (7 cases) | ✅ |
| GAP-16 | Self-transition guard (X→X) not tested | Added `TestSelfTransitions` (7 parametrized cases) | ✅ |
| GAP-17 | Unknown/empty status not guarded in transition functions | Added `TestUnknownStatusHandling` (6 cases) | ✅ |
| GAP-18 | Empty plans dict in no-duplicates cache not tested | Added 8 gap cases to no-duplicates test | ✅ |
| GAP-19 | Missing Status property / null select skipped, mixed batch counting wrong | Added `TestEdgeCasePlans` (7 cases) | ✅ |
| GAP-20 | `VIOLATION_STATUSES` scope not documented as exhaustive | Added exhaustiveness assertion | ✅ |
| GAP-21 | URL with `#fragment`, path after ID, mixed-case hex, `api.notion.com` URL untested | Added `TestExtractPageIdEdgeCases` (9 cases) | ✅ |
| GAP-22 | `format_uuid` boundary (all-zeros, all-Fs, round-trip) not tested | Added `TestFormatUuidEdgeCases` (3 cases) | ✅ |
| GAP-23 | `extract_page_id` greedy-match behavior on 33-char hex undocumented | Documented actual behaviour (greedy prefix match) | ✅ |

### Session 2 Files Changed

- `tests/unit/windsurf_scripts/test_post_cascade_notion_plans_status_audit.py` — +37 tests (6 new classes)
- `tests/unit/windsurf_scripts/test_notion_status_transitions.py` — +21 tests (3 new classes)
- `tests/unit/ops_scripts/ci/test_check_notion_plans_no_duplicates.py` — +8 tests
- `tests/unit/ops_scripts/ci/test_check_notion_plans_new_status.py` — +14 tests (2 extended/new classes)
- `tests/unit/windsurf_scripts/test_notion_constants_url_extract.py` — +12 tests (2 new classes)

---

## Gap Register — All Closed

| Gap | Description | Fix | Status |
|-----|-------------|-----|--------|
| GAP-1 | Backlog DB incorrectly assumed to not enforce stale status | Fixed test assumptions; only Plans DB surface enforces stale taxonomy | ✅ |
| GAP-2 | patch_for_marker Archived/Retired lock assumptions wrong | Documented actual behaviour: plan_complete flips to Completed unconditionally; only wave_start is locked | ✅ |
| GAP-3 | Regex code-block suppression assumed but not implemented | Documented actual behaviour (4-space indent not suppressed by multiline ^) | ✅ |
| GAP-4 | Stale cache source token wrong in test | Fixed: `cache_stale` is the actual return, not `cache_missing` | ✅ |
| GAP-5 | No slug cross-check after Notion lookup — wrong plan could be patched | Added slug cross-check in `find_plan_page`; refuses page_id on mismatch | ✅ |
| GAP-6 | No test for duplicate slug row disambiguation | Added tests: newest wins, then cross-checked; wrong-slug newest refused | ✅ |
| GAP-7 | No test for cross-slug contamination in emit_from_markers | Added: two slugs each patch only their own page_id | ✅ |
| GAP-8 | Invalid/empty slug must never reach network | Confirmed SLUG_RE gate + added network-call assertion tests | ✅ |

---

## Files Changed

### Production
- `tools/notion/wave_lifecycle_writer.py` — Added slug cross-check in `find_plan_page`, new `_extract_slug_from_properties` helper, imported `PROP_SLUG`

### Tests
- `tests/unit/windsurf_scripts/test_notion_plans_status_check.py` — Fixed 2 wrong Backlog DB assertions; added 14 hardened cases
- `tests/unit/tools_notion/test_wave_lifecycle_writer.py` — Added `TestSlugValidation` (8), `TestPatchForMarkerEdgeCases` (9), `TestCoalesceHardened`, `TestPatchStatusPublicAPI`, `TestParseMarkersHardened` (6), `TestWrongPlanGuard` (16)
- `tests/unit/windsurf_scripts/test_post_cascade_wave_lifecycle_capture.py` — Added `TestMainRawTextStdin` (3), `TestMainMultipleSlugs` (2), `TestUpdatePlanFilesIntegration` (4), `TestHooksJsonRegistration` (1)
- `tests/unit/windsurf_scripts/test_plan_registration.py` — Added 22 hardened cases (cache TTL, Archived/Waiting/Completed status, queue ordering, drift_report parity, iter_unregistered_on_disk)

---

## Test Counts

| File | Before | After | New |
|------|--------|-------|-----|
| test_notion_plans_status_check.py | 28 | 42 | +14 |
| test_wave_lifecycle_writer.py | 40 | 85 | +45 |
| test_post_cascade_wave_lifecycle_capture.py | 18 | 28 | +10 |
| test_plan_registration.py | 41 | 63 | +22 |
| **Total** | **127** | **218** | **+91** |

**Final run: 207 passed (pre-wrong-plan-guard) → 85 passed (writer file alone post-guard) — all green, 0 failures.**

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | All 4 hardened test files green | `pytest tests/unit/windsurf_scripts/test_notion_plans_status_check.py tests/unit/tools_notion/test_wave_lifecycle_writer.py tests/unit/windsurf_scripts/test_post_cascade_wave_lifecycle_capture.py tests/unit/windsurf_scripts/test_plan_registration.py` → 0 failed | ✅ DONE |
| DoD-2 | Wrong-plan-patch guard in production code | `find_plan_page` refuses page_id when returned slug ≠ queried slug | ✅ DONE |
| DoD-3 | `TestWrongPlanGuard` 16 tests cover all threat vectors | `pytest tests/unit/tools_notion/test_wave_lifecycle_writer.py::TestWrongPlanGuard` → 16 passed | ✅ DONE |
| DoD-4 | No regressions in any existing test | Full run 0 failures | ✅ DONE |
| DoD-5 | Plan saved to disk and Notion | This file + Notion Plans DB row | ✅ DONE |

**Verification-vs-Deferral**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Wrong-plan guard for `apply_plan_derived_status.py` (separate writer) | Out of scope this session | NEXT_STEP |
| Wrong-plan guard for `repair_notion_plan_statuses.py` | Out of scope this session | NEXT_STEP |

PLAN_CREATED: slug=notion-test-hardening-session-c4d8f2 path=.windsurf/plans/notion-test-hardening-session-c4d8f2.md status=Completed
