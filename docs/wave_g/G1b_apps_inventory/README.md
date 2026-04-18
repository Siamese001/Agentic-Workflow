# G1b — apps_* Runtime and Adapter Inventory

## 1. Sub-wave ID, title, purpose

**G1b** — *apps_\* Runtime and Adapter Inventory*. Enumerate every `apps_*` surface, classify it as runtime app vs library-only, list its entry points and sub-surfaces, and catalogue every direct import from apps into `agentic_core/` resolved against G1's component inventory.

## 2. Inputs

- **ADG snapshot (frozen, same as G1)**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).
- **G1 artefacts** (consumed, not modified):
  - `docs/wave_g/G1_core_runtime_inventory/component_inventory.yaml` (2,014 entries — authoritative module-path source of truth for binding resolution)
  - `docs/wave_g/G1_core_runtime_inventory/cross_cutting_classification.md`
  - `docs/wave_g/G1_core_runtime_inventory/layer_embodiment_map.md`
- **G0 planning artefacts**: `output_contracts.md`, `repo_surface_inventory.md`, `wave_g_execution_plan.md`, etc.
- **Wave F baseline**: `docs/wave_e/99_integration_v14/canonical/*` (v1.4 — commit `4b794d5d46`).
- **Repo surface**: every `.py` under `apps_eval/`, `apps_exec/`, `apps_lic/`, `apps_research/`, `apps_rfp/`, `apps_rg/`, `apps_shared/`, `apps_underwriting_ai/`.

## 3. Outputs

- `README.md` — this index.
- `app_inventory.yaml` — **8 app entries** conforming to the G0 `app_inventory.yaml` schema.
- `app_to_core_bindings.md` — resolved binding hotspots, per-layer distribution, shared-module analysis.
- `adapter_patterns.md` — every adapter/shim identified, with pattern classification.
- `apps_shared_as_library.md` — `apps_shared/` treated as library-only, with rationale.

## 4. Stop condition

Met. Concrete evidence:

- All **8** apps listed in the user request are represented exactly once in `app_inventory.yaml`: `APP-EVAL`, `APP-EXEC`, `APP-LIC`, `APP-RESEARCH`, `APP-RFP`, `APP-RG`, `APP-SHARED`, `APP-UNDERWRITING_AI`.
- Every direct `agentic_core.*` import from every app module resolves to a path in G1's `component_inventory.yaml`. **Total unresolved imports across all 8 apps: 0.**
- Sub-surfaces are recorded as exact paths when present; `null` otherwise (never invented).
- Adapter shims enumerated: 9 distinct shims across 7 apps (see §Summary).
- `apps_shared/` is flagged `is_library_only: true` per G0 rule. `apps_underwriting_ai/` is also library-only (no `__main__.py`, no CLI entry points, 0 agentic_core imports).
- YAML validates against the G0 contract (all required fields present for every app).

## 5. Risks encountered during execution

- **R-G-02 (dynamic wiring)** — deferred to G2 as planned. G1b resolves only static `import` / `from X import Y` statements. Any `importlib`-mediated app-core binding is invisible here.
- **R-G-07 (apps_shared mis-inventory)** — mitigated. `apps_shared/` has no `__main__.py` and no top-level runtime entry; the 23 script files detected under `apps_shared/scripts/` are admin/utility scripts (each with its own `if __name__ == "__main__"` block), not a service entry point. `is_library_only: true` is correct.
- **Seam / L_CONTRACTS non-use observation** — 0 apps directly import from `agentic_core/seams/` or `agentic_core/L_CONTRACTS/`. This is either (a) architecturally correct (seams are core-internal cross-layer contracts; apps should not cross them directly) or (b) a B7 signal that apps bypass seams they should use. G2's `seam_usage_report.md` will disambiguate; G1b records the observation.
- **apps_underwriting_ai** — has 0 agentic_core imports across its 72 modules. This is unusual for a runtime app; likely indicates it is a data-ingestion library that downstream apps consume, rather than a binding against core. Noted for G2.
- **Hot coupling through CROSS_CUTTING**: every app binds most heavily to CROSS_CUTTING subsystems (mixins, runtime contracts, ADG runtime, `adg.runtime.behavioral_index`), not to specific layers. This is consistent with the G1 observation that CROSS_CUTTING is ≈40% of `agentic_core/`.

