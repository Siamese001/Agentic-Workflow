---
plan_id: l7-section-shim-legacy-removal-followup-a9c4e2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# L7 section shim legacy removal follow-up

Close the open migration scope from `l7-auditability-overlap-cleanup-4f8c2d`: make legacy section-shim emission explicitly controllable, verifiable, and documented without breaking legacy readers.

> **plan_id discipline:** `plan_id` = filename stem `l7-section-shim-legacy-removal-followup-a9c4e2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W2
LAST_UPDATED: 2026-06-07

PLAN_CREATED: slug=l7-section-shim-legacy-removal-followup-a9c4e2 path=.claude/plans/l7-section-shim-legacy-removal-followup-a9c4e2.md status=Not Started

---

## Context (SCQA)

- **Situation** - The L7 boundary hardening plan completed provenance, refs-only trust, app-scoped preferred names, evidence package flags, and negative-control verification.
- **Complication** - The closeout intentionally deferred stopping legacy section-shim writes by default because many section readers still consume legacy names such as `route_contract.json`, `compiled_prompt_artifact.json`, `runtime_exhaust_bundle.json`, and `x3_disposition.json`.
- **Question** - How do we close that open scope safely without pretending every downstream reader has migrated in one step?
- **Answer** - Add an explicit migration control to the section package finalizer, keep read compatibility, prove preferred-only cleanup in tests, record open-scope status in a tracked list and receipt, and update Notion after verification.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1-W0.2 | Open-scope list and migration decision | ~2k | Open scope is legacy shim write removal only | DONE | Open scope list exists and names residual risk |
| W1 | W1.1-W1.3 | Migration control implementation | ~5k | Package finalizer is safest choke point | DONE | Preferred-only mode removes legacy shim files after mirroring |
| W2 | W2.1-W2.2 | Verification and closeout | ~3k | Focused tests are sufficient for migration control | DONE | Tests pass, receipt exists, Notion updated |

### Phase Progress

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Create open-scope list | `docs/reports/apps_rg/l7_boundary_open_scope_20260607.md` | Must distinguish closed vs deferred scope | ~1k | DONE |
| W0.2 | State migration policy | Open-scope list + plan | Avoid overclaiming downstream migration | ~1k | DONE |
| W1.1 | Add migration mode resolver | `apps_rg/runtime/section_evidence_package.py` | Env parsing must be deterministic and safe | ~2k | DONE |
| W1.2 | Add preferred-only cleanup | `section_evidence_package.py` | Remove only known legacy shims after preferred mirror exists | ~2k | DONE |
| W1.3 | Add tests | `tests/unit/apps_rg/test_section_evidence_package.py`, contract namespace tests | Must prove both compatibility and preferred-only modes | ~1k | DONE |
| W2.1 | Run focused verification | Existing boundary/package suites | Avoid unrelated dirty-worktree failures | ~1k | DONE |
| W2.2 | Emit receipt and update Notion | `artifacts/certification/apps_rg_l7_open_scope_followup_receipt.json` | Artifacts are gitignored, plan/Notion must reference them | ~2k | DONE |

---

## Open Scope List

| ID | Scope | Status | Implementation Target |
|---|---|---|---|
| OS-1 | Stop legacy section shim writes by default | OPEN | Add explicit `preferred_only` finalizer mode that removes known legacy shim files after preferred mirrors exist |
| OS-2 | Keep legacy reads during migration | OPEN | Preserve `_preferred_or_legacy_ref` and existing downstream legacy readers |
| OS-3 | Prove package metadata reports migration mode | OPEN | Extend evidence package tests |
| OS-4 | Record closeout receipt and Notion follow-up | OPEN | Emit receipt and patch Notion plan row |

---

## Out Of Scope

- Removing every downstream legacy read in this pass.
- Renaming canonical core L7 artifacts.
- Editing unrelated failing tests or unrelated dirty worktree files.
- Deleting historical artifacts already emitted with legacy names.

---

## Wave 0 - Open-scope list

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W0.1** - Write tracked open-scope list and decision note.
- **W0.2** - Mark downstream legacy read removal as out of scope for this pass.

**Acceptance**:
- Open-scope report exists and points back to the parent plan.

---

## Wave 1 - Migration control implementation

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W1.1** - Add a deterministic migration mode resolver.
- **W1.2** - Add preferred-only cleanup that deletes only known legacy shim files after preferred mirrors exist.
- **W1.3** - Add tests for default compatibility mode and preferred-only mode.

**Acceptance**:
- Default mode remains compatibility-safe.
- Preferred-only mode removes only the known legacy shim files that have preferred mirrors.
- Package metadata records mode, mirrored files, and removed legacy files.

---

## Wave 2 - Verification and closeout

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W2.1** - Run focused package/boundary tests.
- **W2.2** - Emit closeout receipt and patch Notion to `Completed`.

**Acceptance**:
- Focused tests pass.
- Receipt records `preferred_only_mode_supported: true`.
- Notion Plans row is `Completed`.

---

## Definition of Done

DoD-1: Open-scope list exists
- Evidence: `docs/reports/apps_rg/l7_boundary_open_scope_20260607.md`
- Status: PASS

DoD-2: Migration control implemented
- Evidence: `apps_rg/runtime/section_evidence_package.py` exposes compatibility and preferred-only modes.
- Status: PASS

DoD-3: Tests pass
- Evidence: focused pytest selectors for section evidence package and namespace tests exit 0.
- Status: PASS

DoD-4: Receipt exists
- Evidence: `artifacts/certification/apps_rg_l7_open_scope_followup_receipt.json`
- Status: PASS

DoD-5: Notion updated
- Evidence: Plans row for this slug reads back as `Completed`.
- Status: PASS

---

## Scope Expansion Authorization

```
DISCOVERED_SCOPE: plan=l7-section-shim-legacy-removal-followup-a9c4e2 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=l7-section-shim-legacy-removal-followup-a9c4e2 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=l7-section-shim-legacy-removal-followup-a9c4e2 reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## Marker Quick Reference

```
WAVE_START: plan=l7-section-shim-legacy-removal-followup-a9c4e2 wave=<N>
WAVE_COMPLETE: plan=l7-section-shim-legacy-removal-followup-a9c4e2 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=l7-section-shim-legacy-removal-followup-a9c4e2 phase=<W1.1>
PLAN_COMPLETE: plan=l7-section-shim-legacy-removal-followup-a9c4e2 note="<final outcome>"
```

---

## Completion Receipts

- Open-scope report: `docs/reports/apps_rg/l7_boundary_open_scope_20260607.md`
- Follow-up receipt: `artifacts/certification/apps_rg_l7_open_scope_followup_receipt.json`
- Verification: `tests/unit/apps_rg/test_section_evidence_package.py` + `tests/_apps_contract/test_apps_rg_section_artifact_namespace.py` passed (`12 passed, 1 skipped`).
