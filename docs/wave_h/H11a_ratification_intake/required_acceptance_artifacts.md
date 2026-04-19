# H11a — Required Acceptance Artifacts

wave: H11a
adg_snapshot: artifacts/adg/adg_indexed_04182026_2015.sqlite
adg_snapshot_timestamp: "04182026_2015"

| blocker_id | exact_accepted_artifact_name_needed | who_must_approve | approval_mode | missing_approval_alone_keeps_below_3 |
|---|---|---|---|---|
| B7-G4-03 | Accepted Canonical-Memory Enforcement Ratification Record | storage/config owner + runtime owner (+ governance acknowledgment) | co-ratified core + governance acknowledgment | yes |
| B7-G6-03 | Accepted Canonical-State Carry-Forward Ratification Record | storage/config owner + runtime owner (+ governance acknowledgment) | co-ratified core + governance acknowledgment | yes |
| B7-G6-05 | Accepted Mixed-Control Threshold and Reduction Ratification Record | architecture owner + runtime owner | co-ratified | yes |
| B7-G6-02 | Accepted Execution-Trace Authority and Alignment Ratification Record | architecture owner + runtime owner | co-ratified | yes |
| B7-G2b-06 | Accepted Egress-Override Governance Ratification Record | governance owner (primary) + runtime owner (supporting) | governance-led co-ratified | yes |
| DISABLE_RUNTIME_MUTATION_GUARD | Accepted Governed Bypass Ratification Record | governance owner (primary) + runtime owner (supporting) | governance-led co-ratified | yes |
| B7-G6-04 | Accepted Taxonomy Closure Threshold Ratification Record | taxonomy owner (primary), architecture owner advisory | single-owner primary (+ advisory) | yes |
| B7-G3-05 | Accepted Resilience Co-Ratification Record | provider/gateway owner + governance owner | mandatory co-ratified | yes |
