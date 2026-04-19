# H11b — Ratification Landing Map

wave: H11b
adg_snapshot: artifacts/adg/adg_indexed_04182026_2022.sqlite
adg_snapshot_timestamp: "04182026_2022"

| blocker_id | expected_accepted_artifact_filename | expected_owner_groups | acceptance_mode | missing_approval_alone_keeps_below_3 |
|---|---|---|---|---|
| B7-G4-03 | `accepted_B7-G4-03_canonical_memory_ratification.md` | storage/config + runtime (+ governance acknowledgment) | co-ratified core + governance acknowledgment | yes |
| B7-G6-03 | `accepted_B7-G6-03_canonical_carry_forward_ratification.md` | storage/config + runtime (+ governance acknowledgment) | co-ratified core + governance acknowledgment | yes |
| B7-G6-05 | `accepted_B7-G6-05_mixed_control_threshold_ratification.md` | architecture + runtime | co-ratified | yes |
| B7-G6-02 | `accepted_B7-G6-02_execution_trace_authority_ratification.md` | architecture + runtime | co-ratified | yes |
| B7-G2b-06 | `accepted_B7-G2b-06_egress_override_governance_ratification.md` | governance + runtime | governance-led co-ratified | yes |
| DISABLE_RUNTIME_MUTATION_GUARD | `accepted_DISABLE_RUNTIME_MUTATION_GUARD_governed_bypass_ratification.md` | governance + runtime | governance-led co-ratified | yes |
| B7-G6-04 | `accepted_B7-G6-04_taxonomy_threshold_ratification.md` | taxonomy (primary), architecture advisory | single-owner primary (+ advisory validation) | yes |
| B7-G3-05 | `accepted_B7-G3-05_resilience_co_ratification.md` | provider/gateway + governance | mandatory co-ratified | yes |
