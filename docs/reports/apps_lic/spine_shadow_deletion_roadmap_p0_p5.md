# apps_lic shadow pipeline deletion roadmap (P0–P5)

Source of truth: shadow inventory S1–S22 (uploaded audit). Target spine:

`U0 → L1 → l0_route_apps_lic → C0/PA (when required) → L3 (R3R4 managed workflow) → l2_execute_apps_lic / 9-HOP → Exit`

**Non-goals:** No apps_rg-style lane pipeline; no `apps_lic` registration in `apps_rg` L2 resolver unless AG-8 explicitly requires it.

## Runner classification (remaining surfaces)

| ID | Surface | Classification | Phase |
|----|---------|----------------|-------|
| S5 | `profile_builder_adapter` | **PRODUCT_CANONICAL** | P2 (wired via dispatch) |
| S9 | `l2_execute_apps_lic` / HOP | **PRODUCT_CANONICAL** | P2 |
| S1 | `integrated_r4_lic` default CLI | **LEGACY_ONLY** | P2 (env gate) |
| S2 | `--apps-e2e-live` governed_run | **LEGACY_ONLY** | P2 (warn; not product) |
| S3/S4 | GovernedLic / spine_handoff | **LEGACY_ONLY** | P3 retire |
| S6 | `lic_ingress_runner` | **DELETE_PENDING** | P3 merge |
| S7/S8 | YAML static/managed L2 recipes | **DELETE_PENDING** | P4 fold/delete |
| S10 | `resolve_l2_recipe("apps_lic")` | **DELETE_PENDING** | P2 block in CLI |
| S11 | `run_workflow_lic.py` | **DELETE_PENDING** | P5 delete |
| S12 | `reasoning/HOPPipelineExecutor.py` | **DELETE_PENDING** | P5 delete |
| S13 | `run_charles_truist_outreach` | **DELETE_PENDING** | P5 delete |
| S14 | `campaign_batch_orchestrator` | **LEGACY_ONLY** | P3 repoint |
| S17 | eval harness | **EVAL_ONLY** | P5 label |
| S21 | `integrated_r4_lic` in agentic_core | **LEGACY_ONLY** | P4 move to app |
| S22 | core `apps_lic_*_binding` | **PRODUCT_CANONICAL** (shim) | P1/P4 app-owned |

---

## P0 — Baseline gap (no deletes)

| Item | Action |
|------|--------|
| Files | `artifacts/apps_lic/spine_convergence/w0_baseline_gap.json` |
| Tests | `pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py` |
| Proof | `python ops_scripts/apps_lic/check_apps_lic_golden_path_runtime.py` (if present) |
| Rollback | N/A (read-only) |

---

## P1 — Bindings migration prep

| Item | Action |
|------|--------|
| Change | Create `apps_lic/runtime/bindings/` mirrors; ≤30-line shims in `agentic_core` |
| Delete | None |
| Imports | Tests import app bindings first |
| Proof | `pytest tests/_apps_contract/test_w3_apps_lic_u0.py tests/_apps_contract/test_w5_apps_lic_c0_pa.py` |
| Rollback | Revert shim paths |

---

## P2 — Canonical dispatch + CLI switch (this wave)

| Item | Action |
|------|--------|
| **Add** | `apps_lic/runtime/dispatch/canonical_dispatch.py`, `spine_run_result.py` |
| **Change** | `apps_lic/__main__.py` → `run_canonical_apps_lic_spine`; legacy behind `APPS_LIC_ALLOW_LEGACY_R4=1` |
| **Change** | `apps_lic/runtime/legacy/r4_single_action.py` |
| **Tests** | `tests/apps_lic/test_canonical_dispatch_smoke.py`; rewrite `test_apps_lic_spine.py`, `test_apps_lic_w1_l0_enforcement.py` |
| **Proof** | `pytest tests/apps_lic/test_canonical_dispatch_smoke.py tests/_apps_contract/test_ag8_apps_lic_golden_path.py -q` |
| **Artifacts** | `artifacts/apps_lic/spine_convergence/runs/<run_id>/spine_run_manifest.json` |
| **Rollback** | Set `APPS_LIC_ALLOW_LEGACY_R4=1` |

---

## P3 — Retire GovernedLic from product

| Item | Action |
|------|--------|
| Delete from product path | `GovernedLicRun` default wiring |
| Repoint | `campaign_batch_orchestrator` off GovernedLic |
| Tests | Remove `GovernedLicRun` expectations from governance |
| Proof | CLI + AG-8 golden path without `governed_run` |
| Rollback | Keep `integrations/governed_lic_run.py` as LEGACY_ONLY |

---

## P4 — YAML L2 recipe fold + HOP/PA convergence

| Item | Action |
|------|--------|
| Fold | `apps_lic_static_dag.yaml` / `apps_lic_managed_dag.yaml` into L3/HOP SSOT (`hop_pipeline.py`) |
| Delete | `lic_l2_recipe_registry` product registration |
| Move | `integrated_r4_lic_pipeline_run` → `apps_lic/runtime/legacy/` |
| Proof | No `resolve_l2_recipe("apps_lic")` in product import graph |
| Rollback | Env legacy R4 |

---

## P5 — Hard deletes + eval labeling

| Item | Action |
|------|--------|
| **Delete** (after grep) | S11 `run_workflow_lic.py`, S12 deprecated HOP executor, S13 charles script |
| **Label** | S17 eval-only `NON_PRODUCT` in README |
| **Shrink** | S21 out of `agentic_core` when app bindings own identity |
| Proof | Full governance + contract suite green |
| Rollback | Git restore deleted paths |

---

## Stale governance test rewrites (exact)

| Test file | Rewrite |
|-----------|---------|
| `tests/governance/test_apps_lic_spine.py` | Expect `run_canonical_apps_lic_spine`; manifest R4+R3R4; no `R3_grounded_read`-only |
| `tests/governance/test_apps_lic_w1_l0_enforcement.py` | `test_main_uses_canonical_dispatch_not_run_workflow_lic` |
| `tests/governance/test_apps_lic_entrypoint_purity.py` | Require `run_canonical_apps_lic_spine`; forbid `run_workflow_lic` in `main()` |
| `tests/governance/test_apps_lic_signal_p2.py` | Keep import-graph ban on `run_workflow_lic` |

---

## Canonical runtime proof command

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
pytest tests/apps_lic/test_canonical_dispatch_smoke.py tests/_apps_contract/test_ag8_apps_lic_golden_path.py -q --tb=short
python -m apps_lic --recipient-class executive --channel email --outreach-mode cold --manual-brief apps_lic/scripts/_interactive_brief.json
```

Expected artifacts: `artifacts/apps_lic/spine_convergence/runs/<run_id>/route_contract.json`, `spine_run_manifest.json`.
