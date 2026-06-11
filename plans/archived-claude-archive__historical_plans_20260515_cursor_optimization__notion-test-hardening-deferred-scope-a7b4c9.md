---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\notion-test-hardening-deferred-scope-a7b4c9.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\notion-test-hardening-deferred-scope-a7b4c9.md'
source_sha256: 9d92e84e333767786adfeb76e9494e74fb34c96eac482863389e7e785f1ef004
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-test-hardening-deferred-scope-a7b4c9
plan_type: testing
dod_exempt: false
status: Not Started
---

# Notion Test Hardening — Deferred Scope

All items explicitly deferred or surfaced-but-not-implemented across the two
Notion test-hardening sessions (sessions 2026-05-10). Nothing here should be implemented without a separate Author-Gate decision and wave plan.

DO_NOT_IMPLEMENT_GUARD: plan=notion-test-hardening-deferred-scope-a7b4c9 reason=requires Author-Gate decision before execution — D-3 through D-8 are unimplemented; executing without gate bypasses constitutional §6

---

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W1 | Wrong-plan guard for secondary writers | `apply_plan_derived_status.py`, `repair_notion_plan_statuses.py` | 🔲 TODO |
| W2 | Pagination hardening | `wave_lifecycle_writer.py`, `check_notion_plans_no_duplicates.py` | 🔲 TODO |
| W3 | Race-condition / idempotency hardening | `wave_lifecycle_writer.py`, `emit_from_markers` | 🔲 TODO |
| W4 | Retry / circuit-breaker tests | `tools/notion/_notion_retry.py`, `_notion_circuit_breaker.py` | 🔲 TODO |
| W5 | Drift-detector tests | `tools/notion/_notion_drift_detector.py` | 🔲 TODO |
| W6 | Property-validator tests | `tools/notion/_notion_property_validator.py` | 🔲 TODO |
| W7 | `pre_notion_plan_write_gate.py` gap-filling | `tests/unit/windsurf_scripts/test_pre_notion_plan_write_gate.py` | 🔲 TODO |
| W8 | Live-Notion integration smoke tests (opt-in) | All writers when `NOTION_TOKEN` set | 🔲 TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Wrong-plan guard for `apply_plan_derived_status.py` | `tools/notion/apply_plan_derived_status.py` | Requires same slug cross-check as `find_plan_page` | ~3K | 🔲 TODO |
| W1.P2 | Wrong-plan guard for `repair_notion_plan_statuses.py` | `tools/notion/repair_notion_plan_statuses.py` | Bulk-repair path reads page IDs from live DB — slug round-trip needed | ~3K | 🔲 TODO |
| W2.P1 | Pagination: cursor exhaustion in `find_plan_page` | `wave_lifecycle_writer.py` | Current `page_size=2` only fetches 2 rows; full cursor pagination not implemented | ~3K | 🔲 TODO |
| W2.P2 | Pagination: cursor exhaustion in `fetch_live_plans` (no-duplicates gate) | `check_notion_plans_no_duplicates.py` | `fetch_live_plans` must follow `next_cursor` until `has_more=false` to avoid missing rows | ~3K | 🔲 TODO |
| W2.P3 | Pagination: offset drift when rows inserted mid-cursor | `wave_lifecycle_writer.py` | If two plans are created between pages, cursor can skip rows — detect and warn | ~2K | 🔲 TODO |
| W3.P1 | Race condition: two `emit_from_markers` calls for same slug | `wave_lifecycle_writer.py` | Concurrent processes can both read the same `summary_rt` then both write — last write wins but interleaves | ~3K | 🔲 TODO |
| W3.P2 | Idempotency: duplicate markers in same response | `_wave_lifecycle_helpers.py` | `coalesce_specs` merges specs but does not detect repeated identical markers — summaries get double-appended | ~2K | 🔲 TODO |
| W4.P1 | Retry tests for `_post_json` / `_patch_json` transient 5xx | `tools/notion/_notion_retry.py` | Retry is implemented but not unit-tested for 429/503 backoff, max-retry cap, non-retryable 400 | ~3K | 🔲 TODO |
| W4.P2 | Circuit-breaker tests | `tools/notion/_notion_circuit_breaker.py` | Open/half-open/closed state transitions, trip threshold, reset timeout untested | ~3K | 🔲 TODO |
| W5.P1 | Drift-detector tests | `tools/notion/_notion_drift_detector.py` | Snapshot diff, staleness detection, auto-repair proposal untested | ~3K | 🔲 TODO |
| W6.P1 | Property-validator roundtrip tests | `tools/notion/_notion_property_validator.py` | Select/title/rich_text/checkbox property shapes — valid + malformed + missing keys | ~2K | 🔲 TODO |
| W7.P1 | `pre_notion_plan_write_gate.py` — `_query_notion_plans_db` error paths | `tests/unit/windsurf_scripts/test_pre_notion_plan_write_gate.py` | Query returning `{"id": "ERROR:..."}` shape is ambiguous — real error vs page with weird ID | ~2K | 🔲 TODO |
| W7.P2 | `pre_notion_plan_write_gate.py` — Logging audit path | Same file | `TestLogging.test_log_written` currently doesn't assert any log entry was written | ~1K | 🔲 TODO |
| W8.P1 | Live smoke: `find_plan_page` round-trip against real Notion | Requires `NOTION_TOKEN` | Opt-in only; validates actual DB ID, slug property name, filter semantics | ~3K | 🔲 TODO |
| W8.P2 | Live smoke: duplicate slug detection in real Plans DB | Requires `NOTION_TOKEN` | Run `check_notion_plans_no_duplicates.py --live` and assert 0 duplicates | ~2K | 🔲 TODO |

