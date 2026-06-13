# ADG v6 — Structural Debt Clearance Plan

Generated: 2026-03-13
ADG Snapshot: adg_indexed_03122026.sqlite
Branch: ADG_v6

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary of Real Issues (ADG-verified)

| Metric | Count | Priority |
|---|---|---|
| `GV_violates` (layer boundary violations) | 233 | Critical |
| `dead_imports` | 16,537 | High |
| E7 drift risk_delta | +3 (WORSE) | Medium |

---

## Phase 1: Dead Import Cleanup

**Goal:** Eliminate dead imports from `__init__.py` files and high-density files first.
**Target:** Top 20 files with most dead imports (117, 111, 49, 47... see audit).
**Tool:** `ruff check --fix` + manual cleanup for re-exports.

Top targets:
- `agentic_core/adg/runtime/__init__.py` (117)
- `agentic_core/L5_safety/config/structure_blueprint/__init__.py` (111)
- `agentic_core/L0_routing/config/__init__.py` (49)
- `agentic_core/evaluation/retrieval/__init__.py` (47)
- `agentic_core/L5_safety/config/structure_blueprint_config.py` (25)
- `apps_lic/reasoning/ArchetypeIndicatorsAgent.py` (24)
- `agentic_core/evaluation/metrics/__init__.py` (23)
- `agentic_core/_compat/l5_safety_aliases.py` (23)
- `agentic_core/runtime/types/__init__.py` (21)
- `agentic_core/runtime/exceptions/workflow_exceptions.py` (21)

---

## Phase 2: Layer Boundary Violation Repair

**Goal:** Fix all 233 `GV_violates` edges.
**Method:** For each violation, either:
  (a) Move the import to a shared/lower layer, or
  (b) Add an interface/seam at the correct layer boundary.

Top violating rules (by count):
- `L0->L5`: 32 — L0_routing scripts importing L5_safety directly
- `L_SHARED->L5`: 20 — shared modules pulling in safety plane
- `L_SHARED->L4`: 14 — shared pulling state/persistence
- `L_SHARED->L0`: 13 — shared pulling routing
- `L2->L5`: 10 — execution importing safety directly
- `L0->L2`: 9 — routing importing execution

Top violating files:
- `execute_ssot.py`: 8 violations (L0->L_SL, L0->L1..L6 — monolith, needs extraction)
- `SubAtomicRegistryAgent.py`: 5
- `hardening_mixin.py`: 4
- `SovereignBaseAgent.py`: 4
- `drift_monitor.py`: 3
- `runtime_bootstrapper_util.py`: 3

By source layer:
- `L0_routing`: 62 violations (biggest offender)
- `mixins`: 28
- `L3_orchestration`: 20
- `L2_execution`: 19
- `utils`: 14
- `runtime`: 12

---

## Phase 3: E7 Drift Reduction

**Goal:** Push risk_delta from +3 back to 0 or negative.
**Method:** Re-run ADG after phases 1+2 and verify delta improves.
**Target:** <0 risk_delta on next ADG scan.

---

## Execution Order

1. P1 — Dead imports (ruff auto-fix, safe)
2. P2a — L0_routing violations (62 — biggest cluster)
3. P2b — mixins violations (28)
4. P2c — L3+L2+utils+runtime violations (remaining ~143)
5. P3 — Re-run ADG, verify drift improvement
6. Commit + push each phase

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

