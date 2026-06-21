# apps_* Testing Model

Use this model when writing, changing, triaging, deleting, skipping, or
xfailing tests under app-owned test surfaces:

- `tests/_apps_contract/`
- `tests/apps_*/`
- `tests/unit/apps_*/`

Core rule:

```text
apps_* tests do not protect old app implementation.
apps_* tests protect governed product behavior.
```

An app test should answer whether the app enters the right governed path,
produces the right artifacts, preserves authority boundaries, and fails
honestly.

## Buckets

| Bucket | Protected claim | Fix target |
|---|---|---|
| LAW | No fake product proof, unauthorized X3, direct L4 write, fabrication, or bypass of required spine authority | App/runtime code |
| APP CONTRACT | Current CLI behavior, dispatch adapter, artifact schema, output contract, exit code, product result shape | App code or canonical adapter |
| SPINE BINDING | App routes through governed `agentic_core` path instead of local/private orchestration | App boundary code |
| EVAL CONTRACT | `apps_eval` grades completed app outputs and snapshots without mutating, rescuing, or promoting | `apps_eval` code |
| HARNESS | Pytest collection, eager imports, fixtures, env setup, path issues, Windows issues, stale run dirs | Test harness |
| MIGRATION | Refactor-era test with still-valid intent but stale assumptions | Rewrite or narrow around current contract |
| ARCHAEOLOGY | Old HOP/reasoning/agent paths, deleted modules, old artifact names, dead architecture | Delete, quarantine, skip, or rewrite |
| FUTURE | Desired behavior not yet part of current required contract | Strict xfail, skip allowlist, or backlog |

Aliases allowed by CI:

- `CONTRACT` -> `APP CONTRACT`
- `SPINE` -> `SPINE BINDING`
- `EVAL` -> `EVAL CONTRACT`

## Decision Questions

| Question | Bucket | Action |
|---|---|---|
| Does the test protect X3 authority, provenance, no fabrication, L4/UWG, or product-proof honesty? | LAW | Fix app/runtime code |
| Does the test verify current CLI, output, artifact schema, dispatch, or exit-code behavior? | APP CONTRACT | Fix app or adapter |
| Does the test prove the app uses the governed spine instead of private orchestration? | SPINE BINDING | Fix app boundary |
| Does the test ensure `apps_eval` only grades and does not mutate/rescue/promote? | EVAL CONTRACT | Fix `apps_eval` |
| Is the failure caused by imports, fixtures, env, stale paths, collection, or Windows behavior? | HARNESS | Fix test machinery |
| Was the test written during a refactor and still has a useful purpose? | MIGRATION | Rewrite around current contract |
| Does the test reference deleted app internals? | ARCHAEOLOGY | Quarantine, delete, skip, or rewrite |
| Is the behavior desired later but not required now? | FUTURE | Strict xfail, skip allowlist, or backlog |

## Test Marker

Every changed app-owned Python test file must include one marker near the top
of the file:

```python
# apps-test-model: LAW
```

or:

```python
"""apps-test-model: APP CONTRACT."""
```

Use exactly one of the canonical buckets unless an alias is listed above.

## APPS_TEST_TRIAGE

For T2/T3 work that changes app test behavior, include this evidence in the
plan or closeout:

```text
## APPS_TEST_TRIAGE
Bucket: LAW | APP CONTRACT | SPINE BINDING | EVAL CONTRACT | HARNESS | MIGRATION | ARCHAEOLOGY | FUTURE
Test claim: <observable governed behavior the test protects>
Protected contract: <CLI/output/artifact/spine/eval/failure contract>
Fix target: <app/runtime | app boundary | apps_eval | test harness | test rewrite | backlog>
Allowed remediation: <fix code | rewrite test | quarantine/delete | strict xfail/skip allowlist>
Evidence command: <pytest or CI gate command>
```

Do not change product behavior to satisfy HARNESS, MIGRATION, ARCHAEOLOGY, or
FUTURE failures. Do not weaken LAW, APP CONTRACT, SPINE BINDING, or EVAL
CONTRACT tests without a migration receipt.

## CI Gate

`ops_scripts/ci/check_apps_test_model.py` enforces marker presence and bucket
validity for changed app-owned test files. The gate is intentionally
changed-file scoped so it does not require all historical tests to be annotated
in one migration.
