---
name: ledger-consulter-prompt-classifier
description: Consult the prompt_classifier ledger for precedent before acting. T0/T1/T2/T3 prediction accuracy vs actual files-edited/lines/layers. Inherits the contract from `ledger-consulter`. Use when Prompt-tier prediction (T0/T1/T2/T3) in pre_prompt_classifier or SR_INTAKE.
trigger: model_decision
---

# Ledger Consulter — prompt_classifier

## Purpose

T0/T1/T2/T3 prediction accuracy vs actual files-edited/lines/layers.

Every row in `artifacts/ledgers/prompt_classifier.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

Prompt-tier prediction (T0/T1/T2/T3) in pre_prompt_classifier or SR_INTAKE.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("prompt_classifier").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "tier_prediction"},
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

- **Wave**: W2.1
- **Writer hook**: `.windsurf/scripts/pre_prompt_classifier.py`
- **Sunset criterion**: classifier F1 ≥0.90 across all tiers for 30 consecutive days

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/prompt_classifier_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
