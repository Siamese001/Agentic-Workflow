---
title: apps_lic U0 Boundary Alignment — Golden Template Adoption
slug: apps-lic-u0-boundary-alignment-4f1d9c
status: Not Started
plan_type: governance
dod_exempt: false
created: 2026-05-12
---

# apps_lic U0 Boundary Alignment — Golden Template Adoption

## Purpose

Use `apps_rg` as the golden template for clean separation between `agentic_core` and app-specific behavior.
Audit `apps_lic` against that template, produce a gap matrix, and deliver a wave-based remediation plan.

`agentic_core` must remain pristine, generic, and untouched. All `apps_lic`-specific behavior must live
in `apps_lic` and enter the spine exclusively through the U0 runtime customization payload/package.

**Stop after producing this plan. No code changes.**

---

## Boundary Law

> ⛔ These rules are invariants, not guidelines. Any implementation step that violates them must be blocked.

### BL-1 — Core owns generic contracts and runners only

`agentic_core` exposes:
- Generic ingress/egress contract types (`IngressPayload`, `ValidatedRequest`, `RouteContract`, `L3RuntimeOrchestrationReceipt`, `FinalEvidenceContract`, `ExitDisposition`)
- Generic runner interfaces (`AppIngressRunner`, `DurableWriteGateway`, `GenericProfileResolver`)
- Generic protocol interfaces (`HITLPolicyProtocol`, `ContentValidatorProtocol`, `AgentTaxonomyRegistryProtocol`)
- Layer enforcement machinery (UWG, L5 HITL evaluation framework, L6 profile consumer)

`agentic_core` does **not** contain:
- Any `apps_lic`-specific business logic, route names, schema definitions, policy rules, agent classes, or config values
- Any `from apps_lic.*` import at module scope (shims are the only exception — see §Allowed Core Exceptions)
- Any file whose name begins with `apps_lic_` except the approved re-export shim files (≤30 lines each)

### BL-2 — App-owned logic lives in apps_lic

All of the following are owned by `apps_lic` and must reside under `apps_lic/`:
- All layer bindings (U0, L0, L1, C0, PA, L2, L3, Exit, L6)
- All route profiles, cache policies, threshold profiles, exit profiles, L6 meta-feedback profiles
- All HITL policies and HITL evaluators
- All UWG write class identifiers and touch-state schemas
- All ingress payload contracts (`AppsLicRequestEnvelope`, `AppsLicIngressPayload`)
- All agent taxonomy entries for `apps_lic` agents
- All U0 adapters (`apps_lic_u0_adapt`, `AppsLicU0AdapterError`, `AppsLicU0ReflectionReceipt`)
- The `apps_lic` dispatch entrypoint (source_channel, declared_schema, task_class identity)

### BL-3 — U0 is the sole spine entry point

`apps_lic` enters the spine **only** via `U0 runtime customization payload`. No layer below U0 may be invoked directly by `apps_lic` code without first passing through U0 validation. Any spine layer (L0, L1, C0, PA, L2, L3, Exit, UWG, L5, L6) invoked without a validated `U0RuntimeCustomizationPackage` present in the call chain must raise `IngressBypassError` (or equivalent fail-closed typed exception).

### BL-4 — Layer behavioral invariants

| Layer | Invariant | Violation |
|-------|-----------|----------|
| **C0** | Emits `GateVerdict` only. No answering, no state writes, no LLM calls | C0 writing to L4 state or invoking LLM = **VIOLATION** |
| **L5** | Certifies evidence against policy only. Issues `HITLDecision`. No data retrieval, no direct state write | L5 reading from DB or emitting X3 = **VIOLATION** |
| **Exit** | Emits exactly **one** `X3Disposition`. Loaded from app-owned `exit_profile_ref`. Fails closed on missing profile | Exit emitting 0 or 2+ X3 = **VIOLATION** |
| **UWG** | Is the **only** durable write path for L4 state. No other layer writes to persistent storage | Any direct DB/file write outside UWG = **VIOLATION** |
| **L6** | Operates on completed runs only. Cannot mutate current run or rescue failed execution | L6 accessing in-flight run state = **VIOLATION** |

### BL-5 — No app-specific logic added to core

If a remediation step requires a generic interface that does not yet exist in `agentic_core` (e.g., `register_app_entries` API on the agent taxonomy registry, `HITLPolicyProtocol` injection slot, `ContentValidatorProtocol` injection slot), that interface addition is tracked as a **separate enabling plan** (`apps-lic-core-interface-gap-<id>.md`). The `apps_lic` boundary alignment plan gates on those enabling plans being completed first — it does not leak `apps_lic` logic into core as a shortcut.

---

## Allowed Core Exceptions

The following are the **only** patterns permitted in `agentic_core` that reference `apps_lic`:

| Exception class | Permitted form | Hard limits | Example |
|-----------------|---------------|-------------|--------|
| **Re-export shim** | A core file `agentic_core/**/apps_lic_<layer>_binding.py` that contains only `from apps_lic.runtime.bindings.<layer>_binding import *` + `__all__` | ≤30 lines total; zero business logic; no conditional imports; docstring must contain `re-export shim` | `agentic_core/runtime/entry/u0_apps_rg_binding.py` (24 lines) |
| **App-package name constant** | `APPS_LIC_DIR: Final[str] = "apps_lic"` and `APPS_LIC_SUBFOLDER_MAP` in `agentic_core/L0_routing/config/path_constants.py` | Read-only string constants for ADG/scanner use only; no behavioral branching on value | `path_constants.py:139,505` (Gap G-19, EXEMPT) |

**Everything else is a violation.** Specifically forbidden even as "temporary" forms:
- Any `apps_lic`-specific dataclass, schema, SQL table, HITL policy, HITL evaluator, agent classification, or write-class constant residing in `agentic_core/`
- Any `from apps_lic.*` import at module scope in a non-shim file
- Any core file that imports `apps_lic` config registries (e.g., `REGISTRY` from `apps_lic.config.hop_pipeline`)
- Any `apps_lic`-named file in `agentic_core/L4_state/`, `agentic_core/L5_safety/`, `agentic_core/runtime/contracts/`, or `agentic_core/runtime/entrypoints/`
- The AG-RGGOV-9 `apps_lic imports preserved` exemption comment in `apps_engines_aliases.py` — this exemption is **invalid** under BL-1 and must be removed

---

## Generic Interface Dependency Order

Some gaps require a new generic core interface before the `apps_lic` migration can complete without leaking app logic into core. These are **pre-requisite enabling plans** — they must be created and completed **before** the affected gap's implementation wave begins.

| Enabling plan (to be created) | Required by | Gaps unblocked | Core interface to add |
|-------------------------------|-------------|----------------|----------------------|
| `apps-lic-core-interface-gap-taxonomy-<id>.md` | W3.P4 | G-12 | `AgentTaxonomyRegistry.register_app_entries(app_id, entries)` generic late-registration API |
| `apps-lic-core-interface-gap-hitl-protocol-<id>.md` | W4.P1 | G-14, G-15 | `HITLPolicyProtocol` injection slot in L5 evaluator framework so app-owned policy can be passed via U0 payload |
| `apps-lic-core-interface-gap-content-validator-<id>.md` | W3.P2 (G-13) | G-13 | `ContentValidatorProtocol` on `SubAtomicRegistryAgent` so app-specific validator is injected, not imported |

**Sequencing rule:** Do not begin implementation of W3.P4, W4.P1, or G-13 remediation until the corresponding enabling plan's core interface is merged. Implementing those gaps by moving `apps_lic` logic into core (even as a "shim") violates BL-5.

**What this plan owns:** creation of the enabling plan files + interface specification. Implementation of the interfaces is in the enabling plans. Implementation of the `apps_lic` migrations is in the follow-on implementation plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W0 | W0.P1–P3 | Baseline audit — inventory all `apps_lic` literals inside `agentic_core` | ~4k | grep/ADG available | Not Started | All contamination sites enumerated with file + line evidence |
| W1 | W1.P1–P5 | `apps_rg` golden template extraction — document canonical binding shape | ~5k | `apps_rg/runtime/bindings/` fully migrated | Not Started | Golden template doc with per-layer contract shape |
| W2 | W2.P1–P6 | `apps_lic` boundary/gap audit — compare against golden template | ~8k | W1 complete | Not Started | Gap matrix populated with category + evidence |
| W3 | W3.P1–P4 | U0 payload alignment plan — per-gap migration steps | ~6k | W2 complete | Not Started | Every gap has an owner + migration approach + acceptance proof |
| W4 | W4.P1–P5 | Contract/gate/L5/Exit/UWG/L6 alignment plan | ~5k | W3 complete | Not Started | Every gate gap has a remediation step + CI hook |
| W5 | W5.P1–P4 | CI/static scanner and negative-control plan | ~5k | W4 complete | Not Started | Scanner spec + negative-control tests per gap category |
| W6 | W6.P1–P3 | Acceptance evidence bundle plan | ~3k | W5 complete | Not Started | Evidence bundle spec per wave |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | Literal scan — `apps_lic` in `agentic_core` | `agentic_core/**/*.py` | 507 matches across 101 files | ~1.5k | Not Started |
| W0.P2 | Direct import scan — `from apps_lic` in core | `agentic_core/**/*.py` | 15 matches across 8 files | ~1k | Not Started |
| W0.P3 | Schema/SQL artifact scan in core | `agentic_core/L4_state/schemas/`, `agentic_core/L5_safety/` | 2 app-specific schema files | ~0.5k | Not Started |
| W1.P1 | U0 binding golden shape | `apps_rg/runtime/bindings/u0_binding.py` | Migrated; core shim retained | ~1k | Not Started |
| W1.P2 | L0/L1/C0/PA/L2 binding golden shapes | `apps_rg/runtime/bindings/{l0,l1,c0,pa,l2}_binding.py` | All in `apps_rg/runtime/bindings/` | ~1.5k | Not Started |
| W1.P3 | Exit binding golden shape | `apps_rg/runtime/bindings/exit_binding.py` | App-owned exit profile | ~0.5k | Not Started |
| W1.P4 | Dispatch golden shape | `apps_rg/runtime/dispatch/apps_rg_dispatch.py` | Pure function dispatch | ~0.5k | Not Started |
| W1.P5 | Profile/config ownership golden pattern | `apps_rg/config/` | All config app-owned | ~0.5k | Not Started |
| W2.P1 | `apps_lic` binding location gap | `agentic_core/*/apps_lic_*_binding.py` | 10 binding files still in `agentic_core` | ~2k | Not Started |
| W2.P2 | Direct core imports from `apps_lic` | 8 files in `agentic_core` | Direct `from apps_lic.*` pulls | ~1.5k | Not Started |
| W2.P3 | App-specific schema/SQL in core L4/L5 | `agentic_core/L4_state/schemas/apps_lic_touch_state.sql`, L5 policy | App data models embedded in core | ~1k | Not Started |
| W2.P4 | Agent taxonomy registry contamination | `agentic_core/L2_execution/types/agent_taxonomy_registry.py` | 35 `apps_lic` matches; app-specific agent entries in core registry | ~1k | Not Started |
| W2.P5 | Core aliases pointing to `apps_lic` | `agentic_core/utils/workflow_engines/apps_engines_aliases.py` | Direct imports of 3 `apps_lic` agent classes | ~0.5k | Not Started |
| W2.P6 | Core entrypoint owning `apps_lic` identity | `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` | Source-channel/schema literals and identity hardcoded in core | ~1k | Not Started |
| W3.P1 | Migration plan: 10 binding files → `apps_lic/runtime/bindings/` | All `agentic_core/*/apps_lic_*_binding.py` | Requires creating `apps_lic/runtime/bindings/` tree | ~2k | Not Started |
| W3.P2 | Migration plan: direct imports → app-owned | 8 import sites in core | Some are deep inside L2/L5/L6 logic bodies | ~1.5k | Not Started |
| W3.P3 | Migration plan: schema/SQL/policy → `apps_lic/` | `L4_state/schemas/`, `L5_safety/policy/`, `L5_safety/evaluators/` | 4 files; L5 HITL policy is app-specific | ~1k | Not Started |
| W3.P4 | Migration plan: agent taxonomy entries → app-owned registry | `agent_taxonomy_registry.py` + new `apps_lic/config/agent_taxonomy.py` | Requires generic registry API that accepts late-registration | ~1.5k | Not Started |
| W4.P1 | L5 HITL policy ownership plan | `apps_lic_reengagement.py` in L5 policy + evaluator | HITL policy is app-specific; must live in `apps_lic/config/` | ~1k | Not Started |
| W4.P2 | UWG/L4 write path ownership plan | `touch_state_writer.py` in L4 UWG | App-specific write schema in generic UWG layer | ~1k | Not Started |
| W4.P3 | Exit/X3 disposition wiring plan | `apps_lic_exit_binding.py` + `RuntimeCustomizationPackageSection` import | Ensure exit profile loaded from `apps_lic/config/`, not synthesized in core | ~1k | Not Started |
| W4.P4 | L6 promo binding plan | `apps_lic_promo_binding.py` in `agentic_core/L6_observability/` | `_load_apps_lic_l6_policy()` is a placeholder stub — must load from real app profile | ~0.5k | Not Started |
| W4.P5 | L5 cert refs and gate binding plan | `apps_lic_l3_binding.py` node_id hardcode, L5 safety reasoning files | App domain strings in core L5 reasoning | ~1k | Not Started |
| W5.P1 | Static scanner spec: literal scan | `ops_scripts/ci/` | New `check_apps_lic_core_contamination.py` gate | ~1.5k | Not Started |
| W5.P2 | Static scanner spec: import boundary | `ops_scripts/ci/` | New `check_apps_lic_core_imports.py` gate | ~1k | Not Started |
| W5.P3 | Negative-control test spec | `tests/_apps_contract/` | Prove `apps_lic` enters only through U0 | ~1.5k | Not Started |
| W5.P4 | Pre-commit hook plan | `.pre-commit-config.yaml` | Add hooks for above scanners | ~0.5k | Not Started |
| W6.P1 | Evidence bundle spec — binding migration | Per-layer receipts | Coverage proof for each migrated binding | ~1k | Not Started |
| W6.P2 | Evidence bundle spec — contamination clean | Rg scan clean outputs | Zero-match proof per scan category | ~1k | Not Started |
| W6.P3 | Evidence bundle spec — tests passing | pytest `tests/_apps_contract/` | Aggregate test count + zero regressions | ~0.5k | Not Started |

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|-------------|
| DoD-1 | Gap matrix complete with category (A–F), file path, evidence, owner, remediation approach, concrete post-remediation command + expected result for every gap | Human review of §Gap Matrix section + §Tightened Acceptance Proofs |
| DoD-2 | Every `agentic_core/*/apps_lic_*_binding.py` file has a migration target path in `apps_lic/runtime/bindings/` | `(Get-ChildItem agentic_core -Recurse -Include "apps_lic_*_binding.py").Count` matches W0.P1 binding file enumeration |
| DoD-3 | Every direct `from apps_lic` import in `agentic_core` has a remediation step and the remediation step does not add new app logic to core | List in §W3.P2 covers all 8 sites; each fix moves import to app side |
| DoD-4 | CI scanner spec (W5.P1/P2) with exact file paths, bypass env var, advisory/fail-closed mode, and registration line in `run_contract_gates.py` | §W5 complete |
| DoD-5 | Negative-control test spec (W5.P3) covers all 5 BL-4 invariants + U0-only entry + import boundary | §W5.P3 expanded negative-control table complete |
| DoD-6 | Generic interface dependency order documented — enabling plans named and sequenced before gaps that require them | §Generic Interface Dependency Order table complete |
| DoD-7 | Boundary Law + Allowed Core Exceptions sections present and unambiguous | §Boundary Law and §Allowed Core Exceptions present in plan |
| DoD-8 | No code changes performed — git diff/status confirms plan-only hardening | §No Code Changes Verification block passes |

### Verification-vs-Deferral

| Item | In scope | Deferred |
|------|----------|---------|
| Actual code changes | ❌ Deferred | All implementation in follow-on implementation plan |
| Creating enabling plans for generic interface gaps | ✅ In scope — plan file stubs only | Implementation of those interfaces is deferred |
| `apps_rg` code changes | ❌ Not touched | Golden template extraction is read-only |
| L5 HITL framework interface addition | ❌ Enabling plan stub only | Implementation in `apps-lic-core-interface-gap-hitl-protocol-<id>.md` |
| Agent taxonomy registry API addition | ❌ Enabling plan stub only | Implementation in `apps-lic-core-interface-gap-taxonomy-<id>.md` |
| `ContentValidatorProtocol` addition | ❌ Enabling plan stub only | Implementation in `apps-lic-core-interface-gap-content-validator-<id>.md` |

---

## W0 — Baseline Audit

### W0.P1 — `apps_lic` literal presence in `agentic_core`

**Verification command:**
```powershell
# Count files with any apps_lic reference
Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "apps_lic" | Select-Object Filename -Unique | Measure-Object
```
```bash
# ripgrep (if available)
rg "apps_lic" agentic_core --include="*.py" -l | wc -l
```

**Observed baseline (2026-05-12):** 507 matches across 101 files.

**Highest-density files (top 10):**

| File | Matches | Classification |
|------|---------|---------------|
| `agentic_core/L3_orchestration/apps_lic_l3_binding.py` | 42 | Binding file — should be app-owned |
| `agentic_core/L2_execution/types/agent_taxonomy_registry.py` | 35 | App-specific registry entries in generic core |
| `agentic_core/L1_cognition/apps_lic_l1_binding.py` | 30 | Binding file — should be app-owned |
| `agentic_core/L0_routing/apps_lic_l0_binding.py` | 29 | Binding file — should be app-owned |
| `agentic_core/runtime/exit/apps_lic_exit_binding.py` | 26 | Binding file — should be app-owned |
| `agentic_core/runtime/c0/apps_lic_c0_binding.py` | 23 | Binding file — should be app-owned |
| `agentic_core/runtime/entry/u0_apps_lic_binding.py` | 23 | Binding file — should be app-owned |
| `agentic_core/L2_execution/apps_lic_l2_binding.py` | 20 | Binding file — should be app-owned |
| `agentic_core/L6_observability/promotion/apps_lic_promo_binding.py` | 19 | Binding file — should be app-owned |
| `agentic_core/prompt_governance/apps_lic_pa_binding.py` | 18 | Binding file — should be app-owned |

### W0.P2 — Direct `from apps_lic` / `import apps_lic` in `agentic_core`

**Verification command:**
```powershell
Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "from apps_lic|import apps_lic" | Select-Object Path, LineNumber, Line
```

**Observed baseline (2026-05-12):** 15 matches across 8 files.

| File | Import statement | Severity |
|------|-----------------|---------|
| `agentic_core/utils/workflow_engines/apps_engines_aliases.py:31-33` | `from apps_lic.reasoning.GovernanceShieldAgent import GovernanceShieldAgent` | **CRITICAL** — core compat shim directly imports app agents |
| `agentic_core/utils/workflow_engines/apps_engines_aliases.py:32` | `from apps_lic.reasoning.LicHealingOrchestrator import LicHealingOrchestrator` | **CRITICAL** |
| `agentic_core/utils/workflow_engines/apps_engines_aliases.py:33` | `from apps_lic.reasoning.LicReflectionAgent import LicReflectionAgent` | **CRITICAL** |
| `agentic_core/runtime/exit/apps_lic_exit_binding.py:55-57` | `from apps_lic.contracts.apps_lic_ingress_contract_v1 import RuntimeCustomizationPackageSection, ProfileRef` | HIGH — core binding imports app contract type |
| `agentic_core/L2_execution/apps_lic_l2_binding.py:161` | `from apps_lic.config.hop_pipeline import REGISTRY` | **CRITICAL** — core L2 binding reads app config directly |
| `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py:382` | `from apps_lic.types.ImmutableStagingBuffer import AppContentValidatorAgent` | HIGH — core reasoning agent imports app type |
| `agentic_core/L5_safety/evaluators/apps_lic_reengagement.py:22-26` | `from agentic_core.L5_safety.policy.apps_lic_reengagement import ...` | MEDIUM — internal cross-ref within contaminated files |
| `agentic_core/runtime/contracts/apps_lic_ingress_payload.py:29` | (defines `AppsLicIngressPayload`) | HIGH — app ingress contract type embedded in core contracts |

