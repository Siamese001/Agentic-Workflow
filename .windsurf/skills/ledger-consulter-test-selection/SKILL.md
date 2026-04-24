---
name: ledger-consulter-test-selection
description: Consult the test_selection ledger for precedent before acting. ADG-driven test triage precision/recall; actual regression coverage per change-set. Inherits the contract from `ledger-consulter`. Use when '/adg-test-triage-gate' invocation; selecting tests for a change-set.
trigger: model_decision
---

# Ledger Consulter — test_selection

## Purpose

ADG-driven test triage precision/recall; actual regression coverage per change-set.

Every row in `artifacts/ledgers/test_selection.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

'/adg-test-triage-gate' invocation; selecting tests for a change-set.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("test_selection").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "triage_selection"},
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

- **Wave**: W4.4
- **Writer hook**: `.windsurf/scripts/post_run_audit.py`
- **Sunset criterion**: triage recall ≥0.95 for 2 consecutive quarters

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/test_selection_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
