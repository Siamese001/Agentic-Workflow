# H1 — Blocker Reduction for ADG+Chroma Hybrid Layer

## 1. Wave ID, title, one-line purpose

**H1** — *Blocker Reduction for ADG+Chroma Hybrid Layer*. Decompose production-blocking residuals from H0/G7 into closure-ready remediation units with explicit owners, evidence requirements, sequencing, and production-readiness delta.

wave: H1
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## 2. Inputs

- H0 readiness and pilot set:
  - `docs/wave_h/H0_readiness_and_pilot/README.md`
  - `docs/wave_h/H0_readiness_and_pilot/readiness_gates.md`
  - `docs/wave_h/H0_readiness_and_pilot/card_family_design.md`
  - `docs/wave_h/H0_readiness_and_pilot/projection_pipeline_plan.md`
  - `docs/wave_h/H0_readiness_and_pilot/pilot_scope.md`
  - `docs/wave_h/H0_readiness_and_pilot/go_no_go_matrix.md`
- G7 integrated baseline:
  - `docs/wave_g/G7_integrated_runtime_map/README.md`
  - `docs/wave_g/G7_integrated_runtime_map/whole_system_runtime_map.md`
  - `docs/wave_g/G7_integrated_runtime_map/traceability_matrix.yaml`
  - `docs/wave_g/G7_integrated_runtime_map/ownership_matrix.md`
  - `docs/wave_g/G7_integrated_runtime_map/open_blockers_and_acceptance.md`
  - `docs/wave_g/G7_integrated_runtime_map/final_gap_register.md`
- Upstream evidence sets: `docs/wave_g/G0..G6` artifacts as cited in H0.
- Wave F baseline: `docs/wave_e/99_integration_v14/canonical/*`.
- Phase 0 precondition evidence:
  - ADG healthy and Redis cache hot on `04182026_0858`.

## 3. Outputs

- `README.md`
- `blocker_breakdown.md`
- `closure_criteria.md`
- `remediation_sequence.md`
- `owner_matrix.md`
- `production_readiness_delta.md`

## 4. Blocker-reduction method

1. Start from H0/G7 production blockers and mandatory H1 blocker set.
2. Normalize each blocker into a common decomposition shape (why block, closure condition, evidence, owner, remediation type, parallelizability, card-family impact).
3. Assign objective closure tests and minimum evidence required for closure declaration.
4. Sequence remediation by dependency graph (canonical-state and ownership foundations before broad production packaging).
5. Separate mandatory production blockers from secondary watch/defer/accept residuals.

## 5. Highest-leverage blockers

Highest leverage (largest downstream unblock impact):

- `B7-G4-03` / `B7-G6-03` memory canonical-state ambiguity
- `B7-G6-05` ownership formalization completion
- `B7-G6-01` + `B7-G6-02` contract-authority resolution
- `B7-G2b-06` + `DISABLE_RUNTIME_MUTATION_GUARD` governance hardening

These collectively gate storage/control-plane card safety, ownership trust labeling, and production governance trust.

## 6. Pilot interaction note

Bounded pilot posture from H0 remains valid:

- pilot-safe families can proceed unchanged if instability labeling and exclusions are preserved,
- H1 blocker reduction does not require pilot suspension,
- pilot outputs remain non-production dependencies.

## 7. Production-readiness recommendation

H production remains **NO-GO** at H1 start.

Recommendation:

- execute H1 blocker reduction sequence first,
- re-evaluate production gates after objective closure evidence is available,
- use H2 for either final blocker closure pass or production-implementation planning depending on achieved H1 delta.
