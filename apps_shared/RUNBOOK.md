# RUNBOOK — apps_shared

> **When to use this:** a shared utility regression cascaded into multiple domain apps.
> **Companion docs:** `SLO.md` · `SVP_ENGINEERING_REVIEW.md`
> **Owner:** see `CODEOWNERS`

## CRITICAL: Read This First

apps_shared is the L_SHARED infrastructure layer used by **every** apps_*. A regression here cascades to ALL consumers. Treat any apps_shared change with proportional caution.

## On-Call Decision Tree

```
Multiple apps_* are misbehaving in the same way
├── Did the same utility get used in all of them?
│   ├── YES → §1 Shared Utility Regression
│   └── NO  → unlikely apps_shared; investigate the apps individually
A single apps_* is failing in apps_shared utility code
├── Cache key non-determinism?
│   ├── YES → §2 Cache Determinism Failure (CRITICAL)
│   └── NO  → continue
├── Validation framework leak (invalid data passing)?
│   ├── YES → §3 Validator Leak (CRITICAL)
│   └── NO  → §4 Generic
```

## §1 Shared Utility Regression

**Symptom:** the same error pattern appears in 2+ apps simultaneously, traceable to a `from apps_shared.<x>` call.

**Triage:**
1. `git log -p apps_shared/<offending_file> --since='7 days ago'` — find the change.
2. Identify all `apps_*` consumers of that utility: `grep -r "from apps_shared.<x>" apps_*/` (this is allowed — text search of the import statement, not dep analysis).
3. Reproduce in the smallest consumer first.

**Mitigation:**
- Revert the apps_shared change FIRST.
- Re-test all affected apps.
- Add a regression test in `apps_shared/tests/` BEFORE re-attempting the change.

## §2 Cache Determinism Failure (CRITICAL)

**Symptom:** `cache_validator.compute_key()` returns different SHA-256 for the same logical input.

**Why critical:** every cache miss across every app trusts this utility. Non-determinism here means **stale cache hits AND missed reads** simultaneously across the platform.

**Triage:**
1. **Halt all caching** — set `CACHE_VALIDATOR_DETERMINISTIC_ASSERTION=1` to crash on any non-determinism (not just observe).
2. Bisect against the last 7 days.
3. Most likely cause: a dict was hashed in non-canonical order, OR a float was included unrounded.

**Mitigation:**
- Restore deterministic ordering (sort keys, canonicalize floats).
- Bump cache version (treat all prior cached values as stale).
- Add a determinism test against the offending input.

## §3 Validator Leak (CRITICAL)

**Symptom:** `validation_validator` accepts data that should have been rejected (downstream apps see invalid data).

**Why critical:** the validation framework is the foundation of every domain app's input contract.

**Triage:**
1. Identify the input that leaked through.
2. Reproduce in `apps_shared/tests/test_validators.py`.
3. Determine: signature gap (validator never knew about this case) or logic bug (validator ran but failed to reject)?

**Mitigation:**
- Add the failing case as a regression test.
- Fix the validator.
- Audit downstream apps for any decisions/outputs based on the leaked data.

## §4 Generic Investigation

1. Run apps_shared tests: `pytest apps_shared/tests/ -v`.
2. Check for new utility additions in last 7 days that don't have tests.
3. Verify W3 purity gate is passing: `python ops_scripts/ci/check_apps_shared_purity.py`.

## Rollback Procedure

apps_shared rollback is **highest blast radius** — touch with care.

1. **DRY-RUN first:** `git revert <commit> --no-commit` then `pytest apps_*/tests/` to surface impact.
2. If tests pass → commit revert and push.
3. If tests fail → the apps have already adapted; rollback would create a worse state. Investigate forward-fix instead.
4. Notify the owner of every affected app.

## Top-3 Failure Modes

1. **Cache determinism failure** → §2 (CRITICAL — silent stale data)
2. **Validator leak** → §3 (CRITICAL — invalid data downstream)
3. **Shared utility regression cascading** → §1 (most common operationally)

## Key Files

- `validators/cache_validator.py` — cache key generation
- `validators/validation_validator.py` — generic validation
- `tests/test_validators.py` — the line of defense
- `types/__init__.py` — type exports

## W3 Purity Gate

`apps_shared` MUST NOT import from any `apps_*/` (other than itself). The gate `ops_scripts/ci/check_apps_shared_purity.py` enforces this on every PR. If you're tempted to violate this, the right move is:

1. Move the apps-specific logic OUT of apps_shared.
2. Or, move the shared concern UP into `agentic_core/L*/`.

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **Owner of every apps_*:** see `CODEOWNERS` (apps_shared changes affect all of them)
