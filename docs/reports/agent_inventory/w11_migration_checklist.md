# W11 Migration Checklist (pre-archive/delete)

**Status:** M1 + M2 + M2.2/M3/M4 prep + **M3A/M4A/M3B/M4B/M4C/M4D** complete (2026-05-19) — execution still blocked for remaining candidates (no DELETE_READY).

## M1 — `apps_rg_l2_binding` shim importers ✅

## M1b — SHIM-ARCHIVE-PREP ✅ (2026-05-19)

| Step | Action | Proof |
|------|--------|-------|
| M1b.1 | Governance: L2 canonical active, core shim archive-pending | ✅ `test_l2_canonical_binding_active_core_shim_archive_pending` |
| M1b.2 | CI: reclassify shim `ARCHIVE_PENDING` in GOV-3 baseline | ✅ `check_agentic_core_addition.py` |
| M1b.3 | Contract: zero Python importers + quarantine string refs only | ✅ 9 shim boundary tests |
| M1b.4 | Matrix: `archive_readiness=YES` for shim | ✅ fan-in matrix |

**Archive executed:** [w11_shim_archive_receipt.md](w11_shim_archive_receipt.md) — `archives/l2_rationalization_20260519/`

## M1 — `apps_rg_l2_binding` shim importers (detail) ✅

| Step | Owner | Action | Proof |
|------|-------|--------|-------|
| M1.1 | Cursor | Replace imports in `test_ag6_apps_rg_golden_path.py` → `apps_rg.runtime.bindings.l2_binding` | ✅ done |
| M1.2 | Cursor | Replace imports in `test_apps_rg_pipeline_capability.py` | ✅ done |
| M1.3 | Cursor | Update `ops_scripts/ci/check_apps_rg_*` to canonical binding paths/modules | ✅ done |
| M1.4 | Cursor | Governance `test_apps_rg_l1_core_boundary.py` | ⛔ **blocked** — intentional shim-in-core assertion |
| M1.5 | Cursor | ADG `adg_edge_fanin` on shim module | ✅ import fan-in **0** (snapshot `05192026_0920`) |

**Remaining path-string refs (not Python imports):** shim boundary test, governance, `check_agentic_core_addition`, exit/UWG quarantine registry, `_w11_*` inventory scripts, `l2_binding_adapter` docstring.

## M2 — ADG fan-in expansion ✅

| Step | Action | Proof |
|------|--------|-------|
| M2.0 | Re-run `_w11_fanin_scan.py` after M1 | ✅ matrix updated |
| M2.1 | Run `_w11_adg_expand.py` for all concrete module candidates | ✅ 8 groups, fan-in 0 |
| M2.2 | Mark env/CLI hatches `NOT_SUPPORTED_PATTERN` | ✅ 4 candidates |
| M2.3 | Per-file `adg_details` on matrix JSON | ✅ [w11_candidate_fanin_matrix.json](w11_candidate_fanin_matrix.json) |

## M2.2 — `validation_orchestrator` quarantine proof ✅ (prep)

| Step | Action | Proof |
|------|--------|-------|
| M2.2.1 | Confirm no runtime `import validation_orchestrator` | ✅ ADG import fan-in **0**; W9 AST test passes |
| M2.2.2 | Classify | ✅ **ARCHIVE_CANDIDATE_AFTER_30D** (E2 SSOT = `l2_phase_pipeline`) |
| M2.2.3 | CI baseline inventory | ✅ hollow + harness baselines = **blockers** |
| M2.2.4 | Remove CI baselines (execution) | 🔲 after 30d quarantine clock |
| M2.2.5 | Archive move (execution) | 🔲 blocked — not in this wave |

Receipt: [w11_remaining_candidates_prep_receipt.md](w11_remaining_candidates_prep_receipt.md)

## M3A — `Rg*` facade canonical export ✅ (2026-05-19)

| Step | Action | Proof |
|------|--------|-------|
| M3A.1 | Add `run_canonical_apps_rg_from_cli_primitives` to facade | ✅ [rg_orchestrator_facade.py](../../apps_shared/adapters/rg_orchestrator_facade.py) |
| M3A.2 | Integrations mirror delegates to primary | ✅ [integrations/adapters/rg_orchestrator_facade.py](../../apps_shared/integrations/adapters/rg_orchestrator_facade.py) |
| M3A.3 | W3 test for canonical symbol | ✅ `test_rg_orchestrator_facade_exports_canonical_dispatch_symbol` |
| M3A.4 | Keep `RgResumeOrchestrator` for eval/tests | ✅ scenario_runner + unit tests unchanged |

Receipt: [w11_m3_m4_facade_dispatch_migration.md](w11_m3_m4_facade_dispatch_migration.md)

## M3 — `Rg*` test/facade migration plan ✅ (prep)

| Step | Action | Proof |
|------|--------|-------|
| M3.1 | Product-path import scan | ✅ zero under `apps_rg/runtime/sections`, `canonical_dispatch` |
| M3.2 | ADG fan-in per `Rg*.py` | ✅ aggregate **0** (7 files) |
| M3.3 | Classify | ✅ **QUARANTINE_30D** — no Rg* archive this wave |
| M3.4 | Targeted tests | ✅ 27 passed (`test_rg_resume_orchestrator`, `test_rg_reasoning`) |
| M3.5 | Migrate `apps_shared` facades → canonical dispatch / section lanes | 🔲 execution |
| M3.6 | Migrate contract smoke `apps_rg.engines.RgResumeOrchestrator` string | 🔲 execution |
| M3.7 | Retire `tests/unit/apps_rg/reasoning/*` incrementally | 🔲 execution |

