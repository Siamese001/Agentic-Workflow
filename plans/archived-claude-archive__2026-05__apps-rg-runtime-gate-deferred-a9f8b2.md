---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-runtime-gate-deferred-a9f8b2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-runtime-gate-deferred-a9f8b2.md'
source_sha256: 282411a928abf6be67d38d67372fdf6c677e0893316aa8dce94d8a886f58770b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
description: Deferred scope from apps-rg-runtime-gate-catalog-c4d7e1
parent_plan: apps-rg-runtime-gate-catalog-c4d7e1.md
status: deferred
---

# apps_rg Runtime Gate Hardening — Deferred Scope

> **Parent Plan:** `apps-rg-runtime-gate-catalog-c4d7e1` (W0-W8 COMPLETED)  
> **This Plan:** Captures explicit non-goals and descoped items from parent execution

---

## 1. Deferred Scope Register

Items explicitly excluded as non-goals during W0-W8 implementation:

### P2 — High Priority (Near-term Blockers)

| ID | Item | Source | Blocker For |
|----|------|--------|-------------|
| P2.1 | Real LLM-judge scoring with Spearman ≥0.80 calibration | Parent plan W2 | Production judge reliability |
| P2.2 | Holdout vs dev eval-set separation | Parent plan W5 | Unbiased evaluation metrics |

### P3 — Medium Priority (Capability Gaps)

| ID | Item | Source | Context |
|------|------|--------|---------|
| P3.1 | Offline judge calibration pipeline | Non-goal throughout | Human-labeled reference data |
| P3.2 | DOCX exporter integration with gate hooks | Non-goal W7 | Native export validation |
| P3.3 | Production-log mining with PII redaction | Parent plan W5 | Privacy-preserving analytics |

### P4 — Lower Priority (Future Work)

| ID | Item | Source | Context |
|------|------|--------|---------|
| P4.1 | Per-app rubric migrations to new grader types | Parent plan | Schema ready; opt-in adoption |
| P4.2 | C0 FEC producer binding (5 grounded apps) | Deferred from eval-harness work | apps_research, apps_rfp, apps_qna, apps_exec, apps_underwriting_ai |

### P5 — Technical Debt / Cleanup

| ID | Item | Source | Note |
|------|------|--------|------|
| P5.1 | W8 validation false positives on module constants | W8 CI gate | 4 constants flagged as "broken" (FORBIDDEN_FILLERS, etc. — expected, not gates) |
| P5.2 | Edge case test refinements for floating point boundary conditions | W5 implementation | Tolerance rounding in length parity calculation |

---

## 2. Success Criteria (This Plan)

- [ ] All P2 items triaged to active plans or accepted as known gaps
- [ ] P3 items sized and scheduled for next quarter
- [ ] P4 items assigned to owning teams with opt-in timeline
- [ ] P5 technical debt acknowledged in relevant code comments

---

## 3. Non-Goals (Stay Out of Scope)

- ❌ New gate waves beyond W8
- ❌ Architectural changes to RuntimeGateEngine
- ❌ Cross-app gate consolidation (each app maintains own gate pack)

---

## 4. Related Documentation

- Parent Plan: `.cursor/plans/apps-rg-runtime-gate-catalog-c4d7e1.md`
- Commit: `d7585d0d2f` — feat(apps_rg): implement W0-W8 runtime gate hardening (206 tests)
- Location: `apps_rg/integrations/gates/` (6 modules, 28 gates)
- Tests: `tests/_apps_contract/test_w*.py` (9 files, 206 tests)
- CI Gate: `ops_scripts/ci/check_apps_rg_runtime_gate_hardening.py`
