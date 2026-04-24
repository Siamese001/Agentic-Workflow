---
name: ledger-consulter-progress-eta
description: Consult the progress_eta ledger for precedent before acting. ProgressReporter predicted vs actual duration; calibrates subprocess timeouts. Inherits the contract from `ledger-consulter`. Use when ProgressReporter init for a named operation; subprocess timeout calibration.
trigger: model_decision
---

# Ledger Consulter — progress_eta

## Purpose

ProgressReporter predicted vs actual duration; calibrates subprocess timeouts.

Every row in `artifacts/ledgers/progress_eta.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

ProgressReporter init for a named operation; subprocess timeout calibration.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("progress_eta").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "eta_predicted"},
    limit=5,
)
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias current decision toward precedent; note alignment in packet/plan. |
| `suggestive`   | Surface precedent in Author-Gate packet or plan body; do not auto-bias. |
| `none`         | State explicitly: `Precedent: ledger had no match (novel case).` |

## Wave / Sunset

- **Wave**: W4.2
- **Writer hook**: `tools/progress_display.py`
- **Sunset criterion**: ETA overrun ratio within ±20% for 90 consecutive days

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/progress_eta_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
