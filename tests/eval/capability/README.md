# Capability Eval Suite (LJH5.2)

Anthropic 'Demystifying evals for AI agents':

> Capability or "quality" evals ask "What can this agent do well?" They
> should start at a **low pass rate**, targeting tasks the agent
> struggles with and giving teams a hill to climb.

## Scope

Tasks the system currently **struggles** with. Accept failures. Track
trend (pass@1, pass@3, pass^3 from ``agentic_core.evaluation.metrics.stability``)
over time to measure capability hill-climbing.

## What NOT to Put Here

- Anything the system already solves reliably (≥98% pass@1) — that's
  regression (see ``tests/eval/regression/``). Promote items here into
  ``tests/eval/regression/`` once they're stable.
- Items from ``data/eval/golden/`` — those calibrate the judge itself,
  not the system under test.

## Runner

```bash
pytest tests/eval/capability -m eval_capability \
  --pass-at-k=3 \
  --report=artifacts/eval/capability_report.json
```
