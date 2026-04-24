---
name: ledger-consulter-hotspot-defect
description: Consult the hotspot_defect ledger for precedent before acting. Hotspot rank vs actual 30-day defect/churn; drives impact-formula coefficients. Inherits the contract from `ledger-consulter`. Use when Hotspot-first refactoring gate, impact-formula review, wave queue prioritization.
trigger: model_decision
---

# Ledger Consulter — hotspot_defect

## Purpose

Hotspot rank vs actual 30-day defect/churn; drives impact-formula coefficients.

Every row in `artifacts/ledgers/hotspot_defect.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

Hotspot-first refactoring gate, impact-formula review, wave queue prioritization.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("hotspot_defect").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "hotspot_prediction"},
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

- **Wave**: W3.1
- **Writer hook**: `ops_scripts/calibration/hotspot_defect_join.py`
- **Sunset criterion**: formula coefficients stable (no ADR change) for 2 consecutive quarters

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/hotspot_defect_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
