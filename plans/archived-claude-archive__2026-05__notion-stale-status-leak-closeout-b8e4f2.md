---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\notion-stale-status-leak-closeout-b8e4f2.md'
original_relative_path: '_archive\\2026-05\\notion-stale-status-leak-closeout-b8e4f2.md'
source_sha256: 197f3cee3b014353f5e75a4109a6891f1a6ccaf0a87951406acc4aa523cac95b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-stale-status-leak-closeout-b8e4f2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Notion Plans stale status leak closeout (Active / Deprioritized)

RCA and code hardening so `Active` and `Deprioritized` cannot be written to the Plans DB Status field again after UI cleanup.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W2
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed

---

## Context (SCQA)

- **Situation** — Plans DB canonical Status options are `In Progress`, `Not Started`, `Lower Priority`, `Waiting`, `Completed`, `Retired`, `Archived`. Notion auto-creates unknown Select names on write.
- **Complication** — Legacy `Active` and `Deprioritized` reappeared in the Notion UI (stale docs, sync scripts, and auditor auto-patch to `Deferred`).
- **Question** — How do we stop re-leak after manual UI deletion?
- **Answer** — SSOT stale map + forbidden set in `_notion_plans_status_check.py`, auditor imports SSOT, fix all writers/docs, user deletes orphan options in Notion UI.

---

## Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | RCA + SSOT stale map (`Active`, `Deprioritized`, `Deferred`) | ✅ DONE | +3 status-check cases | scripts, auditor, CI |
| W2 | Writer/doc fixes + receipt + Notion Completed | ✅ DONE | backfill/freshness | tools/notion, AGENTS, config |

---

## W1 — SSOT and auditor

WAVE_ID: W1
WAVE_STATUS: DONE

- `FORBIDDEN_PLANS_STATUSES`: `Active`, `Deprioritized`
- `STALE_EQUIVALENTS`: `Active` → `In Progress`; `Deprioritized`/`Deferred` → `Lower Priority`
- `unified_notion_status_auditor.py` imports from `_notion_plans_status_check` (no local `Deferred` canonical)

WAVE_COMPLETE: plan=notion-stale-status-leak-closeout-b8e4f2 wave=W1 note="+3 tests, 12 files, scope=notion-status-ssot"

---

## W2 — Closeout

WAVE_ID: W2
WAVE_STATUS: DONE

- User removed stale Select options in Notion UI
- Receipt: [notion_stale_status_leak_closeout_receipt_20260525.md](docs/reports/plans/notion_stale_status_leak_closeout_receipt_20260525.md)
- Notion sync: [plan_notion_sync_notion_stale_status_leak_closeout.py](tools/notion/plan_notion_sync_notion_stale_status_leak_closeout.py)

WAVE_COMPLETE: plan=notion-stale-status-leak-closeout-b8e4f2 wave=W2 note="receipt+notion, scope=closeout"

PLAN_COMPLETE: plan=notion-stale-status-leak-closeout-b8e4f2

---

## Out Of Scope

- Retroactive repair of every historical Plans row (use `repair_notion_plan_statuses.py` ad hoc)
- Backlog Items DB schema option deletion in Notion UI
