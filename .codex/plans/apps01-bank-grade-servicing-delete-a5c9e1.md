---
plan_id: apps01-bank-grade-servicing-delete-a5c9e1
plan_format: v2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps01 Bank-Grade Servicing App Deletion

Delete the standalone `apps_01_bank_grade_servicing_ai_worker_runtime` prototype and remove its stale governance scan justification.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
CURRENT_WAVE: NONE
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-06-13

PLAN_CREATED: slug=apps01-bank-grade-servicing-delete-a5c9e1 path=.codex/plans/apps01-bank-grade-servicing-delete-a5c9e1.md status=In Progress

NOTION_PAGE_ID: 37e27693-f55c-819a-935f-d1271b727b18
NOTION_PAGE_URL: https://app.notion.com/p/37e27693f55c819a935fd1271b727b18

---

## Context (SCQA)

- **Situation** - `apps_01_bank_grade_servicing_ai_worker_runtime` is a standalone prototype/reference app at repo root. It is not listed in the ADR-082 canonical apps taxonomy, and repo pytest discovery only targets top-level `tests/`.
- **Complication** - The app still contributes a stale infra-wiring exception comment, and its runtime source is ignored by the repo-wide `src/` ignore rule, so ordinary `git rm` does not remove the full local tree.
- **Question** - How do we delete the app immediately without leaving stale references or hidden ignored runtime files?
- **Answer** - Remove the tracked app files, clean the ignored local runtime tree, update the stale scanner comment, then prove no live references remain.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | Immediate app deletion | ~4K | User approved immediate deletion on 2026-06-13 | DONE | App tree absent, stale scanner comment removed, reference checks clean outside plan history |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Remove tracked and ignored app files | DONE |
| W1.2 | Clean stale infra scanner justification | DONE |
| W1.3 | Verify references and scanner gate | DONE |

---

## Out Of Scope

- Changes to canonical `apps_*` packages.
- Changes to `agentic_core`.
- Regenerating ADG reports or ratchet baselines.
- Editing unrelated dirty worktree files.

---

## Wave 1 - Immediate App Deletion

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: USER_APPROVED
CHECKPOINT: A

**Authorization**: USER_APPROVED - User approved immediate deletion after the plan-first evidence pass.

**Phases**:
- **W1.1** - Remove tracked and ignored app files | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Clean stale infra scanner justification | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** - Verify references and scanner gate | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `apps_01_bank_grade_servicing_ai_worker_runtime/` is absent from the filesystem.
- `rg` finds no active references to the deleted app path/name outside archived plan history, if any.
- `ops_scripts/ci/infra_wiring_scan.py` no longer cites the deleted app.
- `python ops_scripts/ci/infra_wiring_scan.py` exits 0.

---

## Evidence

- ADG MCP was unavailable in Codex; fallback used `artifacts/adg/adg_indexed_06132026_0847.sqlite`.
- Fallback ADG showed 17 modules under the app and no external concrete source-file edges into the app path.
- Literal search found one active cleanup target: `ops_scripts/ci/infra_wiring_scan.py`.
- `git ls-files apps_01_bank_grade_servicing_ai_worker_runtime` showed 10 tracked files.
- `git check-ignore -v apps_01_bank_grade_servicing_ai_worker_runtime/src/runtime/agent.py` showed `.gitignore:94:src/`, so local runtime files require explicit ignored-tree cleanup.

---

## Definition of Done

DoD-1: App removed
- Evidence: `Test-Path apps_01_bank_grade_servicing_ai_worker_runtime` returns false.
- Status: DONE

DoD-2: Stale references removed
- Evidence: `rg -n "apps_01_bank_grade_servicing_ai_worker_runtime|Bank-Grade Servicing|servicing_ai" . --glob "!plans/**" --glob "!.codex/plans/**" --glob "!docs/archive/**"` returns no matches.
- Status: DONE

DoD-3: Governance scanner remains green
- Evidence: `python ops_scripts/ci/infra_wiring_scan.py` ran; it fails on pre-existing `apps_rg` infra-import and stale ADG structural findings, not on this deleted app. `rg` confirms the scanner no longer names the deleted app.
- Status: DONE_WITH_CAVEAT

DoD-4: Worktree review completed
- Evidence: `git status --short` shows only intended app deletion and scanner/plan edits in this scope, plus pre-existing unrelated dirty files.
- Status: DONE

---

## Closeout

PHASE_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 phase=W1.1
PHASE_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 phase=W1.2
PHASE_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 phase=W1.3
WAVE_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 wave=W1 note="+0 tests, app deleted, scope=apps01-delete"
PLAN_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 note="Standalone apps_01 prototype removed; stale scanner justification cleaned; reference checks clean outside plan history; infra scanner still fails on pre-existing apps_rg findings."

---

## Supersedes

| Predecessor slug | Reason |
|---|---|

_None - net-new plan._

---

## Marker Quick Reference

WAVE_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 wave=W1 note="+0 tests, app deleted, scope=apps01-delete"
PHASE_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 phase=W1.1
PHASE_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 phase=W1.2
PHASE_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 phase=W1.3
PLAN_COMPLETE: plan=apps01-bank-grade-servicing-delete-a5c9e1 note="Standalone apps_01 prototype removed; stale scanner justification cleaned; reference and scanner checks completed."
