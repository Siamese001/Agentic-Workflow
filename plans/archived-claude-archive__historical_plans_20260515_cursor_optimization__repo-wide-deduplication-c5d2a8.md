---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\repo-wide-deduplication-c5d2a8.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\repo-wide-deduplication-c5d2a8.md'
source_sha256: d9c71509881877fdd254a882f03c81d32274fb5f7a913c0398e24900f51304b1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Repo-Wide Deduplication — Consolidation Plan

**Slug:** `repo-wide-deduplication-c5d2a8`
**Status:** In Progress  
**Parent:** None

## Goal

Reduce organizational debt across `.windsurf/`, `scripts/`, `tools/`, `docs/reports/`, and archive roots. Estimated reduction: ~1,800 files + ~3,500 lines from skill collapse.

## Files In Scope

- `.windsurf/plans/` — 333 .md files (many Completed in Notion but on-disk)
- `docs/reports/plans/` — 146 parallel plan-reports
- `tools/archive/` — 1,217 files / 10.68 MB
- `archives/` — 533 files / 4.47 MB
- `scripts/` — 22 misrouted files (per SSOT allowlist)
- `.windsurf/skills/ledger-consulter-*/` — 24 duplicate sibling skills
- `.windsurf/rules/` — 2 deprecated shims + potential consolidations
- `docs/reports/rcas/` + `docs/reports/rca/` — duplicate RCA folders
- `docs/reports/runtime_cert/` + `runtime_certification/` — duplicate folders

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | A | Trivial dedup: deprecated rules, RCA folders, runtime_cert folders | ~2k | Zero callers to update | Pending | 13 files moved/deleted, 2 rules gone |
| W2 | B | Archive completed/retired plans from `.windsurf/plans/` | ~4k | Notion Plans cache queryable | Pending | ~180 files moved to `_archive/` |
| W3 | C | Consolidate `tools/archive/` + `archives/` | ~6k | `archives/` is canonical per §12 | Pending | 1,750 files under single root |
| W4 | D | Move 22 misrouted `scripts/` files to canonical folders | ~8k | All callers identifiable via grep | Pending | 22 files moved, constitutional §32 updated, CI green |
| W5 | E | Collapse 24 `ledger-consulter-*` skills to parent + registry | ~5k | No external references to skill paths | Pending | 23 skills deleted, 1 parent skill updated |
| W6 | F | Read-pass rule families (adg-*, author-gate-*) for consolidation | ~3k | Conditional rules may stay distinct | Pending | Decision table per family: keep/fold |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| A | Trivial dedup sweep | 13 files, 2 deprecated rules | Folder renames, rule deletions | 2k | Pending |
| B | Plans archive wave | `.windsurf/plans/*.md` filtered by Notion status | Bulk move, path preservation | 4k | Pending |
| C | Archive root consolidation | `tools/archive/*` → `archives/` | 1,750 files, verify zero importers | 6k | Pending |
| D | Scripts SSOT routing | 22 files from `scripts/` to `tools/cert/`, `ops_scripts/ci/`, `ops_scripts/maintenance/` | Caller updates, constitutional §32 edit | 8k | Pending |
| E | Ledger-consulter collapse | 24 skills → 1 parent + registry | Skill index rebuild, content merge | 5k | Pending |
| F | Rule family read-pass | `adg-*.md` (6 files), `author-gate-*.md` (4 files) | Content audit, not file moves | 3k | Pending |

## Non-Goals

- **Not deleting tier-shim verifiers** (`scripts/verify_tier*.py`) — they are subsumed by the aggregator but still required as subprocess targets.
- **Not touching CI workflow logic** — only file paths in callers.
- **Not consolidating the 193 `ops_scripts/ci/check_*.py` files** — orthogonal surface, defer until a check-fail cascade.
- **Not touching `adg-ci-gates.yml`** — already consolidated per previous plan.

## Gap Register / Risks

| Risk | Mitigation |
|---|---|
| Caller path string missed in grep | Use `rg -F` with every old path; CI dry-run before push |
| Constitutional §32 path references | Include in Phase D grep-replace; gate blocks on mismatch |
| Notion Plans cache stale | `check_plan_registration_freshness.py --refresh` before Phase B |
| External skill references to `ledger-consulter-*` | Phase E starts with `rg "ledger-consulter-" .windsurf/skills/ --include "*.md"` |

## Success Criteria

- File count: 32 → 15 workflows (already done, this plan doesn't touch)
- Plan count: 333 → ~150 live (remaining archived)
- Archive roots: 2 → 1
- Scripts folder: 65 → 43 (22 moved)
- Skills: 92 → ~69 (23 collapsed)
- Rules: 43 → 41 (2 deprecated deleted) + potential family merges
- RCA folders: 2 → 1
- runtime_cert folders: 2 → 1

## Deduplication Findings Table (Reference)

| # | Category | Evidence | Severity | Remediation |
|---|---|---|---|---|
| 1 | Plans accumulation | 333 .md files, 126 from 2026-04, 207 from 2026-05 | High | W2: Archive Completed/Retired to `_archive/<YYYY-MM>/` |
| 2 | Reports parallel archive | 146 files in `docs/reports/plans/` | Medium | W2: Same `_archive/` pattern |
| 3 | Two archive roots | `tools/archive/` 1,217 files + `archives/` 533 files | Medium | W3: Move all to `archives/` |
| 4 | ADG one-shots in archive | 61 files in `tools/archive/adg_root_oneshots_w5.10/` | Low | W3: Roll into consolidated archive move |
| 5 | 24 ledger-consulter skills | Near-identical 50–150 line siblings | Medium | W5: Collapse to parent + registry table |
| 6 | Deprecated rule shims | `anti-pattern-hitl-gate.md` (removal 2026-07-21), `agents-memory-lifecycle.md` (removal 2026-08-01) | Low | W1: Delete after `rg` confirmation |
| 7 | RCA folder duplication | `rcas/` (10) + `rca/` (3) | Low | W1: `git mv rcas/* rca/` |
| 8 | runtime_cert duplication | `runtime_cert/` (0) + `runtime_certification/` (1) | Low | W1: `git mv` the 1 file, delete empty |
| 9 | Scripts legacy concentration | 22 files NOT on SSOT allowlist | Medium | W4: Move per §31 routing; update constitutional §32 |
| 10 | 6 adg-* rules | Potential overlap with `adg-canonical-invariants` (always_on) | Medium | W6: Read-pass, decision per file |
| 11 | 4 author-gate-* rules | Overlap in enforcement/decision-points/svp-calibration | Medium | W6: Read-pass, `queue-drain` stays separate |
| 12 | 3 notion-* rules | Likely distinct (linkage vs deferral vs taxonomy) | Low | W6: Confirm in read-pass |
| 13 | 2 plan-* rules | `plan-location` (always_on) + `plan-registration-enforcement` (conditional) | Low | W6: Confirm distinct |

## Notes

Pattern source: `ssot-folder-enforcement.md` (§31) defines the canonical taxonomy. Constitutional §32 names specific `scripts/` paths that require coordinated update if moved. All moves preserve git history via `git mv`.
