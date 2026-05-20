# W11-M3A + M4A — Facade and dispatch PA migration receipt

**Generated:** 2026-05-19  
**Status:** PASS (required suites); PRE_EXISTING_FAILURE in optional W3 apps_eval scan

---

## M3_RG_FACADE_MIGRATION

| Field | Detail |
|-------|--------|
| **refs_before** | Facade lazy-exported only `RgResumeOrchestrator` → `apps_rg.reasoning`; no canonical surface on facade |
| **refs_after** | Facade adds `run_canonical_apps_rg_from_cli_primitives` + `CANONICAL_*` metadata; legacy `RgResumeOrchestrator` retained |
| **migrated** | [rg_orchestrator_facade.py](../../apps_shared/adapters/rg_orchestrator_facade.py), [integrations mirror](../../apps_shared/integrations/adapters/rg_orchestrator_facade.py), [test_w3_boundary_facades.py](../../tests/unit/apps_shared/adapters/test_w3_boundary_facades.py), [test_contracts_smoke.py](../../agentic_core/runtime/contracts/tests/test_contracts_smoke.py) deny-path string → `apps_rg.reasoning.RgResumeOrchestrator` |
| **retained_legacy** | `apps_eval/engines/scenario_runner.py` still uses `RgResumeOrchestrator` via facade (eval parity); all `tests/unit/apps_rg/reasoning/*` unchanged |
| **blockers** | Unit tests still import `apps_rg.reasoning.Rg*` directly; `apps_eval/engines/narrative_judge_scorer.py` has direct `apps_rg` imports (pre-existing W3 violation) |
| **archive_readiness** | NO — Rg* modules retained; facade now documents canonical path for new callers |

## M4_DISPATCH_PA_EXTRACTION

| Field | Detail |
|-------|--------|
| **lane_dispatch_pa_map** | [w11_lane_dispatch_pa_map.md](w11_lane_dispatch_pa_map.md) |
| **helpers_extracted** | `attach_reasoning_to_prompt_trace`, `collect_employment_bullets` → `apps_rg/runtime/sections/` |
| **compatibility_refs_retained** | Dispatch modules re-export; tests may still import from `apps_rg.runtime.dispatch.*` |
| **tests** | [test_lane_pa_helper_parity.py](../../tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py) (2 passed); contract quarantine (39 passed) |
| **blockers** | Per-lane `*_pa.py` compile modules still under `dispatch/`; `competencies_lane` still delegates execution to `competencies_dispatch` |
| **archive_readiness** | NO — dispatch package still required for PA compile and lane execution |

---

## Commands

| Command | Exit |
|---------|-----|
| `python -m compileall agentic_core apps_rg apps_shared -q` | 0 |
| `_w11_fanin_scan.py` / `_w11_adg_expand.py` / `_w11_remaining_candidates_prep.py` | 0 |
| Rg* + parity + W3 facade tests (46 collected) | 1 (1 pre-existing) |
| Contract hygiene (39) | 0 |
| L2 orchestration (8) | 0 |

**Pre-existing:** `test_apps_eval_has_no_direct_apps_rg_imports` — `apps_eval/engines/narrative_judge_scorer.py` (not in M3A scope).

---

## Updated counts

| Metric | Value |
|--------|------:|
| archived | 1 |
| delete_ready | 0 |
| archive_ready | 0 |
| migration_required | 8 |
| blocked | 11 |

**Blocker reduction (qualitative):** section lanes no longer import trace/bullet helpers from dispatch; facade exposes canonical dispatch for new cross-app callers.

---

## Explicit non-claims

- no files deleted
- no archive moves
- no deprecation markers added
- no product runtime behavior changed (re-exports preserve object identity)
- no X2/X3 weakened
- no live apps_rg proof run
- Rg* modules not removed
