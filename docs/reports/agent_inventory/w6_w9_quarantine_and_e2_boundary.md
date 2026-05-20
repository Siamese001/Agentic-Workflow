# W6–W9 Quarantine, Canonical Hygiene, and E2 Boundary Report

**Generated:** 2026-05-19  
**Scope:** Tests + docs only — no deletes, no runtime/product behavior change  
**JSON:** [w6_w9_quarantine_and_e2_boundary.json](w6_w9_quarantine_and_e2_boundary.json)

## Summary

| Wave | Result | Confidence |
|------|--------|------------|
| W6 L2 binding shim | RETIRE_CANDIDATE (NEEDS_DECISION to remove) | HIGH |
| W7 Deprecated path quarantine | PASS (registry + tests) | HIGH |
| W8 Canonical runtime hygiene | PASS | HIGH |
| W9 E2 entrypoint | KEEP_CORE pipeline; validation_orchestrator QUARANTINE_UNTIL_REVIEW | HIGH / MEDIUM |

---

## W6 — `apps_rg_l2_binding` shim

| Item | Path | Classification |
|------|------|----------------|
| Canonical | [apps_rg/runtime/bindings/l2_binding.py](../../../apps_rg/runtime/bindings/l2_binding.py) → [l2_binding_adapter.py](../../../apps_rg/runtime/bindings/l2_binding_adapter.py) | KEEP_APPS_RG |
| Core shim | [agentic_core/L2_execution/apps_rg_l2_binding.py](../../../agentic_core/L2_execution/apps_rg_l2_binding.py) | RETIRE_CANDIDATE |

**Evidence:** Shim re-exports identical callables to canonical module. Product entries (`apps_rg.__main__`, `canonical_dispatch`, `apps_rg_dispatch`) do **not** import the shim (AST). Importers are **TEST_SUPPORT_ONLY** / CI: `test_ag6`, `test_apps_rg_pipeline_capability`, governance/CI scripts.

**NEEDS_DECISION:** Migrate tests/CI to `apps_rg.runtime.bindings.l2_binding` before W11 removal.

---

## W7 — Deprecated / quarantine paths

| Path | Classification |
|------|----------------|
| `apps_rg/runtime/dry_run/` | QUARANTINE_UNTIL_REVIEW |
| `apps_rg/runtime/internal/lane_batch.py` | TEST_SUPPORT_ONLY (offline modular orchestrator) |
| `apps_rg/reasoning/Rg*.py` | SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME |
| `runtime/dispatch/*_dispatch.py` | QUARANTINE — `exit_deprecated_dispatch_cli` or ImportError stub (`headline_dispatch`) |
| `deprecated_runtime_cli.py` | KEEP_APPS_RG |

**Default generation:** `modular_section_lanes` when `APPS_RG_R4_GENERATION_MODE` unset.

**Non-product proof env (do not use for product PASS):** `legacy_full_resume`, `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB`, `stub_only` / `FORCE_STUB`, `--mock-judges` without `--allow-test-mock-judges`.

---

## W8 — Canonical product path

```
python -m apps_rg
  → dispatch_apps_rg_run
  → run_canonical_apps_rg_from_cli_primitives
  → modular_section_lanes / run_modular_resume_generation
  → runtime/sections/*_lane + qwen_vllm_provider
  → X2 gates + section_judge_profile (X1D) + runtime_proof_layout artifacts
```

**Not product proof:** `dry_run/`, `contract_harness/` prefixes, offline stub envs, legacy dispatch CLIs, mock judges without test hatch.

---

## W9 — E2 validation entrypoint

| Component | Classification |
|-----------|----------------|
| [l2_phase_pipeline.py](../../../agentic_core/L2_execution/orchestration/l2_phase_pipeline.py) `E2 VALID` → `ValidationReceipt` | **KEEP_CORE** — intended single E2 entry shape (`validator_fn`) |
| [e2_validate_before_execute.py](../../../agentic_core/L2_execution/enforcement/e2_validate_before_execute.py) | KEEP_CORE — supplemental work-order gate |
| [e2_agent_gate.py](../../../agentic_core/L2_execution/enforcement/e2_agent_gate.py) | KEEP_CORE — decorator adapter |
| [boundary_validator.py](../../../agentic_core/L2_execution/enforcement/boundary_validator.py) | KEEP_CORE — composable validator |
| [authority_validator.py](../../../agentic_core/L2_execution/reasoning/authority_validator.py) | KEEP_CORE — composable validator |
| [validation_orchestrator.py](../../../agentic_core/L2_execution/reasoning/validation_orchestrator.py) | **QUARANTINE_UNTIL_REVIEW** — zero static Python importers outside self; ADAPT_TO_E2 not started |

**No E2 behavior refactor in this wave.**

---

## Test evidence

| Suite | Result |
|-------|--------|
| `test_apps_rg_l2_binding_shim_boundary.py` | 7 passed |
| `test_apps_rg_deprecated_path_quarantine.py` | 21 passed |
| `test_apps_rg_canonical_runtime_hygiene.py` | 7 passed |
| `test_l2_e2_validation_entrypoint_boundary.py` | 5 passed |
| `orchestration/` | 8 passed |

Broad filtered contract/unit suites: **NOT_RUN_SLOW** (pre-existing noise).

---

## Explicit non-claims

- No files deleted or archived
- No runtime or product behavior changed
- Static import scan ≠ runtime reachability for `ValidationOrchestrator`
- No live apps_rg proof run
