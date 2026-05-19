# Legacy dependency burndown — Phase D

**Plan:** [apps-rg-legacy-dependency-burndown-b7e4a2.md](../../.cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md)  
**Date:** 2026-05-19  
**Status:** PARTIAL (scoped seam PASS; full-tree `pytest tests -k …` exits 1 on unrelated collection errors)

## Goal

Shrink `competencies_dispatch` / `ibm_narrative_dispatch` **execution** surfaces for future quarantine/archive. No archive/delete, no deprecation markers added, no runtime behavior change.

## Orthogonal to Executive Summary session

Phase D is **unrelated** to the separate Cursor chat that ran and hardened `python -m apps_rg --section executive_summary` ([transcript 17c779f9-1065-4362-9bdf-dae0471e23c9](../../../.cursor/projects/c-Git-Agentic-Workflow-FRESH/agent-transcripts/17c779f9-1065-4362-9bdf-dae0471e23c9/17c779f9-1065-4362-9bdf-dae0471e23c9.jsonl)).

| Area | Executive Summary chat | Phase D (this receipt) |
|------|------------------------|-------------------------|
| Sections | `executive_summary` only | `competencies`, `ibm_narrative` only |
| Modules touched | `executive_summary_lane`, `section_cli_defaults`, `canonical_dispatch` exec-summary branch | `*_dispatch` helpers + `*_lane_execution` |
| Behavior change | Yes — mandatory CLI inputs (fail-closed) | No — execution relocation only |
| Live proof | That session ran exec summary | Phase D explicitly did **not** run live proof |

Pre-existing cross-lane references remain unchanged (e.g. competencies companion context reads `executive_summary` L2 artifacts; shared `build_sentence_claim_coverage` import from `executive_summary_x2` validator). Those are not Executive Summary **execution** changes.

## DISPATCH_EXECUTION_MAP

### competencies

| Layer | Before | After |
|-------|--------|-------|
| E2E execution | [competencies_dispatch.py](apps_rg/runtime/dispatch/competencies_dispatch.py) `run_competencies_execution` (~667 LOC) | [competencies_lane_execution.py](apps_rg/runtime/sections/competencies_lane_execution.py) `run_competencies_lane_execution` |
| Dispatch module | ~2232 lines (helpers + execution + CLI) | ~1574 lines (**helpers +** `run_dispatch` + lazy PEP 562 re-export) |
| Canonical CLI | `python -m apps_rg --section competencies` → [competencies_lane.py](apps_rg/runtime/sections/competencies_lane.py) | unchanged |
| Legacy `-m …competencies_dispatch` | `exit_deprecated_dispatch_cli` | unchanged (exit 2) |

### ibm_narrative

| Layer | Before | After |
|-------|--------|-------|
| E2E execution | [ibm_narrative_dispatch.py](apps_rg/runtime/dispatch/ibm_narrative_dispatch.py) `run_ibm_narrative_execution` (~650 LOC) | [ibm_narrative_lane_execution.py](apps_rg/runtime/sections/ibm_narrative_lane_execution.py) `run_ibm_narrative_lane_execution` |
| Dispatch module | ~1288 lines | ~647 lines (helpers + lazy re-export + deprecated `__main__`) |
| Canonical CLI | `python -m apps_rg --section ibm_narrative` → [ibm_narrative_lane.py](apps_rg/runtime/sections/ibm_narrative_lane.py) | unchanged |
| Legacy `-m …ibm_narrative_dispatch` | `exit_deprecated_dispatch_cli` | unchanged |

## Implementation notes

- Lane execution modules **hydrate** helper symbols from dispatch on first `run_*_lane_execution` call (avoids import cycle).
- Dispatch modules use **`__getattr__`** lazy re-export of `run_*_execution` / `run_*_lane_execution` (no eager import of lane_execution at module load).
- Split automation: [phase_d_split_dispatch_execution.py](../../tools/cursor/phase_d_split_dispatch_execution.py)

## MIGRATED

- `run_competencies_lane_execution` body → sections SSOT
- `run_ibm_narrative_lane_execution` body → sections SSOT

## RETAINED_COMPAT

- Dispatch helper libraries (parse/repair/X2 prep, IBM metric trim, mock builders, etc.)
- `run_competencies_execution` / `run_ibm_narrative_execution` thin compat wrappers on lane_execution
- Contract tests that import repair helpers from dispatch (intentional)

## BLOCKERS

- **Helper extraction:** moving competencies repair helpers out of dispatch would ripple to `headline_lane` and multiple tests — deferred.
- **Full-tree pytest:** `pytest tests -k "competencies and …"` reports 52 unrelated collection errors with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`; scoped `_apps_contract` + `unit/apps_rg` paths pass.

## QUARANTINE_READINESS

| Module | Execution | Helpers | `__main__` | DELETE_GATE |
|--------|-----------|---------|------------|-------------|
| competencies_dispatch | removed (lazy re-export) | retained | deprecated exit 2 | **not ready** (fan-in) |
| ibm_narrative_dispatch | removed (lazy re-export) | retained | deprecated exit 2 | **not ready** (fan-in) |

Product path for proof: `python -m apps_rg --section <lane>` → `canonical_dispatch` → `*_lane_execution`.

## Verification

| Command | Result |
|---------|--------|
| `compileall agentic_core apps_rg apps_shared apps_eval` | exit 0 |
| `pytest … -k "competencies and (canonical or lane or x2 or x3)"` (scoped) | **59 passed**, 1 unrelated collection error |
| `pytest … -k "ibm_narrative and (canonical or lane or x2 or x3)"` (scoped) | **19 passed**, 1 unrelated collection error |
| `pytest test_apps_rg_deprecated_path_quarantine + canonical_runtime_hygiene` | **28 passed** |
| `test_lane_pa_helper_parity` + `test_competencies_canonical_lane_contract` | **27 passed** |

Machine-readable: [legacy_dependency_burndown_phase_d.json](legacy_dependency_burndown_phase_d.json)

## Next

**Phase E:** gated archive when fan-in zero and DELETE_GATE satisfied (dispatch helper library may need extraction first).
