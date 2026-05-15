---
plan_id: plan-complete-marker-enforcement-d2e9f1
plan_type: governance
dod_exempt: false
---

# Plan COMPLETE Marker Enforcement

Enforce that Cursor Agent always emits a `PLAN_COMPLETE: plan=<slug>` marker (or calls `wave_execution_state.py complete`) when all plan tasks are done, so Notion status auto-flips to `Completed` without manual intervention.

---

## Context (SCQA)

- **Situation** — The wave-lifecycle auto-sync machinery (`post_cascade_wave_lifecycle_capture.py` + `tools/notion/wave_lifecycle_writer.py`) is fully functional. A `PLAN_COMPLETE: plan=<slug>` marker in any Cursor Agent response triggers a direct-HTTP PATCH that flips the Plans DB row to `Completed`. The hook fires on every `post_cascade_response` event (line 246 of `hooks.json`).
- **Complication** — Cursor Agent routinely finishes all plan tasks and closes the session without emitting the marker. Root cause confirmed 2026-05-10: `notion-np10-deferred-scope-c8f1a4` was left at `Not Started` after all 7 DS items were implemented and tested. The Notion row had to be patched manually. No existing post-cascade audit script detects "plan appears done but `PLAN_COMPLETE:` was never emitted."
- **Question** — How do we make Cursor Agent reliably emit `PLAN_COMPLETE: plan=<slug>` when a plan's work is finished, with a CI/audit backstop that catches omissions?
- **Answer** — Three-layer enforcement: (1) a new post-cascade audit hook `post_cascade_plan_complete_audit.py` that warns when a response's todo list goes all-completed without a `PLAN_COMPLETE:` marker; (2) a CI gate `check_plan_complete_marker_freshness.py` that detects Plans DB rows stuck in `In Progress` longer than a staleness threshold; (3) a rule addition to `notion-plan-wave-deferral.md` making the marker emission explicit and machine-checkable.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/scripts/post_cascade_wave_lifecycle_capture.py` | Existing hook that processes `PLAN_COMPLETE:` — confirms machinery works | ✅ |
| `tools/notion/_wave_lifecycle_helpers.py` | `patch_for_marker` decision matrix — `plan_complete` always flips to `Completed` | ✅ |
| `.windsurf/hooks.json` line 246 | Confirms hook is registered; `show_output=false` — silent when no markers found | ✅ |
| `.windsurf/rules/notion-plan-wave-deferral.md` | Constitutional rule requiring lifecycle markers; needs `PLAN_COMPLETE:` added explicitly | ✅ |
| RCA 2026-05-10 | `notion-np10-deferred-scope-c8f1a4` stuck `Not Started`; manual patch required | ✅ |

---

## Wave Structure

| Wave | Scope | Focus | Status |
|------|-------|-------|--------|
| W1 | `post_cascade_plan_complete_audit.py` + rule update | New post-cascade audit hook + `notion-plan-wave-deferral.md` addition | 🔲 |
| W2 | `check_plan_complete_marker_freshness.py` + gate registration | CI gate for long-stale `In Progress` rows + `run_contract_gates.py` entry | 🔲 |
| W3 | Tests + DoD verification | Unit tests for both new scripts; DoD sweep | 🔲 |

---

## Out Of Scope

- Backfilling `PLAN_COMPLETE:` markers for already-completed plans (Notion rows are already correct).
- Modifying `wave_lifecycle_writer.py` or `_wave_lifecycle_helpers.py` — the processing machinery is correct.
- Enforcing `WAVE_START:` / `WAVE_COMPLETE:` markers — this plan focuses only on the `PLAN_COMPLETE:` gap.
- Changing when `show_output` is true/false on `post_cascade_wave_lifecycle_capture.py`.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | post-cascade audit hook | `.windsurf/scripts/post_cascade_plan_complete_audit.py` (NEW) | Must detect "todo-list all-completed + no PLAN_COMPLETE: in response" heuristic reliably | ~8K | 🔲 TODO |
| 1.2 | Rule update | `.windsurf/rules/notion-plan-wave-deferral.md` | Add `PLAN_COMPLETE:` to the explicit marker grammar + enforcement table | ~2K | 🔲 TODO |
| 2.1 | CI gate | `ops_scripts/ci/check_plan_complete_marker_freshness.py` (NEW) | Query Plans DB for rows In Progress > 14 days with no recent wave-log entry | ~8K | 🔲 TODO |
| 2.2 | Gate registration | `ops_scripts/ci/run_contract_gates.py` | Add NP12 gate entry after NP11 | ~1K | 🔲 TODO |
| 3.1 | Tests | `tests/unit/windsurf_scripts/test_post_cascade_plan_complete_audit.py` (NEW) | Cover: no marker + all-done → warn; marker present → silent; partial done → silent | ~6K | 🔲 TODO |
| 3.2 | DoD verification | All new files | Run tests + gate sweep | ~2K | 🔲 TODO |

