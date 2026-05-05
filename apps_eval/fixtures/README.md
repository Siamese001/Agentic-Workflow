# apps_eval Fixtures — Holdout vs Dev Contract

The directory contract that keeps holdout corpora **uncontaminated** so they remain a valid measurement of generalization, not a leaked test set.

## Directory Contract

- **`dev/`** — iterative evaluation corpus. Cascade and developers may add / modify / read freely during development.
- **`holdout/`** — **release-gate corpus. TOUCHED ONLY BY RELEASE-GATE CI.** Developers MUST NOT read, edit, or inspect holdout data during iterative work. Doing so contaminates it and collapses its value as a measure of true generalization.

## Why This Contract Exists

Anthropic + OpenAI eval best practice: a holdout set the developer has never seen is the only way to measure true generalization. Once a human looks at a holdout sample, that sample is no longer holdout.

The contract makes this **structural** rather than aspirational — `holdout/` is in `.codeiumignore`, fenced by directory tests, and reserved for release-gate paths only.

## Enforcement

- `tests/_apps_contract/test_w2_fixtures_scaffold.py` — asserts the directory structure exists.
- Future: pre-commit gate `check_holdout_isolation.py` blocks any diff that reads `holdout/` from a non-release-gate path.

## Adding Fixtures

### `dev/` — any time
Drop JSONL files with `{"input": ..., "expected": ...}` rows. No approval required.

### `holdout/` — release-gate only
Requires Author-Gate approval and an ADR. Do not add fixtures by hand during development.

## Current Status

Scaffold only. No fixtures authored yet — operators supply real corpus in a future plan.
