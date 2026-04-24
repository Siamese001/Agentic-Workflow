---
name: ledger-consulter-refactor-outcome
description: Consult the refactor_outcome ledger for precedent before acting. Predicted vs actual P-count delta per refactoring wave; rollback attribution. Inherits the contract from `ledger-consulter`. Use when Wave planning, refactor-scope Author-Gate decisions, hotspot queue ordering.
trigger: model_decision
---

# Ledger Consulter — refactor_outcome

## Purpose

Predicted vs actual P-count delta per refactoring wave; rollback attribution.

Every row in `artifacts/ledgers/refactor_outcome.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

Wave planning, refactor-scope Author-Gate decisions, hotspot queue ordering.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("refactor_outcome").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "wave_prediction"},
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

- **Wave**: W1.2
- **Writer hook**: `.windsurf/scripts/post_commit_outcome_binder.py`
- **Sunset criterion**: prediction accuracy ≥85% for 4 consecutive waves

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/refactor_outcome_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