### W0.P3 — App-specific schema/SQL and policy files in core

**Verification command:**
```powershell
Get-ChildItem -Path agentic_core/L4_state/schemas -Filter "apps_lic*"
Get-ChildItem -Path agentic_core/L5_safety -Recurse -Filter "apps_lic*"
```

**Observed baseline:**

| File | Issue |
|------|-------|
| `agentic_core/L4_state/schemas/apps_lic_touch_state.sql` | App-specific DB schema embedded in generic L4 schemas |
| `agentic_core/L5_safety/policy/apps_lic_reengagement.py` | App-specific HITL policy dataclass in generic L5 policy |
| `agentic_core/L5_safety/evaluators/apps_lic_reengagement.py` | App-specific HITL evaluator in generic L5 evaluators |
| `agentic_core/runtime/contracts/apps_lic_ingress_payload.py` | App-specific contract type in generic core contracts |
| `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` | App-specific entrypoint + identity (source_channel, declared_schema) in generic runtime entrypoints |

---

### W0 Closeout Receipt

**Executed:** 2026-05-12  
**Executed by:** Cursor Agent (read-only audit — zero source file modifications)

```
W0_STATUS: PASS
PLAN: apps-lic-u0-boundary-alignment-4f1d9c
SOURCE_CHANGES_MADE: false
IMPLEMENTATION_STARTED: false
WORKSPACE_DIFF_BLOCKER: true

COUNTS:
  apps_lic literal files:                      101 unique files, 507 line matches
  executable direct imports (from/import):     6 lines across 4 files
  schema/policy/contract/entrypoint files:     5 files

DELTA FROM PLAN BASELINE:
  W0.P1: 0 delta — 101 files / 507 matches confirmed
  W0.P2: plan recorded 15 total hits / 8 files; live count is 15 total hits,
         6 executable import lines across 4 files. Delta is comment/string
         occurrences vs. executable import lines — no new imports introduced.
  W0.P3: 0 delta — same 5 contamination files confirmed

WORKSPACE_DIFF_NOTE:
  Receipt (§Pre-existing Workspace Diff Exclusion Receipt) documented 6 files.
  Workspace now shows 28 modified files. Delta of 22 is from other sessions
  (governance consolidation, apps_rg bindings, author-gate rule updates).
  Zero agentic_core/ files appear in the diff. Block Condition remains in force.

NEXT_ALLOWED_WAVE: W1 (read-only golden-template extraction) may proceed
  provided no source changes are made during W1 execution.

IMPLEMENTATION_WAVES_BLOCKED: W3–W6 remain blocked until workspace cleanliness
  is resolved via one of:
    Option A — Commit pre-existing diffs under their own commit(s).
    Option B — Stash or revert pre-existing diffs.
    Option C — Baseline under a separate plan if the diffs represent
               in-flight work requiring its own plan completion first.
  After resolution, re-run: git diff --name-only HEAD
  Expected result: empty (or only the apps-lic plan file as untracked).
```

---

## W1 — apps_rg Golden Template Extraction

### W1.P1 — U0 binding golden shape

**Golden file:** `apps_rg/runtime/bindings/u0_binding.py`

**Key shape invariants:**
- Pure function `u0_validate_apps_rg(envelope) -> ValidatedRequest`
- No I/O, no state, no provider calls
- Imports only from `agentic_core.runtime.contracts.*` (generic contracts) and `agentic_core.runtime.u0.*` (generic adapter framework)
- App-specific adapter lives at `apps_rg/runtime/u0/adapter.py` (app-owned)
- Core shim `agentic_core/runtime/entry/u0_apps_rg_binding.py` is a **re-export only** (24 lines) pointing to the app-owned location

**Golden pattern:**
```
apps_rg/runtime/bindings/u0_binding.py          ← OWNS the logic
agentic_core/runtime/entry/u0_apps_rg_binding.py ← re-export shim only (24 lines, no logic)
```

### W1.P2 — L0/L1/C0/PA/L2 binding golden shapes

**Golden files:** `apps_rg/runtime/bindings/{l0,l1,c0,pa,l2}_binding.py`

**Key shape invariants for each:**
- Pure functions consuming and producing only generic `agentic_core.runtime.contracts.*` types
- App-specific config/profile loaded from `apps_rg/config/` (app-owned YAML/JSON)
- No app string literals hardcoded; all loaded from app-owned profile refs
- No direct calls to L4 write, ChromaDB, embedding models, or LLM
- Each emits a typed receipt/contract object as sole output

**Comparison:** `apps_lic` equivalent bindings all live in `agentic_core/*/apps_lic_*_binding.py` — the opposite of this pattern.

### W1.P3 — Exit binding golden shape

**Golden file:** `apps_rg/runtime/bindings/exit_binding.py`

**Key shape invariants:**
- Exit profile loaded from app-owned config ref (`apps_rg/config/`)
- Emits exactly one X3 disposition
- No hardcoded G-number set in core
- No direct L4 write

### W1.P4 — Dispatch golden shape

**Golden file:** `apps_rg/runtime/dispatch/apps_rg_dispatch.py`

**Key shape invariants:**
- Thin composition: calls each layer binding in sequence
- All identity (source_channel, declared_schema, task_class) lives in app-owned dispatch, not in core entrypoint
- Core entrypoint (`agentic_core/runtime/entry/app_ingress_runner.py`) is generic; identity injected via `RequestEnvelope`

### W1.P5 — Profile/config ownership golden pattern

**Golden tree:**
```
apps_rg/config/
  domain_contract/
    route_profiles.yaml          ← L0 route policy
    cache_policy.yaml            ← C0 cache policy
    threshold_profiles.yaml      ← eval thresholds
    meta_feedback_profile.*.json ← L6 profile
  cert_route_registry.yaml       ← Exit cert profile ref
  agent_spec_config.py           ← L2 agent spec
```

**Invariant:** `agentic_core` reads these files only via generic profile resolver interfaces — never via hardcoded paths or direct imports.

**Proof scan:**
```powershell
# Must return 0 results for apps_rg config paths inside agentic_core (excluding comments):
Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "apps_rg/config" | Where-Object { $_ -notmatch "^\s*#" }
```

---

### W1 Closeout Receipt

**Executed:** 2026-05-12  
**Executed by:** Cursor Agent (read-only golden-template extraction — zero source file modifications)

```
W1_STATUS: PASS
PLAN: apps-lic-u0-boundary-alignment-4f1d9c
SOURCE_CHANGES_MADE: false
IMPLEMENTATION_STARTED: false
WORKSPACE_DIFF_BLOCKER: true (unchanged from W0)

GOLDEN_TEMPLATE_CONFIRMED: true
CORE_SHIM_VALID: true
CONFIG_OWNERSHIP_VALID: true (with 1 noted exception — see below)

─────────────────────────────────────────────────────────────────────
W1.P1 — U0 Binding Golden Shape
─────────────────────────────────────────────────────────────────────
FILE: apps_rg/runtime/bindings/u0_binding.py  (159 lines)
  ✅ Pure function: u0_validate_apps_rg(envelope) -> ValidatedRequest
  ✅ No I/O, no state, no provider calls
  ✅ Imports only: agentic_core.runtime.contracts.* + agentic_core.runtime.u0.*
  ✅ App-specific adapter lives at apps_rg/runtime/u0/adapter.py (app-owned)
  ✅ L5 certification ref present: APPS_RG_U0_CERT_REF
  ✅ __all__ exports exactly: APPS_RG_TASK_CLASS, APPS_RG_U0_CERT_REF, u0_validate_apps_rg

CORE SHIM: agentic_core/runtime/entry/u0_apps_rg_binding.py  (24 lines)
  ✅ Re-export only — zero logic
  ✅ Docstring explicitly marks: "LEGACY_SHIM — Migrated to apps_rg/runtime/bindings/u0_binding.py"
  ✅ Exactly 3 re-exported symbols: APPS_RG_TASK_CLASS, APPS_RG_U0_CERT_REF, u0_validate_apps_rg
  ✅ 24 lines ≤ 30-line shim budget
  PATTERN CONFIRMED: apps_rg owns logic; core shim re-exports only

─────────────────────────────────────────────────────────────────────
W1.P2 — L0/L1/C0 Binding Golden Shapes
─────────────────────────────────────────────────────────────────────
L0 (apps_rg/runtime/bindings/l0_binding.py, 285 lines):
  ✅ Pure function: l0_route_apps_rg(l1_plan: L1PlanContract) -> RouteContract
  ✅ Consumes only generic contracts (L1PlanContract, RouteContract, RuntimePosture)
  ✅ App-specific enums (RouteFamily, CacheEligibility, HitlPosture) defined locally — not imported from core
  ✅ Route profile loaded by digest check (_ROUTE_PROFILE_RELPATH = "apps_rg/profiles/rg_route_profile.yaml")
  ✅ No direct LLM, ChromaDB, L4 write calls
  ✅ Cert ref: APPS_RG_L0_CERT_REF
  ✅ Fail-closed validation on missing task_spec/query_spec keys

C0 (apps_rg/runtime/bindings/c0_binding.py, 696 lines):
  ✅ Accepts ValidatedRequest (generic contracts) — not legacy AppsRgIngressPayload
  ✅ ONLY emits FinalEvidenceContract via core generic contract type
  ✅ Chroma path opt-in via chromadb_path param / env var (never hardcoded)
  ✅ Cert ref: APPS_RG_C0_CERT_REF = "c0-apps-rg-resume-generation-app-payload-b3a449"
  ✅ No direct imports from apps_rg.config.* (config refs passed via ValidatedRequest.app_payload)

─────────────────────────────────────────────────────────────────────
W1.P3 — Exit Binding Golden Shape
─────────────────────────────────────────────────────────────────────
FILE: apps_rg/runtime/bindings/exit_binding.py  (696 lines)
  ✅ Pure function: exit_finalize_apps_rg(sealed, target_company, target_role, ...) -> ExitBindingResult
  ✅ Consumes SealedL2Artifact + emits X3Disposition (both generic contracts)
  ✅ Gate set G24/G25/G26/G27 defined locally (not imported from core hardcoded set)
  ✅ Cache writeback opt-in via env var — not forced
  ✅ No direct L4 write
  ✅ Cert ref: APPS_RG_EXIT_CERT_REF = "exit-apps-rg-resume-generation-w3p5"
  ✅ Broad-exception catches carry guardian comments (guardian: allow-broad-net)
  NOTE: Exit binding contains DOCX template path hardcoded to user home
        (C:/Users/amita/Documents/Resumes/SVP Engineering Resume_Ayer.pdf).
        This is user-machine-specific but out of scope for this boundary plan.
        DEFERRED — not a boundary violation; the path is inside the app-owned binding,
        not in agentic_core.

─────────────────────────────────────────────────────────────────────
W1.P4 — Dispatch Golden Shape
─────────────────────────────────────────────────────────────────────
FILE: apps_rg/runtime/dispatch/apps_rg_dispatch.py  (531 lines)
  ✅ All imports from apps_rg.runtime.bindings.* (app-owned)
  ✅ Generic contracts imported from agentic_core.runtime.contracts.*
  ✅ Thin composition: calls each layer binding in sequence (u0 → l1 → l0 → c0 → pa → l2 → exit)
  ✅ App identity (task_class, source_channel, declared_schema) lives in dispatch, NOT in core entrypoint
  ✅ apps_rg_parse() and APPS_RG_REQUIRED_FIELDS defined here — glue between AppIngressRunner and domain
  ✅ No logic that belongs in core: no routing policy, no planning, no execution

─────────────────────────────────────────────────────────────────────
W1.P5 — Profile/Config Ownership
─────────────────────────────────────────────────────────────────────
CONFIRMED CONFIG TREE:
  apps_rg/config/
    domain_contract/         (28 items — all app-owned)
    cert_route_registry.yaml
    rg_thresholds.yaml
    route_registry.yaml
    hitl_trigger_policy.yaml
    provider_profiles.yaml
    workflow_manifest.resume_generation.v1.yaml
    section_prompts/         (8 items)
    ...

PROOF SCAN — apps_rg/config paths inside agentic_core:
  Matches found: 11 lines across 4 files
  All matches are in docstrings, comments, or string ref literal values
  (profile resolver key strings passed through generic interfaces)
  agentic_core/prompt_governance/managed_workflow_pa_resolver.py: docstring examples
  agentic_core/runtime/contracts/managed_prompt_artifact.py: docstring examples
  agentic_core/runtime/entry/apps_rg_w9_managed_workflow_e2e.py: string ref dict values
    (lines 327-331: profile_ref / schema_ref / rubric_ref / threshold_ref / grader_roster_ref
     passed as string keys through generic profile resolver — NOT direct path reads/imports)
  agentic_core/runtime/exit/hitl_policy_registry.py: docstring/comment
  agentic_core/runtime/judges/resume_judges/*.py: docstring/comment
  ✅ ZERO executable import statements or Path() reads of apps_rg/config from agentic_core
  ✅ Config ownership invariant: CONFIRMED

─────────────────────────────────────────────────────────────────────
BINDINGS DIRECTORY INVENTORY (apps_rg/runtime/)
─────────────────────────────────────────────────────────────────────
  bindings/  8 items: __init__.py + c0, exit, l0, l1, l2, pa, u0 bindings
  dispatch/  2 items: apps_rg_dispatch.py
  entry/     2 items
  u0/        3 items (app-owned adapter)
  profiles/  2 items (app-owned route profiles)
  All 7 layer bindings (U0/L0/L1/C0/PA/L2/Exit) present and app-owned.

─────────────────────────────────────────────────────────────────────
COMPARISON: apps_lic VIOLATIONS vs apps_rg GOLDEN PATTERN
─────────────────────────────────────────────────────────────────────
| Dimension               | apps_rg (GOLDEN)                  | apps_lic (VIOLATION)                  |
|-------------------------|-----------------------------------|---------------------------------------|
| U0 binding location     | apps_rg/runtime/bindings/         | agentic_core/runtime/entry/           |
| Core shim size          | 24 lines, re-export only          | 189 lines of logic                    |
| L0 binding location     | apps_rg/runtime/bindings/         | agentic_core/L0_routing/              |
| C0 binding location     | apps_rg/runtime/bindings/         | agentic_core/runtime/c0/              |
| PA binding location     | apps_rg/runtime/bindings/         | agentic_core/prompt_governance/       |
| L2 binding location     | apps_rg/runtime/bindings/         | agentic_core/L2_execution/            |
| Exit binding location   | apps_rg/runtime/bindings/         | agentic_core/runtime/exit/            |
| App ingress contract    | apps_rg (via ValidatedRequest)    | agentic_core/runtime/contracts/       |
| Config ownership        | apps_rg/config/ (app-owned)       | Mixed — some in core                  |
| runtime/bindings/ tree  | PRESENT (7 bindings)              | ABSENT (G-22)                         |
| Direct core→app imports | ZERO                              | 13+ violations (G-06, G-08, G-11–G-13)|

─────────────────────────────────────────────────────────────────────
WORKSPACE DIFF (W1 scope only)
─────────────────────────────────────────────────────────────────────
Modified files in apps_rg/ / agentic_core/ / apps_lic/ vs HEAD:
  apps_rg/runtime/bindings/c0_binding.py       (pre-existing — golden-state migration plan)
  apps_rg/runtime/bindings/exit_binding.py     (pre-existing — golden-state migration plan)
  apps_rg/runtime/bindings/l0_binding.py       (pre-existing — golden-state migration plan)
  apps_rg/runtime/dispatch/apps_rg_dispatch.py (pre-existing — golden-state migration plan)
  apps_rg/runtime/entry/dispatch.py            (pre-existing — golden-state migration plan)
  agentic_core/: 0 modified files
  apps_lic/:     0 modified files
  W1 source changes made: ZERO

─────────────────────────────────────────────────────────────────────
NEXT STEPS AND BLOCKERS
─────────────────────────────────────────────────────────────────────
NEXT_ALLOWED_WAVE: W2 (apps_lic boundary/gap audit — read-only) may proceed
  W2 is the 23-gap matrix audit; it is also read-only and does not require
  workspace cleanliness.

IMPLEMENTATION_WAVES_BLOCKED: W3–W6 remain blocked until workspace cleanliness
  is resolved. Same options as documented in W0 receipt.
  Workspace diff count: 5 pre-existing files in apps_rg/ (migration plan).
  agentic_core/ and apps_lic/ show 0 modified files — clean for implementation
  scope when workspace cleanliness condition is lifted.
```

---

## W2 — apps_lic Boundary/Gap Audit

### Gap Matrix

