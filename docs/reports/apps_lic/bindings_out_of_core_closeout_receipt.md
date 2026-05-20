# apps_lic spine bindings — out of agentic_core closeout

**Date:** 2026-05-20  
**Scope:** Move app-owned spine stage bindings from `agentic_core` to `apps_lic/runtime/bindings` with no core re-export shims.

## What moved

| Former path | New path |
|-----------|----------|
| [apps_lic_l0_binding.py](agentic_core/L0_routing/apps_lic_l0_binding.py) | [l0_binding.py](apps_lic/runtime/bindings/l0_binding.py) |
| [apps_lic_l1_binding.py](agentic_core/L1_cognition/apps_lic_l1_binding.py) | [l1_binding.py](apps_lic/runtime/bindings/l1_binding.py) |
| [apps_lic_l2_binding.py](agentic_core/L2_execution/apps_lic_l2_binding.py) | [l2_binding.py](apps_lic/runtime/bindings/l2_binding.py) |
| [apps_lic_l3_binding.py](agentic_core/L3_orchestration/apps_lic_l3_binding.py) | [l3_binding.py](apps_lic/runtime/bindings/l3_binding.py) |
| [apps_lic_c0_binding.py](agentic_core/runtime/c0/apps_lic_c0_binding.py) | [c0_binding.py](apps_lic/runtime/bindings/c0_binding.py) |
| [apps_lic_pa_binding.py](agentic_core/prompt_governance/apps_lic_pa_binding.py) | [pa_binding.py](apps_lic/runtime/bindings/pa_binding.py) |
| [apps_lic_exit_binding.py](agentic_core/runtime/exit/apps_lic_exit_binding.py) | [exit_binding.py](apps_lic/runtime/bindings/exit_binding.py) |
| [apps_lic_promo_binding.py](agentic_core/L6_observability/promotion/apps_lic_promo_binding.py) | [promo_binding.py](apps_lic/runtime/bindings/promo_binding.py) |
| [u0_apps_lic_binding.py](agentic_core/runtime/entry/u0_apps_lic_binding.py) | [u0_binding.py](apps_lic/runtime/bindings/u0_binding.py) |

**Product spine import surface:** [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) → `apps_lic.runtime.bindings.*`

**Left in agentic_core (generic contracts, not stage runners):** e.g. [apps_lic_ingress_payload.py](agentic_core/runtime/contracts/apps_lic_ingress_payload.py), L5 evaluators, touch-state writers.

## Grep proof (zero core binding modules)

```text
glob agentic_core/**/apps_lic*binding* → 0 files
rg 'from agentic_core\.(L0_routing|L1_cognition|L2_execution|L3_orchestration|runtime\.(c0|exit|entry)|prompt_governance|L6_observability\.promotion)\.apps_lic' *.py → 0 matches
```

## CI / governance updates

- [check_apps_lic_golden_path_runtime.py](ops_scripts/ci/check_apps_lic_golden_path_runtime.py) — source paths repointed to `apps_lic/runtime/bindings/`
- [check_apps_lic_shared_x3_path.py](ops_scripts/ci/check_apps_lic_shared_x3_path.py) — exit binding path repointed
- [check_agentic_core_addition.py](ops_scripts/ci/check_agentic_core_addition.py) — removed migrated `apps_lic_exit_binding` allowlist entry
- [test_no_app_specific_literals_in_core.py](tests/governance/test_no_app_specific_literals_in_core.py) — adapter exemplar switched to `apps_rg_l0_binding`
- [test_ag5_no_app_specific_exit_imports.py](tests/_core_contract/test_ag5_no_app_specific_exit_imports.py) — dropped skip for moved exit binding

## Verification

| Command | Result |
|---------|--------|
| `pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -q` | 109 passed |
| `pytest tests/apps_lic/test_spine_convergence_negative_proof.py tests/_apps_contract/test_w6_apps_lic_boundary_governance.py -q` | 91 passed |
| `pytest tests/_apps_contract/test_w6_apps_lic_l3_l2.py -q` | 76 passed (repointed `_canonical_pipeline` import to [test_w5_apps_lic_c0_pa.py](tests/apps_lic/test_w5_apps_lic_c0_pa.py)) |
| `pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py::TestA01_RuntimeImports -q` | 11 passed |
| `python ops_scripts/ci/check_apps_lic_shared_x3_path.py` | ALL CHECKS PASS |
| `python ops_scripts/ci/check_apps_lic_exit_x1_x3.py` | all checks passed |
| `python ops_scripts/ci/check_apps_lic_golden_path_runtime.py` | 17/18 pass (advisory); `l3_participates_for_managed_workflow` pre-existing route-family assertion |

**Note:** Live `python -m apps_lic` can block on provider; binding seam proof is via pytest + CI gates above (no mocks in golden-path contract tests).

## Status

**PASS** for bindings migration seam (files moved, imports repointed, core binding modules deleted, tests/gates green on binding surface).
