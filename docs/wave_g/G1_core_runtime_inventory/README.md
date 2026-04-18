# G1 — Core Runtime Component Inventory

## 1. Sub-wave ID, title, purpose

**G1** — *Core Runtime Component Inventory*. Classify every `.py` module under `agentic_core/` by layer (L0–L6 or CROSS_CUTTING) and role (from the fixed enum in `docs/wave_g/G0_full_runtime_plan/output_contracts.md`), and record which v1.3/v1.4 requirement-graph atoms each module embodies.

## 2. Inputs

- **ADG snapshot (frozen)**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (timestamp `04172026_0611`; 83,319 nodes, 638,815 edges; schema 1.0; redis cache healthy at run time).
- **Planning artefacts (G0)**:
  - `docs/wave_g/G0_full_runtime_plan/output_contracts.md` (Component inventory schema, role enum, layer enum)
  - `docs/wave_g/G0_full_runtime_plan/artifact_plan.md`
  - `docs/wave_g/G0_full_runtime_plan/proposed_subwaves.md`
  - `docs/wave_g/G0_full_runtime_plan/dependency_and_risk_register.md`
  - `docs/wave_g/G0_full_runtime_plan/wave_g_execution_plan.md`
  - `docs/wave_g/G0_full_runtime_plan/runtime_scope_map.md`
  - `docs/wave_g/G0_full_runtime_plan/repo_surface_inventory.md`
- **Wave F baseline** (v1.4 canonical, signed off; commit `4b794d5d46`):
  - `docs/wave_e/99_integration_v14/canonical/atoms.yaml`
  - `docs/wave_e/99_integration_v14/canonical/edges.yaml`
  - `docs/wave_e/99_integration_v14/canonical/sources.yaml`
  - `docs/wave_e/99_integration_v14/canonical/exclusions.yaml`
  - `docs/wave_e/F4_edge_exclusion_cleanup/weak_edge_upgrade_matrix.md`
- **Repo surface**: every `.py` under `agentic_core/**`, excluding `__pycache__/`.

## 3. Outputs

- `README.md` — this index.
- `component_inventory.yaml` — **2,014 entries**, one per `agentic_core/**/*.py`, conforming to the G0 component schema.
- `layer_embodiment_map.md` — L0–L6 atom → concrete modules that embody each atom, plus CROSS_CUTTING anchor notes.
- `cross_cutting_classification.md` — classification of every cross-cutting subsystem (runtime, agents, seams, mixins, etc.) with representative modules.
- `unclassified_modules.md` — explicit register of modules with `role=other` (337 entries) deferred to G6 for finer role resolution, plus any surfaces that could not be classified at all (0).

## 4. Stop condition

Met. Concrete evidence:

- Every `.py` under `agentic_core/` appears **exactly once** in `component_inventory.yaml`. Round-trip verification:
  - FS walk: 2,014 `.py` files (excluding `__pycache__`).
  - YAML entries: 2,014 unique `path` values, 2,014 unique `id` values.
  - Set difference both directions: 0.
- Every entry has all fields required by the G0 schema: `id`, `path`, `layer`, `role`, `entry_points`, `exports`, `imports_summary` (`intra_layer`, `cross_layer`, `external`), `seams_used`, `embodies.atoms`, `embodies.edges`, `embodies.sources`, `notes`.
- Layer values are drawn from `{L0, L1, L2, L3, L4, L5, L6, CROSS_CUTTING}` only.
- Role values are drawn from the 20-member enum only.
- No module is double-homed (a module is either layered or CROSS_CUTTING, never both).
- The ADG snapshot path and timestamp are recorded in the YAML header and in this README.
- `role=other` modules are classified (the role is valid) and additionally listed in `unclassified_modules.md` with deferral reason and proposed downstream owner (G6).

## 5. Risks encountered during execution

