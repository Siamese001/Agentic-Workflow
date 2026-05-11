---
trigger: model_decision
tier: 1
description: |
  Trigger boundary audit when agentic_core files changed or app-specific 
  literals appear in core. Use /core-boundary-audit workflow.
---

# Boundary Audit Triggers

> Boundary audit is required when the agentic_core/apps_* boundary may be violated.

## When to Run Boundary Audit

Activate `/core-boundary-audit` workflow when:

### File Changes
- Any file under `agentic_core/` is modified
- Any `*_binding.py` file is added/modified/deleted
- Any new app-specific literal appears in core

### Code Patterns
- Adding `if app_id == "..."` checks
- Adding `apps_lic`, `apps_rg`, `apps_qna` string literals to `agentic_core/`
- Adding app-specific route names (e.g., `R4_MANAGED_DRAFT`)
- Adding app-specific cache bypass profiles
- Adding app-specific Exit gate IDs
- Adding app-specific judge thresholds

### Review Triggers
- PR touches both `agentic_core/` and `apps_*/`
- PR adds new binding file
- PR modifies existing binding file
- PR claims "generic" but includes app-specific constants

## /core-boundary-audit Workflow

Run this workflow to validate boundary integrity:

```
1. git diff → list changed files
2. Classify each agentic_core/ file:
   - GENERIC_INFRASTRUCTURE
   - TEMPORARY_THIN_ADAPTER  
   - CORE_APP_SPECIFIC_LEAKAGE
3. Scan for forbidden literals:
   - apps_lic, apps_rg, apps_qna (outside allowed contexts)
   - if app_id, app_id ==
   - Hardcoded route names
4. Verify receipts exist for TEMPORARY_THIN_ADAPTER
5. Verify no undocumented app-specific logic
6. Write receipt if audit passes
7. BLOCK if leakage found without migration plan
```

## Audit Outcomes

| Outcome | Action | Receipt Required |
|---------|--------|------------------|
| `ALLOW` | No core changes or all generic | No |
| `ALLOW_WITH_GENERIC_REFACTOR` | Core changes are generic | Yes |
| `BLOCK_MOVE_TO_APPS_CONFIG` | App-specific logic in core | Yes, + move code |
| `BLOCK_ROLLBACK_REQUIRED` | Leakage without migration path | Yes, + rollback |

## Receipt Required For

Any of these outcomes require boundary receipt:
- ALLOW_WITH_GENERIC_REFACTOR
- BLOCK_MOVE_TO_APPS_CONFIG (post-migration)
- BLOCK_ROLLBACK_REQUIRED (post-rollback)

Receipt location: `artifacts/governance/boundary_receipts/<timestamp>_<audit_id>.json`

## Classification Definitions

### GENERIC_INFRASTRUCTURE
- No app-specific string literals
- Uses profile refs, not hardcoded values
- Applies to all apps_* equally
- Example: Generic profile resolver

### TEMPORARY_THIN_ADAPTER  
- Named `*_binding.py` with explicit app prefix
- Has migration receipt
- Target: GENERIC_READY
- Example: `apps_lic_l0_binding.py` (being migrated)

### CORE_APP_SPECIFIC_LEAKAGE
- Hardcoded app_id checks
- Hardcoded app-specific constants
- No migration receipt
- Example: `if app_id == "apps_lic": return R4_MANAGED_DRAFT`

## CI Enforcement

CI gates (W4) automatically audit:
- `test_agentic_core_static_boundary.py` — No app policy in shared core
- `test_no_app_specific_literals_in_core.py` — Literal scan
- `test_apps_runtime_package_contracts.py` — Package validation

## Local Enforcement

Pre-commit hooks (W3) block:
- Core edits without classification
- New app-specific literals in core
- Undocumented binding changes

## Emergency Bypass

`BOUNDARY_AUDIT_BYPASS=1` — logs warning, proceeds (not recommended).

## Related

- `/core-boundary-audit` workflow — Canonical procedure
- `.windsurf/rules/agentic-core-static.md` — Core law
- `.windsurf/rules/agentic-core-glob-lock.md` — Editing guard
- `agentic_core/AGENTS.md` — Core boundary rules
