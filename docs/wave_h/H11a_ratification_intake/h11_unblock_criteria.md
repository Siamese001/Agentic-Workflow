# H11a — H11 Unblock Criteria

wave: H11a
adg_snapshot: artifacts/adg/adg_indexed_04182026_2015.sqlite
adg_snapshot_timestamp: "04182026_2015"

## What exact accepted artifacts must exist before true H11 can run

Accepted in-repo ratification artifacts must exist for one or more blockers from this set:

- Accepted Canonical-Memory Enforcement Ratification Record (`B7-G4-03`)
- Accepted Canonical-State Carry-Forward Ratification Record (`B7-G6-03`)
- Accepted Mixed-Control Threshold and Reduction Ratification Record (`B7-G6-05`)
- Accepted Execution-Trace Authority and Alignment Ratification Record (`B7-G6-02`)
- Accepted Egress-Override Governance Ratification Record (`B7-G2b-06`)
- Accepted Governed Bypass Ratification Record (`DISABLE_RUNTIME_MUTATION_GUARD`)
- Accepted Taxonomy Closure Threshold Ratification Record (`B7-G6-04`)
- Accepted Resilience Co-Ratification Record (`B7-G3-05`)

## Whether H11 can run if only some blockers gain acceptance

Yes, true H11 can run if at least one blocker has newly accepted in-repo ratification evidence.

However, final-gate qualification remains no until all mandatory blockers reach score 3.

## Exact rule for when H11 should be retried

Retry true H11 immediately when BOTH are true:

1. One or more newly accepted in-repo ratification artifacts are added for the 8 mandatory blockers.
2. Each new artifact has explicit blocker mapping and owner approval metadata (owner role, status, timestamp, artifact path).
