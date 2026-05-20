# Prove R4 entrypoint deletion validity — audit receipt

**PLAN_ID:** `prove-r4-entrypoint-deletion-validity`  
**STATUS:** PASS (audit + controlled probe complete; file restored)  
**Date:** 2026-05-20

## SCOPE_MATCH

- Dependency map, canonical call graph, cache-bypass analysis, controlled deletion probe, replacement feasibility, and verdict for `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py`.
- No committed deletion; probe file restored cleanly.

## SCOPE_DRIFT

- None (read-only audit except temporary quarantine move).

## FILES_CHANGED

- **NONE** (probe: move → test → restore original path).

---

## TARGET_FILE

[integrated_r4_deterministic_pipeline_run.py](agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py)

- Public API: `run_integrated_r4_deterministic_pipeline`
- Constants: `CHAIN_KIND`, `ROUTE_FAMILY`, `ROUTE_ID` = `"R4_SINGLE_ACTION"`
- **No** `if __name__ == "__main__"` / **no** `argparse` (not a `python -m` CLI surface)

Related sibling (out of scope for delete-this-file, but same pattern): [integrated_r4_lic_pipeline_run.py](agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py) for `apps_lic`.

---

## REFERENCE_INVENTORY

| Path | Symbol / usage | Class | Direct public entry? | Bypasses R1A/R1B? | Deletion impact |
|------|----------------|-------|----------------------|-------------------|-----------------|
| [apps_rg/runtime/orchestration/canonical_dispatch.py](apps_rg/runtime/orchestration/canonical_dispatch.py) | `import run_integrated_r4_deterministic_pipeline`; call after `run_whole_run_cache_preflight` | **production/runtime** | no (library) | **no** on whole-run path (preflight first); **yes** if called without preflight | **REQUIRED_RUNTIME** — whole product generation breaks |
| [apps_rg/__main__.py](apps_rg/__main__.py) | module-level import; `_run_with_args` calls R4 after preflight | production + **test shim** | `python -m apps_rg` only | shim: **no** (preflight); import at load ties CLI to R4 | **REQUIRED_RUNTIME** for whole-run; top-level import blocks `apps_rg` load |
| [agentic_core/runtime/entry/apps_rg_dispatch.py](agentic_core/runtime/entry/apps_rg_dispatch.py) | `dispatch_apps_rg_run` → `run_canonical_apps_rg_from_cli_primitives` | production | no | **no** (inherits preflight) | indirect **REQUIRED_RUNTIME** |
| [apps_rg/cache/whole_run_entrypoint_preflight.py](apps_rg/cache/whole_run_entrypoint_preflight.py) | documents `miss_behavior` / `delegates_to` | SSOT docs-in-code | no | N/A (enforces preflight **outside** R4) | **DOC_ONLY** strings |
| [apps_rg/runtime/integrated_product_proof_gate.py](apps_rg/runtime/integrated_product_proof_gate.py) | `_detect_integrated_r4` via manifest/how_trace/spine artifacts | proof validator | no | does **not** require cache preflight receipts | **CERTIFICATION_DEPENDENCY** on R4 **artifacts**, not on module path |
| [apps_rg/runtime/run_bundle_index.py](apps_rg/runtime/run_bundle_index.py) | producer label `integrated_r4_deterministic_pipeline` | artifact index | no | N/A | **ARTIFACT_SCHEMA** naming |
| [agentic_core/L5_safety/runtime_gates/g07_route_selection.py](agentic_core/L5_safety/runtime_gates/g07_route_selection.py) | `R4_SINGLE_ACTION` alias | L0 gate enum | no | N/A | route-family data (not entrypoint) |
| [ops_scripts/ci/check_agentic_core_addition.py](ops_scripts/ci/check_agentic_core_addition.py) | allowlist string `R4_SINGLE_ACTION` | CI | no | N/A | **STALE_REFERENCE** risk if route renamed |
| [config/profiles/apps_rg/pipeline_defaults.yaml](config/profiles/apps_rg/pipeline_defaults.yaml) | comment reference | profile | no | N/A | **DOC_ONLY** |
| `tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_*.py` (4 modules) | direct `run_integrated_r4_*` | **test/cert** | no | **yes** (by design for spine/L7 contracts) | **TEST_ONLY** / **CERTIFICATION** |
| `tests/_apps_contract/test_apps_rg_*` (≥6 modules) | direct R4 invocation | contract | no | **yes** | **TEST_ONLY** / **CERTIFICATION** |
| `tests/unit/apps_rg/test_r1b_whole_run_entrypoint_parity_w9b.py` | monkeypatch R4; asserts preflight order in **source** | test | no | tests wiring, not bypass | **TEST_ONLY** |
| `docs/reports/**`, `.cursor/plans/**` | historical | docs | no | N/A | **DOC_ONLY** |

