# apps_rg L2 E1-E5 Gap Inventory - 2026-07-05

This inventory records the Wave 0 baseline for plan `apps-rg-l2-e1-e5-best-practice-closeout-9d2a31`.

## Evidence Status

- User approved the adjusted plan on 2026-07-05.
- User requested an ADG checkpoint bypass. This report treats that bypass as limited to non-structural plan/report scaffolding only.
- ADG MCP remains blocked for structural implementation: `mcp__adg_sqlite.adg_health` and `mcp__adg_sqlite.adg_reopen_connections` both returned `Transport closed`.
- `python scripts/governance/codex_readiness.py --json` failed with required MCP route failures for memory, GitKraken, adg_sqlite, and vector_db. The ADG route was `EXPOSED_BLOCKED` with `closed_transport`.
- DEGRADED_FALLBACK: reason=ADG_MCP_TRANSPORT_CLOSED; scope=inventory_report_only; no production/test implementation edits were made from degraded evidence.

## Current Git/Workspace Baseline

- Primary checkout: `C:\Git\Agentic-Workflow-FRESH`
- Branch: `main`
- Tracking: `main...origin/main [ahead 3]`
- Existing untracked files before this inventory:
  - `docs/reports/codex/codex_mcp_transport_http_migration_f7b2a9.json`
  - `docs/reports/codex/codex_mcp_transport_http_migration_f7b2a9.md`
  - `plans/apps-rg-l0-routing-only-a4c9e2.md`
  - `plans/codex-mcp-http-transport-hardening-f7b2a9.md`

## Files Inspected

- `apps_rg/runtime/bindings/l2_binding_adapter.py`
- `apps_rg/runtime/bindings/l2_envelope_adapter.py`
- `apps_rg/runtime/bindings/l2_envelope_contracts.py`
- `apps_rg/runtime/spine/governed_l2_exit_compose.py`
- `apps_rg/runtime/section_l2_lane_integration.py`
- `apps_rg/runtime/section_l2_spine_receipt.py`
- `apps_rg/runtime/spine/l2_handoff_receipt.py`
- `ops_scripts/ci/check_apps_rg_l2_v4_envelope.py`
- `apps_eval/registries/apps_rg_lane_contract.json`
- `tests/_apps_contract/test_apps_rg_l2_envelope.py`
- `tests/_apps_contract/test_apps_rg_one_pipeline_e2e.py`
- `tests/unit/apps_rg/test_one_spine_l2_receipt_w5b.py`

## Baseline Findings

### 1. Product-visible bridge is still optional/flag-driven

`apps_rg/runtime/bindings/l2_binding_adapter.py` has `_use_v4_l2_envelope()` gated on `APPS_RG_L2_USE_V4_ENVELOPE=1`.

Current `_l2_execute_apps_rg_core()` order:

1. `APPS_RG_L2_FORCE_STUB=1` returns a stub sealed artifact.
2. `APPS_RG_L2_USE_V4_ENVELOPE=1` calls `run_apps_rg_l2_envelope()`.
3. Otherwise the legacy package-driven path returns `_stub_sealed_from_prompt()`.

Risk: governed/product-visible `l2_execute_apps_rg()` can still route to stub/package behavior instead of canonical v4 envelope by default.

### 2. Stub fallback can still produce a sealed artifact shape

`_stub_sealed_from_prompt()` returns `SealedL2Artifact` with `execution_status="completed_stub_fallback"` and inert write-authority fields.

Risk: even if write authority remains false, a product-visible path needs to prevent a stub artifact from being mistaken for canonical L2 proof.

### 3. E1 can synthesize route/request authority from CPA-only input

`apps_rg/runtime/bindings/l2_envelope_adapter.py` has `_synth_route_and_vr_from_prompt_artifact()`, which creates:

- `route_id="R3_SIMPLE_GROUNDED_READ"`
- request/run/app/trace/tenant fields copied from the CPA
- a minimal validated-request namespace

Risk: product mode can create missing authority internally instead of rejecting missing route/work-order authority before E3.

### 4. E1 determinism is not deterministic enough

`_build_determinism_bundle()` derives hashes from CPA fields, but `attempt_seed` is `uuid.uuid4()`.

Risk: same packet and same attempt number cannot be replay-proven by seed equality.

### 5. E2 validation is too narrow for the target contract

`_validate_work_order()` currently checks replay key, compilation hash, target model, max tokens, allowed model membership, and prep readiness. It emits an `ApprovedWorkOrder` on pass.

Target gaps:

- route or L3 step identity validation
- signature/hash chain validation
- capability token validation
- sandbox envelope validation
- side-effect class validation
- L5/final evidence contract reference validation
- explicit runtime gate refs G11/G12/G13/G15/G19/G20
- UNKNOWN-as-FAIL semantics

### 6. E3 is model-lane oriented and needs a lane dispatcher fence

The adapter imports `ProviderGateway` and has provider resolution/run-mode logic. The target contract requires an explicit lane dispatcher where MODEL is wired via `ProviderGateway.invoke`, while READ_ANALYSIS, TOOL, ACTION, ARTIFACT, and PTC fail closed unless implemented.

Risk: lane semantics are implicit rather than a decisive E3 unsupported-lane proof.

### 7. Provider aliases and live-required authenticity need explicit closure

