---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\plan-update-enforcement-template-fix-e7a3c1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\plan-update-enforcement-template-fix-e7a3c1.md'
source_sha256: f37d19a480b89f98ddb294a74f29d2081cae5651e1bd790e95ce33bdef02d0ad
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: plan-update-enforcement-template-fix-e7a3c1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: true
touches_plan_templates: true
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Plan Update Enforcement + Template Fix

Fix the three root causes that prevent wave/phase green-check updates from working, then revise the plan template to be enforcer-friendly with tables at the top.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: CLOSED
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-14

---

## Context (SCQA)

- **Situation** — The `post_cascade_wave_lifecycle_capture.py` hook + `_plan_wave_table_updater.py` are wired and running, but wave/phase green-check updates never actually appear in plan files.
- **Complication** — Three silent failure modes: (1) `SLUG_RE` rejects any slug that doesn't end in exactly 6 hex chars, so master plans and numerically-prefixed plans are silently dropped; (2) `_find_plan_file` only does an exact filename match, so `01_apps-rg-...md` is never found when slug=`apps-rg-...`; (3) S-series phase IDs (`S0`, `S1`…) don't match `_PHASE_ROW_RE` which only accepts `W`-prefix. Additionally the plan template buries status tables far below the context, making them hard for both humans and enforcement hooks to locate.
- **Question** — How do we make wave/phase completions automatically update the correct plan file tables, and make the template structure enforcer-friendly?
- **Answer** — Apply targeted hotfixes to the slug matching + file lookup + phase regex (already done as hotfixes), then restructure the template so status tables are the first thing after the header, and add auto-capture of test/scope additions per wave.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Slug matching + phase regex hotfixes | ✅ DONE | 0 (infrastructure only) | 3 |
| W2 | Template restructure | ✅ DONE | 0 | 1 |
| W3 | Auto-scope/test capture in hook + regression tests | ✅ DONE | 12 | 3 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Fuzzy slug lookup in _find_plan_file | ✅ DONE |
| W1.2 | Relax SLUG_RE for non-hex-suffix slugs | ✅ DONE |
| W1.3 | S-prefix phase support in _PHASE_ROW_RE | ✅ DONE |
| W1.4 | Unresolvable-slug warning in hook | ✅ DONE |
| W2.1 | Rewrite template: tables at top, plan_id discipline | ✅ DONE |
| W2.2 | Add Tests Added / Files Changed columns to wave table | ✅ DONE |
| W3.1 | Hook: extract test count delta from WAVE_COMPLETE note | ✅ DONE |
| W3.2 | Hook: append scope/test delta to plan wave table row | ✅ DONE |

---

## RCA Summary

### Root Cause 1 — SLUG_RE Too Strict (FIXED)

`SLUG_RE = r"^[a-z0-9][a-z0-9-]*-[0-9a-f]{6}$"` requires exactly 6 trailing hex chars.
Plans like `apps-rg-master-governed-runtime-hardening` or `01_apps-rg-master-...` are silently dropped by `parse_wave_lifecycle_markers()` before the file lookup is even attempted.

**Fix**: Relaxed to `r"^[a-z0-9_][a-z0-9_-]{3,}$"` — any kebab/underscore alphanum string ≥4 chars.

### Root Cause 2 — _find_plan_file Exact Match Only (FIXED)

`_find_plan_file(repo_root, slug)` only tried `.windsurf/plans/<slug>.md`. File `01_apps-rg-master-governed-runtime-hardening.md` is never found for slug `apps-rg-master-governed-runtime-hardening`.

**Fix**: Three-tier resolution:
1. Exact match `<slug>.md`
2. Strip numeric prefix (`01_`, `02-`, etc.) and match bare stem
3. Scan frontmatter `plan_id:` value for any `.windsurf/plans/*.md`

### Root Cause 3 — _PHASE_ROW_RE Only Matches W-Prefix (FIXED)

`_PHASE_ROW_RE` used `W\d+...` which never matches `S0`, `S1`, `S0.5` phase labels used in the active master plan.

**Fix**: Changed character class to `[WS]\d+...` to accept both W-series and S-series phase IDs.

### Root Cause 4 — Silent Failure (FIXED)

When a slug couldn't be resolved, the hook returned success with no output. Now `_warn_unresolvable_slugs()` emits a loud `WARN:` to stderr with the exact slug and marker kind.

### Root Cause 5 — Template Tables Buried (PENDING — W2)

Current template puts Wave Manifest at line ~44 and status tables don't exist as standalone sections. The updater's regex scans the whole file for `| W<N> |` rows — if the table is buried in "## Wave Overview" prose, it still works but is invisible to humans reviewing status. New template puts tables immediately after SCQA, before any wave detail.

### Root Cause 6 — No Auto-Capture of Test/Scope Additions (PENDING — W3)

When Cascade adds tests or new files during a wave and emits `WAVE_COMPLETE: plan=... wave=N note="+12 tests, 4 files"`, the hook writes the Notion Summary but doesn't update the plan's wave table with the test/scope data. W3 adds this.

---