## 6. B7 candidates surfaced

**None authored.** G1b observations that may become B7 candidates are flagged for G2 / G7 to decide:

- Zero-seam-use signal (7 seams, 0 app consumers) — G2 will classify.
- `apps_underwriting_ai` zero-core-import signal — G2 will classify.
- `agentic_core.L3_orchestration.inference.qwen_vllm` imported by 6 apps — a cross-layer edge not obviously covered by v1.4 edges; G2 candidate.
- `agentic_core.adg.runtime.behavioral_index` imported by 7 apps — CROSS_CUTTING, but ADG is tooling not runtime authority; warrants G6 follow-up on whether this is an "ADG tool" vs "runtime behavioral index" naming collision.

G1b itself does not open B7 records; per G0 policy only G7 populates `b7_candidate_register.md`.

## 7. Hand-off note for G2

- `app_inventory.yaml` is ready to use. Every app has: entry_points, sub_surfaces, core_bindings.direct_imports_from, imports_by_layer, resolved_target_files, seam_uses, interface_uses, l_contract_uses, adapter_shims.
- Every import in `direct_imports_from` resolves to a G1 `component_inventory.yaml` path — G2 can join on module path directly.
- ADG snapshot `artifacts/adg/adg_indexed_04172026_0611.sqlite` is fresh; G2 may regenerate or use it.
- G2 should use `apps_rg` as the primary walk anchor (most entry points, heaviest cross-cutting coupling, explicit `bootstrap_runtime.py`). Secondary walk anchors: `apps_lic` (4 entry points, 134 modules) and `apps_exec` (has `_optional_agentic_core.py` — the most interesting adapter pattern).
- For dynamic-import detection (R-G-02), scan `importlib.import_module(`, `__import__(`, and string-keyed dispatch tables during G2. Not G1b's job.
- **Gate 1 is now fully satisfied**: G1 classified `agentic_core/**` (2014 modules) and G1b classified `apps_*/**` (see §Summary below). No unresolved app-to-core bindings. G2 may start.

## Summary (authoritative, derived from `app_inventory.yaml`)

### Per-app counts

| App | Modules | library_only | Entry points | Core imports | Unresolved | Adapter shims | Dominant layer target |
|---|---:|---|---:|---:|---:|---:|---|
| APP-EVAL | 59 | false | 2 | 11 | 0 | 1 | CROSS_CUTTING |
| APP-EXEC | 59 | false | 2 | 9 | 0 | 1 | CROSS_CUTTING |
| APP-LIC | 134 | false | 4 | 29 | 0 | 0 | CROSS_CUTTING |
| APP-RESEARCH | 55 | false | 2 | 11 | 0 | 1 | CROSS_CUTTING |
| APP-RFP | 56 | false | 2 | 9 | 0 | 2 | CROSS_CUTTING |
| APP-RG | 164 | false | 10 | 31 | 0 | 1 | CROSS_CUTTING |
| APP-SHARED | 268 | **true** | 23 (scripts) | 37 | 0 | 2 | CROSS_CUTTING |
| APP-UNDERWRITING_AI | 72 | **true** | 0 | 0 | 0 | 0 | (none) |
| **Total** | **867** | 2 lib | 45 scripts + 13 service entries | — | **0** | 9 | — |

### Runtime apps vs library-only

- **Runtime apps (6)**: APP-EVAL, APP-EXEC, APP-LIC, APP-RESEARCH, APP-RFP, APP-RG. Each has `__main__.py` at the package root.
- **Library-only (2)**: APP-SHARED (explicit: no `__main__.py`, serves as shared primitives), APP-UNDERWRITING_AI (no `__main__.py`, no agentic_core imports, ingestion-only library).

Ready for G2. Gate 1 complete.
