---
name: "ledger-consulter-apps-qna-pack-lifecycle"
description: "Consult the apps_qna_pack_lifecycle ledger before changing apps_qna pack-build, lint, route-selection, paste-set, promotion, or interview-outcome behavior."
---

# Ledger Consulter - apps_qna_pack_lifecycle

## Ledger

- **Name**: `apps_qna_pack_lifecycle`
- **DB**: `artifacts/ledgers/apps_qna_pack_lifecycle.sqlite`
- **Purpose**: Track apps_qna pack build, lint, self-eval, route-select, paste-set, promotion, and interview-outcome decisions for cross-interview transfer and calibration.

## Trigger Features

Consult this ledger when:

- Changing `apps_qna` card pack build behavior.
- Changing likely-question route selection, paste-set selection, or promotion gates.
- Investigating pack-build regressions, paste-budget drift, or interview-outcome feedback.

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("apps_qna_pack_lifecycle").lookup(
    query_text="<current apps_qna decision summary>",
    filters={"event_kind": "pack_build"},
    limit=5,
)
```

## Verdict To Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong` | Bias current decision toward precedent; note alignment in the plan or handoff. |
| `suggestive` | Surface precedent as context, but do not auto-bias. |
| `none` | State explicitly: `Precedent: ledger had no match (novel case).` |

## References

- Base skill: `.claude/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.claude/schemas/apps_qna_pack_lifecycle_ledger.schema.sql`
- Writer hook: `apps_qna/builder/card_pack_builder.py`

## MANUAL MIGRATION REQUIRED

Review unsupported Claude skill fields manually: `trigger`.
