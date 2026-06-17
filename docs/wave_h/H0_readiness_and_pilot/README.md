# H0 — ADG+Chroma Hybrid Layer Readiness, Gating, and Pilot Design

## 1. Wave ID, title, one-line purpose

**H0** — *ADG+Chroma Hybrid Layer Readiness, Gating, and Pilot Design*. Convert the completed Wave G runtime map into an evidence-based Wave H readiness decision, bounded pilot scope, and explicit pilot-to-production gates for the hybrid symbolic-plus-semantic layer.

wave: H0
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## 2. Inputs

- Primary H0 integration baseline:
  - `docs/wave_g/G7_integrated_runtime_map/README.md`
  - `docs/wave_g/G7_integrated_runtime_map/whole_system_runtime_map.md`
  - `docs/wave_g/G7_integrated_runtime_map/traceability_matrix.yaml`
  - `docs/wave_g/G7_integrated_runtime_map/ownership_matrix.md`
  - `docs/wave_g/G7_integrated_runtime_map/open_blockers_and_acceptance.md`
  - `docs/wave_g/G7_integrated_runtime_map/final_gap_register.md`
- Upstream Wave G evidence sets consumed:
  - `docs/wave_g/G6_taxonomy_cleanup/*`
  - `docs/wave_g/G5_runtime_topology/*`
  - `docs/wave_g/G4b_control_plane/*`
  - `docs/wave_g/G4_storage_infra/*`
  - `docs/wave_g/G3_pipelines/*`
  - `docs/wave_g/G2b_provider_gateway/*`
  - `docs/wave_g/G2_service_wiring/*`
  - `docs/wave_g/G1b_apps_inventory/*`
  - `docs/wave_g/G1_core_runtime_inventory/*`
  - `docs/wave_g/G0_full_runtime_plan/*`
- Wave F canonical baseline:
  - `docs/wave_e/99_integration_v14/canonical/*`
- Phase 0 precondition evidence:
  - `adg_health` healthy on snapshot `04182026_0858`
  - Redis hot-cache aligned after force ingest and reload to `04182026_0858`

## 3. Outputs

- `README.md`
- `readiness_gates.md`
- `card_family_design.md`
- `projection_pipeline_plan.md`
- `pilot_scope.md`
- `go_no_go_matrix.md`

## 4. H readiness logic

H0 readiness uses a two-layer rule:

1. **Pilot readiness rule**: start a bounded pilot if unresolved items do not corrupt card truth for selected families/use-cases.
2. **Production readiness rule**: start full implementation only when blocker-class residuals that can create canonical-state ambiguity, ownership ambiguity, or governance-trust ambiguity are closed.

Symbolic/semantic split for H:

- ADG remains exact structural authority (imports, fan-in/out, layer facts, process/store topology references).
- Chroma is a semantic access layer over curated, labeled, stability-aware cards.
- Cards with unstable truth are either excluded from pilot, flagged as unstable, or deferred.

## 5. Residuals that matter most

Highest-impact residuals for H production readiness:

- `B7-G4-03` and `B7-G6-03` memory canonical-state ambiguity
- `B7-G6-05` ownership formalization completion
- `B7-G2b-06` egress-guard audit gap
- `DISABLE_RUNTIME_MUTATION_GUARD` bypass posture
- `B7-G6-01` dead/unwired `L_CONTRACTS` status
- `B7-G6-02` duplicate execution-trace ownership
- `B7-G6-04` 337-module taxonomy residual bucket

Residuals that do not block a bounded pilot when scope is constrained:

- `B7-G3-04` partial replay topology
- `B7-G3-06` partial system_learning topology
- selected G5 operational ambiguities (restart opacity, unknown restart modes)

## 6. Pilot recommendation

Start a bounded H pilot now with:

- 1–2 initial consumer use cases (`apps_rg` and `apps_lic` support paths from `apps_research`)
- safe-now and pilot-only card families only (no unstable canonical claims)
- explicit “non-production dependency” posture
- hard evaluation gates and rollback/no-go criteria

## 7. Production recommendation

Do **not** start full H production implementation yet.

Production should wait for closure of production-blocking residuals listed in `go_no_go_matrix.md` and `readiness_gates.md`, especially canonical-state, ownership, and governance-trust blockers.
