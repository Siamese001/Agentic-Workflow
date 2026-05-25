# execution_form SSOT decision (W0)

**Plan:** `l0-l3-parent-gap-remediation-a7f3e2`  
**Date:** 2026-05-25

## Decision

Production apps_rg resume routing uses **v15 three-form vocabulary** via `route_profiles.yaml` (`execution_form: MANAGED_WORKFLOW` for whole-run). Parent doc seven-form snake_case labels are **documentation aliases** mapped in gap analysis — not a second runtime enum.

## Implication

- W1 route evidence uses `apps_rg/runtime/bindings/l0_route_evidence.py` (digest + HMAC).
- L3 binding: `apps_rg/runtime/bindings/l3_binding.py` (`l3_orchestrate_apps_rg`).
- Full parent §7 validator matrix remains **W2+** (advisory `check_l0_parent_invariants.py` shipped first).