- **R-G-05 (taxonomy drift)** — partially realized. 337/2014 modules (16.7%) resolve only to `role=other` after pattern + content heuristics. This is expected in a repo of this size: the role enum is coarse and some subsystems (ADG tooling, evaluation internals, knowledge lifecycle scaffolding) do not map cleanly to the 19 non-`other` roles. These are deferred to G6 for consolidation / finer classification; `unclassified_modules.md` records them and the subsystem they cluster in.
- **R-G-02 (dynamic imports)** — deferred. Import counts are computed from static AST parsing of `import` / `from X import Y` statements only. Dynamic imports via `importlib.import_module(...)` are not captured here and are explicitly G2's responsibility.
- **R-G-03 (grep drift)** — avoided. No `grep_search` was used for dependency analysis. Every import-layer classification is derived from AST-parsed module names compared against the known layer prefix map. ADG snapshot is recorded for G2 to re-probe structural edges.
- **Content-hint false positives** — mitigated by ordering: directory-driven classification runs before filename heuristics, which run before content heuristics. Directory signal (e.g., `enforcement/` → `policy`; `interfaces/` → `interface`) dominates.
- **`__init__.py` re-export shims** — classified as `role=other` when their body is under ~400 characters and they only re-export. This is deliberate: they are not runtime components, they are packaging. Treat as G6 cleanup candidates if needed.

## 6. B7 candidates surfaced

**None.** G1 is classification-only; it inspects static module structure and cited atoms. It does not infer cross-layer interactions. B7 candidates will be surfaced in G2 (wiring) and G3/G3b (pipelines).

## 7. Hand-off note for G1b and G2

- **For G1b (apps inventory)**: `component_inventory.yaml` is the authoritative list of `agentic_core` modules. When G1b records `core_bindings.direct_imports_from` for each app, those imports MUST resolve to paths present in `component_inventory.yaml`. Cross-cutting modules an app depends on (e.g., `agentic_core/seams/*`, `agentic_core/interfaces/*`, `agentic_core/L_CONTRACTS/*`) are all present in the inventory.
- **For G2 (wiring)**: ADG snapshot `artifacts/adg/adg_indexed_04172026_0611.sqlite` is the probe for G2. Every module in `component_inventory.yaml` is a graph node — G2's edge matrix can join on `path`. G2 should additionally enumerate `importlib` / `__import__` call sites, which G1 did not capture.
- **Gate 1 status**: satisfied for the `agentic_core/` portion. G1b can start once it has run its own enumeration of `apps_*/`. G2 can start after G1b completes, using the ADG snapshot recorded here (or a fresh snapshot — either is acceptable, as long as it is recorded).

## Summary counts (authoritative; re-derivable from `component_inventory.yaml`)

| Dimension | Value |
|---|---:|
| Total `.py` modules inventoried | **2014** |
| Layer L0 | 88 |
| Layer L1 | 152 |
| Layer L2 | 194 |
| Layer L3 | 167 |
| Layer L4 | 141 |
| Layer L5 | 382 |
| Layer L6 | 89 |
| CROSS_CUTTING | 801 |
| Role `util` | 352 |
| Role `other` | 337 |
| Role `policy` | 253 |
| Role `contract` | 215 |
| Role `reasoner` | 204 |
| Role `shim` | 123 |
| Role `runtime-scaffold` | 111 |
| Role `agent` | 103 |
| Role `validator` | 89 |
| Role `mixin` | 55 |
| Role `interface` | 38 |
| Role `reader` | 35 |
| Role `gate` | 31 |
| Role `orchestrator` | 23 |
| Role `evaluator` | 16 |
| Role `healer` | 12 |
| Role `registry` | 7 |
| Role `seam` | 5 |
| Role `adapter` | 3 |
| Role `writer` | 2 |
| Modules with at least one v1.3/v1.4 atom citation | 1215 |
| Modules without an atom citation (`no v1.x mapping`) | 799 |

Ready for G1b and G2.
