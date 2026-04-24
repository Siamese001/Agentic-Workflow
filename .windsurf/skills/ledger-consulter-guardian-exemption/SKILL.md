---
name: ledger-consulter-guardian-exemption
description: Consult the guardian_exemption ledger for precedent before acting. Guardian-exemption lifecycle; RCA→exemption linkage for silent-failure attribution. Inherits the contract from `ledger-consulter`. Use when Any new '# guardian: allow-*' comment; before approving Author-Gate exemption.
trigger: model_decision
---

# Ledger Consulter — guardian_exemption

## Purpose

Guardian-exemption lifecycle; RCA→exemption linkage for silent-failure attribution.

Every row in `artifacts/ledgers/guardian_exemption.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

Any new '# guardian: allow-*' comment; before approving Author-Gate exemption.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("guardian_exemption").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "exemption_created"},
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

- **Wave**: W4.1
- **Writer hook**: `.windsurf/scripts/post_write_audit.py`
- **Sunset criterion**: zero exemption-attributed defects for 180 days

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/guardian_exemption_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
