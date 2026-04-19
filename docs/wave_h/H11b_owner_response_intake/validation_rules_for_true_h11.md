# H11b — Validation Rules for True H11

wave: H11b
adg_snapshot: artifacts/adg/adg_indexed_04182026_2022.sqlite
adg_snapshot_timestamp: "04182026_2022"

## What counts as accepted in-repo ratification

A record counts as accepted only if all are true:

1. In-repo artifact exists with required schema fields.
2. `approval_status = approved`.
3. Artifact paths reviewed are explicit and resolve in repo.
4. Owner role is valid for blocker.
5. For co-ratified blockers, all required co-ratifier approvals are present and linked.

## What does NOT count

- Draft templates
- Unsigned/unaccepted records
- Records with `rejected` or `changes_requested`
- Records missing blocker mapping, timestamp, rationale, or artifact paths reviewed
- Role assignment tables without explicit approval decisions

## When partial approval is enough to retry H11

Partial approval is enough to retry true H11 when:

- at least one blocker gains newly accepted valid ratification evidence per schema
- evidence is committed in repo with required metadata and blocker mapping

## When partial approval is NOT enough for final-gate qualification

Partial approval is not enough for final-gate qualification when:

- one or more mandatory blockers remain below score 3
- any blocker lacking required co-ratifier acceptance still blocks final gate

Therefore:

- true H11 retry can start with partial accepted evidence,
- final-gate qualification remains no until all 8 mandatory blockers satisfy score-3 criteria.