## Wave 1 — Slug + Phase Hotfixes (COMPLETE)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Files changed**:
- `tools/notion/_wave_lifecycle_helpers.py` — SLUG_RE relaxed
- `tools/windsurf/_plan_wave_table_updater.py` — _find_plan_file 3-tier lookup + S-prefix _PHASE_ROW_RE
- `.windsurf/scripts/post_cascade_wave_lifecycle_capture.py` — _warn_unresolvable_slugs added

**Phases**:
- **W1.1** — Fuzzy slug lookup in _find_plan_file | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Relax SLUG_RE | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** — S-prefix _PHASE_ROW_RE | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.4** — Unresolvable-slug warning | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `WAVE_COMPLETE: plan=apps-rg-master-governed-runtime-hardening wave=9` resolves to `01_apps-rg-master-governed-runtime-hardening.md`
- `WAVE_COMPLETE: plan=plan-update-enforcement-template-fix-e7a3c1 wave=1` resolves to this plan's file
- `PHASE_COMPLETE: plan=apps-rg-master-governed-runtime-hardening phase=S6` updates the S6 row

---

## Wave 2 — Template Restructure

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Rewrite execution-plan-template.md: move Wave+Phase tables to top (after SCQA), add plan_id frontmatter discipline note, keep DoD at bottom | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Add "Tests Added" and "Files Changed" columns to wave table in template | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Status tables appear within the first 40 lines of a plan authored from the new template
- `plan_id:` frontmatter is populated and matches the filename stem
- Wave table has columns: Wave | Focus | Status | Tests Added | Files Changed

---

## Wave 3 — Auto-Scope/Test Capture in Hook

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Hook: parse test count delta from `note=` field (e.g. `+12 tests`) in WAVE_COMPLETE marker | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Hook: append test/scope delta to the plan's wave table row (Tests Added + Files Changed columns) | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `WAVE_COMPLETE: plan=foo-abc123 wave=2 note="+8 tests, 3 files"` causes the W2 row in the plan table to show `8` in Tests Added and `3` in Files Changed
- Columns absent from the table are skipped gracefully (no crash)

---

## Out Of Scope

- Backfilling existing plans with Tests Added / Files Changed data
- Migrating `01_apps-rg-master-governed-runtime-hardening.md` S-series phases to W-series
- Notion DB schema changes
- Changing how existing committed plans are named

---

## Definition of Done

DoD-1: All three silent-failure root causes resolved — WAVE_COMPLETE markers for master plans and S-series phases update the plan table
- Evidence: emit `WAVE_COMPLETE: plan=plan-update-enforcement-template-fix-e7a3c1 wave=1` in a response and verify this file's W1 row shows ✅ DONE
- Status: **DONE**

DoD-2: New template has status tables in the first 40 lines
- Evidence: read new template, count lines to first `| Wave |` table header
- Status: **DONE**

DoD-3: Hook warns loudly when slug is unresolvable
- Evidence: `_warn_unresolvable_slugs()` emits `WARN:` to stderr; covered by `test_warn_unresolvable_slug_emits_stderr`
- Status: **DONE**

DoD-4: No regressions in existing plan update behavior + regression tests added
- Evidence: 57/57 pass in `test_plan_wave_table_updater.py` (+12 new); 164/165 pass across hook + writer test suites; 1 remaining failure is pre-existing known debt (see below)
- Status: **DONE**

DoD-5: Note-column overwrite behavior correct + idempotency proven
- Evidence: `test_note_column_*` (fill/overwrite/preserve/nonnumeric/invalid/idempotent) all green; `test_wave_complete_idempotent` + `test_phase_complete_idempotent` green
- Status: **DONE**

DoD-6: `agentic_core/` untouched
- Evidence: zero edits to any file under `agentic_core/` this plan; confirmed by `git diff --name-only` scope
- Status: **DONE**

---

## Known Debt Register

### KD-1 — Pre-existing Hook Schema Test Failure

- **Test**: `tests/unit/windsurf_scripts/test_post_cascade_wave_lifecycle_capture.py::TestHooksJsonRegistration::test_hook_entry_schema_pure`
- **Status**: FAILING — pre-existing, not introduced by this plan
- **Cause**: Commit `809d847c2d` (`refactor(governance): consolidate windsurf rules + enrich hooks.json with full metadata`) enriched all hooks.json entries with governance metadata fields (`hook_id`, `lifecycle_stage`, `priority`, `entrypoint`, `blocking_mode`, `bypass_env_var`, `emits_receipt`, `owner_rule_ref`, `replacement_for`). The test still asserts the older minimal schema (`command`, `working_directory`, `show_output` only), per constitutional §27.
- **Evidence**: `git log --oneline -1 .windsurf/hooks.json` → `809d847c2d`; all hook entries in hooks.json carry the extra fields, not just the wave lifecycle entry.
- **Disposition**: Outside scope of this plan. Requires a separate contract decision: either (a) update the test to allow the enriched schema as the new §27-compliant surface, or (b) strip the extra keys from hooks.json back to minimal schema. Neither is a regression from this plan's changes.
- **Blocking this plan**: NO
