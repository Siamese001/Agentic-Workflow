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
