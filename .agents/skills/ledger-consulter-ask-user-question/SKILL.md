---
name: "ledger-consulter-ask-user-question"
description: "|"
---

# Ledger Consulter — Ask User Question

## Ledger

- **Name**: `ask_user_question`
- **DB**: `artifacts/ledgers/ask_user_question.sqlite`
- **Purpose**: Track enriched_choice_builder decisions (recommendation vs selection, confidence calibration, UI invariant compliance) for the shadow learning loop.

## Trigger Features

Consult this ledger when:

- Building an `ask_user_question` payload via `enriched_choice_builder`
- The telemetry_context matches a context with prior decisions
- Confidence calibration analysis is needed (did past recommendations at similar confidence levels get accepted?)

## Minimal Query

```python
from tools.ledgers.consulter import AskUserQuestionConsulter

consulter = AskUserQuestionConsulter()
verdict = consulter.lookup(
    context="import-cycle",
    limit=5,
)
# verdict.strength in {"strong", "suggestive", "none"}
# verdict.matches includes recommendation vs selection data
# verdict.acceptance_rate = float (0.0–1.0)
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong` | Bias confidence scores toward historical acceptance patterns. Note alignment in telemetry packet. |
| `suggestive` | Surface acceptance rate in the enriched choice context but do not auto-adjust confidence. |
| `none` | State explicitly: "Precedent: no prior ask_user_question decisions for this context (novel case)." |

## Key Signals

- **Acceptance rate**: `selected_index == recommended_index` ratio — measures recommendation quality
- **Override rate**: Inverse of acceptance — signals confidence miscalibration
- **Confidence calibration**: Binned confidence vs acceptance rate — detects systematic over/under-confidence
- **Per-context patterns**: Some decision types may have structurally different acceptance rates

## References

- Writer: `tools/ledgers/ask_user_question_ledger.py`
- Builder: `tools/decisions/enriched_choice_builder.py`
- Dashboard: `tools/ledgers/telemetry_dashboard.py`
- Weekly report: `ops_scripts/calibration/ask_user_question_weekly_report.py`
- Parent skill: `.codex/skills/ledger-consulter/SKILL.md`

## MANUAL MIGRATION REQUIRED

Review unsupported Claude skill fields manually: `trigger`.
