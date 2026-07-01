# ProceduralPattern:AppsRgX1DModelSsotLockdownInvariant

INVARIANT: Keep apps_rg proof-judge topology and model pins sourced from runtime SSOT modules, not copied into rollups, operator tools, env examples, or test fixtures.

scope: `apps_rg/runtime/section_judge_policy.py`, `apps_rg/config/provider_profiles.yaml`, `apps_rg/runtime/internal/generated_lane_rollup.py`, `tools/apps_rg/*.py`, `apps_research/config/domain_contract/provider_profile.company_brief.v1.yaml`, and targeting brief sidecars.

enforcement: `tests/unit/apps_rg/test_x1d_judge_transport_parity.py::test_rollup_and_operator_tools_do_not_restore_anthropic_proof_slot`; `tests/apps_research/engines/test_company_brief_engine.py::test_apps_research_active_contracts_do_not_restore_stale_model_pins`.

violation_examples: hardcoding `anthropic_claude` as an X1D proof judge for Claude-primary apps_rg sections; emitting `anthropic_provider_status` as a required rollup column; advertising `APPS_RESEARCH_BRIEF_MODEL` as an env model override; using `gemini-pro-3.1-preview` as a provider key.

canonical_pattern: import `REQUIRED_JUDGE_PROVIDER_KEYS` for proof-roster displays and operator commands; resolve apps_research company-brief synthesis model through `approved_model_lanes.primary` in `provider_profile.company_brief.v1.yaml`; use `judge_name=gemini_pro` and `judge_model=gemini-3.1-pro-preview`.

doctrine_ref: AGENTS.md Plan First / SSOT governance; discovered: 2026-07-01, validated: 2026-07-01.