**Production importers (Python): exactly 2**

1. `apps_rg/runtime/orchestration/canonical_dispatch.py`
2. `apps_rg/__main__.py` (eager import + `_run_with_args` shim)

**No** `python -m agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run` references found.

---

## CANONICAL_CALL_GRAPH

### Whole product (governed)

```text
python -m apps_rg
  → apps_rg.__main__.main
  → agentic_core.runtime.entry.apps_rg_dispatch.dispatch_apps_rg_run   [no section arg]
    → apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives(section="")
      → build_raw_request_for_r4
      → apps_rg.cache.whole_run_entrypoint_preflight.run_whole_run_cache_preflight
           ├─ R1A exact (compute_r1a_key / check_r1a_cache)
           ├─ R1B semantic (execute_whole_run_r1b_preflight) when enabled
           └─ section_lane=False → full preflight
      ├─ [cache hit] build_cache_hit_dispatch_result → return (NO R4)
      └─ [cache miss] run_integrated_r4_deterministic_pipeline(app_name="apps_rg")
           → resolve_l2_recipe → GenerateResumeStep / modular lanes
           → U0 → L1 → L0 → C0 bypass → L2 → Exit V6 → exhaust → L7 emit
      → maybe_ingest_r1b_post_exit
```

### Section lane (`--section <lane>`)

```text
python -m apps_rg --section executive_summary
  → run_canonical_apps_rg_from_cli_primitives(section=<lane>)
  → _run_<lane>_lane_from_cli   [early return — does NOT call R4]
```

Section paths use lane modules (`executive_summary_lane`, etc.), not the integrated R4 entrypoint.

### Test shim (non-product CLI path)

```text
apps_rg.__main__._run_with_args  [contract tests monkeypatch]
  → run_whole_run_cache_preflight(ENTRYPOINT_CLI_SHIM)
  → [miss] run_integrated_r4_deterministic_pipeline
```

---

## CACHE_PREFLIGHT_PROOF

| Question | Evidence |
|----------|----------|
| R4 before cache preflight on product path? | **No.** [canonical_dispatch.py](apps_rg/runtime/orchestration/canonical_dispatch.py) L1253–1277: `run_whole_run_cache_preflight` then `if not preflight.generation_required: return hit` else R4. |
| R4 on cache hit? | **No** on whole-run path (early return). |
| R4 after cache miss only? | **Yes** for whole-run product dispatch. |
| Section lanes skip R1A/R1B? | **Yes** by design: [whole_run_entrypoint_preflight.py](apps_rg/cache/whole_run_entrypoint_preflight.py) L109–114 sets `section_lane=True`, `generation_required=True` — section runs are non-whole-run; they do not invoke R4. |
| Can R4 be called without preflight? | **Yes** — any code or test that imports `run_integrated_r4_deterministic_pipeline` directly. R4 does **not** enforce cache internally. |
| Product proof validator requires cache evidence? | **No.** [integrated_product_proof_gate.py](apps_rg/runtime/integrated_product_proof_gate.py) checks `python -m apps_rg`, integrated artifacts, Exit ALLOW, non-product classifications — **no** `whole_run_cache_preflight` / R1A / R1B receipt requirement today. |

**Architecture drift (P1, not P0):** contract tests and Fort Knox/L7 probes may call R4 directly and still produce `agentic_core_how_trace.json` + `r4_run_manifest.json` that satisfy `_detect_integrated_r4` without proving cache preflight ran. That is a **proof-guard gap**, not proof that the entrypoint file must keep its current name/path.

---

## R4_INVOCATION_SURFACES

| Surface | Callable? | Product? | Cache preflight? |
|---------|-----------|----------|------------------|
| `python -m apps_rg` (whole) | yes | yes | yes (via canonical_dispatch) |
| `python -m apps_rg --section *` | yes | lane-dev | N/A (no R4) |
| `python -m` on R4 module | **no** `__main__` | no | — |
| Direct import `run_integrated_r4_deterministic_pipeline` | yes | only if caller skips dispatch | **caller-dependent** |
| `_run_with_args` | tests | no | yes |

