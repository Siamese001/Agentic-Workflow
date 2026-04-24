---
name: ledger-consulter-deferred-scope-calibration
description: Consult the deferred_scope_calibration ledger for precedent before acting. Computed P-band vs actual days-to-done for Wave/Phase rows; tunes scorer thresholds. Inherits the contract from `ledger-consulter`. Use when DEFERRED_SCOPE marker emission, P-band assignment, scorer tuning.
trigger: model_decision
---

# Ledger Consulter — deferred_scope_calibration

## Purpose

Computed P-band vs actual days-to-done for Wave/Phase rows; tunes scorer thresholds.

Every row in `artifacts/ledgers/deferred_scope_calibration.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

DEFERRED_SCOPE marker emission, P-band assignment, scorer tuning.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("deferred_scope_calibration").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "deferred_scope_capture"},
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

- **Wave**: W3.2
- **Writer hook**: `ops_scripts/calibration/deferred_scope_poller.py`
- **Sunset criterion**: band-threshold drift under 5% for 2 consecutive quarters

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/deferred_scope_calibration_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
