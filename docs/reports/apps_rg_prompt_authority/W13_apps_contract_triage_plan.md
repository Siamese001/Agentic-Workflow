# W13 — `tests/_apps_contract` full-suite triage plan (plan only)

## Goal

Provide a **classification and execution playbook** for running the entire `tests/_apps_contract` surface **without** fixing failures in this wave. No full suite was executed for W13.

## Canonical pytest command

From repo root, with plugin autoload disabled (repo norm):

```bat
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -p pytest_timeout tests/_apps_contract -q --tb=short
```

Optional first pass (collection smoke):

```bat
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -p pytest_timeout tests/_apps_contract --collect-only -q
```

## Known failing inventory (prior transcripts)

| Test module | Symptom class | Notes |
|-------------|----------------|-------|
| `test_apps_rg_prompt_bom_exists.py` | **Stale BOM/layout contract** | Expects `bom["app"] == "apps_rg"` but BOM uses `app_id`. Resolves template paths from repo root `templates/` instead of `apps_rg/prompt_assembly/templates/`. Imports `FLOW_ROUTE_TO_TEMPLATE` from `apps_rg.prompt_assembly.compiler` — symbol missing / moved. |

## Failure buckets (classify every failure into exactly one primary bucket)

1. **Prompt-authority regression** — W4–W11 contracts (registry, no-inline PA, ledger-only, X2/X1D) break.
2. **Stale BOM/layout contract** — BOM/YAML path assumptions, `app` vs `app_id`, template root drift.
3. **Route/profile drift** — L2 route maps, spine manifest, dispatch registry vs test expectations.
4. **Judge harness** — X1D / mock judge fixtures, rubric paths, diagnostic JSON shapes.
5. **Collection/setup** — import errors, missing fixtures, `PYTHONPATH`, optional deps.
6. **pytest/plugin environment** — duplicate plugins, autoload vs explicit `-p`, timeout/xdist conflicts.
7. **Fixture drift** — golden files, snapshot paths, artifact dirs renamed.
8. **Unrelated app contract failure** — tests for other apps under shared `_apps_contract` folder.

## W12 blocker vs W13-only

| If failure is… | Bucket | Blocks W12 “pure” claim? |
|----------------|--------|---------------------------|
| `test_apps_rg_prompt_bom_exists.py` (as known) | Stale BOM/layout | **W13-only** — does not negate PA compile or slice proofs unless BOM is promoted as SSOT gate for the same seams. |
| `test_apps_rg_prompt_registry_integrity.py` / no-inline / X2 alignment / ledger-only | Prompt-authority | **W12-relevant** — these are already green in scoped proof. |
| Import/collection failure in unrelated module | Collection/setup | **W13** until proven to hide a W12 seam. |
| Modified `agentic_core` in working tree | Out-of-scope churn | **W12 purity gate** — not a pytest failure, but blocks “no core diff” release story. |

## Recommended child plan (when full suite is requested)

1. Run collection-only; archive `collect_output.txt`.
2. Run full suite with `--maxfail=1` once to get first hard failure; then run by file clusters (`apps_rg` prompt tests, other apps, judge harness).
3. Fix order: **collection/import** → **BOM/layout parity** (`prompt_bom_exists`) → **prompt-authority** → **remaining**.
4. Re-run scoped W12 proof bundle after any `apps_rg` prompt touch.

## Explicit non-goals (this document)

- Do not “fix forward” `test_apps_rg_prompt_bom_exists.py` until explicitly promoted.
- Do not run full `tests/_apps_contract` in W13 unless requested.

## Status

**PASS** (plan-only deliverable).