---

## Gap Register

**GAP-1: No audit detects "response closes plan work without PLAN_COMPLETE: marker"**
- `post_cascade_wave_lifecycle_capture.py` is purely reactive — it processes markers when present; it does NOT warn when expected markers are absent.
- Impact: Notion rows stay at `In Progress` or `Not Started` indefinitely; manual patch required.

**GAP-2: No CI gate detects stale `In Progress` plans in Notion**
- `check_notion_plans_status_canonical.py` (NP3) checks for non-canonical status strings but does NOT flag plans that have been `In Progress` with no recent activity.
- Impact: Completed plan work goes unregistered in Notion until someone notices.

**GAP-3: `notion-plan-wave-deferral.md` does not explicitly require `PLAN_COMPLETE:`**
- The rule documents `wave_execution_state.py complete` and the marker grammar in the `Sanctioned non-MCP path` section, but the marker is not listed as a hard requirement with enforcement language.
- Impact: Cursor Agent treats the marker as optional prose; no author-gate fires when it is omitted.

---

## Execution Plan

### Phase 1.1 — Post-cascade plan-complete audit hook

**Scope**: New script `.windsurf/scripts/post_cascade_plan_complete_audit.py`.

Heuristic: scan the Cursor Agent response text for both:
1. A "todo_list all-completed" signal — the response contains a `todo_list` tool call where every item has `"status": "completed"`.
2. Absence of a `PLAN_COMPLETE:` marker at line-start.

When both conditions hold, emit a `WARN` to stderr and log to `artifacts/windsurf/plan_complete_audit.jsonl`. **Never block** (fail-soft, exit 0 always).

Bypass: `PLAN_COMPLETE_AUDIT_BYPASS=1`.
Fail-closed: not applicable (advisory only; the purpose is visibility, not blocking).

Register in `hooks.json` under `post_cascade_response` with `show_output: true`.

**Acceptance**: Script exits 0 on all inputs; WARN fires when todo-all-done + no marker; silent otherwise.

### Phase 1.2 — Rule update: notion-plan-wave-deferral.md

**Scope**: `.windsurf/rules/notion-plan-wave-deferral.md`.

Add to the "Protocol" section (after step 4):

> ⛔ **`PLAN_COMPLETE:` marker is mandatory when all plan tasks complete in a single session.** If `wave_execution_state.py complete` is not called, emit `PLAN_COMPLETE: plan=<slug-6hex>` as a bare line in the final response. Omission = status enforcement failure. Enforced by `post_cascade_plan_complete_audit.py` (advisory warn) and CI gate NP12.

Also add `PLAN_COMPLETE:` to the marker grammar table.

**Acceptance**: Rule prose unambiguously requires the marker; no prior constraint removed.

### Phase 2.1 — CI gate: check_plan_complete_marker_freshness.py

**Scope**: New file `ops_scripts/ci/check_plan_complete_marker_freshness.py`.

Logic:
- Query Plans DB for rows with `Status = In Progress`.
- For each, check `last_edited_time`: if > `_STALE_DAYS` (default 7) ago, check `wave_lifecycle_capture.jsonl` for a recent `apply_spec_patch` event with `reason` containing `plan_complete`.
- If no such event found → `WARN: plan <slug> has been In Progress for N days with no PLAN_COMPLETE marker`.

