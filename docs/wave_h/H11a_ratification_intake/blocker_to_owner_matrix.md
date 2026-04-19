# H11a — Blocker to Owner Matrix

wave: H11a
adg_snapshot: artifacts/adg/adg_indexed_04182026_2015.sqlite
adg_snapshot_timestamp: "04182026_2015"

| blocker_id | required_owners | required_acceptance_type | acceptance_mode |
|---|---|---|---|
| B7-G4-03 | storage/config owner + runtime owner (+ governance acknowledgment) | accepted closure ratification for canonical-memory enforcement package | multi-owner (core) + governance acknowledgment |
| B7-G6-03 | storage/config owner + runtime owner (+ governance acknowledgment) | accepted closure ratification for carry-forward canonical-state package | multi-owner (core) + governance acknowledgment |
| B7-G6-05 | architecture owner + runtime owner | accepted closure ratification for threshold + measured reduction package | multi-owner co-ratification |
| B7-G6-02 | architecture owner + runtime owner | accepted closure ratification for single-authority and downstream alignment package | multi-owner co-ratification |
| B7-G2b-06 | governance owner (primary) + runtime owner (supporting) | accepted governance control package ratification (schema/records/workflow) | governance-led multi-owner |
| DISABLE_RUNTIME_MUTATION_GUARD | governance owner (primary) + runtime owner (supporting) | accepted governed bypass package ratification (policy/audit/rejection) | governance-led multi-owner |
| B7-G6-04 | taxonomy owner (primary) + architecture owner (advisory) | accepted taxonomy closure package ratification (threshold pass + decomposition sufficiency) | single-owner primary with advisory validation |
| B7-G3-05 | provider/gateway owner + governance owner | accepted co-ratification of resilience contract + conformance package | mandatory co-ratification |

## Single-owner vs multi-owner summary

Single-owner-primary possible:
- `B7-G6-04` (taxonomy owner primary; architecture advisory)

Mandatory multi-owner/co-ratified:
- `B7-G4-03`, `B7-G6-03`, `B7-G6-05`, `B7-G6-02`, `B7-G2b-06`, `DISABLE_RUNTIME_MUTATION_GUARD`, `B7-G3-05`
