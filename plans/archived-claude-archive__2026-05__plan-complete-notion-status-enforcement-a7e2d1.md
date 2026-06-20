---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\plan-complete-notion-status-enforcement-a7e2d1.md'
original_relative_path: '_archive\\2026-05\\plan-complete-notion-status-enforcement-a7e2d1.md'
source_sha256: 8acce84804e6f7b149a1b1c1ee3ab9a16928998a118cd4f236f1985c81862334
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: plan-complete-notion-status-enforcement-a7e2d1
plan_type: governance
dod_exempt: false
---

# RCA + Fix: Plan-Complete Notion Status Enforcement

Harden the plan-complete lifecycle so Notion status reliably flips to "Completed" when a plan finishes, closing the gap exposed by `apps-lic-quarantine-u0-coverage-review-d9f4a2`.

---

## Context (SCQA)

- **Situation** — Three automation paths exist to flip a plan's Notion status to "Completed": (1) `wave_execution_state.py complete`, (2) `PLAN_COMPLETE:` marker → `post_cursor_agent_wave_lifecycle_capture.py` hook, (3) `post_cursor_agent_plan_complete_audit.py` advisory warning. The code in `_wave_lifecycle_helpers.py` line 302-309 correctly flips `plan_complete` → `Completed`.

- **Complication** — Plan `apps-lic-quarantine-u0-coverage-review-d9f4a2` completed all 11 waves but Notion remained at `Archived`. Root cause chain: (A) plan was pre-emptively set to `Archived` with a stale context note before W8–W10 resumed, (B) `wave_execution_state.py start/complete` was never called — plan predates the wave-lifecycle autosync and was driven by ad-hoc user instructions, (C) the `PLAN_COMPLETE:` marker was emitted in the previous response but the hook either had no `NOTION_TOKEN` available, the HTTP PATCH failed silently (fail-open), or the hook did fire but the plan had already been manually fixed before verification. The capture log shows only test entries — no real invocation for this plan's slug.

- **Question** — How do we ensure that when a plan is done, its Notion status reaches "Completed" regardless of which execution path was used?

- **Answer** — Add a belt-and-suspenders CI gate (`NP-PLAN-DONE-STATUS`) that detects plans with all waves ✅ on disk but Notion status ≠ Completed, plus harden the `PLAN_COMPLETE:` hook with visible logging when token is missing.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `tools/notion/_wave_lifecycle_helpers.py:302-309` | `plan_complete` flip logic | ✅ REVIEWED |
| `tools/plan_lifecycle/wave_execution_state.py:448-519` | `_cmd_complete` deferred-scope reconciliation | ✅ REVIEWED |
| `.cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py` | Hook that parses `PLAN_COMPLETE:` markers | ✅ REVIEWED |
| `artifacts/cursor/wave_lifecycle_capture.jsonl` | No real entries for this plan slug | ✅ REVIEWED |
| `.cursor/hooks.json` | Hook registered, show_output=false | ✅ REVIEWED |
| Plan `apps-lic-quarantine-u0-coverage-review-d9f4a2` Notion row | Was `Archived`, manually patched to `Completed` | ✅ REVIEWED |

---

## RCA — Failure Chain

```
1. Plan created → registered in Notion (unknown initial status)
2. Plan set to "Archived" + stale "Waiting For" note (before W8-W10 work)
3. W8–W10 executed via ad-hoc user instructions (no wave_execution_state.py start/complete)
4. PLAN_COMPLETE: marker emitted in Cursor Agent response
5. post_cursor_agent_wave_lifecycle_capture.py hook:
   - Either NOTION_TOKEN absent → skipped silently (no stderr, show_output=false)
   - Or HTTP PATCH failed → swallowed (fail-open policy)
   - Or hook didn't receive the response text (payload extraction issue)
6. Result: Notion stayed at "Archived" until manual MCP API-patch-page
```

**Root cause**: No enforcement layer catches "all waves done on disk + Notion ≠ Completed". The hook is best-effort/fail-open by design, and `wave_execution_state.py complete` is opt-in.

