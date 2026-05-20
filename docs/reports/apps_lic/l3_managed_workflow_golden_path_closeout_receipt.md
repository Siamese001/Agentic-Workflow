# apps_lic L3 managed-workflow golden-path advisory — closeout

**Date:** 2026-05-20  
**Scope:** Rebaseline `l3_participates_for_managed_workflow` in AG-8 golden-path CI only. No binding migration, no shadow deletion, no dispatch forks.

## Root cause

The advisory failed because the runtime check omitted L0 routing inputs that the route profile requires:

- `context_signals` → L1 `task_spec` freshness fields (`briefing_fresh`, `lead_profile_valid`, `context_grounded`)
- Without them, L0 selected `R5_FALLBACK` → `execution_form=terminal_fallback` (correct fail-closed behavior, stale assertion)

Runtime bindings were already correct; the CI probe did not match [test_ag8_apps_lic_golden_path.py](tests/_apps_contract/test_ag8_apps_lic_golden_path.py) / [l0_route_profile.outreach_message.v1.json](apps_lic/config/domain_contract/l0_route_profile.outreach_message.v1.json) semantics.

## Fix

[check_apps_lic_golden_path_runtime.py](ops_scripts/ci/check_apps_lic_golden_path_runtime.py):

- `_managed_workflow_route_contract()` — U0→L1→L0 with `context_signals` on `ValidatedRequest.app_payload`
- **R4 path:** fresh context → `R4_MANAGED_DRAFT` + `managed_workflow` + `l3_required`
- **R3R4 path:** stale context + post-U0 `allow_research` on `app_payload` → `R3R4_MANAGED_RESEARCH_THEN_DRAFT` + `managed_workflow`
- **L3 handoff proof:** `c0_retrieve_apps_lic` → `pa_compose_apps_lic` → `l3_orchestrate_apps_lic` returns receipt + step (canonical L2/HOP boundary)

No changes to [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) or binding modules.
