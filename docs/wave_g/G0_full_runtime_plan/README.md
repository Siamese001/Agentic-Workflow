# Wave G0 — Full Runtime Topology Planning

Planning wave for the **whole runtime embodiment** of the Agentic-Workflow repository. This is not a requirement-graph wave — Wave E/F already delivered the normative control graph (v1.3 canonical + F4 cleanup). Wave G maps how that control graph is actually *wired, deployed, configured, operated, and observed* in the current codebase.

## Relationship to Wave E/F

| Aspect | Wave E/F (closed) | Wave G (this planning wave) |
|---|---|---|
| Primary artefact | Requirement/control graph (families, atoms, edges, exclusions, sources) | Runtime topology map (components, wires, pipelines, storage, deployment, ops) |
| Unit of work | Claim / invariant | Module / service / pipeline / store / config knob |
| Authority model | Sources cited per atom/edge | Code paths, configs, MCP servers, ops scripts cited per topology node |
| Schema SSOT | `docs/wave_e/00_schema/requirement_graph_schema.yaml` | Runtime-node / runtime-edge schema to be specified in G1 |
| Success criterion | NORMATIVE coverage per family | Every runtime surface in this repo has a traced, named embodiment in a G artefact |
| Status at G0 start | v1.3 canonical publishable; F4 cleanup merged; B7 interaction candidates deferred | This plan |

## Baseline signed off before G starts

- `docs/wave_e/99_integration_v13/canonical/` — all 12 families GREEN, 60/60 ACTIVE atoms NORMATIVE.
- `docs/wave_e/F4_edge_exclusion_cleanup/` — 8 weak edges closed, OOS-003 superseded (integrated in v1.4 per commit `4b794d5d46`).
- **B7 (6 deferred interaction candidates)**: explicitly parked as later graph-completeness work; does not gate Wave G. Where a G sub-wave surfaces a runtime interaction not yet represented in the v1.3 graph, G records it as a *candidate B7 extension* rather than trying to close B7.

## Non-duplication discipline

Wave G MUST NOT re-derive normative claims that already live in v1.3. It MUST cite v1.3 atoms/edges by ID when a runtime fact is the embodiment of a claim (e.g., "this is the F09 UWG seam" → cite F09.01–F09.05). When a runtime fact has no corresponding atom, G records it as:
- a **runtime-only fact** (implementation detail outside the requirement graph), or
- a **B7 candidate** (new interaction the requirement graph should eventually first-class).

## Files in this directory

| File | Purpose |
|---|---|
| `README.md` | This index. |
| `runtime_scope_map.md` | What the G runtime map must and must not cover, by dimension. |
| `repo_surface_inventory.md` | Concrete repo-path inventory G is accountable for, with coarse classification. |
| `proposed_subwaves.md` | Full list of G sub-waves with scope, surfaces, outputs, stop conditions, risks. |
| `artifact_plan.md` | Canonical output-artefact layout and naming for each sub-wave. |
| `output_contracts.md` | Minimum schema/shape contract every G artefact must satisfy. |
| `dependency_and_risk_register.md` | Ordering dependencies between sub-waves, blind spots, and risk register. |
| `wave_g_execution_plan.md` | Executable plan: ordered sub-wave sequence, preconditions, and gates. |

## Outcome of G0

After this planning wave, the team can execute G1 → G7 in order without further planning rework. Each sub-wave's scope, inputs, outputs, and stop condition is explicit and repo-grounded.