Observed provider handling includes external/live and stub modes. The target asks for normalized aliases:

- `external_claude` / `anthropic` / `claude` -> Anthropic
- `external_openai` / `openai` / `gpt` / `azure_openai` -> OpenAI
- `external_gemini` / `google_gemini` / `gemini` / `google` -> Google

Risk: local/stub aliases must fail in live-required mode, not downgrade to allowed test behavior.

### 8. E4 repair currently mutates prompt authority

`_apply_heal_repair_patch()` appends bounded repair context to `user_instruction`, appends a `PromptBlock(role="system", ...)`, and recomputes `compilation_hash`.

This conflicts with the new target:

- stop mutating user instruction and system prompt blocks
- represent repair as separate H0 repair context / repair invocation patch
- preserve policy, blueprint, capability token, sandbox envelope, prompt hash, replay key, source snapshot, and evidence refs

### 9. Unknown repair causes can fall to JSON repair

`_heal_attempt_failure()` picks `json_repair_intact_source` in the final `else` branch for soft-repairable attempts.

Risk: unknown causes are silently treated as JSON repair instead of `NEEDS_HELP` or terminal failure.

### 10. E5 seal digest coverage is too small

`_seal_digest_hex()` currently covers request/run/trace, prep receipt ID, validation packet ID, attempt receipt ID, and compilation hash.

Target digest must also cover route/step, prompt hash, policy hash, blueprint hash, replay key, output digest, proposed state diff digest, local check digest, receipt hashes, provider/model refs, and evidence refs.

### 11. Receipt bundle persistence is missing

No separate `l2_receipt_bundle.json` persistence was confirmed in the inspected adapter. Current `SealedL2Artifact` audit refs include prep/validation/attempt/heal refs, but not a complete persisted receipt bundle.

Target files:

- `prep_receipt.json`
- `validation_receipt.json`
- `attempt_receipt.json`
- `heal_receipt.json` when used
- `seal_receipt.json`
- `l2_receipt_bundle.json`

### 12. Section lanes still use compatibility mirror artifacts

`apps_rg/runtime/section_l2_lane_integration.py` currently calls:

- `build_l2_execution_packet_for_section()`
- `emit_l2_execution_packet_artifact()`
- `emit_section_l2_spine_receipt_artifacts()`
- section X3 finalization after sealed L2 mirror output

Risk: product-visible section provider calls need canonical E1/E2 approval before provider execution, with section artifacts derived from canonical receipt bundles.

### 13. apps_eval lane contract does not yet require canonical L2 roles

`apps_eval/registries/apps_rg_lane_contract.json` currently requires L2 roles:

- `lane_l2_output`
- `lane_runtime_payload`

Target required L2 roles:

- `l2_execution_packet`
- `prep_receipt`
- `validation_receipt`
- `attempt_receipt`
- `seal_receipt`
- `l2_receipt_bundle`
- `sealed_l2_artifact`
- `heal_receipt` only when retry/heal path is used

### 14. CI gate is advisory by default

`ops_scripts/ci/check_apps_rg_l2_v4_envelope.py` exits 0 on failures unless `APPS_RG_L2_V4_ENVELOPE_FAIL_CLOSED=1`.

Target: fail closed by default, with explicit `APPS_RG_L2_V4_ENVELOPE_ADVISORY=1` override.

## Baseline Acceptance Commands

These are the Wave 0 no-code-change baseline commands from the user grounding:

```bash
python -m pytest tests/_apps_contract/test_apps_rg_l2_envelope.py --collect-only -q
python ops_scripts/ci/check_apps_rg_l2_v4_envelope.py
```

Results from this run:

- `python -m pytest tests/_apps_contract/test_apps_rg_l2_envelope.py --collect-only -q` exited 0 and collected 144 tests.
- `python -m pytest tests/_apps_contract/test_apps_rg_l2_envelope.py -q --tb=short` exited 1: 142 passed, 2 failed.
- `python ops_scripts/ci/check_apps_rg_l2_v4_envelope.py` exited 0 only because advisory mode is the default, but its final verdict was FAIL: 4 checks passed, 3 failed.
- Direct `python -m pytest tests/_apps_contract/ --collect-only -q` exited 1 after collecting 7266 items, with one collection error in `tests/_apps_contract/test_exec_summary_cli.py`.

Focused L2 failures:

1. `TestE1FrozenExecutionContext::test_e1_fec_uses_safe_defaults_for_missing_fields`
   - Expected provider lane: `local_local_model_server`
   - Actual provider lane: `external_claude`
2. `TestW7BFeatureFlag::test_w7b_feature_flag_bridge_delegates_to_v4_envelope`
   - Expected bridge result object identity to be the mocked v4 envelope result.
   - Actual result was a distinct `SealedL2Artifact` instance.

Directory-level collection blocker:

- `tests/_apps_contract/test_exec_summary_cli.py` imports missing symbol `CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_RETIRED_PROVIDER_PROFILE` from `apps_rg.runtime.section_cli_defaults`.

## Implementation Stop Condition

Do not edit production/test implementation files for Waves 1-8 until:

1. `mcp__adg_sqlite.adg_health` succeeds in the active Codex session.
2. Graph-backed scope and impacted-test selection are recorded.
3. The implementation work occurs in the isolated app-scope worktree branch `codex-apps-rg-l2-e1-e5-best-practice-closeout`.
