# Backlog Linkage Followup

**Slug**: `backlog-linkage-followup-c2e9f3`
**Status**: Live
**Type**: Notion data-hygiene + governance
**Parent context**: Followup to `backlog-plan-linkage-enforcement-a4b2f1`. Closes 3 deferred items.

## Goal

Close the last residual true-orphan Backlog rows (MCP-BACKLOG rows with no Plan File slug — NP3 flags them advisory). Promote NP3 gate to fail-closed once orphan count == 0.

## Scope

**In scope**
- Backlog Items DB (`aa8d2507-101e-4384-81d9-60ea3fe33876`) — patch 3 true orphans.
- `ops_scripts/ci/run_contract_gates.py` — update NP3 comment to reflect fail-closed readiness.
- `.cursor/rules/notion-backlog-plan-linkage.md` — update fill-rate table to reflect completion.

**Out of scope**
- Authoring new plan markdown files for orphan rows.
- Changes to Wave/Phase Convergence semantics.
- Any apps-eval or certification work.

## Non-Goals

- Re-running the full backfill scripts (W1/W3 of parent plan — already completed).
- Any new CI gate or new script file.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | 1.1 | Identify + patch 3 true orphans via Notion API | ~2k | MCP-BACKLOG rows exist in Backlog DB; catch-all plan page 35527693-f55c-81f0-be31-dad3f36fa674 is available | ✅ Done | 0 true orphans; NP3 gate shows 0 violations |
| W2 | 2.1 | Promote NP3 to fail-closed via env var documentation + gate comment update | ~1k | Orphan count == 0 before this wave | ✅ Done | NP3 comment updated; BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1 documented |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| 1.1 | Orphan patch | Notion API — Backlog Items patch (3 rows) | Identifying exact page IDs of orphans | 2k | Done |
| 2.1 | NP3 fail-closed promotion | `ops_scripts/ci/run_contract_gates.py`, `.cursor/rules/notion-backlog-plan-linkage.md` | None | 1k | Done |

## Gap Register

1. **Orphan identification** — exact page IDs must be read from live Backlog DB (NP3 artifact or direct query).
2. **Catch-all plan page** — `35527693-f55c-81f0-be31-dad3f36fa674` (created W2 of parent plan) used as relation target.

## ADG_HOTSPOT_REPORT

N/A — Notion data-hygiene; no production code modules affected. Same stance as parent plan.

## ADG_GRAPH_LAYER_EVIDENCE

N/A — see above.

## Success Criteria

1. **0 true orphans** in Backlog DB (NP3 gate returns 0 violations).
2. **NP3 gate documentation** updated to note fail-closed readiness.
3. **Rule file** fill-rate table updated to reflect 100% Plan File.

## AI Summary

- Target: Notion Backlog Items DB — close 3 residual true-orphan rows + promote NP3 gate.
- Closes: DEFERRED_SCOPE from backlog-plan-linkage-enforcement-a4b2f1 (3 orphans + NP3 fail-closed).
- New files: none.
- Edits: Notion API patch (3 rows), `ops_scripts/ci/run_contract_gates.py` comment, `.cursor/rules/notion-backlog-plan-linkage.md`.
- Pattern source: backlog-plan-linkage-enforcement-a4b2f1. 2 waves, ~3k tokens.
- Non-goals: no new scripts, no new gates, no app behavior changes.
- Success: NP3 gate 0 violations; rule updated.

## References

- Parent plan: `.cursor/plans/backlog-plan-linkage-enforcement-a4b2f1.md`
- CI gate: `ops_scripts/ci/check_notion_backlog_plan_linkage.py`
- Rule: `.cursor/rules/notion-backlog-plan-linkage.md`
- Catch-all plan page: `35527693-f55c-81f0-be31-dad3f36fa674`
