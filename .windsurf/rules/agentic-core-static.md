---
trigger: model_decision
tier: 0
description: |
  Core architecture law: agentic_core is app-agnostic governed runtime.
  apps_* customize behavior through U0 runtime_customization_package and app-owned profile refs.
  Demoted from always_on 2026-05-26 (governance-dedup-closeout-e8a4c2 W4). Cursor SSOT: .cursor/rules/agentic-core-static.mdc (alwaysApply: false).
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

Generic contract-chain propagation, profile resolver, route policy interpreter, GateMesh/UWG/Exit enforcement, L6 completed-run consumer, proof/receipt validators, anti-bypass checks.

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

## Core Addition Author-Gate

> ⛔ Any `agentic_core/` edit adding mechanism, layer, contract, or capability MUST carry a `CoreAdditionAuthorGateReceipt` (verdict=PASS). Missing receipt → fail closed. Requires `plan_type: platform_core_change`.

Core owns reusable mechanisms; apps own meaning. App literals, app-specific branches/defaults/routes/validation/graph/prompt/writeback/eval in `agentic_core` → **FAIL**. Future `apps_*` plug in via app-owned config only.

## Triage Categories for App References

App-specific literal matches are classified as: `CORE_APP_SPECIFIC_LEAKAGE` (migrate immediately) · `TEMPORARY_THIN_ADAPTER` (tolerated with receipt) · `GENERIC_READY` (core stays) · `TEST_ALLOWED` · `DOC_ALLOWED` · `RECEIPT_ALLOWED` · `APP_CONFIG_ALLOWED` · `MIGRATION_EXCEPTION` (explicit exemption with deadline).

## Related

- `agentic_core/AGENTS.md` — Core boundary rules
- `apps_lic/AGENTS.md`, `apps_rg/AGENTS.md`, etc. — App customization rules
- `.windsurf/rules/agentic-core-glob-lock.md` — Editing restrictions
- `.windsurf/rules/boundary-audit-required.md` — Audit triggers