**Do not** batch-archive `apps_rg/reasoning/Rg*.py` until M3.5–M3.7 complete.

## M4A — dispatch PA helper extraction ✅ (2026-05-19)

| Step | Action | Proof |
|------|--------|-------|
| M4A.1 | Extract `prompt_trace_reasoning` → sections | ✅ [sections/prompt_trace_reasoning.py](../../apps_rg/runtime/sections/prompt_trace_reasoning.py) |
| M4A.2 | Extract `collect_employment_bullets` → sections | ✅ [sections/resume_employment_bullets.py](../../apps_rg/runtime/sections/resume_employment_bullets.py) |
| M4A.3 | Update lane imports to sections | ✅ 5 lanes + proof_pool_resolver |
| M4A.4 | Dispatch compat re-exports | ✅ dispatch shims unchanged symbol identity |
| M4A.5 | Parity tests | ✅ [test_lane_pa_helper_parity.py](../../tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py) |

Map: [w11_lane_dispatch_pa_map.md](w11_lane_dispatch_pa_map.md)

## M4 — deprecated dispatch / dry_run / orchestrate_full_resume ✅ (prep)

| Step | Action | Proof |
|------|--------|-------|
| M4.1 | Confirm retired `python -m apps_rg.runtime.dispatch.*` not product proof | ✅ W8 hygiene + quarantine tests (39 passed) |
| M4.2 | Classify `*_dispatch.py` PA modules | ✅ **QUARANTINE_30D** (lanes still import) |
| M4.3 | Classify `dry_run/` | ✅ **QUARANTINE_30D**; ADG fan-in **0** |
| M4.4 | Classify `orchestrate_full_resume` | ✅ **KEEP_TEST_SUPPORT_ONLY** |
| M4.5 | `legacy_full_resume` env | ✅ **KEEP_ROLLBACK_ONLY** |
| M4.6 | Extract PA imports to `sections/` before archive | ✅ M4B (2026-05-19) |

Receipt: [w11_fast_blocker_burn_m3b_m4d.md](w11_fast_blocker_burn_m3b_m4d.md)

## M3B — apps_eval Rg integrations boundary ✅ (2026-05-19)

| Step | Action | Proof |
|------|--------|-------|
| M3B.1 | Route narrative judge integrations via facade | ✅ [rg_integrations_facade.py](../../apps_shared/adapters/rg_integrations_facade.py) |
| M3B.2 | Restore minimal `apps_rg/integrations/` for lazy imports | ✅ anti_overfitting, length_budget, hops/_llm_client |
| M3B.3 | W3 no direct apps_eval → apps_rg | ✅ `test_apps_eval_has_no_direct_apps_rg_imports` |
| M3B.4 | Keep scenario_runner on rg_orchestrator_facade | ✅ eval parity |

## M4B — all safe lane PA extraction ✅ (2026-05-19)

| Step | Action | Proof |
|------|--------|-------|
| M4B.1 | Move 7 `compile_*_prompt` modules to sections | ✅ `apps_rg/runtime/sections/*_pa.py` |
| M4B.2 | Dispatch thin re-exports | ✅ `apps_rg/runtime/dispatch/*_pa.py` |
| M4B.3 | Lane imports → sections PA | ✅ executive_summary, headline, ibm_bullets, unify_* |
| M4B.4 | Parity tests | ✅ 10 passed [test_lane_pa_helper_parity.py](../../tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py) |

## M4C — competencies lane execution surface ✅ PARTIAL (2026-05-19)

| Step | Action | Proof |
|------|--------|-------|
| M4C.1 | `competencies_lane_execution` canonical entry | ✅ default trace `sections.competencies_lane` |
| M4C.2 | Lane stops importing dispatch directly | ✅ |
| M4C.3 | Move `run_competencies_execution` body to sections | 🔲 blocked — high coupling |
| M4C.4 | Contract tests | ✅ 10/10 pass — [w11_m4c_competencies_contract_fix.md](w11_m4c_competencies_contract_fix.md) |

## M4D — fan-in / matrix refresh ✅ (2026-05-19)

| Step | Action | Proof |
|------|--------|-------|
| M4D.1 | Re-run fan-in scan + ADG expand | ✅ [w11_candidate_fanin_matrix.json](w11_candidate_fanin_matrix.json) |
| M4D.2 | Update lane map + gated plan | ✅ |
| M4D.3 | Next archive target | ✅ `validation_orchestrator` (ARCHIVE_CANDIDATE_AFTER_30D) |

## M5 — Signal-quality stubs (`apps_shared`)

| Step | Action | Proof |
|------|--------|-------|
| M5.1 | W4 QUARANTINE — wire or ADR before delete | 🔲 |
| M5.2 | ADG fan-in on both stub modules | ✅ aggregate **0** |

## M6 — Env / CLI rollback surfaces (no migration — KEEP)

- `APPS_RG_R4_GENERATION_MODE=legacy_full_resume`
- `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB`
- `APPS_RG_L2_PROVIDER_MODE=stub_only`
- `--mock-judges` + `--allow-test-mock-judges`

**Do not remove** without explicit rollback retirement ADR.