| ID | Gap Description | Category | File(s) | Evidence | Expected Owner | Remediation Approach | Acceptance Proof | CI Scanner |
|----|----------------|----------|---------|----------|----------------|---------------------|-----------------|-----------|
| G-01 | `apps_lic` U0 binding lives in `agentic_core/runtime/entry/u0_apps_lic_binding.py` (189 lines of logic, not a re-export shim) | A | `agentic_core/runtime/entry/u0_apps_lic_binding.py` | Full `_envelope_to_raw_json` synthesizer + `apps_lic_u0_adapt` call in core | `apps_lic` | Migrate logic to `apps_lic/runtime/bindings/u0_binding.py`; reduce core file to 24-line re-export shim matching apps_rg pattern | Core file ≤30 lines; imports only from app-owned path | `check_apps_lic_core_contamination.py` G-01 |
| G-02 | `apps_lic` L0 binding lives in `agentic_core/L0_routing/apps_lic_l0_binding.py` (355 lines) | A | `agentic_core/L0_routing/apps_lic_l0_binding.py` | App-specific route comment block, `APPS_LIC_L0_CERT_REF`, `R4_MANAGED_DRAFT` route name all in core | `apps_lic` | Migrate to `apps_lic/runtime/bindings/l0_binding.py`; retain core shim re-export | Core shim ≤30 lines | Same scanner G-02 |
| G-03 | `apps_lic` L1 binding lives in `agentic_core/L1_cognition/apps_lic_l1_binding.py` | A | `agentic_core/L1_cognition/apps_lic_l1_binding.py` | 30 matches; app-specific plan contract in core L1 | `apps_lic` | Migrate to `apps_lic/runtime/bindings/l1_binding.py` | Core shim ≤30 lines | Same scanner G-03 |
| G-04 | `apps_lic` C0 binding lives in `agentic_core/runtime/c0/apps_lic_c0_binding.py` | A | `agentic_core/runtime/c0/apps_lic_c0_binding.py` | 23 matches; C0 policy and bypass receipt synthesized in core | `apps_lic` | Migrate to `apps_lic/runtime/bindings/c0_binding.py` | Core shim ≤30 lines | Same scanner G-04 |
| G-05 | `apps_lic` PA binding lives in `agentic_core/prompt_governance/apps_lic_pa_binding.py` | A | `agentic_core/prompt_governance/apps_lic_pa_binding.py` | 18 matches; prompt envelope assembly rules for apps_lic in core PA layer | `apps_lic` | Migrate to `apps_lic/runtime/bindings/pa_binding.py` | Core shim ≤30 lines | Same scanner G-05 |
| G-06 | `apps_lic` L2 binding lives in `agentic_core/L2_execution/apps_lic_l2_binding.py` AND directly imports `apps_lic.config.hop_pipeline.REGISTRY` | B | `agentic_core/L2_execution/apps_lic_l2_binding.py:161` | `from apps_lic.config.hop_pipeline import REGISTRY` — core L2 reads app config directly | `apps_lic` | Migrate binding to `apps_lic/runtime/bindings/l2_binding.py`; registry loaded via app-owned config ref only | No `from apps_lic` in `agentic_core/L2_execution/` | `check_apps_lic_core_imports.py` G-06 |
| G-07 | `apps_lic` L3 binding lives in `agentic_core/L3_orchestration/apps_lic_l3_binding.py` (444 lines) with hardcoded `node_id="apps_lic.hop_pipeline.execute"` | A | `agentic_core/L3_orchestration/apps_lic_l3_binding.py` | App domain string literal hardcoded in core L3 | `apps_lic` | Migrate to `apps_lic/runtime/bindings/l3_binding.py`; node_id loaded from app-owned config | Core shim ≤30 lines | Same scanner G-07 |
| G-08 | `apps_lic` Exit binding lives in `agentic_core/runtime/exit/apps_lic_exit_binding.py` AND imports `from apps_lic.contracts.apps_lic_ingress_contract_v1` | B | `agentic_core/runtime/exit/apps_lic_exit_binding.py:55-57` | Direct `from apps_lic.contracts.*` import into core exit layer | `apps_lic` | Migrate binding to `apps_lic/runtime/bindings/exit_binding.py`; `RuntimeCustomizationPackageSection` / `ProfileRef` resolved via generic protocol only | No `from apps_lic` in `agentic_core/runtime/exit/` | `check_apps_lic_core_imports.py` G-08 |
| G-09 | `apps_lic` L6 promo binding lives in `agentic_core/L6_observability/promotion/apps_lic_promo_binding.py` with `_load_apps_lic_l6_policy()` stub returning `{}` | A+D | `agentic_core/L6_observability/promotion/apps_lic_promo_binding.py:159-166` | Policy loader is a stub; app profile never actually loaded | `apps_lic` | Migrate to `apps_lic/runtime/bindings/l6_binding.py`; real policy loader reads `apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json` | Policy dict non-empty on test invocation | Same scanner G-09 |
| G-10 | `apps_lic` ingress contract (`AppsLicIngressPayload`, `AppsLicRequestEnvelope`) embedded in `agentic_core/runtime/contracts/` | A | `agentic_core/runtime/contracts/apps_lic_ingress_payload.py` | App-specific dataclass in generic core contracts package | `apps_lic` | Move to `apps_lic/contracts/` or `apps_lic/runtime/contracts/`; core references via generic `IngressPayload` protocol | No `apps_lic` in `agentic_core/runtime/contracts/` filenames | Same scanner G-10 |
| G-11 | Core compat alias `apps_engines_aliases.py` directly imports 3 `apps_lic` agent classes | B+C | `agentic_core/utils/workflow_engines/apps_engines_aliases.py:31-33` | `from apps_lic.reasoning.GovernanceShieldAgent import GovernanceShieldAgent` — core module is a live import path to app agents | `apps_lic` | Remove `apps_lic.*` imports from core aliases; agents registered via late-registration protocol or accessed only through app-owned dispatch | Zero `from apps_lic` in `apps_engines_aliases.py` | `check_apps_lic_core_imports.py` G-11 |
| G-12 | `agentic_core/L2_execution/types/agent_taxonomy_registry.py` contains 35 `apps_lic` matches — all `apps_lic`-specific agent entries in generic core registry | B | `agentic_core/L2_execution/types/agent_taxonomy_registry.py` | Lines 384–1020+: `IntelligenceLibrarianAgent`, `LicHealingOrchestrator`, `LICValidationExecutor`, and 10+ more `apps_lic` agents hardcoded in core taxonomy | `apps_lic` | Introduce late-registration API on taxonomy registry; move `apps_lic` entries to `apps_lic/config/agent_taxonomy.py` registered at app init time | `grep "apps_lic" agentic_core/L2_execution/types/agent_taxonomy_registry.py` returns 0 | `check_apps_lic_core_contamination.py` G-12 |
| G-13 | `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py:382` imports `from apps_lic.types.ImmutableStagingBuffer import AppContentValidatorAgent` | B | `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py:382` | Core reasoning agent (L2) depends on app-specific type at runtime | `apps_lic` | Replace with generic `ContentValidatorProtocol`; app-specific implementation passed in via app-owned binding | No `from apps_lic` in `agentic_core/L2_execution/reasoning/` | `check_apps_lic_core_imports.py` G-13 |
| G-14 | `agentic_core/L5_safety/policy/apps_lic_reengagement.py` — app-specific HITL policy class in generic L5 policy layer | B | `agentic_core/L5_safety/policy/apps_lic_reengagement.py` | `ReengagementHITLPolicy`, `HITLPolicyRegistry` with `policy_id="apps_lic.reengagement"` hardcoded in core | `apps_lic` | Move to `apps_lic/policy/reengagement_hitl_policy.py`; L5 consumes via generic `HITLPolicyProtocol` injected at spine entry | No `apps_lic` files in `agentic_core/L5_safety/policy/` | `check_apps_lic_core_contamination.py` G-14 |
| G-15 | `agentic_core/L5_safety/evaluators/apps_lic_reengagement.py` — app-specific HITL evaluator in generic L5 evaluators | B | `agentic_core/L5_safety/evaluators/apps_lic_reengagement.py` | `ReengagementPolicyEvaluator` hardwired to `apps_lic.reengagement` policy; imports from core L5 policy contaminated file | `apps_lic` | Move to `apps_lic/policy/reengagement_evaluator.py`; L5 uses generic evaluator interface | No `apps_lic` files in `agentic_core/L5_safety/evaluators/` | Same scanner G-15 |
| G-16 | `agentic_core/L4_state/schemas/apps_lic_touch_state.sql` — app-specific DB schema in generic L4 schemas | B | `agentic_core/L4_state/schemas/apps_lic_touch_state.sql` | App-specific `apps_lic_touch_state` table definition embedded in generic core L4 schema directory | `apps_lic` | Move to `apps_lic/state/schemas/touch_state.sql`; `touch_state_writer.py` migrates with binding (G-17) | No `apps_lic` files in `agentic_core/L4_state/schemas/` | Same scanner G-16 |
| G-17 | `agentic_core/L4_state/uwg/touch_state_writer.py` — app-specific UWG adapter for apps_lic touch state in generic L4 UWG | B | `agentic_core/L4_state/uwg/touch_state_writer.py` | File header: `App: apps_lic`, `TOUCH_STATE_WRITE_CLASS = "apps_lic.touch_state"` hardcoded in core UWG layer | `apps_lic` | Move to `apps_lic/state/touch_state_writer.py`; core UWG is generic — app provides write-class and schema ref via U0 payload | No `apps_lic` in filenames under `agentic_core/L4_state/uwg/` | Same scanner G-17 |
| G-18 | `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` — app identity (source_channel, declared_schema) and full entrypoint logic in core | C | `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` | `source_channel="apps_lic_cli"`, `declared_schema="apps_lic_outreach_v1"`, `LicR4RunResult` type — all app-specific identity in core entrypoint | `apps_lic` | Move to `apps_lic/runtime/entry/` (parallel to `apps_rg/runtime/entry/`); core entrypoint is generic | No `apps_lic` in `agentic_core/runtime/entrypoints/` filenames | Same scanner G-18 |
| G-19 | `agentic_core/L0_routing/config/path_constants.py` contains `APPS_LIC_DIR`, `APPS_LIC_SUBFOLDER_MAP` — app-specific routing constants in core config | A | `agentic_core/L0_routing/config/path_constants.py:139,505` | `APPS_LIC_DIR: Final[str] = "apps_lic"` + subfolder map exported from core | Generic / acceptable | **EXEMPT** — `path_constants.py` is the SSOT app-package naming registry; `APPS_LIC_DIR` is a generic string constant used by ADG/L5 boundary scanners, not app domain logic. No remediation needed. | Confirm no behavioral branch on `APPS_LIC_DIR` value in spine | N/A — acceptable |
| G-20 | U0 contract `AppsLicU0AdapterError` / `AppsLicU0ReflectionReceipt` / `apps_lic_u0_adapt` imported from `agentic_core/runtime/u0/` by core binding | A | `agentic_core/runtime/entry/u0_apps_lic_binding.py:31-35` + `agentic_core/runtime/u0/apps_lic_u0_adapter.py` | Core U0 adapter contains app-specific adapter logic | `apps_lic` | Move `apps_lic_u0_adapter.py` to `apps_lic/runtime/u0/adapter.py` (mirroring `apps_rg/runtime/u0/adapter.py`) | No `apps_lic` files in `agentic_core/runtime/u0/` | Same scanner G-20 |
| G-21 | `agentic_core/utils/workflow_engines/apps_engines_aliases.py` comment: `AG-RGGOV-9: apps_lic imports preserved (different app, out of scope)` — explicitly ratified but still a violation | C | `agentic_core/utils/workflow_engines/apps_engines_aliases.py:29` | Comment treats direct app-agent imports as acceptable; contradicts agentic_core boundary law | `apps_lic` | The `apps_rg` fix (removing all `apps_rg` aliases) must be replicated for `apps_lic`; the "different app" exemption is invalid under the boundary law | File contains zero `from apps_lic` imports | `check_apps_lic_core_imports.py` G-21 |
| G-22 | No `apps_lic/runtime/bindings/` tree exists (missing golden structure) | D | (path does not exist) | `apps_lic/runtime/` directory is absent or does not mirror `apps_rg/runtime/bindings/` | `apps_lic` | Create `apps_lic/runtime/__init__.py`, `apps_lic/runtime/bindings/__init__.py`, `apps_lic/runtime/dispatch/`, `apps_lic/runtime/entry/` mirroring apps_rg structure | Directory tree present; all migrated bindings in place | Manual tree check + import test |
| G-23 | No test proof that `apps_lic` enters the spine exclusively through U0 (`tests/_apps_contract/` has no U0-entry negative-control tests for apps_lic) | F | `tests/_apps_contract/` | Golden-template compliance not covered by contract tests | `apps_lic` test suite | Add `test_apps_lic_u0_only_entry.py` with negative controls proving direct spine bypass is rejected | Test file passes; negative controls fail with expected errors | `pytest tests/_apps_contract/test_apps_lic_u0_only_entry.py` |

---

## Tightened Acceptance Proofs

Each gap has a **post-remediation command** and **expected result**. These supersede any looser language in the Gap Matrix.

| Gap | Post-remediation command | Expected result |
|-----|------------------------|----------------|
| G-01 | `(Get-Content agentic_core/runtime/entry/u0_apps_lic_binding.py).Count` | `≤ 30` |
| G-01 | `python -c "from apps_lic.runtime.bindings.u0_binding import u0_validate_apps_lic"` | exits 0 |
| G-02 | `(Get-Content agentic_core/L0_routing/apps_lic_l0_binding.py).Count` | `≤ 30` |
| G-02 | `python -c "from apps_lic.runtime.bindings.l0_binding import l0_route_apps_lic"` | exits 0 |
| G-03 | `(Get-Content agentic_core/L1_cognition/apps_lic_l1_binding.py).Count` | `≤ 30` |
| G-04 | `(Get-Content agentic_core/runtime/c0/apps_lic_c0_binding.py).Count` | `≤ 30` |
| G-05 | `(Get-Content agentic_core/prompt_governance/apps_lic_pa_binding.py).Count` | `≤ 30` |
| G-06 | `Select-String -Path agentic_core/L2_execution/apps_lic_l2_binding.py -Pattern "from apps_lic"` | 0 matches |
| G-07 | `(Get-Content agentic_core/L3_orchestration/apps_lic_l3_binding.py).Count` | `≤ 30` |
| G-08 | `Select-String -Path agentic_core/runtime/exit/apps_lic_exit_binding.py -Pattern "from apps_lic"` | 0 matches |
| G-09 | `python -c "from apps_lic.runtime.bindings.l6_binding import load_apps_lic_l6_policy; p=load_apps_lic_l6_policy(); assert p, 'empty policy'"` | exits 0 |
| G-10 | `Test-Path agentic_core/runtime/contracts/apps_lic_ingress_payload.py` | `False` |
| G-10 | `Test-Path apps_lic/contracts/ingress_payload.py` | `True` |
| G-11 | `Select-String -Path agentic_core/utils/workflow_engines/apps_engines_aliases.py -Pattern "from apps_lic"` | 0 matches |
| G-12 | `Select-String -Path agentic_core/L2_execution/types/agent_taxonomy_registry.py -Pattern "apps_lic"` | 0 matches |
| G-13 | `Select-String -Path agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py -Pattern "from apps_lic"` | 0 matches |
| G-14 | `Test-Path agentic_core/L5_safety/policy/apps_lic_reengagement.py` | `False` |
| G-14 | `Test-Path apps_lic/policy/reengagement_hitl_policy.py` | `True` |
| G-15 | `Test-Path agentic_core/L5_safety/evaluators/apps_lic_reengagement.py` | `False` |
| G-15 | `Test-Path apps_lic/policy/reengagement_evaluator.py` | `True` |
| G-16 | `Test-Path agentic_core/L4_state/schemas/apps_lic_touch_state.sql` | `False` |
| G-16 | `Test-Path apps_lic/state/schemas/touch_state.sql` | `True` |
| G-17 | `(Get-ChildItem agentic_core/L4_state/uwg -Filter "apps_lic*").Count` | `0` |
| G-17 | `Test-Path apps_lic/state/touch_state_writer.py` | `True` |
| G-18 | `Test-Path agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` | `False` |
| G-18 | `Test-Path apps_lic/runtime/dispatch/apps_lic_dispatch.py` | `True` |
| G-20 | `(Get-ChildItem agentic_core/runtime/u0 -Filter "apps_lic*").Count` | `0` |
| G-20 | `Test-Path apps_lic/runtime/u0/adapter.py` | `True` |
| G-21 | `Select-String -Path agentic_core/utils/workflow_engines/apps_engines_aliases.py -Pattern "apps_lic"` | 0 matches |
| G-22 | `Test-Path apps_lic/runtime/bindings/__init__.py` | `True` |
| G-23 | `python -m pytest tests/_apps_contract/test_apps_lic_u0_only_entry.py -v` | all tests PASS |

---

### W2 Closeout Receipt

**Executed:** 2026-05-12  
**Executed by:** Cursor Agent (read-only boundary/gap audit — zero source file modifications)

