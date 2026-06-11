---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\query-progress-bar-backlog.md'
original_relative_path: 'query-progress-bar-backlog.md'
source_sha256: 96bc6191142d0d8677a28a2b33ffe24f1a81937380f263e1c66eb33238312a2b
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: query-progress-bar-backlog
plan_type: infra
---

# Query Progress Bar Backlog

Scaffold for the §16 (Query Progress Bar) compliance burndown — residual call sites in `ops_scripts/`, `tools/`, etc. that still lack progress reporting on loops >10 items or operations >5s.

---

## Evidence Sources

| Source | Why | Status |
|---|---|---|
| `.windsurf/rules/query-progress-bar.md` | policy SSOT | ✅ |
| `ops_scripts/ci/check_query_progress_bar.py` | gate that flags non-compliant sites | ✅ |
| `tools/progress_display.py` | canonical `ProgressReporter` | ✅ |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|---------|
| W1 | Inventory non-compliant sites | run check_query_progress_bar.py on full tree | A | 1,000 🟢 |
| W2 | Burn residuals | wrap loops with `ProgressReporter` / `tqdm` | B | 4,000 🟢 |

---

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Inventory — list every remaining violation | CI gate output | silent >5s ops | ~1k | 🔲 TODO |
| W2.1 | Burn residuals one module at a time | each violation site | monochrome output | ~4k | 🔲 TODO |

---

## Notes

Pre-existing rule §16 enforces this on new code via CI gate; this plan captures the **existing** non-compliant sites that pre-dated the rule. Treat as a ratchet — pick the noisiest 5 sites per session until CI gate reports zero.

## Success Criteria

- [ ] `python ops_scripts/ci/check_query_progress_bar.py` exits 0 with no violations
- [ ] All long-running loops emit a colored progress bar per §16
