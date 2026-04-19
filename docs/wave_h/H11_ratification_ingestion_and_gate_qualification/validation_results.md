# H11 — Validation Results

wave: H11
adg_snapshot: artifacts/adg/adg_indexed_04182026_2038.sqlite
adg_snapshot_timestamp: "04182026_2038"

## Valid accepted artifacts

All 8 newly landed artifacts passed H11b minimum schema validation:

- blocker_id present
- owner_role present in approval_records
- approval_status = approved
- timestamp_utc present
- artifact_paths_reviewed present
- rationale present
- co_ratifier_linkage present where co-ratified mode requires it

Valid list:

1. `accepted_B7-G4-03_canonical_memory_ratification.md`
2. `accepted_B7-G6-03_canonical_carry_forward_ratification.md`
3. `accepted_B7-G6-05_mixed_control_threshold_ratification.md`
4. `accepted_B7-G6-02_execution_trace_authority_ratification.md`
5. `accepted_B7-G2b-06_egress_override_governance_ratification.md`
6. `accepted_DISABLE_RUNTIME_MUTATION_GUARD_governed_bypass_ratification.md`
7. `accepted_B7-G6-04_taxonomy_threshold_ratification.md`
8. `accepted_B7-G3-05_resilience_co_ratification.md`

## Invalid artifacts

None.

## Partial-but-insufficient artifacts

None at schema validation layer.

Functional sufficiency for score movement is assessed separately in `updated_closure_scorecard.md`.
