---
name: ledger-consulter-apps-qna-pack-lifecycle
description: Use this skill when changing or diagnosing apps_qna pack building, linting, route selection, paste-set selection, promotion, or interview-outcome behavior and relevant lifecycle precedent may affect the decision.
metadata:
  owner: apps-qna
  version: "2.0"
---

# apps_qna pack-lifecycle precedent

Consult `artifacts/ledgers/apps_qna_pack_lifecycle.sqlite` before a material lifecycle decision. The
ledger is contextual evidence, not an authority that overrides current tests, policy, or user intent.

## Workflow

1. Summarize the current decision in one task-specific sentence.
2. Query at most five relevant rows with a narrow event-kind filter.
3. Report whether the precedent is strong, suggestive, or absent.
4. State how the current evidence aligns with or departs from the precedent.
5. Record the final outcome through the owning writer path after the change is validated.

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("apps_qna_pack_lifecycle").lookup(
    query_text="<current apps_qna decision summary>",
    filters={"event_kind": "pack_build"},
    limit=5,
)
```

| Strength | Use |
|---|---|
| `strong` | Bias the decision only when current evidence remains compatible. |
| `suggestive` | Surface the pattern without automatically changing the plan. |
| `none` | State that the case is novel and proceed from current evidence. |

## References

- Reader API: `tools/ledgers/consulter.py`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.codex/schemas/apps_qna_pack_lifecycle_ledger.schema.sql`
- Writer integration: `apps_qna/builder/card_pack_builder.py`