**Outside-main policy:** R4 module is **not** in `ALLOWED_OUTSIDE_MAIN_MODULE_CLI`; not a second CLI product entry.

---

## BEHAVIOR_OWNERSHIP_TABLE

| Capability | Owned by this file? | Also elsewhere? | Unique to R4 file? |
|------------|---------------------|-----------------|---------------------|
| U0 intake (`run_request_intake`) | sequences | canonical components | composition only |
| U0→L1 bridge | sequences | `validated_request_to_plan_contract` | composition only |
| L0 route gates | sequences | `check_route_gates` | composition only |
| RouteContract emission | yes (writes `route_contract.json` for L7) | L0 authority | **wired in this composer** |
| C0 bypass receipt | sequences | `build_c0_bypass_receipt` | composition only |
| L2 static DAG / recipe resolve | sequences | `resolve_l2_recipe(app_name)` | **apps_rg production path** |
| Exit V6 | sequences | `ExitEvalPipeline.run` | composition only |
| Runtime exhaust seal | sequences | exhaust helpers | composition only |
| L7 how_trace + route_family_coverage + spine_proof | **emits** | L7 builders | **required for 99/L7 proof artifacts** |
| Integrated manifest / r4_run_manifest | **emits** | emitter helpers | **product proof detection** |
| No-bypass assertions in how_trace | **emits** | L7 stage payloads | certification tests depend on this path |
| R1A/R1B cache | **no** | `whole_run_entrypoint_preflight` (apps_rg) | **not in R4** |
| Product proof eligibility logic | **no** | `integrated_product_proof_gate` | separate |

**Conclusion:** The file is the **sole integrated composer** for `apps_rg` whole-run spine + L7 artifact emission. Individual steps are generic; **the composed pipeline and artifact bundle are not duplicated** in another `apps_rg`-callable module today.

---

## CONTROLLED_DELETION_PROBE

**Method:** `Move-Item` to `agentic_core/runtime/entrypoints/_deleted_probe_integrated_r4_deterministic_pipeline_run.py.disabled` (no commit).

**Restored:** yes → [integrated_r4_deterministic_pipeline_run.py](agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py)

### Commands and exit codes

| Command | Exit | Observation |
|---------|------|-------------|
| `python -m apps_rg --help` | **1** | `ModuleNotFoundError` on import in `apps_rg/__main__.py` |
| `python -c "import apps_rg.__main__"` | **1** | same |
| `python -c "from apps_rg.runtime.orchestration.canonical_dispatch import ..."` | **1** | same |
| `pytest` (R4-focused bundle) | **2** collect / **10** fail | see below |

### Failures (classified)

| Failure | Classification |
|---------|----------------|
| `ModuleNotFoundError` importing `integrated_r4_deterministic_pipeline_run` in `canonical_dispatch`, `apps_rg.__main__` | **REQUIRED_RUNTIME_DEPENDENCY** |
| `test_integrated_r4_l7_emit.py` collection error | **CERTIFICATION_DEPENDENCY** |
| `test_integrated_r4_pipeline_profile_hardening.py` collection error | **CERTIFICATION_DEPENDENCY** |
| `test_apps_rg_generation_entrypoints.py` collection error (via `modular_resume_generation` → `canonical_dispatch`) | **REQUIRED_RUNTIME_DEPENDENCY** |
| `test_apps_rg_r4_manifest_l2_fault_consistency.py` (3 tests) | **CERTIFICATION_DEPENDENCY** |
| `test_apps_rg_missing_recipe_fails_closed.py` (3 tests) | **CERTIFICATION_DEPENDENCY** |
| `test_apps_rg_cannot_inject_l2_callable.py` (3 tests) | **CERTIFICATION_DEPENDENCY** |
| `test_r1b_whole_run_entrypoint_parity_w9b.py` (2 tests) | **TEST_ONLY_DEPENDENCY** (import `canonical_dispatch` at collection) |
| `test_integrated_product_proof_gate.py` | **passed** (17/17 in partial bundle — no import of R4 module) |

---

## DELETION_VERDICT

### **DELETE_AFTER_REPLACEMENT_VALID**

**Not DELETE_NOW_VALID** — removal breaks production import chain and L7/certification contracts immediately.

**Not DO_NOT_DELETE_FOREVER** — the concern (separate R4-named public entrypoint as product shortcut) is valid architecturally, but the **behavior** must survive as an internal composer; only the **surface name and import path** should converge.

