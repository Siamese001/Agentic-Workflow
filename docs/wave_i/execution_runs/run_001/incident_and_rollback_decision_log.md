# Incident and Rollback Decision Log — Run 001

Create one entry per incident decision event.

## Matrix Authority References

- Wave I authority matrix: `docs/wave_i/owner_escalation_and_rollback_matrix.md`
- Incident severity model: `docs/runbooks/v15_incident_playbook.md`
- Rollback drill evidence baseline: `docs/runbooks/d2_rollback_drill_evidence.md`

Rollback authority alignment rule:
- If rollback trigger is hit on the semantic-cache canary surface, decision authority must align to that matrix row rollback authority (`Runtime Operator Role`) with escalation path captured.
- If rollback trigger is hit on another in-scope surface cluster, authority must align to that cluster's matrix row.

## Entry Header

- Incident decision ID: `[execution-time fill-in]`
- Timestamp (UTC): `[execution-time fill-in]`
- Related rollout event: `Wave I Run 001`
- Related rollout unit: `Semantic-cache-enabled single canary unit (no widening in this run record set)`

## Incident Summary

- Incident summary: `[execution-time fill-in]`
- Affected surface cluster (from Wave I matrix): `[execution-time fill-in]`
- Severity: `[SEV-1 / SEV-2 / SEV-3]`

## Matrix Owner Path Used

- Primary role engaged: `[execution-time fill-in]`
- Secondary/escalation role engaged: `[execution-time fill-in]`
- Incident Commander role engaged: `[execution-time fill-in: Y/N]`
- Matrix row reference: `[execution-time fill-in: exact surface-cluster row]`

## Containment and Rollback Decision

- Containment decision: `[execution-time fill-in]`
- Rollback trigger hit: `[execution-time fill-in: Y/N]`
- Rollback authority invoked by role: `[execution-time fill-in or N/A]`
- Rollback action executed: `[execution-time fill-in: Y/N]`
- If rollback not executed, reason: `[execution-time fill-in or N/A]`

## Final Disposition

- Final disposition: `[CONTAINED / ROLLED_BACK / HOLD_OPEN / ESCALATED]`
- Decision authority role: `[execution-time fill-in; must align to matrix rollback authority when rollback trigger is hit]`
- Decision timestamp (UTC): `[execution-time fill-in]`

## Follow-Up Item

| Follow-Up ID | Item | Owner Role | Due Checkpoint | Status |
|---|---|---|---|---|
| `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[OPEN/CLOSED]` |

## Required Evidence Sections

- Incident evidence pointer: `[execution-time fill-in]`
- Monitoring evidence pointer: `[execution-time fill-in]`
- Matrix authority evidence pointer: `[execution-time fill-in]`
- Rollback evidence pointer (if applicable): `[execution-time fill-in]`