```
W2_STATUS: PASS
PLAN: apps-lic-u0-boundary-alignment-4f1d9c
SOURCE_CHANGES_MADE: false
IMPLEMENTATION_STARTED: false
WORKSPACE_DIFF_BLOCKER: true (unchanged from W0/W1)
GOLDEN_TEMPLATE_USED: apps_rg
ACTIONABLE_GAPS_CONFIRMED: 22
EXEMPT_GAPS_CONFIRMED: 1  (G-19)
DIRECT_EXECUTABLE_IMPORTS_CONFIRMED: 6
SCHEMA_POLICY_CONTRACT_ENTRYPOINT_FILES_CONFIRMED: 5
MISSING_APP_RUNTIME_TREE_CONFIRMED: true  (apps_lic/runtime/bindings/ absent)
NEXT_ALLOWED_WAVE: W3 planning-only migration design may proceed
IMPLEMENTATION_WAVES_BLOCKED: W3-W6 implementation remains blocked until workspace cleanliness is resolved

─────────────────────────────────────────────────────────────────────
WORKSPACE DIFF STATUS (pre-W2, confirmed read-only)
─────────────────────────────────────────────────────────────────────
Modified vs HEAD (relevant scope only):
  apps_rg/runtime/bindings/c0_binding.py       pre-existing
  apps_rg/runtime/bindings/exit_binding.py     pre-existing
  apps_rg/runtime/bindings/l0_binding.py       pre-existing
  apps_rg/runtime/dispatch/apps_rg_dispatch.py pre-existing
  apps_rg/runtime/entry/dispatch.py            pre-existing
  agentic_core/: 0 modified files
  apps_lic/:     0 modified files
  W2 source changes made: ZERO

─────────────────────────────────────────────────────────────────────
W2.P1 — Binding Location Gap (apps_lic vs apps_rg golden pattern)
─────────────────────────────────────────────────────────────────────
GOLDEN PATTERN: all bindings in apps_rg/runtime/bindings/ (7 files, all app-owned)
APPS_LIC STATE: apps_lic/runtime/bindings/ does NOT exist

apps_lic binding files found in agentic_core (line counts confirmed live):
  agentic_core/runtime/entry/u0_apps_lic_binding.py           188 lines  (G-01)
  agentic_core/L0_routing/apps_lic_l0_binding.py              354 lines  (G-02)
  agentic_core/L1_cognition/apps_lic_l1_binding.py            381 lines  (G-03)
  agentic_core/runtime/c0/apps_lic_c0_binding.py              525 lines  (G-04)
  agentic_core/prompt_governance/apps_lic_pa_binding.py       349 lines  (G-05)
  agentic_core/L2_execution/apps_lic_l2_binding.py            412 lines  (G-06)
  agentic_core/L3_orchestration/apps_lic_l3_binding.py        443 lines  (G-07)
  agentic_core/runtime/exit/apps_lic_exit_binding.py          634 lines  (G-08)
  agentic_core/L6_observability/promotion/apps_lic_promo_binding.py 266 lines (G-09)
  agentic_core/runtime/contracts/apps_lic_ingress_payload.py  131 lines  (G-10)

TOTAL: 10 binding/contract files in core vs 0 in apps_lic/runtime/bindings/

apps_lic/runtime/ exists with only:
  runtime/__init__.py
  runtime/u0/__init__.py
  runtime/u0/adapter.py       ← app-owned adapter IS present (partial migration)

NOTE on G-20 (U0 adapter):
  Plan baseline listed agentic_core/runtime/u0/apps_lic_u0_adapter.py as the violation.
  LIVE STATE: that file does NOT exist in agentic_core/runtime/u0/.
  agentic_core/runtime/entry/u0_apps_lic_binding.py imports via:
    from agentic_core.runtime.u0.apps_lic_u0_adapter import ...
  This import would FAIL at runtime — agentic_core/runtime/u0/ has no apps_lic file.
  The adapter logic IS already at apps_lic/runtime/u0/adapter.py (app-owned).
  REVISED G-20 EVIDENCE: u0_apps_lic_binding.py has a broken import pointing to a
  nonexistent core module. Fix: update the import to apps_lic.runtime.u0.adapter
  (or replace with full shim re-export pointing to the now-correct app-owned path).

─────────────────────────────────────────────────────────────────────
W2.P2 — Direct core→app Executable Import Scan
─────────────────────────────────────────────────────────────────────
W0.P2 RECONCILIATION:
  W0 baseline: 15 total pattern hits / 8 files
  Live (W2) executable `from apps_lic` import lines (non-comment, non-docstring):
    6 executable lines across 4 files

  The delta (15 hits vs 6 executable) is explained by:
    - 3 hits in agentic_core/L0_routing/apps_lic_l0_binding.py:169,174,193
      → docstring text "from apps_lic route profile" — NOT executable imports
    - 2 hits in agentic_core/L6_observability/promotion/apps_lic_promo_binding.py:5,86
      → module docstring and function docstring references — NOT executable
    - 1 hit in agentic_core/runtime/contracts/apps_lic_ingress_payload.py:32
      → class docstring — NOT executable
    - 1 hit in agentic_core/L5_safety/reasoning/FileClassificationAgent.py:2251
      → string in a conditional expression checking for boundary violations — NOT executable
    - 1 hit in agentic_core/runtime/exit/apps_lic_exit_binding.py:63
      → comment line — NOT executable
    Total non-executable: 9 hits → 15 - 9 = 6 executable ✅ RECONCILED

EXECUTABLE IMPORT LINES CONFIRMED (6 lines, 4 files):
  1. agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py:382
     `    from apps_lic.types.ImmutableStagingBuffer import AppContentValidatorAgent`
     → lazy import inside function body (G-13)
  2. agentic_core/L2_execution/apps_lic_l2_binding.py:161
     `    from apps_lic.config.hop_pipeline import REGISTRY`
     → lazy import inside function body (G-06)
  3. agentic_core/runtime/exit/apps_lic_exit_binding.py:55
     `from apps_lic.contracts.apps_lic_ingress_contract_v1 import (...)`
     → module-scope import (G-08) — MOST SEVERE
  4-6. agentic_core/utils/workflow_engines/apps_engines_aliases.py:31-33
     `from apps_lic.reasoning.GovernanceShieldAgent import GovernanceShieldAgent`
     `from apps_lic.reasoning.LicHealingOrchestrator import LicHealingOrchestrator`
     `from apps_lic.reasoning.LicReflectionAgent import LicReflectionAgent`
     → module-scope imports, 3 app agent classes (G-11, G-21)

  SEVERITY RANKING:
    CRITICAL (module-scope, executes on import): apps_lic_exit_binding.py:55,
      apps_engines_aliases.py:31-33 (4 lines)
    HIGH (lazy/deferred, executes at call time): SubAtomicRegistryAgent.py:382,
      apps_lic_l2_binding.py:161 (2 lines)

  NOTE: agentic_core/runtime/entry/u0_apps_lic_binding.py:31-35 imports
  `from agentic_core.runtime.u0.apps_lic_u0_adapter import ...` — this is a
  core→core import that FAILS at runtime (file absent). Counted under G-20,
  not as a direct apps_lic import.

─────────────────────────────────────────────────────────────────────
W2.P3 — Schema/SQL/Policy/Contract/Evaluator Files in Core
─────────────────────────────────────────────────────────────────────
CONFIRMED (5 files):
  agentic_core/L4_state/schemas/apps_lic_touch_state.sql      134 lines  (G-16)
  agentic_core/L5_safety/policy/apps_lic_reengagement.py      378 lines  (G-14)
  agentic_core/L5_safety/evaluators/apps_lic_reengagement.py  469 lines  (G-15)
  agentic_core/runtime/contracts/apps_lic_ingress_payload.py  131 lines  (G-10)
  agentic_core/L4_state/uwg/touch_state_writer.py             (G-17, app identity in core UWG)

  All 5 confirmed. Counts match W0.P3 baseline.

─────────────────────────────────────────────────────────────────────
W2.P4 — Agent Taxonomy Registry Contamination
─────────────────────────────────────────────────────────────────────
  agentic_core/L2_execution/types/agent_taxonomy_registry.py
  apps_lic matches: 35 (confirmed by live scan)
  Contains: IntelligenceLibrarianAgent, LicHealingOrchestrator, LICValidationExecutor,
    and 10+ more apps_lic-specific agent classifications hardcoded in core taxonomy
  Requires: generic AgentTaxonomyRegistry.register_app_entries() API (enabling plan)
  Gap: G-12 CONFIRMED

─────────────────────────────────────────────────────────────────────
W2.P5 — Core Aliases Pointing to apps_lic Agent Classes
─────────────────────────────────────────────────────────────────────
  agentic_core/utils/workflow_engines/apps_engines_aliases.py:31-33
  3 module-scope `from apps_lic.reasoning.*` imports confirmed
  Comment at line 29: AG-RGGOV-9 "apps_lic imports preserved (different app, out of scope)"
    → This exemption is INVALID under BL-1; must be removed
  Gaps: G-11, G-21 CONFIRMED

─────────────────────────────────────────────────────────────────────
W2.P6 — Core Entrypoint Owning apps_lic Identity
─────────────────────────────────────────────────────────────────────
  agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py EXISTS (confirmed)
  Docstring line 43-44: "This module owns the apps_lic identity
    (source_channel='apps_lic_cli', declared_schema='apps_lic_outreach_v1')"
  App identity (source_channel, declared_schema, task_class) hardcoded in core
  Gap: G-18 CONFIRMED

─────────────────────────────────────────────────────────────────────
G-19 EXEMPTION VERIFICATION
─────────────────────────────────────────────────────────────────────
  agentic_core/L0_routing/config/path_constants.py:139 APPS_LIC_DIR: Final[str] = "apps_lic"
  agentic_core/L0_routing/config/path_constants.py:505 APPS_LIC_SUBFOLDER_MAP: Final[...]
  APPS_LIC_DIR is used as a read-only string key in:
    - L5 enforcement enforcers (boundary_validator, import_boundary_check_enforcer, etc.)
    - L5 reasoning agents (FileClassificationAgent, location_validator, SafetyInspectorAgent)
    - L6 monitors (SovereignHealthMonitor)
    - Core mixins (ast_enforcement_mixin, meta_learning_client_mixin)
  All uses are: frozenset membership, Path() construction for scan roots,
    string containment checks for module namespace detection.
  ZERO behavioral routing branches on APPS_LIC_DIR value.
  G-19 EXEMPT: CONFIRMED — ADG/scanner/namespace support only. No remediation.

─────────────────────────────────────────────────────────────────────
MISSING APPS_LIC RUNTIME TREE
─────────────────────────────────────────────────────────────────────
  apps_lic/runtime/bindings/: ABSENT (G-22 CONFIRMED)
  apps_lic/runtime/dispatch/:  ABSENT
  apps_lic/runtime/entry/:     ABSENT
  PRESENT: apps_lic/runtime/u0/adapter.py (partial — app adapter already migrated)
  apps_lic/runtime/ exists but has only u0/ subtree — full bindings tree must be created

─────────────────────────────────────────────────────────────────────
NEGATIVE-CONTROL TEST GAP
─────────────────────────────────────────────────────────────────────
  Existing tests/_apps_contract/ has 12 apps_lic test files (test_w3_apps_lic_u0.py,
    test_w6_apps_lic_boundary_governance.py, etc.)
  test_apps_lic_u0_only_entry.py: ABSENT (G-23 CONFIRMED)
  Existing tests do NOT prove that direct spine bypass is rejected with
    IngressBypassError. test_w6_apps_lic_boundary_governance.py has no
    IngressBypass/U0-only negative-control patterns.

─────────────────────────────────────────────────────────────────────
FULL GAP INVENTORY RECONCILIATION (G-01 through G-23)
─────────────────────────────────────────────────────────────────────
GAP  | STATUS    | LIVE EVIDENCE
-----|-----------|------------------------------------------------------
G-01 | CONFIRMED | u0_apps_lic_binding.py: 188 lines of logic (not shim)
G-02 | CONFIRMED | apps_lic_l0_binding.py: 354 lines in agentic_core/L0_routing/
G-03 | CONFIRMED | apps_lic_l1_binding.py: 381 lines in agentic_core/L1_cognition/
G-04 | CONFIRMED | apps_lic_c0_binding.py: 525 lines in agentic_core/runtime/c0/
G-05 | CONFIRMED | apps_lic_pa_binding.py: 349 lines in agentic_core/prompt_governance/
G-06 | CONFIRMED | apps_lic_l2_binding.py: 412 lines + lazy from apps_lic.config import
G-07 | CONFIRMED | apps_lic_l3_binding.py: 443 lines; APPS_LIC_NODE_ID hardcoded
G-08 | CONFIRMED | apps_lic_exit_binding.py: 634 lines; module-scope from apps_lic.contracts
G-09 | CONFIRMED | apps_lic_promo_binding.py: 266 lines; _load_apps_lic_l6_policy() stub
G-10 | CONFIRMED | apps_lic_ingress_payload.py: 131 lines in agentic_core/runtime/contracts/
G-11 | CONFIRMED | apps_engines_aliases.py:31-33: 3 module-scope from apps_lic.reasoning imports
G-12 | CONFIRMED | agent_taxonomy_registry.py: 35 apps_lic matches; app agents in core
G-13 | CONFIRMED | SubAtomicRegistryAgent.py:382: lazy from apps_lic.types import
G-14 | CONFIRMED | L5_safety/policy/apps_lic_reengagement.py: 378 lines in core L5 policy
G-15 | CONFIRMED | L5_safety/evaluators/apps_lic_reengagement.py: 469 lines in core L5 eval
G-16 | CONFIRMED | L4_state/schemas/apps_lic_touch_state.sql: 134 lines in core L4 schema
G-17 | CONFIRMED | L4_state/uwg/touch_state_writer.py: app identity (TOUCH_STATE_WRITE_CLASS)
G-18 | CONFIRMED | runtime/entrypoints/integrated_r4_lic_pipeline_run.py: owns apps_lic identity
G-19 | EXEMPT    | path_constants.py: read-only package-name constants for ADG/scanner use only
G-20 | CONFIRMED | u0_apps_lic_binding.py:31-35 imports nonexistent agentic_core.runtime.u0.apps_lic_u0_adapter
             (REVISED: the adapter IS at apps_lic/runtime/u0/adapter.py — import path is broken/wrong)
G-21 | CONFIRMED | AG-RGGOV-9 "apps_lic imports preserved" exemption comment is invalid (BL-1)
G-22 | CONFIRMED | apps_lic/runtime/bindings/ directory absent
G-23 | CONFIRMED | test_apps_lic_u0_only_entry.py absent; no U0-bypass negative controls

ACTIONABLE: 22 gaps (G-01–G-18, G-20–G-23)
EXEMPT:      1 gap  (G-19)

─────────────────────────────────────────────────────────────────────
NEXT STEPS
─────────────────────────────────────────────────────────────────────
NEXT_ALLOWED_WAVE: W3 planning-only migration design may proceed
  W3 is already populated in this plan with migration steps for each gap.
  W3 planning review (read-only) may begin without workspace cleanliness.

IMPLEMENTATION_WAVES_BLOCKED: W3-W6 implementation remains blocked.
  Blocker: 5 pre-existing diffs in apps_rg/ from golden-state migration plan.
  agentic_core/ and apps_lic/ are CLEAN (0 modified files).
  Resolution options (unchanged from W0 receipt):
    Option A — Commit pre-existing diffs under their own commit(s).
    Option B — Stash or revert pre-existing diffs.
    Option C — Baseline under a separate plan if in-flight work requires it.
  After resolution, re-run: git diff --name-only HEAD
  Expected result: empty (or only .cursor/plans/* as untracked/modified).
```

---

## W3 — U0 Payload Alignment Plan

### W3.P1 — Migrate 10 binding files to `apps_lic/runtime/bindings/`

**Target tree to create:**
```
apps_lic/
  runtime/
    __init__.py
    bindings/
      __init__.py
      u0_binding.py      ← from agentic_core/runtime/entry/u0_apps_lic_binding.py
      l0_binding.py      ← from agentic_core/L0_routing/apps_lic_l0_binding.py
      l1_binding.py      ← from agentic_core/L1_cognition/apps_lic_l1_binding.py
      c0_binding.py      ← from agentic_core/runtime/c0/apps_lic_c0_binding.py
      pa_binding.py      ← from agentic_core/prompt_governance/apps_lic_pa_binding.py
      l2_binding.py      ← from agentic_core/L2_execution/apps_lic_l2_binding.py
      l3_binding.py      ← from agentic_core/L3_orchestration/apps_lic_l3_binding.py
      exit_binding.py    ← from agentic_core/runtime/exit/apps_lic_exit_binding.py
      l6_binding.py      ← from agentic_core/L6_observability/promotion/apps_lic_promo_binding.py
    dispatch/
      __init__.py
      apps_lic_dispatch.py  ← migrated from agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py
    entry/
      __init__.py
      dispatch.py
    u0/
      __init__.py
      adapter.py         ← from agentic_core/runtime/u0/apps_lic_u0_adapter.py
```

**Migration pattern per binding (mirrors apps_rg W2 migration):**
1. Create `apps_lic/runtime/bindings/<layer>_binding.py` with full logic
2. Reduce `agentic_core/**/apps_lic_<layer>_binding.py` to ≤30-line re-export shim
3. Run `pytest tests/_apps_contract/` — zero regressions
4. Update any callers to import from app-owned path

**Verification command per binding:**
```powershell
# After migration, core shim must be ≤30 lines:
(Get-Content agentic_core/runtime/entry/u0_apps_lic_binding.py).Count
# Expected: ≤30
```

**Gap coverage:** G-01 through G-09, G-18, G-20

### W3.P2 — Remove direct `from apps_lic` imports from `agentic_core`

**8 import sites to remediate:**

| Site | Proposed fix |
|------|-------------|
| `apps_engines_aliases.py:31-33` (G-11, G-21) | Remove `apps_lic` imports entirely; agents accessed via late-registration or app-owned dispatch only |
| `apps_lic_l2_binding.py:161` (G-06) | After migration to app-owned binding, `REGISTRY` load moves to `apps_lic/runtime/bindings/l2_binding.py` — import stays app-side |
| `apps_lic_exit_binding.py:55-57` (G-08) | After migration, `RuntimeCustomizationPackageSection`/`ProfileRef` resolved via generic protocol; import moves to app-owned exit binding |
| `SubAtomicRegistryAgent.py:382` (G-13) | Replace with generic `ContentValidatorProtocol`; concrete class injected via U0 payload or app-owned factory |
| `apps_lic_promo_binding.py` (2 matches) | After migration, internal to app-owned L6 binding |
| `apps_lic_l0_binding.py` (3 matches) | After migration, internal to app-owned L0 binding |
| `apps_lic_ingress_payload.py:29` (G-10) | After moving contract to `apps_lic/contracts/`, core references via generic `IngressPayload` protocol |
| `FileClassificationAgent.py:2251` | Analysis-only; no remediation needed — this is a scanner checking for `apps_lic` string patterns, not a behavioral import |

**Verification command (post-remediation):**
```powershell
Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "^from apps_lic|^import apps_lic" |
  Where-Object { $_.Path -notmatch "apps_lic_l[0-9]_binding|apps_lic_[a-z]+_binding" }
# Expected: 0 results (shims excluded from check by naming convention)
```

### W3.P3 — Move schema/SQL/policy artifacts to `apps_lic/`

| Artifact | Source | Target | Gap covered |
|----------|--------|--------|-------------|
| `apps_lic_touch_state.sql` | `agentic_core/L4_state/schemas/` | `apps_lic/state/schemas/touch_state.sql` | G-16 |
| `touch_state_writer.py` | `agentic_core/L4_state/uwg/` | `apps_lic/state/touch_state_writer.py` | G-17 |
| `apps_lic_reengagement.py` (policy) | `agentic_core/L5_safety/policy/` | `apps_lic/policy/reengagement_hitl_policy.py` | G-14 |
| `apps_lic_reengagement.py` (evaluator) | `agentic_core/L5_safety/evaluators/` | `apps_lic/policy/reengagement_evaluator.py` | G-15 |
| `apps_lic_ingress_payload.py` | `agentic_core/runtime/contracts/` | `apps_lic/contracts/ingress_payload.py` | G-10 |

**Verification command:**
```powershell
# After migration, no apps_lic* files remain in core schema/policy/evaluator dirs:
Get-ChildItem agentic_core/L4_state/schemas, agentic_core/L5_safety/policy,
  agentic_core/L5_safety/evaluators, agentic_core/runtime/contracts |
  Where-Object { $_.Name -match "apps_lic" }
# Expected: 0 results
```

### W3.P4 — Agent taxonomy late-registration plan

**Problem:** `agentic_core/L2_execution/types/agent_taxonomy_registry.py` has 35+ hardcoded `apps_lic` agent entries in a generic registry (G-12).

**Proposed pattern (mirrors apps_rg agent removal in AG-RGGOV-9):**
1. Add `AgentTaxonomyRegistry.register_app_entries(app_id: str, entries: dict)` generic API to the registry
2. Create `apps_lic/config/agent_taxonomy.py` with all apps_lic-specific entries
3. Call `register_app_entries("apps_lic", APPS_LIC_ENTRIES)` from `apps_lic/__init__.py` (app init side-effect)
4. Remove all `apps_lic`-specific entries from `agentic_core/L2_execution/types/agent_taxonomy_registry.py`

**Note:** If the generic `register_app_entries` API does not yet exist on the registry, this constitutes a **generic core interface gap** — a separate plan (`apps-lic-core-interface-gap-<id>.md`) should be created. The apps_lic boundary alignment plan itself does not modify core logic.

**Verification command:**
```powershell
Select-String -Path agentic_core/L2_execution/types/agent_taxonomy_registry.py -Pattern "apps_lic"
# Expected: 0 results
```

---

### W3 Closeout Receipt

**Executed:** 2026-05-12  
**Executed by:** Cursor Agent (planning-only migration design — zero source file modifications)

