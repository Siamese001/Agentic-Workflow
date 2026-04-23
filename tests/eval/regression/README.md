# Regression Eval Suite (LJH5.2)

Anthropic 'Demystifying evals for AI agents':

> Regression evals ask "Does the agent still handle all the tasks it
> used to?" and should have a **nearly 100% pass rate**. They protect
> against backsliding.

## Scope

Tasks the system solves reliably today (≥98% pass@1 in three consecutive
capability runs). Any decline below that threshold is a BLOCKER.

## What NOT to Put Here

- Anything flaky or aspirational — that's capability (see
  ``tests/eval/capability/``).
- Judge-calibration items — those live in ``data/eval/golden/``.

## Runner

```bash
pytest tests/eval/regression -m eval_regression \
  --pass-at-k=1 \
  --fail-under=0.98 \
  --report=artifacts/eval/regression_report.json
```

A drop below ``--fail-under`` must block the release gate.
