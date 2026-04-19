# H8 — Ratification and Sign-Off Requirements

wave: H8
adg_snapshot: artifacts/adg/adg_indexed_04182026_2001.sqlite
adg_snapshot_timestamp: "04182026_2001"

## Ratification model

A blocker is not closure-ready at score 3 if any required owner ratification artifact is absent.

## 1) Architecture-owner ratification

Required for:

- `B7-G6-05`: ratify mixed-control threshold definition and threshold-pass criteria.
- `B7-G6-02`: ratify single execution-trace authority decision and downstream alignment completion.

Required artifacts:

1. architecture decision note with explicit closure criteria,
2. architecture-owner closure recommendation signature/approval record.

## 2) Runtime-owner ratification

Required for:

- `B7-G6-05`: attest measured reduction evidence is runtime-realistic and sustained.
- `B7-G6-02`: attest downstream reference realignment is runtime-correct.
- `B7-G4-03` / `B7-G6-03`: attest canonical-memory enforcement behavior in runtime scope.

Required artifacts:

1. runtime conformance attestation,
2. runtime owner sign-off on deployed/operational behavior assumptions used in closure evidence.

## 3) Governance-owner ratification

Required for:

- `B7-G2b-06`: ratify egress-override schema, governance-minimum fields, and exception workflow.
- `DISABLE_RUNTIME_MUTATION_GUARD`: ratify policy-constrained bypass, audit evidence, unauthorized rejection controls.
- `B7-G3-05`: co-sign resilience production posture with provider/gateway owner.

Required artifacts:

1. governance approval record for control policy artifacts,
2. governance acceptance of auditability and enforcement evidence.

## 4) Provider/gateway-owner ratification

Required for:

- `B7-G3-05`: accept resilience contract and contract-conformance execution evidence.

Required artifacts:

1. provider/gateway owner acceptance note,
2. cross-reference to conformance execution bundle.

## 5) Taxonomy-owner ratification

Required for:

- `B7-G6-04`: accept full-bucket taxonomy closure metrics and production-safe threshold proof.

Required artifacts:

1. taxonomy decomposition closure note,
2. taxonomy-owner sign-off that threshold pass is sufficient for production packaging scope.

## Ratification dependency summary by blocker

| blocker_id | mandatory ratification/sign-off dependencies |
|---|---|
| B7-G4-03 | storage/config owner + runtime owner (+ governance acknowledgement for policy controls) |
| B7-G6-03 | storage/config owner + runtime owner (+ governance acknowledgement for policy controls) |
| B7-G6-05 | architecture owner + runtime owner |
| B7-G6-02 | architecture owner + runtime owner |
| B7-G2b-06 | governance owner (primary), runtime owner (supporting) |
| DISABLE_RUNTIME_MUTATION_GUARD | governance owner (primary), runtime owner (supporting) |
| B7-G6-04 | taxonomy owner (primary), architecture owner (advisory) |
| B7-G3-05 | provider/gateway owner + governance owner |