**Not BLOCKED_UNKNOWN** — caller graph and probe failures are complete.

---

## EVIDENCE_FOR_VERDICT

1. **Only two production importers**, both after cache preflight on the whole-run path (or test shim with preflight).
2. **No direct `python -m` CLI** on the R4 module.
3. **Controlled probe:** `python -m apps_rg` cannot load; `canonical_dispatch` cannot import; ≥10 contract tests fail — all trace to missing module.
4. **Section product path does not use R4** — lanes are separate; deleting R4 does not remove section CLI, but removes whole-run generation.
5. **Parallel pattern:** `integrated_safe_reuse_run`, `integrated_managed_workflow_run`, `integrated_r4_lic_pipeline_run` show the platform pattern is “integrated entrypoint per route family,” not accidental duplication only in apps_rg.
6. **Cache bypass is real for direct callers** but is **not** the production `python -m apps_rg` path; fixing that belongs in product proof gate + test policy, not in keeping a misnamed file forever.

---

## REPLACEMENT_PLAN_IF_NEEDED

Smallest safe replacement (future plan, not executed here):

1. Add `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` (or `integrated_route_family_spine_run.py`):
   - `run_integrated_single_action_spine(*, route_family: str, app_name: str, ...)`
   - Move body from current R4 file; `R4_SINGLE_ACTION` becomes **data** (`route_family` / profile), not module identity.
2. Thin shim at old path (temporary) **only if** external probes require — user policy says **no** deprecated stubs; prefer single release with import repoint:
   - `canonical_dispatch` → new symbol
   - `apps_rg/__main__.py` → lazy import inside functions (remove eager top-level import)
3. Optional gate on composer: `require_cache_preflight_evidence: dict | None` — reject or stamp when called from apps_rg without preflight receipt (closes P1 proof gap).
4. Update `integrated_product_proof_gate` to require `whole_run_cache_preflight` outcome in run_dir for product PASS.
5. Repoint certification tests to new module path; keep `CHAIN_KIND`/`route_id` strings in artifacts.

---

## CACHE_BYPASS_RISK

| Risk | Severity | Mitigation (not done in this audit) |
|------|----------|-----------------------------------|
| Direct `run_integrated_r4_deterministic_pipeline` in tests | P1 | Gate product proof on preflight receipt; restrict direct calls to `_test_mode` / fixtures |
| Product proof gate ignores cache | P1 | Add hard_fail if no `whole_run_cache_preflight` / R1A/R1B receipt on whole-run dirs |
| Eager import in `apps_rg/__main__.py` | P2 | Lazy import — reduces accidental coupling, does not remove R4 behavior |
| Section lanes skip whole-run cache | by design | Section proof must stay `SECTION_*` classification (already in gate) |

---

## PRODUCT_PROOF_IMPACT

- **Deleting now:** whole-run `python -m apps_rg` cannot run; integrated manifests/L7 artifacts not produced; `_detect_integrated_r4` fails on real runs.
- **Renaming/replacing with same behavior:** no impact if artifact names and `producer_component` preserved.
- **Validator today:** does not block “R4 without cache”; separate hardening recommended.

---

## TESTS_REQUIRED_BEFORE_ACTUAL_DELETE

1. All `test_integrated_r4_*` entrypoint tests pass against new module.
2. `test_apps_rg_r4_manifest_l2_fault_consistency`, `test_apps_rg_missing_recipe_fails_closed`, `test_apps_rg_cannot_inject_l2_callable`.
3. `test_r1b_whole_run_entrypoint_parity_w9b` + `test_apps_rg_generation_entrypoints`.
4. `python -m apps_rg --help` and dry-run whole-run path.
5. `test_integrated_product_proof_gate` + optional new test: reject run_dir with R4 artifacts but no preflight receipt.
6. Fort Knox / L7 route-family coverage probes (if run in CI).

---

## PROTECTED_PATHS_TOUCHED

- None committed.

## FORBIDDEN_FILES_TOUCHED

- None (probe only; restored).

## EXPLICIT_NON_CLAIMS

- No live product/Fort Knox/L7 proof run in this audit.
- No `agentic_core` refactor implemented.
- No deletion committed.
- No claim that R4 name is “only historical” — current code **requires** the module for whole-run spine execution.

## NEXT_BLOCKER

Implement replacement composer + import repoint + product-proof cache receipt gate before physical delete. Optional: lazy-import in `apps_rg/__main__.py` to decouple CLI load from entrypoint identity.
