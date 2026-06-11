---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-legacy-dependency-burndown-b7e4a2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-legacy-dependency-burndown-b7e4a2.md'
source_sha256: 1058ee8736c47a96becc58b435c3005156172cf1f0132e56b6f767f188c4bc99
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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
PLAN_STATUS: COMPLETE
CURRENT_WAVE: C
LAST_COMPLETED_WAVE: C
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed
NOTION_RECONCILED: 2026-05-25
PLAN_COMPLETED: 2026-05-25
CLOSEOUT_CLASS: PHASES_ABC_DONE
PLAN_COMPLETE: plan=apps-rg-legacy-dependency-burndown-b7e4a2 note="competencies contract; PA parity; Rg migration"
DEFERRED_SCOPE: D3_stub_repair_hardening,Phase_E_archive_when_fanin_zero
CLOSEOUT_RECEIPT: docs/reports/plans/active_backlog_closeout_receipt_20260525.md
NOTION_PAGE_ID: 36527693-f55c-8178-8c13-f1c889dccaf1
NOTION_RECONCILED: 2026-05-24
ACTIVE_BACKLOG_MANIFEST: docs/reports/plans/active_in_progress_plans_manifest_20260524.md
ACTIVE_BACKLOG_ROLE: spine_child_p2
PARENT_PLAN: apps-rg-spine-only-unification-d8f4a2
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
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
