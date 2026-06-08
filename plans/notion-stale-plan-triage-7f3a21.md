---
plan_type: governance
dod_exempt: true
---

# Notion Stale-Plan Triage — Not Started + Lower Priority

## Context (SCQA)

- **Situation:** The Notion Plans DB (`ac53d31b-3068-4039-9ebe-856c12caab32`) held 13 `Not Started`
  and 5 `Lower Priority` rows — many created weeks ago and referencing the now-removed `.cursor/plans/`
  tree (files migrated to `.claude/plans/`).
- **Complication:** Old `Not Started`/`Lower Priority` rows accumulate as a graveyard. The user wants a
  per-plan recommendation: **complete the scope, or retire it** — and for the "not" cases, adjust the
  Notion status to `Retired`/`Completed` with an explanatory comment.
- **Question:** For each of the 18 stale rows, is the scope (a) already done → `Completed`,
  (b) obsolete/superseded/won't-do → `Retired`, or (c) genuinely-still-pending live work → keep `Not Started`?
- **Answer:** Investigate each plan's on-disk file + git/code evidence, classify, then write the Notion
  status + a comment for every row not left as-is.

## Status Tables

### Wave Progress

| Wave | Focus | Status | Success Criteria |
|------|-------|--------|------------------|
| W1 | Scope + on-disk reality (query Notion, locate files) | Completed | 18 rows enumerated; disk paths resolved |
| W2 | Per-plan evidence investigation (fan-out) | Completed | Each plan classified COMPLETE/RETIRE/KEEP with evidence |
| W3 | Notion writeback (status + comment) | Completed | 6 Completed + 2 Retired written with comments; 10 KEEP untouched |
| W4 | Report recommendation table inline | Completed | User-facing table delivered |
| W5 | Pointer correction (stale Plan File Path) | Completed | apps-lic-linkedin-qwen pointer + Exists On Disk fixed |
| W6 | Branch cleanup (misnamed merged branches) | Completed | 2 stale codex/*linkedin-qwen* branches deleted |
| W7 | RCA — "15 visible vs 10 KEEP" reconciliation | Completed | RC-1 scope (In Progress excluded), RC-2 status-class, RC-3 Lower-Priority option deleted (2 rows nulled) |

## Triage outcome (18 rows)

**COMPLETE → Completed (6):** windsurf-tree-deletion-ci-parity-b8e4f1 · exec-summary-judge-display-override-parity-7c3e8a ·
exec-summary-rc-narrative-quality-c4e9a1 · skills-graph-hardening-gap-closure-53576c · qwen-prompt-regen-reduction-7481e3 ·
adg-mv-materialization-perf-b3d9f1

**RETIRE → Retired (2):** qwen3-32b-vllm-upgrade-d7a3f1 · l6-alignment-deferred-scope-c5e8a7

**KEEP (10):** apps-lic-c0-c03-redesign-refactor-plan · apps-lic-linkedin-qwen-refactor-a9c4e2 ·
apps-rg-aig-e2e-remediation-e4b7c1 · legacy-windsurf-tree-decommission-9f2c47 · cursor-naming-rename-w5-b4f1a9 ·
cursor-windsurf-codeium-decommission-dec0de · apps_rg-lean-core-binding-a1b2c3 ·
exec-summary-failed-run-persistence-notion-e7c4b2 · agent-capability-spine-harvest-e8f4a2 (was Lower Priority) ·
agent-inventory-deferred-followup-c2a8f1 (was Lower Priority)

## RCA — "I see 15 (Not Started or In Progress), not 10"

- **RC-1 (scope):** Original ask covered Not Started + Lower Priority only. The **7 In Progress** rows were never in scope → account for 7 of 15.
- **RC-2 (status-class/filter):** My 10 KEEP = 8 Not Started + 2 Lower Priority. User filter "Not Started or In Progress" drops the 2 LP, adds 7 IP → 8 + 7 = 15.
- **RC-3 (concurrent schema change):** The `Lower Priority` Status option was deleted from the Plans DB after the triage (by the `feat/notion-supersession-auto-retire` worktree effort), nulling the 2 KEEP LP rows (`agent-capability-spine-harvest-e8f4a2`, `agent-inventory-deferred-followup-c2a8f1`) → now `Status=null`, invisible to all filters.

## Definition of Done
(dod_exempt — governance/curation plan, no executable surface)

- DoD-1: All 18 rows have an evidence-backed COMPLETE/RETIRE/KEEP verdict. ✅
- DoD-2: Every COMPLETE/RETIRE row written in Notion (status + comment). ✅
- DoD-3: Recommendation table delivered inline to the user. ✅
- DoD-4: No KEEP row mutated (status). ✅
- DoD-5: Each Notion comment cites the decisive reason (done / superseded-by / obsolete-tech). ✅

## Open follow-ups (awaiting user direction)

1. Fix the 2 orphaned null-status rows (recommend `Not Started`, or `Retired`).
2. Triage the 7 In Progress plans the same way (out of original scope).
