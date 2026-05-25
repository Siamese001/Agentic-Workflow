# Agentic Core — Boundary Rules

> `agentic_core` is app-agnostic governed runtime infrastructure. It provides generic enforcement engines that consume app-owned profiles, not app-specific logic.

## Core Mandate

**Allowed**: Generic runtime infrastructure applicable to all `apps_*`.

**Forbidden**: App-specific behavior unless explicitly documented as `TEMPORARY_THIN_ADAPTER` with migration receipt.

## Allowed in agentic_core

These are **generic** and belong here:

### Resolvers & Interpreters
- Generic profile resolver — resolves any app profile by ref
- Generic route policy interpreter — consumes L0 route profiles
- Generic prompt assembly (PA) resolver — consumes prompt profiles
- Generic C0 retrieval coordinator — consumes retrieval profiles

### Enforcement Engines
- Generic GateMesh law enforcement
- Generic Exit profile enforcer — consumes Exit profiles, emits X3
- Generic UWG write admission — validates CommitRequest, writes L4
- Generic L6 completed-run consumer — consumes meta-feedback profiles
- **Multi-provider judge panel harness** — `runtime/judges/panel/` (`JudgePanelRunner`, `CanonicalJudgeContract`, transport preflight, gate-closure reconcile algorithm). Apps register `JudgeProviderAdapter` implementations and supply rubric/gate-closure maps; core enforces one contract hash and provider-neutral pass math.

### Product spine vs agent taxonomy (SSOT — ADR-088)

| Surface | Role |
|---------|------|
| `run_integrated_single_action_spine` + linked pipeline functions | **Canonical product E2E spine** (function/stage based) |
| `AGENT_TAXONOMY_MAP` | **Inventory/control only** — not the runtime execution graph |
| `*Agent` classes | Adjacent governance/healing/validation unless **artifact-proven** spine-invoked (A1) |

Taxonomy registration **does not** imply E2E invocation (A2). See [ADR-088](../docs/architecture/adr/ADR-088-product-spine-function-truth.md) and [runtime/LAYER.md](runtime/LAYER.md).

### Vocabulary — Exit vs 00C vs L5 vs UWG vs L6 (SSOT)

Docs-only clarity (child plan **f8e3c1** W5); behavior unchanged.

| Symbol / concern | Role |
|------------------|------|
| `GateVerdict` in `runtime_gates` | **00C / GateMesh** — live proceed-or-stop gate evidence; not Exit X3 |
| `ExitGateVerdict` in `apps_rg.runtime.bindings.exit_binding` | **apps_rg-local** Exit helper enum — **not** 00C `GateVerdict` |
| Exit / X3 | Exactly **one** X3 disposition per run — Exit-owned after X1/X2 aggregation |
| L5 certification packets | **Governance evidence only** — not runtime disposition |
| UWG | **Only** durable write admission path to governed L4 |
| L6 | **Completed-run** and **future-run** proposals only — no current-run rescue, no X3 |

### Infrastructure
- Generic contract propagation chain
- Generic proof and receipt validators
- Generic anti-bypass checks
- Generic audit trail emitters

### Package-Driven Handoff
- U0 runtime_customization_package validator
- Package digest verification
- Field map resolution
- Schema validation

## Forbidden in agentic_core

These are **leakage** and must migrate to `apps_*`:

### App-Specific Branching
```python
# FORBIDDEN — move to apps_*/config/domain_contract/
if app_id == "apps_lic":
    ...
if app_id == "apps_rg":
    ...
```

### Hardcoded App Names
```python
# FORBIDDEN — use profile refs instead
apps_lic_route = "R4_MANAGED_DRAFT"
apps_rg_route = "R1_RESUME_GENERATION"
```

### App-Specific Policy Lists
```python
# FORBIDDEN — move to app config
APPS_LIC_FINAL_DRAFT_ROUTES = ["R4_MANAGED_DRAFT", "R3R4_MANAGED_RESEARCH_THEN_DRAFT"]
APPS_LIC_CACHE_BYPASS_PROFILES = ["linkedin_send", "email_outbox_send"]
```

### App-Specific Thresholds
```python
# FORBIDDEN — move to threshold_profiles.yaml
APPS_LIC_MIN_JUDGE_SCORE = 0.85
APPS_RG_MIN_JUDGE_SCORE = 0.75
```

### Direct App Gate IDs
```python
# FORBIDDEN — use Exit profile refs
if gate_id in APPS_LIC_EXIT_GATES:
    ...
```

## Temporary Thin Adapter Exception

Files matching `*_binding.py` in `agentic_core/` may be `TEMPORARY_THIN_ADAPTER` **only if**:

1. Named explicitly with app prefix (e.g., `apps_lic_l0_binding.py`)
2. Documented migration receipt exists at `artifacts/governance/migration_receipts/`
3. Target state is generic engine + app profile (GENERIC_READY)
4. Not actively extended — only maintained until migration complete

## Classification of Core Files

Every file in `agentic_core/` must be classified:

| Classification | Marker | Treatment |
|----------------|--------|-----------|
| `GENERIC_INFRASTRUCTURE` | No app refs | Core stays here |
| `GENERIC_READY` | Uses profile refs | Core stays here |
| `TEMPORARY_THIN_ADAPTER` | `*_binding.py` with receipt | Migrate to GENERIC_READY |
| `CORE_APP_SPECIFIC_LEAKAGE` | Hardcoded app logic | **Migrate immediately** |

## Migration Receipt Format

Required for any temporary adapter:

```json
{
  "receipt_version": "1.0",
  "binding_file": "agentic_core/L0_routing/apps_lic_l0_binding.py",
  "classification": "TEMPORARY_THIN_ADAPTER",
  "migration_target": "Generic L0 route interpreter + apps_lic route profile",
  "target_location": "agentic_core/L0_routing/package_driven_l0_binding.py",
  "app_profile_refs": [
    "apps_lic/config/domain_contract/l0_route_profile.yaml"
  ],
  "expected_completion": "2026-Q3",
  "acceptance_criteria": [
    "Generic L0 binding consumes apps_lic route profile",
    "apps_lic_l0_binding.py deleted",
    "Tests pass with generic binding + app profile"
  ]
}
```

## Editing Core Files

Before editing any `agentic_core/` file:

1. Classify the file (see table above)
2. If TEMPORARY_THIN_ADAPTER: verify receipt exists and is current
3. If adding app-specific logic: **BLOCK** — move to `apps_*` profile
4. If adding generic infrastructure: proceed with receipt for boundary audit

## Related

- Root `AGENTS.md` — Architecture law
- `.cursor/rules/agentic-core-static.md` — Always-on guidance
- `.cursor/rules/agentic-core-glob-lock.md` — Editing restrictions
- `apps_lic/AGENTS.md`, `apps_rg/AGENTS.md`, etc. — App customization rules
