# Hypercare Run Log

Use one row per checkpoint. Add additional rows for the same checkpoint if multiple incidents occur.

| Checkpoint | Timestamp (UTC) | Observation Summary | Incident ID (if any) | Severity (`SEV-1/2/3`) | Owner Role Engaged | Action Taken | Rollback Considered (`Y/N`) | Decision Status (`STABLE`/`HOLD`/`ESCALATED`) | Evidence Pointer |
|---|---|---|---|---|---|---|---|---|---|
| T0 | `[fill-in]` | `[fill-in]` | `[fill-in or N/A]` | `[fill-in or N/A]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` |
| T+15m | `[fill-in]` | `[fill-in]` | `[fill-in or N/A]` | `[fill-in or N/A]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` |
| T+60m | `[fill-in]` | `[fill-in]` | `[fill-in or N/A]` | `[fill-in or N/A]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` |
| T+24h | `[fill-in]` | `[fill-in]` | `[fill-in or N/A]` | `[fill-in or N/A]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` |
| T+48h | `[fill-in]` | `[fill-in]` | `[fill-in or N/A]` | `[fill-in or N/A]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` |
| T+72h | `[fill-in]` | `[fill-in]` | `[fill-in or N/A]` | `[fill-in or N/A]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` |
| T+7d | `[fill-in]` | `[fill-in]` | `[fill-in or N/A]` | `[fill-in or N/A]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` | `[fill-in]` |

## Checkpoint Completion Controls

- [ ] Every required checkpoint row has timestamp and decision status.
- [ ] Every incident entry includes severity, owner role, and action.
- [ ] Every rollback consideration is explicitly marked `Y` or `N`.
- [ ] Escalated decisions reference the corresponding incident/rollback decision record.
