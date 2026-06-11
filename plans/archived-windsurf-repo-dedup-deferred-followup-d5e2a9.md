---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\repo-dedup-deferred-followup-d5e2a9.md'
original_relative_path: 'repo-dedup-deferred-followup-d5e2a9.md'
source_sha256: a800fddb27e738df5b0868441aaa032321b10e05bcb5bcaf572f3e759f303b64
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
title: "Repo Deduplication — Deferred Follow-up"
description: "Post-W1-W6 cleanup items: orphan plan analysis, archive lifecycle, and future consolidation opportunities."
status: Draft
created: 2026-05-06
---

# Repo Deduplication — Deferred Follow-up (d5e2a9)

Parent plan: [repo-wide-deduplication-c5d2a8](https://www.notion.so/repo-wide-deduplication-c5d2a8-35827693f55c81149803f822907c3434) (Completed)

## Goal

Address deferred cleanup items identified during W1-W6 execution that were out of scope for the initial deduplication pass.

## Deferred Scope Register

### DS1: Orphan Plan Analysis (P2)
**Source:** W2 gap — 257 files remain in `.windsurf/plans/` but only 4 are "live" per Notion

- **Count:** ~253 potentially orphaned plan files
- **Condition:** Files exist on disk but Notion shows no corresponding row, or status is stale
- **Risk:** Low — files are inert but clutter the plans folder
- **Remediation approach:**
  1. Cross-reference all 257 files against Notion Plans DB
  2. Identify true orphans (file exists, no DB row OR file exists, DB shows Retired/Archived without archive folder)
  3. Batch move confirmed orphans to `.windsurf/plans/_orphan_review/` for human triage
  4. After 30-day grace period, move to `.windsurf/plans/_archive/2026-orphaned/`

**Deferred reason:** W2 scope limited to Notion-verified Completed/Retired/Archived only

---

### DS2: Archive Lifecycle Policy (P3)
**Source:** W3 — archives/tools_archive_2026/ now contains 1,319 items

- **Gap:** No retention policy for archive contents
- **Recommendation:** 
  - 90-day: Compress archive folders >90 days to `.tar.gz`
  - 1-year: Move to cold storage (separate repo or S3)
  - 2-year: Delete (after verifying no active references)

**Deferred reason:** Requires archive reference audit before any deletion

---

### DS3: Plan Registration Backfill (P2)
**Source:** W2 orphan gap + §36 enforcement

- **Gap:** ~253 orphan plans likely lack Notion registration
- **Impact:** Cannot use `wave_execution_state.py start` on these plans until registered
- **Remediation:** Batch backfill script to create Notion rows for existing plans
  - Status: Draft (unknown live status)
  - Exists On Disk: true
  - Summary: Auto-generated from plan frontmatter

**Deferred reason:** Requires human review of each plan to set correct Status

---

### DS4: Future Rule Consolidation (P4)
**Source:** W6 audit — candidates identified but not actionable now

| Candidate Rules | Current State | Consolidation Trigger |
|-----------------|-------------|----------------------|
| plan-location.md + plan-registration-enforcement.md | Both stable | Merge if both unchanged for 90 days |
| notion-plans-taxonomy.md + notion-plan-wave-deferral.md | Both stable | Merge if taxonomy stabilizes |
| adg-graph-layer-enforcement.md + adg-hotspot-enforcement.md | Active development | Wait until ADG v2 complete |

**Deferred reason:** Rules are actively referenced; consolidation risk > benefit at this time

---

### DS5: Skills Registry Reconciliation (P3)
**Source:** W5 collapse — 24 child skills deleted, but references may persist

- **Action:** Search for lingering references to deleted skill paths
  - `.windsurf/skills/ledger-consulter-*/` (24 patterns)
  - In rules, workflows, and scripts
- **Remediation:** Update any hardcoded references to point to parent skill

**Deferred reason:** Reference search is non-blocking; skills are advisory only

---

## Non-Goals

- No new deduplication categories (scope is W1-W6 follow-up only)
- No archive deletion without 90-day review period
- No plan file deletion without human review

## Success Criteria

1. Orphan plan count documented with triage queue
2. Archive lifecycle policy documented and scheduled
3. Plan registration backfill script authored (even if not run)
4. Skills reference audit complete, no broken links

## Wave Structure

| Wave | Phase | Focus | Status |
|------|-------|-------|--------|
| W1 | P1 | Orphan plan cross-reference and triage queue | Not Started |
| W1 | P2 | Batch move orphans to _orphan_review/ | Not Started |
| W2 | P1 | Archive lifecycle policy document | Not Started |
| W2 | P2 | Compress 2026-04 archives | Not Started |
| W3 | P1 | Plan registration backfill script | Not Started |
| W3 | P2 | Backfill dry-run (no writes) | Not Started |
| W4 | P1 | Skills reference audit | Not Started |
| W4 | P2 | Reference fixes (if any found) | Not Started |

## Gap Register / Risks

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | Orphan triage may surface "zombie" active plans | Human review required before any archive |
| R2 | Archive compression may break scripts referencing paths | Use symlinks or update scripts first |
| R3 | Mass Notion registration may create duplicates | Dry-run with slug collision detection |

## Notes

This plan is **registration only** — no implementation without explicit user approval per wave.
