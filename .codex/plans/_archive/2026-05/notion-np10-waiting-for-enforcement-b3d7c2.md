---
slug: notion-np10-waiting-for-enforcement-b3d7c2
status: Completed
dod_exempt: false
---

# NP10 — Notion Plans Waiting-For Completeness Enforcement

## Goal

Enforce that every Plans DB row with `Status = "Waiting"` has a non-blank
`Waiting For` property. A blank `Waiting For` on a blocked plan is
unactionable — no one knows what to resolve.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | P1–P6 | Full enforcement stack | ~6k | Plans DB has `Waiting For` rich_text property | ✅ DONE | 43 tests pass; NP10 gate exits 0 |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | Pure logic helper | `_notion_plans_status_check.py` | Minimal — add `WaitingForViolation` + `decide_waiting_for()` | ~500 | ✅ Done |
| P2 | Live-DB check in NP2 gate | `check_notion_plans_status_canonical.py` | Add `_fetch_waiting_plans`, `_check_waiting_for_completeness`, wire into `main()` | ~800 | ✅ Done |
| P3 | Write-time post-cursor-agent audit | `post_cursor_agent_notion_plans_status_audit.py` | Add `_WAITING_FOR_RE` regex + `WAITING_EMPTY_WAITING_FOR` detection in `detect_violations()` | ~600 | ✅ Done |
| P4 | Standalone NP10 CI gate | `ops_scripts/ci/check_notion_plans_waiting_for.py` (new) | New file — offline-safe, bypass + fail-closed env vars | ~700 | ✅ Done |
| P5 | CI registration | `ops_scripts/ci/run_contract_gates.py` | Add NP10 entry after NP9 | ~100 | ✅ Done |
| P6 | Rule + tests | `notion-plans-taxonomy.md`, `test_notion_plans_status_check.py` | Rule NP10 section; 11 new test cases | ~500 | ✅ Done |

## Files In Scope

- `.cursor/scripts/_notion_plans_status_check.py`
- `.cursor/scripts/post_cursor_agent_notion_plans_status_audit.py`
- `.cursor/rules/notion-plans-taxonomy.md`
- `ops_scripts/ci/check_notion_plans_status_canonical.py`
- `ops_scripts/ci/check_notion_plans_waiting_for.py` (new)
- `ops_scripts/ci/run_contract_gates.py`
- `tests/unit/windsurf_scripts/test_notion_plans_status_check.py`

## Definition of Done

| # | Criterion | Verified |
|---|-----------|---------|
| DoD-1 | `decide_waiting_for(PLANS_DB_ID, "Waiting", "")` returns `WaitingForViolation` | ✅ |
| DoD-2 | `decide_waiting_for(PLANS_DB_ID, "Waiting", "ADR-085 approval")` returns `None` | ✅ |
| DoD-3 | 43 tests pass in `test_notion_plans_status_check.py` (11 new `decide_waiting_for` cases) | ✅ |
| DoD-4 | `python ops_scripts/ci/check_notion_plans_waiting_for.py` exits 0, reports 0 violations against live DB (12 Waiting plans, all populated) | ✅ |
| DoD-5 | NP10 registered in `run_contract_gates.py` assurance_gates list | ✅ |
| DoD-6 | `post_cursor_agent_notion_plans_status_audit.py` detects `WAITING_EMPTY_WAITING_FOR` when `Status=Waiting` written without `Waiting For` in invoke body | ✅ |

## Verification-vs-Deferral

| Item | Disposition |
|------|-------------|
| Live-DB query on `--query-notion` in NP2 gate | ✅ Implemented |
| Standalone NP10 gate with bypass/fail-closed | ✅ Implemented |
| Write-time detection in post-cursor-agent audit | ✅ Implemented |
| Auto-patch for blank Waiting For (similar to stale-status auto-patch) | ⏭ DEFERRED — see deferred-scope plan |
| TBD/unknown value heuristic ("TBD", "unknown" → still a violation) | ⏭ DEFERRED — listed in deferred-scope plan |
| Backlog Items DB parity (same rule for Backlog Waiting rows) | ⏭ DEFERRED |
