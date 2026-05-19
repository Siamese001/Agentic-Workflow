# Legacy dependency burndown — Phase C

**Plan:** [apps-rg-legacy-dependency-burndown-b7e4a2.md](../../.cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md)  
**Date:** 2026-05-19  
**Status:** PASS

## Goal

Route remaining safe `apps_eval` references to `Rg*` through `apps_shared` facades. No archive/delete, no `apps_rg/reasoning/*.py` edits, no product runtime behavior change.

## Orthogonal to Executive Summary session

Phase C is **unrelated** to the separate Cursor chat that ran and hardened `python -m apps_rg --section executive_summary` ([transcript 17c779f9-1065-4362-9bdf-dae0471e23c9](../../../.cursor/projects/c-Git-Agentic-Workflow-FRESH/agent-transcripts/17c779f9-1065-4362-9bdf-dae0471e23c9/17c779f9-1065-4362-9bdf-dae0471e23c9.jsonl)).

| Area | Executive Summary chat | Phase C (this receipt) |
|------|------------------------|-------------------------|
| Tree | `apps_rg` product runtime (`executive_summary` lane) | `apps_eval` evaluation framework only |
| Change type | Mandatory CLI inputs (fail-closed); live section proof | Config/doc strings + boundary test; no runtime behavior change |
| Facades | Not in scope | `rg_orchestrator_facade`, `rg_integrations_facade` import paths |
| `apps_rg/reasoning/*.py` | Unchanged in that session | Explicitly not edited in Phase C |

Phase C `orchestration_hop` eval scenarios still call `RgResumeOrchestrator` **via** `rg_orchestrator_facade` (eval harness only). That is not executive-summary generation and does not modify the exec-summary lane.

## Inventory (apps_eval)

| Surface | Before | After |
|---------|--------|-------|
| Direct `import apps_rg` / `from apps_rg` | 0 | 0 |
| `apps_rg.reasoning` module strings | 2 | 0 |
| `scenario_runner` orchestration | `rg_orchestrator_facade` | unchanged (already correct) |
| `narrative_judge_scorer` | `rg_integrations_facade` | unchanged (already correct) |
| `apps_eval/contracts/` | no Rg refs | no change |

## Migrated

1. [agent_spec_config.py](apps_eval/config/agent_spec_config.py) — `orchestration_hop.target_module` → `apps_shared.adapters.rg_orchestrator_facade`
2. [TECHNICAL_SPEC.md](apps_eval/TECHNICAL_SPEC.md) — scenario doc path → facade
3. [README.md](apps_eval/README.md) — benchmark suite table
4. [EvalOrchestrator.py](apps_eval/reasoning/EvalOrchestrator.py) — module docstring

## Regression guard

[test_w3_boundary_facades.py](tests/unit/apps_shared/adapters/test_w3_boundary_facades.py) — new `test_apps_eval_has_no_apps_rg_reasoning_module_strings` scans `apps_eval/**/*.py` for embedded `apps_rg.reasoning` paths.

## Retained legacy (intentional)

- `tests/unit/apps_rg/reasoning/test_rg_*.py` — direct legacy imports for Rg behavior contracts
- `tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py` — DO_NOT_DELETE path registry
- `apps_shared/adapters/rg_orchestrator_facade.py` — lazy bridge to `apps_rg.reasoning.RgResumeOrchestrator`

## Verification

| Command | Result |
|---------|--------|
| `python -m compileall agentic_core apps_rg apps_shared apps_eval -q` | exit 0 |
| `pytest tests/unit/apps_shared/adapters/test_w3_boundary_facades.py` | 19 passed |
| `pytest tests/unit/apps_rg/reasoning/ -k test_rg_` | 45 passed, 1 skipped |
| `pytest tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py tests/_apps_contract/test_apps_rg_canonical_runtime_hygiene.py` | 28 passed |

Machine-readable receipt: [legacy_dependency_burndown_phase_c.json](legacy_dependency_burndown_phase_c.json)

## Next

**Phase D:** Shrink `competencies_dispatch` / `ibm_narrative_dispatch` execution (quarantine wiring; no archive).