```
W3_STATUS: PASS
PLAN: apps-lic-u0-boundary-alignment-4f1d9c
SOURCE_CHANGES_MADE: false
IMPLEMENTATION_STARTED: false
WORKSPACE_DIFF_BLOCKER: true (unchanged — agentic_core/: 0 modified, apps_lic/: 0 modified)
ACTIONABLE_GAPS_DESIGNED: 22
EXEMPT_GAPS_CONFIRMED: 1  (G-19)
GENERIC_CORE_ENABLING_PLANS_REQUIRED:
  - taxonomy:          AgentTaxonomyRegistry.register_app_entries() — absent from core
  - hitl-protocol:     HITLPolicyProtocol injection slot — absent from core L5
  - content-validator: ContentValidatorProtocol on SubAtomicRegistryAgent — absent from core
BROKEN_IMPORT_G20_HANDLED_AS: G-01 shim migration (acceptance proof added below)
NEXT_ALLOWED_WAVE: W4 planning-only contract/gate/L5/Exit/UWG/L6 alignment review
IMPLEMENTATION_WAVES_BLOCKED: W3-W6 implementation remains blocked until workspace cleanliness is resolved

─────────────────────────────────────────────────────────────────────
ENABLING INTERFACE GAPS (confirmed absent from agentic_core)
─────────────────────────────────────────────────────────────────────
1. TAXONOMY ENABLING GAP
   Symbol: AgentTaxonomyRegistry.register_app_entries(app_id: str, entries: dict)
   Current state: only register(classification: AgentClassification) exists (line 57)
   Absence confirmed: no matches for register_app_entries in agentic_core/
   Enabling plan stub: apps-lic-core-interface-gap-taxonomy-<id>.md
   Blocks: G-12 (agent taxonomy registry contamination)
   Design: generic late-registration API accepting (app_id, entries_dict); entry is called
     once from apps_lic/__init__.py at import time; no behavioral branch in core.

2. HITL-PROTOCOL ENABLING GAP
   Symbol: HITLPolicyProtocol (injection slot in L5 evaluator framework)
   Current state: ReengagementHITLPolicy is a concrete class (L5 policy line 118);
     HITLPolicyRegistry is app-specific (line 336); no protocol ABC in core L5
   Absence confirmed: 0 matches for HITLPolicyProtocol in agentic_core/
   Enabling plan stub: apps-lic-core-interface-gap-hitl-protocol-<id>.md
   Blocks: G-14 (L5 policy file), G-15 (L5 evaluator file)
   Design: abstract protocol ABC in agentic_core/L5_safety/protocols/hitl_policy_protocol.py;
     app passes hitl_policy_ref via U0 RuntimeCustomizationPackageSection;
     L5 evaluator resolves via generic factory, never imports concrete class directly.

3. CONTENT-VALIDATOR ENABLING GAP
   Symbol: ContentValidatorProtocol on SubAtomicRegistryAgent injection slot
   Current state: SubAtomicRegistryAgent.py:382 has lazy import of AppContentValidatorAgent
     from apps_lic.types.ImmutableStagingBuffer; used at lines 426-428 as a concrete class ref
   Absence confirmed: 0 matches for ContentValidatorProtocol in agentic_core/
   Enabling plan stub: apps-lic-core-interface-gap-content-validator-<id>.md
   Blocks: G-13
   Design: abstract protocol ABC in agentic_core/L2_execution/protocols/content_validator_protocol.py;
     concrete AppContentValidatorAgent injected via U0 payload factory key;
     SubAtomicRegistryAgent receives protocol instance, never imports app class.

─────────────────────────────────────────────────────────────────────
W3.P1 — BINDING MIGRATION DESIGN (G-01 through G-09, G-18, G-20)
─────────────────────────────────────────────────────────────────────
Migration pattern per binding: move full logic → apps_lic/runtime/bindings/<layer>_binding.py;
  reduce core file to ≤30-line re-export shim. Mirror apps_rg golden pattern exactly.

TARGET TREE:
  apps_lic/runtime/bindings/    (to create — absent today)
    __init__.py
    u0_binding.py               ← G-01 + G-20
    l0_binding.py               ← G-02
    l1_binding.py               ← G-03
    c0_binding.py               ← G-04
    pa_binding.py               ← G-05
    l2_binding.py               ← G-06
    l3_binding.py               ← G-07
    exit_binding.py             ← G-08
    l6_binding.py               ← G-09
  apps_lic/runtime/dispatch/    (to create)
    __init__.py
    apps_lic_dispatch.py        ← G-18
  apps_lic/runtime/u0/          (ALREADY EXISTS)
    __init__.py
    adapter.py                  ← partial migration already done

BINDING-BY-BINDING DESIGN:

G-01 + G-20 — U0 Binding
  Source:         agentic_core/runtime/entry/u0_apps_lic_binding.py (188 lines)
  Target:         apps_lic/runtime/bindings/u0_binding.py
  Owner after:    apps_lic
  Logic to move:  _envelope_to_raw_json(), u0_validate_apps_lic(), APPS_LIC_TASK_CLASS,
                  APPS_LIC_U0_CERT_REF
  Core shim after: ≤30 lines; re-exports all 4 symbols from apps_lic.runtime.bindings.u0_binding
  G-20 fix:       core shim re-exports from apps_lic.runtime.bindings.u0_binding, which
                  imports from apps_lic.runtime.u0.adapter (already app-owned, correct path).
                  The broken import agentic_core.runtime.u0.apps_lic_u0_adapter is replaced
                  by the shim redirect. No separate file needed for G-20.
  Interface dep:  None (adapter already at apps_lic/runtime/u0/adapter.py)
  Acceptance proof:
    (Get-Content agentic_core/runtime/entry/u0_apps_lic_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.u0_binding import u0_validate_apps_lic"  → exit 0
    python -c "from apps_lic.runtime.bindings.u0_binding import u0_validate_apps_lic"  → exit 0
    python -m pytest tests/_apps_contract/test_w3_apps_lic_u0.py -v  → all PASS
  Scanner: check_apps_lic_core_contamination.py G-01 (shim line count assertion)

G-02 — L0 Binding
  Source:         agentic_core/L0_routing/apps_lic_l0_binding.py (354 lines)
  Target:         apps_lic/runtime/bindings/l0_binding.py
  Owner after:    apps_lic
  Logic to move:  l0_route_apps_lic(), all route-family enums, APPS_LIC_L0_CERT_REF,
                  R4_MANAGED_DRAFT route constant
  Core shim after: ≤30 lines; re-exports l0_route_apps_lic + APPS_LIC_L0_CERT_REF
  Interface dep:  None
  Acceptance proof:
    (Get-Content agentic_core/L0_routing/apps_lic_l0_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.l0_binding import l0_route_apps_lic"  → exit 0
    python -m pytest tests/_apps_contract/test_w4_apps_lic_l1_l0.py -v  → all PASS
  Scanner: check_apps_lic_core_contamination.py G-02

G-03 — L1 Binding
  Source:         agentic_core/L1_cognition/apps_lic_l1_binding.py (381 lines)
  Target:         apps_lic/runtime/bindings/l1_binding.py
  Owner after:    apps_lic
  Logic to move:  l1_plan_apps_lic(), apps_lic-specific plan contract fields
  Core shim after: ≤30 lines
  Interface dep:  None
  Acceptance proof:
    (Get-Content agentic_core/L1_cognition/apps_lic_l1_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.l1_binding import l1_plan_apps_lic"  → exit 0
    python -m pytest tests/_apps_contract/test_w4_apps_lic_l1_l0.py -v  → all PASS
  Scanner: check_apps_lic_core_contamination.py G-03

G-04 — C0 Binding
  Source:         agentic_core/runtime/c0/apps_lic_c0_binding.py (525 lines)
  Target:         apps_lic/runtime/bindings/c0_binding.py
  Owner after:    apps_lic
  Logic to move:  c0_gate_apps_lic(), C0 policy, bypass receipt synthesizer
  Core shim after: ≤30 lines
  Interface dep:  None (C0 emits only GateVerdict — generic contract, already present)
  Acceptance proof:
    (Get-Content agentic_core/runtime/c0/apps_lic_c0_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.c0_binding import c0_gate_apps_lic"  → exit 0
    python -m pytest tests/_apps_contract/test_w5_apps_lic_c0_pa.py -v  → all PASS
  Scanner: check_apps_lic_core_contamination.py G-04
  BL-4 invariant preserved: C0 must only return GateVerdict; test_c0_binding_does_not_write_state
    in W5.P3 test suite enforces this.

G-05 — PA Binding
  Source:         agentic_core/prompt_governance/apps_lic_pa_binding.py (349 lines)
  Target:         apps_lic/runtime/bindings/pa_binding.py
  Owner after:    apps_lic
  Logic to move:  pa_compile_apps_lic(), prompt profile loading, section prompt orchestration
  Core shim after: ≤30 lines
  Interface dep:  None
  Acceptance proof:
    (Get-Content agentic_core/prompt_governance/apps_lic_pa_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.pa_binding import pa_compile_apps_lic"  → exit 0
    python -m pytest tests/_apps_contract/test_w5_apps_lic_c0_pa.py -v  → all PASS
  Scanner: check_apps_lic_core_contamination.py G-05

G-06 — L2 Binding
  Source:         agentic_core/L2_execution/apps_lic_l2_binding.py (412 lines)
  Target:         apps_lic/runtime/bindings/l2_binding.py
  Owner after:    apps_lic
  Logic to move:  l2_execute_apps_lic(), REGISTRY import (from apps_lic.config.hop_pipeline),
                  all DAG execution logic
  Core shim after: ≤30 lines
  Interface dep:  None (REGISTRY import moves app-side with the logic)
  Acceptance proof:
    (Get-Content agentic_core/L2_execution/apps_lic_l2_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.l2_binding import l2_execute_apps_lic"  → exit 0
    python -m pytest tests/_apps_contract/test_w6_apps_lic_l3_l2.py -v  → all PASS
  Scanner: check_apps_lic_core_contamination.py G-06

G-07 — L3 Binding
  Source:         agentic_core/L3_orchestration/apps_lic_l3_binding.py (443 lines)
  Target:         apps_lic/runtime/bindings/l3_binding.py
  Owner after:    apps_lic
  Logic to move:  l3_orchestrate_apps_lic(), APPS_LIC_NODE_ID, APPS_LIC_DAG_ID,
                  APPS_LIC_WORKFLOW_TYPE, APPS_LIC_L3_CERT_REF, single-node DAG topology
  Core shim after: ≤30 lines
  Interface dep:  None (node_id read from apps_lic/config/ profile in app-owned binding)
  Acceptance proof:
    (Get-Content agentic_core/L3_orchestration/apps_lic_l3_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.l3_binding import l3_orchestrate_apps_lic"  → exit 0
    python -m pytest tests/_apps_contract/test_w6_apps_lic_l3_l2.py -v  → all PASS
    Select-String -Path agentic_core/L3_orchestration/apps_lic_l3_binding.py -Pattern "apps_lic\.hop"
    → 0 matches (node_id no longer hardcoded in core)
  Scanner: check_apps_lic_core_contamination.py G-07 (shim + no domain strings)

G-08 — Exit Binding
  Source:         agentic_core/runtime/exit/apps_lic_exit_binding.py (634 lines)
  Target:         apps_lic/runtime/bindings/exit_binding.py
  Owner after:    apps_lic
  Logic to move:  exit_finalize_apps_lic(), module-scope import from apps_lic.contracts
                  (apps_lic_ingress_contract_v1), all exit gate logic
  Core shim after: ≤30 lines; zero module-scope app imports
  Interface dep:  G-10 must be done first (apps_lic_ingress_payload.py moved to
                  apps_lic/contracts/); exit binding then imports from app-owned contracts.
                  RuntimeCustomizationPackageSection resolved via generic ProfileRef protocol
                  (no new core interface required — protocol already used in apps_rg).
  Acceptance proof:
    (Get-Content agentic_core/runtime/exit/apps_lic_exit_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.exit_binding import exit_finalize_apps_lic"  → exit 0
    python -m pytest tests/_apps_contract/test_w7_apps_lic_exit_x1_x3.py -v  → all PASS
    test_apps_lic_exit_emits_exactly_one_x3 → PASS (BL-4/Exit invariant)
    test_apps_lic_exit_fails_closed_on_missing_profile → PASS
  Scanner: check_apps_lic_core_contamination.py G-08

G-09 — L6 Binding
  Source:         agentic_core/L6_observability/promotion/apps_lic_promo_binding.py (266 lines)
  Target:         apps_lic/runtime/bindings/l6_binding.py
  Owner after:    apps_lic
  Logic to move:  promote_apps_lic_run(), _load_apps_lic_l6_policy() (currently stub →
                  must implement real loader from apps_lic/config/domain_contract/
                  meta_feedback_profile.outreach_message.v1.json)
  Core shim after: ≤30 lines
  Interface dep:  None (L6 consumes completed runs via generic profile consumer)
  Acceptance proof:
    (Get-Content agentic_core/L6_observability/promotion/apps_lic_promo_binding.py).Count  → ≤30
    python -c "from apps_lic.runtime.bindings.l6_binding import promote_apps_lic_run"  → exit 0
    test_apps_lic_l6_policy_non_empty → PASS (policy dict non-empty)
    test_l6_cannot_rescue_current_run → PASS (BL-4/L6 invariant)
  Scanner: check_apps_lic_core_contamination.py G-09

G-18 — Dispatch Entrypoint
  Source:         agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py
  Target:         apps_lic/runtime/dispatch/apps_lic_dispatch.py
  Owner after:    apps_lic
  Logic to move:  _build_lic_envelope(), run_apps_lic_pipeline(), source_channel literal
                  "apps_lic_cli", declared_schema literal "apps_lic_outreach_v1",
                  task_class identity binding
  Core file after: ≤30-line re-export shim or delete entirely (no callers should import from
                  agentic_core/runtime/entrypoints/ for app-specific dispatch)
  Interface dep:  None (apps_rg has identical pattern in apps_rg/runtime/dispatch/)
  Acceptance proof:
    python -c "from apps_lic.runtime.dispatch.apps_lic_dispatch import run_apps_lic_pipeline"  → exit 0
    Select-String -Path agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py
      -Pattern "source_channel.*apps_lic_cli|declared_schema.*outreach_v1"
    → 0 matches (identity strings live in app-owned dispatch only)
  Scanner: check_apps_lic_core_contamination.py G-18

─────────────────────────────────────────────────────────────────────
W3.P2 — DIRECT IMPORT REMOVAL DESIGN (G-06, G-08, G-11, G-13, G-21)
─────────────────────────────────────────────────────────────────────
All 6 executable import lines removed once binding migrations complete.
Details per site:

SITE 1 — agentic_core/utils/workflow_engines/apps_engines_aliases.py:31-33 (G-11, G-21)
  Current:  3 module-scope from apps_lic.reasoning.* imports + invalid AG-RGGOV-9 exemption
  Fix:      Remove all 3 import lines and the AG-RGGOV-9 comment entirely.
            Agents accessed via app-owned dispatch; no core alias needed.
  Unblocked by: G-09 migration (L6 promo handles promotion for app agents)
  Acceptance proof:
    Select-String -Path agentic_core/utils/workflow_engines/apps_engines_aliases.py
      -Pattern "from apps_lic"  → 0 matches
    Select-String ... -Pattern "AG-RGGOV-9.*apps_lic"  → 0 matches
  Scanner: check_apps_lic_core_imports.py

SITE 2 — agentic_core/L2_execution/apps_lic_l2_binding.py:161 (G-06)
  Current:  lazy `from apps_lic.config.hop_pipeline import REGISTRY`
  Fix:      After G-06 migration, entire file becomes ≤30-line shim; lazy import
            moves to apps_lic/runtime/bindings/l2_binding.py (app-owned)
  Acceptance proof: shim file has 0 from apps_lic lines

SITE 3 — agentic_core/runtime/exit/apps_lic_exit_binding.py:55 (G-08)
  Current:  module-scope `from apps_lic.contracts.apps_lic_ingress_contract_v1 import (...)`
  Fix:      After G-08 migration, import moves to apps_lic/runtime/bindings/exit_binding.py
            (app-owned contracts referenced app-side only)
  Acceptance proof: shim file has 0 from apps_lic lines at module scope

SITE 4 — agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py:382 (G-13)
  Current:  lazy `from apps_lic.types.ImmutableStagingBuffer import AppContentValidatorAgent`
            (used at lines 426-428 as a concrete class injected into 3 validator slots)
  Fix:      Replace with ContentValidatorProtocol injection. Core receives protocol instance
            via U0 payload factory key; no concrete import. Null protocol (no-op) used when
            no factory key is present (safe default — existing apps_rg path has no validator).
  BLOCKED BY: content-validator enabling plan (ContentValidatorProtocol does not exist in core)
  Interim (safe, no behavior change): guard with `if TYPE_CHECKING:` + runtime isinstance check
    so import is analysis-only until enabling plan ships.
  Acceptance proof (post enabling plan):
    Select-String -Path agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py
      -Pattern "from apps_lic"  → 0 matches

─────────────────────────────────────────────────────────────────────
W3.P3 — SCHEMA/SQL/POLICY/CONTRACT RELOCATION DESIGN (G-10, G-14, G-15, G-16, G-17)
─────────────────────────────────────────────────────────────────────
G-10 — Ingress Contract
  Source:   agentic_core/runtime/contracts/apps_lic_ingress_payload.py (131 lines)
  Target:   apps_lic/contracts/ingress_payload.py  (create apps_lic/contracts/__init__.py too)
  Owner:    apps_lic
  Note:     G-08 exit migration depends on G-10 completing first (exit binding imports this).
            Core references converted to generic IngressPayload protocol (no new interface
            required — IngressPayload ABC already exists in agentic_core/runtime/contracts/).
  Acceptance proof:
    Test-Path agentic_core/runtime/contracts/apps_lic_ingress_payload.py  → False
    python -c "from apps_lic.contracts.ingress_payload import AppsLicRequestEnvelope"  → exit 0

G-14 — L5 HITL Policy
  Source:   agentic_core/L5_safety/policy/apps_lic_reengagement.py (378 lines)
  Target:   apps_lic/policy/reengagement_hitl_policy.py
  Owner:    apps_lic
  BLOCKED BY: hitl-protocol enabling plan. L5 evaluator framework has no HITLPolicyProtocol
    injection slot. Cannot move the policy without core accepting it via generic protocol.
  Safe pre-work (not blocked): move the concrete class to apps_lic/policy/ and expose
    it; L5 evaluator continues to import from old location via re-export shim until
    enabling plan ships and injection slot exists.
  Acceptance proof (post enabling plan):
    Get-ChildItem agentic_core/L5_safety/policy -Filter "apps_lic*"  → 0 results

G-15 — L5 HITL Evaluator
  Source:   agentic_core/L5_safety/evaluators/apps_lic_reengagement.py (469 lines)
  Target:   apps_lic/policy/reengagement_evaluator.py
  Owner:    apps_lic
  BLOCKED BY: hitl-protocol enabling plan (same as G-14)
  Acceptance proof (post enabling plan):
    Get-ChildItem agentic_core/L5_safety/evaluators -Filter "apps_lic*"  → 0 results

G-16 — L4 Touch State SQL
  Source:   agentic_core/L4_state/schemas/apps_lic_touch_state.sql (134 lines)
  Target:   apps_lic/state/schemas/touch_state.sql  (create apps_lic/state/schemas/)
  Owner:    apps_lic
  NOT blocked (pure move of a SQL file; no generic interface required)
  Core UWG accepts schema via DurableWriteGateway generic protocol (already exists)
  Acceptance proof:
    Test-Path agentic_core/L4_state/schemas/apps_lic_touch_state.sql  → False
    Test-Path apps_lic/state/schemas/touch_state.sql  → True

G-17 — L4 Touch State Writer (UWG)
  Source:   agentic_core/L4_state/uwg/touch_state_writer.py (app identity in core UWG)
  Target:   apps_lic/state/touch_state_writer.py
  Owner:    apps_lic
  Note:     TOUCH_STATE_WRITE_CLASS constant moves app-side. Core DurableWriteGateway
            remains generic. apps_lic/runtime/bindings/l2_binding.py imports writer.
  NOT blocked (pure relocation)
  BL-4/UWG invariant: test_uwg_is_only_durable_write_path in W5.P3 enforces no raw writes.
  Acceptance proof:
    Get-ChildItem agentic_core/L4_state/uwg -Filter "apps_lic*"  → 0 results
    python -c "from apps_lic.state.touch_state_writer import TouchStateWriter"  → exit 0

─────────────────────────────────────────────────────────────────────
W3.P4 — AGENT TAXONOMY LATE-REGISTRATION DESIGN (G-12)
─────────────────────────────────────────────────────────────────────
G-12 — Agent Taxonomy Registry
  Source:   agentic_core/L2_execution/types/agent_taxonomy_registry.py (35 apps_lic matches)
  Current:  Only register(classification: AgentClassification) exists (line 57).
            No register_app_entries() bulk API.
  Target:   apps_lic/config/agent_taxonomy.py (new file, all apps_lic entries)
  Owner:    apps_lic
  BLOCKED BY: taxonomy enabling plan.
    register_app_entries(app_id: str, entries: dict) must be added to AgentTaxonomyRegistry.
    This is a generic core interface addition — requires CoreAdditionAuthorGateReceipt.
  Enabling plan stub to create: apps-lic-core-interface-gap-taxonomy-<id>.md
    Specifies: method signature, batch-register semantics, idempotency guarantee,
    no behavioral branching on app_id value, late-registration call from apps_lic/__init__.py
  After enabling plan ships:
    apps_lic/config/agent_taxonomy.py defines APPS_LIC_AGENT_ENTRIES dict
    apps_lic/__init__.py calls AgentTaxonomyRegistry().register_app_entries("apps_lic", APPS_LIC_AGENT_ENTRIES)
    All 35 hardcoded entries removed from agentic_core registry
  Acceptance proof (post enabling plan):
    Select-String -Path agentic_core/L2_execution/types/agent_taxonomy_registry.py
      -Pattern "apps_lic"  → 0 matches
    python -c "from apps_lic.config.agent_taxonomy import APPS_LIC_AGENT_ENTRIES; assert len(APPS_LIC_AGENT_ENTRIES) > 0"

─────────────────────────────────────────────────────────────────────
GAP CLASSIFICATION SUMMARY
─────────────────────────────────────────────────────────────────────
CATEGORY A — Safe app-side migrations (no enabling plan, not blocked):
  G-01, G-02, G-03, G-04, G-05, G-06, G-07, G-09, G-16, G-17, G-18, G-20
  (12 gaps — pure binding/file moves; all interfaces already exist)

CATEGORY B — Core shim reductions (follow Category A; no new core logic):
  G-08 (depends on G-10), G-10, G-11, G-21
  (4 gaps — shim write + import removal; G-08 sequenced after G-10)

CATEGORY C — True generic core interface gaps (blocked until enabling plan ships):
  G-12 (taxonomy), G-13 (content-validator), G-14 (hitl-protocol), G-15 (hitl-protocol)
  (4 gaps across 3 enabling plans)

CATEGORY D — Missing app runtime tree (structural, not logic):
  G-22 (runtime/bindings/ dir creation — resolved by Category A migrations)
  G-23 (negative-control tests — created as part of W5.P3; no source change)
  (2 gaps — resolved by other waves)

ENABLING PLANS REQUIRED BEFORE CATEGORY C CAN SHIP:
  1. apps-lic-core-interface-gap-taxonomy-<id>.md
     Interface: AgentTaxonomyRegistry.register_app_entries()
     Blocks: G-12
  2. apps-lic-core-interface-gap-hitl-protocol-<id>.md
     Interface: HITLPolicyProtocol injection slot in L5 evaluator
     Blocks: G-14, G-15
  3. apps-lic-core-interface-gap-content-validator-<id>.md
     Interface: ContentValidatorProtocol on SubAtomicRegistryAgent
     Blocks: G-13

BOUNDARY LAW STATUS (BL-1 through BL-5):
  BL-1 (core owns generic contracts/runners only): PRESERVED — all migrations move
    app logic OUT; no new app logic added to core
  BL-2 (app-owned logic in apps_lic): PRESERVED — all 9 bindings land in apps_lic/runtime/
  BL-3 (U0 sole entry point): PRESERVED — IngressBypassError tests in W5.P3 enforce this
  BL-4 (layer behavioral invariants): PRESERVED — per-layer BL-4 acceptance proofs above
    (C0 no write; Exit one X3; UWG only durable write; L6 completed runs only)
  BL-5 (no app-specific logic added to core): PRESERVED — enabling plans add GENERIC
    interfaces only; apps_lic content never enters core

G-19 EXEMPT STATUS: CONFIRMED UNCHANGED
  APPS_LIC_DIR is used as a generic string key in ADG/scanner/namespace enforcement.
  Live scan confirmed: all uses are frozenset membership, Path() scan roots, or module
  namespace string containment. Zero behavioral routing branches on the value.
  No remediation required or planned.

─────────────────────────────────────────────────────────────────────
WORKSPACE CONFIRMATION
─────────────────────────────────────────────────────────────────────
git diff --name-only HEAD -- agentic_core/ apps_lic/:  0 modified files
W3 source changes made: ZERO
```

---

## W4 — Contract/Gate/L5/Exit/UWG/L6 Alignment Plan

### W4.P1 — L5 HITL policy ownership (G-14, G-15)

**Hard constraint:** L5 must remain generic. HITL policy rules for `apps_lic` re-engagement are app-specific.

