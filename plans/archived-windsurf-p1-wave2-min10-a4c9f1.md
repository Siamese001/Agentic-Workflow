---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\p1-wave2-min10-a4c9f1.md'
original_relative_path: 'p1-wave2-min10-a4c9f1.md'
source_sha256: dd530db90b81ff198000677cc35a3ece9d08b1c71605a61648989f3a43391491
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-18'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave 2 P1 Exception Hardening (Min 10 Files per Wave)

ADG-guided execution plan for reducing P1 `except Exception` anti-patterns in bounded waves of at least 10 files each.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| Wave 1 | 1.1, 1.2 | L1 model family (10 files) broad-catch narrowing | ~24K 🟢 | Snapshot `04182026_0738` remains canonical | 🔄 IN PROGRESS | 10 files patched, `py_compile` pass, no `except Exception` in wave files |
| Wave 2 | 2.1, 2.2 | Next 10 ADG-ranked P1 files outside current family | ~24K 🟢 | Same patch pattern remains behavior-safe | 🔲 TODO | 10 additional files patched + verification |
| Wave 3 | 3.1, 3.2 | Cross-layer remaining P1 tails (L0/L5) | ~24K 🟢 | No blocking architecture conflicts | 🔲 TODO | 10 additional files patched + verification |
| Wave 4 | 4.1, 4.2 | Residual queue + reconciliation rerun | ~24K 🟢 | ADG rerun available for progress delta | 🔲 TODO | Updated ADG burndown deltas + final queue |

**Token estimation source**: `python tools/utils/planning/token_estimator.py --demo --json` (green: projected 20,028 tokens baseline).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| 1.1 | ADG ranking + wave queue freeze | `artifacts/adg/adg_indexed_04182026_0738.sqlite`, `artifacts/adg/issues/p1_high_antipattern_rows_04182026_0738.json` | Quoting-safe SQL extraction, noisy mixed antipattern symbols | ~3K | ✅ DONE |
| 1.2 | Patch Wave 1 (10 L1 model files) | `agentic_core/L1_cognition/reasoning/ml_decision_support/models/*.py` (selected set) | Preserve fallback behavior while narrowing exception tuples | ~21K | 🔄 IN PROGRESS |
| 2.1 | Patch Wave 2 (next 10 files) | ADG-ranked P1 files outside Wave 1 set | Non-uniform handler semantics across layers | ~12K | 🔲 TODO |
| 2.2 | Verify and reconcile ADG deltas | Compile + grep + ADG refresh artifacts | Queue drift after edits | ~12K | 🔲 TODO |
| 3.1 | Patch Wave 3 core tails | Remaining high-density P1 files | Higher blast radius in shared infra paths | ~12K | 🔲 TODO |
| 3.2 | Verify and rerank | Verification + queue update | Residual false positives from historical snapshot | ~12K | 🔲 TODO |
| 4.1 | Final residual wave | Last 10+ candidates | Edge-case fallback contracts | ~12K | 🔲 TODO |
| 4.2 | Burndown closure report | ADG burndown + next queue | Must show measurable P1 delta | ~12K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Wave 1 Target Set (Min 10)

1. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/advanced_c0_reranker.py`
2. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/advanced_l0_router.py`
3. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/advanced_l6_detector.py`
4. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/base_model.py`
5. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/c0_reranker.py`
6. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/c1_query_optimizer.py`
7. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/l5_risk_calibrator.py`
8. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/l6_anomaly_detector.py`
9. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/multi_layer_coordinator.py`
10. `agentic_core/L1_cognition/reasoning/ml_decision_support/models/semantic_cache_classifier.py`

---

## Rules

- Keep changes behavior-preserving; only narrow broad exception handlers.
- Use scoped operational exceptions (`AttributeError`, `KeyError`, `OSError`, `RuntimeError`, `TypeError`, `ValueError`) unless path-specific alternatives are required.
- Verify each wave with `py_compile` and `grep_search` (`except Exception` == zero for wave file set).

---

## Success Criteria

- [ ] Wave 1: all 10 target files patched
- [ ] Wave 1: compile verification passes
- [ ] Wave 1: grep verification shows no `except Exception` in wave files
- [ ] Updated queue prepared for Wave 2
