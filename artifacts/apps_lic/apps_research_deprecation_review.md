# apps_lic apps_research deprecation review

## Scope

Review and hardening pass for `apps_lic` to remove the deprecated `apps_research` managed workflow support path from the live product spine.

## Findings

- `apps_lic/runtime/dispatch/canonical_dispatch.py` still documents the product spine as `U0 -> L1 -> L0 -> (R3R4 research) -> C0 -> PA -> L3 -> L2 -> Exit` and says R3R4 research uses `ManagedWorkflowDispatcher` before re-planning.
- `canonical_dispatch.py` still contains `_build_request_for_briefing`, `_research_bridge`, `_serialize_research_outcome`, and `_run_r3r4_research`; those functions import `apps_lic.integrations.managed_workflow_dispatcher` and bridge into deprecated `apps_research`.
- `build_cli_ingress_raw(... allow_research=True ...)` still sets `research_requirements.allow_research=True`, which can route the run into `R3R4_MANAGED_RESEARCH_THEN_DRAFT`.
- `apps_lic/config/domain_contract/l0_route_profile.outreach_message.v1.json` still allows `R3R4_MANAGED_RESEARCH_THEN_DRAFT` and describes an `L3 apps_research support` path.
- `apps_lic/integrations/apps_research_bridge.py` still imports `apps_research.integrations.governed_research_run` and `apps_research.types.research_types` in `_invoke_apps_research`.
- `apps_lic/integrations/managed_workflow_dispatcher.py` still models the deprecated L3 support workflow as a success-producing dispatcher.
- Governance tests still assert that the dispatcher/bridge are active and success-producing.

## Hardening plan

1. Make `canonical_dispatch.py` manual-brief / inline-context only: no R3R4 research dispatch, no managed research merge, and fail closed if a stale R3R4 route reaches dispatch.
2. Change CLI and ingress behavior so `--auto-research` / `allow_research=True` becomes a deprecated, disabled signal rather than a route to apps_research.
3. Update the L0 route profile to remove `R3R4_MANAGED_RESEARCH_THEN_DRAFT` from allowed families and mark it forbidden/deprecated.
4. Convert apps_lic research bridge/dispatcher modules into compatibility shims that always fail closed with `APPS_RESEARCH_DEPRECATED` and never import `apps_research`.
5. Replace active research workflow tests with deprecation/boundary tests.
6. Add a closeout receipt after changes.