---

## Deferred Item Detail

### D-1 — Wrong-plan guard for `apply_plan_derived_status.py`

**Source**: `notion-test-hardening-session-c4d8f2` Verification-vs-Deferral, NEXT_STEP.

`apply_plan_derived_status.py` writes plan status to Notion by `page_id` obtained via a slug lookup but does **not** perform the slug cross-check that was added to `find_plan_page` in W2.P1 of the first session. If the lookup returns a page with a mismatched slug (DB corruption, Notion drift), the wrong plan gets patched.

**Fix required**: Extract the slug cross-check into a shared helper (`_assert_slug_matches`) and call it from `apply_plan_derived_status.py` before any `_patch_json` call.

**Tests required**:
- Mismatch detected → write aborted, event logged
- Match succeeds → write proceeds
- Page with no slug property → write proceeds (permissive)

---

### D-2 — Wrong-plan guard for `repair_notion_plan_statuses.py`

**Source**: `notion-test-hardening-session-c4d8f2` Verification-vs-Deferral, NEXT_STEP.

`repair_notion_plan_statuses.py` iterates over all plans in the DB and applies bulk status repairs. It resolves `page_id` by querying the DB and then patches each page. Same slug-mismatch risk as D-1 but at bulk scale.

**Fix required**: Verify slug on every page before patching; log and skip mismatches rather than aborting the whole run.

---

### D-3 — Pagination cursor exhaustion

**Source**: Web research (Notion API returns max 100 rows per call; `has_more + next_cursor` pattern required). Surfaced during `test_check_notion_plans_no_duplicates.py` gap-filling.

Current `fetch_live_plans` does a single POST with `page_size=100` and stops. Plans DB has >350 rows — only the first 100 are checked for duplicates.

**Fix required**: Loop on `has_more`, accumulating all pages before dedup analysis.

**Test required**: Mock three pages of 100/100/50 rows, assert all 250 slugs are evaluated.

---

### D-4 — Race condition / double-append in `emit_from_markers`

**Source**: Web research (Notion API has no atomic read-modify-write; concurrent callers both read old `summary_rt` then both POST overwrite).

**Fix required**: Add an ETag / `last_edited_time` guard — if the page changed between read and write, retry the read-modify-write cycle once.

---

### D-5 — Retry / circuit-breaker coverage

**Source**: `tools/notion/_notion_retry.py` and `_notion_circuit_breaker.py` exist but have zero unit tests (verified by `tests/unit/tools_notion/test_retry.py` and `test_circuit_breaker.py` stubs that were untracked as of session end).

**Fix required**: Wire the stub test files into the pytest collection and implement the test bodies.

---

### D-6 — Drift-detector and property-validator coverage

**Source**: `tools/notion/_notion_drift_detector.py` and `_notion_property_validator.py` exist but have zero unit tests.

---

### D-7 — `pre_notion_plan_write_gate.py` logging assertion gap

**Source**: `TestLogging.test_log_written` in `test_pre_notion_plan_write_gate.py` calls `verify_plan_identity` but does not assert any log file was written. The test currently only verifies no exception was raised.

**Fix required**: Assert that the JSONL log file received at least one line after a verification call.

---

### D-8 — Live-Notion integration smoke (opt-in)

**Source**: All hardening work so far is purely unit-level (mocked HTTP). No smoke test validates the actual Notion API schema hasn't drifted (e.g., `Slug` property renamed, `Status` property ID changed).

**Fix required**: Opt-in pytest mark (`@pytest.mark.notion_live`) that runs only when `NOTION_TOKEN` is set, hits the real Plans DB, and asserts the first result has the expected property shape.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Both secondary writers have slug cross-check | `grep -r "_assert_slug_matches" tools/notion/` returns ≥2 hits | 🔲 |
| DoD-2 | `fetch_live_plans` follows cursor until `has_more=false` | Test: 3-page mock, all 250 slugs evaluated | 🔲 |
| DoD-3 | Retry / circuit-breaker tests green | `pytest tests/unit/tools_notion/test_retry.py test_circuit_breaker.py` → 0 failures | 🔲 |
| DoD-4 | Drift-detector and property-validator tests green | `pytest tests/unit/tools_notion/test_drift_detector.py test_property_validator.py` → 0 failures | 🔲 |
| DoD-5 | Logging assertion gap closed | `test_log_written` asserts ≥1 JSONL line written | 🔲 |
| DoD-6 | Live smoke passes in CI with real token | `pytest -m notion_live` exits 0 | 🔲 |

---

## Verification-vs-Deferral

| Item | Why deferred further | Tracked in |
|---|---|---|
| Real Notion API schema validation | Requires live token + network; opt-in only | D-8 |
| ETag / last-edited-time concurrency guard | Requires Notion `retrieve page` extra call; latency tradeoff needs Author-Gate | D-4 |
| R1B / ChromaDB Notion sync | Out of scope for all Notion test hardening | Different domain |

PLAN_CREATED: slug=notion-test-hardening-deferred-scope-a7b4c9 path=.windsurf/plans/notion-test-hardening-deferred-scope-a7b4c9.md status=Not Started
