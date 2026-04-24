---
name: ledger-consulter-memory-recall
description: Consult the memory_recall ledger for precedent before acting. Memory-MCP recalled entities vs session reference; shrinks context pollution. Inherits the contract from `ledger-consulter`. Use when Session-start recall weighting; before requesting mem_recall_session_start.
trigger: model_decision
---

# Ledger Consulter — memory_recall

## Purpose

Memory-MCP recalled entities vs session reference; shrinks context pollution.

Every row in `artifacts/ledgers/memory_recall.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

Session-start recall weighting; before requesting mem_recall_session_start.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("memory_recall").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "entity_recalled"},
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

- **Wave**: W4.3
- **Writer hook**: `.windsurf/scripts/post_cascade_writeback_audit.py`
- **Sunset criterion**: entity hit-rate ≥0.60 after 3 calibration rounds

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/memory_recall_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
