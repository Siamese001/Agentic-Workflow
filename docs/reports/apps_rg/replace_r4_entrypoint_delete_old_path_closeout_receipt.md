# Replace R4 Entrypoint — Delete Old Path — Closeout Receipt

PLAN_ID: replace-r4-entrypoint-delete-old-path

## STATUS: PASS

## FILES_DELETED

- [integrated_r4_deterministic_pipeline_run.py](agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py) — hard delete; no shim, no deprecation stub

## NEW_COMPOSER

- [integrated_single_action_spine_run.py](agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py)
- Public API: `run_integrated_single_action_spine`, `SingleActionSpineRunResult`
- Route data: `route_family` / `route_id` / `chain_kind` (default `R4_SINGLE_ACTION` for apps_rg)
- Manifest fields: `cache_preflight_completed`, `r1a_preflight_status`, `r1b_preflight_status`, `cache_result`, `cache_miss_receipt_ref`, `generation_spine_invocation_allowed`, `generation_spine_invocation_blocked_reason`, `route_family`

## FILES_CHANGED (primary)

- [integrated_single_action_spine_run.py](agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py) — NEW composer
- [cache_preflight_evidence.py](apps_rg/cache/cache_preflight_evidence.py) — NEW preflight evidence + receipts
- [canonical_dispatch.py](apps_rg/runtime/orchestration/canonical_dispatch.py) — preflight → hit short-circuit / miss → spine
- [__main__.py](apps_rg/__main__.py) — lazy spine import; cache evidence on whole-run path
- [integrated_product_proof_gate.py](apps_rg/runtime/integrated_product_proof_gate.py) — BLOCK without cache preflight artifacts
- [pipeline_defaults.yaml](config/profiles/apps_rg/pipeline_defaults.yaml) — comment repoint
- [test_single_action_spine_entrypoint.py](tests/unit/apps_rg/test_single_action_spine_entrypoint.py) — NEW required tests
- Bulk repoint: tests, `apps_rg` L2 recipe modules, `integrated_r4_lic_pipeline_run.py` (comment), contract tests

## IMPORTS_REPOINTED

- `agentic_core` / `apps_rg` / `tests` Python: **zero** active imports of `integrated_r4_deterministic_pipeline_run` or `run_integrated_r4_deterministic_pipeline` (grep verified)
- Only intentional reference: [test_single_action_spine_entrypoint.py](tests/unit/apps_rg/test_single_action_spine_entrypoint.py) `ModuleNotFoundError` negative control
- Historical mentions remain in archived plans / audit receipts (not runtime)

## CACHE_PREFLIGHT_ENFORCEMENT

- Whole-run: `run_whole_run_cache_preflight` (R1A → R1B) before spine in [canonical_dispatch.py](apps_rg/runtime/orchestration/canonical_dispatch.py) and [__main__.py](apps_rg/__main__.py)
- **Hit:** `write_cache_hit_receipt`; spine **not** invoked; `generation_spine_invocation_blocked_reason` set
- **Miss:** `write_cache_miss_receipt`; spine invoked once with `cache_preflight_evidence`
- **Section lanes:** do not invoke whole-run generation spine
- Production `app_name=apps_rg` direct spine call without evidence → fault `CACHE_PREFLIGHT` (harness may pass `_test_mode=True`)

## PRODUCT_PROOF_GATE_CHANGES

- Whole-run artifact dirs without `whole_run_cache_preflight.json` / miss receipt → **FAIL** `cache_preflight_evidence_missing`
- Direct composer bypass without receipts cannot pass product proof (tested)

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `python -m apps_rg --help` | 0 |
| `import integrated_r4_deterministic_pipeline_run` | 1 (`ModuleNotFoundError`) |
| Targeted pytest bundle (121 tests, see below) | 0 |

## TESTS_GATES

| Suite | Result |
|-------|--------|
| [test_single_action_spine_entrypoint.py](tests/unit/apps_rg/test_single_action_spine_entrypoint.py) | pass |
| [test_r1b_whole_run_entrypoint_parity_w9b.py](tests/unit/apps_rg/test_r1b_whole_run_entrypoint_parity_w9b.py) | pass |
| [test_integrated_product_proof_gate.py](tests/unit/apps_rg/test_integrated_product_proof_gate.py) | pass |
| [test_no_outside_main_runtime_entrypoints.py](tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py) | pass |
| [test_integrated_r4_l7_emit.py](tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_l7_emit.py) | pass |
| [test_integrated_r4_pipeline_profile_hardening.py](tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_pipeline_profile_hardening.py) | pass |
| [test_apps_rg_r4_manifest_l2_fault_consistency.py](tests/_apps_contract/test_apps_rg_r4_manifest_l2_fault_consistency.py) | pass |
| [test_apps_rg_generation_entrypoints.py](tests/_apps_contract/test_apps_rg_generation_entrypoints.py) | pass |
| [test_integrated_single_action_run_identity.py](tests/governance/test_integrated_single_action_run_identity.py) | pass |
| **Total** | **121 passed** |

## OLD_R4_DELETION_PROOF

- File absent on disk (glob 0 matches)
- `importlib.import_module("...integrated_r4_deterministic_pipeline_run")` → `ModuleNotFoundError`
- No Python imports in `agentic_core` / `apps_rg` / `ops_scripts` / `.github`

## CACHE_HIT_NEGATIVE_CONTROL

- R1A hit: spine mock not called; `generation_skipped` true
- R1B hit: `test_canonical_dispatch_r1b_hit_skips_pipeline` — pipeline not called; `cache_result == r1b_hit`

## CACHE_MISS_POSITIVE_CONTROL

- `test_cache_miss_invokes_spine_once` — exactly one spine call; `whole_run_cache_preflight_miss.json` written; `generation_spine_invocation_allowed` true

## DIRECT_COMPOSER_BYPASS_CONTROL

- `test_apps_rg_production_requires_cache_preflight_evidence` — production spine without evidence faults
- `test_direct_spine_without_cache_fails_product_proof` — product proof FAIL `cache_preflight_evidence_missing`

## ROUTE_FAMILY_DATA_PROOF

- `ROUTE_FAMILY == "R4_SINGLE_ACTION"` on new module; manifest / evidence carry `route_family` as data (not entrypoint identity)
- L7 emit tests still pass on repointed spine module

## SHADOW_DELETION_REGRESSION

- [test_no_outside_main_runtime_entrypoints.py](tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py) — pass (outside-`__main__` shadow entrypoints)

## EXPLICIT_NON_CLAIMS

- No public R4 entrypoint kept
- No semantic cache bypass accepted (preflight ordering enforced on canonical whole-run path)
- No live product / Fort Knox / L7 certification PASS on a real canonical whole-run artifact in this wave
- No full-repo pytest green claimed

## NEXT_BLOCKER

- None for this plan scope. Optional: refresh historical audit/plan markdown that still names the deleted module path (documentation-only).
