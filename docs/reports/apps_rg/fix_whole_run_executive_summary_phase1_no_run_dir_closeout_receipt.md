# fix-whole-run-executive-summary-phase1-no-run-dir — closeout receipt

**PLAN_ID:** `fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2`  
**Plan file:** [.cursor/plans/fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md](../../.cursor/plans/fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md)  
**Generated:** 2026-05-20

---

## STATUS: PASS

Materialization seam PASS. Whole-run still exits 1 on aggregation preflight / product gate (out of scope).

## SCOPE_MATCH

| In scope | Out of scope |
|----------|--------------|
| Whole-run `executive_summary` run_dir under `modular_r4/sections/executive_summary/real/` | Judge / semantic cache / L7 / 99 |
| Briefing file-ref dispatch (not inline-only) | Product proof PASS |
| Pre-run failure surfacing when pointer missing | Shadow runner restore |
| Native C0.3 unchanged | Aggregation preflight fix |

## ROOT_CAUSE

- Dispatch reported `ok|missing_pointer` while section-mode wrote under `runtime_proofs` or wrong tree.
- Whole-run Phase-1 passed inline briefing text; section mode used file paths.
- `APPS_RG_MODULAR_R4_SECTIONS_ROOT` not re-asserted per integrated lane.

## FIX (code)

| File | Change |
|------|--------|
| [modular_lane_adapter.py](../../apps_rg/l2_recipe/modular_lane_adapter.py) | `phase1_manual_brief_for_dispatch()`, `phase1_jd_dispatch_refs()` |
| [modular_resume_generation.py](../../apps_rg/l2_recipe/modular_resume_generation.py) | File-ref dispatch; sections root re-assert; pre-run failure emit |
| [canonical_dispatch.py](../../apps_rg/runtime/orchestration/canonical_dispatch.py) | `_resolve_lane_manual_brief()` for executive_summary |
| [test_integrated_executive_summary_materialization_w8c.py](../../tests/unit/apps_rg/test_integrated_executive_summary_materialization_w8c.py) | W8C unit coverage |

## PROOF_RUN

**cli_22cf55c9fd58** — canonical `python -m apps_rg` (Brown & Brown)

| Check | Result |
|-------|--------|
| Exec summary dir | [modular_r4/sections/executive_summary/real/exec_summary_20260520_201036/](artifacts/apps_rg/runs/cli_22cf55c9fd58/modular_r4/sections/executive_summary/real/exec_summary_20260520_201036/) |
| `run_manifest.json` | Present; command = whole-run `__main__.py` (no `--section`) |
| `evidence_package_index.json` | Present |
| `section_l7_binding_manifest.json` | Present |
| `RUN_LINKS` executive_summary | `status=EXECUTED`, `lane_x3=X3_BLOCK` (not `PHASE1_NO_RUN_DIR`) |
| Whole-run exit | 1 — `AggregationPreflightError` / blocked X3 on executive_summary |
| `integrated_product_proof_gate` | FAIL (expected; not product authorized) |

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `pytest tests/unit/apps_rg/test_integrated_executive_summary_materialization_w8c.py` + related gates | PASS |
| `python -m apps_rg` whole-run | Materialization PASS; exit 1 aggregation |

## ARTIFACTS

- [RUN_LINKS.json](artifacts/apps_rg/runs/cli_22cf55c9fd58/RUN_LINKS.json)
- [run_manifest.json](artifacts/apps_rg/runs/cli_22cf55c9fd58/modular_r4/sections/executive_summary/real/exec_summary_20260520_201036/run_manifest.json)
- [apps_rg_chat_session_w8_waves_closeout_manifest.json](apps_rg_chat_session_w8_waves_closeout_manifest.json)

## EXPLICIT_NON_CLAIMS

- Product / Fort Knox / L7 PASS
- Whole-run `outcome_authorized=true`
- Executive summary X3 quality PASS

## NEXT_BLOCKER (optional product seam)

Fix integrated aggregation preflight blocking on `executive_summary` X3_BLOCK so whole-run can reach authorized outcome — content/X2/X3, not materialization.
