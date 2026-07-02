# apps_eval RG/LIC Hard Reset

Status: Completed
Created: 2026-06-13
Owner: Codex

## Objective

Hard-reset `apps_eval` into a clean deterministic evaluation harness for only
`apps_rg` and `apps_lic`.

## Operating Model

- `apps_eval` owns exam mechanics: fixtures, rubrics, deterministic graders,
  scorecards, baselines, sealed eval artifacts, and optional L6 handoff files.
- `apps_rg` and `apps_lic` are the product runtimes under test.
- L6 owns post-run learning, drift tracking, RCA, calibration workflow, and
  promotion/regret decisions.

## Non-Negotiables

- No active Agent, AgentSpec, reasoning orchestrator, planner, HOP, or
  PromotionLoop concepts remain in active `apps_eval`.
- No L0/L1/L2/L3/Exit runtime authority is owned by `apps_eval`.
- No L6 import, promotion gate call, regret decision, durable L4 write, or
  MetaLearningBus publish exists in the core harness path.
- Active registry contains only:
  - `apps_rg.dev.resume_generation`
  - `apps_rg.holdout.resume_generation`
  - `apps_lic.dev.outreach_message`
  - `apps_lic.holdout.outreach_message`
- Snapshot mode is the default. Live adapter mode is explicit and narrow.

## Plan

1. Quarantine old implementation under `apps_eval_legacy/`.
2. Rebuild active `apps_eval` around `contracts`, `registry`, `adapters`,
   `fixtures`, `rubrics`, `graders`, `runner`, `outputs`, and `tests`.
3. Move the two accepted rubrics into `apps_eval/rubrics/`.
4. Implement pure contracts, registries, fixture loading, deterministic graders,
   scorecard computation, regression comparison, artifact emission, and CLI.
5. Add CI gates for no agents, rg/lic scope, no runtime authority, holdout
   isolation, and record comparison.
6. Add focused package tests under `apps_eval/tests`.
7. Run the requested acceptance commands and repair failures.

## Verification

Acceptance commands from the user request are the completion contract.

Completed with bundled Python plus an isolated temp pytest target:

- `python ops_scripts/ci/check_apps_eval_no_agents.py`
- `python ops_scripts/ci/check_apps_eval_scope_rg_lic_only.py`
- `python ops_scripts/ci/check_apps_eval_no_runtime_authority.py`
- `python ops_scripts/ci/check_apps_eval_holdout_isolation.py`
- `pytest apps_eval/tests/test_registry_contracts.py`
- `pytest apps_eval/tests/test_fixture_contracts.py`
- `pytest apps_eval/tests/test_apps_rg_dev_suite.py`
- `pytest apps_eval/tests/test_apps_lic_dev_suite.py`
- `pytest apps_eval/tests/test_scorecard_determinism.py`
- `pytest apps_eval/tests/test_regression_engine.py`
- `pytest apps_eval/tests/test_l6_handoff_shape.py`
- `python -m apps_eval list-apps`
- `python -m apps_eval list-suites`
- `python -m apps_eval run --suite apps_rg.dev.resume_generation --mode snapshot --deterministic-only`
- `python -m apps_eval run --suite apps_lic.dev.outreach_message --mode snapshot --deterministic-only`

## Inspection Notes

Initial read-only inspection found the active package contains old scaffold:
`apps_eval/reasoning`, `EvalAgentSpecs`, `EvalOrchestrator`, HOP wrappers,
enterprise orchestration, L6 promotion imports, MetaLearningBus publishing, and
governed-run/Exit wiring. These are to be removed or quarantined from active
`apps_eval`.
