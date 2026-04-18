# G1b — `apps_shared/` as Library-Only

`apps_shared/` is classified **`is_library_only: true`** in `app_inventory.yaml`. This document records the evidence and implications.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## Evidence

### 1. No runtime `__main__.py` at package root

```
apps_shared/
  __init__.py      (package init)
  _compat/         (standalone-mode shims)
  config/
  data/
  data_adapters/
  enforcement/
  integrations/
  mixins/
  prompts/
  reasoning/
  scripts/         (admin / dev tooling — NOT service entries)
  services/
  spine/
  tests/
  types/
  utils/
  validators/
  SVP_ENGINEERING_REVIEW.md
```

There is **no** `apps_shared/__main__.py`. Compare with the six runtime apps, each of which has one.

### 2. `scripts/` directory contains admin utilities, not service entries

23 files under `apps_shared/scripts/` have `if __name__ == "__main__":` blocks — these are developer / maintenance utilities (migration scripts, one-offs, verification helpers), not long-running service entry points. They are captured in `entry_points` for completeness with `kind: cli_script`, not `kind: cli`.

### 3. 268 modules consumed by other apps

`apps_shared/` is the second-largest consumer of `agentic_core` (415 import occurrences across 268 modules) because it wraps core primitives for reuse by the 6 runtime apps. This is the defining characteristic of a shared primitives library.

### 4. Per-app `apps_shared` consumption

`app_inventory.yaml` records each runtime app's `apps_shared_uses` field. Short summary of who consumes `apps_shared`:

- APP-EVAL → consumes multiple `apps_shared` modules (in sub_surfaces: engines, integrations, services)
- APP-EXEC → consumes `apps_shared`
- APP-LIC → consumes `apps_shared`
- APP-RESEARCH → consumes `apps_shared`
- APP-RFP → consumes `apps_shared`
- APP-RG → consumes `apps_shared`
- APP-UNDERWRITING_AI → likely does not consume `apps_shared` (it has 0 agentic_core imports and is likely a separate ingestion library)

The exact list for each app is in `app_inventory.yaml` under `apps_shared_uses`.

## Sub-surfaces unique to `apps_shared/`

Compared to the runtime apps' standardized sub-surfaces (`engines/`, `reasoning/`, `integrations/`, `services/`, `spine/`, `outputs/`, `validators/`, `types/`, `tools/`, `config/`, `tests/`), `apps_shared/` introduces additional structure that confirms its library role:

| Sub-surface | Purpose | Library evidence |
|---|---|---|
| `data_adapters/` | Adapter layer between external data formats and agentic_core types | Only present here; not in any runtime app |
| `mixins/` | App-level mixins (distinct from `agentic_core/mixins/`) | Shared composition for runtime apps |
| `prompts/` | Shared prompt templates | Consumed by runtime apps' reasoning |
| `enforcement/` | Shared enforcement primitives | Runtime apps re-apply these |

Runtime apps' structure assumes `apps_shared/*` is importable; no runtime app re-implements these sub-surfaces.

## Rules G1b applied

Per `docs/wave_g/G0_full_runtime_plan/dependency_and_risk_register.md` §R-G-07:
> `apps_shared/` is not a runtime app — must not get an `__main__`-style entry. `is_library_only: true` required for apps_shared; no `__main__` entry permitted.

Compliance:
- `is_library_only: true` set in `app_inventory.yaml` ✅
- No `kind: cli` entry — all 23 entries are `kind: cli_script` (admin/dev utilities) ✅
- Sub-surfaces standard (no invented structure) ✅

## Implications

### For G2

- Treat `apps_shared/` as an intermediate layer in the app-to-core binding graph. Runtime app → `apps_shared` → `agentic_core` is the expected pattern for many call-chains.
- When computing boundary-violation counts, `apps_shared/` imports of `agentic_core` are LEGITIMATE (apps_shared is the library that wraps core for reuse).

### For G4

- `apps_shared/data/` is a shared data surface. It is not durable-state — treat as fixture/seed data until G4 can inspect content.

### For G4b

- `apps_shared/prompts/` is a shared prompt surface. Catalogue in the prompt surface map alongside `agentic_core/prompt_governance/`.
- `apps_shared/config/` is a shared configuration plane. Catalogue in the config knob catalogue.

### For G6

- `apps_shared/mixins/` and `agentic_core/mixins/` may have duplicate responsibilities — both provide cross-cutting composition. G6 should classify the boundary (likely: core mixins bind to runtime primitives; shared mixins bind to multi-app patterns).

## Conclusion

`apps_shared/` is correctly and deliberately library-only. No runtime entry point exists, no runtime invocation of `apps_shared` as a service is expected. Its role is to wrap agentic_core primitives for reuse by the 6 runtime apps.

No further action needed in G1b. Downstream waves (G2, G4, G4b, G6) will consume this classification.
