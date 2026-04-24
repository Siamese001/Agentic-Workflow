---
name: ledger-consulter-tool-routing
description: Consult the tool_routing ledger for precedent before acting. Retrieval-tool choice precision/recall; which query features → which tool. Inherits the contract from `ledger-consulter`. Use when Any retrieval-class tool dispatch (grep, ADG query, semantic search, read_file).
trigger: model_decision
---

# Ledger Consulter — tool_routing

## Purpose

Retrieval-tool choice precision/recall; which query features → which tool.

Every row in `artifacts/ledgers/tool_routing.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

Any retrieval-class tool dispatch (grep, ADG query, semantic search, read_file).

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("tool_routing").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "retrieval_tool_choice"},
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

- **Wave**: W1.1
- **Writer hook**: `.windsurf/scripts/post_cascade_adg_audit.py`
- **Sunset criterion**: grep-for-deps violation rate under 1% for 90 consecutive days

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/tool_routing_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
