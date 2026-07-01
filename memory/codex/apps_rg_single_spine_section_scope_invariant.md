# apps_rg Single-Spine Section Scope Invariant

Protected memory type: ProceduralPattern

- name: `ProceduralPattern:AppsRgSingleSpineSectionScopeInvariant`
- entityType: `ProceduralPattern`

Observations:

- INVARIANT: apps_rg full and section resume-generation execution must enter through one core integrated single-action spine; apps_rg may customize U0 inputs and L2 recipe bodies, but must not own a parallel U0/L1/L0/L7 pipeline.
- scope: `apps_rg/runtime/orchestration/canonical_dispatch.py`, `apps_rg/runtime/spine/apps_rg_spine_run.py`, `apps_rg/l2_recipe/*`, `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`, and `agentic_core/runtime/l2_recipe_resolver.py`.
- enforcement: section scope sets `raw_request.execution_scope="section"` plus the apps_rg U0 `runtime_customization_package`, then calls `run_integrated_single_action_spine(app_name="apps_rg")`; core L2 resolves `scope_steps["section"]` to the app-owned `GenerateSectionStep`.
- violation_examples: dispatching section lanes directly from `apps_rg_spine_run`, emitting apps_rg-owned L7 HOW traces, or adding apps_rg literals/branches in core beyond the lazy recipe registry seam.
- canonical_pattern: `build_raw_request_for_r4()` attaches apps_rg U0 package fields; `run_apps_rg_spine(scope="section")` calls the core spine; `GenerateSectionStep` calls `run_registered_section_lane()` as the L2 body; X2/X3 remain apps_rg product validation while L7 remains core output.
- doctrine_ref: `AGENTS.md` Core vs apps summary; tests `_apps_contract/test_apps_rg_no_second_pipeline.py`, `_apps_contract/test_apps_rg_no_shadow_l7_emission.py`, and `tests/unit/apps_rg/test_single_action_spine_entrypoint.py`; validated 2026-07-01.
