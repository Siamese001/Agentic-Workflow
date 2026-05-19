---
plan_id: apps_rg_legacy_dependency_burndown
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg legacy dependency burndown

**Successor to:** [l2-rationalization-waves-c8e4f1.md](l2-rationalization-waves-c8e4f1.md) (W11 closed — no further archive under that plan)

**Handoff:** [w11_closeout_and_next_plan_handoff.md](../docs/reports/agent_inventory/w11_closeout_and_next_plan_handoff.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: D3_PARTIAL
LAST_UPDATED: 2026-05-19
NOTION_STATUS: In Progress
DISK_SSOT: .cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md
EVIDENCE_SSOT: docs/reports/agent_inventory/w11_closeout_and_next_plan_handoff.md

---

## Context

W11 completed **one** gated archive (L2 binding shim) and inventory/classification for 13 candidates. Remaining work is **dependency burn-down**, not archive expansion. All legacy paths remain **DO_NOT_DELETE** until fan-in zero and DELETE_GATE satisfied.

---

## Phases

| Phase | ID | Focus | Status |
|-------|-----|-------|--------|
| A | competencies contract | SRFS stub + X2=42 + one-spine proof_pool wiring + contract tests | ✅ DONE |
| B | PA parity | Sections SSOT; dispatch `*_pa` re-exports; parity tests | 🔲 MOSTLY DONE — verify lanes |
| C | Rg migration | `apps_eval` / contract strings → facades; keep Rg* unit tests | ✅ DONE |
| D | dispatch quarantine | Shrink `competencies_dispatch` / `ibm_narrative_dispatch` execution | ✅ DONE |
| D2 | helper fan-in | Extract shared helpers to `runtime/sections/`; dispatch re-exports | ✅ DONE |
| D3 | blockers + load_base_resume | Stub failure RCA; `lane_base_resume`; repair fan-in map | ⚠️ PARTIAL |
| E | gated archive | `validation_orchestrator` after 30d + CI baselines; others fan-in 0 | 🔲 BLOCKED |

---

## Hard rules

- No X2/X3 weakening; no forced ALLOW
- No archive/delete until DELETE_GATE
- No live apps_rg proof unless explicitly scoped
- Keep compatibility re-exports and wrappers

---

## First next action

**Phase D3 follow-up:** Harden offline stub + repair pipeline so `test_canonical_lane_mock_judge_x3_review_code` passes (≥2 terms/category after repair); then Phase E when fan-in zero.

## Phase D3 evidence

- [legacy_dependency_burndown_phase_d3.md](../docs/reports/apps_rg/legacy_dependency_burndown_phase_d3.md)
- [legacy_dependency_burndown_phase_d3.json](../docs/reports/apps_rg/legacy_dependency_burndown_phase_d3.json)

## Phase D2 evidence

- [legacy_dependency_burndown_phase_d2.md](../docs/reports/apps_rg/legacy_dependency_burndown_phase_d2.md)
- [legacy_dependency_burndown_phase_d2.json](../docs/reports/apps_rg/legacy_dependency_burndown_phase_d2.json)

## Phase D evidence

- [legacy_dependency_burndown_phase_d.md](../docs/reports/apps_rg/legacy_dependency_burndown_phase_d.md)
- [legacy_dependency_burndown_phase_d.json](../docs/reports/apps_rg/legacy_dependency_burndown_phase_d.json)

## Phase C evidence

- [legacy_dependency_burndown_phase_c.md](../docs/reports/apps_rg/legacy_dependency_burndown_phase_c.md)
- [legacy_dependency_burndown_phase_c.json](../docs/reports/apps_rg/legacy_dependency_burndown_phase_c.json)

---

## Evidence

- [w11_candidate_fanin_matrix.json](../docs/reports/agent_inventory/w11_candidate_fanin_matrix.json)
- [w11_gated_archive_delete_plan.md](../docs/reports/agent_inventory/w11_gated_archive_delete_plan.md)
- [w11_m4c_competencies_contract_fix.md](../docs/reports/agent_inventory/w11_m4c_competencies_contract_fix.md)
