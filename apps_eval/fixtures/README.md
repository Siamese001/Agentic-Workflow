# apps_eval Fixtures — Holdout vs Dev Contract

Per plan `.windsurf/plans/apps-eval-harness-residual-a2d9c7.md` W2.

## Directory Contract

- `dev/` — iterative evaluation corpus. Cascade + developers may add/modify/read freely during development.
- `holdout/` — **release-gate corpus. TOUCHED ONLY BY RELEASE-GATE CI.** Developers MUST NOT read, edit, or inspect holdout data during iterative work; doing so contaminates it.

## Why This Contract Exists

Anthropic + OpenAI eval best practice: a holdout set that developers have never seen is the only way to measure true generalization. Once a human looks at a holdout sample, its value as a holdout collapses.

## Enforcement

- `tests/_apps_contract/test_w2_fixtures_scaffold.py` asserts the directory structure exists.
- Future: pre-commit gate `check_holdout_isolation.py` blocks any diff that reads `holdout/` from a non-release-gate path.

## Adding Fixtures

### dev/ (any time)
Drop JSONL files with `{"input": ..., "expected": ...}` rows. No approval required.

### holdout/ (release-gate only)
Requires Author-Gate approval and an ADR. Do not add fixtures by hand during development.

## Current Status

Scaffold only. No fixtures authored yet — operators supply real corpus in a future plan.
