---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\hybrid-search-adg-seed-impl.md'
original_relative_path: 'hybrid-search-adg-seed-impl.md'
source_sha256: 3859725ea54bf809130f01b7e5c782f51bdab61580ca8b0efec1352127d12ade
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: hybrid-search-adg-seed-impl
plan_type: refactor
---

# HybridSearchEngine `adg_seed` Implementation

Implement the missing `adg_seed` method on HybridSearchEngine (referenced by E.F1.1 P1 row, impact 404.5).

---

## Evidence Sources

| Source | Why | Status |
|---|---|---|
| Wave/Phase row `E.F1.1` (P1, impact 404.5) | concrete consumer failure | ✅ captured |
| `agentic_core/.../HybridSearchEngine.py` | the class missing the method | 🔲 confirm path on execution |
| `hybrid-search-adg-seed-rerank-c58e21.md` | parent plan covering the design | ✅ |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|---------|
| W1 | Implement `adg_seed` | HybridSearchEngine | A | 3,000 🟢 |

---

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Add `adg_seed` method wired through to ADG retrieval path | HybridSearchEngine + adapter | AttributeError at runtime | ~3k | 🔲 TODO |

---

## Notes

Scaffold — the design already exists in `hybrid-search-adg-seed-rerank-c58e21`. This plan is the implementation-side counterpart. Consider merging the two rather than creating a separate file; if merged, update the Backlog row's Plan relation and archive this stub.

## Success Criteria

- [ ] E.F1.1 Backlog row transitions to Done
- [ ] `adg_seed` covered by a unit test that exercises the ADG path