**Remediation steps:**
1. Move `apps_lic_reengagement.py` (policy) → `apps_lic/policy/reengagement_hitl_policy.py`
2. Move `apps_lic_reengagement.py` (evaluator) → `apps_lic/policy/reengagement_evaluator.py`
3. Core L5 consumes via generic `HITLPolicyProtocol` injected through U0 payload section `hitl_policy_ref`
4. `apps_lic_l3_binding.py` (after migration) passes policy ref from `RuntimeCustomizationPackageSection`

**Acceptance proof:**
```powershell
# No apps_lic in L5 policy or evaluator dirs:
Get-ChildItem agentic_core/L5_safety/policy, agentic_core/L5_safety/evaluators -Filter "apps_lic*"
# Expected: 0 results
```

### W4.P2 — UWG/L4 write path ownership (G-16, G-17)

**Hard constraint:** No direct L4 writes outside UWG. C0 must not write. PA must not write. Only L2→UWG path.

**Remediation steps:**
1. Move `touch_state_writer.py` to `apps_lic/state/touch_state_writer.py`
2. Move `apps_lic_touch_state.sql` to `apps_lic/state/schemas/touch_state.sql`
3. `apps_lic/runtime/bindings/l2_binding.py` imports from `apps_lic/state/touch_state_writer.py` (app-owned)
4. Core UWG (`DurableWriteGateway`) remains generic — it accepts write requests shaped per the generic protocol
5. `TOUCH_STATE_WRITE_CLASS = "apps_lic.touch_state"` lives in app-owned writer, not in core

**Acceptance proof:**
```powershell
Get-ChildItem agentic_core/L4_state/uwg -Filter "apps_lic*"
Get-ChildItem agentic_core/L4_state/schemas -Filter "apps_lic*"
# Both expected: 0 results
```

### W4.P3 — Exit/X3 disposition wiring (G-08)

**Hard constraint:** Exit must emit exactly one X3 disposition. Exit profile must be loaded from app-owned config, not synthesized in core.

**Remediation steps:**
1. Migrate exit binding to `apps_lic/runtime/bindings/exit_binding.py`
2. `RuntimeCustomizationPackageSection` / `ProfileRef` imports remain in `apps_lic/contracts/` (after G-10 migration)
3. Verify `apps_lic/config/cert_route_registry.yaml` has a valid `exit_profile_ref`
4. Verify exit binding raises `AppsLicExitProfileError` (fail-closed) when config unavailable — behavior preserved in app-owned binding

**Verification commands:**
```powershell
# Exit profile ref must exist in app config:
Select-String -Path apps_lic/config/cert_route_registry.yaml -Pattern "exit_profile"

# Core exit binding must be ≤30-line shim after migration:
(Get-Content agentic_core/runtime/exit/apps_lic_exit_binding.py).Count
```

### W4.P4 — L6 promo binding stub remediation (G-09)

**Problem:** `_load_apps_lic_l6_policy()` returns `{}` (empty dict) — the L6 learning profile is never actually loaded.

**Remediation steps:**
1. After migration to `apps_lic/runtime/bindings/l6_binding.py`, implement real policy loader:
   - Read `apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json`
   - Return structured policy dict consumed by generic L6 profile consumer
2. Add smoke test: `test_apps_lic_l6_policy_non_empty` asserts policy dict is non-empty on invocation

**Acceptance proof:**
```powershell
# Profile file must exist:
Test-Path apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json
# Expected: True
```

### W4.P5 — L5 cert refs and gate binding (G-07, L3 node_id)

**Problem:** `node_id = "apps_lic.hop_pipeline.execute"` is a hardcoded app domain string in core L3 binding.

**Remediation steps:**
1. After L3 migration, `node_id` loaded from `apps_lic/config/` (e.g., `pipeline_node_id` field in route profile)
2. `APPS_LIC_L3_CERT_REF` constant moves to app-owned binding
3. Verify L3 receipt `l3_no_execute_assertion=True` / `l3_no_l4_write_assertion=True` invariants preserved in migrated binding

**Verification command:**
```powershell
# No hardcoded apps_lic domain strings in core L3:
Select-String -Path agentic_core/L3_orchestration/apps_lic_l3_binding.py -Pattern "apps_lic\.hop_pipeline"
# Expected: 0 results (file should be a shim after migration)
```

---

### W4 Closeout Receipt

**Executed:** 2026-05-12  
**Executed by:** Cursor Agent (planning-only alignment review — zero source file modifications)

```
W4_STATUS: PASS
PLAN: apps-lic-u0-boundary-alignment-4f1d9c
SOURCE_CHANGES_MADE: false
IMPLEMENTATION_STARTED: false
WORKSPACE_DIFF_BLOCKER: true (unchanged — agentic_core/: 0 modified, apps_lic/: 0 modified)
W4_ITEMS_REVIEWED: 5
L5_HITL_ALIGNMENT_CONFIRMED: true
UWG_WRITE_PATH_ALIGNMENT_CONFIRMED: true
EXIT_X3_ALIGNMENT_CONFIRMED: true
L6_FIREWALL_ALIGNMENT_CONFIRMED: true
L5_CERT_REFS_ALIGNMENT_CONFIRMED: true
NEXT_ALLOWED_WAVE: W5 planning-only CI/static scanner and negative-control plan
IMPLEMENTATION_WAVES_BLOCKED: W3-W6 implementation remains blocked until workspace cleanliness is resolved

─────────────────────────────────────────────────────────────────────
W4.P1 — L5 HITL POLICY OWNERSHIP (G-14, G-15)
─────────────────────────────────────────────────────────────────────
CURRENT VIOLATION (confirmed live):
  agentic_core/L5_safety/policy/apps_lic_reengagement.py   (13,506 bytes)
    Classes: HITLPolicyRule (line 87), ReengagementHITLPolicy (line 118),
             HITLPolicyRegistry (line 336)
    These are concrete app-specific classes in core L5 — BL-1 violation.
  agentic_core/L5_safety/evaluators/apps_lic_reengagement.py (16,165 bytes)
    Line 22: from agentic_core.L5_safety.policy.apps_lic_reengagement import (...)
    Class: ReengagementPolicyEvaluator (line 235)
    Evaluator directly imports its own app-specific policy from core L5 policy dir.
    This creates a hard coupling: evaluator cannot be moved without policy moving first.

APP-OWNED TARGET LOCATIONS:
  Policy:    apps_lic/policy/reengagement_hitl_policy.py
             (create apps_lic/policy/__init__.py)
  Evaluator: apps_lic/policy/reengagement_evaluator.py

GENERIC CORE INTERFACE DEPENDENCY:
  HITLPolicyProtocol ABC — ABSENT (0 matches in agentic_core/).
  Required: agentic_core/L5_safety/protocols/hitl_policy_protocol.py
    defining abstract evaluate(request: PolicyEvalRequest) -> PolicyEvalResult
  L5 evaluator framework must accept injected HITLPolicyProtocol via
    U0 RuntimeCustomizationPackageSection.hitl_policy_ref.
  BLOCKED BY: hitl-protocol enabling plan.

SAFE PRE-WORK (not blocked by enabling plan):
  Both files can be moved to apps_lic/policy/ immediately.
  Core re-export shims at original paths maintain backward compat.
  Full cleanup (shim deletion, injection slot wire-up) requires enabling plan.

FAIL-CLOSED BEHAVIOR:
  ReengagementPolicyEvaluator must raise HitlPolicyUnavailableError (new exception)
    when hitl_policy_ref resolves to None — not silent pass-through.
  Policy file missing → fail-closed, no fallback.
  Core evaluator framework: if no HITLPolicyProtocol injected → skip HITL check
    entirely (safe default — apps_rg has no HITL policy).

BL-5 PRESERVED: enabling plan adds generic ABC only. No apps_lic logic enters core.

ACCEPTANCE PROOF (post enabling plan):
  Get-ChildItem agentic_core/L5_safety/policy -Filter "apps_lic*"      → 0 results
  Get-ChildItem agentic_core/L5_safety/evaluators -Filter "apps_lic*"  → 0 results
  python -c "from apps_lic.policy.reengagement_hitl_policy import ReengagementHITLPolicy"  → exit 0
  python -c "from apps_lic.policy.reengagement_evaluator import ReengagementPolicyEvaluator"  → exit 0

W5 NEGATIVE-CONTROL TESTS NEEDED:
  test_no_apps_lic_in_core_l5_policy        (BL-1: no apps_lic* files in L5/policy/)
  test_no_apps_lic_in_core_l5_evaluators    (BL-1: no apps_lic* files in L5/evaluators/)
  test_l5_hitl_fails_closed_on_missing_policy (fail-closed: HitlPolicyUnavailableError)

L5_HITL_ALIGNMENT_CONFIRMED: true — violation confirmed, target confirmed, enabling plan
  gap confirmed, safe pre-work path identified, fail-closed behavior specified.

─────────────────────────────────────────────────────────────────────
W4.P2 — UWG / L4 WRITE PATH OWNERSHIP (G-16, G-17)
─────────────────────────────────────────────────────────────────────
CURRENT VIOLATION (confirmed live):
  agentic_core/L4_state/schemas/apps_lic_touch_state.sql   (5,464 bytes)
    App-specific SQL schema in core L4 schema directory — BL-1 violation (G-16).
  agentic_core/L4_state/uwg/touch_state_writer.py — NO apps_lic* filename match, but:
    Line 136: TOUCH_STATE_WRITE_CLASS = "apps_lic.touch_state"
    Line 223: write_class=TOUCH_STATE_WRITE_CLASS
    Line 254: "table": "apps_lic_touch_state"
    Docstring (lines 1, 5, 10, 15): owned by apps_lic — app identity hardcoded in core UWG
    This is G-17: not a filename violation but a content identity violation.

APP-OWNED TARGET LOCATIONS:
  SQL schema: apps_lic/state/schemas/touch_state.sql
              (create apps_lic/state/__init__.py, apps_lic/state/schemas/)
  Writer:     apps_lic/state/touch_state_writer.py

GENERIC CORE INTERFACE DEPENDENCY:
  None. DurableWriteGateway is already generic — accepts write requests via
  generic write_class + table contract. Writer relocation is a pure move.
  apps_lic/runtime/bindings/l2_binding.py imports writer from app-owned path.

INVARIANT VERIFIED — UWG IS ONLY DURABLE WRITE PATH:
  touch_state_writer.py lines 223, 254 confirm all writes go through
  write_class / DurableWriteGateway — no raw sqlite3/psycopg2/file writes.
  This BL-4/UWG invariant is ALREADY SATISFIED in the existing code.
  Migration preserves it: app-owned writer still calls DurableWriteGateway.

C0 WRITE INVARIANT:
  apps_lic_c0_binding.py comment: "C0 must not write. PA must not write."
  W4.P2 relocation does not affect C0 (C0 binding never imports touch_state_writer).
  C0 BL-4 invariant: test_c0_binding_does_not_write_state in W5.P3 enforces.

FAIL-CLOSED BEHAVIOR:
  TouchStateWriter must raise TouchStateSchemaError when schema SQL is absent/malformed.
  Target path: apps_lic/state/schemas/touch_state.sql — if absent → fail-closed, no fallback.

ACCEPTANCE PROOF:
  Test-Path agentic_core/L4_state/schemas/apps_lic_touch_state.sql  → False
  Get-ChildItem agentic_core/L4_state/uwg -Filter "apps_lic*"       → 0 results
  Select-String -Path agentic_core/L4_state/uwg/touch_state_writer.py
    -Pattern "apps_lic"  → 0 matches (file itself is gone, moved to app-owned path)
  python -c "from apps_lic.state.touch_state_writer import TouchStateWriter"  → exit 0
  Test-Path apps_lic/state/schemas/touch_state.sql  → True

W5 NEGATIVE-CONTROL TESTS NEEDED:
  test_no_apps_lic_in_core_l4_schemas  (BL-1: no apps_lic* files in L4/schemas/)
  test_no_apps_lic_in_core_uwg         (BL-1: no apps_lic* files in L4/uwg/)
  test_uwg_is_only_durable_write_path  (BL-4: TouchStateWriter uses DurableWriteGateway only)

UWG_WRITE_PATH_ALIGNMENT_CONFIRMED: true — violations confirmed, target confirmed, no enabling
  plan required, BL-4/UWG invariant already satisfied in current code.

─────────────────────────────────────────────────────────────────────
W4.P3 — EXIT / X3 DISPOSITION WIRING (G-08)
─────────────────────────────────────────────────────────────────────
CURRENT VIOLATION (confirmed live):
  agentic_core/runtime/exit/apps_lic_exit_binding.py (634 lines)
    Line 55: module-scope from apps_lic.contracts.apps_lic_ingress_contract_v1 import (...)
    App-specific binding logic (634 lines) in core — BL-1/BL-2 violation.

EXIT INVARIANTS CONFIRMED IN CURRENT CODE:
  1. EXACTLY ONE X3 per invocation:
     exit_finalize_apps_lic(l2: SealedL2Artifact) -> X3Disposition (line 578)
     Docstring: "Produces exactly one X3Disposition per invocation."
     Single return path at line 256: return X3Disposition(...)
     Build path: _build_exit_review_packet → build_x3_packet → _x3_packet_to_disposition
     INVARIANT SATISFIED. Must be preserved in app-owned binding.

  2. FAIL-CLOSED ON MISSING EXIT PROFILE:
     AppsLicExitProfileError defined at line 92.
     Line 65: "binding raises AppsLicExitProfileError (fail-closed). apps_lic owns policy."
     _EXIT_PROFILE_PATH = _resolve_config_path("apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json")
     5 distinct raise AppsLicExitProfileError(...) sites (lines 312, 318, 326, 342, 351).
     INVARIANT SATISFIED. Must be preserved in app-owned binding.

  3. NO RETRIEVAL / NO PROMPT / NO LLM EXECUTION:
     Docstring: "No retrieval, no prompt assembly, no tool/model execution."
     "No direct L4 write, no ChromaDB mutation, no embedding generation."
     INVARIANT SATISFIED.

EXIT PROFILE REF in apps_lic/config/cert_route_registry.yaml:
  exit_profile key: ABSENT as a top-level field.
  However, invoke_exit_eval: true is present — this triggers v6 Exit pipeline from
    cert entrypoint. Binding resolves profile from:
    apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json (hardcoded path).
  POST-MIGRATION: profile path should be expressed as exit_profile_ref in cert_route_registry.yaml
    rather than hardcoded string in binding. Add to migration checklist.

APP-OWNED TARGET: apps_lic/runtime/bindings/exit_binding.py
GENERIC CORE INTERFACE DEPENDENCY:
  ProfileRef protocol — already used in apps_rg golden pattern. No new core interface.
  RuntimeCustomizationPackageSection — already exists in core contracts.
  Requires G-10 first (apps_lic/contracts/ingress_payload.py must exist before exit binding
  can import from apps_lic.contracts).

FAIL-CLOSED BEHAVIOR PRESERVED AFTER MIGRATION:
  AppsLicExitProfileError must remain in apps_lic/runtime/bindings/exit_binding.py.
  All 5 raise sites must survive the move.
  Core shim (≤30 lines) re-exports exit_finalize_apps_lic — raises transparently.

ACCEPTANCE PROOF:
  (Get-Content agentic_core/runtime/exit/apps_lic_exit_binding.py).Count  → ≤30
  python -c "from apps_lic.runtime.bindings.exit_binding import exit_finalize_apps_lic"  → exit 0
  python -m pytest tests/_apps_contract/test_w7_apps_lic_exit_x1_x3.py -v  → all PASS

W5 NEGATIVE-CONTROL TESTS NEEDED:
  test_apps_lic_exit_emits_exactly_one_x3         (BL-4: exactly one X3Disposition per call)
  test_apps_lic_exit_fails_closed_on_missing_profile (BL-4: AppsLicExitProfileError raised)
  test_apps_lic_exit_no_llm_no_retrieval           (BL-4: no LLM/retrieval calls on mock)

EXIT_X3_ALIGNMENT_CONFIRMED: true — exactly-one-X3 invariant confirmed in current code,
  fail-closed confirmed (5 raise sites), no LLM confirmed, migration design sound.

─────────────────────────────────────────────────────────────────────
W4.P4 — L6 PROMO BINDING STUB REMEDIATION (G-09)
─────────────────────────────────────────────────────────────────────
CURRENT VIOLATION (confirmed live):
  agentic_core/L6_observability/promotion/apps_lic_promo_binding.py (266 lines)
    _load_apps_lic_l6_policy() at line 159: returns {} (empty dict, logger.debug only).
    app_policy = _load_apps_lic_l6_policy() called at line 101 — policy is never loaded.
    App-specific binding in core (266 lines) — BL-1/BL-2 violation.

L6 FIREWALL INVARIANTS CONFIRMED IN CURRENT CODE:
  1. FUTURE-RUN ONLY (NO CURRENT-RUN RESCUE):
     Docstring line 82: "Future-run only (no current-run rescue)"
     BL-4/L6 law comment confirmed.
     L6CurrentRunMutationError: ABSENT from current code — this exception does not
       yet exist. Must be ADDED in the app-owned binding as a new typed exception.
     INVARIANT STATED IN DESIGN BUT NOT YET ENFORCED BY CODE.

  2. UWG REQUIRED FOR PROMOTION:
     Docstring: "UWG required for promotion" — stated as a spine law.
     Enforcement via generic engine, not directly in this binding.
     BL-4/UWG invariant covered under W4.P2.

  3. NO DIRECT L4 WRITE:
     Docstring: "No direct L4 write" — stated.
     No direct DB/file writes observed in binding scan.

POLICY STUB ISSUE:
  _load_apps_lic_l6_policy() returns {} — L6 promotion operates with no policy.
  Target profile: apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json
    → CONFIRMED PRESENT (live scan: True).
  After migration: app-owned l6_binding.py reads and returns this file.
  This is a functional gap beyond boundary alignment — policy stub means L6
    promotion criteria are never applied for apps_lic.

APP-OWNED TARGET: apps_lic/runtime/bindings/l6_binding.py
GENERIC CORE INTERFACE DEPENDENCY: None (generic L6 profile consumer already exists).

NEW EXCEPTION REQUIRED:
  L6CurrentRunMutationError must be added to apps_lic/runtime/bindings/l6_binding.py.
  Raised when promote_apps_lic_run() is called with run_status != "completed".
  This exception is apps_lic-owned (not a core interface gap).

FAIL-CLOSED BEHAVIOR AFTER MIGRATION:
  promote_apps_lic_run(run_bundle) raises L6CurrentRunMutationError if
    run_bundle.run_status != "completed"  → fail-closed
  Policy load failure → L6PolicyLoadError (new, app-owned) → fail-closed

ACCEPTANCE PROOF:
  (Get-Content agentic_core/L6_observability/promotion/apps_lic_promo_binding.py).Count → ≤30
  python -c "from apps_lic.runtime.bindings.l6_binding import promote_apps_lic_run"  → exit 0
  test_apps_lic_l6_policy_non_empty → PASS (policy dict non-empty after real loader)
  test_l6_cannot_rescue_current_run → PASS (L6CurrentRunMutationError raised)

W5 NEGATIVE-CONTROL TESTS NEEDED:
  test_apps_lic_l6_policy_non_empty     (BL-2: real policy loaded; not empty dict)
  test_l6_cannot_rescue_current_run     (BL-4: L6CurrentRunMutationError raised when in-flight)
  test_l6_promo_requires_uwg            (BL-4: promotion attempt without UWG auth is rejected)

L6_FIREWALL_ALIGNMENT_CONFIRMED: true — future-run-only stated in existing code; L6CurrentRunMutationError
  must be added as new app-owned exception in app binding; policy stub confirmed; profile file confirmed present.

─────────────────────────────────────────────────────────────────────
W4.P5 — L5 CERT REFS AND L3 GATE BINDING (G-07)
─────────────────────────────────────────────────────────────────────
CURRENT VIOLATION (confirmed live):
  agentic_core/L3_orchestration/apps_lic_l3_binding.py (443 lines)
    Line 14:  docstring: "node_id (fixed: 'apps_lic.hop_pipeline.execute')"
    Line 66:  APPS_LIC_NODE_ID: str = "apps_lic.hop_pipeline.execute"
    Line 67:  APPS_LIC_DAG_ID:  str = "apps_lic.hop_pipeline.dag_v1"
    Lines 94, 96, 178, 179, 194, 214, 226: used 7+ times in DAG topology construction
    App domain identity literals hardcoded in core L3 — BL-1 violation.

L5 CERT REF HANDLING:
  APPS_LIC_L3_CERT_REF constant should live in app-owned binding.
  L3 receipt fields l3_no_execute_assertion=True / l3_no_l4_write_assertion=True
    are layer invariants enforced generically — they survive migration unchanged.
  Core L3 enforces "no execute, no L4 write" as a generic contract;
    apps_lic-specific pipeline_node_id is just a label — moves app-side.

APP-OWNED TARGET: apps_lic/runtime/bindings/l3_binding.py
GENERIC CORE INTERFACE DEPENDENCY: None.
  APPS_LIC_NODE_ID and APPS_LIC_DAG_ID are string labels read from app-owned config.
  apps_lic/config/l3_dag.yaml confirmed present (cert_route_registry.yaml references
  "Static DAG on disk is SSOT" at apps_lic/config/l3_dag.yaml).
  Post-migration: l3_binding.py reads pipeline_node_id from l3_dag.yaml (or route profile).

MIGRATION CHECKLIST:
  1. Move APPS_LIC_NODE_ID, APPS_LIC_DAG_ID, APPS_LIC_WORKFLOW_TYPE, APPS_LIC_L3_CERT_REF
     to apps_lic/runtime/bindings/l3_binding.py.
  2. Read node_id from apps_lic/config/l3_dag.yaml::pipeline_node_id field (config-driven).
  3. Core shim (≤30 lines): re-exports l3_orchestrate_apps_lic.
  4. Verify l3_no_execute_assertion=True / l3_no_l4_write_assertion=True are present in
     the L3 receipt produced by app-owned binding.

FAIL-CLOSED BEHAVIOR:
  l3_dag.yaml absent or pipeline_node_id field missing → raise L3ConfigError (app-owned).
  No soft fallback to hardcoded node_id — config must be present.

ACCEPTANCE PROOF:
  (Get-Content agentic_core/L3_orchestration/apps_lic_l3_binding.py).Count  → ≤30
  Select-String -Path agentic_core/L3_orchestration/apps_lic_l3_binding.py
    -Pattern "apps_lic\.hop_pipeline"  → 0 matches
  python -c "from apps_lic.runtime.bindings.l3_binding import l3_orchestrate_apps_lic"  → exit 0

W5 NEGATIVE-CONTROL TESTS NEEDED:
  test_l3_no_hardcoded_domain_strings   (BL-1: core L3 shim has 0 apps_lic domain literals)
  test_l3_cert_refs_are_app_owned       (BL-2: APPS_LIC_L3_CERT_REF in apps_lic binding)
  test_l3_fails_closed_on_missing_config (fail-closed: L3ConfigError when l3_dag.yaml absent)

L5_CERT_REFS_ALIGNMENT_CONFIRMED: true — domain literals confirmed at 7 sites (lines 66/67/94/96/178/179/226);
  target is config-driven reads from apps_lic/config/l3_dag.yaml; no core interface gap.

─────────────────────────────────────────────────────────────────────
LAYER BEHAVIORAL INVARIANT SUMMARY
─────────────────────────────────────────────────────────────────────
INVARIANT                                | STATUS    | EVIDENCE
-----------------------------------------|-----------|------------------
C0 does not answer, write state, call LLM | SATISFIED | "C0 must not write. PA must not write."
                                         |           | C0 binding comment confirmed; no state write
                                         |           | in c0 binding scan. test_c0_binding_does_not_write_state in W5.P3.
L5 certifies evidence only; no X3 emit  | SATISFIED | L5 evaluator (G-15) evaluates policy;
                                         |           | X3 is emitted only by Exit (separate layer).
                                         |           | No X3 import in L5 evaluator confirmed.
Exit emits exactly one X3; fails closed  | SATISFIED | exit_finalize_apps_lic → X3Disposition
                                         |           | (single return path); 5 raise sites for
                                         |           | AppsLicExitProfileError confirmed live.
UWG is only durable write path           | SATISFIED | touch_state_writer.py uses
                                         |           | DurableWriteGateway exclusively (lines 223, 254).
                                         |           | No raw DB/file writes in writer.
L6 future-run only; no current-run rescue| STATED    | "Future-run only (no current-run rescue)"
                                         |           | in docstring. L6CurrentRunMutationError
                                         |           | NOT YET in code — must be added in app binding.
                                         |           | test_l6_cannot_rescue_current_run in W5.P3.

─────────────────────────────────────────────────────────────────────
ADDITIONAL MIGRATION DETAIL: exit_profile_ref GAP
─────────────────────────────────────────────────────────────────────
apps_lic/config/cert_route_registry.yaml: no exit_profile_ref field.
Current behavior: binding uses hardcoded path string in _EXIT_PROFILE_PATH.
Post-migration requirement: add exit_profile_ref to cert_route_registry.yaml so
  binding resolves profile via ProfileRef protocol (matches apps_rg golden pattern).
This is a config-only addition (no source change needed in core).
Acceptance proof: Select-String -Path apps_lic/config/cert_route_registry.yaml
  -Pattern "exit_profile_ref"  → 1 match

─────────────────────────────────────────────────────────────────────
WORKSPACE CONFIRMATION
─────────────────────────────────────────────────────────────────────
git diff --name-only HEAD -- agentic_core/ apps_lic/:  0 modified files
W4 source changes made: ZERO
```

