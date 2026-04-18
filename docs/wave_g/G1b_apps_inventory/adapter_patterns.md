# G1b — Adapter Patterns

Nine adapter shims identified across 7 apps (APP-LIC and APP-UNDERWRITING_AI have none). All shims share a common architectural intent: **allow the app to remain importable and runnable even when `agentic_core` is absent or partially installed** ("standalone mode"). They do NOT introduce new runtime behaviour — they degrade gracefully.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## Pattern catalogue

### Pattern A — Telemetry-emitter no-op shim

**Representatives**:
- `apps_eval/_telemetry.py`
- `apps_research/_telemetry.py`

**Shape**:
- Single module, not a package.
- Defines a minimal `LayerSegment` enum locally (duplicating the `agentic_core.runtime.contracts.lifecycle_trace_contract.LayerSegment` values).
- `__getattr__` on the module returns a `_noop` callable for any name matching `_emit_*` or `emit_*`.
- Purpose: the app's business logic calls telemetry emitters that would normally come from `agentic_core`; in standalone mode, they silently become no-ops.

**Classification**: degrade-to-noop telemetry shim.
**Risk posture**: low. Pure no-op; cannot cause incorrect runtime behaviour in production (production always has real `agentic_core`).

### Pattern B — Optional-import full module substitute

**Representatives**:
- `apps_exec/_optional_agentic_core.py`
- `apps_shared/_compat/agentic_core_shim.py`

**Shape**:
- Constructs `types.ModuleType` instances in `sys.modules` for selected `agentic_core.*` paths when the real package is absent.
- Provides minimal fallback classes (`LayerSegment`, `LifecycleModule` stubs).
- Activated via explicit import from the app's entry chain when detecting absent `agentic_core`.

**Classification**: module-synthesis compatibility shim.
**Risk posture**: medium. The shim injects fake modules into `sys.modules` — G2's import-graph analysis will see these as normal imports. Must be flagged so G2 does not mistake shim-provided classes for real L0–L6 bindings. `apps_exec/_optional_agentic_core.py` is noted explicitly in the G0 plan as a pattern worth watching.

### Pattern C — Try/except import with real fallback

**Representatives**:
- `apps_rfp/_compat/lifecycle_trace.py`
- `apps_shared/_compat/__init__.py` + `agentic_core_shim.py` (combination pattern B+C)

**Shape**:
```python
try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import *
    _STANDALONE = False
except ImportError:
    # define local fallbacks
    _STANDALONE = True
```

- App code consumes the symbol regardless of source.
- Real production path uses real agentic_core; standalone path uses local fallbacks.

**Classification**: conditional-import shim.
**Risk posture**: low. The real-import branch is the default in production.

### Pattern D — Runtime bootstrap (non-degrading)

**Representative**:
- `apps_rg/bootstrap_runtime.py`

**Shape**:
- Explicitly ensures modules are installed in `sys.modules` (`_ensure_module`).
- Installs pydantic compatibility layers.
- Called early in the app's startup chain (before `__main__` logic runs).
- Does NOT substitute `agentic_core` itself — it prepares the environment for real imports to succeed.

**Classification**: runtime environment bootstrap.
**Risk posture**: medium-high in complexity (mutates `sys.modules`, sets up pydantic compat), but low in correctness risk — it is additive preparation, not substitution. APP-RG is the flagship runtime app and has the richest bootstrap.

## Per-app shim registry

| App | Shim file | Pattern | Standalone-mode fallback | `sys.modules` mutation |
|---|---|---|---|---|
| APP-EVAL | `apps_eval/_telemetry.py` | A (telemetry no-op) | yes | no |
| APP-EXEC | `apps_exec/_optional_agentic_core.py` | B (module substitute) | yes | **yes** |
| APP-RESEARCH | `apps_research/_telemetry.py` | A (telemetry no-op) | yes | no |
| APP-RFP | `apps_rfp/_compat/__init__.py` | (container) | — | no |
| APP-RFP | `apps_rfp/_compat/lifecycle_trace.py` | C (try/except) | yes | no |
| APP-RG | `apps_rg/bootstrap_runtime.py` | D (bootstrap) | **no** (real-only) | **yes** |
| APP-SHARED | `apps_shared/_compat/__init__.py` | (container) | — | no |
| APP-SHARED | `apps_shared/_compat/agentic_core_shim.py` | B (module substitute) | yes | **yes** |
| APP-LIC | — | — | — | — |
| APP-UNDERWRITING_AI | — | — | — | — |

## Key observations

1. **Three apps mutate `sys.modules`** (APP-EXEC, APP-RG, APP-SHARED). These are the apps where G2's static import-graph analysis will see synthetic modules. G2's `seam_usage_report.md` and `import_edge_matrix.md` should treat `sys.modules` writes as a separate category so they do not confuse real agentic_core imports with shim fallbacks.
2. **Standalone-mode is a deliberate architectural choice**. Every app except APP-RG has some version of "run even when agentic_core is missing". APP-RG takes the opposite stance: it assumes real agentic_core and only bootstraps pydantic / module-tree plumbing.
3. **LayerSegment enum is duplicated** in at least 4 places (`apps_eval/_telemetry.py`, `apps_exec/_optional_agentic_core.py`, `apps_shared/_compat/agentic_core_shim.py`, and the real home in `agentic_core/runtime/contracts/lifecycle_trace_contract.py`). G6 should note this as a duplicate-responsibility candidate; canonical owner is the contract module.
4. **No app uses dynamic `importlib.import_module` in its shims** at the source level I inspected. Shims use `sys.modules[name] = module` (direct assignment) or `try/except ImportError`. G2's dynamic-import scan should still confirm this for the whole apps tree.
5. **APP-LIC has zero shims** — it assumes agentic_core is always present. Given LIC has 134 modules and 4 entry points, this is an architectural choice worth recording (most likely because LIC is deployed only as part of the full stack).

## Hand-off notes

- **For G2**: treat Pattern B and D shims as *synthetic import sources*; do not count their fake modules as real agentic_core bindings in the import-edge matrix. The `core_bindings.direct_imports_from` list in `app_inventory.yaml` is already sanitized — it contains only statically-resolved `agentic_core.*` imports against G1, not shim-synthesized modules.
- **For G6**: flag the duplicate `LayerSegment` enum across 4 locations. Propose canonical owner: `agentic_core/runtime/contracts/lifecycle_trace_contract.py`.
- **For G4b**: shims are part of the standalone-mode control plane. Document this in the control plane map as a feature flag / runtime mode.
