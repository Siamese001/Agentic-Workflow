# Incident and Rollback Decision Log

Create one entry per incident decision event.

## Entry Header

- Incident decision ID: `[fill-in]`
- Timestamp (UTC): `[fill-in]`
- Related rollout event: `[fill-in]`
- Related rollout unit: `[fill-in]`

## Incident Summary

- Incident summary: `[fill-in]`
- Affected surface cluster (from Wave I matrix): `[fill-in]`
- Severity: `[SEV-1 / SEV-2 / SEV-3]`

## Matrix Owner Path Used

- Primary role engaged: `[fill-in]`
- Secondary/escalation role engaged: `[fill-in]`
- Incident Commander role engaged: `[Y/N]`
- Matrix row reference: `[fill-in]`

## Containment and Rollback Decision

- Containment decision: `[fill-in]`
- Rollback trigger hit: `[Y/N]`
- Rollback authority invoked by role: `[fill-in or N/A]`
- Rollback action executed: `[Y/N]`
- If rollback not executed, reason: `[fill-in or N/A]`

## Final Disposition

- Final disposition: `[CONTAINED / ROLLED_BACK / HOLD_OPEN / ESCALATED]`
- Decision authority role: `[fill-in; must align to rollback authority role in docs/wave_i/owner_escalation_and_rollback_matrix.md when rollback trigger is hit]`
- Decision timestamp (UTC): `[fill-in]`

## Follow-Up Item

| Follow-Up ID | Item | Owner Role | Due Checkpoint | Status |
|---|---|---|---|---|
| `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[OPEN/CLOSED]` |

## Evidence Pointers

- Incident evidence pointer: `[fill-in]`
- Monitoring evidence pointer: `[fill-in]`
- Rollback evidence pointer (if applicable): `[fill-in]`
