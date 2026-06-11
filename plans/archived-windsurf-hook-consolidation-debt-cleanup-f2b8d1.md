---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\hook-consolidation-debt-cleanup-f2b8d1.md'
original_relative_path: 'hook-consolidation-debt-cleanup-f2b8d1.md'
source_sha256: 6225f5bf24b5ce06fc0ec6bf54e0e7c2fd66d2c611ea1be7ddf423260c894312
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: hook-consolidation-debt-cleanup-f2b8d1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Hook Consolidation Debt Cleanup — Remove Duplicate post_cascade_notion_plan_identity_audit

Remove the stale `post_cascade_notion_plan_identity_audit` hook entry from `hooks.json`.
It was declared replaced by `unified_notion_status_auditor` during W2.P1 consolidation but
never deleted, causing it to run concurrently at a higher priority (350 vs 340) and
creating audit race conditions on every post_cascade_response.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: CLOSED
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-05-14

---

## Context (SCQA)

- **Situation** — During plan `plan-lifecycle-procedures` W2.P1, `unified_notion_status_auditor`
  was registered as the survivor hook that consolidates `post_cascade_notion_plans_status_audit`
  and `post_cascade_notion_plan_identity_audit`. Its `replacement_for` array names both replaced
  hooks explicitly.
- **Complication** — The `post_cascade_notion_plan_identity_audit` entry was **never removed**
  from `hooks.json` (lines 1078–1095). It still runs at priority 350, one tick after the
  survivor at 340, producing duplicate audit passes and potential enforcement gaps if the stale
  hook fails or evaluates stale state.
- **Question** — How do we close the W2.P1 consolidation debt safely without breaking anything?
- **Answer** — Delete lines 1078–1095 (the entire `post_cascade_notion_plan_identity_audit`
  block) from `hooks.json`. Keep the `.py` script as a tombstone. Validate JSON. Done.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Delete stale hook entry + validate JSON | ✅ DONE | 0 | 1 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Delete lines 1078-1095 from hooks.json | ✅ DONE |
| W1.2 | Validate JSON integrity | ✅ DONE |
| W1.3 | Verify no references to the stale hook_id outside hooks.json | ✅ DONE |

---

## RCA

### Root Cause — W2.P1 Consolidation Debt

`unified_notion_status_auditor` was registered at commit `809d847c2d` with
`"replacement_for": ["post_cascade_notion_plans_status_audit", "post_cascade_notion_plan_identity_audit"]`.
The `post_cascade_notion_plans_status_audit` entry was correctly deleted at that time, but
`post_cascade_notion_plan_identity_audit` (lines 1078–1095) was overlooked and left in the
file. This is confirmed by:

- `unified_notion_status_auditor` at lines 942–964 with `"status": "consolidated"` and
  `"replacement_for"` naming the stale hook.
- `post_cascade_notion_plan_identity_audit` at lines 1078–1095 still carrying `"replacement_for": []`
  with no deprecation marker.

### Impact

| Impact | Severity |
|--------|----------|
| Both hooks fire on every post_cascade_response | Medium |
| Stale hook at priority 350 runs AFTER survivor at 340 | Medium |
| Potential duplicate or inconsistent audit log entries | Medium |
| Constitutional §27 schema: hooks.json must contain only official fields — extra entries for dead hooks are clutter | Low |

---

## Wave 1 — Delete Stale Hook Entry

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

### Phases

**W1.1** — Delete the 18-line `post_cascade_notion_plan_identity_audit` block (lines 1078–1095 inclusive, plus the trailing comma that joins it to the next entry) from `.windsurf/hooks.json`.

**W1.2** — Validate JSON: `python -c "import json; json.load(open('.windsurf/hooks.json', encoding='utf-8'))"` must exit 0.

**W1.3** — Confirm no active references to hook_id `post_cascade_notion_plan_identity_audit` remain in:
- `ops_scripts/ci/` (CI gate allow-lists)
- `tests/` (test fixtures referencing the hook_id)
- `.windsurf/hooks.json` (must be gone)
The `.py` script itself is kept as a tombstone — no deletion required.

### Acceptance

- `hooks.json` no longer contains `"hook_id": "post_cascade_notion_plan_identity_audit"`.
- `python -c "import json; json.load(open('.windsurf/hooks.json', encoding='utf-8'))"` exits 0.
- `unified_notion_status_auditor` still present with `"replacement_for"` array intact.

---

## Out Of Scope

- Deleting the `.windsurf/scripts/post_cascade_notion_plan_identity_audit.py` script (keep as tombstone).
- Renaming or changing the priority of `unified_notion_status_auditor`.
- Any change to `post_cascade_wave_completion_audit` or other hooks at priority 350.
- Fixing `test_hook_entry_schema_pure` in `test_post_cascade_wave_lifecycle_capture.py` — that is pre-existing KD-1 debt from `plan-update-enforcement-template-fix-e7a3c1`.
- Backfilling Notion audit logs.

---

## Definition of Done

DoD-1: `hooks.json` no longer contains `"hook_id": "post_cascade_notion_plan_identity_audit"`.
- Verification: `python -c "import json; d=json.load(open('.windsurf/hooks.json',encoding='utf-8')); assert not any(h.get('hook_id')=='post_cascade_notion_plan_identity_audit' for h in d.get('hooks',[])), 'stale hook still present'"`

DoD-2: `hooks.json` parses as valid JSON after the deletion.
- Verification: `python -c "import json; json.load(open('.windsurf/hooks.json', encoding='utf-8'))"`; exit 0.

DoD-3: `unified_notion_status_auditor` entry is untouched — `replacement_for` array still names both replaced hooks.
- Verification: manual read of lines 941–964 post-edit.

DoD-4: No test references to the stale hook_id that would now fail.
- Verification: `grep -r "post_cascade_notion_plan_identity_audit" tests/` returns zero matches.

DoD-5: `agentic_core/` untouched.
- Verification: zero edits to any file under `agentic_core/`.
