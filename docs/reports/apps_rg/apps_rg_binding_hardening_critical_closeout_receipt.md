# apps_rg binding hardening (critical) — closeout receipt

**Generated:** 2026-05-22  
**Scope:** Blocking authority ambiguity (W-A subset) — **complete**

## STATUS: PASS

All six critical items delivered. Legacy `agentic_core/**/apps_rg_*_binding.py` shims **deleted** after caller burndown. Rigor convergence wired into runtime X2 writer.

## SCOPE_MATCH

| Item | Done |
|------|------|
| Import SSOT hard block (repo-wide) | Yes |
| L1 route_hints ADVISORY_ONLY | Yes |
| disposition_authority labeling | Yes |
| Section rollup prefers exit_disposition_receipt | Yes |
| Rigor-critical bundle guard + runtime write | Yes |
| AG-2 direct app binding imports | Yes |
| Shim burndown + deletion | Yes |

## SCOPE_DRIFT

None.

## FILES_CHANGED

- [disposition_authority.py](../../apps_rg/runtime/disposition_authority.py)
- [l1_binding.py](../../apps_rg/runtime/bindings/l1_binding.py)
- [u0_binding.py](../../apps_rg/runtime/bindings/u0_binding.py)
- [section_x2_gate_outputs.py](../../apps_rg/runtime/sections/section_x2_gate_outputs.py)
- [lane_registry.py](../../apps_rg/runtime/rigor/lane_registry.py)
- [convergence_audit.py](../../apps_rg/runtime/rigor/convergence_audit.py)
- [generated_lane_rollup.py](../../apps_rg/runtime/internal/generated_lane_rollup.py)
- [resume_package_disposition.py](../../apps_rg/runtime/internal/resume_package_disposition.py)
- [apps_rg_dispatch.py](../../agentic_core/runtime/entry/apps_rg_dispatch.py)
- [apps_rg_w9_managed_workflow_e2e.py](../../agentic_core/runtime/entry/apps_rg_w9_managed_workflow_e2e.py)
- [x3_disposition.py](../../agentic_core/runtime/exit/x3_disposition.py)
- **Deleted:** `agentic_core/L0_routing/apps_rg_l0_binding.py`, `L1_cognition/apps_rg_l1_binding.py`, `runtime/c0/apps_rg_c0_binding.py`, `prompt_governance/apps_rg_pa_binding.py`, `runtime/exit/apps_rg_exit_binding.py`, `runtime/entry/u0_apps_rg_binding.py`
- Contract tests + CI/test import migrations (32+ files)
- [test_apps_rg_rigor_convergence_runtime_write.py](../../tests/_apps_contract/test_apps_rg_rigor_convergence_runtime_write.py)

## COMMANDS_RUN

- `python -m pytest` (binding hardening suite, 10 modules) → **30 passed**, 1 skipped
- `rg` / AST: **0** `from agentic_core.*apps_rg_*_binding` imports in `*.py`

## TESTS_GATES

- `tests/_apps_contract/test_apps_rg_binding_import_ssot.py` → pass (4 tests, repo-wide + shim deletion)
- `tests/_apps_contract/test_apps_rg_l1_route_authority_advisory.py` → pass
- `tests/_apps_contract/test_apps_rg_ag2_direct_binding_import.py` → pass
- `tests/_apps_contract/test_apps_rg_disposition_authority_receipts.py` → pass
- `tests/_apps_contract/test_apps_rg_rigor_critical_runtime_bundle_guard.py` → pass
- `tests/_apps_contract/test_apps_rg_rigor_convergence_runtime_write.py` → pass
- `tests/_apps_contract/test_apps_rg_package_rollup_exit_authority.py` → pass
- `tests/governance/test_apps_rg_l1_core_boundary.py` → pass

## LEGACY_SHIM_CALLERS_REMAINING

**None** (shim modules deleted; imports migrated to `apps_rg.runtime.bindings.*`).

## DISPOSITION_AUTHORITY_PROOF

- Lane `x3_disposition.json`: `disposition_authority=lane`, `section_x3_mirror_only=true`, `spine_x3_claimed=false`
- `exit_disposition_receipt.json`: `disposition_authority=lane`
- Rollup/package prefer spine receipt over lane mirror when both exist

## FORBIDDEN_FILES_TOUCHED

Targeted `agentic_core` only: `apps_rg_dispatch.py`, `x3_disposition.py` (comment), `apps_rg_w9_managed_workflow_e2e.py` (imports). Six shim files **removed**.

## PROOF_CLASSIFICATION

CONTRACT_TEST_PROOF + RUNTIME_X2_WRITE_PROOF (`test_apps_rg_rigor_convergence_runtime_write`)

## EXPLICIT_NON_CLAIMS

- No integrated spine LIVE_RUNTIME_PROOF
- No RELEASE_ELIGIBLE / certification
- `test_ag6_apps_rg_golden_path` / some pipeline tests have **pre-existing** payload/smoke mismatches unrelated to this seam

## NEXT_BLOCKER

None for critical binding hardening. Optional: fix pre-existing golden-path `briefing_artifact_ref` and e2e smoke enum expectations in a separate seam.
