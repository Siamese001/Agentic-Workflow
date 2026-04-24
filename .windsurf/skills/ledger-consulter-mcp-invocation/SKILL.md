---
name: ledger-consulter-mcp-invocation
description: Consult the mcp_invocation ledger for precedent before acting. Per-MCP-server latency, retries, hang attribution; drives SLO. Inherits the contract from `ledger-consulter`. Use when Before any mcp* tool call on a latency-sensitive path (e.g., inside a hook).
trigger: model_decision
---

# Ledger Consulter — mcp_invocation

## Purpose

Per-MCP-server latency, retries, hang attribution; drives SLO.

Every row in `artifacts/ledgers/mcp_invocation.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

Before any mcp* tool call on a latency-sensitive path (e.g., inside a hook).

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("mcp_invocation").lookup(
    query_text="<current intent summary>",
    filters={"event_kind": "mcp_call"},
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

- **Wave**: W2.2
- **Writer hook**: `.windsurf/scripts/post_mcp_audit.py`
- **Sunset criterion**: upstream anthropics/claude-agent-sdk-typescript#41 closed AND p95 latency stable 30d

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/mcp_invocation_ledger.schema.sql`
- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