**Contributing factors**:
- Plan was prematurely archived by prior context (stale assessment)
- Hook has `show_output: false` — failures are invisible
- No CI gate validates disk-vs-Notion status convergence for completed plans

---

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W1 | Hook observability + plan_complete_audit hardening | 2 files | ✅ DONE |
| W2 | CI gate: disk-vs-Notion status divergence for completed plans | 1 new file + registration | ✅ DONE |
| W3 | Rule update + verification | 1 rule file + tests | ✅ DONE |

**Estimated tokens: ~15K total.**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Add visible stderr warning in `post_cursor_agent_wave_lifecycle_capture.py` when `NOTION_TOKEN` is absent | 1 file | Silent skip makes failures invisible | ~3K | ✅ DONE |
| W1.P2 | Add visible stderr warning in `wave_lifecycle_writer.emit_from_markers` when token is absent | 1 file | Same silent-skip pattern | ~2K | ✅ DONE |
| W2.P1 | New CI gate `check_plan_done_notion_status.py` | 1 new file in `ops_scripts/ci/` | Detects all-waves-done on disk + Notion ≠ Completed | ~5K | ✅ DONE |
| W2.P2 | Register gate in `run_contract_gates.py` | 1 file | Advisory, fail-closed via env var | ~1K | ✅ DONE |
| W3.P1 | Update `notion-plan-wave-deferral.md` rule with RCA reference | 1 rule file | Document failure mode | ~2K | ✅ DONE |
| W3.P2 | Verify all hooks + gate green | test run | End-to-end confirmation | ~2K | ✅ DONE |

---

## Files In Scope

| File | Action | Wave |
|------|--------|------|
| `.cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py` | Add token-absent warning | W1 |
| `tools/notion/wave_lifecycle_writer.py` | Add token-absent warning | W1 |
| `ops_scripts/ci/check_plan_done_notion_status.py` | NEW — CI gate | W2 |
| `ops_scripts/ci/run_contract_gates.py` | Register NP-DONE gate | W2 |
| `.cursor/rules/notion-plan-wave-deferral.md` | Add RCA reference | W3 |

---

## Out Of Scope

- Changing the fail-open policy of the hook (by design — hooks must never block Cursor Agent)
- Making `wave_execution_state.py start/complete` mandatory for all plans (too disruptive for ad-hoc work)
- Retroactively fixing other plans with stale Notion status (separate maintenance task)
- Changing `show_output` on the wave lifecycle capture hook (it's noisy by design)

---

## Definition of Done

| DoD | Criteria | Verification | Status |
|-----|----------|-------------|--------|
| DoD-1 | `post_cursor_agent_wave_lifecycle_capture.py` emits `[wave_lifecycle_capture] WARN: NOTION_TOKEN not set` to stderr when token absent | Code review + test | 🔲 TODO |
| DoD-2 | `wave_lifecycle_writer.py` emits similar warning | Code review | 🔲 TODO |
| DoD-3 | `check_plan_done_notion_status.py` detects all-done-on-disk + Notion ≠ Completed | Dry run against Plans DB | 🔲 TODO |
| DoD-4 | Gate registered in `run_contract_gates.py` as advisory | `python ops_scripts/ci/run_contract_gates.py` exits 0 | 🔲 TODO |
| DoD-5 | Rule updated with RCA reference | File review | 🔲 TODO |

### Verification vs Deferral

| Item | Verify Now | Defer | Reason |
|------|-----------|-------|--------|
| Hook stderr output | ✅ | | Can test locally |
| CI gate dry-run | ✅ | | Needs NOTION_TOKEN but can mock |
| Retroactive plan status repair | | ✅ | Separate maintenance sweep |

---

## Gap Register

| Gap ID | Description | Severity | Status |
|--------|-------------|----------|--------|
| GAP-001 | No CI gate for disk-vs-Notion status divergence on completed plans | HIGH | OPEN → W2 |
| GAP-002 | Hook silently skips when NOTION_TOKEN absent | MEDIUM | OPEN → W1 |
| GAP-003 | Plans can be prematurely archived while still having open work | LOW | DEFERRED |
