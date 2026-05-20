# Fix whole-run executive_summary PHASE1_NO_RUN_DIR — closeout receipt

**PLAN_ID:** `fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2`  
**Plan file:** [.cursor/plans/fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md](../../.cursor/plans/fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md)  
**Generated:** 2026-05-20

---

## STATUS

**PARTIAL** — Planning waves W1–W5 closed on disk and Notion; runtime product proof remains BLOCKED until a post-fix canonical whole-run achieves `outcome_authorized=true` and integrated validator PASS.

---

## ROOT_CAUSE

**Classification:** run_dir discovery mismatch + dispatch/pointer divergence (not native C0.3 schema defect).

**Evidence (failed run `cli_c61c8be7fc9c`):**

- `phase1_lane_inventory.json`: `"executive_summary": "ok|missing_pointer:…"` — in-process dispatch reported success, but no resolvable pointer under `modular_r4/sections/executive_summary/`.
- `modular_r4/sections/executive_summary/` — **absent** (no `real/<run_id>/`, no `latest_real_run.json`).
- `modular_r4/sections/competencies/real/competencies_20260520_193745/native_c03_final_evidence.json` — competencies lane materialized correctly in same whole-run.
- `generate_resume_step_receipt.json`: `fatal_lane_recipe_policy:executive_summary:PHASE1_NO_RUN_DIR`.
- `integrated_lane_evidence_status.json`: executive_summary in `missing_lanes` with `PHASE1_NO_RUN_DIR`.

**Mechanism:** Phase1 calls `run_canonical_apps_rg_from_cli_primitives` with inline `job_description_text` and `manual_brief` while `MODULAR_R4_SECTIONS_ROOT` points at `cli_*/modular_r4/sections`. Executive_summary must call `finalize_runtime_proof_run` so `latest_*_run.json` lands under that sections root. When briefing/JD threading or early-return paths skip finalize, dispatch can still surface as `ok` while rollup resolution fails → `PHASE1_NO_RUN_DIR`.

**Section-mode contrast:** CLI passes `--jd` and `--manual-brief` as **file paths**; whole-run Phase1 passes **inline text** (Brown & Brown briefing contains `/` segments). `_read_optional_brief` must treat non-file strings as inline text (not path resolution failures).

---

## FIX_SUMMARY

| Seam | Change |
|------|--------|
| Briefing threading | Preserve inline briefing through `_read_optional_brief` / executive_summary dispatch (slashes in text) |
| Pre-run surfacing | `emit_integrated_lane_pre_run_failure` writes under `sections/executive_summary/` when pointer missing |
| Tests | `tests/unit/apps_rg/test_integrated_executive_summary_materialization_w8c.py` — Phase1 modular root, inline brief, pre-run blocker refs |
| Native C0.3 | No schema change; existing `apps_rg/runtime/native_c03_skills_graph.py` + proof pool enrich |

---

## FAILED_RUN_INSPECTION

| Artifact | Finding |
|----------|---------|
| [r4_run_manifest.json](../../artifacts/apps_rg/runs/cli_c61c8be7fc9c/r4_run_manifest.json) | `L2_EXECUTION_ERROR` / `PHASE1_NO_RUN_DIR` |
| [phase1_lane_inventory.json](../../artifacts/apps_rg/runs/cli_c61c8be7fc9c/modular_r4/phase1_lane_inventory.json) | exec `ok\|missing_pointer` |
| [integrated_lane_evidence_status.json](../../artifacts/apps_rg/runs/cli_c61c8be7fc9c/integrated_lane_evidence_status.json) | exec missing; 6 lanes finalized |
| [section_provider_calls.json](../../artifacts/apps_rg/runs/cli_c61c8be7fc9c/modular_r4/section_provider_calls.json) | exec `provider_call_attempted: false`, `PHASE1_NO_RUN_DIR` |

---

## SECTION_MODE_COMPARISON

| Dimension | Section mode | Whole-run Phase1 |
|-----------|--------------|------------------|
| Entry | `python -m apps_rg --section executive_summary` | `run_modular_resume_generation` → `run_canonical_apps_rg_from_cli_primitives` |
| JD / brief | File paths on CLI | Inline `jd_text` / `briefing_text` from `ModularLaneTargeting` |
| Run dir root | `artifacts/apps_rg/runtime_proofs/executive_summary/` | `cli_*/modular_r4/sections/executive_summary/` via `MODULAR_R4_SECTIONS_ROOT` |
| Envelope | Section proof | `APPS_RG_WHOLE_RUN_ENVELOPE=1`, `APPS_RG_CORRELATED_CLI_RUN` |

---

## EXPLICIT_NON_CLAIMS

- No section-only proof upgraded to product / Fort Knox / L7 certification
- No deleted shadow runner restored
- No product proof gate PASS unless integrated validator reports PASS with authorized outcome
- No C0.3 expansion beyond executive_summary + competencies first wave

---

## NEXT_BLOCKER

Re-run canonical whole-run after merge; confirm `integrated_product_proof_gate` only PASS when `outcome_authorized=true` and all seven generated lanes materialize under `modular_r4/sections/`.

---

## FILES_CHANGED (plan + receipt wave)

- [fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md](../../.cursor/plans/fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md)
- [fix_whole_run_executive_summary_phase1_no_run_dir_closeout_receipt.md](fix_whole_run_executive_summary_phase1_no_run_dir_closeout_receipt.md)
- [plan_notion_sync_fix_whole_run_exec_summary_phase1.py](../../tools/notion/plan_notion_sync_fix_whole_run_exec_summary_phase1.py)

Implementation files in working tree: see git commit message for full apps_rg / native C0.3 / spine convergence set.