Advisory by default. Fail-closed via `NOTION_PLAN_COMPLETE_FAIL_CLOSED=1`. Bypass via `NOTION_PLAN_COMPLETE_BYPASS=1`. Skips when `NOTION_API_KEY` / `NOTION_TOKEN` unset.

Emits: `artifacts/ci/plan_complete_marker_freshness.json`.

**Acceptance**: Gate runs; exits 0 advisory; correct rows flagged; token unset = skip.

### Phase 2.2 — Gate registration

**Scope**: `ops_scripts/ci/run_contract_gates.py`.

Add after NP11:

```python
# NP12 -- Plans stuck In Progress without a PLAN_COMPLETE marker for >7d.
# Advisory. Fail-closed: NOTION_PLAN_COMPLETE_FAIL_CLOSED=1.
# Bypass: NOTION_PLAN_COMPLETE_BYPASS=1. Skips offline CI.
(
    "NP12 Notion Plans PLAN_COMPLETE marker freshness (advisory)",
    "ops_scripts/ci/check_plan_complete_marker_freshness.py",
),
```

**Acceptance**: Gate entry appears in `run_contract_gates.py`; runs without error on dry invocation.

### Phase 3.1 — Unit tests

**Scope**: `tests/unit/windsurf_scripts/test_post_cascade_plan_complete_audit.py` (NEW).

Test cases:
1. Response with todo-all-completed + no `PLAN_COMPLETE:` → WARN logged.
2. Response with todo-all-completed + `PLAN_COMPLETE: plan=foo-abc123` present → no WARN.
3. Response with mixed todo statuses (some pending) + no `PLAN_COMPLETE:` → no WARN.
4. Response with no todo_list at all → no WARN.
5. Bypass env var set → no WARN regardless.
6. `PLAN_COMPLETE:` in prose (mid-sentence) vs line-start → only line-start triggers suppress.

**Acceptance**: All 6+ tests pass; zero regressions in sibling test files.

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | `post_cascade_plan_complete_audit.py` warns when todo-all-done + no marker in same response | `pytest tests/unit/windsurf_scripts/test_post_cascade_plan_complete_audit.py -v` | 🔲 |
| DoD-2 | `check_plan_complete_marker_freshness.py` exits 0 (offline, token unset) | `python ops_scripts/ci/check_plan_complete_marker_freshness.py` with no `NOTION_TOKEN` set | 🔲 |
| DoD-3 | NP13 registered in `run_contract_gates.py` | `grep "NP13" ops_scripts/ci/run_contract_gates.py` exits 0 | 🔲 |
| DoD-4 | Hook registered in `hooks.json` | `python -c "import json; d=json.load(open('.windsurf/hooks.json')); assert any('plan_complete_audit' in c['command'] for c in d['hooks']['post_cascade_response'])"` | 🔲 |
| DoD-5 | `notion-plan-wave-deferral.md` rule updated | Rule contains `PLAN_COMPLETE:` in the Protocol section with `⛔` enforcement language | 🔲 |
| DoD-6 | All new tests pass; zero regressions | `pytest tests/unit/windsurf_scripts/ -v` — N pass, 0 fail | 🔲 |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Backfill PLAN_COMPLETE for historic completed plans | Notion rows already show Completed; no functional gap | Not tracked — no action needed |
| Enforcing WAVE_START / WAVE_COMPLETE markers | Separate concern; those only affect Summary log lines, not Status | NEXT_STEP if desired |
| Fail-closed mode for NP12 | Advisory baseline first; flip after ≥7 days clean data | `NOTION_PLAN_COMPLETE_FAIL_CLOSED=1` gate mechanism already wired |

---

## Rules

- New scripts follow SSOT folder routing: `post_cascade_*` → `.windsurf/scripts/`; `check_*` → `ops_scripts/ci/`.
- Both new scripts must be fail-soft (exit 0 always); they are observers, not blockers.
- Bypass env vars must be documented inline and in the rule.
- `hooks.json` edit must re-read the file before editing to avoid stale-content corruption (precedent: NP10 session hooks.json incident).
- No changes to `wave_lifecycle_writer.py` or `_wave_lifecycle_helpers.py` — processing machinery is correct.
