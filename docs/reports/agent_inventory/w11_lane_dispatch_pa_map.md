# W11 — Section lane ↔ dispatch PA import map

**Generated:** 2026-05-19 (M4A + M4B)  
**Purpose:** Track SSOT vs compatibility re-exports after PA extraction to `apps_rg/runtime/sections/`.

## SSOT: `apps_rg/runtime/sections/`

| Module | Primary symbols | Dispatch compat re-export |
|--------|-----------------|-------------------------|
| [prompt_trace_reasoning.py](../../apps_rg/runtime/sections/prompt_trace_reasoning.py) | `attach_reasoning_to_prompt_trace` | [dispatch/prompt_trace_reasoning.py](../../apps_rg/runtime/dispatch/prompt_trace_reasoning.py) |
| [resume_employment_bullets.py](../../apps_rg/runtime/sections/resume_employment_bullets.py) | `collect_employment_bullets` | [competencies_dispatch.py](../../apps_rg/runtime/sections/competencies_lane_api.py) |
| [headline_pa.py](../../apps_rg/runtime/sections/headline_pa.py) | `compile_headline_prompt` | [dispatch/headline_pa.py](../../apps_rg/runtime/dispatch/headline_pa.py) |
| [competencies_pa.py](../../apps_rg/runtime/sections/competencies_pa.py) | `compile_competencies_prompt` | [dispatch/competencies_pa.py](../../apps_rg/runtime/dispatch/competencies_pa.py) |
| [ibm_bullets_pa.py](../../apps_rg/runtime/sections/ibm_bullets_pa.py) | `compile_ibm_bullets_prompt` | [dispatch/ibm_bullets_pa.py](../../apps_rg/runtime/dispatch/ibm_bullets_pa.py) |
| [ibm_narrative_pa.py](../../apps_rg/runtime/sections/ibm_narrative_pa.py) | `compile_ibm_narrative_prompt` | [dispatch/ibm_narrative_pa.py](../../apps_rg/runtime/dispatch/ibm_narrative_pa.py) |
| [unify_bullets_pa.py](../../apps_rg/runtime/sections/unify_bullets_pa.py) | `compile_unify_bullets_prompt` | [dispatch/unify_bullets_pa.py](../../apps_rg/runtime/dispatch/unify_bullets_pa.py) |
| [unify_narrative_pa.py](../../apps_rg/runtime/sections/unify_narrative_pa.py) | `compile_unify_narrative_prompt` | [dispatch/unify_narrative_pa.py](../../apps_rg/runtime/dispatch/unify_narrative_pa.py) |
| [executive_summary_pa.py](../../apps_rg/runtime/sections/executive_summary_pa.py) | `compile_executive_summary_prompt` | [dispatch/executive_summary_pa.py](../../apps_rg/runtime/dispatch/executive_summary_pa.py) |

**Compiler spine (unchanged):** [section_prompt_adapter.py](../../apps_rg/runtime/bindings/section_prompt_adapter.py) — `compile_section_prompt`

## Lane imports (post-M4B)

| Lane | PA compile import | Execution / helpers |
|------|-------------------|---------------------|
| [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py) | `sections.executive_summary_pa` | sections trace/bullets |
| [headline_lane.py](../../apps_rg/runtime/sections/headline_lane.py) | `sections.headline_pa` | sections trace/bullets |
| [ibm_bullets_lane.py](../../apps_rg/runtime/sections/ibm_bullets_lane.py) | `sections.ibm_bullets_pa` | sections bullets (lazy) |
| [unify_bullets_lane.py](../../apps_rg/runtime/sections/unify_bullets_lane.py) | `sections.unify_bullets_pa` | sections trace/bullets |
| [unify_narrative_lane.py](../../apps_rg/runtime/sections/unify_narrative_lane.py) | `sections.unify_narrative_pa` | sections trace/bullets |
| [competencies_lane.py](../../apps_rg/runtime/sections/competencies_lane.py) | via dispatch execution path | [competencies_lane_execution.py](../../apps_rg/runtime/sections/competencies_lane_execution.py) → `competencies_dispatch.run_competencies_execution` |
| [ibm_narrative_lane.py](../../apps_rg/runtime/sections/ibm_narrative_lane.py) | via `ibm_narrative_dispatch` | dispatch execution (not extracted) |

## Still on `apps_rg/runtime/dispatch/` (execution — next waves)

| Module | Role | Blocker |
|--------|------|---------|
| `competencies_dispatch.py` | Full competencies runtime + shared helpers | ~1.8k lines; lane execution delegates here |
| `ibm_narrative_dispatch.py` | IBM narrative runtime | Lane wiring + PA compile |
| `*_dispatch.py` CLIs | Retired entrypoints | Quarantine tests only |

## M4C competencies surface

```
competencies_lane.run_competencies_lane_execution
  → competencies_lane_execution (trace_runtime_path=sections.competencies_lane)
    → competencies_dispatch.run_competencies_execution
```

## Parity proof

[test_lane_pa_helper_parity.py](../../tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py) — dispatch `compile_*` and helper re-exports are **identical objects** to sections SSOT.

## apps_eval boundary (M3B)

| Consumer | Import path |
|----------|-------------|
| narrative_judge_scorer | `apps_shared.adapters.rg_integrations_facade` |
| scenario_runner | `apps_shared.adapters.rg_orchestrator_facade` (RgResumeOrchestrator retained) |
