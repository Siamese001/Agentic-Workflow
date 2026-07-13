---
name: ledger-consulter-ask-user-question
description: Use this skill when calibrating a material structured user choice from prior recommendation acceptance, override, and confidence patterns without allowing historical preference to replace current evidence.
metadata:
  owner: platform-team
  version: "2.0"
---

# User-choice precedent consultation

Use the `ask_user_question` ledger only for material choices where historical acceptance and override
patterns can improve confidence calibration. The ledger is read-only evidence during the decision.

## Workflow

1. Normalize the current decision to a stable context key.
2. Retrieve at most five comparable decisions.
3. Compare recommendation acceptance, override rate, confidence band, and decision context.
4. Adjust confidence only when the precedent is strong and current evidence is compatible.
5. State when no comparable precedent exists.

```python
from tools.ledgers.consulter import AskUserQuestionConsulter

verdict = AskUserQuestionConsulter().lookup(
    context="import-cycle",
    limit=5,
)
```

| Strength | Use |
|---|---|
| `strong` | Use the historical calibration as one input to the confidence value. |
| `suggestive` | Surface the acceptance pattern without automatically changing confidence. |
| `none` | State that the current choice is a novel context. |

## Guardrails

- Do not infer user preference from unrelated contexts.
- Do not ask a question solely because a ledger exists.
- Explicit current user direction overrides historical acceptance patterns.
- Safety and blast-radius evidence override popularity.

## References

- Reader: `tools/ledgers/consulter.py`
- Writer: `tools/ledgers/ask_user_question_ledger.py`
- Calibration helper: `tools/ledgers/ask_user_question_calibration.py`
- Dashboard: `tools/ledgers/telemetry_dashboard.py`
