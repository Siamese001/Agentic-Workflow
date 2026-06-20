---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-agentic-core-binding-hardening-b7e3f1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-agentic-core-binding-hardening-b7e3f1.md'
source_sha256: 5fb9ea1796f9d6131f3112b2c5dcff61a05fabbb179126384f6c42d5f27eb2aa
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-agentic-core-binding-hardening-b7e3f1
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg ↔ agentic_core Critical Binding Hardening (W-A)

Implements blocking authority ambiguity fixes from [overlap review](docs/reports/apps_rg/apps_rg_agentic_core_binding_overlap_review_20260522.md): import SSOT, L1 advisory route_hints, disposition_authority labeling, rollup spine preference, rigor-critical X2 convergence, AG-2 direct bindings, legacy shim deletion.

> **plan_id discipline**: `apps-rg-agentic-core-binding-hardening-b7e3f1` matches filename stem.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W-A
LAST_COMPLETED_WAVE: W-A
LAST_UPDATED: 2026-05-22
PLAN_COMPLETE: 2026-05-22

---

## Waves

| Wave | Scope | Status |
|------|--------|--------|
| W-A | Critical binding hardening (6 items) | ✅ COMPLETE |

### W-A deliverables

1. Import SSOT — repo-wide forbid `agentic_core.*apps_rg_*_binding`; canonical `apps_rg.runtime.bindings.*`
2. L1 route_hints `ADVISORY_ONLY`; L0 `RouteContract` sole route authority
3. `disposition_authority` on lane/spine receipts; rollup prefers `exit_disposition_receipt.json`
4. Rigor-critical registry guard + runtime X2 `BLOCK` injection
5. AG-2 `apps_rg_dispatch` direct c0/pa imports
6. Deleted six legacy core shims after caller burndown

**Closeout:** [apps_rg_binding_hardening_critical_closeout_receipt.md](docs/reports/apps_rg/apps_rg_binding_hardening_critical_closeout_receipt.md)

**Proof:** `python -m pytest tests/_apps_contract/test_apps_rg_binding_import_ssot.py tests/_apps_contract/test_apps_rg_l1_route_authority_advisory.py tests/_apps_contract/test_apps_rg_ag2_direct_binding_import.py tests/_apps_contract/test_apps_rg_disposition_authority_receipts.py tests/_apps_contract/test_apps_rg_rigor_critical_runtime_bundle_guard.py tests/_apps_contract/test_apps_rg_rigor_convergence_runtime_write.py tests/_apps_contract/test_apps_rg_package_rollup_exit_authority.py -q` → 30 passed

---

## Deferred (out of scope)

- W-B..W-E from overlap review (ValidatedRequest move, judge relocation, L2 collapse, eval redesign)
- LIVE_RUNTIME_PROOF integrated spine run
- Golden-path `briefing_artifact_ref` / e2e smoke enum fixes

---

PLAN_COMPLETE: plan=apps-rg-agentic-core-binding-hardening-b7e3f1 waves=W-A status=PASS proof=CONTRACT_TEST_PROOF
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