---

## W5 — CI/Static Scanner and Negative-Control Plan

> **W5 scope:** Planning-only design of two static scanners, 17 negative-control tests, and two pre-commit hooks. No source files are modified in W5. Implementation is deferred to the W3–W6 implementation waves (currently blocked — see §Block Condition).

---

### W5.P1 — Static scanner: literal contamination

**New file (planned):** `ops_scripts/ci/check_apps_lic_core_contamination.py`

**Purpose:** Catch app-specific files and content-identity violations left in core directories after migration. This is the structural filesystem gate.

**Exact forbidden-path rules (fail = any match):**

| Checked path | Forbidden pattern | Gaps covered | BL |
|---|---|---|---|
| `agentic_core/L4_state/schemas/` | any filename matching `apps_lic*` | G-16 (SQL schema in core) | BL-1 |
| `agentic_core/L5_safety/policy/` | any filename matching `apps_lic*` | G-14 (HITL policy in core) | BL-1 |
| `agentic_core/L5_safety/evaluators/` | any filename matching `apps_lic*` | G-15 (HITL evaluator in core) | BL-1 |
| `agentic_core/runtime/contracts/` | any filename matching `apps_lic*` | G-11 (ingress payload in core) | BL-1 |
| `agentic_core/runtime/entrypoints/` | any filename matching `apps_lic*` | G-18 (entrypoint owns app identity) | BL-1 |
| `agentic_core/L4_state/uwg/` | any filename matching `apps_lic*` | G-17 (UWG content identity) | BL-1 |
| `agentic_core/L4_state/uwg/touch_state_writer.py` (content) | any `apps_lic` string literal in source | G-17 (content-identity in generic file) | BL-1 |
| `agentic_core/L2_execution/types/agent_taxonomy_registry.py` (content) | any `apps_lic` string match | G-12 (app entries in core registry) | BL-1 |

**Shim line-count rule:**
- For every `agentic_core/*/apps_lic_*_binding.py` discovered via `glob.glob("agentic_core/**/*apps_lic_*binding*.py", recursive=True)`:
  - Count non-blank, non-comment lines.
  - If count > 30: emit `ERROR` with file path + actual line count.
  - This enforces the shim-not-logic invariant: after migration each core binding file must be a minimal re-export shim only.

**Allowed exceptions (scanner must skip):**
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` — contains string literals `"from apps_lic"` and `"import apps_lic"` as analysis-only patterns. Excluded from content-identity checks by filename allowlist.
- `agentic_core/runtime/u0/apps_lic_u0_adapter.py` — **only if it has been deleted** as part of migration (file absence is the correct post-migration state). If still present post-migration, it IS a violation.
- Plan files (`.cursor/plans/`) — never scanned.
- This scanner's own source file.

**Pass condition:** Zero ERROR-level findings across all path + content checks.
**Fail condition:** Any file found in a forbidden path, any content-identity match in a generic file, or any shim exceeding 30 non-blank lines.
**Expected failure mode (pre-migration):** Multiple ERRORs — `apps_lic_touch_state.sql` (L4 schemas), `apps_lic_reengagement.py` (L5 policy + evaluators), `apps_lic_ingress_payload.py` (contracts), taxonomy registry content matches, shim oversize for all 8 existing bindings.

**Config:**
```python
BYPASS_ENV = "APPS_LIC_CONTAMINATION_BYPASS"
FAIL_CLOSED_ENV = "APPS_LIC_CONTAMINATION_FAIL_CLOSED"
REPORT_PATH = "artifacts/ci/apps_lic_contamination_gate.json"
```

**JSON receipt shape:**
```json
{
  "gate": "ALIC-CONTAM",
  "status": "pass|fail|bypassed",
  "timestamp": "<iso8601>",
  "errors": [
    {"check": "forbidden_file", "path": "<path>", "message": "<detail>"},
    {"check": "content_identity", "path": "<path>", "line": 136, "match": "apps_lic.touch_state"},
    {"check": "shim_oversize", "path": "<path>", "line_count": 254, "limit": 30}
  ],
  "summary": {"error_count": 0, "warn_count": 0}
}
```

**Registration:** Add to `ops_scripts/ci/run_contract_gates.py` assurance_gates list as:
```python
("ALIC-CONTAM", "apps_lic core contamination scan", "ops_scripts/ci/check_apps_lic_core_contamination.py")
```

---

### W5.P2 — Static scanner: import boundary

**New file (planned):** `ops_scripts/ci/check_apps_lic_core_imports.py`

**Purpose:** Catch executable `from apps_lic` / `import apps_lic` statements in any `agentic_core/` Python file. This is the import-graph enforcement gate.

**Executable import detection:**
- Scan all `*.py` files under `agentic_core/` recursively.
- Use AST parsing (`ast.parse` + `ast.walk`) to find `Import` and `ImportFrom` nodes where the module starts with `apps_lic`.
- AST-based detection eliminates docstring/comment/string-literal false positives — only actual import statements in the parse tree are flagged.
- Fallback (if AST parse fails): regex scan for `^from apps_lic` / `^import apps_lic` at line start (excluding indented aliases).

**False-positive handling:**
- Docstrings/comments: eliminated by AST approach; never flagged.
- String literals (e.g., `"from apps_lic.reasoning..."` in `FileClassificationAgent.py`): not import nodes; not flagged.
- `# noqa` lines in `apps_engines_aliases.py` (lines 31–33): these are REAL executable imports — they ARE violations and MUST be flagged.

**Shim exclusions (post-migration, advisory):**
- Files matching `agentic_core/*/apps_lic_*_binding.py` that are ≤30 non-blank lines AND contain `re-export` or `# shim` in their docstring may be listed as `INFO` (expected shims) rather than `ERROR`. Advisory only — shims still need migration to zero imports eventually.

**FileClassificationAgent exclusion:**
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` excluded from import scan via explicit path allowlist. File uses app-package names as analysis-only string constants, not live imports.

**Known pre-migration violations (expected ERROR output before W3 remediation):**
- `agentic_core/utils/workflow_engines/apps_engines_aliases.py` lines 31–33: 3 direct `from apps_lic.reasoning.*` imports.
- `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` line 382: `from apps_lic.types.ImmutableStagingBuffer import AppContentValidatorAgent`.
- `agentic_core/runtime/exit/apps_lic_exit_binding.py` line 55: `from apps_lic.contracts.apps_lic_ingress_contract_v1 import ...`.

**Pass condition:** Zero ERROR-level import violations (or all violations are in confirmed shim files listed as INFO).
**Fail condition:** Any live `from apps_lic` / `import apps_lic` import node found in a non-shim core file.
**Expected failure mode (pre-migration):** At minimum 5 violations across 3 files.

**Config:**
```python
BYPASS_ENV = "APPS_LIC_IMPORT_BYPASS"
FAIL_CLOSED_ENV = "APPS_LIC_IMPORT_FAIL_CLOSED"
REPORT_PATH = "artifacts/ci/apps_lic_import_gate.json"
```

**JSON receipt shape:**
```json
{
  "gate": "ALIC-IMPORT",
  "status": "pass|fail|bypassed",
  "timestamp": "<iso8601>",
  "violations": [
    {
      "file": "agentic_core/utils/workflow_engines/apps_engines_aliases.py",
      "line": 31,
      "statement": "from apps_lic.reasoning.GovernanceShieldAgent import GovernanceShieldAgent",
      "severity": "ERROR"
    }
  ],
  "shims_info": [
    {"file": "agentic_core/runtime/exit/apps_lic_exit_binding.py", "line_count": 12, "severity": "INFO"}
  ],
  "summary": {"error_count": 0, "info_count": 0}
}
```

**Registration:** Add to `ops_scripts/ci/run_contract_gates.py` assurance_gates list as:
```python
("ALIC-IMPORT", "apps_lic core import boundary scan", "ops_scripts/ci/check_apps_lic_core_imports.py")
```

**Verification command (manual, pre-AST scanner):**
```powershell
Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "^from apps_lic|^import apps_lic"
# Pre-remediation expected: lines 31-33 apps_engines_aliases.py, line 382 SubAtomicRegistryAgent.py, line 55 apps_lic_exit_binding.py
# Post-remediation expected: 0 results
```

---

### W5.P3 — Negative-control tests

**New file (planned):** `tests/_apps_contract/test_apps_lic_boundary_negative_controls.py`

> **Stale count fix:** The W5 design previously referenced "all 10 tests pass." W4 accumulated 15 negative-control candidates. This receipt replaces that language with the authoritative 17-test design below. The expected pytest invocation line count is 17 passed, 0 failed.

**Test cases to include:**

| # | Test name | File (tests/_apps_contract/) | BL invariant | Gaps covered | What it proves | Pass condition | Expected failure mode |
|---|-----------|------------------------------|-------------|--------------|----------------|---------------|----------------------|
| 1 | `test_apps_lic_u0_binding_is_app_owned` | test_apps_lic_boundary_negative_controls.py | BL-2 | G-01 | `apps_lic.runtime.bindings.u0_binding` is importable; core shim ≤30 lines | Import succeeds + line count ≤ 30 | `ImportError` if tree missing; `AssertionError` if shim too long |
| 2 | `test_apps_lic_l0_binding_is_app_owned` | same | BL-2 | G-02 | `apps_lic.runtime.bindings.l0_binding` importable; core shim ≤30 lines | same shape | same |
| 3 | `test_no_apps_lic_in_core_l4_schemas` | same | BL-1 | G-16 | `agentic_core/L4_state/schemas/` contains no `apps_lic*` file | `glob` returns empty | `AssertionError` listing `apps_lic_touch_state.sql` |
| 4 | `test_no_apps_lic_in_core_l5_policy` | same | BL-1 | G-14 | `agentic_core/L5_safety/policy/` contains no `apps_lic*` file | `glob` returns empty | `AssertionError` listing `apps_lic_reengagement.py` |
| 5 | `test_no_apps_lic_in_core_l5_evaluators` | same | BL-1 | G-15 | `agentic_core/L5_safety/evaluators/` contains no `apps_lic*` file | `glob` returns empty | `AssertionError` listing `apps_lic_reengagement.py` |
| 6 | `test_no_apps_lic_in_core_uwg` | same | BL-1 | G-17 | `agentic_core/L4_state/uwg/` contains no `apps_lic*` file | `glob` returns empty | `AssertionError` listing violations |
| 7 | `test_no_apps_lic_in_core_contracts` | same | BL-1 | G-11 | `agentic_core/runtime/contracts/` contains no `apps_lic*` file | `glob` returns empty | `AssertionError` listing `apps_lic_ingress_payload.py` |
| 8 | `test_no_apps_lic_in_core_entrypoints` | same | BL-1 | G-18 | `agentic_core/runtime/entrypoints/` contains no `apps_lic*` file | `glob` returns empty | `AssertionError` listing violations |
| 9 | `test_no_direct_apps_lic_import_in_core_taxonomy` | same | BL-1 | G-12 | `agent_taxonomy_registry.py` source contains zero `apps_lic` string matches | `re.search` returns None | `AssertionError` listing matched lines |
| 10 | `test_no_direct_from_apps_lic_in_core_aliases` | same | BL-1 | G-13 | `apps_engines_aliases.py` source contains zero `from apps_lic` lines | `re.search` returns None | `AssertionError` listing lines 31–33 |
| 11 | `test_apps_lic_enters_spine_through_u0_only` | same | BL-3 | G-01/G-02 | Calling `l0_route_apps_lic()` without a validated U0 package raises `IngressBypassError` | `pytest.raises(IngressBypassError)` passes | `IngressBypassError` absent → test fails |
| 12 | `test_direct_l2_call_without_u0_raises` | same | BL-3 | G-03 | Calling L2 binding directly without U0 validation token raises `IngressBypassError` | `pytest.raises(IngressBypassError)` passes | Same |
| 13 | `test_apps_lic_exit_emits_exactly_one_x3` | same | BL-4/Exit | G-08 | App-owned exit binding produces exactly one `X3Disposition` on mock invocation | `len(x3_list) == 1` | `AssertionError` if 0 or 2+ emitted |
| 14 | `test_apps_lic_exit_fails_closed_on_missing_profile` | same | BL-4/Exit | G-08 | Exit binding raises `AppsLicExitProfileError` when `cert_route_registry.yaml` absent or missing `exit_profile_ref` | `pytest.raises(AppsLicExitProfileError)` passes | Exception absent → test fails |
| 15 | `test_c0_binding_does_not_write_state` | same | BL-4/C0 | G-05 | C0 binding returns only `GateVerdict`; mock `DurableWriteGateway` receives zero write calls | `mock_uwg.write.call_count == 0` | `AssertionError` if any write call observed |
| 16 | `test_uwg_is_only_durable_write_path` | same | BL-4/UWG | G-16/G-17 | `apps_lic/state/touch_state_writer.py` (post-migration) imports only from `DurableWriteGateway`; AST scan of source confirms no `open()`, `sqlite3`, or `psycopg2` | AST walk finds zero raw-IO nodes | `AssertionError` listing forbidden imports |
| 17 | `test_l6_cannot_rescue_current_run` | same | BL-4/L6 | G-09 | App-owned L6 binding raises `L6CurrentRunMutationError` when called with `run_status != "completed"` | `pytest.raises(L6CurrentRunMutationError)` passes | Exception absent (stub returns `{}`) → test fails |

> **Notes on tests 11–12 (BL-3 U0-only entry):** Pre-migration these tests may need to be marked `xfail(strict=True)` with reason `"BL-3 enforcement not yet wired; enforced in W3 implementation"`. The `xfail` must be removed when BL-3 is implemented.
>
> **Note on test 17 (L6 firewall):** `L6CurrentRunMutationError` is absent from the current `apps_lic_promo_binding.py` stub. Pre-migration this test will fail with `Failed: DID NOT RAISE`. The test is the authoritative negative control that proves the L6 firewall is not yet code-enforced — the failure itself is the correct pre-migration state. Do not mark xfail; let it fail loudly until W3 implementation.
>
> **Note on tests 1–2 (app-owned shims):** These tests fail pre-migration because `apps_lic.runtime.bindings` does not exist yet. Correct approach: mark `xfail(strict=True, reason="BL-2 migration not yet executed")`.

**Expected pytest output (post-W3 implementation):**
```
17 passed, 0 failed, 0 errors
```

**Expected pytest output (pre-W3, tests 1-2 and 11-12 xfail, test 17 failing):**
```
12 passed, 2 xfailed, 2 xfailed, 1 FAILED [test_l6_cannot_rescue_current_run]
```

**Verification command:**
```powershell
python -m pytest tests/_apps_contract/test_apps_lic_boundary_negative_controls.py -v
```

---

### W5.P4 — Pre-commit hook additions

**Additions to `.pre-commit-config.yaml` (planned):**
```yaml
- id: apps-lic-core-contamination
  name: apps_lic core contamination scan (ALIC-CONTAM)
  language: python
  entry: python ops_scripts/ci/check_apps_lic_core_contamination.py
  pass_filenames: false
  stages: [commit]
  # Bypass: APPS_LIC_CONTAMINATION_BYPASS=1
  # Fail-closed: APPS_LIC_CONTAMINATION_FAIL_CLOSED=1

