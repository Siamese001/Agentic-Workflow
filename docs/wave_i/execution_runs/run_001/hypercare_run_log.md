# Hypercare Run Log — Run 001

Use one row per required checkpoint. Add additional rows for repeated incidents at the same checkpoint.

## Required Checkpoints

`T0`, `T+15m`, `T+60m`, `T+24h`, `T+48h`, `T+72h`, `T+7d`

## Allowed Decision States

- `STABLE`
- `HOLD`
- `ESCALATED`

## Checkpoint Log

| Checkpoint | Timestamp (UTC) | Observation Summary | Incident ID (if any) | Severity (`SEV-1/2/3`) | Owner Role Engaged | Action Taken | Rollback Considered (`Y/N`) | Decision Status (`STABLE`/`HOLD`/`ESCALATED`) | Evidence Pointer |
|---|---|---|---|---|---|---|---|---|---|
| T0 | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` |
| T+15m | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` |
| T+60m | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` |
| T+24h | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` |
| T+48h | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` |
| T+72h | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` |
| T+7d | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in or N/A]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` | `[execution-time fill-in]` |

## Field Expectations

- Every row must include timestamp and decision status.
- Every incident entry must include severity, engaged owner role, and action.
- Every rollback consideration must be explicitly `Y` or `N`.
- Any `HOLD` or `ESCALATED` row must point to `incident_and_rollback_decision_log.md`.
