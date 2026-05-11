---
trigger: always_on
tier: 0
description: |
  Core architecture law: agentic_core is app-agnostic governed runtime.
  apps_* customize behavior through U0 runtime_customization_package and app-owned profile refs.
  This rule is always on — applies to every task.
---

# agentic_core Static Architecture Law

> ⛔ **Non-negotiable**: `agentic_core` is app-agnostic. App-specific behavior in shared core is **leakage** unless explicitly documented as temporary thin adapter with migration receipt.

## Core Principle

**Apps customize inputs. Core enforces contracts.**

```
CORRECT FLOW:
apps_*
  → U0 runtime_customization_package (app-owned refs)
  → agentic_core generic profile resolver
  → generic L0/L1/L2/L3/Exit/UWG/L6 enforcement

FORBIDDEN (LEAKAGE):
apps_*
  → app-specific code scattered inside agentic_core layers
```

## Before Any Core Edit

Classify the change:

| Question | If YES | If NO |
|-----------|--------|-------|
| Does this apply to ALL apps_*? | ✅ Generic infrastructure — allowed with receipt | ❌ App-specific — move to apps_*/ |
| Is this a temporary thin adapter? | ✅ Allowed ONLY with migration receipt | ❌ Must migrate to generic + profile |
| Does this hardcode an app_id check? | ❌ **LEAKAGE** — move to app profile | ✅ Generic — proceed |
| Does this hardcode apps_*/apps_rg/apps_qna? | ❌ **LEAKAGE** — use profile refs | ✅ Generic — proceed |

## Allowed Generic Core Changes

- Generic contract-chain propagation
- Generic profile resolver (any app profile)
- Generic route policy interpreter
- Generic GateMesh enforcement
- Generic Exit profile enforcer
- Generic UWG enforcement
- Generic L6 completed-run profile consumer
- Generic proof and receipt validators
- Generic anti-bypass checks

## Forbidden App-Specific Core Changes

- `if app_id == "apps_lic"` — move to apps_lic route profile
- `if app_id == "apps_rg"` — move to apps_rg route profile
- `apps_lic_route = "R4_MANAGED_DRAFT"` — move to apps_lic L0 profile
- `APPS_LIC_CACHE_BYPASS_PROFILES = [...]` — move to apps_lic cache policy
- App-specific judge thresholds — move to threshold_profile.yaml
- App-specific Exit gate lists — move to Exit profile
- App-specific L6 promotion rules — move to meta_feedback profile

## Receipt Required

Before modifying `agentic_core/`:

1. Classify file: GENERIC_INFRASTRUCTURE | TEMPORARY_THIN_ADAPTER | CORE_APP_SPECIFIC_LEAKAGE
2. If TEMPORARY_THIN_ADAPTER: verify migration receipt exists at `artifacts/governance/migration_receipts/`
3. If adding new app-specific logic: **BLOCK** — move to `apps_*/config/domain_contract/`
4. Write/update receipt documenting: files changed, classification, tests, migration path

## Triage Categories for App References

The 1,292 app-specific literal matches are classified as:

| Category | Treatment | Example |
|----------|-----------|---------|
| `CORE_APP_SPECIFIC_LEAKAGE` | Migrate immediately | `if app_id == "apps_lic":` |
| `TEMPORARY_THIN_ADAPTER` | Tolerated with receipt | `apps_lic_l0_binding.py` |
| `GENERIC_READY` | Core stays | Generic resolver using profile ref |
| `TEST_ALLOWED` | Allowed in test context | `tests/_apps_contract/test_*.py` |
| `DOC_ALLOWED` | Allowed in documentation | `.md` files referencing apps |
| `RECEIPT_ALLOWED` | Allowed in migration receipts | `artifacts/governance/` receipts |
| `APP_CONFIG_ALLOWED` | Allowed in app configs | `apps_lic/config/domain_contract/` |
| `MIGRATION_EXCEPTION` | Allowed temporarily | Explicit exemption with deadline |

## Related

- `agentic_core/AGENTS.md` — Core boundary rules
- `apps_lic/AGENTS.md`, `apps_rg/AGENTS.md`, etc. — App customization rules
- `.windsurf/rules/agentic-core-glob-lock.md` — Editing restrictions
- `.windsurf/rules/boundary-audit-required.md` — Audit triggers