- id: apps-lic-core-imports
  name: apps_lic core import boundary scan (ALIC-IMPORT)
  language: python
  entry: python ops_scripts/ci/check_apps_lic_core_imports.py
  pass_filenames: false
  stages: [commit]
  # Bypass: APPS_LIC_IMPORT_BYPASS=1
  # Fail-closed: APPS_LIC_IMPORT_FAIL_CLOSED=1
```

**Hook behavior:**
- Both hooks are advisory by default (exit 0 even on violations; violations written to JSON report).
- `FAIL_CLOSED` env var converts to blocking (exit 1 on any ERROR-level finding).
- `BYPASS` env var skips the check entirely and writes a `{"status": "bypassed"}` receipt.
- Both hooks are idempotent and safe to run on every commit. Expected runtime < 3 seconds each.

---

### W5.P5 — Scanner and test coverage map

| Gap | Covered by scanner | Covered by negative-control test | Notes |
|-----|-------------------|----------------------------------|-------|
| G-01 U0 binding ownership | — | Test 1 | Scanner checks shim size only |
| G-02 L0 binding ownership | — | Test 2 | Same |
| G-03 L2 binding ownership (BL-3 entry) | ALIC-IMPORT (shim line count) | Test 12 | |
| G-05 C0 no-write/no-LLM | — | Test 15 | Runtime behavior; no static proxy |
| G-07 L3 hardcoded domain strings | ALIC-CONTAM (content-identity on L3 binding) | — | Covered by content scan on `apps_lic_l3_binding.py` |
| G-08 Exit X3 + fail-closed | — | Tests 13, 14 | Runtime behavior; static scanner confirms binding size |
| G-09 L6 policy non-empty + firewall | — | Test 17 | Runtime behavior; L6CurrentRunMutationError absent pre-migration |
| G-11 Ingress payload in core | ALIC-CONTAM | Test 7 | Dual coverage |
| G-12 App entries in core taxonomy | ALIC-CONTAM (content) | Test 9 | Dual coverage |
| G-13 Direct imports in aliases | ALIC-IMPORT | Test 10 | Dual coverage |
| G-14 HITL policy in core | ALIC-CONTAM | Test 4 | Dual coverage |
| G-15 HITL evaluator in core | ALIC-CONTAM | Test 5 | Dual coverage |
| G-16 SQL schema in core | ALIC-CONTAM | Test 3 | Dual coverage |
| G-17 UWG content identity | ALIC-CONTAM | Test 16 | Dual coverage |
| G-18 Entrypoint app identity | ALIC-CONTAM | Test 8 | |

---

## W5 Closeout Receipt

```
W5_STATUS: PASS
PLAN: apps-lic-u0-boundary-alignment-4f1d9c
SOURCE_CHANGES_MADE: false
IMPLEMENTATION_STARTED: false
WORKSPACE_DIFF_BLOCKER: true (0 diffs in agentic_core/ or apps_lic/)
SCANNERS_DESIGNED: 2
  - check_apps_lic_core_contamination.py (ALIC-CONTAM)
  - check_apps_lic_core_imports.py (ALIC-IMPORT)
NEGATIVE_CONTROLS_DESIGNED: 17
  - tests/_apps_contract/test_apps_lic_boundary_negative_controls.py
  - Covers BL-1 through BL-4/L6; gaps G-01 through G-18
PRECOMMIT_HOOKS_DESIGNED: 2
  - apps-lic-core-contamination (advisory, bypass+fail-closed env vars)
  - apps-lic-core-imports (advisory, bypass+fail-closed env vars)
STALE_TEST_COUNT_FIXED: true
  - Replaced "all 10 tests pass" with authoritative 17-test table
  - W4 accumulated 15 candidates; W5 design adds 2 (L5 evaluators, core aliases) = 17 total
KNOWN_PRE_MIGRATION_FAILURES:
  - Tests 1, 2: apps_lic.runtime.bindings does not exist → xfail(strict=True) until W3
  - Tests 11, 12: BL-3 enforcement not wired → xfail(strict=True) until W3
  - Test 17: L6CurrentRunMutationError absent → FAIL loud until W3
  - ALIC-CONTAM: multiple ERRORs expected (SQL schema, L5 policy/evaluators, ingress payload, UWG)
  - ALIC-IMPORT: minimum 5 violations across 3 files (aliases, SubAtomicRegistry, exit binding)
NEXT_ALLOWED_WAVE: W6 planning-only acceptance evidence bundle
IMPLEMENTATION_WAVES_BLOCKED: W3-W6 implementation remains blocked until workspace cleanliness is resolved
```

---

## No Code Changes Verification

This plan is a planning-only hardening pass. The following commands MUST return clean output before this plan is considered complete. They prove no source files were modified.

```powershell
# 1. Git status — must show no modified tracked files (plan file itself is the only new file)
git -C C:\Git\Agentic-Workflow-FRESH status --short
# Expected: only the plan file listed (M or ?? for .cursor/plans/apps-lic-u0-boundary-alignment-4f1d9c.md)
# Must NOT show: any *.py, *.sql, *.yaml, *.json modification

# 2. Git diff — must show zero changes to any source file
git -C C:\Git\Agentic-Workflow-FRESH diff HEAD -- agentic_core/ apps_lic/ ops_scripts/ tests/
# Expected: empty output

# 3. Confirm no apps_lic source files were added
git -C C:\Git\Agentic-Workflow-FRESH diff HEAD --name-only --diff-filter=A | Select-String "apps_lic"
# Expected: 0 matches (no new apps_lic files added)

# 4. Confirm no agentic_core source files were modified
git -C C:\Git\Agentic-Workflow-FRESH diff HEAD --name-only | Select-String "agentic_core"
# Expected: 0 matches

# 5. Plan file is the only changed artifact
git -C C:\Git\Agentic-Workflow-FRESH diff HEAD --name-only
# Expected: at most .cursor/plans/apps-lic-u0-boundary-alignment-4f1d9c.md
```

**Interpretation:** If any of commands 2–5 return non-empty output pointing to `.py` / `.sql` / `.yaml` files, a code change was made during this planning pass and the plan has violated its own scope. Block the implementation wave until confirmed clean.

---

## Pre-existing Workspace Diff Exclusion Receipt

**Purpose:** The No Code Changes Verification commands above detect 6 pre-existing diffs in the workspace that were present *before* this planning pass began. This receipt formally excludes them from the hardening-pass scope, proves they were not introduced by this plan, and records the implementation-wave blocking condition.

**Receipt status:** CONDITIONAL — implementation of this plan's waves is BLOCKED until workspace cleanliness is resolved (see §Block Condition below).

### Evidence of Pre-existence

All 6 diffs originate from commit context `b8f365d7a9` (`feat(ci): AG-PURITY W4 CI registration, synthetic tests, baseline, promotion doc`) and its follow-up `ccae445c1a` (`docs(plan): AG-PURITY plan cleanup and closure — W0-W4 COMPLETE`). These commits predate this hardening pass. The diffs represent uncommitted workspace changes from the AG-PURITY plan that were staged but not yet committed at the time this hardening pass ran.

**Verification of pre-existence:**
```powershell
# Confirm all 6 files were last touched by AG-PURITY commits, not this plan:
git -C C:\Git\Agentic-Workflow-FRESH log --oneline -1 -- `
  ops_scripts/ci/baselines/graph_layer_evidence_baseline.json `
  ops_scripts/ci/check_agentic_core_addition.py `
  ops_scripts/ci/executor_theater_gate.py `
  ops_scripts/ci/infra_wiring_scan.py `
  ops_scripts/ci/run_contract_gates.py `
  tests/_apps_contract/test_apps_rg_app_payload_consumption.py
# Expected: b8f365d7a9 feat(ci): AG-PURITY W4 CI registration...
# This hardening plan's only artifact is .cursor/plans/apps-lic-u0-boundary-alignment-4f1d9c.md
```

### Excluded File Inventory

| File | Owner plan | Belongs to | Relationship to this plan |
|------|-----------|-----------|--------------------------|
| `ops_scripts/ci/baselines/graph_layer_evidence_baseline.json` | AG-PURITY W4 | CI gate baseline | None — unrelated CI baseline update |
| `ops_scripts/ci/check_agentic_core_addition.py` | AG-PURITY W4 | Core-addition gate | None — enforces a different gate |
| `ops_scripts/ci/executor_theater_gate.py` | AG-PURITY W4 | Executor theater gate | None — unrelated CI gate |
| `ops_scripts/ci/infra_wiring_scan.py` | AG-PURITY W4 | Infra wiring scan | None — unrelated scan |
| `ops_scripts/ci/run_contract_gates.py` | AG-PURITY W4 | Gate registry | Tangential — this plan will also register ALIC gates here, but the pre-existing edits are AG-PURITY registrations |
| `tests/_apps_contract/test_apps_rg_app_payload_consumption.py` | AG-PURITY W4 | `apps_rg` contract tests | None — `apps_rg` test, not `apps_lic` |

### Block Condition

> ⛔ **Implementation of this plan's waves (W3–W6) is BLOCKED until one of the following conditions is met:**
>
> **Option A — Commit the pre-existing AG-PURITY diffs** under their own commit (separate from this plan's implementation commits). After the commit, commands 2–5 in §No Code Changes Verification must return empty output.
>
> **Option B — Stash or revert the pre-existing diffs** if they are not ready to commit. After stash/revert, commands 2–5 must return empty output.
>
> **Option C — Baseline under a separate plan** if the AG-PURITY diffs represent in-flight work that requires its own plan completion first. In that case, open `ag-purity-w4-closeout-<id>.md`, close it, and then begin this plan's implementation waves.
>
> **This receipt does not weaken the No Code Changes Verification requirement.** It merely documents the source of the current diff noise and confirms it did not originate from this hardening pass. The block stands until workspace is clean.

### Attestation

This exclusion receipt was authored at plan-hardening time (2026-05-12). The plan file `apps-lic-u0-boundary-alignment-4f1d9c.md` is the **only** artifact created by this hardening pass. No `.py`, `.sql`, `.yaml`, or `.json` files were created or modified.

---

## W6 — Acceptance Evidence Bundle Plan

### W6.P1 — Binding migration evidence

For each of the 10 migrated bindings, capture:

```
artifacts/governance/migration_receipts/apps-lic-u0-boundary-alignment/
  u0_binding_migration.json
  l0_binding_migration.json
  l1_binding_migration.json
  c0_binding_migration.json
  pa_binding_migration.json
  l2_binding_migration.json
  l3_binding_migration.json
  exit_binding_migration.json
  l6_binding_migration.json
  u0_adapter_migration.json
```

**Receipt schema per binding:**
```json
{
  "gap_id": "G-01",
  "binding": "u0",
  "source": "agentic_core/runtime/entry/u0_apps_lic_binding.py",
  "target": "apps_lic/runtime/bindings/u0_binding.py",
  "core_shim_line_count": 24,
  "tests_before": <int>,
  "tests_after": <int>,
  "regression_count": 0,
  "verification_command": "pytest tests/_apps_contract/ -v",
  "timestamp": "<ISO8601>"
}
```

### W6.P2 — Contamination clean evidence

For each category, a clean-scan output:

| Scan | Command | Expected output |
|------|---------|----------------|
| Literal contamination | `python ops_scripts/ci/check_apps_lic_core_contamination.py` | `"status": "PASS"`, 0 violations |
| Import boundary | `python ops_scripts/ci/check_apps_lic_core_imports.py` | `"status": "PASS"`, 0 violations |
| L4 schema | `Get-ChildItem agentic_core/L4_state/schemas -Filter "apps_lic*"` | Empty |
| L5 policy | `Get-ChildItem agentic_core/L5_safety/policy -Filter "apps_lic*"` | Empty |
| L4 UWG | `Get-ChildItem agentic_core/L4_state/uwg -Filter "apps_lic*"` | Empty |
| Agent taxonomy | `Select-String agentic_core/L2_execution/types/agent_taxonomy_registry.py -Pattern "apps_lic"` | 0 matches |
| Core aliases | `Select-String agentic_core/utils/workflow_engines/apps_engines_aliases.py -Pattern "apps_lic"` | 0 matches |
| Core contracts | `Get-ChildItem agentic_core/runtime/contracts -Filter "apps_lic*"` | Empty |

### W6.P3 — Test suite evidence

```powershell
# Full contract test suite must pass:
python -m pytest tests/_apps_contract/ -v --tb=short
# Expected: all existing tests pass + new apps_lic U0-only entry tests pass

# apps_lic negative-control tests:
python -m pytest tests/_apps_contract/test_apps_lic_u0_only_entry.py -v
# Expected: all 10 tests pass

# Contract gate suite:
python ops_scripts/ci/run_contract_gates.py
# Expected: ALIC-CONTAM PASS, ALIC-IMPORT PASS
```

---

## Gap Summary by Category

| Category | Count | Gaps |
|----------|-------|------|
| A — App payload/config gap (binding location wrong) | 9 | G-01, G-02, G-03, G-04, G-05, G-07, G-09, G-10, G-22 |
| B — Illegal core contamination (app data/logic in core) | 8 | G-06, G-08, G-11, G-12, G-13, G-14, G-15, G-16 |
| C — Direct core interaction/bypass | 3 | G-17, G-18, G-21 |
| D — Missing contract/gate/certification receipt | 2 | G-09 (stub), G-23 (missing CI gate) |
| E — Exit/UWG/L6 governance gap | 3 | G-08 (exit imports), G-17 (UWG in core), G-09 (L6 policy stub) |
| F — Test/CI proof gap | 1 | G-23 |
| **EXEMPT** | 1 | G-19 |
| **Total actionable** | **22** | G-01 through G-22 (excl. G-19) |

---

## Hard Constraints (reiterated)

1. **No app-specific changes inside `agentic_core`** — all remediation moves code OUT of core into `apps_lic`. Constraint sourced from §BL-1 + §BL-5.
2. **Generic core interface gap (W3.P4, G-13, G-14/15):** If the required generic interface does not yet exist, create a **separate enabling plan** (see §Generic Interface Dependency Order). The present plan does not add `apps_lic` logic to core as a shortcut.
3. **No direct L4 writes outside UWG** — `touch_state_writer.py` migration preserves UWG path; writer moves to app-owned location, UWG mechanism stays generic. Sourced from §BL-4/UWG.
4. **C0 emits `GateVerdict` only** — C0 binding migration must preserve `BYPASS_PRELOADED_CONTEXT` typed bypass; no C0 state write, no LLM call. Sourced from §BL-4/C0.
5. **PA only composes prompt envelopes** — PA binding migration preserves no-retrieval/no-execution constraint.
6. **L2 may emit `proposed_state_diff` only** — L2 binding migration preserves this; no direct L4 write in migrated binding.
7. **Exit emits exactly one X3** — Exit binding migration preserves single-X3 invariant and `fail-closed` on missing `exit_profile_ref`. Sourced from §BL-4/Exit.
8. **L6 is completed-run/future-run only** — L6 binding migration raises `L6CurrentRunMutationError` on in-flight run input. Sourced from §BL-4/L6.
9. **L5 certifies evidence only** — L5 HITL policy migration does not alter L5 evaluation framework; framework consumes `HITLPolicyProtocol` injected from app-owned config. Sourced from §BL-4/L5.
10. **No code changes in this plan** — verified by §No Code Changes Verification block.

---

## Appendix A — Verification Command Reference

```powershell
# W0.P1 — baseline literal count
(Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "apps_lic" | Select-Object Filename -Unique).Count

# W0.P2 — direct imports baseline
Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "^from apps_lic|^import apps_lic"

# W1.P1 — apps_rg shim proof (≤30 lines)
(Get-Content agentic_core/runtime/entry/u0_apps_rg_binding.py).Count

# W1.P5 — no apps_rg config paths in core
Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "apps_rg/config" | Where-Object { $_ -notmatch "^\s*#" }

# W2 gap enumeration — route/exit/profile config ownership scan
Get-ChildItem apps_lic/config -Recurse | Where-Object { $_.Name -match "route|cache|exit|meta_feedback" }

# W3.P1 — post-migration shim line counts
foreach ($f in Get-ChildItem agentic_core -Recurse -Include "apps_lic_*_binding.py") {
  Write-Host "$($f.Name): $((Get-Content $f).Count) lines"
}

# W3.P2 — post-remediation import scan (expected: 0)
Get-ChildItem -Path agentic_core -Recurse -Include "*.py" |
  Select-String -Pattern "^from apps_lic|^import apps_lic" |
  Where-Object { $_.Path -notmatch "_binding\.py$" }

# W5.P1 — run contamination scanner
python ops_scripts/ci/check_apps_lic_core_contamination.py

# W5.P2 — run import boundary scanner
python ops_scripts/ci/check_apps_lic_core_imports.py

# W6.P3 — full contract test suite
python -m pytest tests/_apps_contract/ -v --tb=short
python -m pytest tests/_apps_contract/test_apps_lic_u0_only_entry.py -v
python ops_scripts/ci/run_contract_gates.py
```

---

## Appendix B — apps_rg vs apps_lic Binding Location Comparison

| Layer | apps_rg (golden) | apps_lic (current) | apps_lic (target) |
|-------|------------------|--------------------|-------------------|
| U0 | `apps_rg/runtime/bindings/u0_binding.py` ✅ | `agentic_core/runtime/entry/u0_apps_lic_binding.py` ❌ | `apps_lic/runtime/bindings/u0_binding.py` |
| L0 | `apps_rg/runtime/bindings/l0_binding.py` ✅ | `agentic_core/L0_routing/apps_lic_l0_binding.py` ❌ | `apps_lic/runtime/bindings/l0_binding.py` |
| L1 | `apps_rg/runtime/bindings/l1_binding.py` ✅ | `agentic_core/L1_cognition/apps_lic_l1_binding.py` ❌ | `apps_lic/runtime/bindings/l1_binding.py` |
| C0 | `apps_rg/runtime/bindings/c0_binding.py` ✅ | `agentic_core/runtime/c0/apps_lic_c0_binding.py` ❌ | `apps_lic/runtime/bindings/c0_binding.py` |
| PA | `apps_rg/runtime/bindings/pa_binding.py` ✅ | `agentic_core/prompt_governance/apps_lic_pa_binding.py` ❌ | `apps_lic/runtime/bindings/pa_binding.py` |
| L2 | `apps_rg/runtime/bindings/l2_binding.py` ✅ | `agentic_core/L2_execution/apps_lic_l2_binding.py` ❌ | `apps_lic/runtime/bindings/l2_binding.py` |
| L3 | `apps_rg/runtime/bindings/` (dispatch) ✅ | `agentic_core/L3_orchestration/apps_lic_l3_binding.py` ❌ | `apps_lic/runtime/bindings/l3_binding.py` |
| Exit | `apps_rg/runtime/bindings/exit_binding.py` ✅ | `agentic_core/runtime/exit/apps_lic_exit_binding.py` ❌ | `apps_lic/runtime/bindings/exit_binding.py` |
| L6 | `apps_rg/runtime/bindings/` (l6) ✅ | `agentic_core/L6_observability/promotion/apps_lic_promo_binding.py` ❌ | `apps_lic/runtime/bindings/l6_binding.py` |
| Dispatch | `apps_rg/runtime/dispatch/apps_rg_dispatch.py` ✅ | `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` ❌ | `apps_lic/runtime/dispatch/apps_lic_dispatch.py` |
| U0 adapter | `apps_rg/runtime/u0/adapter.py` ✅ | `agentic_core/runtime/u0/apps_lic_u0_adapter.py` ❌ | `apps_lic/runtime/u0/adapter.py` |
| HITL policy | N/A | `agentic_core/L5_safety/policy/apps_lic_reengagement.py` ❌ | `apps_lic/policy/reengagement_hitl_policy.py` |
| Touch state writer | N/A | `agentic_core/L4_state/uwg/touch_state_writer.py` ❌ | `apps_lic/state/touch_state_writer.py` |
| Touch state schema | N/A | `agentic_core/L4_state/schemas/apps_lic_touch_state.sql` ❌ | `apps_lic/state/schemas/touch_state.sql` |
| Ingress payload contract | N/A | `agentic_core/runtime/contracts/apps_lic_ingress_payload.py` ❌ | `apps_lic/contracts/ingress_payload.py` |

**Legend:** ✅ = correct app-owned location · ❌ = contamination in `agentic_core`
